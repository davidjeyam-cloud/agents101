"""Phase 8b — Coding Agent (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 8b — Coding Agent", page_icon="💻", layout="wide")

st.markdown(phase_header(
    "Phase 8b &nbsp;·&nbsp; Agents in Practice &nbsp;·&nbsp; Coming Soon",
    "💻 Coding Agent",
    "GitHub issue → read codebase → write fix → run tests → iterate → PR. "
    "The closest real-world coding agent to Claude Code.",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

st.markdown("### What this phase will cover")
st.markdown("""
- Full production build — Anthropic Appendix 1
- GitHub issue → read codebase → write fix → run tests → iterate → PR
- Combines: RAG over codebase (5a) + code execution (3d) + reflection (3b)
- ReAct loop with real filesystem tools, not mocked APIs
- Closest to Claude Code — shows how production coding agents work
""")

st.markdown("---")
st.markdown("### What's next → Phase 9 — Best Practices")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
