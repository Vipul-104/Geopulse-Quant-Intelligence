"""
GeoPulse Quant Intelligence Terminal – upgraded app.py

Upgrades from v1:
  • Renders structured IntelligenceBriefing (not raw string)
  • Risk score gauge, commodity impact table, actor/choke-point chips
  • Parallel / key-difference cards
  • Confidence badges per commodity
  • Export to JSON button
  • Session history (last 5 analyses stored in st.session_state)
  • Sidebar shows DB health stats
  • Clean warning suppression
"""

import warnings
import os
import json
from datetime import datetime
from src.pdf_export import generate_briefing_pdf

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import streamlit as st
import plotly.graph_objects as go
from src.crew import GeoPulseIntelligenceCrew
from src.db import GeopoliticalVectorStore
from src.models import IntelligenceBriefing, RiskLevel, ConfidenceLevel, PriceDirection
from src.news_feed import fetch_live_headlines

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="GeoPulse Quant – Intel Terminal",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Styling helpers
# ─────────────────────────────────────────────

RISK_COLORS = {
    RiskLevel.CRITICAL: ("#E24B4A", "#fff"),
    RiskLevel.HIGH:     ("#EF9F27", "#fff"),
    RiskLevel.MODERATE: ("#639922", "#fff"),
    RiskLevel.LOW:      ("#1D9E75", "#fff"),
    RiskLevel.MINIMAL:  ("#888780", "#fff"),
}

DIRECTION_EMOJI = {
    PriceDirection.SHARP_RISE:    "🔺🔺",
    PriceDirection.MODERATE_RISE: "🔺",
    PriceDirection.STABLE:        "➡️",
    PriceDirection.MODERATE_FALL: "🔻",
    PriceDirection.SHARP_FALL:    "🔻🔻",
}

CONFIDENCE_COLORS = {
    ConfidenceLevel.VERY_HIGH: "🟢",
    ConfidenceLevel.HIGH:      "🟢",
    ConfidenceLevel.MODERATE:  "🟡",
    ConfidenceLevel.LOW:       "🟠",
    ConfidenceLevel.UNCERTAIN: "🔴",
}


def risk_badge(level: RiskLevel, score: int | None = None) -> str:
    bg, fg = RISK_COLORS.get(level, ("#888", "#fff"))
    label = f"{level.value}" + (f" ({score}/100)" if score is not None else "")
    return f'<span style="background:{bg};color:{fg};padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem">{label}</span>'


def chip(text: str, color: str = "#374151") -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
        f'padding:3px 10px;border-radius:14px;font-size:0.8rem;margin:2px;display:inline-block">'
        f'{text}</span>'
    )


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
@st.cache_resource
def get_crew_engine():
    return GeoPulseIntelligenceCrew()

if "crew_engine" not in st.session_state:
    st.session_state.crew_engine = get_crew_engine()
    
if "history" not in st.session_state:
    st.session_state.history: list[IntelligenceBriefing] = []

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🦅 GEOPULSE QUANT")
    st.caption("INTERNAL USE ONLY — CLASSIFIED RISK ARCHIVE")
    st.markdown("---")

    # DB health
    try:
        db_temp = GeopoliticalVectorStore()
        stats = db_temp.get_collection_stats()
        st.markdown("### 🖥️ SYSTEM STATUS")
        st.success(f"**Vector DB:** {stats['total_profiles']} profiles indexed")
        st.info("**Embedding:** all-mpnet-base-v2")
        st.error("**Compute:** Groq LPU — llama-3.3-70b-versatile")
        st.success("**RAG depth:** Top-3 precedents")
    except Exception as e:
        st.warning(f"DB status check failed: {e}")

    st.markdown("---")
    st.markdown("### 👥 ACTIVE NODES")
    st.markdown("🛡️ **Node 01** — Sr. Geopolitical Historian")
    st.markdown("📊 **Node 02** — Lead Commodities Quant")
    st.markdown("🧠 **Node 03** — Chief Intel Synthesizer")

    st.markdown("---")
    # Session history
    if st.session_state.history:
        st.markdown("### 📋 SESSION HISTORY")
        for i, past in enumerate(reversed(st.session_state.history[-5:])):
            level = past.geopolitical_analysis.overall_risk_level
            bg, _ = RISK_COLORS.get(level, ("#888", "#fff"))
            ts = past.timestamp[:16].replace("T", " ")
            if st.button(f"[{level.value}] {past.headline[:38]}…", key=f"hist_{i}"):
                st.session_state.active_briefing = past


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────

