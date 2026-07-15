"""
RepoProfessor MCP — Streamlit Frontend
Day 4: Chat interface with tool selector, repo path input, and source display.
"""

import streamlit as st
import sys
from pathlib import Path

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.ingest import ingest_repo
from src.tools.query import ask_repo
from src.tools.analyze import analyze_architecture, trace_execution_flow, identify_design_patterns
from src.tools.teach import explain_like_senior, generate_learning_path
from src.tools.docs import generate_documentation
from src.store.store import get_collection_stats

# ─── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RepoProfessor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Pacifico&display=swap');

/* ✨ Winx Club Bloom palette ✨ */
:root {
    --bg:        #1a0a1e;
    --bg-card:   #26102e;
    --border:    #7a3a8a;
    --accent:    #ff6eb4;
    --accent2:   #ff9de2;
    --flame:     #ff4d6d;
    --gold:      #ffd166;
    --text:      #ffe6f4;
    --muted:     #c48fbb;
    --danger:    #ff4d6d;
    --glow:      rgba(255, 110, 180, 0.35);
}

@keyframes sparkle {
    0%,100% { opacity: 1; transform: scale(1) rotate(0deg); }
    50%      { opacity: 0.6; transform: scale(1.3) rotate(180deg); }
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-6px); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #3a0a4a 0%, #1a0a1e 50%, #0d0515 100%) !important;
    color: var(--text);
    font-family: 'Quicksand', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2a0a38 0%, #1a0a1e 100%) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 24px rgba(255,110,180,0.1);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hide default Streamlit header/footer */
#MainMenu, footer, header { visibility: hidden; }

/* Custom app header */
.rp-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 0 22px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
    animation: fadeInUp 0.6s ease both;
}
.rp-header h1 {
    font-family: 'Pacifico', cursive;
    font-size: 2rem;
    margin: 0;
    background: linear-gradient(135deg, #ff6eb4 0%, #ffd166 50%, #ff9de2 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
    filter: drop-shadow(0 0 12px rgba(255,110,180,0.5));
}
.rp-header span {
    font-family: 'Quicksand', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--muted);
    padding: 3px 10px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: rgba(255,110,180,0.07);
    letter-spacing: 0.5px;
}

/* Chat messages */
.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 16px 0 6px 0;
    animation: fadeInUp 0.3s ease both;
}
.chat-user .bubble {
    background: linear-gradient(135deg, #ff6eb4, #ff4d6d);
    color: #fff;
    padding: 11px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 72%;
    font-size: 0.92rem;
    line-height: 1.5;
    font-weight: 600;
    box-shadow: 0 4px 20px rgba(255,77,109,0.4);
}

.chat-bot {
    display: flex;
    justify-content: flex-start;
    margin: 6px 0 16px 0;
    gap: 12px;
    animation: fadeInUp 0.3s ease both;
}
.chat-bot .avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6eb4, #ffd166);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    margin-top: 2px;
    box-shadow: 0 0 16px var(--glow);
    animation: float 3s ease-in-out infinite;
}
.chat-bot .bubble {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 14px 18px;
    border-radius: 4px 20px 20px 20px;
    max-width: 82%;
    font-size: 0.92rem;
    line-height: 1.65;
    box-shadow: 0 2px 16px rgba(122,58,138,0.3);
}

/* Sources bar */
.sources-bar {
    margin-top: 10px;
    padding: 8px 14px;
    background: rgba(255,110,180,0.06);
    border: 1px solid rgba(255,110,180,0.25);
    border-radius: 12px;
    font-size: 0.68rem;
    color: var(--muted);
    font-family: 'Quicksand', sans-serif;
    font-weight: 600;
}
.sources-bar strong { color: var(--accent); }

