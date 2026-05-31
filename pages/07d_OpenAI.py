"""Phase 11d — OpenAI Assistants (Coming Soon)"""
import streamlit as st

st.set_page_config(page_title="Phase 11d — OpenAI Assistants", page_icon="☁️", layout="wide")


st.markdown("""
<div style="background:rgba(230,235,240,0.6);border:2px dashed #AEB6BF;border-radius:12px;
padding:32px;text-align:center;margin-bottom:28px;">
  <div style="font-size:2.5rem;margin-bottom:10px;">☁️</div>
  <div style="font-size:1.5rem;font-weight:700;color:#1C2833;margin-bottom:6px;">Phase 11d — OpenAI Assistants</div>
  <div style="font-size:0.75rem;font-weight:700;letter-spacing:2px;color:#D35400;
              text-transform:uppercase;margin-bottom:10px;">Phase 11 — Managed Platforms</div>
  <div style="color:#5D6D7E;font-size:0.9rem;">
    This module is planned — content will be added as the course progresses in sequence.
  </div>
</div>
""", unsafe_allow_html=True)

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
