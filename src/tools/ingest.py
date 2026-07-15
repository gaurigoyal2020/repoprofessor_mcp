from src.parser.scanner import scan_and_chunk
from src.embedder.embedder import embed_texts
from src.store.store import save_chunks, clear_collection
from rich.console import Console
import sys

console = Console(file=sys.stderr)


def ingest_repo(repo_path: str, clear_existing: bool = True) -> dict:
    """
    Full ingestion pipeline: scan → chunk → embed → store.

    repo_path: absolute path to the local repository
    clear_existing: wipe previous ingestion before starting (recommended)

    Returns a summary dict with stats about what was ingested.
    """

    console.print(f"\n[bold cyan]RepoProfessor[/bold cyan] ingesting: {repo_path}")

    # Step 1: Scan and chunk the repository
    console.print("[yellow]Step 1/3:[/yellow] Scanning repository...")
    try:
        repo_meta, chunks = scan_and_chunk(repo_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    if not chunks:
        return {
            "success": False,
            "error": "No source files found. Check the path or file types."
        }

    console.print(f"  Found [green]{repo_meta['total_files']}[/green] files → "
                  f"[green]{len(chunks)}[/green] chunks")
    console.print(f"  Languages: {repo_meta['languages']}")

    # Step 2: Embed all chunks
    console.print("[yellow]Step 2/3:[/yellow] Generating embeddings...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = embed_texts(texts)
    console.print(f"  Embedded [green]{len(embeddings)}[/green] chunks")

    # Step 3: Store in ChromaDB
    console.print("[yellow]Step 3/3:[/yellow] Storing in vector database...")
    if clear_existing:
        clear_collection()

    save_chunks(chunks, embeddings)
    console.print("[bold green]✓ Ingestion complete![/bold green]\n")

    return {
        "success": True,
        "repo_path": repo_path,
        "total_files": repo_meta["total_files"],
        "total_chunks": len(chunks),
        "languages": repo_meta["languages"],
    }