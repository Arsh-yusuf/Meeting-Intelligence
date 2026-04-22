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

## 🛠️ Tech Stack
- **Framework**: LangChain, LangGraph
- **Vector Database**: FAISS (Local)
- **LLM**: OpenAI / OpenRouter
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Database**: Local JSON storage

## 📁 Project Structure
```text
├── agents/            # Specialized AI Agents (Summarizer, Taxonomy, ClickUp)
├── sources/           # Data Ingestion Providers (Fathom, Dummy, Base)
├── rag/               # RAG Pipeline (Ingestion, Retrieval, Vector Store)
├── config/            # System Configuration & Settings
├── data/              # Persistent Storage (JSON & Vector Index)
└── main.py            # Entry point for the application
```

## ⚙️ Setup Instructions

1. **Clone the repository** and navigate to the root directory.
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_key_here
   CLICKUP_API_KEY=your_key_here
   CLICKUP_TASK_ID=your_task_id
   ```

## 🚀 Usage

Run the main intelligence pipeline:
```bash
python main.py
```

The system will:
1. Generate/Load meeting transcripts.
2. Index them into the Vector Store.
3. Run the Map-Reduce Orchestrator.
4. Post the final intelligence report to ClickUp.

