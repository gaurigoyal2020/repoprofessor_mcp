"""
Tests for src/tools/query.py -- ask_repo (the core RAG pipeline).

ask_repo calls three external things: embed_query (embedding model),
query_chunks (ChromaDB), and call_llm (Groq API). We don't want tests
that hit real APIs -- slow, costs quota, and fails if the service is
down even when our code is correct.

Instead we MOCK each dependency: replace it with a fake that returns a
fixed value, so we can test that ask_repo wires everything together
correctly -- without needing network access or an API key.

Run with: pytest tests/test_query.py -v
"""
from unittest.mock import patch
from src.tools.query import ask_repo


def test_returns_error_when_no_repo_ingested():
    """If ChromaDB is empty, ask_repo should fail early and NOT try to
    call the embedder or the LLM at all."""
    with patch("src.tools.query.get_collection_stats") as mock_stats:
        mock_stats.return_value = {"total_chunks": 0}

        result = ask_repo("What does this code do?")

        assert result["success"] is False
        assert "ingest" in result["error"].lower()


def test_happy_path_returns_answer_and_sources():
    """With a populated store, ask_repo should embed the question,
    retrieve chunks, call the LLM, and return a well-formed result."""
    fake_chunks = [
        {"path": "src/main.py", "content": "def run(): pass"},
        {"path": "src/utils.py", "content": "def helper(): pass"},
    ]

    with patch("src.tools.query.get_collection_stats") as mock_stats, \
         patch("src.tools.query.embed_query") as mock_embed, \
         patch("src.tools.query.query_chunks") as mock_query, \
         patch("src.tools.query.call_llm") as mock_llm:

        mock_stats.return_value = {"total_chunks": 42}
        mock_embed.return_value = [0.1, 0.2, 0.3]  # fake vector
        mock_query.return_value = fake_chunks
        mock_llm.return_value = "This code runs the main entry point."

        result = ask_repo("What does this code do?")

        assert result["success"] is True
        assert result["answer"] == "This code runs the main entry point."
        assert result["sources"] == ["src/main.py", "src/utils.py"]
        assert result["question"] == "What does this code do?"


def test_question_is_embedded_before_querying():
    """The exact question text should be passed to the embedder --
    catches bugs where a stale/wrong variable gets embedded instead."""
    with patch("src.tools.query.get_collection_stats") as mock_stats, \
         patch("src.tools.query.embed_query") as mock_embed, \
         patch("src.tools.query.query_chunks") as mock_query, \
         patch("src.tools.query.call_llm") as mock_llm:

        mock_stats.return_value = {"total_chunks": 5}
        mock_embed.return_value = [0.0]
        mock_query.return_value = []
        mock_llm.return_value = "answer"

        ask_repo("how does auth work?")

        mock_embed.assert_called_once_with("how does auth work?")


def test_n_chunks_param_is_passed_through():
    """If the caller asks for a custom n_chunks, that value should
    reach query_chunks -- not silently get ignored or hardcoded."""
    with patch("src.tools.query.get_collection_stats") as mock_stats, \
         patch("src.tools.query.embed_query") as mock_embed, \
         patch("src.tools.query.query_chunks") as mock_query, \
         patch("src.tools.query.call_llm") as mock_llm:

        mock_stats.return_value = {"total_chunks": 5}
        mock_embed.return_value = [0.0]
        mock_query.return_value = []
        mock_llm.return_value = "answer"

        ask_repo("some question", n_chunks=3)

        _, kwargs = mock_query.call_args
        assert kwargs.get("n_results") == 3