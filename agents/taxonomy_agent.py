from langchain.tools import tool
from llm.llm_client import call_llm

@tool
def build_taxonomy_tool(keywords: str) -> str:
    """Groups keywords into logical categories to build a taxonomy."""
    prompt = f"""
    Group the following keywords or technical terms into logical categories to build a structured taxonomy:

    {keywords}

    Return the result in a clear, formatted JSON-like structure or a nested list.
    """
    return call_llm(prompt)