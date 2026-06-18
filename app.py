import warnings
import os

# Suppress background framework warnings to keep terminal logs clean for interviewers
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import streamlit as st
from src.crew import GeoPulseIntelligenceCrew

# Set executive page configurations with an operations room layout
st.set_page_config(
    page_title="GeoPulse Quant - Intel Terminal",
    page_icon="🦅",
    layout="wide"
)

# Application Header UI - Geopolitical Terminal Theme
st.title("🦅 GEOPULSE QUANT INTELLIGENCE TERMINAL")
st.caption("INTERNAL USE ONLY — CLASSIFIED RISK ARCHIVE AND FORECASTING DECK")
st.markdown("---")

st.write(
    "**Operating Protocol:** Input real-time tactical updates or breaking geopolitical developments. "
    "The system embeds the payload, executes a semantic query against historical vector archives, "
    "and deploys dual-agent sequential analysis loops via localized LPU infrastructure."
)

# Sidebar Setup - Technical Specification Matrix
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop", caption="GeoPulse Core V2.0")
    st.markdown("### 🖥️ SYSTEM INFRASTRUCTURE")
    st.info("**Orchestration:** CrewAI Framework")
    st.error("**Compute Layer:** Groq Shared LPU Cluster")
    st.success("**Vector Database:** ChromaDB Persistent Store")
    
    st.markdown("---")
    st.markdown("### 👥 ACTIVE INTELLIGENCE NODES")
    st.markdown("🛡️ **Node 01:** Senior Geopolitical Historian")
    st.markdown("📊 **Node 02:** Lead Commodities Quant Strategist")

# User Input Text Field — Designed like an intelligence dispatch window
user_headline = st.text_area(
    "📥 INCOMING COMMAND DISPATCH / BREAKING GEOPOLITICAL FLASH:",
    height=120,
    placeholder="Enter breaking scenario (e.g., Unidentified drone activity forces sudden shipping halts near critical maritime channels...)"
)

# Execution Trigger Button
if st.button("RUN INTELLIGENCE WORKFLOW", use_container_width=True):
    if not user_headline.strip():
        st.warning("🚨 SYSTEM ALERT: Incoming dispatch string cannot be empty. Input payload data.")
    else:
        # Create a persistent wrapper outside the status box so the final layout does not collapse
        report_placeholder = st.container()
        
        # Professional operational logs
        with st.status("Executing system pipeline...", expanded=True) as status:
            st.write("🛰️ Generating semantic tensor embeddings...")
            st.write("🔍 Extracting closest historical precedent coordinates from ChromaDB...")
            st.write("⚡ Patching caching headers and initializing agent hand-offs...")
            
            try:
                # Initialize the backend engine
                crew_engine = GeoPulseIntelligenceCrew()
                
                # Execute dynamic analytics loop
                final_briefing = crew_engine.run_analysis(user_headline)
                
                # Collapse loading status cleanly upon successful delivery
                status.update(label="✅ Analysis pipeline successfully completed.", state="complete", expanded=False)
                
                # Force the output to print onto the persistent main screen element
                with report_placeholder:
                    st.markdown("---")
                    st.subheader("📋 EXECUTIVE ASSET RISK ASSESSMENT REPORT")
                    st.info(final_briefing)
                    st.markdown("---")
                    st.caption("🔒 End of Dispatch. Data grounded through local vector assets. Treat output as predictive risk model.")
                
            except Exception as e:
                status.update(label="❌ Pipeline execution aborted due to an internal system error.", state="error")
                st.error(f"Critical System Interruption: {e}")