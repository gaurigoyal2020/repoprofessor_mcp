from src.embedder.embedder import embed_query
from src.store.store import query_chunks
from src.tools.llm import call_llm, build_context_from_chunks


def _multi_query_search(queries: list[str], n_per_query: int = 6) -> list[dict]:
    """
    Run multiple ChromaDB searches and combine results.
    Deduplicates by file path so the same chunk isn't sent twice.
    
    Why multiple queries? One search gives a narrow view.
    Multiple searches with different angles gives broad coverage —
    essential for generating complete documentation.
    """
    seen_paths = set()
    all_chunks = []

    for query in queries:
        vector = embed_query(query)
        chunks = query_chunks(vector, n_results=n_per_query)

        for chunk in chunks:
            # Deduplicate — same path appearing twice wastes context window
            if chunk["path"] not in seen_paths:
                seen_paths.add(chunk["path"])
                all_chunks.append(chunk)

    return all_chunks


def generate_documentation(doc_type: str = "readme") -> dict:
    """
    Generate structured documentation for the repository.

    doc_type options:
    - 'readme'        → full README.md with overview, setup, usage
    - 'architecture'  → technical architecture document
    - 'contributing'  → contributor onboarding guide
    """

    # Different doc types need different search angles
    query_map = {
        "readme": [
            "project overview purpose what this does",
            "installation setup requirements dependencies",
            "usage examples how to use",
            "main features functionality",
        ],
        "architecture": [
            "main modules components structure layers",
            "data flow how components connect",
            "design patterns abstractions interfaces",
            "configuration settings environment",
        ],
        "contributing": [
            "project structure files organisation",
            "how to add new features extension points",
            "configuration setup development environment",
            "main workflows pipelines how things work",
        ],
    }

    queries = query_map.get(doc_type.lower(), query_map["readme"])
    chunks = _multi_query_search(queries)
    context = build_context_from_chunks(chunks)

    prompt_map = {
        "readme": {
            "system": """You are a technical writer generating a professional README.md.

Structure your README with these sections:
# Project Name
## What is this?
## Why does it exist? (the problem it solves)
## How it works (brief technical overview)
## Installation
## Usage (with examples)
## Project Structure
## Technology Stack
## Contributing

Write in clear, friendly markdown. Be specific — use actual 
file names, function names, and technical details from the code.
Do not use placeholder text like [Your Project Name].""",

            "user": f"""Here is the repository code:

{context}

Generate a complete, professional README.md for this project."""
        },

        "architecture": {
            "system": """You are a senior architect writing technical documentation.

Structure your document with:
# Architecture Overview
## System Design
## Components and Responsibilities  
## Data Flow
## Key Technical Decisions (and why)
## Tradeoffs and Limitations
## Future Considerations

Be precise and technical. This document is for engineers 
who need to deeply understand the system.""",

            "user": f"""Here is the repository code:

{context}

Generate a complete architecture document for this project."""
        },

        "contributing": {
            "system": """You are writing a contributor guide for new developers.

Structure your document with:
# Contributing Guide
## Project Overview
## Setting Up Your Development Environment
## Project Structure (file by file)
## How to Add a New Feature
## Core Concepts You Must Understand
## Common Patterns Used in This Codebase
## Step-by-Step: Making Your First Contribution

Be welcoming and thorough. Assume the reader is a competent 
developer but completely unfamiliar with this codebase.""",

            "user": f"""Here is the repository code:

{context}

Generate a complete contributor guide for this project."""
        },
    }

    prompts = prompt_map.get(doc_type.lower(), prompt_map["readme"])

    answer = call_llm(
        prompts["system"],
        prompts["user"],
        max_tokens=2000
    )

    return {
        "success": True,
        "doc_type": doc_type,
        "answer": answer,
        "sources": [c["path"] for c in chunks],
    }