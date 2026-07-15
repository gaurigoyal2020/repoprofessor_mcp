# RepoProfessor

An MCP server that turns any local codebase into an interactive teaching assistant.

RepoProfessor indexes a repository, retrieves relevant code using Retrieval-Augmented Generation (RAG), and provides tools to help understand architecture, trace execution, identify design patterns, and generate documentation. Every response is grounded in the indexed source code.

It is designed to make onboarding into unfamiliar codebases faster and to help developers understand not just what the code does, but why it is structured the way it is.

## Features

- Index a local repository
- Answer questions grounded in the repository
- Explain project architecture
- Trace the execution flow of features and functions
- Detect design patterns and discuss their tradeoffs
- Explain concepts with practical reasoning
- Generate learning paths
- Generate repository documentation

## How It Works

### 1. Ingest

The repository is scanned recursively with path traversal protection.

Files are split into overlapping chunks before embedding. This helps keep functions and other logical units together during retrieval.

Embeddings are generated locally using `sentence-transformers`, avoiding embedding API costs during indexing.

### 2. Store

Embeddings are stored in ChromaDB using cosine similarity.

Writes are batched to improve indexing performance.

### 3. Retrieve and Reason

Each MCP tool uses its own retrieval strategy instead of relying on a single generic search.

For example:

- Architecture analysis retrieves code that provides structural context, such as entry points and major components.
- Execution tracing retrieves code related to the requested feature or execution path.

The retrieved context is then used to generate responses with Llama 3.3 70B through Groq.

## MCP Tools

| Tool | Description |
|------|-------------|
| `ingest_repository` | Index a local repository |
| `ask_repository` | Ask questions about the indexed repository |
| `get_architecture_overview` | Explain the project's architecture, layers, and entry points |
| `trace_code_execution` | Trace the execution flow from a starting point |
| `find_design_patterns` | Detect design patterns and explain their tradeoffs |
| `explain_concept_like_senior` | Explain concepts with practical reasoning |
| `get_learning_path` | Generate a structured learning roadmap based on skill level |
| `generate_repo_documentation` | Generate README and architecture documentation |

## Tech Stack

- FastMCP
- ChromaDB
- sentence-transformers
- Groq
- Llama 3.3 70B

## Setup

Add your installation and `.env` configuration here.

## Design Decisions

### Local Embeddings

Embeddings are generated locally using `sentence-transformers` instead of an embedding API.

This keeps repository ingestion free from per-chunk embedding costs.

### Overlapping Chunks

Files are split into chunks of **1500 characters** with a **200-character overlap**.

The overlap helps reduce the chance of splitting functions across chunk boundaries, improving retrieval quality.

### Tool-Specific Retrieval

Different questions require different context.

Instead of sharing a single retrieval strategy across every tool, each tool retrieves context based on its specific purpose before generating a response.

For example, architecture analysis benefits from broader structural context, while execution tracing focuses on code related to a specific feature.

## Why RepoProfessor?

General-purpose code assistants are useful for explaining individual files or answering isolated questions.

RepoProfessor is designed for understanding an entire repository. Its tools are built around common codebase exploration tasks such as architecture analysis, execution tracing, design pattern discovery, learning, and documentation generation.
