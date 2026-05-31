"""
Phase 2b — Routing
Classify input first, then route to exactly ONE specialist handler.
Demo: Customer message → Router → Billing / Technical / General / Spam-stop
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

st.set_page_config(page_title="Phase 2b — Routing", page_icon="🔀", layout="wide")
st.title("🔀 Phase 2b — Routing")
st.caption("Workflow Pattern 2 of 5 — from *Building Effective Agents*, Anthropic Engineering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_2b
st.image(diagram_2b(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Routing — and how is it different from Chaining?"):
    st.markdown("""
    > *"Routing classifies an input and directs it to a specialized followup task.
    > This allows for separation of concerns and building more specialised prompts."*
    > — Anthropic, Building Effective Agents

    **Key difference from 2a (Chaining):**

    | | 2a Chaining | 2b Routing |
    |---|---|---|
    | Steps that run | **ALL** steps, every time | **ONE** branch, chosen by router |
    | Flow shape | Linear sequence | Fan-out then single branch |
    | LLM calls | Fixed number (e.g. always 3) | Variable (1 router + 1 specialist) |
    | Use case | Transform task step-by-step | Handle different input types differently |

    **Why routing matters:**
    - A billing specialist can be optimised for payment terminology
    - A technical specialist can know your product's error codes
    - Unused specialists cost zero tokens

    **Why it is NOT an Agent:**
    Your code defines all possible routes. The router LLM only classifies —
    it never invents a new route or decides to loop back.
    """)

st.markdown("---")

# ── Specialists ────────────────────────────────────────────────────────────────

SPECIALISTS = {
    "billing": {
        "icon": "💳",
        "label": "Billing Specialist",
        "color": "orange",
        "system": (
            "You are a billing support specialist. You handle payment issues, "
            "refunds, subscription changes, and invoice queries. "
            "Be precise about amounts and timelines. "
            "Always acknowledge the financial inconvenience and provide clear next steps. "
            "Keep replies under 120 words."
        ),
    },
    "technical": {
        "icon": "🔧",
        "label": "Technical Specialist",
        "color": "blue",
        "system": (
            "You are a technical support specialist. You troubleshoot app issues, "
            "bugs, connectivity problems, and performance concerns. "
            "Be empathetic — technical issues are frustrating. "
            "Give numbered troubleshooting steps when possible. "
            "Keep replies under 120 words."
        ),
    },
    "general": {
        "icon": "💬",
        "label": "General Support Specialist",
        "color": "green",
        "system": (
            "You are a friendly general support agent. You handle feedback, "
            "feature requests, account questions, and general enquiries. "
            "Be warm and helpful. "
            "Keep replies under 100 words."
        ),
    },
}

EXAMPLES = {
    "Billing":   "I was charged $49.99 on the 3rd but my plan is only $29.99. Please explain the extra charge and issue a refund if it was a mistake.",
    "Technical": "The app crashes immediately when I tap the upload button. I've tried reinstalling twice. My phone is iPhone 14 running iOS 17.",
    "General":   "I love the product! Just wondering if you have plans to add keyboard shortcuts? It would really speed up my workflow.",
    "Spam (route stop)": "CLICK HERE FOR FREE MONEY!! LIMITED TIME OFFER!! WORK FROM HOME EARN $5000/DAY!!",
}

# ── Router function ────────────────────────────────────────────────────────────

def route(message: str) -> dict:
    """Call the Router LLM — classify and choose a specialist."""
    prompt = f"""You are a customer support router. Classify this message.

Routes available:
- billing    : payment, charge, refund, invoice, subscription, price
- technical  : bug, crash, error, app, login, slow, broken, not working
- general    : feedback, question, feature request, compliment, other
- spam       : advertisement, gibberish, not a genuine customer message

Reply with valid JSON only (no markdown):
{{"route": "...", "confidence": "high|medium|low", "reason": "one phrase"}}

