from langchain.tools import tool
from llm.llm_client import call_llm

@tool
def extract_keywords_tool(text: str) -> str:
    """Extracts top 10 important keywords and trends from the given meeting text."""
    prompt = f"""
    Extract top 10 important keywords and trends from the following meeting transcript:

    {text}

    Return the result as a bulleted list.
    """
    return call_llm(prompt)