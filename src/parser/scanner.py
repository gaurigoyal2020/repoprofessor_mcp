from pathlib import Path
from typing import Generator
from src.config import (
    IGNORE_DIRS, IGNORE_EXTENSIONS, LANGUAGE_MAP,
    CHUNK_SIZE, CHUNK_OVERLAP
)


def _is_safe_path(base: Path, target: Path) -> bool:
    """
    Security guard: ensure target path doesn't escape the base directory.
    Prevents path traversal attacks like ../../etc/passwd
    """
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def scan_repository(repo_path: str) -> dict:
    """
    Walk a repository and return metadata + all source files found.
    Returns a dict with repo stats and list of file info dicts.
    """
    root = Path(repo_path)

    if not root.exists():
        raise ValueError(f"Path does not exist: {repo_path}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {repo_path}")

    files = []
    language_counts = {}

    for file_path in root.rglob("*"):
        # Security check
        if not _is_safe_path(root, file_path):
            continue

        # Skip directories
        if not file_path.is_file():
            continue

        # Skip ignored directories anywhere in the path
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue

        # Skip ignored extensions
        if file_path.suffix.lower() in IGNORE_EXTENSIONS:
            continue

        # Only process known languages
        lang = LANGUAGE_MAP.get(file_path.suffix.lower())
        if not lang:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not content.strip():
            continue

        language_counts[lang] = language_counts.get(lang, 0) + 1

        files.append({
            "path": str(file_path.relative_to(root)),
            "abs_path": str(file_path),
            "language": lang,
            "content": content,
            "size": len(content),
        })

    return {
        "root": str(root),
        "total_files": len(files),
        "languages": language_counts,
        "files": files,
    }


def chunk_file(file_info: dict) -> list[dict]:
    """
    Split a file's content into overlapping chunks for embedding.

    Why overlap? If a function definition starts at the end of chunk N,
    we don't want chunk N+1 to be missing its context. Overlap ensures
    every piece of meaningful code appears fully in at least one chunk.
    """
    content = file_info["content"]
    path = file_info["path"]
    lang = file_info["language"]

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(content):
        end = start + CHUNK_SIZE
        chunk_text = content[start:end]

        chunks.append({
            "chunk_id": f"{path}::chunk_{chunk_index}",
            "path": path,
            "language": lang,
            "content": chunk_text,
            "chunk_index": chunk_index,
            "start_char": start,
            "end_char": min(end, len(content)),
        })

        chunk_index += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP  # slide forward with overlap

    return chunks


def scan_and_chunk(repo_path: str) -> tuple[dict, list[dict]]:
    """
    Convenience function: scan a repo and return (metadata, all_chunks).
    This is what the ingestion tool calls.
    """
    repo_meta = scan_repository(repo_path)
    all_chunks = []

    for file_info in repo_meta["files"]:
        chunks = chunk_file(file_info)
        all_chunks.extend(chunks)

    repo_meta.pop("files")  # don't need full file content in metadata anymore
    repo_meta["total_chunks"] = len(all_chunks)

    return repo_meta, all_chunks