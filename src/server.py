from fastmcp import FastMCP
from src.tools.ingest import ingest_repo
from src.tools.query import ask_repo
from src.tools.analyze import (
    analyze_architecture,
    trace_execution_flow,
    identify_design_patterns,
)

mcp = FastMCP(
    name="RepoProfessor",
    instructions="""An intelligent repository teaching assistant.
    
    Workflow:
    1. First call ingest_repository() with the repo path
    2. Then use any other tool to learn about the codebase
    """
)


@mcp.tool()
def ingest_repository(repo_path: str, clear_existing: bool = True) -> dict:
    """
    Ingest a local repository for analysis.
    Always call this first before using any other tool.

    Args:
        repo_path: Absolute path to the repository on disk.
        clear_existing: Wipe previous ingestion first. Default True.
    """
    return ingest_repo(repo_path, clear_existing)


@mcp.tool()
def ask_repository(question: str) -> dict:
    """
    Ask any question about the ingested repository.
    Searches relevant code and answers based on actual source files.

    Args:
        question: Any question about the codebase.
    """
    return ask_repo(question)


@mcp.tool()
def get_architecture_overview(specific_question: str = "") -> dict:
    """
    Analyze and explain the repository's architecture.
    Identifies layers, components, entry points and relationships.

    Args:
        specific_question: Optional focus area. Leave empty for full overview.
    """
    return analyze_architecture(specific_question)


@mcp.tool()
def trace_code_execution(starting_point: str) -> dict:
    """
    Trace execution flow through the codebase from a starting point.
    Example starting points: 'user login', 'file upload', 'data ingestion'

    Args:
        starting_point: Feature or function to trace from.
    """
    return trace_execution_flow(starting_point)


@mcp.tool()
def find_design_patterns(focus_area: str = "") -> dict:
    """
    Identify and explain software design patterns in the repository.

    Args:
        focus_area: Optional area to focus on. Leave empty to scan all.
    """
    return identify_design_patterns(focus_area)


if __name__ == "__main__":
    mcp.run()