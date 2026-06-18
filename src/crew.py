import os
import warnings

# =====================================================================
# 🔥 BUG FIX & LOG FILTERING: Intercept CrewAI's cache engine to prevent 
# unsupported 'cache_breakpoint' calls, and keep the console quiet.
# =====================================================================
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

# Import the database built in Phase 1
from src.db import GeopoliticalVectorStore

load_dotenv()

class GeoPulseIntelligenceCrew:
    def __init__(self):
        # Natively interface with Groq LPUs disguised via OpenAI base_url 
        # to ensure ultra-fast token streaming speeds on a free tier.
        self.llm = LLM(
            model="openai/llama-3.3-70b-versatile", 
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.2
        )
        
        # Connect to your persistent ChromaDB Vector Database
        self.db = GeopoliticalVectorStore()

    def _create_agents(self):
        """Defines the personas, backstories, and operational rules for the nodes."""
        
        historian = Agent(
            role='Senior Geopolitical Historian',
            goal='Analyze breaking news against historical precedents to identify structural risks.',
            backstory='You are a seasoned global policy expert at a top intelligence agency. You specialize in analyzing how past maritime, energy, and military crises escalate.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        quant_strategist = Agent(
            role='Lead Commodities Quant Strategist',
            goal='Translate geopolitical risk into measurable commodity market forecasts.',
            backstory='You operate at the intersection of international trade policy and algorithmic trading. You forecast supply elasticities and price volatility for energy and agriculture.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return historian, quant_strategist

    def run_analysis(self, breaking_headline: str):
        """The core dynamic execution pipeline. Resolves inputs at runtime."""
        
        # 1. Fetch the grounding truth from ChromaDB dynamically
        historical_matches = self.db.query_historical_context(breaking_headline, max_results=1)
        
        if historical_matches:
            context_data = historical_matches[0]
            context_str = f"Event: {context_data['associated_event']}\nRegime: {context_data['regime_impact']}\nDetails: {context_data['text']}"
        else:
            # Resilient fallback handler if no database coordinates match
            context_str = "No close historical precedent found in local archives."

        # 2. Spawn the specialized agent nodes
        historian, quant = self._create_agents()

        # 3. Compile Dynamic Tasks via Python f-strings
        research_task = Task(
            description=f"""
            Analyze this breaking headline: '{breaking_headline}'.
            Use this extracted historical data as your absolute factual precedent: 
            ---
            {context_str}
            ---
            Synthesize how this past crisis mirrors or differs from the current headline.
            """,
            expected_output="A structured 2-paragraph briefing analyzing the geopolitical gravity and escalation risks.",
            agent=historian
        )

        strategy_task = Task(
            description="""
            Review the Historian's briefing. Map out the direct economic consequences this event will impose on relevant commodity markets (like oil, gas, or agriculture) over the next 14 days.
            """,
            expected_output="A clear, bulleted risk assessment including expected price volatility direction and supply chain impacts.",
            agent=quant
        )

        # 4. Bind into an orchestration container and execute sequentially
        crew = Crew(
            agents=[historian, quant],
            tasks=[research_task, strategy_task],
            process=Process.sequential
        )

        final_result = crew.kickoff()
        return final_result

# --- Local Terminal Test Framework ---
if __name__ == "__main__":
    geopulse = GeoPulseIntelligenceCrew()
    test_headline = "Unidentified armed drones have targeted two commercial oil vessels in the Red Sea, causing major shipping lines to halt transit."
    
    print("\n⚡ Kicking off Backend Execution Test...")
    final_report = geopulse.run_analysis(test_headline)
    print("\n==================================================")
    print(final_report)