from src.embedder.embedder import embed_query
from src.store.store import query_chunks, get_collection_stats
from src.tools.llm import call_llm, build_context_from_chunks


def ask_repo(question: str, n_chunks: int = 8) -> dict:
    """
    Core RAG pipeline. The foundation of every other tool.
    
    Step 1: Check we have an indexed repo
    Step 2: Embed the question into a vector
    Step 3: Find the most similar code chunks
    Step 4: Build a prompt with those chunks as context
    Step 5: Call Groq and return the answer
    """

    # Step 1: Make sure a repo has been ingested
    stats = get_collection_stats()
    if stats["total_chunks"] == 0:
        return {
            "success": False,
            "error": "No repository ingested yet. Run ingest_repository first."
        }

    # Step 2: Convert the question to a vector
    query_vector = embed_query(question)

    # Step 3: Find most relevant chunks
    chunks = query_chunks(query_vector, n_results=n_chunks)

    # Step 4: Build context string from chunks
    context = build_context_from_chunks(chunks)

    # Step 5: Build prompt and call Groq
    system_prompt = """You are an expert software engineer helping someone 
understand an unfamiliar codebase. You are given relevant code snippets 
from the repository and a question about it.

Your job:
- Answer based on the actual code provided
- Be clear and educational  
- Point to specific files and functions when relevant
- If the code doesn't contain enough info to answer fully, say so honestly

Do not make up code or functionality that isn't shown."""

    user_message = f"""Relevant code from the repository:

{context}

Question: {question}"""

    answer = call_llm(system_prompt, user_message)

    return {
        "success": True,
        "question": question,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }