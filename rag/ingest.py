import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from rag.vector_store import get_embeddings
from sources.base import MeetingSource

VECTOR_STORE_PATH = "data/vector_store"

def ingest(sources: list[MeetingSource] = None):
    all_meetings = []
    
    # Load from local JSON if it exists and is not empty
    if os.path.exists("data/meetings.json") and os.path.getsize("data/meetings.json") > 0:
        try:
            with open("data/meetings.json") as f:
                all_meetings.extend(json.load(f))
        except json.JSONDecodeError:
            print("Warning: data/meetings.json is malformed. Skipping.")

    # Load from additional sources
    if sources:
        for source in sources:
            all_meetings.extend(source.fetch_meetings())

    # Save to local JSON to ensure it's not empty for next time
    with open("data/meetings.json", "w") as f:
        json.dump(all_meetings, f, indent=4)

    if not all_meetings:
        print("No meetings found to ingest.")
        return

    # Load existing vector store or create new one
    embeddings = get_embeddings()
    index_file = os.path.join(VECTOR_STORE_PATH, "index.faiss")
    if os.path.exists(index_file):
        db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        db = None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    new_docs = []
    for m in all_meetings:
        meeting_text = m["transcript"]
        metadata = {
            "meeting_id": m.get("meeting_id", "unknown"),
             "source": m.get("source", "json")
        }
        chunks = splitter.create_documents([meeting_text], metadatas=[metadata])
        new_docs.extend(chunks)

    if db:
        db.add_documents(new_docs)
    else:
        db = FAISS.from_documents(new_docs, embeddings)

    db.save_local(VECTOR_STORE_PATH)

if __name__ == "__main__":
    from sources.fathom import FathomSource
    
    # Example usage with Fathom
    fathom_src = FathomSource(links=["https://fathom.video/share/link1", "https://fathom.video/share/link2"])
    
    print("Starting incremental ingestion...")
    ingest(sources=[fathom_src])
    print("Ingestion complete.")

