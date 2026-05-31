"""
Phase 2e — Evaluator-Optimizer
Generator LLM produces output · Evaluator LLM scores it · loop repeats until threshold.
Demo: Customer support email iteratively improved until quality score >= threshold.
"""

import streamlit as st
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 2e — Evaluator-Optimizer", page_icon="🔄", layout="wide")
st.title("🔄 Phase 2e — Evaluator-Optimizer")
st.caption("Workflow Pattern 5 of 5 — from *Building Effective Agents*, Anthropic Engineering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_2e
st.image(diagram_2e(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Evaluator-Optimizer — and why is it the bridge to Agents?"):
    st.markdown("""
    > *"In the evaluator-optimizer workflow, one LLM call generates a response while
    > another provides evaluation and feedback in a loop."*
    > — Anthropic, Building Effective Agents

    **What's new vs the other workflow patterns:**

    | Feature | 2a–2d | 2e Evaluator-Optimizer |
    |---|---|---|
    | Fixed structure | ✅ Always same steps | ✅ Still fixed loop structure |
    | Output feeds back in | ❌ No | ✅ **Yes — first feedback loop** |
    | Number of steps | Fixed | Variable (until threshold) |

    **Why it is the bridge to Agents:**
    For the first time, a previous result (the evaluation) changes what happens next.
    The generator sees the evaluator's feedback and adapts.
    This **feedback loop** is the core mechanism that makes agents possible.

    **Why it is STILL NOT an Agent:**
    The loop structure is hardcoded by you. The model cannot decide to try a completely
    different strategy, add new tools, or exit the loop differently.
    A true agent would observe a low score and might decide to ask a clarifying question,
    search for more information, or restructure the approach entirely.

    **Scoring criteria (what the Evaluator checks):**
    - **Empathy** — does it acknowledge the customer's feelings?
    - **Accuracy** — does it address the specific complaint?
    - **Clarity** — is it professional and well-written?
    - **Actionability** — does it give clear next steps?
    """)

st.markdown("---")

# ── Generator + Evaluator functions ───────────────────────────────────────────

def generate(complaint: str, previous: str | None = None,
             feedback: str | None = None) -> str:
    """Generator LLM — writes or refines the response."""
    if previous and feedback:
        prompt = f"""You are improving a customer support email based on evaluator feedback.

Previous draft:
\"\"\"{previous}\"\"\"

Evaluator feedback to address:
{feedback}

Customer complaint:
\"\"\"{complaint}\"\"\"

Write an improved version that specifically addresses the feedback above:"""
    else:
        prompt = f"""Write a professional customer support email response.

Customer complaint:
\"\"\"{complaint}\"\"\"

Response (be empathetic, specific, and include clear next steps):"""

    response = _call(client.models.generate_content, model=MODEL, contents=prompt)
    return response.text.strip()


def evaluate(complaint: str, response_text: str) -> dict:
    """Evaluator LLM — scores the draft on 4 criteria."""
    prompt = f"""You are a quality evaluator for customer support emails.
Score this response on each criterion from 1 (poor) to 10 (excellent).

Criteria:
- empathy       : acknowledges the customer's feelings and situation
- accuracy      : directly addresses the specific complaint
- clarity       : professional, clear, well-structured
- actionability : provides specific, concrete next steps

Compute overall as the average of all four scores.

Return only valid JSON:
{{
  "empathy": N,
  "accuracy": N,
  "clarity": N,
  "actionability": N,
  "overall": N.N,
  "feedback": "2-3 specific improvements needed (or 'Excellent — no improvements needed' if score >= 8)"
}}

Customer complaint:
\"\"\"{complaint}\"\"\"

Response to evaluate:
\"\"\"{response_text}\"\"\"
"""
    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        data = json.loads(response.text)
        # Safety: ensure overall is computed correctly
        criteria = ["empathy", "accuracy", "clarity", "actionability"]
        scores = [float(data.get(c, 5)) for c in criteria]
        data["overall"] = round(sum(scores) / len(scores), 1)
        return data
    except Exception:
        return {"empathy": 5, "accuracy": 5, "clarity": 5, "actionability": 5,
                "overall": 5.0, "feedback": "Could not parse evaluation."}


# ── Examples ───────────────────────────────────────────────────────────────────

EXAMPLES = {
    "Billing dispute":    "I was charged $49.99 on March 3rd but cancelled my subscription on February 28th. I have the cancellation email. I want a full refund and an explanation of why I was charged after cancelling.",
    "Technical crisis":   "Your app crashed 3 times this week during important work. I've lost data twice. This is unacceptable — I pay for a premium plan and expect reliability. Nothing I've tried has fixed it.",
    "Poor experience":    "I've contacted support 4 times about the same issue and each agent tells me something different. Nobody follows up. I'm completely frustrated and considering cancelling after 3 years as a customer.",
}

# ── UI ─────────────────────────────────────────────────────────────────────────

col_l, col_r = st.columns([3, 1])

with col_r:
    st.markdown("**Quick examples:**")
    if "sel_2e" not in st.session_state:
        st.session_state.sel_2e = EXAMPLES["Billing dispute"]
    for label, text in EXAMPLES.items():
        if st.button(label, key=f"ex2e_{label}"):
            st.session_state.sel_2e = text
            st.rerun()

    st.markdown("---")
    threshold = st.slider("Quality threshold (stop when ≥):",
                          min_value=5.0, max_value=9.5, value=7.5,
                          step=0.5, key="threshold_2e")
    max_iter  = st.slider("Max iterations:",
                          min_value=2, max_value=6, value=4,
                          key="maxiter_2e")

with col_l:
    complaint = st.text_area(
        "Customer complaint:",
        value=st.session_state.sel_2e,
        height=120,
    )

st.markdown("---")

if st.button("▶  Run Evaluator-Optimizer Loop", type="primary", key="run_2e"):

    if not complaint.strip():
        st.warning("Please enter a complaint.")
        st.stop()

    history   = []   # {iteration, draft, scores, feedback, overall}
    draft     = None
    feedback  = None

    progress  = st.progress(0, text="Starting loop…")
    loop_area = st.container()

    t_total = time.time()

    for i in range(max_iter):
        progress.progress((i + 1) / max_iter,
                          text=f"Iteration {i+1}/{max_iter} — generating…")

        # ── Generate ──────────────────────────────────────────────────────────
        t0 = time.time()
        with st.spinner(f"Iteration {i+1} — Generator writing…"):
            draft = generate(complaint, draft, feedback)

        # ── Evaluate ──────────────────────────────────────────────────────────
        with st.spinner(f"Iteration {i+1} — Evaluator scoring…"):
            scores = evaluate(complaint, draft)

        elapsed = time.time() - t0
        history.append({
            "iteration": i + 1,
            "draft":     draft,
            "scores":    scores,
            "elapsed":   elapsed,
        })

        overall  = scores["overall"]
        feedback = scores["feedback"]

        # ── Show this iteration inline ─────────────────────────────────────────
        with loop_area:
            status = "✅ THRESHOLD MET" if overall >= threshold else f"↺ needs improvement (threshold: {threshold})"
            color  = "success" if overall >= threshold else "warning"
            with st.expander(
                f"**Iteration {i+1}** — Score: {overall}/10  |  {status}",
                expanded=(i == 0),
            ):
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown("**Draft:**")
                    if color == "success":
                        st.success(draft)
                    else:
                        st.warning(draft)
                with c2:
                    st.markdown("**Scores:**")
                    score_cols = st.columns(2)
                    criteria = ["empathy", "accuracy", "clarity", "actionability"]
                    for j, crit in enumerate(criteria):
                        score_cols[j % 2].metric(
                            crit.capitalize(), f"{scores.get(crit, '?')}/10"
                        )
                    st.metric("**Overall**", f"{overall}/10")
                    if overall < threshold:
                        st.markdown(f"**Feedback → Generator:**\n\n_{feedback}_")

        if overall >= threshold:
            progress.progress(1.0, text=f"✅ Quality threshold {threshold} reached at iteration {i+1}!")
            break

    else:
        progress.progress(1.0, text=f"⚠ Max iterations ({max_iter}) reached.")

    total_time = time.time() - t_total

    # ── Score chart ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 Score Progression Across Iterations")

    chart_data = {
        "Iteration": [h["iteration"] for h in history],
        "Overall":   [h["scores"]["overall"] for h in history],
        "Empathy":   [h["scores"]["empathy"] for h in history],
        "Accuracy":  [h["scores"]["accuracy"] for h in history],
        "Clarity":   [h["scores"]["clarity"] for h in history],
        "Actionability": [h["scores"]["actionability"] for h in history],
    }

    import pandas as pd
    df = pd.DataFrame(chart_data).set_index("Iteration")
    st.line_chart(df, height=250)

    # Threshold reference line note
    st.caption(f"Threshold line: {threshold}  |  "
               f"Loop ran {len(history)} iteration(s)  |  "
               f"Total time: {total_time:.1f}s")

    # ── First vs final ─────────────────────────────────────────────────────────
    st.markdown("### 🔍 First Draft vs Final Draft")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(f"**Iteration 1** — Score: {history[0]['scores']['overall']}/10")
        st.warning(history[0]["draft"])
    with fc2:
        st.markdown(f"**Iteration {len(history)}** — Score: {history[-1]['scores']['overall']}/10")
        st.success(history[-1]["draft"])

    # ── Summary ────────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 What just happened — and what changes in Phase 3"):
        score_gain = history[-1]["scores"]["overall"] - history[0]["scores"]["overall"]
        st.markdown(f"""
| Iteration | Overall Score | Change |
|---|---|---|
""" + "\n".join(
    f"| {h['iteration']} | {h['scores']['overall']}/10 | "
    f"{'▲ +' if h['iteration']>1 and h['scores']['overall'] > history[h['iteration']-2]['scores']['overall'] else '▼ ' if h['iteration']>1 else '—'}"
    f"{abs(h['scores']['overall'] - history[h['iteration']-2]['scores']['overall']) if h['iteration']>1 else ''} |"
    for h in history) + f"""

**Score improvement:** +{score_gain:.1f} over {len(history)} iterations.

**What this pattern adds over 2d:**
The evaluator's feedback directly influences the generator's next output.
For the first time, a previous result changes what the model does next.
This is the **feedback loop** concept.

**What's still missing for a true Agent:**
The loop structure is your code. The model cannot decide to:
- Ask a clarifying question before generating
- Search for relevant policies before drafting
- Completely change strategy if quality stays low
- Stop early if it recognises the complaint is unclear

Phase 3 gives the model those freedoms.
""")

    st.markdown("---")
    st.markdown("### 🎉 Phase 2 Complete — All 5 Workflow Patterns Done!")
    st.info(
        "You've now seen every workflow pattern. The key distinction from Phase 3: "
        "in ALL of Phase 2, the overall structure was defined by YOUR code. "
        "In Phase 3 (Agents), the model defines its own structure at runtime."
    )
    st.markdown("### What's next → Phase 3a: ReAct Agent")
    st.markdown(
        "The model gets a goal, a set of tools, and **no predefined structure**. "
        "It decides what to do, does it, observes, and decides again — until it "
        "concludes the goal is met. That self-directed loop is an Agent."
    )
