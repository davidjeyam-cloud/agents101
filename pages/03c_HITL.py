"""
Phase 4b — Human-in-the-Loop (HITL)
Agent pauses at risk checkpoints and waits for human approval before proceeding.
Scenario: Banking agent processing customer requests with checkpoint rules.
"""

import streamlit as st
import os
import json
import uuid
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 4b — Human-in-the-Loop", page_icon="👤", layout="wide")
st.title("👤 Phase 4b — Human-in-the-Loop (HITL)")
st.caption("Agent pauses at risk checkpoints — human judgment where automation alone isn't enough")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_3c
st.image(diagram_3c(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Human-in-the-Loop — and when must you use it?"):
    st.markdown("""
    > *"For agentic systems, it's important to implement human oversight at appropriate
    > points. Agents should pause and verify with users when actions are irreversible
    > or when uncertainty is high."*
    > — Anthropic, Building Effective Agents

    **Two types of agent decisions:**

    | Decision type | Example | HITL needed? |
    |---|---|---|
    | Low-stakes, reversible | Answer an FAQ | ❌ Auto |
    | Low-stakes, reversible | Check account balance | ❌ Auto |
    | Medium-stakes | £50 refund within policy | ❌ Auto |
    | High-stakes, irreversible | £2,000 refund outside policy | ✅ HITL |
    | High risk | Legal threat detected | ✅ HITL |
    | Uncertain | Agent confidence < 70% | ✅ HITL |
    | Regulatory | Compliance flag raised | ✅ HITL |

    **Three human decisions at a checkpoint:**
    - **Approve** — agent proceeds with its proposed action
    - **Reject** — request stopped, customer informed
    - **Modify** — human edits the agent's draft response before sending

    **Why automation alone isn't enough:**
    Guardrails (3b) catch *bad* inputs/outputs automatically.
    HITL handles *ambiguous* situations where the right answer depends on context
    a human understands better than the model — business relationships, legal nuance, empathy.
    """)

with st.expander("📐 Core Code Pattern — HITL Checkpoint"):
    st.code('''
# ── AGENT ANALYSES AND SELF-ASSESSES ─────────────────────────────────────────
analysis = agent_analyse(request)
# Returns: understanding, proposed_action, proposed_response,
#          confidence, risk_level, checkpoint_triggers, requires_hitl

# ── CHECKPOINT EVALUATION (business rules on top of LLM) ────────────────────
if analysis["confidence"] < 0.70:
    analysis["requires_hitl"] = True          # low confidence → human decides
if analysis["risk_level"] in ("high", "critical"):
    analysis["requires_hitl"] = True          # high risk → human decides

# ── ROUTING ───────────────────────────────────────────────────────────────────
if not analysis["requires_hitl"]:
    send_to_customer(analysis["proposed_response"])  # auto-process

else:
    # ── PAUSE — present to human reviewer ───────────────────────────────────
    # Show: understanding, proposed_action, proposed_response,
    #       risk_level, confidence, factors_for, factors_against
    human_decision = wait_for_human_input()   # Streamlit: session_state

    if human_decision == "approved":
        final = analysis["proposed_response"]

    elif human_decision == "rejected":
        final = generate_rejection(request, human_note)  # new LLM call

    elif human_decision == "modified":
        final = human_edited_text             # human\'s version, verbatim

    send_to_customer(final)
    audit_log(ref=case_ref, decision=human_decision,
              agent_draft=analysis["proposed_response"],
              final_sent=final)               # immutable log — FCA SYSC 9.1
''', language="python")
    st.markdown("""
**Key distinction from Guardrails (3b):**
- **Guardrails:** automatic pass/fail on clear violations — no ambiguity
- **HITL:** human judgment for ambiguous cases — context, relationships, legal nuance

**Three human outcomes wired up:**
- `approved` → send agent's draft as-is
- `rejected` → agent generates a polite rejection (new LLM call with human's reason)
- `modified` → human's edited text sent verbatim — agent not involved

**Why audit logging is mandatory:** In financial services, every HITL decision
(including who made it, what the agent proposed, what was sent) must be retained
for regulatory inspection (FCA SYSC 9.1: 7 years).
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Checkpoint rules — business logic that triggers HITL
# ══════════════════════════════════════════════════════════════════════════════

CHECKPOINT_RULES = {
    "high_value_refund":     ("Refund request exceeds £500 threshold",     "high"),
    "outside_policy":        ("Request falls outside standard policy",      "high"),
    "legal_threat":          ("Customer mentions legal action / regulator", "critical"),
    "repeat_refund":         ("3rd+ refund request in 30 days",            "high"),
    "vulnerable_customer":   ("Potential vulnerable customer indicators",   "medium"),
    "low_confidence":        ("Agent confidence below 70%",                 "medium"),
    "account_closure":       ("Account closure after 5+ years",            "medium"),
    "large_transaction":     ("Transaction > £10,000 (AML threshold)",     "critical"),
}

# ══════════════════════════════════════════════════════════════════════════════
# Agent functions
# ══════════════════════════════════════════════════════════════════════════════

def agent_analyse(request: str) -> dict:
    """Agent analyses the request and provides structured assessment."""
    prompt = f"""You are a banking customer service AI agent for NexaBank UK.
Analyse this customer request carefully.

Bank policies:
- Refunds: allowed within 30 days of purchase, up to £500 without manager approval
- Refunds over £500 OR outside 30 days require human approval
- Account closures after 5+ years require retention specialist review
- Any mention of legal action, FCA, or ombudsman must be escalated
- 3 or more refund requests in 30 days triggers fraud review

Return ONLY valid JSON:
{{
  "understanding": "what the customer is asking for (1-2 sentences)",
  "proposed_action": "approve_refund|reject_refund|answer_query|close_account|escalate|process_payment",
  "proposed_response": "your complete draft response to the customer (professional, empathetic)",
  "confidence": 0.0-1.0,
  "risk_level": "low|medium|high|critical",
  "checkpoint_triggers": ["list any checkpoint rules that apply, empty if none"],
  "relevant_policy": "which policy applies",
  "factors_for": ["up to 3 reasons supporting your proposed action"],
  "factors_against": ["up to 3 concerns or reasons against"],
  "requires_hitl": true/false
}}

Customer request: {request}"""

    try:
        response = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(response.text)
        # Apply hard-coded business rules on top of LLM assessment
        triggers = data.get("checkpoint_triggers", [])
        risk     = data.get("risk_level", "low")
        conf     = data.get("confidence", 1.0)
        if conf < 0.7:
            triggers.append("low_confidence")
        if risk in ("high", "critical"):
            data["requires_hitl"] = True
        if triggers:
            data["requires_hitl"] = True
        data["checkpoint_triggers"] = triggers
        return data
    except Exception as e:
        return {
            "understanding": "Unable to parse request.",
            "proposed_action": "escalate",
            "proposed_response": "I need to escalate this to a specialist.",
            "confidence": 0.5,
            "risk_level": "medium",
            "checkpoint_triggers": ["low_confidence"],
            "relevant_policy": "N/A",
            "factors_for": [],
            "factors_against": [f"Parse error: {e}"],
            "requires_hitl": True,
        }


def agent_continue(request: str, analysis: dict, human_decision: str,
                   human_note: str = "", modified_response: str = "") -> str:
    """Agent generates final response after human decision."""
    if human_decision == "approved":
        return analysis.get("proposed_response", "Your request has been processed.")
    elif human_decision == "modified":
        return modified_response if modified_response else analysis.get("proposed_response", "")
    else:  # rejected
        prompt = f"""You are a NexaBank customer service agent.
The customer's request has been reviewed and cannot be approved at this time.
Reason from reviewer: {human_note or 'Does not meet policy requirements.'}

Write a professional, empathetic rejection message. Offer alternative options where possible.
Keep it under 80 words.

Original request: {request}"""
        response = _call(client.models.generate_content, model=MODEL, contents=prompt)
        return response.text.strip()


# ══════════════════════════════════════════════════════════════════════════════
# Scenario examples
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS = {
    "✅ Low-risk (auto)":
        "I'd like to know the current interest rate on my savings account and whether I can add to it online.",

    "🟡 Medium refund (auto)":
        "I purchased a subscription 2 weeks ago for £29.99 but I haven't used it at all. "
        "I'd like a refund please.",

    "🔴 High-value refund (HITL)":
        "I need a full refund of £850 for the annual premium plan I bought 45 days ago. "
        "The product doesn't work as advertised and I have screenshots as evidence.",

    "🔴 Legal threat (HITL — critical)":
        "This is absolutely unacceptable. You've charged me twice and no one is helping. "
        "I'm filing a complaint with the FCA and taking this to the Financial Ombudsman Service "
        "if this isn't resolved by end of day. I want my £200 back immediately.",

    "🟡 Account closure (HITL)":
        "I've been a NexaBank customer for 8 years but I'd like to close all my accounts "
        "and transfer my balance elsewhere. Please process this today.",

    "🔴 Large transaction (HITL — AML)":
        "I need to transfer £15,000 to a new overseas account urgently. "
        "It's for a business investment opportunity. Please process immediately.",
}

# ══════════════════════════════════════════════════════════════════════════════
# Session state init
# ══════════════════════════════════════════════════════════════════════════════

for key, default in [
    ("hitl_state",     "idle"),       # idle | analysing | checkpoint | decided | complete
    ("hitl_analysis",  None),
    ("hitl_request",   ""),
    ("hitl_decision",  None),
    ("hitl_note",      ""),
    ("hitl_modified",  ""),
    ("hitl_final",     ""),
    ("hitl_ref",       ""),
    ("sel_3c",         SCENARIOS["🔴 High-value refund (HITL)"]),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Scenarios:**")
    for label, text in SCENARIOS.items():
        if st.button(label, key=f"sc3c_{label}"):
            st.session_state.sel_3c     = text
            st.session_state.hitl_state = "idle"
            st.session_state.hitl_analysis = None
            st.session_state.hitl_decision = None
            st.session_state.hitl_final    = ""
            st.rerun()
with col1:
    request = st.text_area(
        "Customer request:",
        value=st.session_state.sel_3c,
        height=100,
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — AGENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

if st.button("▶  Run Agent", type="primary", key="run_3c",
             disabled=st.session_state.hitl_state not in ("idle",)):
    st.session_state.hitl_request  = request
    st.session_state.hitl_ref      = uuid.uuid4().hex[:8].upper()
    st.session_state.hitl_decision = None
    st.session_state.hitl_final    = ""

    with st.spinner("Agent analysing request…"):
        analysis = agent_analyse(request)
    st.session_state.hitl_analysis = analysis

    if analysis.get("requires_hitl"):
        st.session_state.hitl_state = "checkpoint"
    else:
        st.session_state.hitl_state = "complete"
        st.session_state.hitl_decision = "auto"
        st.session_state.hitl_final = analysis.get("proposed_response", "")
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

state    = st.session_state.hitl_state
analysis = st.session_state.hitl_analysis

if state == "idle":
    st.info("Select a scenario above and click **▶ Run Agent** to start.")
    st.stop()

# ── Agent analysis card ───────────────────────────────────────────────────────
if analysis:
    with st.container(border=True):
        st.markdown("#### 🤖 Agent Analysis")
        risk_colors = {"low": "✅", "medium": "🟡", "high": "🔴", "critical": "🚨"}
        r = analysis.get("risk_level", "low")
        c = analysis.get("confidence", 1.0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Risk Level",  f"{risk_colors.get(r,'?')} {r.upper()}")
        m2.metric("Confidence",  f"{c:.0%}")
        m3.metric("Action",      analysis.get("proposed_action", "—").replace("_", " ").title())
        m4.metric("HITL",        "✅ Required" if analysis.get("requires_hitl") else "❌ Not needed")

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"**Understanding:** {analysis.get('understanding','')}")
            st.markdown(f"**Policy:** {analysis.get('relevant_policy','')}")
            if analysis.get("checkpoint_triggers"):
                st.markdown("**Checkpoint triggers:**")
                for t in analysis["checkpoint_triggers"]:
                    rule = CHECKPOINT_RULES.get(t, (t, "medium"))
                    st.warning(f"⚠️  {rule[0]}  `[{rule[1]}]`")
        with col_r:
            if analysis.get("factors_for"):
                st.markdown("**Factors FOR proposed action:**")
                for f in analysis["factors_for"]:
                    st.markdown(f"  ✓ {f}")
            if analysis.get("factors_against"):
                st.markdown("**Factors AGAINST:**")
                for f in analysis["factors_against"]:
                    st.markdown(f"  ✗ {f}")

# ══════════════════════════════════════════════════════════════════════════════
# AUTO PATH — no HITL needed
# ══════════════════════════════════════════════════════════════════════════════

if state == "complete" and st.session_state.hitl_decision == "auto":
    st.success("### ✅ Auto-processed — No human approval needed")
    st.info(
        "**Risk level is low and confidence is high.** "
        "Agent responded automatically without pausing."
    )
    st.success(f"**Response sent to customer:**\n\n{st.session_state.hitl_final}")
    st.caption(f"Ref: {st.session_state.hitl_ref} | Auto-processed | No HITL triggered")

# ══════════════════════════════════════════════════════════════════════════════
# CHECKPOINT PATH — HITL required
# ══════════════════════════════════════════════════════════════════════════════

elif state in ("checkpoint", "decided", "complete") and analysis:

    st.markdown(
        "<div style='text-align:center;font-size:1.4rem'>↓ HITL checkpoint triggered</div>",
        unsafe_allow_html=True
    )

    # ── Human review panel ────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            f"### 👤 HUMAN REVIEW REQUIRED  |  Ref: `{st.session_state.hitl_ref}`"
        )
        st.markdown(
            f"**Risk:** `{analysis.get('risk_level','').upper()}`  |  "
            f"**Confidence:** `{analysis.get('confidence',0):.0%}`  |  "
            f"**Proposed:** `{analysis.get('proposed_action','').replace('_',' ').title()}`"
        )
        st.markdown("---")

        st.markdown("**Customer's original request:**")
        st.info(st.session_state.hitl_request)

        st.markdown("**Agent's proposed response (draft):**")
        st.warning(analysis.get("proposed_response", ""))

        # ── Decision buttons ──────────────────────────────────────────────────
        if state == "checkpoint":
            st.markdown("---")
            st.markdown("#### Your decision:")
            d1, d2, d3 = st.columns(3)

            with d1:
                if st.button("✅  Approve", key="hitl_approve",
                              type="primary", use_container_width=True):
                    st.session_state.hitl_decision = "approved"
                    st.session_state.hitl_state    = "decided"
                    st.rerun()

            with d2:
                reject_note = st.text_input("Reason (optional):", key="reject_note_3c",
                                            placeholder="e.g. Outside 30-day policy")
                if st.button("❌  Reject", key="hitl_reject",
                              use_container_width=True):
                    st.session_state.hitl_decision = "rejected"
                    st.session_state.hitl_note     = reject_note
                    st.session_state.hitl_state    = "decided"
                    st.rerun()

            with d3:
                modified = st.text_area(
                    "Edit response:", key="modified_resp_3c",
                    value=analysis.get("proposed_response", ""),
                    height=100,
                )
                if st.button("✏️  Approve Modified", key="hitl_modify",
                              use_container_width=True):
                    st.session_state.hitl_decision = "modified"
                    st.session_state.hitl_modified = modified
                    st.session_state.hitl_state    = "decided"
                    st.rerun()

    # ── Agent continues after decision ────────────────────────────────────────
    if state == "decided":
        decision = st.session_state.hitl_decision
        with st.spinner("Agent processing human decision…"):
            final = agent_continue(
                st.session_state.hitl_request,
                analysis,
                decision,
                st.session_state.hitl_note,
                st.session_state.hitl_modified,
            )
        st.session_state.hitl_final = final
        st.session_state.hitl_state = "complete"
        st.rerun()

    # ── Final outcome ─────────────────────────────────────────────────────────
    if state == "complete" and st.session_state.hitl_final:
        decision = st.session_state.hitl_decision
        outcome_map = {
            "approved": ("✅ Approved — Response Sent", "success"),
            "rejected": ("❌ Rejected — Rejection Sent", "error"),
            "modified": ("✏️ Modified — Edited Response Sent", "warning"),
        }
        title, style = outcome_map.get(decision, ("Complete", "info"))
        st.markdown(f"### {title}")
        getattr(st, style)(st.session_state.hitl_final)
        st.caption(
            f"Ref: {st.session_state.hitl_ref} | "
            f"Decision: {decision.upper()} | "
            f"Logged for audit trail (FCA SYSC 9.1)"
        )

        with st.expander("🔍 HITL summary — what happened and why"):
            st.markdown(f"""
| Step | What happened |
|---|---|
| **Agent analysed** | Parsed request, assessed risk: `{analysis.get('risk_level')}`, confidence: `{analysis.get('confidence',0):.0%}` |
| **Checkpoint triggered** | `{', '.join(analysis.get('checkpoint_triggers', ['none']))}` |
| **Agent paused** | Presented draft to human reviewer |
| **Human decided** | `{decision.upper()}` |
| **Agent resumed** | Generated final response based on human decision |

**Why HITL over guardrails alone:**
Guardrails (3b) catch *unsafe* inputs/outputs automatically.
HITL handles *ambiguous* situations — policy edge cases, relationship context,
legal nuance — where a human understands the full picture better than the model.

**In production:** Checkpoint queue feeds into a case management system.
Reviewers have SLA timers. If no decision within X minutes → auto-escalate.
""")

        if st.button("🔄  Reset — try another scenario", key="reset_3c"):
            for k in ["hitl_state", "hitl_analysis", "hitl_decision",
                      "hitl_note", "hitl_modified", "hitl_final"]:
                st.session_state[k] = ("idle" if k == "hitl_state" else
                                       None if k == "hitl_analysis" else "")
            st.rerun()

st.markdown("---")
st.markdown("### What's next → Phase 5a: RAG Agent")
st.markdown(
    "Combines retrieval with agency — agent searches a knowledge base "
    "before answering, grounding responses in your specific documents."
)