/* Tool pills */
.tool-label {
    display: inline-block;
    font-size: 0.65rem;
    padding: 2px 10px;
    border-radius: 20px;
    background: rgba(255,110,180,0.1);
    border: 1px solid var(--accent);
    color: var(--accent);
    margin-bottom: 8px;
    font-weight: 700;
}

/* Error box */
.error-box {
    padding: 12px 16px;
    border: 1px solid var(--danger);
    border-radius: 12px;
    background: rgba(255,77,109,0.08);
    color: #ff9de2;
    font-size: 0.88rem;
    font-weight: 600;
}

/* Streamlit widget overrides */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff6eb4, #ff4d6d) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 20px !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 8px 22px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(255,110,180,0.4) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(255,110,180,0.6) !important;
}

.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

.stCheckbox > label { color: var(--text) !important; font-weight: 600 !important; }

div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 {
    color: var(--text) !important;
}
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2 {
    color: var(--accent) !important;
}
div[data-testid="stMarkdownContainer"] strong { color: var(--gold) !important; }

div[data-testid="stMarkdownContainer"] code {
    background: rgba(255,110,180,0.12) !important;
    color: var(--accent2) !important;
    font-size: 0.82em !important;
    padding: 2px 6px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(255,110,180,0.2) !important;
}
div[data-testid="stMarkdownContainer"] pre {
    background: #1a0a1e !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

hr { border-color: rgba(122,58,138,0.4) !important; }

.stSpinner > div { border-top-color: var(--accent) !important; }

.stSuccess {
    background: rgba(255,110,180,0.1) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent2) !important;
    border-radius: 12px !important;
}
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "repo_ingested" not in st.session_state:
    st.session_state.repo_ingested = False
if "repo_meta" not in st.session_state:
    st.session_state.repo_meta = {}

# ─── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = {
    "💬 Ask anything": {
        "id": "ask",
        "description": "Ask any question about the codebase",
        "placeholder": "What does the ingest pipeline do?",
        "needs_input": True,
    },
    "🏛️ Architecture overview": {
        "id": "architecture",
        "description": "Analyze components, layers, and relationships",
        "placeholder": "Optional: focus on a specific part (or leave empty)",
        "needs_input": True,
    },
    "🔍 Trace execution flow": {
        "id": "trace",
        "description": "Follow code execution from a starting point",
        "placeholder": "e.g. repository ingestion, user query, file upload",
        "needs_input": True,
    },
    "🧩 Find design patterns": {
        "id": "patterns",
        "description": "Identify patterns like Factory, Repository, RAG, etc.",
        "placeholder": "Optional: focus area (or leave empty for full scan)",
        "needs_input": True,
    },
    "🎓 Explain like a senior": {
        "id": "explain",
        "description": "Deep explanation of a concept with WHY and tradeoffs",
        "placeholder": "e.g. the embedding pipeline, ChromaDB storage design",
        "needs_input": True,
    },
    "🗺️ Learning path": {
        "id": "learning",
        "description": "Structured roadmap to understand this codebase",
        "placeholder": "",
        "needs_input": False,
        "options": ["beginner", "intermediate", "advanced"],
    },
    "📄 Generate docs": {
        "id": "docs",
        "description": "Generate README, architecture doc, or contributing guide",
        "placeholder": "",
        "needs_input": False,
        "options": ["readme", "architecture", "contributing"],
    },
}

# ─── Tool runner ──────────────────────────────────────────────────────────────

