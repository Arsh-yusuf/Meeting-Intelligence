"""
server.py — LangServe API layer for Meeting Intelligence AI.

This file exposes the LangGraph orchestrator as an HTTP endpoint
via FastAPI + LangServe. main.py (the CLI runner) is untouched.

Endpoints:
  POST /analyze/invoke   — Run full Map-Reduce pipeline
  GET  /analyze/stream   — Stream intermediate steps
  GET  /health           — Health check
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from rag.ingest import ingest
from agents.orchestrator import create_orchestrator
from sources.dummy import DummyMeetingSource

# ── Bootstrap data on startup ────────────────────────────────────────────────
def _ensure_data():
    """Seed the vector store with dummy data if meetings.json is empty, then run proactive ingestion."""
    meetings_file = "data/meetings.json"
    
    # 1. Generate data if missing
    if not os.path.exists(meetings_file) or os.path.getsize(meetings_file) <= 10:
        print("[server] No data found — generating 5 dummy meetings...")
        ingest(sources=[DummyMeetingSource(count=5)])
    else:
        # 2. Run proactive ingestion to summarize any new meetings and update master report
        print("[server] Existing data found — synchronizing intelligence...")
        ingest() 
    
    print("[server] Intelligence synchronization complete.")

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Meeting Intelligence AI",
    description="Multi-agent RAG system for meeting analysis.",
    version="1.0.0",
)

# Allow requests from the Next.js frontend (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Meeting Intelligence AI"}

# ── Register LangGraph as a LangServe route ──────────────────────────────────
orchestrator = create_orchestrator()

add_routes(
    app,
    orchestrator,
    path="/analyze",
    input_type=dict,
    config_keys=["recursion_limit"],
)

# ── Startup event ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    _ensure_data()

# ── Run directly (for local dev without Docker) ───────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)
