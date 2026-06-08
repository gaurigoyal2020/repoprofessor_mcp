from src.embedder.embedder import embed_query
from src.store.store import query_chunks
from src.tools.llm import call_llm, build_context_from_chunks


def explain_like_senior(concept: str) -> dict:
    """
    Explain a concept from the repo the way a senior engineer would.
    Focuses on WHY decisions were made, not just WHAT the code does.
    Covers architecture intent, tradeoffs, and alternative approaches.
    """

    query_vector = embed_query(concept)
    chunks = query_chunks(query_vector, n_results=8)
    context = build_context_from_chunks(chunks)

    system_prompt = """You are a senior software engineer with 10+ years 
of experience, onboarding a junior developer to a new codebase.

Your explanation style:
- Start with WHY this component exists — what problem does it solve?
- Explain WHAT it does, grounded in the actual code shown
- Discuss the key DECISIONS made and why (what alternatives were considered)
- Point out TRADEOFFS — what does this approach give up?
- Mention what you would do DIFFERENTLY at scale or in production
- Use analogies when helpful
- Be honest about limitations or areas that could be improved

You are not just describing code. You are transferring understanding.
A junior should walk away knowing not just how it works but why it 
was built this way."""

    user_message = f"""Here is relevant code from the repository:

{context}

Explain this concept like a senior engineer onboarding a junior developer: {concept}"""

    answer = call_llm(system_prompt, user_message, max_tokens=1500)

    return {
        "success": True,
        "concept": concept,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }


def generate_learning_path(level: str = "beginner") -> dict:
    """
    Generate a structured learning roadmap for understanding this repository.
    
    level: 'beginner', 'intermediate', or 'advanced'
    
    Beginner  → entry points, main workflow, core modules
    Intermediate → dependencies, design patterns, data flow  
    Advanced  → optimization, extension points, architectural tradeoffs
    """

    # Search broadly to get a representative view of the whole codebase
    query_vector = embed_query(
        "main modules entry points core functionality structure overview"
    )
    chunks = query_chunks(query_vector, n_results=10)
    context = build_context_from_chunks(chunks)

    level_instructions = {
        "beginner": """Focus on:
- Where to start reading (entry points)
- The main workflow from start to finish
- The 3-5 most important files to read first
- What each core module does in simple terms
- What to ignore for now""",

        "intermediate": """Focus on:
- How components depend on each other
- The data flow through the system
- Design patterns and why they were chosen
- Configuration and how to customise behaviour
- How to add new features""",

        "advanced": """Focus on:
- Performance bottlenecks and optimisation opportunities
- Extension points and how to scale the system
- Architectural tradeoffs and what they cost
- What would need to change for production use
- Alternative architectural approaches""",
    }

    instructions = level_instructions.get(
        level.lower(),
        level_instructions["beginner"]
    )

    system_prompt = f"""You are a senior engineer creating a learning roadmap 
for a new team member joining a project.

The developer's level is: {level.upper()}

{instructions}

Format your response as a clear, numbered learning path:
1. Start here: [file/concept] — why start here
2. Then read: [file/concept] — what you'll learn
3. Next: [file/concept] — how it connects to previous
...and so on.

End with a "Key concepts to understand" section listing the 
most important mental models for this codebase."""

    user_message = f"""Here is the repository structure and code:

{context}

Generate a {level} learning path for understanding this repository."""

    answer = call_llm(system_prompt, user_message, max_tokens=1500)

    return {
        "success": True,
        "level": level,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }