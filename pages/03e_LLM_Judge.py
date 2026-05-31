"""
Phase 4c — LLM-as-Judge
An independent LLM evaluates the agent's response quality.
Verdict: PASS (deliver) | REVIEW (escalate to HITL) | FAIL (retry/fallback)
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

st.set_page_config(page_title="Phase 4c — LLM-as-Judge", page_icon="⚖️", layout="wide")
st.title("⚖️ Phase 4c — LLM-as-Judge")
st.caption("Independent quality evaluation — Judge scores the agent's response and routes it")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_3e
st.image(diagram_3e(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is LLM-as-Judge — and how is it different from 2e and 3b?"):
    st.markdown("""
    **Three patterns that evaluate responses — all different:**

    | Pattern | Phase | How it works | Purpose |
    |---|---|---|---|
    | **Guardrails** | 3b | Regex + LLM classifier | Safety: block unsafe input/output |
    | **Evaluator-Optimizer** | 2e | Generator + Evaluator in a loop | Quality: improve until threshold |
    | **LLM-as-Judge** | 3e | Independent Judge, single evaluation | Quality gate: PASS / REVIEW / FAIL |

    **What makes 3e unique:**
    - Judge runs **after** the agent, not inside a loop
    - Judge has **independent context** — it cannot be influenced by the agent's reasoning
    - Judge routes the response: deliver · escalate to human · trigger retry
    - Used for **systematic quality assurance** — every response evaluated, not just suspicious ones

    **Four evaluation criteria:**
    - **Accuracy** — factually correct, no hallucinations
    - **Groundedness** — response uses retrieved context (not training-data guesses)
    - **Tone** — appropriate, professional, empathetic
    - **Completeness** — all parts of the question answered

    **Three verdicts:**
    - ✅ **PASS** (score ≥ 7.0) → deliver to user
    - 🟡 **REVIEW** (score 5–6.9) → escalate to human (connects to Phase 4b HITL)
    - ❌ **FAIL** (score < 5) → retry with different prompt / fallback response

    **Why "independent"?**
    The Judge receives only the question and the response — not the agent's chain-of-thought,
    tool call history, or retrieved documents (unless you choose to include them for
    groundedness checking). This independence is intentional — the Judge cannot be misled
    by clever agent reasoning.
    """)

with st.expander("📐 Core Code Pattern — LLM-as-Judge"):
    st.code('''
# ── AGENT generates a response ────────────────────────────────────────────────
agent_response = run_agent(question)

# ── JUDGE evaluates independently ────────────────────────────────────────────
# Judge gets: question + response (+ optional context for groundedness)
# Judge does NOT get: agent reasoning, tool call history, chain of thought
verdict = judge_llm(
    question=question,
    response=agent_response,
    context=retrieved_chunks,   # optional — for groundedness check
)
# verdict = {
#   "accuracy": 8, "groundedness": 9, "tone": 7, "completeness": 6,
#   "overall": 7.5, "verdict": "PASS",
#   "issues": [], "feedback": "Good response, missing refund timeline"
# }

# ── ROUTING based on verdict ──────────────────────────────────────────────────
if verdict["verdict"] == "PASS":
    deliver_to_user(agent_response)

elif verdict["verdict"] == "REVIEW":
    send_to_hitl(                           # Phase 4b checkpoint
        response=agent_response,
        judge_feedback=verdict["feedback"],
        score=verdict["overall"],
    )

else:  # FAIL
    fallback = generate_safe_fallback(question)
    deliver_to_user(fallback)
    log_failure(question, agent_response, verdict)
''', language="python")
    st.markdown("""
**Key implementation principle — Judge independence:**
The Judge LLM runs in a completely separate `generate_content` call with its own
system prompt. It has NO access to the agent's internal reasoning.
This prevents "judge-washing" — where the agent's verbose reasoning misleads the judge.

**Connecting to Phase 4b (HITL):**
The REVIEW verdict is the bridge between automated quality checks and human oversight.
Low-confidence responses automatically enter the human review queue.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Agent + Judge functions
# ══════════════════════════════════════════════════════════════════════════════

_AGENT_SYS = (
    "You are NexaBank's customer service AI. "
    "Answer customer questions professionally and empathetically. "
    "Be specific — cite policies, rates, and timelines when you know them. "
    "Keep responses under 100 words."
)

_JUDGE_SYS = (
    "You are an expert quality judge for a banking AI assistant. "
    "Evaluate responses objectively on four criteria. Return only valid JSON."
)


def run_banking_agent(question: str, context: str = "") -> tuple:
    """Returns (response_text, trace_dict)."""
    ctx_section = f"\n\nRelevant policy context:\n{context}" if context else ""
    user_msg = f"Customer question: {question}{ctx_section}"
    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=user_msg,
        config=types.GenerateContentConfig(system_instruction=_AGENT_SYS),
    )
    return response.text.strip(), {"system": _AGENT_SYS, "user": user_msg}


def judge(question: str, response: str, context: str = "") -> tuple:
    """
    LLM-as-Judge — independent quality evaluation.
    Returns (verdict_dict, prompt_string, raw_json_string).
    """
    ctx_note = (
        f"\n\nContext that was available to the agent:\n{context[:400]}"
        if context else "\n\nNo context was provided to the agent."
    )

    prompt = f"""You are an expert quality judge for a banking AI assistant.
Evaluate the response below on four criteria, each scored 1-10.

Criteria:
- accuracy      : factually correct, no hallucinations, specific figures cited correctly
- groundedness  : uses the provided context (if any), does not invent policies/rates
- tone          : professional, empathetic, appropriate for banking, not dismissive
- completeness  : addresses ALL parts of the question, no missing information

Scoring guide: 9-10 = excellent, 7-8 = good, 5-6 = needs work, 1-4 = poor/wrong

Verdict rules:
- PASS   if overall >= 7.0
- REVIEW if overall >= 5.0 and < 7.0
- FAIL   if overall < 5.0

Return ONLY valid JSON:
{{
  "accuracy": N, "groundedness": N, "tone": N, "completeness": N,
  "overall": N.N,
  "verdict": "PASS|REVIEW|FAIL",
  "issues": ["specific issue 1", "specific issue 2"],
  "feedback": "1-2 sentence summary of main strengths and weaknesses",
  "suggested_improvement": "one specific change that would most improve the response"
}}

Customer question: {question}{ctx_note}

Agent response to evaluate:
\"\"\"{response}\"\"\"
"""
    raw_json = ""
    try:
        result = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        raw_json = result.text
        data = json.loads(raw_json)
        criteria = ["accuracy", "groundedness", "tone", "completeness"]
        scores = [float(data.get(c, 5)) for c in criteria]
        data["overall"] = round(sum(scores) / len(scores), 1)
        if data["overall"] >= 7.0:
            data["verdict"] = "PASS"
        elif data["overall"] >= 5.0:
            data["verdict"] = "REVIEW"
        else:
            data["verdict"] = "FAIL"
        return data, prompt, raw_json
    except Exception as e:
        return (
            {
                "accuracy": 5, "groundedness": 5, "tone": 5, "completeness": 5,
                "overall": 5.0, "verdict": "REVIEW",
                "issues": [f"Judge error: {e}"],
                "feedback": "Could not evaluate.", "suggested_improvement": "Retry.",
            },
            prompt,
            raw_json,
        )

# ══════════════════════════════════════════════════════════════════════════════
# Test scenarios — designed to produce different verdicts
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS = {
    "✅ Good question (expect PASS)":
        "I want to open a savings account. What interest rate do you offer and are there any restrictions?",

    "⚠️ Multi-part question (expect REVIEW — completeness risk)":
        "I need to: (1) check my overdraft limit, (2) understand the interest charges, and (3) know how to increase my limit. Can you help with all three?",

    "❌ Ambiguous question (expect FAIL — accuracy risk)":
        "What's the best account for someone like me? I earn about £45k, have £10k savings, and might buy a house next year.",

    "✅ Complaint (tests tone)":
        "I've been waiting 2 weeks for my refund and nobody is helping me. This is absolutely terrible service.",

    "🔍 Policy question with context (tests groundedness)":
        "How long does a refund take and what's the maximum amount without manager approval?",
}

# Optional context (from the knowledge base — simulates RAG feeding the judge)
POLICY_CONTEXT = (
    "NexaBank Refund Policy: Customers may request a full refund within 30 days. "
    "Refunds up to £500 processed automatically in 3-5 working days. "
    "Refunds above £500 require manager approval and take 5-10 working days."
)

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