Message: {message}"""

    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"route": "general", "confidence": "low", "reason": "parse error"}


def handle(message: str, route_key: str) -> str:
    """Call the specialist LLM for the chosen route."""
    spec = SPECIALISTS[route_key]
    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=f"Customer message:\n\"{message}\"\n\nPlease respond:",
        config=types.GenerateContentConfig(system_instruction=spec["system"]),
    )
    return response.text.strip()


# ── UI ─────────────────────────────────────────────────────────────────────────

if "sel_2b" not in st.session_state:
    st.session_state.sel_2b = EXAMPLES["Billing"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Quick examples:**")
    for label, text in EXAMPLES.items():
        if st.button(label, key=f"ex2b_{label}"):
            st.session_state.sel_2b = text
            st.rerun()
with col1:
    message = st.text_area(
        "Customer message:",
        value=st.session_state.sel_2b,
        height=100,
    )

st.markdown("---")

if st.button("▶  Run Router", type="primary", key="run_2b"):

    if not message.strip():
        st.warning("Please enter a message.")
        st.stop()

    # ── STEP 1 — Route ────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 1 — 🗺️ Router LLM: Classify & Choose Branch")
        st.caption("One LLM call. Output is a route key — NOT the final answer.")

        with st.spinner("Router classifying…"):
            routing = route(message)

        chosen = routing.get("route", "general")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Input:**")
            st.info(message[:200] + ("…" if len(message) > 200 else ""))
        with col_r2:
            st.markdown("**Router output:**")
            st.json(routing)

    # ── ROUTE DISPLAY — show all branches, highlight chosen ───────────────────
    st.markdown("#### Which branch runs?")

    all_routes = list(SPECIALISTS.keys()) + ["spam"]
    cols = st.columns(len(all_routes))

    for col, route_key in zip(cols, all_routes):
        with col:
            if route_key == chosen:
                if route_key == "spam":
                    st.error("🚫 **SPAM**\nChain stops here.\nNo specialist called.")
                else:
                    spec = SPECIALISTS[route_key]
                    st.success(
                        f"{spec['icon']} **{spec['label']}**\n\n✅ THIS branch runs"
                    )
            else:
                label = SPECIALISTS[route_key]["label"] if route_key in SPECIALISTS else "Spam / Stop"
                st.markdown(
                    f"<div style='background:#F0F2F6;padding:10px;border-radius:8px;"
                    f"color:#AAB7B8;text-align:center;font-size:0.85rem'>"
                    f"{'💳' if route_key=='billing' else '🔧' if route_key=='technical' else '💬' if route_key=='general' else '🚫'} "
                    f"{label}<br><b>✗ not chosen</b></div>",
                    unsafe_allow_html=True,
                )

    # ── SPAM GATE ─────────────────────────────────────────────────────────────
    if chosen == "spam":
        st.markdown("---")
        st.error(
            "**Route = spam — pipeline stopped.**\n\n"
            "No specialist LLM was called. Zero additional tokens spent.\n\n"
            "This is routing's cost advantage: unused branches are free."
        )
        st.stop()

    st.markdown("---")

    # ── STEP 2 — Specialist ───────────────────────────────────────────────────
    spec = SPECIALISTS[chosen]
    with st.container(border=True):
        st.markdown(f"#### Step 2 — {spec['icon']} {spec['label']} responds")
        st.caption(
            f"This specialist has a tailored system prompt for **{chosen}** issues. "
            "The other specialists were never called."
        )

        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.markdown("**Specialist system prompt (excerpt):**")
            st.code(spec["system"][:180] + "…", language="text")
        with col_s2:
            with st.spinner(f"Calling {spec['label']}…"):
                reply = handle(message, chosen)
            st.markdown("**Response:**")
            st.success(reply)

    # ── Summary ───────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 What just happened — routing summary"):
        st.markdown(f"""
| Step | LLM call | Output |
|---|---|---|
| **Router** | `generate_content` | `{{"route": "{chosen}", "confidence": "{routing.get('confidence')}"}}` |
| **{spec['label']}** | `generate_content` | Final customer reply |
| Billing specialist | *(not called)* | — |
| Technical specialist | *(not called)* | — |
| General specialist | *(not called)* | — |

**Total LLM calls: 2** — Router + 1 specialist. The other 2 specialists were never invoked.

**Key insight:** The router's only job is classification — a focused, reliable task.
The specialist's only job is responding — tuned perfectly for one type of issue.
Separation of concerns makes each LLM call simpler and more accurate.
""")

    st.markdown("---")
    st.markdown("### What's next → Phase 2c: Parallelization")
    st.markdown(
        "Instead of routing to ONE branch, we'll run **multiple branches simultaneously** "
        "and either merge results or take a majority vote."
    )
