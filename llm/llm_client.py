from langchain_openai import ChatOpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL

def get_llm():
    return ChatOpenAI(
        model=MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        temperature=0.7
    )

def call_llm(prompt):
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content