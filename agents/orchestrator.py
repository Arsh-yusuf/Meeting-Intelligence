import json
import os
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from agents.keyword_agent import extract_keywords_tool
from agents.summary_agent import summarize_tool
from agents.taxonomy_agent import build_taxonomy_tool
from agents.clickup_agent import post_to_clickup_tool
from llm.llm_client import call_llm, get_llm
from rag.retreiver import get_relevant_chunks

class AgentState(TypedDict):
    query: str
    meetings: List[dict]
    individual_summaries: List[str]
    summary: str
    keywords: str
    taxonomy: str
    clickup_status: str
    final_output: str
    intent: str  # "GLOBAL" or "SPECIFIC"
    show_taxonomy: bool

def proactive_rag_node(state: AgentState):
    print("---PROACTIVE RAG: FETCHING INTELLIGENCE---")
    # Fetch more chunks to include both raw and summary docs
    chunks = get_relevant_chunks(state["query"], k=10)
    context = "\n\n".join(chunks)
    
    prompt = f"""
    You are a Meeting Intelligence AI. Answer the user query using the provided context.
    The context includes raw meeting transcripts, individual meeting summaries, and a master intelligence report.
    
    If the query is global (e.g., 'What are the blockers?'), focus on the summaries and master report in the context.
    If the query is specific (e.g., 'What did John say?'), focus on the raw transcript chunks.
    
    Context:
    {context}
    
    Query: {state['query']}
    """
    answer = call_llm(prompt)
    return {"summary": answer}

def load_all_meetings_node(state: AgentState):
    print("---LOADING ALL MEETINGS---")
    meetings_path = "data/meetings.json"
    if os.path.exists(meetings_path):
        with open(meetings_path, 'r') as f:
            meetings = json.load(f)
    else:
        meetings = []
    
    # Optional: Filter meetings based on query if needed, but for Map-Reduce we take all
    return {"meetings": meetings}

def map_summarize_node(state: AgentState):
    meetings_path = "data/meetings.json"
    cache_path = "data/cache_summary.txt"
    
    # Cache Check
    if os.path.exists(cache_path) and os.path.exists(meetings_path):
        mtime_meetings = os.path.getmtime(meetings_path)
        mtime_cache = os.path.getmtime(cache_path)
        
        if mtime_cache > mtime_meetings:
            print("---USING CACHED SUMMARY---")
            with open(cache_path, 'r') as f:
                cached_summary = f.read()
            return {"summary": cached_summary, "individual_summaries": ["CACHED"]}

    print(f"---MAP PHASE: Summarizing {len(state['meetings'])} meetings individually---")
    meetings = state["meetings"]
    summaries = []
    
    for m in meetings:
        meeting_id = m.get("meeting_id", "Unknown")
        print(f"  > Summarizing {meeting_id}...")
        res = summarize_tool.invoke({"text": m["transcript"]})
        summaries.append(f"MEETING {meeting_id} SUMMARY:\n{res}")
    
    return {"individual_summaries": summaries}

def reduce_summary_node(state: AgentState):
    cache_dir = "data"
    summary_cache_path = os.path.join(cache_dir, "cache_summary.txt")
    keywords_cache_path = os.path.join(cache_dir, "cache_keywords.txt")

    if state.get("individual_summaries") == ["CACHED"]:
        if os.path.exists(keywords_cache_path):
            with open(keywords_cache_path, 'r') as f:
                cached_keywords = f.read()
            return {"keywords": cached_keywords}
        return {}

    print("---REDUCE PHASE: Consolidating Insights---")
    combined_summaries = "\n\n---\n\n".join(state["individual_summaries"])
    
    final_report = summarize_tool.invoke({
        "text": f"Below are summaries of multiple meetings. Create one cohesive master report that identifies common themes and cross-meeting action items.\n\n{combined_summaries}"
    })
    
    keywords = extract_keywords_tool.invoke({"text": combined_summaries})

    # Cache the final report and keywords
    os.makedirs(cache_dir, exist_ok=True)
    with open(summary_cache_path, "w") as f:
        f.write(final_report)
    with open(keywords_cache_path, "w") as f:
        f.write(keywords)
    
    return {"summary": final_report, "keywords": keywords}

def taxonomy_node(state: AgentState):
    if not state.get("keywords"):
        print("---SKIPPING TAXONOMY (No keywords)---")
        return {"taxonomy": "N/A"}
    
    print("---BUILDING TAXONOMY---")
    keywords = state["keywords"]
    taxonomy = build_taxonomy_tool.invoke({"keywords": keywords})
    return {"taxonomy": taxonomy}

def clickup_node(state: AgentState):
    query = state["query"].lower()
    keywords = ["update", "post", "clickup", "sync", "task", "create"]
    
    if not any(k in query for k in keywords):
        print("---SKIPPING CLICKUP POST---")
        return {"clickup_status": "Skipped (No action requested)"}

    print("---POSTING TO CLICKUP---")
    summary = state["summary"]
    status = post_to_clickup_tool.invoke({"message": summary})
    return {"clickup_status": status}

def final_output_node(state: AgentState):
    taxonomy_section = f"\n\nTaxonomy: {state['taxonomy']}" if state.get("taxonomy") and state.get("show_taxonomy") else ""
    return {"final_output": f"### Meeting Intelligence Report\n\n{state['summary']}{taxonomy_section}"}

def create_orchestrator():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("proactive_rag", proactive_rag_node)
    workflow.add_node("clickup", clickup_node)
    workflow.add_node("output", final_output_node)

    # Build Graph
    workflow.set_entry_point("proactive_rag")
    
    workflow.add_edge("proactive_rag", "clickup")
    workflow.add_edge("clickup", "output")
    workflow.add_edge("output", END)

    return workflow.compile()

if __name__ == "__main__":
    app = create_orchestrator()
    inputs = {"query": "Give me a master summary of all recent discussions."}
    result = app.invoke(inputs)
    print(result["final_output"])
