"""
GeoPulse – Intelligence Crew (upgraded)

Upgrades from v1:
  • 3 agents: Historian, Quant Strategist, Validator/Synthesizer
  • Structured JSON output enforced via prompt schema
  • Multi-precedent RAG context (top-3 results with similarity scores)
  • Richer task descriptions with explicit JSON schema instructions
  • Pydantic parsing of agent outputs into IntelligenceBriefing
  • Simple in-memory result cache to skip re-analysis of identical headlines
  • Returns IntelligenceBriefing object (not raw string)
"""

from __future__ import annotations

import os
import json
import hashlib
import warnings
from datetime import datetime, timezone

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv  
from litellm.exceptions import RateLimitError, APIConnectionError, ServiceUnavailableError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)

from src.db import GeopoliticalVectorStore
from src.models import (
    IntelligenceBriefing,
    GeopoliticalRiskMatrix,
    QuantRiskBriefing,
    RiskLevel,
    ConfidenceLevel,
    PriceDirection,
    CommodityImpact,
)

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# JSON schema snippets injected into agent prompts
# ─────────────────────────────────────────────────────────────────────────────

_HISTORIAN_SCHEMA = """
{
  "headline_summary": "string",
  "overall_risk_level": "CRITICAL|HIGH|MODERATE|LOW|MINIMAL",
  "risk_score": 0-100,
  "escalation_probability_pct": 0-100,
  "historical_precedent_event": "string",
  "historical_precedent_year": "string or null",
  "key_parallels": ["string", ...],
  "structural_differences": ["string", ...],
  "geopolitical_actors": ["string", ...],
  "choke_points_at_risk": ["string", ...],
  "analyst_note": "string"
}
"""

_QUANT_SCHEMA = """
{
  "primary_commodity_affected": "string",
  "commodity_impacts": [
    {
      "name": "string",
      "ticker_hint": "string",
      "price_direction": "SHARP RISE|MODERATE RISE|STABLE|MODERATE FALL|SHARP FALL",
      "expected_move_pct_min": float (signed, e.g. 3.5 or -2.0),
      "expected_move_pct_max": float (signed, e.g. 15.0 or -8.0),
      "volatility_index": 0-100,
      "historical_avg_move_pct": float (signed, observed move in matched precedent),
      "supply_elasticity_score": 0-100,
      "supply_chain_impact": "string",
      "confidence": "VERY HIGH|HIGH|MODERATE|LOW|UNCERTAIN"
    }
  ],
  "supply_disruption_severity": "CRITICAL|HIGH|MODERATE|LOW|MINIMAL",
  "estimated_disruption_duration_days": integer,
  "macro_regime_shift": true|false,
  "tail_risk_scenario": "string",
  "trading_considerations": ["string", ...],
  "sectors_to_monitor": ["string", ...],
  "overall_confidence": "VERY HIGH|HIGH|MODERATE|LOW|UNCERTAIN",
  "quant_note": "string"
}
"""

