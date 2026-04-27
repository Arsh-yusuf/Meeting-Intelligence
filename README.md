# Meeting Intelligence AI

A modular, scalable multi-agent system designed to ingest meeting transcripts, analyze them using a Map-Reduce RAG architecture, and automatically synchronize insights with project management tools like ClickUp.

## 🚀 Overview

This project transforms raw meeting recordings (transcripts) into actionable project intelligence. It uses a **Master-Slave Agent Architecture** to ensure high-fidelity analysis across any number of meetings.

### Key Features
- **Map-Reduce Summarization**: Every meeting is summarized individually before being aggregated into a master report, ensuring 100% data coverage.
- **RAG Architecture**: Uses FAISS vector storage for semantic retrieval of meeting context.
- **Multi-Agent Orchestration**: Powered by LangGraph to coordinate specialized agents for Summarization, Keyword Extraction, and Taxonomy Building.
- **ClickUp Integration**: Automatically pushes consolidated intelligence reports to ClickUp tasks via API.
- **Parallel Generation**: Includes a high-speed dummy data generator for rapid testing and prototyping.
- **LangServe API**: Exposes the full pipeline as a REST + Streaming API via FastAPI.
- **Dockerized**: Fully containerized backend and Next.js frontend.

## 🛠️ Tech Stack
- **Framework**: LangChain, LangGraph, LangServe
- **Vector Database**: FAISS (Local, upgradeable to ChromaDB)
- **LLM**: OpenAI / OpenRouter
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **API Server**: FastAPI + Uvicorn
- **Frontend**: LangChain Next.js Template
- **Containerization**: Docker + Docker Compose

## 📁 Project Structure
```text
├── agents/            # Specialized AI Agents (Summarizer, Taxonomy, ClickUp)
├── sources/           # Data Ingestion Providers (Fathom, Dummy, Base)
├── rag/               # RAG Pipeline (Ingestion, Retrieval, Vector Store)
├── config/            # System Configuration & Settings
├── data/              # Persistent Storage (JSON & Vector Index)
├── frontend/          # Next.js frontend (cloned from LangChain template)
├── server.py          # LangServe API server (FastAPI)
├── main.py            # CLI entry point (unchanged)
├── Dockerfile         # Backend container definition
└── docker-compose.yml # Orchestrates backend + frontend
```

## ⚙️ Setup Instructions

### Option A: Local (CLI)

1. **Clone the repository** and navigate to the root directory.
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment** — create a `.env` file:
   ```env
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   MODEL=meta-llama/llama-3-8b-instruct
   CLICKUP_API_KEY=your_clickup_key
   CLICKUP_TASK_ID=your_task_id
   ```
5. **Run the CLI pipeline**:
   ```bash
   python main.py
   ```

---

### Option B: Docker (API + Frontend)

#### Step 1 — Clone the Next.js frontend template
```bash
git clone https://github.com/langchain-ai/langchain-nextjs-template ./frontend
```

#### Step 2 — Ensure your `.env` file is populated (see above)

#### Step 3 — Build and start all services
```bash
docker-compose up --build
```

#### Step 4 — Access the services
| Service  | URL |
|----------|-----|
| Backend API (Swagger UI) | http://localhost:8000/docs |
| Backend Health Check | http://localhost:8000/health |
| Analyze Endpoint | http://localhost:8000/analyze/invoke |
| Frontend | http://localhost:3000 |

#### Step 5 — Run the CLI inside Docker (optional)
```bash
docker-compose exec backend python main.py
```

---

### API Usage (LangServe)

Send a POST request to analyze your meetings:
```bash
curl -X POST http://localhost:8000/analyze/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"query": "Summarize all trending topics from recent meetings."}}'
```

## 📄 License
MIT
