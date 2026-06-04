"""Phase 11c — AWS Bedrock Agents (Coming Soon)"""
import streamlit as st
from utils.styles import phase_header, ACCENT_COMING

st.set_page_config(page_title="Phase 11c — AWS Bedrock Agents", page_icon="☁️", layout="wide")

st.markdown(phase_header(
    "Phase 11c &nbsp;·&nbsp; Managed Platforms &nbsp;·&nbsp; Coming Soon",
    "☁️ AWS Bedrock Agents",
    "Multi-model Amazon Bedrock Agents — Lambda action groups, S3 knowledge bases, "
    "and guardrails. The AWS-native path to production agents.",
    accent=ACCENT_COMING,
), unsafe_allow_html=True)
st.info("🔜 This phase is planned and will be built as the course progresses in sequence.")

st.markdown("### What this phase will cover")
st.markdown("""
- Amazon Bedrock Agents — multi-model (Claude, Titan, Llama, Mistral)
- Action groups: Lambda functions as agent tools
- Knowledge bases: S3 + OpenSearch for RAG (same pattern as Phase 5a)
- Guardrails: content filtering and PII redaction (same as Phase 4a)
- When to use: AWS-native deployments, multi-model flexibility
""")

st.markdown("---")
st.markdown("### What's next → Phase 11d — OpenAI Assistants")
st.caption("Navigate using the sidebar to return to Home or continue to another completed phase.")
