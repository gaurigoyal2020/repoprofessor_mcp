from src.embedder.embedder import embed_query
from src.store.store import query_chunks
from src.tools.llm import call_llm, build_context_from_chunks


def analyze_architecture(specific_question: str = "") -> dict:
    """
    Analyze the high-level architecture of the ingested repository.
    Identifies layers, components, entry points and their relationships.
    """

    # For architecture analysis we use a broad query to get a wide view
    # of the codebase rather than zooming into one specific area
    search_query = specific_question if specific_question else \
        "main modules components architecture entry points structure layers"

    query_vector = embed_query(search_query)
    chunks = query_chunks(query_vector, n_results=10)
    context = build_context_from_chunks(chunks)

    system_prompt = """You are a senior software architect analyzing an 
unfamiliar codebase. You have been given code snippets from the repository.

Your job is to identify and explain:
1. The overall architectural pattern (MVC, layered, microservices, etc.)
2. The main components/modules and what each does
3. How components relate to and communicate with each other
4. The entry points of the application
5. The data flow through the system

Be structured. Use clear headings. Give a junior developer a mental map 
of the system they can hold in their head."""

    user_message = f"""Here are code snippets from the repository:

{context}

{"Specific question: " + specific_question if specific_question else "Provide a full architecture overview."}"""

    answer = call_llm(system_prompt, user_message, max_tokens=1500)

    return {
        "success": True,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }


def trace_execution_flow(starting_point: str) -> dict:
    """
    Trace the execution flow starting from a given function, feature, or concept.
    Example: "user login", "file upload", "database query"
    """

    query_vector = embed_query(starting_point)
    chunks = query_chunks(query_vector, n_results=10)
    context = build_context_from_chunks(chunks)

    system_prompt = """You are a senior engineer explaining how code executes 
to a new team member. You have been given relevant code snippets.

Your job:
- Trace the execution path step by step
- Show the chain: entry point → function → function → result
- Explain what happens at each step and why
- Format it as a clear numbered flow, like:
  1. Request enters at X
  2. X calls Y because...
  3. Y does Z which...
- Point to specific files and functions at each step

Make it feel like you're walking someone through a debugger."""

    user_message = f"""Here are relevant code snippets:

{context}

Trace the execution flow for: {starting_point}"""

    answer = call_llm(system_prompt, user_message, max_tokens=1500)

    return {
        "success": True,
        "starting_point": starting_point,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }


def identify_design_patterns(focus_area: str = "") -> dict:
    """
    Identify and explain software design patterns used in the repository.
    Optionally focus on a specific area of the codebase.
    """

    search_query = focus_area if focus_area else \
        "patterns classes interfaces abstractions factories repositories services"

    query_vector = embed_query(search_query)
    chunks = query_chunks(query_vector, n_results=10)
    context = build_context_from_chunks(chunks)

    system_prompt = """You are a senior engineer with deep knowledge of 
software design patterns. You have been given code snippets from a repository.

Your job:
- Identify design patterns present in the code
- For each pattern found explain:
  * What the pattern is (in simple terms)
  * Where exactly it appears in this codebase
  * Why it was likely chosen
  * What benefit it provides
  * What tradeoff or complexity it adds

Common patterns to look for: MVC, Repository, Service Layer, Factory, 
Singleton, Observer, Dependency Injection, Strategy, Decorator.

If a pattern is absent but would be beneficial, mention it."""

    user_message = f"""Here are code snippets from the repository:

{context}

{"Focus area: " + focus_area if focus_area else "Identify all notable patterns."}"""

    answer = call_llm(system_prompt, user_message, max_tokens=1500)

    return {
        "success": True,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }