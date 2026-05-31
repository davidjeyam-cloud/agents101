"""Phase 11e — Platform Comparison (Coming Soon)"""
import streamlit as st

st.set_page_config(page_title="Phase 11e — Platform Comparison", page_icon="☁️", layout="wide")


st.markdown("""
<div style="background:rgba(230,235,240,0.6);border:2px dashed #AEB6BF;border-radius:12px;
padding:32px;text-align:center;margin-bottom:28px;">
  <div style="font-size:2.5rem;margin-bottom:10px;">☁️</div>
  <div style="font-size:1.5rem;font-weight:700;color:#1C2833;margin-bottom:6px;">Phase 11e — Platform Comparison</div>
  <div style="font-size:0.75rem;font-weight:700;letter-spacing:2px;color:#D35400;
              text-transform:uppercase;margin-bottom:10px;">Phase 11 — Managed Platforms</div>
  <div style="color:#5D6D7E;font-size:0.9rem;">
    This module is planned — content will be added as the course progresses in sequence.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### What this phase will cover")
st.markdown("""
- Decision guide: Vertex AI vs Azure vs Bedrock vs OpenAI Assistants
- Cost model comparison: per-token vs per-request vs per-session
- Vendor lock-in risk: how much custom code do you need to migrate?
- Open-source alternative: self-hosted LangServe / ADK on GKE
- The meta-lesson: managed platforms trade control for operational simplicity
""")

st.markdown("---")
st.markdown("### You have reached the end of the planned course — well done!")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
