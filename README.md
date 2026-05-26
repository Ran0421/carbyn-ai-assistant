# Carbyn AI — Industrial Maintenance Assistant

> Multimodal AI assistant for hands-free factory workers. Upload an equipment image, ask a question, get step-by-step guidance grounded in real technical manuals — read aloud via TTS.

---

## Demo
Upload an image of a circuit breaker, electrical panel, or any industrial equipment → ask "why is this tripping?" → get structured diagnosis + action steps cited from the actual manual.

---

## Features
- **Vision analysis** — Groq Llama-4 Scout 17B identifies equipment type, anomalies, and faults from images
- **RAG retrieval** — ChromaDB retrieves relevant sections from indexed PDF manuals before answering
- **Structured response** — every answer follows: What I see → Diagnosis → Action steps → Manual reference
- **Text-to-speech** — gTTS reads the diagnosis and steps aloud for hands-free use
- **FastAPI backend** — clean REST API with Pydantic validation and OpenAPI docs at /docs
- **Streamlit frontend** — simple UI with image upload, text query, and audio playback

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM / Vision | Groq Llama-4 Scout 17B 16E Instruct |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local) |
| Vector store | ChromaDB (persistent, no Docker needed) |
| RAG framework | LangChain + langchain-chroma |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| TTS | gTTS |
| PDF loading | LangChain PyPDFDirectoryLoader |

---

## Setup

### 1. Clone and install
```bash
git clone https://github.com/Ran0421/carbyn-ai-assistant.git
cd carbyn-ai-assistant
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Add your GROQ_API_KEY from https://console.groq.com/keys
```

### 3. Add manuals and ingest
```bash
# Drop PDF manuals into data/manuals/
python rag_ingest.py
```

### 4. Run
```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload

# Terminal 2 — frontend
streamlit run frontend/app.py
```

Visit http://localhost:8501

---

## Project Structure
```
carbyn-ai-assistant/
├── backend/
│   ├── main.py                     # FastAPI app
│   ├── api/
│   │   └── routes.py               # /analyze endpoint
│   ├── models/
│   │   └── response_model.py       # Pydantic response schema
│   ├── services/
│   │   ├── assistant_service.py    # RAG + Groq vision pipeline
│   │   └── vision_service.py       # standalone image analysis
│   └── utils/
│       └── file_handler.py         # temp file management
├── frontend/
│   └── app.py                      # Streamlit UI
├── data/manuals/                   # PDF manuals (not tracked)
├── vectorstore/                    # ChromaDB vectors (not tracked)
├── rag_ingest.py                   # PDF ingestion script
├── requirements.txt
└── .env.example
```

---

## Architecture

```
[ Streamlit Frontend ]
        |  HTTP
        v
[ FastAPI  /analyze ]
        |
   +---------+----------+
   |                    |
[ RAG Service ]   [ Vision Service ]
[ ChromaDB    ]   [ Groq Llama-4   ]
[ MiniLM-L6   ]   [ Scout 17B      ]
        |
[ PDF Manuals ]
```

Pipeline per request:
1. Image + query arrive at POST /analyze
2. ChromaDB retrieves top-2 relevant manual chunks
3. RAG context + image sent together to Groq vision model
4. Structured response parsed into vision analysis, diagnosis, action steps, manual reference
5. gTTS converts diagnosis + steps to audio

---

## What I'd Improve
- Streaming responses for lower perceived latency
- Whisper STT for full voice input (already wired in voice_service.py)
- Session memory for multi-turn conversation per technician
- Edge deployment with quantised models for fully offline use
- Per-technician auth and session isolation for production

---

## Author
Ranjeeta Mashal 