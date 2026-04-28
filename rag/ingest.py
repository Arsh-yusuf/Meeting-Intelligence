import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from rag.vector_store import get_embeddings
from sources.base import MeetingSource
from agents.summary_agent import summarize_tool
from langchain_core.documents import Document

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
    
    # Track processed meetings to avoid redundant LLM calls
    processed_path = "data/processed_meetings.json"
    processed_ids = set()
    if os.path.exists(processed_path):
        with open(processed_path, "r") as f:
            processed_ids = set(json.load(f))

    new_docs = []
    newLY_processed_ids = []
    
    print(f"Checking {len(all_meetings)} meetings for new insights...")
    
    for m in all_meetings:
        mid = m.get("meeting_id", "unknown")
        
        # 1. Store Raw Chunks (Always for simplicity, or check if exists)
        # For now we recreate docs if not in processed_ids
        if mid not in processed_ids:
            print(f"  > Processing new meeting: {mid}")
            meeting_text = m["transcript"]
            metadata = {
                "meeting_id": mid,
                "source": m.get("source", "json"),
                "type": "raw"
            }
            chunks = splitter.create_documents([meeting_text], metadatas=[metadata])
            new_docs.extend(chunks)

            # 2. Proactive Summarization
            print(f"  > Generating proactive summary for {mid}...")
            summary = summarize_tool.invoke({"text": meeting_text})
            summary_doc = Document(
                page_content=f"SUMMARY OF MEETING {mid}:\n{summary}",
                metadata={
                    "meeting_id": mid,
                    "type": "summary",
                    "source": m.get("source", "json")
                }
            )
            new_docs.append(summary_doc)
            newLY_processed_ids.append(mid)

    if new_docs:
        print(f"Adding {len(new_docs)} new intelligence documents to FAISS...")
        if db:
            db.add_documents(new_docs)
        else:
            db = FAISS.from_documents(new_docs, embeddings)
        
        db.save_local(VECTOR_STORE_PATH)
        
        # Update processed IDs
        all_processed = list(processed_ids.union(set(newLY_processed_ids)))
        with open(processed_path, "w") as f:
            json.dump(all_processed, f, indent=4)
        
        # 3. Regenerate Master Report if new data was added
        print("Generating updated Master Report...")
        all_summaries = [d.page_content for d in db.docstore._dict.values() if d.metadata.get("type") == "summary"]
        combined_summaries = "\n\n---\n\n".join(all_summaries)
        
        master_report = summarize_tool.invoke({
            "text": f"Below are summaries of multiple meetings. Create one cohesive master report that identifies common themes and cross-meeting action items.\n\n{combined_summaries}"
        })
        
        master_doc = Document(
            page_content=f"MASTER INTELLIGENCE REPORT (LATEST):\n{master_report}",
            metadata={"type": "master_report"}
        )
        
        # Replace old master report if it exists
        # In FAISS, we'd ideally delete by metadata, but for now we just add it.
        # Simple RAG will pick the latest or most relevant.
        db.add_documents([master_doc])
        db.save_local(VECTOR_STORE_PATH)
        print("Master Report updated and stored in Vector DB.")
    else:
        print("No new meetings to process.")

if __name__ == "__main__":
    from sources.fathom import FathomSource
    
    # Example usage with Fathom
    fathom_src = FathomSource(links=["https://fathom.video/share/link1", "https://fathom.video/share/link2"])
    
    print("Starting incremental ingestion...")
    ingest(sources=[fathom_src])
    print("Ingestion complete.")

