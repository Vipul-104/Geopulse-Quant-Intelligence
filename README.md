# 🦅 GeoPulse Quant Intelligence Terminal

> An enterprise-grade, RAG-grounded multi-agent intelligence system running sequential CrewAI workflows on Groq LPUs to synthesize real-time commodity market risk matrices.

---

## Overview

GeoPulse Quant Intelligence Terminal is an AI-powered geopolitical risk analysis platform. It ingests breaking geopolitical events, performs semantic retrieval against a vector archive of historical precedents, and deploys a dual-agent sequential pipeline to produce executive-grade commodity market risk assessments.

**Built for:** Quantitative analysts, commodity traders, and risk intelligence teams who need rapid, grounded assessments of how geopolitical shocks translate into market exposure.

---

## Architecture

```
User Input (Breaking Event)
        │
        ▼
Semantic Embedding (sentence-transformers)
        │
        ▼
ChromaDB Vector Store ◄── Historical Risk Archive
        │
        ▼
CrewAI Sequential Workflow
   ├── Agent 01: Senior Geopolitical Historian
   │       └── Retrieves & contextualizes historical analogues
   └── Agent 02: Lead Commodities Quant Strategist
           └── Maps geopolitical risk → commodity market impact
        │
        ▼
Executive Asset Risk Assessment Report (Streamlit UI)
```

**Compute Layer:** Groq LPU cluster (low-latency inference)  
**Orchestration:** CrewAI framework  
**Vector DB:** ChromaDB persistent store  
**Frontend:** Streamlit

---

## Features

- **RAG-Grounded Analysis** — every output is anchored to retrieved historical precedents, not hallucinated
- **Dual-Agent Pipeline** — geopolitical historian + quant strategist agents run sequentially for layered insight
- **Groq LPU Inference** — ultra-low latency completions via Groq's hardware-accelerated API
- **ChromaDB Vector Store** — persistent semantic search across a curated risk archive
- **Streamlit Intel Terminal** — classified-operations-room UI for dispatch input and report rendering

---

## Project Structure

```
Geopulse-Quant-Intelligence/
├── app.py                  # Streamlit frontend — main entry point
├── requirements.txt        # Python dependencies
├── .gitignore
├── src/
│   └── crew.py             # CrewAI agent definitions and workflow logic
├── data/                   # Raw source documents for vector ingestion
└── vector_store/           # ChromaDB persistent embeddings
```

---

## Quickstart

### Prerequisites

- Python 3.10+
- [Groq API key](https://console.groq.com/)
- (Optional) OpenAI-compatible key if using `langchain-openai` fallback

### Installation

```bash
git clone https://github.com/Vipul-104/Geopulse-Quant-Intelligence.git
cd Geopulse-Quant-Intelligence
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here   # if required by langchain-openai
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

1. Enter a breaking geopolitical event or scenario in the **INCOMING COMMAND DISPATCH** field.
   - Example: *"Unidentified drone activity forces sudden shipping halts near critical maritime channels"*
2. Click **RUN INTELLIGENCE WORKFLOW**.
3. The system will:
   - Embed the input and query ChromaDB for historical analogues
   - Run Agent 01 (Geopolitical Historian) → Agent 02 (Quant Strategist) sequentially
   - Render an **Executive Asset Risk Assessment Report**

---

## Dependencies

| Package | Role |
|---|---|
| `crewai` | Multi-agent orchestration |
| `langchain-openai` | LLM interface layer |
| `chromadb` | Persistent vector store |
| `sentence-transformers` | Semantic embedding generation |
| `streamlit` | Frontend UI |
| `python-dotenv` | Environment variable management |
| `pydantic` | Data validation |
| `fastapi` / `uvicorn` | API layer (optional backend) |
| `gTTS` | Text-to-speech (optional audio output) |

---

## Intelligence Nodes

| Node | Role |
|---|---|
| 🛡️ **Node 01 — Senior Geopolitical Historian** | Retrieves closest historical precedents from vector archive; contextualizes the current event |
| 📊 **Node 02 — Lead Commodities Quant Strategist** | Translates geopolitical risk vectors into commodity exposure matrices and price impact forecasts |

---

## Roadmap

- [ ] Live news feed ingestion (RSS/NewsAPI → auto-dispatch)
- [ ] Expanded vector archive (energy, agriculture, metals)
- [ ] PDF report export
- [ ] Multi-scenario stress testing mode
- [ ] WebSocket streaming for real-time agent output

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Vipul** — [@Vipul-104](https://github.com/Vipul-104)

---

> *"Data grounded through local vector assets. Treat output as predictive risk model."*
