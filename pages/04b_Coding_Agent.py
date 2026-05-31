"""Phase 8b — Coding Agent (Coming Soon)"""
import streamlit as st

st.set_page_config(page_title="Phase 8b — Coding Agent", page_icon="💻", layout="wide")


st.markdown("""
<div style="background:rgba(230,235,240,0.6);border:2px dashed #AEB6BF;border-radius:12px;
padding:32px;text-align:center;margin-bottom:28px;">
  <div style="font-size:2.5rem;margin-bottom:10px;">💻</div>
  <div style="font-size:1.5rem;font-weight:700;color:#1C2833;margin-bottom:6px;">Phase 8b — Coding Agent</div>
  <div style="font-size:0.75rem;font-weight:700;letter-spacing:2px;color:#D35400;
              text-transform:uppercase;margin-bottom:10px;">Phase 8 — Agents in Practice</div>
  <div style="color:#5D6D7E;font-size:0.9rem;">
    This module is planned — content will be added as the course progresses in sequence.
  </div>
</div>
""", unsafe_allow_html=True)

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
