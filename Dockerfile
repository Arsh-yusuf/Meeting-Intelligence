# ── Base image ─────────────────────────────────────────────────────────────
# Using slim variant to keep image size small
FROM python:3.12-slim

# ── System dependencies ────────────────────────────────────────────────────
# faiss-cpu and sentence-transformers need these build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ────────────────────────────────────────────
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ─────────────────────────────────────────────────────
COPY . .

# ── Create data directories (vector store + meetings JSON) ─────────────────
RUN mkdir -p data/vector_store

# ── Expose the FastAPI port ────────────────────────────────────────────────
EXPOSE 8000

# ── Start the LangServe API ────────────────────────────────────────────────
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