_EXECUTIVE_SCHEMA = """
{
  "executive_summary": "string (3-5 sentences synthesizing both analyses)",
  "confidence_disclaimer": "string (AI limitations caveat)"
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    """
    Robustly extract first valid JSON object from an LLM response.
    Strips markdown fences, leading/trailing prose.
    """
    raw = raw.strip()
    # Strip ```json ... ``` fences
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except json.JSONDecodeError:
                continue

    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Find first { ... } block
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from LLM output:\n{raw[:500]}")


def _format_rag_context(matches: list[dict]) -> str:
    """Format top-N RAG matches into a structured context block for agents."""
    if not matches:
        return "No close historical precedents found in local archives."

    lines = []
    for i, m in enumerate(matches, 1):
        score = m.get("similarity_score", 0)
        lines.append(
            f"[Precedent {i} | Similarity: {score}%]\n"
            f"Event: {m['associated_event']} ({m.get('year', 'Unknown year')})\n"
            f"Category: {m.get('category', 'General')} | "
            f"Primary commodity: {m.get('primary_commodity', 'N/A')}\n"
            f"Macro regime: {m['regime_impact']}\n"
            f"Context: {m['text']}"
        )
    return "\n\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main crew class
# ─────────────────────────────────────────────────────────────────────────────

class GeoPulseIntelligenceCrew:
    def __init__(self):
        self.llm = LLM(
            model="groq/openai/gpt-oss-20b",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.15,   # lower = more consistent structured output
        )
        self.db = GeopoliticalVectorStore()

        # Simple in-memory cache: headline hash → IntelligenceBriefing
        self._cache: dict[str, IntelligenceBriefing] = {}

    # ── Agents ────────────────────────────────────────────────────────────────

    def _create_agents(self) -> tuple[Agent, Agent, Agent]:
        historian = Agent(
            role="Senior Geopolitical Historian",
            goal=(
                "Analyze a breaking geopolitical headline against curated historical "
                "precedents, then output a structured JSON risk assessment."
            ),
            backstory=(
                "You are a 20-year veteran of the DIA and Oxford's Conflict Research "
                "Programme. You have authored classified reports on every major energy "
                "and maritime crisis since the Gulf War. You communicate exclusively "
                "in precise, evidence-grounded language and structured data."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

        quant_strategist = Agent(
            role="Lead Commodities Quant Strategist",
            goal=(
                "Translate the historian's geopolitical risk matrix into a structured "
                "JSON commodity market impact briefing with per-commodity forecasts."
            ),
            backstory=(
                "You spent 15 years running quant macro books at Goldman Sachs "
                "Commodities and Citadel. You model supply elasticity, basis risk, "
                "and regime-shift probability. You do not speculate — every forecast "
                "is anchored to structural supply-demand fundamentals."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

        synthesizer = Agent(
            role="Chief Intelligence Synthesizer",
            goal=(
                "Merge the historian's risk matrix and the quant's commodity briefing "
                "into a concise executive summary JSON block."
            ),
            backstory=(
                "You are the final editorial layer of a tier-1 geopolitical intelligence "
                "desk. You distill dual-analyst reports into an executive briefing that "
                "a board-level risk committee can act on within 90 seconds."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

        return historian, quant_strategist, synthesizer

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def _create_tasks(
        self,
        headline: str,
        rag_context: str,
        historian: Agent,
        quant: Agent,
        synthesizer: Agent,
    ) -> tuple[Task, Task, Task]:

        historian_task = Task(
            description=f"""
You are analyzing a breaking geopolitical headline for systemic risk.

HEADLINE:
"{headline}"

HISTORICAL ARCHIVE MATCHES (ranked by semantic similarity):
---
{rag_context}
---

INSTRUCTIONS:
1. Identify the single best historical precedent from the archive.
2. Quantify overall risk on a 0-100 scale.
3. Estimate escalation probability within 30 days.
4. List 3-5 structural parallels AND 2-3 key differences vs the precedent.
5. Name all geopolitical actors and physical choke points at risk.
6. Write 2-3 sentences of qualitative analyst judgment.

OUTPUT FORMAT — respond with ONLY valid JSON matching this schema, no prose before or after:
{_HISTORIAN_SCHEMA}
""",
            expected_output=(
                "Valid JSON object matching the GeopoliticalRiskMatrix schema."
            ),
            agent=historian,
        )

        quant_task = Task(
            description=f"""
You are translating the previous geopolitical risk analysis into commodity market impact forecasts.

ORIGINAL HEADLINE:
"{headline}"

Use the historian's structured risk output (from the previous task) as your primary input.

INSTRUCTIONS:
1. Identify 2-6 commodities most exposed to this event.
2. For each commodity provide: name, ticker hint, 14-day price direction, a SIGNED numeric min/max % move range (floats, not strings), volatility index (0-100), historical average % move seen in the matched precedent, supply elasticity score (0-100), supply chain impact, confidence.
3. Classify overall supply disruption severity.
4. Estimate disruption duration in days.
5. Assess whether this event could trigger a macro regime shift (true/false).
6. Describe the worst-case tail risk scenario in 1-2 sentences.
7. List 3-5 trading considerations (NOT financial advice; frame as risk factors to monitor).
8. List equity sectors most exposed.

OUTPUT FORMAT — respond with ONLY valid JSON matching this schema, no prose before or after:
{_QUANT_SCHEMA}
""",
            expected_output=(
                "Valid JSON object matching the QuantRiskBriefing schema."
            ),
            agent=quant,
            context=[historian_task],
        )

        synthesizer_task = Task(
            description=f"""
