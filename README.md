# Meeting Intelligence AI

A modular, scalable multi-agent system designed to ingest meeting transcripts, analyze them using a Map-Reduce RAG architecture, and automatically synchronize insights with project management tools like ClickUp.

## 🚀 Overview

This project transforms raw meeting recordings (transcripts) into actionable project intelligence. It uses a **Master-Slave Agent Architecture** to ensure high-fidelity analysis across any number of meetings.

### Key Features
- **Proactive Intelligence**: Analyzes and summarizes meetings the moment they are ingested, ensuring zero-latency responses for users.
- **Incremental Ingestion**: Only processes new meetings and intelligently updates the project-wide Master Report.
- **Hybrid RAG Architecture**: A unified retrieval system that provides the AI with both raw transcript context and high-level pre-processed insights.
- **Premium UI Overhaul**:
    - **Action Item Highlighting**: Automatically detects and styles task items as distinct cards.
    - **Collapsible Technical Views**: Neatly organizes complex data like Taxonomies into collapsible sections.
    - **Markdown Support**: Full support for rich text and structured formatting in AI responses.
- **ClickUp Integration**: Seamlessly syncs consolidated meeting intelligence with project tasks.
- **LangServe API**: Exposes the full proactive pipeline as a scalable API via FastAPI.

## 🛠️ Tech Stack
- **Framework**: LangChain, LangGraph, LangServe
- **Vector Database**: FAISS (Local, upgradeable to ChromaDB)
- **LLM**: OpenAI / OpenRouter
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **API Server**: FastAPI + Uvicorn
- **Frontend**: LangChain Next.js Template
## 🧠 Proactive Intelligence Workflow
Unlike traditional RAG systems that analyze data on-demand, this platform uses a **Proactive Sync** model:
1. **Ingest**: New transcripts are added.
2. **Analyze**: The system immediately summarizes the meeting and updates the project-wide **Master Report**.
3. **Embed**: Both raw text and high-level summaries are indexed into the FAISS Vector DB.
4. **Retrieve**: When a user asks a question, the AI instantly pulls the pre-computed intelligence, delivering expert-level insights without the wait.

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
| Frontend (Next.js) | http://localhost:3000 |
| **Frontend (Chainlit)** | **http://localhost:8001** |

---

### Option C: Chainlit (Python-Native UI)
For a faster, pure-python experience without React:
1. **Run the Chainlit App**:
   ```bash
   chainlit run app_chainlit.py -w --port 8001
   ```
2. Access the UI at `http://localhost:8001`.

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
