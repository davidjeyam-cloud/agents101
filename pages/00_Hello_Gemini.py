"""
Phase 0 — Hello Gemini
Verify your API key works and make your first LLM call.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Phase 0 — Hello Gemini", page_icon="👋", layout="centered")

st.title("👋 Phase 0 — Hello Gemini")
st.caption("Goal: confirm your API key works and make your first LLM call.")

st.markdown("---")

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

st.success(f"API key loaded — `{api_key[:8]}...{api_key[-4:]}`")

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

    In Phase 0, we strip away the augmentations and prove the bare call works.
    In Phase 1, we'll add them back one by one.
    """)

# ── Live demo ──────────────────────────────────────────────────────────────────
st.subheader("Try it — ask Gemini anything")

prompt = st.text_input(
    "Your question:",
    value="What is agentic AI in one sentence?",
    placeholder="Type a question and hit Enter or click Send",
)

if st.button("Send", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Calling Gemini 2.5 Flash..."):
            try:
                import sys, os
                from google import genai as _genai
                from utils.llm import _call

                _api_key = os.getenv("GEMINI_API_KEY")
                _client  = _genai.Client(api_key=_api_key)
                _MODEL   = "gemini-2.5-flash"

                _response = _call(
                    _client.models.generate_content,
                    model=_MODEL,
                    contents=prompt,
                )
                reply = _response.text

                st.markdown("### Gemini replied:")
                st.markdown(reply)

                with st.expander("🔍 What just happened under the hood?"):
                    st.code(
                        f"""from google import genai

client = genai.Client(api_key=YOUR_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="{prompt}",
)
print(response.text)
""",
                        language="python",
                    )
                    st.markdown("""
**`utils/llm.py`** is our wrapper. It:
1. Loads `GEMINI_API_KEY` from `.env`
2. Creates a `google.genai.Client` with that key
3. Calls `client.models.generate_content(model="gemini-2.5-flash", ...)`
4. Returns the plain text reply

Every phase will call the same `chat()` function.
To use a different model, change **one line** in `utils/llm.py`.
                    """)

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ── What's next ───────────────────────────────────────────────────────────────
st.markdown("""
### What's next → Phase 1: The Augmented LLM

We'll take this bare call and add three capabilities:
- **Memory** — the model remembers earlier parts of the conversation
- **Tools** — the model can call functions (look up data, do calculations)
- **Retrieval** — the model can search a knowledge base before answering
""")
