"""Phase 11e — Platform Comparison (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 11e — Platform Comparison", page_icon="☁️", layout="wide")

st.markdown(phase_header(
    "Phase 11e &nbsp;·&nbsp; Managed Platforms &nbsp;·&nbsp; Coming Soon",
    "☁️ Platform Comparison",
    "Decision guide — Vertex AI vs Azure vs Bedrock vs OpenAI Assistants. "
    "Cost models, vendor lock-in risk, and when to self-host instead.",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

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
