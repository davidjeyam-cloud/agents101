"""
Phase 0 — Hello Gemini
Verify your API key works and make your first LLM call.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Phase 0 — Hello Gemini", page_icon="👋", layout="wide")

# ── Phase 0 header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#0D1117 0%,#0F1A2E 100%);
border-left:5px solid #00FF9F;border-radius:8px;padding:18px 24px;margin-bottom:24px'>
  <div style='font-size:0.65rem;font-weight:700;letter-spacing:3px;
              text-transform:uppercase;color:#00FF9F;margin-bottom:6px'>
    Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Setup
  </div>
  <div style='font-size:1.7rem;font-weight:800;color:#E6EDF3;line-height:1.2'>
    👋 Hello Gemini
  </div>
  <div style='font-size:0.88rem;color:#8B949E;margin-top:6px'>
    Confirm your API key is working and make your first live LLM call.
    Every pattern in this course runs on this one call.
  </div>
</div>
""", unsafe_allow_html=True)

# ── API key check ──────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "**GEMINI_API_KEY not found.**\n\n"
        "1. Copy `.env.example` → `.env`\n"
        "2. Paste your key from [Google AI Studio](https://aistudio.google.com/apikey)\n"
        "3. Restart Streamlit (`Ctrl+C` then `streamlit run app.py`)"
    )
    st.stop()

st.success(f"✅ API key loaded — `{api_key[:8]}...{api_key[-4:]}`")

st.markdown("---")

# ── Concept explainer ──────────────────────────────────────────────────────────
with st.expander("📖 What is the most basic agentic building block?"):
    st.markdown("""
Before we build agents, we need **one reliable LLM call**.
Every pattern in this cookbook — chaining, routing, parallelization, agents —
is just this one call, composed in different ways.

The Anthropic article calls this the **Augmented LLM**:
> *"The basic building block of agentic systems is an LLM enhanced with
> augmentations such as retrieval, tools, and memory."*

In Phase 0 we strip away the augmentations and prove the bare call works.
In Phase 1 we'll add them back one by one.
""")

# ── Live demo ──────────────────────────────────────────────────────────────────
st.subheader("Try it — ask the model anything")

prompt = st.text_input(
    "Your question:",
    value="What is agentic AI in one sentence?",
    placeholder="Type a question and press Send",
)

if st.button("Send", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Calling Gemini 2.5 Flash…"):
            try:
                from google import genai as _genai
                from utils.llm import _call

                _client = _genai.Client(api_key=api_key)
                _MODEL  = "gemini-2.5-flash"
                _resp   = _call(_client.models.generate_content, model=_MODEL, contents=prompt)

                st.markdown("**Response:**")
                st.markdown(_resp.text)

                with st.expander("🔍 What just happened under the hood?"):
                    st.code(f'''from google import genai

client   = genai.Client(api_key=YOUR_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="{prompt}",
)
print(response.text)''', language="python")
                    st.markdown("""
`utils/llm.py` is our wrapper — it loads the key, creates the client, calls the model,
and returns plain text. Every phase uses the same function.
To swap the model, change **one line** in `utils/llm.py`.
""")

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown("### What's next → Phase 1 — The Augmented LLM")
st.markdown(
    "We'll take this bare call and add three capabilities: "
    "**Memory** (the model remembers the conversation), "
    "**Tools** (it can call real functions), and "
    "**Agency** (it decides its own next step)."
)
