"""Phase 11b — Azure AI Agent (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 11b — Azure AI Agent", page_icon="☁️", layout="wide")

st.markdown(phase_header(
    "Phase 11b &nbsp;·&nbsp; Managed Platforms &nbsp;·&nbsp; Coming Soon",
    "☁️ Azure AI Agent Service",
    "Microsoft's managed agent service — built on OpenAI Assistants API with "
    "Active Directory, Key Vault, and enterprise compliance built-in.",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

st.markdown("### What this phase will cover")
st.markdown("""
- Microsoft Azure AI Agent Service — built on OpenAI Assistants API
- Runs on Azure OpenAI or other Azure-hosted models
- Enterprise integration: Active Directory, Azure Key Vault, compliance
- Persistent threads and file search built-in (same as OpenAI Assistants)
- When to use: Microsoft-stack enterprises, Azure-native deployments
""")

st.markdown("---")
st.markdown("### What's next → Phase 11c — AWS Bedrock")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