You are writing the executive summary layer for a dual-analyst intelligence briefing.

ORIGINAL HEADLINE:
"{headline}"

You have access to the historian's geopolitical risk matrix and the quant's commodity briefing from the previous two tasks.

INSTRUCTIONS:
1. Write a 3-5 sentence executive summary that synthesizes both analyses. Do NOT repeat raw numbers — synthesize the narrative.
2. Write a 1-2 sentence confidence disclaimer noting AI limitations and that outputs should be verified against official sources.

OUTPUT FORMAT — respond with ONLY valid JSON, no prose before or after:
{_EXECUTIVE_SCHEMA}
""",
            expected_output=(
                "Valid JSON object with 'executive_summary' and 'confidence_disclaimer' fields."
            ),
            agent=synthesizer,
            context=[historian_task, quant_task],
        )

        return historian_task, quant_task, synthesizer_task

    # ── Core pipeline ─────────────────────────────────────────────────────────
   # ── Retry-wrapped crew execution ─────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        retry=retry_if_exception_type(
            (RateLimitError, APIConnectionError, ServiceUnavailableError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
        )
    
    def _kickoff_with_retry(self, crew: Crew):
        """
        Run crew.kickoff() with exponential backoff on transient LLM errors
        (rate limits, connection drops, provider outages).
        Attempts: 4 total. Waits: 2s, 4s, 8s ... capped at 60s.
        """
        return crew.kickoff()
    
    
    def run_analysis(self, breaking_headline: str) -> IntelligenceBriefing:
        """
        Full pipeline: RAG retrieval → 3-agent sequential crew → structured output.
        Returns an IntelligenceBriefing Pydantic object.
        """
        # Cache check
        cache_key = hashlib.sha256(breaking_headline.strip().lower().encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. RAG retrieval — top 3 historical precedents
        raw_matches   = self.db.query_historical_context(breaking_headline, max_results=3)
        rag_context   = _format_rag_context(raw_matches)

        # 2. Build agents
        historian, quant, synthesizer = self._create_agents()

        # 3. Build tasks
        h_task, q_task, s_task = self._create_tasks(
            breaking_headline, rag_context,
            historian, quant, synthesizer
        )

        # 4. Run sequential crew
        crew = Crew(
            agents=[historian, quant, synthesizer],
            tasks=[h_task, q_task, s_task],
            process=Process.sequential,
        )
        # crew_result = crew.kickoff()
        try:
            crew_result = self._kickoff_with_retry(crew)
        except (RateLimitError, APIConnectionError, ServiceUnavailableError) as e:
            logger.error(f"LLM call failed after all retries: {e}")
            raise RuntimeError(
                "The analysis engine is temporarily rate-limited or unreachable. "
                "Please wait a minute and try again."
            ) from e

        # 5. Parse task outputs into Pydantic models
        geo_data   = _extract_json(str(h_task.output))
        quant_data = _extract_json(str(q_task.output))
        synth_data = _extract_json(str(s_task.output))

        # 6. Build structured Pydantic briefing
        briefing = IntelligenceBriefing(
            headline=breaking_headline,
            timestamp=datetime.now(timezone.utc).isoformat(),
            geopolitical_analysis=GeopoliticalRiskMatrix(**geo_data),
            commodity_analysis=QuantRiskBriefing(
                **{
                    **quant_data,
                    "commodity_impacts": [
                        CommodityImpact(**c) for c in quant_data.get("commodity_impacts", [])
                    ],
                }
            ),
            executive_summary=synth_data.get("executive_summary", ""),
            confidence_disclaimer=synth_data.get(
                "confidence_disclaimer",
                "AI-generated analysis — verify with official sources before acting."
            ),
        )

        # Cache result
        self._cache[cache_key] = briefing
        return briefing


# ── Local test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json as _json
    crew = GeoPulseIntelligenceCrew()
    headline = (
        "Unidentified armed drones have targeted two commercial oil vessels "
        "in the Red Sea, causing major shipping lines to halt transit."
    )
    print("\n⚡ Running upgraded pipeline...\n")
    result = crew.run_analysis(headline)
    print(_json.dumps(result.model_dump(), indent=2))
