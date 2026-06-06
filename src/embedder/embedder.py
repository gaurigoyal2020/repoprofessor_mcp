from chromadb.utils import embedding_functions
from src.config import EMBEDDING_MODEL

_ef = None

def get_embedding_function():
    global _ef
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
    return _ef

def embed_texts(texts: list[str]) -> list[list[float]]:
    ef = get_embedding_function()
    return ef(texts)

def embed_query(query: str) -> list[float]:
    ef = get_embedding_function()
    return ef([query])[0]