if "sel_3e" not in st.session_state:
    st.session_state.sel_3e = SCENARIOS["✅ Good question (expect PASS)"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Scenarios (designed for different verdicts):**")
    for label, text in SCENARIOS.items():
        if st.button(label, key=f"ex3e_{label}"):
            st.session_state.sel_3e = text
            st.rerun()
    st.markdown("---")
    use_context = st.checkbox(
        "Provide policy context to judge\n(enables groundedness check)",
        value=True,
    )
    pass_threshold = st.slider("PASS threshold:", 5.0, 9.0, 7.0, 0.5, key="thresh_3e")

with col1:
    question = st.text_area(
        "Customer question:",
        value=st.session_state.sel_3e,
        height=100,
    )

st.markdown("---")

if st.button("▶  Run Agent + Judge", type="primary", key="run_3e"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    context = POLICY_CONTEXT if use_context else ""

    # ── Step 1: Agent answers ─────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### 🤖 Step 1 — Agent Response")
        st.caption("Agent answers the question (with optional policy context injected)")
        with st.spinner("Agent generating response…"):
            agent_resp, agent_trace = run_banking_agent(question, context)
        st.info(agent_resp)

    st.markdown(
        "<div style='text-align:center;font-size:1.2rem'>↓ independent Judge evaluates</div>",
        unsafe_allow_html=True,
    )

    # ── Step 2: Judge evaluates ───────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### ⚖️ Step 2 — Judge Evaluation")
        st.caption(
            "Judge receives question + response (+ context if enabled). "
            "No access to agent's reasoning."
        )
        with st.spinner("Judge LLM evaluating independently…"):
            verdict, judge_prompt, judge_raw_json = judge(question, agent_resp, context)

        # Score cards
        criteria = ["accuracy", "groundedness", "tone", "completeness"]
        c1, c2, c3, c4, c5 = st.columns(5)
        cols = [c1, c2, c3, c4]
        for col, crit in zip(cols, criteria):
            score = verdict.get(crit, 0)
            delta_color = "normal" if score >= 7 else ("off" if score >= 5 else "inverse")
            col.metric(crit.capitalize(), f"{score}/10",
                       delta="✓" if score >= 7 else ("~" if score >= 5 else "✗"),
                       delta_color=delta_color)
        c5.metric("**Overall**", f"{verdict['overall']}/10")

        # Issues
        if verdict.get("issues"):
            for issue in verdict["issues"]:
                st.warning(f"⚠️  {issue}")

        # Feedback
        st.markdown(f"**Judge feedback:** {verdict.get('feedback', '')}")
        if verdict.get("suggested_improvement"):
            st.caption(f"💡 Suggested improvement: {verdict['suggested_improvement']}")

    st.markdown(
        "<div style='text-align:center;font-size:1.2rem'>↓ verdict routes response</div>",
        unsafe_allow_html=True,
    )

    # ── Step 3: Routing ───────────────────────────────────────────────────────
    v = verdict["verdict"]
    overall = verdict["overall"]

    with st.container(border=True):
        st.markdown("#### 🔀 Step 3 — Routing Decision")

        if v == "PASS":
            st.success(
                f"### ✅ PASS  (score {overall}/10 ≥ threshold {pass_threshold})\n\n"
                "Response delivered to customer."
            )
            st.success(f"**Delivered:**\n\n{agent_resp}")

        elif v == "REVIEW":
            st.warning(
                f"### 🟡 REVIEW  (score {overall}/10 — needs human check)\n\n"
                "Response sent to HITL queue. Reviewer sees agent response + judge feedback."
            )
            with st.container(border=True):
                st.markdown("**HITL reviewer sees:**")
                st.markdown(f"- Agent response: _{agent_resp[:120]}…_")
                st.markdown(f"- Judge score: **{overall}/10**")
                st.markdown(f"- Issues: {', '.join(verdict.get('issues', ['none']))}")
                st.markdown(f"- Suggested fix: _{verdict.get('suggested_improvement', '')}_")
            st.caption("→ Connects to Phase 4b HITL — reviewer approves/modifies before delivery")

        else:  # FAIL
            st.error(
                f"### ❌ FAIL  (score {overall}/10 < 5.0)\n\n"
                "Agent response too poor to deliver. Safe fallback sent instead."
            )
            fallback = (
                "Thank you for your question. I want to make sure I give you accurate information. "
                "Please call us on 0800 123 4567 or use our secure chat for a specialist response."
            )
            st.warning(f"**Fallback sent to customer:**\n\n{fallback}")
            with st.expander("🔍 What the agent actually said (not delivered)"):
                st.error(agent_resp)

    # ── Summary ───────────────────────────────────────────────────────────────
    with st.expander("🔍 LLM-as-Judge summary — what ran and why"):
        criteria_vals = [verdict['accuracy'], verdict['groundedness'], verdict['tone'], verdict['completeness']]
        st.markdown(f"""
| Step | Who | What happened this run |
|---|---|---|
| **Agent** | Banking agent LLM | Answered: *"{agent_resp[:80]}..."* |
| **Judge** | Independent Judge LLM | Scored: Accuracy {verdict['accuracy']} · Groundedness {verdict['groundedness']} · Tone {verdict['tone']} · Completeness {verdict['completeness']} |
| **Score math** | Python | ({' + '.join(str(s) for s in criteria_vals)}) / 4 = **{verdict['overall']}** |
| **Routing** | Threshold logic | {verdict['overall']} {'≥' if verdict['overall'] >= 7.0 else '<'} 7.0 → **{v}** |

**Why independence matters:**
The Judge had no access to the agent's reasoning. If the agent produces a confident-sounding
but incorrect answer, the Judge evaluates only the output — exactly as the customer will see it.

**Connection to other phases:**
- 4a Guardrails: catches *unsafe* content → **block**
- 4c LLM-as-Judge: catches *poor quality* content → **route**
- 4b HITL: human decides on *ambiguous* cases → **approve/reject/modify**
Together these three form a complete response quality pipeline.
""")

    # ── Execution Trace ────────────────────────────────────────────────────────
    with st.expander("🔬 Execution Trace — exact prompts, raw responses, decision logic"):
        t_agent, t_judge, t_score = st.tabs(["① Agent LLM", "② Judge LLM", "③ Score + Routing"])

        with t_agent:
            st.markdown("**System prompt sent to the agent:**")
            st.code(agent_trace["system"], language="text")
            st.markdown("**User message sent to the agent** (includes injected context if enabled):**")
            st.code(agent_trace["user"], language="text")
            st.markdown("**Agent raw response** (what the judge receives):**")
            st.code(agent_resp, language="text")

        with t_judge:
            st.markdown("**Full judge prompt** (question + agent response + optional context — no agent reasoning):**")
            st.code(judge_prompt, language="text")
            st.markdown("**Judge raw JSON response** (before any post-processing):**")
            if judge_raw_json:
                st.code(judge_raw_json, language="json")
            else:
                st.warning("Raw JSON not captured (parse error occurred).")

        with t_score:
            a, g, t_v, c_v = verdict['accuracy'], verdict['groundedness'], verdict['tone'], verdict['completeness']
            computed = round((a + g + t_v + c_v) / 4, 1)
            st.markdown("**Score computation — how overall is calculated:**")
            st.code(
                f"accuracy={a} + groundedness={g} + tone={t_v} + completeness={c_v}\n"
                f"= {a + g + t_v + c_v} / 4\n"
                f"= {computed}  (overall)",
                language="text",
            )
            st.markdown("**Routing decision — threshold checks with real values:**")
            st.code(
                f"overall = {verdict['overall']}\n\n"
                f"if overall >= 7.0:   # {verdict['overall']} >= 7.0 → {verdict['overall'] >= 7.0}\n"
                f"    verdict = 'PASS'\n"
                f"elif overall >= 5.0: # {verdict['overall']} >= 5.0 → {verdict['overall'] >= 5.0}\n"
                f"    verdict = 'REVIEW'\n"
                f"else:                # overall < 5.0  → {verdict['overall'] < 5.0}\n"
                f"    verdict = 'FAIL'\n\n"
                f"# Result: verdict = '{v}'",
                language="python",
            )
            st.markdown("**Issues flagged by judge:**")
            for issue in verdict.get("issues", []):
                st.markdown(f"- {issue}")
            if verdict.get("suggested_improvement"):
                st.info(f"Suggested improvement: {verdict['suggested_improvement']}")

    st.markdown("---")
    st.markdown("### What's next → Phase 3b: Reflection Agent")
    st.markdown(
        "Andrew Ng's core pattern 1: the agent reviews its **own** output and decides "
        "whether to try again — no separate judge, no external evaluator. "
        "One model, self-directed improvement loop."
    )
