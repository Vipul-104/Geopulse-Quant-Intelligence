"""
Structured output models for GeoPulse Quant Intelligence.
All agent outputs are parsed into these Pydantic schemas for
consistent rendering, export, and downstream processing.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MODERATE = "MODERATE"
    LOW      = "LOW"
    MINIMAL  = "MINIMAL"


class PriceDirection(str, Enum):
    SHARP_RISE   = "SHARP RISE"
    MODERATE_RISE = "MODERATE RISE"
    STABLE        = "STABLE"
    MODERATE_FALL = "MODERATE FALL"
    SHARP_FALL    = "SHARP FALL"


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "VERY HIGH"
    HIGH      = "HIGH"
    MODERATE  = "MODERATE"
    LOW       = "LOW"
    UNCERTAIN = "UNCERTAIN"


# ─────────────────────────────────────────────
# Sub-models
# ─────────────────────────────────────────────

class CommodityImpact(BaseModel):
    """Price & supply impact for a single commodity."""
    name: str = Field(description="Commodity name, e.g. 'Brent Crude Oil'")
    ticker_hint: str = Field(description="Common ticker or code, e.g. 'BZ', 'XAU', 'CBOT-W'")
    price_direction: PriceDirection = Field(description="Expected directional move over 14 days")

    # Numeric range (signed floats, e.g. -3.5 to +15.0). Negative = downside move.
    expected_move_pct_min: float = Field(description="Lower bound of expected % price move over 14 days, signed")
    expected_move_pct_max: float = Field(description="Upper bound of expected % price move over 14 days, signed")

    # Extra quant fields
    volatility_index: int = Field(ge=0, le=100, description="0-100 implied volatility score vs normal baseline")
    historical_avg_move_pct: float = Field(description="Average % move seen in the matched historical precedent for this commodity")
    supply_elasticity_score: int = Field(ge=0, le=100, description="0-100, higher = more inelastic / harder to substitute supply")

    supply_chain_impact: str = Field(description="1-sentence supply chain consequence")
    confidence: ConfidenceLevel = Field(description="Model confidence in this commodity forecast")

    @property
    def expected_move_pct_mid(self) -> float:
        return round((self.expected_move_pct_min + self.expected_move_pct_max) / 2, 1)


class GeopoliticalRiskMatrix(BaseModel):
    """Output from Node 01 – Senior Geopolitical Historian."""
    headline_summary: str = Field(description="One-sentence restatement of the breaking event")
    overall_risk_level: RiskLevel = Field(description="Aggregate geopolitical risk classification")
    risk_score: int = Field(ge=0, le=100, description="Quantified risk score 0-100")
    escalation_probability_pct: int = Field(ge=0, le=100, description="Probability of further escalation within 30 days (%)")
    historical_precedent_event: str = Field(description="Name of the closest matched historical crisis")
    historical_precedent_year: Optional[str] = Field(default=None, description="Year(s) of the historical precedent")
    key_parallels: list[str] = Field(description="3-5 bullet parallels between current event and precedent")
    structural_differences: list[str] = Field(description="2-3 bullet ways the current event differs from precedent")
    geopolitical_actors: list[str] = Field(description="Primary state and non-state actors involved")
    choke_points_at_risk: list[str] = Field(description="Maritime, energy, or logistical choke points threatened")
    analyst_note: str = Field(description="2-3 sentence qualitative judgment from the historian")


class QuantRiskBriefing(BaseModel):
    """Output from Node 02 – Lead Commodities Quant Strategist."""
    primary_commodity_affected: str = Field(description="Single most impacted commodity")
    commodity_impacts: list[CommodityImpact] = Field(
        min_length=2, max_length=6,
        description="Ranked list of impacted commodities with forecasts"
    )
    supply_disruption_severity: RiskLevel = Field(description="Overall supply disruption classification")
    estimated_disruption_duration_days: int = Field(ge=1, description="Best-estimate disruption window in days")
    macro_regime_shift: bool = Field(description="True if this event could trigger a sustained macro regime change")
    tail_risk_scenario: str = Field(description="Worst-case scenario description in 1-2 sentences")
    trading_considerations: list[str] = Field(
        description="3-5 structured trading considerations (NOT financial advice)"
    )
    sectors_to_monitor: list[str] = Field(description="Equity sectors most exposed")
    overall_confidence: ConfidenceLevel = Field(description="Quant's overall confidence in this briefing")
    quant_note: str = Field(description="2-3 sentence quant judgment on model reliability")


class IntelligenceBriefing(BaseModel):
    """
    Master structured output merging both agent reports.
    This is what gets rendered in the UI and exported.
    """
    headline: str = Field(description="Original user-submitted headline")
    timestamp: str = Field(description="ISO8601 timestamp of analysis")
    geopolitical_analysis: GeopoliticalRiskMatrix
    commodity_analysis: QuantRiskBriefing
    executive_summary: str = Field(
        description="3-5 sentence executive summary synthesizing both analyses"
    )
    confidence_disclaimer: str = Field(
        description="Standard disclaimer about AI-generated forecast limitations"
    )

    # Convenience computed helpers (not from LLM)
    @property
    def risk_badge_color(self) -> str:
        colors = {
            RiskLevel.CRITICAL: "#E24B4A",
            RiskLevel.HIGH:     "#EF9F27",
            RiskLevel.MODERATE: "#639922",
            RiskLevel.LOW:      "#1D9E75",
            RiskLevel.MINIMAL:  "#888780",
        }
        return colors.get(self.geopolitical_analysis.overall_risk_level, "#888780")
