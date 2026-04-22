from langchain.tools import tool
from llm.llm_client import call_llm

@tool
def summarize_tool(text: str) -> str:
    """Summarizes the meeting transcript into decisions, blockers, and action items."""
    prompt = f"""
    Summarize the following meeting transcript. Focus on:
    - Key Decisions
    - Identified Blockers
    - Specific Action Items (with owners if mentioned)

    Transcript:
    {text}
    """
    return call_llm(prompt)