st.title("🦅 GEOPULSE QUANT INTELLIGENCE TERMINAL")
st.caption("INTERNAL USE ONLY — CLASSIFIED RISK ARCHIVE AND FORECASTING DECK")
st.markdown("---")

st.markdown(
    "**Operating Protocol:** Input a breaking geopolitical development. "
    "The system embeds the payload, executes semantic retrieval across historical archives "
    "(top-3 precedents), and deploys a 3-node sequential agent loop on Groq LPUs — "
    "returning a **fully structured risk intelligence briefing**."
)

# ─────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────

with st.expander("🛰️ Fetch live headlines (GDELT)", expanded=False):
    if st.button("🔄 Pull latest geopolitical/commodity headlines"):
        with st.spinner("Querying GDELT live news feed..."):
            try:
                st.session_state.live_headlines = fetch_live_headlines(max_results=10)
                if not st.session_state.live_headlines:
                    st.info("No matching headlines returned right now — try again shortly.")
            except RuntimeError as e:
                st.error(f"Live feed error: {e}")
                st.session_state.live_headlines = []

    if st.session_state.get("live_headlines"):
        options = [h["title"] for h in st.session_state.live_headlines]
        picked = st.selectbox("Select a live headline to load into the dispatch box:", options)
        if st.button("📥 Load selected headline"):
            st.session_state.loaded_headline = picked

user_headline = st.text_area(
    "📥 INCOMING COMMAND DISPATCH / BREAKING GEOPOLITICAL FLASH:",
    height=120,
    value=st.session_state.get("loaded_headline", ""),
    placeholder=(
        "e.g. Unidentified drone activity forces sudden shipping halts "
        "near critical maritime channels in the Strait of Hormuz..."
    ),
)

col_run, col_seed = st.columns([3, 1])
with col_run:
    run_clicked = st.button("⚡ RUN INTELLIGENCE WORKFLOW", use_container_width=True, type="primary")
with col_seed:
    seed_clicked = st.button("🌱 Seed / Re-seed DB", use_container_width=True)

if seed_clicked:
    with st.spinner("Seeding vector database from raw_history.json…"):
        try:
            db_s = GeopoliticalVectorStore()
            n = db_s.seed_database_from_json("data/raw_history.json")
            st.success(f"✅ {n} profiles indexed into ChromaDB.")
        except Exception as e:
            st.error(f"Seeding failed: {e}")


# ─────────────────────────────────────────────
# Render briefing
# ─────────────────────────────────────────────

