import os
import json
from agents.orchestrator import create_orchestrator
from rag.ingest import ingest
from sources.dummy import DummyMeetingSource

def run():
    # 1. Check for existing data to avoid redundant generation
    meetings_file = "data/meetings.json"
    if os.path.exists(meetings_file) and os.path.getsize(meetings_file) > 10:
        print("--- EXISTING DATA FOUND, SKIPPING GENERATION ---")
        sources = None
    else:
        print("--- GENERATING DUMMY MEETING DATA ---")
        sources = [DummyMeetingSource(count=10)]
    
    ingest(sources=sources)

    # 2. Run Intelligence Analysis
    query = "Summarize the key takeaways and trending topics from these meetings."
    
    app = create_orchestrator()
    config = {"recursion_limit": 50}
    inputs = {"query": query}
    
    print("\n--- STARTING MEETING INTELLIGENCE AGENT ---\n")
    result = app.invoke(inputs, config=config)
    
    print("\nFINAL SUMMARY:\n", result.get("summary"))
    print("\nFINAL TAXONOMY:\n", result.get("taxonomy"))
    print("\nCLICKUP STATUS:\n", result.get("clickup_status"))

if __name__ == "__main__":
    run()