def run_tool(tool_id: str, input_text: str, option: str = "") -> dict:
    if tool_id == "ask":
        return ask_repo(input_text)
    elif tool_id == "architecture":
        return analyze_architecture(input_text)
    elif tool_id == "trace":
        return trace_execution_flow(input_text)
    elif tool_id == "patterns":
        return identify_design_patterns(input_text)
    elif tool_id == "explain":
        return explain_like_senior(input_text)
    elif tool_id == "learning":
        return generate_learning_path(option or "beginner")
    elif tool_id == "docs":
        return generate_documentation(option or "readme")
    return {"success": False, "error": "Unknown tool"}

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 20px 0;">
        <div style="font-family: 'Pacifico', cursive; font-size: 1.3rem; background: linear-gradient(135deg, #ff6eb4, #ffd166); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            ✨ RepoProfessor
        </div>
        <div style="font-family: 'Quicksand', sans-serif; font-weight: 600; font-size: 0.7rem; color: #c48fbb; margin-top: 4px;">
            MCP Teaching Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Repository Path**")
    repo_path = st.text_input(
        "repo_path",
        label_visibility="collapsed",
        placeholder="E:\\PROJECTS\\my-repo",
        key="repo_path_input",
    )

    clear_existing = st.checkbox("Clear previous ingestion", value=True)

    if st.button("⚡ Ingest Repository", use_container_width=True):
        if not repo_path.strip():
            st.error("Enter a repository path first.")
        else:
            with st.spinner("Scanning, embedding, storing…"):
                result = ingest_repo(repo_path.strip(), clear_existing)
            if result["success"]:
                st.session_state.repo_ingested = True
                st.session_state.repo_meta = result
                st.session_state.messages = []
                st.success(
                    f"✓ {result['total_files']} files · {result['total_chunks']} chunks"
                )
            else:
                st.error(result.get("error", "Ingestion failed"))

    # Status
    st.markdown("---")
    stats = get_collection_stats()
    if stats["total_chunks"] > 0:
        meta = st.session_state.repo_meta
        st.markdown(f"""
        <div style="font-family: 'Quicksand', sans-serif; font-weight: 700; font-size: 0.72rem; color: #ff6eb4;">
            ✦ INDEXED
        </div>
        <div style="font-size: 0.78rem; color: #c48fbb; margin-top: 6px; font-family: 'Quicksand', sans-serif; font-weight: 600;">
            {stats['total_chunks']:,} chunks stored
        </div>
        """, unsafe_allow_html=True)
        if meta.get("languages"):
            lang_str = " · ".join(f"{v} {k}" for k, v in meta["languages"].items())
            st.markdown(
                f'<div style="font-size: 0.7rem; color: #c48fbb; font-family: Quicksand, sans-serif; font-weight: 600; margin-top: 4px;">{lang_str}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div style="font-family: \'Quicksand\', sans-serif; font-weight: 700; font-size: 0.72rem; color: #7a3a8a;">○ NO REPO INDEXED</div>',
            unsafe_allow_html=True
        )

    # Clear chat
    st.markdown("---")
    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # About
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.72rem; color: #c48fbb; font-family: 'Quicksand', sans-serif; font-weight: 600; line-height: 1.6;">
        Stack: FastMCP · ChromaDB<br>
        LLM: Groq llama-3.3-70b<br>
        Embeddings: all-MiniLM-L6-v2
    </div>
    """, unsafe_allow_html=True)

# ─── Main area ────────────────────────────────────────────────────────────────

st.markdown("""
<div class="rp-header">
    <h1>RepoProfessor</h1>
    <span>codebase teaching assistant</span>
