"""
Tests for src/tools/llm.py -- build_context_from_chunks only.

This is pure logic (string formatting, no network calls), so it's tested
the same way as the scanner: no mocking needed.

Run with: pytest tests/test_llm.py -v
"""
from src.tools.llm import build_context_from_chunks


def test_empty_chunks_returns_fallback_message():
    result = build_context_from_chunks([])
    assert result == "No relevant code found in the repository."


def test_single_chunk_includes_path_and_content():
    chunks = [{"path": "src/main.py", "content": "def hello(): pass"}]
    result = build_context_from_chunks(chunks)

    assert "src/main.py" in result
    assert "def hello(): pass" in result


def test_multiple_chunks_are_separated_and_labeled():
    chunks = [
        {"path": "a.py", "content": "x = 1"},
        {"path": "b.py", "content": "y = 2"},
    ]
    result = build_context_from_chunks(chunks)

    # both chunks present
    assert "a.py" in result and "x = 1" in result
    assert "b.py" in result and "y = 2" in result

    # order preserved: a.py's block should appear before b.py's block
    assert result.index("a.py") < result.index("b.py")

    # chunks are visibly separated, not concatenated into one blob
    assert "\n\n" in result