def render_briefing(briefing: IntelligenceBriefing):
    geo  = briefing.geopolitical_analysis
    comm = briefing.commodity_analysis

    st.markdown("---")

    # ── Executive summary banner ──────────────────────────────────────────
    bg_color, _ = RISK_COLORS.get(geo.overall_risk_level, ("#888", "#fff"))
    st.markdown(
        f'<div style="background:{bg_color}18;border-left:5px solid {bg_color};'
        f'padding:16px 20px;border-radius:8px;margin-bottom:12px">'
        f'<p style="margin:0;font-size:0.9rem;font-weight:600;color:{bg_color}">EXECUTIVE SUMMARY</p>'
        f'<p style="margin:8px 0 0">{briefing.executive_summary}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Top KPI row ───────────────────────────────────────────────────────
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Risk Score", f"{geo.risk_score} / 100")
        st.markdown(risk_badge(geo.overall_risk_level), unsafe_allow_html=True)
    with kpi2:
        st.metric("Escalation Probability", f"{geo.escalation_probability_pct}%")
    with kpi3:
        sev_bg, _ = RISK_COLORS.get(comm.supply_disruption_severity, ("#888", "#fff"))
        st.metric("Supply Disruption", comm.supply_disruption_severity.value)
    with kpi4:
        st.metric("Est. Disruption Window", f"{comm.estimated_disruption_duration_days} days")
        if comm.macro_regime_shift:
            st.markdown("⚠️ **Macro regime shift possible**")

    st.markdown("---")

    # ── Geopolitical analysis ─────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.subheader("🛡️ Geopolitical Risk Matrix")

        st.markdown(f"**Precedent:** {geo.historical_precedent_event}" +
                    (f" ({geo.historical_precedent_year})" if geo.historical_precedent_year else ""))

        st.markdown("**Key Parallels**")
        for p in geo.key_parallels:
            st.markdown(f"✅ {p}")

        st.markdown("**Structural Differences**")
        for d in geo.structural_differences:
            st.markdown(f"⚠️ {d}")

        st.markdown("**Geopolitical Actors**")
        actors_html = " ".join(chip(a, "#185FA5") for a in geo.geopolitical_actors)
        st.markdown(actors_html, unsafe_allow_html=True)

        st.markdown("**Choke Points at Risk**")
        choke_html = " ".join(chip(c, "#A32D2D") for c in geo.choke_points_at_risk)
        st.markdown(choke_html, unsafe_allow_html=True)

        st.markdown(f"> 📝 *{geo.analyst_note}*")

    # ── Commodity impact table ────────────────────────────────────────────
    with col_right:
        st.subheader("📊 Commodity Impact Table")

        # Compute global max abs move for bar scaling
        all_moves = [
            max(abs(ci.expected_move_pct_min), abs(ci.expected_move_pct_max))
            for ci in comm.commodity_impacts
        ]
        global_max = max(all_moves) if all_moves else 10.0

        for ci in comm.commodity_impacts:
            conf_dot = CONFIDENCE_COLORS.get(ci.confidence, "⚪")
            dir_em   = DIRECTION_EMOJI.get(ci.price_direction, "➡️")

            # Neon color driven by volatility index
            v = ci.volatility_index
            if v <= 33:
                neon  = "#39FF14"
                glow  = "0 0 4px #39FF1444"
            elif v <= 66:
                neon  = "#FFD700"
                glow  = "0 0 4px #FFD70044"
            else:
                neon  = "#FF2D6B"
                glow  = "0 0 4px #FF2D6B44"

            min_pct = max(4, round(abs(ci.expected_move_pct_min) / global_max * 100, 1))
            max_pct = max(min_pct, round(abs(ci.expected_move_pct_max) / global_max * 100, 1))

            st.markdown(
                f'<div style="background:#0D0D0D;border:1px solid {neon}55;border-radius:10px;'
                f'padding:12px 16px;margin-bottom:12px;box-shadow:{glow}">'

                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-weight:700;color:{neon};letter-spacing:0.5px">{ci.name}</span>'
                f'<span style="font-size:0.75rem;color:#888;background:#1A1A1A;padding:2px 8px;border-radius:10px">{ci.ticker_hint}</span>'
                f'</div>'

                f'<div style="display:flex;gap:10px;align-items:center;margin:8px 0 4px;flex-wrap:wrap">'
                f'<span style="color:#ccc">{dir_em} {ci.price_direction.value}</span>'
                f'<span style="font-weight:700;font-size:1rem;color:{neon}">{ci.expected_move_pct_min:+.1f}% to {ci.expected_move_pct_max:+.1f}%</span>'
                f'<span style="font-size:0.78rem;color:#888">(mid {ci.expected_move_pct_mid:+.1f}%)</span>'
                f'<span style="color:#aaa">{conf_dot} {ci.confidence.value}</span>'
                f'</div>'

                f'<div style="background:#1A1A1A;border-radius:4px;height:6px;width:100%;position:relative;margin:8px 0">'
                f'<div style="background:{neon};opacity:0.3;border-radius:4px;height:6px;width:{min_pct}%;position:absolute;left:0"></div>'
                f'<div style="background:{neon};border-radius:4px;height:6px;width:{max_pct}%;position:absolute;left:0;box-shadow:0 0 3px {neon}66"></div>'
                f'</div>'

                f'<div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:6px">'
                f'<span style="color:#888">Volatility: <strong style="color:{neon}">{ci.volatility_index}/100</strong></span>'
                f'<span style="color:#888">Hist avg: <strong style="color:{neon}">{ci.historical_avg_move_pct:+.1f}%</strong></span>'
                f'<span style="color:#888">Elasticity: <strong style="color:{neon}">{ci.supply_elasticity_score}/100</strong></span>'
                f'</div>'

                f'<div style="font-size:0.82rem;color:#aaa;border-top:1px solid #222;padding-top:6px">{ci.supply_chain_impact}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("**Tail Risk Scenario**")
        st.error(f"🚨 {comm.tail_risk_scenario}")

    st.markdown("---")

    # ── Cross-commodity comparison chart ──────────────────────────────────
    st.subheader("📉 Cross-Commodity % Move Comparison (14-day forecast)")

    names    = [ci.name for ci in comm.commodity_impacts]
    mids     = [ci.expected_move_pct_mid for ci in comm.commodity_impacts]
    mins     = [ci.expected_move_pct_min for ci in comm.commodity_impacts]
    maxs     = [ci.expected_move_pct_max for ci in comm.commodity_impacts]
    err_low  = [m - lo for m, lo in zip(mids, mins)]
    err_high = [hi - m for hi, m in zip(maxs, mids)]
    colors   = ["#DC2626" if m < 0 else "#D97706" for m in mids]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=mids,
        marker_color=colors,
        error_y=dict(
            type="data",
            symmetric=False,
            array=err_high,
            arrayminus=err_low,
            color="#374151",
            thickness=1.5,
            width=4,
        ),
        text=[f"{m:+.1f}%" for m in mids],
        textposition="outside",
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Expected price move (%)",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.add_hline(y=0, line_width=1, line_color="#9CA3AF")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Trading considerations & sectors ──────────────────────────────────
    col_tc, col_sec = st.columns([1, 1], gap="medium")

    with col_tc:
        st.subheader("🔍 Trading Considerations")
        st.caption("These are risk factors to monitor — not financial advice.")
        for tc in comm.trading_considerations:
            st.markdown(f"• {tc}")

    with col_sec:
        st.subheader("📈 Sectors to Monitor")
        sec_html = " ".join(chip(s, "#3B6D11") for s in comm.sectors_to_monitor)
        st.markdown(sec_html, unsafe_allow_html=True)

        st.markdown("")
        st.markdown(f"> 📝 *{comm.quant_note}*")

    # ── Overall confidence & disclaimer ───────────────────────────────────
    st.markdown("---")
    conf_dot = CONFIDENCE_COLORS.get(comm.overall_confidence, "⚪")
    st.markdown(
        f"**Model Confidence:** {conf_dot} {comm.overall_confidence.value}  \n"
        f"🔒 *{briefing.confidence_disclaimer}*"
    )

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown("")
    from src.pdf_export import generate_briefing_pdf
    pdf_bytes = generate_briefing_pdf(briefing)
    st.download_button(
    label="⬇️ Export Briefing (PDF)",
    data=pdf_bytes,
    file_name=f"geopulse_briefing_{briefing.timestamp[:10]}.pdf",
    mime="application/pdf",
    )


# ─────────────────────────────────────────────
# Run workflow
# ─────────────────────────────────────────────

if run_clicked:
    if not user_headline.strip():
        st.warning("🚨 SYSTEM ALERT: Dispatch string cannot be empty.")
    else:
        report_area = st.container()

        with st.status("Executing intelligence pipeline...", expanded=True) as status:
            st.write("🛰️ Generating semantic tensor embeddings...")
            st.write("🔍 Querying top-3 historical precedents from ChromaDB...")
            st.write("🧠 Node 01 (Historian) — analyzing geopolitical risk...")
            st.write("📊 Node 02 (Quant) — building commodity impact matrix...")
            st.write("✍️ Node 03 (Synthesizer) — compiling executive briefing...")

            try:
                briefing = st.session_state.crew_engine.run_analysis(user_headline)
                st.session_state.active_briefing = briefing

                # Append to history (deduplicate by headline)
                existing_headlines = [b.headline for b in st.session_state.history]
                if user_headline not in existing_headlines:
                    st.session_state.history.append(briefing)

                status.update(
                    label="✅ Intelligence pipeline complete.",
                    state="complete",
                    expanded=False,
                )

            except Exception as e:
                status.update(label="❌ Pipeline aborted.", state="error")
                st.error(f"Critical error: {e}")
                st.stop()

# Render active briefing (from run or history click)
if "active_briefing" in st.session_state:
    render_briefing(st.session_state.active_briefing)
