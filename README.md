# 🦅 GeoPulse Quant Intelligence

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-purple?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LPU%20Inference-orange?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-green?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-teal?style=for-the-badge)

**Agentic AI system that transforms breaking geopolitical headlines into structured commodity risk intelligence briefings — in under 60 seconds.**

[Features](#features) • [Architecture](#architecture) • [Setup](#setup) • [Usage](#usage) • [PDF Export](#pdf-export) • [Tech Stack](#tech-stack)

</div>

---

## 🎯 What is GeoPulse?

GeoPulse Quant Intelligence is an open-source, AI-powered geopolitical risk analysis terminal. Paste a breaking news headline — drone strikes, maritime disruptions, sanctions, wars — and the system automatically:

- 🔍 **Retrieves** the top-3 most similar historical crisis precedents from a curated vector archive
- 🧠 **Deploys** 3 sequential AI agents to analyze risk, forecast commodity impacts, and synthesize an executive briefing
- 📊 **Returns** a fully structured, typed intelligence briefing with risk scores, commodity price forecasts, and PDF export

> **No Bloomberg Terminal. No analyst team. Just AI.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🛡️ RAG-Grounded Analysis | Top-3 historical precedents retrieved via cosine similarity from ChromaDB |
| 🤖 3-Node Agent Pipeline | Historian → Quant Strategist → Synthesizer, powered by Groq LPU |
| 📐 Structured Typed Output | All outputs enforced via Pydantic v2 schemas — no hallucinated formats |
| 📈 Commodity Forecasts | Per-commodity min/max % price move, volatility index (0-100), supply elasticity |
| 🎨 Neon Volatility UI | Commodity cards colored by volatility score — green/orange/red |
| 📄 Professional PDF Export | White-background, print-ready PDF with full briefing layout |
| 💾 Session History | Last 5 analyses stored in session, revisit any past briefing |
| ⚡ Groq LPU Speed | 10x faster inference vs GPU-based APIs — real-time multi-agent pipeline |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    app.py — Streamlit UI                 │
│     Headline Input → Run Workflow → Structured Dashboard │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  src/models.py — Pydantic                │
│    IntelligenceBriefing · RiskMatrix · CommodityImpact  │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  src/crew.py — CrewAI                    │
│         Sequential 3-Agent Pipeline on Groq LPU         │
├────────────────┬────────────────┬───────────────────────┤
│   Node 01      │   Node 02      │   Node 03             │
│  Historian     │  Quant Strat   │  Synthesizer          │
│  Risk Matrix   │  Commodity     │  Executive            │
│  JSON Output   │  Forecasts     │  Summary              │
└────────────────┴───────┬────────┴───────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  src/db.py — ChromaDB                    │
│   Sentence Transformers · Cosine Similarity · HNSW      │
│   Top-3 Historical Precedents Retrieved Per Query       │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              data/raw_history.json                       │
│   25 Curated Historical Crisis Profiles (1973–2024)     │
└─────────────────────────────────────────────────────────┘
```

---

## 📄 PDF Export

The system generates a professional, print-ready PDF briefing:

```
┌─────────────────────────────────────────────┐
│  GEOPULSE QUANT INTELLIGENCE  [dark header] │
├─────────────────────────────────────────────┤
│  INCOMING HEADLINE                          │
│  ─────────────────────────────────────────  │
│  ┌─ EXECUTIVE SUMMARY (risk-colored box) ─┐ │
│  │ Risk: HIGH | Score: 78/100            │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [RISK SCORE] [ESCALATION] [SUPPLY] [DAYS] │
│                                             │
│  GEOPOLITICAL RISK MATRIX                  │
│  + Key Parallels (green)                   │
│  - Structural Differences (red)            │
│  Actors | Choke Points                     │
│                                             │
│  COMMODITY IMPACT TABLE                    │
│  ┌─ Brent Crude ────────────────────────┐  │
│  │ +8.0% to +15.0% (mid +11.5%)       │  │
│  │ Vol: 58/100 | Hist: +9.8%          │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  TAIL RISK (red box)                       │
│  TRADING CONSIDERATIONS                    │
└─────────────────────────────────────────────┘
```

---

## 🚀 Setup

### Prerequisites
- Python 3.11+
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/Vipul-104/Geopulse-Quant-Intelligence.git
cd Geopulse-Quant-Intelligence

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 5. Run the app
streamlit run app.py
```

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 📖 Usage

1. **Start the app** — `streamlit run app.py`
2. **Seed the database** — Click "Seed / Re-seed DB" on first run
3. **Paste a headline** — Any breaking geopolitical event
4. **Click "Run Intelligence Workflow"** — Wait 20-40 seconds
5. **View the briefing** — Risk scores, commodity forecasts, executive summary
6. **Export PDF** — Click "Export Briefing (PDF)" for a print-ready report

### Example Headlines to Try

```
Unidentified armed drones have targeted two commercial oil vessels 
in the Red Sea, causing major shipping lines to halt transit.

Russia suspends natural gas pipeline flows to Europe citing 
technical maintenance issues amid escalating sanctions dispute.

China imposes export controls on rare earth minerals critical 
for semiconductor and electric vehicle battery manufacturing.
```

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | LLaMA 3.3-70B via Groq | Agent reasoning |
| Agent Framework | CrewAI | Multi-agent orchestration |
| Vector Store | ChromaDB | Historical precedent retrieval |
| Embeddings | Sentence Transformers (MiniLM-L6) | Semantic similarity |
| Structured Output | Pydantic v2 | Typed JSON schema enforcement |
| UI | Streamlit + Plotly | Dashboard + charts |
| PDF Export | ReportLab Platypus | Professional report generation |
| Language | Python 3.11 | Core runtime |

---

## 📊 Structured Output Schema

Every analysis returns a fully typed `IntelligenceBriefing` object:

```python
IntelligenceBriefing(
    headline: str,
    timestamp: str,
    geopolitical_analysis: GeopoliticalRiskMatrix(
        overall_risk_level: RiskLevel,      # CRITICAL/HIGH/MODERATE/LOW/MINIMAL
        risk_score: int,                     # 0-100
        escalation_probability_pct: int,     # 0-100
        historical_precedent_event: str,
        key_parallels: list[str],
        structural_differences: list[str],
        geopolitical_actors: list[str],
        choke_points_at_risk: list[str],
    ),
    commodity_analysis: QuantRiskBriefing(
        commodity_impacts: list[CommodityImpact(
            name: str,
            expected_move_pct_min: float,    # signed, e.g. +8.0
            expected_move_pct_max: float,    # signed, e.g. +15.0
            volatility_index: int,           # 0-100
            historical_avg_move_pct: float,
            supply_elasticity_score: int,    # 0-100
            confidence: ConfidenceLevel,
        )],
        tail_risk_scenario: str,
        macro_regime_shift: bool,
    ),
    executive_summary: str,
)
```

---

## 🗂️ Project Structure

```
Geopulse-Quant-Intelligence/
├── app.py                  # Streamlit UI dashboard
├── requirements.txt        # Dependencies
├── .env                    # API keys (not committed)
├── .streamlit/
│   └── config.toml         # Streamlit config (no file watcher)
├── src/
│   ├── __init__.py
│   ├── crew.py             # CrewAI 3-agent pipeline
│   ├── db.py               # ChromaDB vector store
│   ├── models.py           # Pydantic output schemas
│   └── pdf_export.py       # ReportLab PDF generation
├── data/
│   └── raw_history.json    # 25 historical crisis profiles
└── vector_store/           # ChromaDB persistent storage
```

---

## 🌍 Historical Crisis Archive

The system includes 25 curated geopolitical crisis profiles spanning 1973–2024:

- 1973 Arab Oil Embargo
- 1979 Iranian Revolution
- 1990 Gulf War
- 2001 September 11 Attacks
- 2008 Global Financial Crisis
- 2011 Arab Spring
- 2019 Saudi Aramco Abqaiq Attack
- 2019 Strait of Hormuz Tanker Attacks
- 2022 Russia-Ukraine War
- 2023 Red Sea Houthi Attacks
- *...and 15 more*

---

## 🔮 Future Scope

- [ ] Live web search agent — real-time news grounding
- [ ] Validator agent — 4th agent that critiques outputs
- [ ] Live commodity price feed (Yahoo Finance / Alpha Vantage)
- [ ] Cloud deployment (AWS / GCP)
- [ ] REST API for third-party integration
- [ ] Fine-tuned domain-specific LLM on crisis datasets

---

## 👤 Author

**Vipul Barmukh** 

---

## ⚠️ Disclaimer

This system is for research and educational purposes only. All outputs are AI-generated and should be verified against official sources before any decision-making. This is not financial advice.

---

<div align="center">
Built with ❤️ using CrewAI · Groq · ChromaDB · Streamlit
</div>
