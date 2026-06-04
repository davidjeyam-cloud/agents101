"""Phase 11d — OpenAI Assistants (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 11d — OpenAI Assistants", page_icon="☁️", layout="wide")

st.markdown(phase_header(
    "Phase 11d &nbsp;·&nbsp; Managed Platforms &nbsp;·&nbsp; Coming Soon",
    "☁️ OpenAI Assistants API",
    "Threads, Runs, Messages — OpenAI's hosted agent runtime with built-in "
    "code interpreter (Phase 3d equivalent) and file search (Phase 5a equivalent).",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

st.markdown("### What this phase will cover")
st.markdown("""
- OpenAI Assistants API: Threads, Runs, Messages, Files
- Built-in tools: code interpreter (Phase 3d equivalent), file search (Phase 5a equivalent)
- Persistent threads replace Phase 1b memory pattern
- Vector stores for file search — hosted RAG without managing embeddings
- When to use: GPT-4o agents, when OpenAI's ecosystem is preferred
""")

st.markdown("---")
st.markdown("### What's next → Phase 11e — Platform Comparison")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
