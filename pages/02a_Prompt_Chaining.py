"""
Phase 2a — Prompt Chaining
Sequential LLM calls where each output feeds the next input.
Demo: Customer complaint → Classify → Gate → Draft → Polish → Final Email
"""

import streamlit as st
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 2a — Prompt Chaining", page_icon="🔗", layout="wide")
st.title("🔗 Phase 2a — Prompt Chaining")
st.caption("Workflow Pattern 1 of 5 — from *Building Effective Agents*, Anthropic Engineering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_2a
st.image(diagram_2a(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Prompt Chaining?"):
    st.markdown("""
    > *"Prompt chaining decomposes a task into a sequence of steps, where each LLM call
    > processes the output of the previous one."*
    > — Anthropic, Building Effective Agents

    **When to use it:**
    - The task is too complex for a single prompt
    - Each step needs its own focus / persona / instructions
    - You want to validate or gate intermediate results before continuing

    **The gate concept:**
    Between steps, your code can run a programmatic check.
    If the check fails (e.g. input is spam), the chain stops early — no wasted LLM calls.

    **Why it is NOT an Agent:**
    You wrote `step1 → gate → step2 → step3`. The LLM never decides what comes next.
    It only processes its own step.

    **Compared to Phase 1:**
    - 1c: ONE LLM call, picks a tool → returns
    - 2a: THREE LLM calls in sequence, each building on the last
    """)

st.markdown("---")

# ── Chain functions ────────────────────────────────────────────────────────────

def step1_classify(complaint: str) -> dict:
    """Step 1 — Classify the complaint. Returns structured JSON."""
    prompt = f"""You are a customer support classifier.
Classify the complaint below into exactly one category.

Categories:
- billing    : payment, invoice, charge, refund, subscription
- technical  : app crash, bug, error, login, performance
- general    : feedback, question, request, compliment
- spam       : not a real complaint, gibberish, advertisement

Reply with valid JSON only, no markdown:
{{"category": "...", "urgency": "high|medium|low", "summary": "one sentence"}}

Complaint: {complaint}"""

    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"category": "general", "urgency": "medium", "summary": complaint[:80]}


def step2_draft(complaint: str, classification: dict) -> str:
    """Step 2 — Draft a reply tailored to the classification."""
    tone_map = {
        "billing":   "apologetic and precise — acknowledge the financial concern directly",
        "technical": "technical and empathetic — show you understand the frustration",
        "general":   "friendly and helpful",
    }
    tone = tone_map.get(classification["category"], "professional and helpful")
    urgency = classification["urgency"]

    prompt = f"""You are a customer support agent drafting a reply.

Classification: {classification['category'].upper()} | Urgency: {urgency}
Tone required: {tone}

Customer complaint:
\"\"\"{complaint}\"\"\"

Write a draft reply that:
- Opens by acknowledging the specific issue
- Provides a clear next step or resolution
- Matches the tone above
- Is 3–4 sentences

Draft:"""

    response = _call(client.models.generate_content, model=MODEL, contents=prompt)
    return response.text.strip()


def step3_polish(draft: str, classification: dict) -> str:
    """Step 3 — Polish the draft into a professional customer email."""
    prompt = f"""You are a senior customer support editor.
Polish the draft below into a professional, warm customer-facing email.

Rules:
- Keep the same resolution/content — do not add or remove facts
- Improve flow, grammar, and empathy
- Add a proper greeting (Dear Customer,) and sign-off (Best regards, Support Team)
- {classification['category'].capitalize()} issue — adjust tone accordingly

Draft to polish:
\"\"\"{draft}\"\"\"

Polished email:"""

    response = _call(client.models.generate_content, model=MODEL, contents=prompt)
    return response.text.strip()


# ── UI ─────────────────────────────────────────────────────────────────────────

EXAMPLES = {
    "Billing issue":   "I was charged twice for my subscription this month. I see two charges of $29.99 on my credit card statement dated the 3rd and 5th. Please refund the duplicate charge immediately.",
    "Technical issue": "Your app keeps crashing every time I try to upload a photo. I've tried reinstalling it three times but the problem persists. This is really frustrating as I need it for work.",
    "General feedback":"I've been using your service for 2 years and overall it's great! Just wanted to suggest adding a dark mode — it would really help late-night users like me.",
    "Spam (gate test)": "BUY CHEAP WATCHES!! CLICK HERE NOW!!! BEST PRICES GUARANTEED!!!",
}

if "sel_2a" not in st.session_state:
    st.session_state.sel_2a = EXAMPLES["Billing issue"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Quick examples:**")
    for label, text in EXAMPLES.items():
        if st.button(label, key=f"ex_{label}"):
            st.session_state.sel_2a = text
            st.rerun()
with col1:
    complaint = st.text_area(
        "Customer complaint:",
        value=st.session_state.sel_2a,
        height=110,
    )

st.markdown("---")

if st.button("▶  Run Chain", type="primary", key="run_2a"):

    if not complaint.strip():
        st.warning("Please enter a complaint.")
        st.stop()

    # ── STEP 1 — Classify ────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 1 — 🏷️ Classify")
        st.caption("LLM reads the complaint and outputs a structured classification.")
        col_in, col_arrow, col_out = st.columns([5, 1, 5])
        with col_in:
            st.markdown("**Input:**")
            st.info(complaint[:200] + ("…" if len(complaint) > 200 else ""))
        with col_arrow:
            st.markdown("<div style='text-align:center;font-size:2rem;margin-top:1.5rem'>→</div>",
                        unsafe_allow_html=True)
        with col_out:
            with st.spinner("Classifying…"):
                classification = step1_classify(complaint)
            st.markdown("**Output (feeds Step 2):**")
            st.json(classification)

    # ── GATE CHECK ───────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Gate — ✅ / ✗ Programmatic check before continuing")
        st.caption("Your code inspects the classification. If spam → chain stops. No LLM called.")

        if classification.get("category") == "spam":
            st.error(
                "**✗ Gate FAILED — chain stopped.**\n\n"
                f"Classification returned `spam`. "
                "No further LLM calls made — Steps 2 & 3 skipped entirely.\n\n"
                "This is the power of gates: early exit saves tokens and time."
            )
            st.stop()
        else:
            st.success(
                f"**✓ Gate PASSED** — category is `{classification.get('category')}`, "
                f"urgency `{classification.get('urgency')}`. Proceeding to Step 2."
            )

    st.markdown("<div style='text-align:center;font-size:1.5rem'>↓</div>",
                unsafe_allow_html=True)

    # ── STEP 2 — Draft ───────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 2 — ✍️ Draft Reply")
        st.caption("LLM receives complaint + classification from Step 1 and drafts a reply.")
        col_in, col_arrow, col_out = st.columns([5, 1, 5])
        with col_in:
            st.markdown("**Input (from Step 1 + original complaint):**")
            st.info(f"Category: `{classification['category']}`  |  "
                    f"Urgency: `{classification['urgency']}`\n\n"
                    f"Summary: {classification.get('summary', '')}")
        with col_arrow:
            st.markdown("<div style='text-align:center;font-size:2rem;margin-top:1.5rem'>→</div>",
                        unsafe_allow_html=True)
        with col_out:
            with st.spinner("Drafting reply…"):
                draft = step2_draft(complaint, classification)
            st.markdown("**Output (feeds Step 3):**")
            st.warning(draft)

    st.markdown("<div style='text-align:center;font-size:1.5rem'>↓</div>",
                unsafe_allow_html=True)

    # ── STEP 3 — Polish ──────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 3 — ✨ Polish")
        st.caption("LLM receives the draft from Step 2 and produces a professional final email.")
        col_in, col_arrow, col_out = st.columns([5, 1, 5])
        with col_in:
            st.markdown("**Input (from Step 2):**")
            st.warning(draft[:300] + ("…" if len(draft) > 300 else ""))
        with col_arrow:
            st.markdown("<div style='text-align:center;font-size:2rem;margin-top:1.5rem'>→</div>",
                        unsafe_allow_html=True)
        with col_out:
            with st.spinner("Polishing…"):
                final_email = step3_polish(draft, classification)
            st.markdown("**Output — Final Email ✅**")
            st.success(final_email)

    # ── Chain summary ─────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 What just happened — chain summary"):
        st.markdown(f"""
| Step | LLM call | Input | Output |
|---|---|---|---|
| **1 — Classify** | `generate_content` | Raw complaint | `{{"category": "{classification.get('category')}", "urgency": "{classification.get('urgency')}"}}` |
| **Gate** | *(no LLM)* | Classification JSON | Pass ✓ or Stop ✗ |
| **2 — Draft** | `generate_content` | Complaint + classification | Draft reply |
| **3 — Polish** | `generate_content` | Draft reply | Final email |

**Total LLM calls: 3** — each focused on one task.

**Key insight:** Each step's output is the next step's input.
Your code wired this sequence — the LLMs only processed their own step.
This is fundamentally different from 1d where the model decided the sequence.
""")
    st.toast("✅ Chain complete — 3 LLM calls", icon="🔗")

    st.markdown("---")
    st.markdown("### What's next → Phase 2b: Routing")
    st.markdown(
        "Same idea but instead of chaining steps, we **classify first then route** "
        "to a specialist — one branch runs, the others don't."
    )