</div>
""", unsafe_allow_html=True)

# Tool selector
selected_tool_name = st.selectbox(
    "Tool",
    list(TOOLS.keys()),
    label_visibility="collapsed",
)
tool = TOOLS[selected_tool_name]

st.markdown(
    f'<div style="font-size: 0.8rem; color: #c48fbb; margin: -4px 0 16px 0; font-family: Quicksand, sans-serif; font-weight: 600;">'
    f'{tool["description"]}</div>',
    unsafe_allow_html=True
)

# Input row
col_input, col_option, col_btn = st.columns([5, 2, 1])

with col_input:
    if tool["needs_input"]:
        user_input = st.text_input(
            "input",
            label_visibility="collapsed",
            placeholder=tool["placeholder"],
            key="chat_input",
        )
    else:
        user_input = ""
        st.markdown("")

with col_option:
    if "options" in tool:
        option_val = st.selectbox(
            "option",
            tool["options"],
            label_visibility="collapsed",
            key="tool_option",
        )
    else:
        option_val = ""
        st.markdown("")

with col_btn:
    send = st.button("▶ Run", use_container_width=True)

# Run on button press
if send:
    if not st.session_state.repo_ingested and get_collection_stats()["total_chunks"] == 0:
        st.markdown(
            '<div class="error-box">⚠ No repository indexed. Use the sidebar to ingest a repo first.</div>',
            unsafe_allow_html=True
        )
    elif tool["needs_input"] and not user_input.strip():
        st.markdown(
            '<div class="error-box">⚠ Enter a question or topic above.</div>',
            unsafe_allow_html=True
        )
    else:
        # Build display prompt
        if tool["needs_input"]:
            display_prompt = user_input.strip()
        else:
            display_prompt = f"{selected_tool_name}" + (f" ({option_val})" if option_val else "")

        st.session_state.messages.append({
            "role": "user",
            "tool": selected_tool_name,
            "content": display_prompt,
        })

        with st.spinner("Professor is thinking…"):
            result = run_tool(
                tool["id"],
                user_input.strip(),
                option_val,
            )

        if result.get("success"):
            st.session_state.messages.append({
                "role": "assistant",
                "tool": selected_tool_name,
                "content": result.get("answer", ""),
                "sources": result.get("sources", []),
            })
        else:
            st.session_state.messages.append({
                "role": "error",
                "content": result.get("error", "Unknown error occurred."),
            })

        st.rerun()

# ─── Chat history ─────────────────────────────────────────────────────────────

st.markdown("---")

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 60px 0; color: #c48fbb;">
        <div style="font-size: 2.5rem; margin-bottom: 12px; animation: float 3s ease-in-out infinite; display: inline-block;">🧚‍♀️</div>
        <div style="font-family: 'Pacifico', cursive; font-size: 1.1rem; background: linear-gradient(135deg, #ff6eb4, #ffd166); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Ingest a repository, then ask anything.
        </div>
        <div style="font-family: 'Quicksand', sans-serif; font-weight: 600; font-size: 0.75rem; margin-top: 10px; color: #7a3a8a;">
            ✦ architecture · execution flow · design patterns · learning paths · docs ✦
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in reversed(st.session_state.messages):  # newest first
        if msg["role"] == "user":
            tool_label = msg.get("tool", "")
            st.markdown(
                f'<div class="chat-user">'
                f'<div class="bubble">'
                f'<div style="font-size:0.65rem; opacity:0.7; margin-bottom:4px; font-family: Space Mono, monospace;">{tool_label}</div>'
                f'{msg["content"]}'
                f'</div></div>',
                unsafe_allow_html=True
            )
        elif msg["role"] == "assistant":
            sources = msg.get("sources", [])
            unique_sources = list(dict.fromkeys(sources))

            sources_html = ""
            if unique_sources:
                files = " &nbsp;·&nbsp; ".join(
                    f'<code style="font-size:0.68rem;">{s}</code>'
                    for s in unique_sources[:8]
                )
                extra = f" +{len(unique_sources)-8} more" if len(unique_sources) > 8 else ""
                sources_html = (
                    f'<div class="sources-bar">'
                    f'<strong>sources</strong> &nbsp; {files}{extra}'
                    f'</div>'
                )

            st.markdown(
                '<div class="chat-bot">'
                '<div class="avatar">🎓</div>'
                '<div style="flex:1; min-width:0;">',
                unsafe_allow_html=True
            )
            st.markdown(msg["content"])
            st.markdown(f'{sources_html}</div></div>', unsafe_allow_html=True)
        elif msg["role"] == "error":
            st.markdown(
                f'<div class="error-box">⚠ {msg["content"]}</div>',
                unsafe_allow_html=True
            )