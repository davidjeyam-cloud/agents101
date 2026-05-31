"""Phase 10a — LangGraph Workflows (Coming Soon)"""
import streamlit as st

st.set_page_config(page_title="Phase 10a — LangGraph Workflows", page_icon="🕸️", layout="wide")


st.markdown("""
<div style="background:rgba(230,235,240,0.6);border:2px dashed #AEB6BF;border-radius:12px;
padding:32px;text-align:center;margin-bottom:28px;">
  <div style="font-size:2.5rem;margin-bottom:10px;">🕸️</div>
  <div style="font-size:1.5rem;font-weight:700;color:#1C2833;margin-bottom:6px;">Phase 10a — LangGraph Workflows</div>
  <div style="font-size:0.75rem;font-weight:700;letter-spacing:2px;color:#D35400;
              text-transform:uppercase;margin-bottom:10px;">Phase 10 — Frameworks Layer</div>
  <div style="color:#5D6D7E;font-size:0.9rem;">
    This module is planned — content will be added as the course progresses in sequence.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### What this phase will cover")
st.markdown("""
- Reimplement Phase 2 workflow patterns as LangGraph state graphs
- Nodes = LLM calls or tools; Edges = transitions; State = shared dict
- Conditional edges replace if/else routing from Phase 2b
- Parallel nodes replace ThreadPoolExecutor from Phase 2c
- Key insight: LangGraph is just a graph execution engine over patterns you built from scratch
""")

st.markdown("---")
st.markdown("### What's next → Phase 10b — LangGraph Agents")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
