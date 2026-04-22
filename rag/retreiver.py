from langchain_community.vectorstores import FAISS
from rag.vector_store import get_embeddings

def get_relevant_chunks(query, k=5):
    db = FAISS.load_local(
    "data/vector_store",
    get_embeddings(),
    allow_dangerous_deserialization=True
)
    docs = db.similarity_search(query, k=k)
    return [d.page_content for d in docs]