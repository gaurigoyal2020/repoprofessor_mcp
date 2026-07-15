"""
Tests for src/tools/analyze.py -- analyze_architecture, trace_execution_flow,
identify_design_patterns.

Same mocking pattern as test_query.py: embed_query, query_chunks, and
call_llm are all faked so we test OUR wiring logic, not Groq/ChromaDB.

The one new thing tested here that query.py didn't have: each function
picks a DEFAULT search query when the caller doesn't provide one
(e.g. analyze_architecture() with no args should search broadly for
"architecture entry points" -- not fail, and not search for "").
That default-vs-custom branching is exactly the kind of logic bug
mocking lets us catch cheaply.

Run with: pytest tests/test_analyze.py -v
"""
from unittest.mock import patch
from src.tools.analyze import (
    analyze_architecture,
    trace_execution_flow,
    identify_design_patterns,
)


FAKE_CHUNKS = [{"path": "src/main.py", "content": "def run(): pass"}]


# ---------- analyze_architecture ----------

def test_architecture_uses_default_query_when_none_given():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Architecture explanation."

        analyze_architecture()  # no specific_question passed

        # the embedded text should be the broad default, not empty
        embedded_text = mock_embed.call_args[0][0]
        assert embedded_text != ""
        assert "architecture" in embedded_text.lower()


def test_architecture_uses_custom_question_when_given():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Answer about auth."

        analyze_architecture(specific_question="how does auth work?")

        mock_embed.assert_called_once_with("how does auth work?")


def test_architecture_returns_expected_shape():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Architecture explanation."

        result = analyze_architecture()

        assert result["success"] is True
        assert result["answer"] == "Architecture explanation."
        assert result["sources"] == ["src/main.py"]


# ---------- trace_execution_flow ----------

def test_trace_embeds_the_starting_point_directly():
    """Unlike analyze_architecture, this function has no default --
    it should always embed exactly what the caller passed in."""
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Trace explanation."

        trace_execution_flow("user login")

        mock_embed.assert_called_once_with("user login")


def test_trace_returns_starting_point_in_result():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Trace explanation."

        result = trace_execution_flow("file upload")

        assert result["starting_point"] == "file upload"
        assert result["success"] is True


# ---------- identify_design_patterns ----------

def test_patterns_uses_default_query_when_no_focus_area():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Patterns explanation."

        identify_design_patterns()  # no focus_area passed

        embedded_text = mock_embed.call_args[0][0]
        assert embedded_text != ""
        assert "pattern" in embedded_text.lower()


def test_patterns_uses_custom_focus_area_when_given():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Patterns in store layer."

        identify_design_patterns(focus_area="storage layer")

        mock_embed.assert_called_once_with("storage layer")


def test_patterns_returns_expected_shape():
    with patch("src.tools.analyze.embed_query") as mock_embed, \
         patch("src.tools.analyze.query_chunks") as mock_query, \
         patch("src.tools.analyze.call_llm") as mock_llm:

        mock_embed.return_value = [0.0]
        mock_query.return_value = FAKE_CHUNKS
        mock_llm.return_value = "Patterns explanation."

        result = identify_design_patterns()

        assert result["success"] is True
        assert result["sources"] == ["src/main.py"]