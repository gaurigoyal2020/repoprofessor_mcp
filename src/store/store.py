import chromadb
from chromadb.config import Settings
from src.config import CHROMA_PATH, CHROMA_COLLECTION


def get_client():
    """
    Create a persistent ChromaDB client.
    'persistent' means data survives between runs — stored in .chroma/ folder.
    """
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False)  # no phoning home
    )


def get_or_create_collection(client=None):
    """
    Get existing collection or create a fresh one.
    A ChromaDB 'collection' is like a table — all chunks for one repo live here.
    """
    if client is None:
        client = get_client()

    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}  # cosine similarity for code chunks
    )


def clear_collection():
    """
    Wipe the collection clean — used when re-ingesting a repo.
    Why: if you ingest repo A then repo B, you don't want A's chunks
    polluting B's answers.
    """
    client = get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass  # collection didn't exist, that's fine
    return client.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )


def save_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """
    Save chunks + their embeddings into ChromaDB.

    chunks: list of chunk dicts from scanner.py
    embeddings: parallel list of embedding vectors (one per chunk)
    """
    collection = get_or_create_collection()

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "path": chunk["path"],
            "language": chunk["language"],
            "chunk_index": chunk["chunk_index"],
            "start_char": chunk["start_char"],
            "end_char": chunk["end_char"],
        }
        for chunk in chunks
    ]

    # ChromaDB has a 5461 item batch limit — chunk our chunks!
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
        )


def query_chunks(query_embedding: list[float], n_results: int = 8) -> list[dict]:
    """
    Find the most semantically similar chunks to a query.

    Why n_results=8? Enough context for the LLM without blowing the
    context window. Tunable via the calling tool.
    """
    collection = get_or_create_collection()

    # Check collection isn't empty
    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "content": doc,
            "path": results["metadatas"][0][i]["path"],
            "language": results["metadatas"][0][i]["language"],
            "distance": results["distances"][0][i],
        })

    return chunks


def get_collection_stats() -> dict:
    """How many chunks are stored? Useful for sanity checks."""
    try:
        collection = get_or_create_collection()
        return {"total_chunks": collection.count(), "status": "ok"}
    except Exception as e:
        return {"total_chunks": 0, "status": str(e)}