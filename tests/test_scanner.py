"""
Tests for src/parser/scanner.py

Run with: pytest tests/test_scanner.py -v
"""
import pytest
from pathlib import Path
from src.parser.scanner import scan_repository, chunk_file, scan_and_chunk, _is_safe_path


# ---------- fixtures ----------

@pytest.fixture
def sample_repo(tmp_path):
    """Build a tiny fake repo on disk to scan."""
    (tmp_path / "main.py").write_text("def hello():\n    return 'hi'\n")
    (tmp_path / "app.js").write_text("function greet() { return 'hi'; }\n")

    # should be ignored
    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "lib.js").write_text("junk")

    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")  # ignored extension
    (tmp_path / "empty.py").write_text("")  # empty file, should be skipped

    return tmp_path


# ---------- scan_repository ----------

def test_scan_finds_valid_source_files(sample_repo):
    result = scan_repository(str(sample_repo))
    paths = {f["path"] for f in result["files"]}

    assert "main.py" in paths
    assert "app.js" in paths
    assert result["total_files"] == 2


def test_scan_skips_ignored_dirs(sample_repo):
    result = scan_repository(str(sample_repo))
    paths = {f["path"] for f in result["files"]}

    assert not any("node_modules" in p for p in paths)


def test_scan_skips_ignored_extensions_and_empty_files(sample_repo):
    result = scan_repository(str(sample_repo))
    paths = {f["path"] for f in result["files"]}

    assert "image.png" not in paths
    assert "empty.py" not in paths


def test_scan_counts_languages_correctly(sample_repo):
    result = scan_repository(str(sample_repo))
    assert result["languages"]["python"] == 1
    assert result["languages"]["javascript"] == 1


def test_scan_raises_on_missing_path():
    with pytest.raises(ValueError):
        scan_repository("/this/path/does/not/exist")


def test_scan_raises_on_file_not_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hi")
    with pytest.raises(ValueError):
        scan_repository(str(f))


# ---------- _is_safe_path ----------

def test_is_safe_path_rejects_traversal(tmp_path):
    base = tmp_path / "repo"
    base.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")

    assert _is_safe_path(base, outside) is False


def test_is_safe_path_accepts_child(tmp_path):
    base = tmp_path / "repo"
    base.mkdir()
    child = base / "file.py"
    child.write_text("x = 1")

    assert _is_safe_path(base, child) is True


# ---------- chunk_file ----------

def test_chunk_file_single_chunk_for_small_file():
    file_info = {"path": "small.py", "language": "python", "content": "x = 1"}
    chunks = chunk_file(file_info)

    assert len(chunks) == 1
    assert chunks[0]["content"] == "x = 1"
    assert chunks[0]["chunk_id"] == "small.py::chunk_0"


def test_chunk_file_splits_large_file_with_overlap():
    # content longer than CHUNK_SIZE (1500) forces multiple chunks
    file_info = {"path": "big.py", "language": "python", "content": "a" * 3000}
    chunks = chunk_file(file_info)

    assert len(chunks) > 1
    # verify overlap: chunk 1 should start before chunk 0 ends
    assert chunks[1]["start_char"] < chunks[0]["end_char"]


def test_chunk_file_covers_entire_content_no_gaps():
    file_info = {"path": "big.py", "language": "python", "content": "b" * 3200}
    chunks = chunk_file(file_info)

    # last chunk should reach the end of the content
    assert chunks[-1]["end_char"] == 3200


# ---------- scan_and_chunk ----------

def test_scan_and_chunk_returns_metadata_and_chunks(sample_repo):
    meta, chunks = scan_and_chunk(str(sample_repo))

    assert "files" not in meta  # stripped out per scan_and_chunk contract
    assert meta["total_chunks"] == len(chunks)
    assert len(chunks) >= 2  # at least one chunk per file