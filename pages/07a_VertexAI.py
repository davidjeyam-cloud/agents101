"""Phase 11a — Vertex AI Agents (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 11a — Vertex AI Agents", page_icon="☁️", layout="wide")

st.markdown(phase_header(
    "Phase 11a &nbsp;·&nbsp; Managed Platforms &nbsp;·&nbsp; Coming Soon",
    "☁️ Vertex AI Agents",
    "Google's managed agent engine — autoscaling, grounding to Google Search, "
    "Agent Builder, and enterprise IAM built-in.",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

st.markdown("### What this phase will cover")
st.markdown("""
- Google's managed agent engine on Vertex AI
- Deploy Gemini agents with autoscaling, logging, and IAM built-in
- Grounding: connect to Google Search and enterprise data sources
- Agent Builder: low-code agent configuration for non-engineers
- When to use: production Google Cloud deployments, enterprise Gemini
""")

st.markdown("---")
st.markdown("### What's next → Phase 11b — Azure AI Agent")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
