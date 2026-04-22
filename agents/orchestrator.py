import json
import os
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from agents.keyword_agent import extract_keywords_tool
from agents.summary_agent import summarize_tool
from agents.taxonomy_agent import build_taxonomy_tool
from agents.clickup_agent import post_to_clickup_tool

class AgentState(TypedDict):
    query: str
    meetings: List[dict]
    individual_summaries: List[str]
    summary: str
    keywords: str
    taxonomy: str
    clickup_status: str
    final_output: str

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
    print(f"---MAP PHASE: Summarizing {len(state['meetings'])} meetings individually---")
    meetings = state["meetings"]
    summaries = []
    
    # In a production app, we would parallelize this with ThreadPoolExecutor
    for m in meetings:
        meeting_id = m.get("meeting_id", "Unknown")
        print(f"  > Summarizing {meeting_id}...")
        res = summarize_tool.invoke({"text": m["transcript"]})
        summaries.append(f"MEETING {meeting_id} SUMMARY:\n{res}")
    
    return {"individual_summaries": summaries}

def reduce_summary_node(state: AgentState):
    print("---REDUCE PHASE: Consolidating Insights---")
    combined_summaries = "\n\n---\n\n".join(state["individual_summaries"])
    
    # We ask the tool to summarize the combined individual summaries
    final_report = summarize_tool.invoke({
        "text": f"Below are summaries of multiple meetings. Create one cohesive master report that identifies common themes and cross-meeting action items.\n\n{combined_summaries}"
    })
    
    # Also extract keywords from the combined view
    keywords = extract_keywords_tool.invoke({"text": combined_summaries})
    
    return {"summary": final_report, "keywords": keywords}

def taxonomy_node(state: AgentState):
    print("---BUILDING TAXONOMY---")
    keywords = state["keywords"]
    taxonomy = build_taxonomy_tool.invoke({"keywords": keywords})
    return {"taxonomy": taxonomy}

def clickup_node(state: AgentState):
    print("---POSTING TO CLICKUP---")
    summary = state["summary"]
    status = post_to_clickup_tool.invoke({"message": summary})
    return {"clickup_status": status}

def final_output_node(state: AgentState):
    return {"final_output": f"Final Report: {state['summary']}\n\nTaxonomy: {state['taxonomy']}"}

def create_orchestrator():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("load_meetings", load_all_meetings_node)
    workflow.add_node("map_summarize", map_summarize_node)
    workflow.add_node("reduce_summary", reduce_summary_node)
    workflow.add_node("taxonomy", taxonomy_node)
    workflow.add_node("clickup", clickup_node)
    workflow.add_node("output", final_output_node)

    # Build Graph
    workflow.set_entry_point("load_meetings")
    
    workflow.add_edge("load_meetings", "map_summarize")
    workflow.add_edge("map_summarize", "reduce_summary")
    workflow.add_edge("reduce_summary", "taxonomy")
    workflow.add_edge("taxonomy", "clickup")
    workflow.add_edge("clickup", "output")
    workflow.add_edge("output", END)

    return workflow.compile()

if __name__ == "__main__":
    app = create_orchestrator()
    inputs = {"query": "Give me a master summary of all recent discussions."}
    result = app.invoke(inputs)
    print(result["final_output"])
