from fastmcp import FastMCP
from src.tools.ingest import ingest_repo

mcp = FastMCP(
    name="RepoProfessor",
    instructions="An intelligent repository teaching assistant. "
                 "Ingest a repo first, then ask anything about it."
)


@mcp.tool()
def ingest_repository(repo_path: str, clear_existing: bool = True) -> dict:
    """
    Ingest a local repository for analysis.

    Args:
        repo_path: Absolute path to the repository on disk.
        clear_existing: If True, clears any previously ingested repo first.

    Returns:
        Summary of ingestion including file count, chunk count, and languages.
    """
    return ingest_repo(repo_path, clear_existing)


if __name__ == "__main__":
    mcp.run()