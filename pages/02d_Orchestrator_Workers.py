"""
Phase 2d — Orchestrator-Workers
Orchestrator LLM dynamically plans sub-tasks; Worker LLMs execute each one in parallel.
Demo: Customer complaint → Orchestrator plans → Workers execute → Final package
"""

import streamlit as st
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 2d — Orchestrator-Workers", page_icon="🎯", layout="wide")
st.title("🎯 Phase 2d — Orchestrator-Workers")
st.caption("Workflow Pattern 4 of 5 — from *Building Effective Agents*, Anthropic Engineering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_2d
st.image(diagram_2d(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Orchestrator-Workers — and how close is it to an Agent?"):
    st.markdown("""
    > *"In the orchestrator-workers workflow, an orchestrator LLM directs agents to use
    > tools or undertake tasks with the intention of completing some broader goal."*
    > — Anthropic, Building Effective Agents

    **How it differs from the previous patterns:**

    | Pattern | Who decides the tasks? | Fixed structure? |
    |---|---|---|
    | 2a Chaining | You (hardcoded steps) | ✅ Always same steps |
    | 2b Routing | You (hardcoded branches) | ✅ Always same branches |
    | 2c Parallelization | You (hardcoded workers) | ✅ Always same calls |
    | **2d Orchestrator-Workers** | **Orchestrator LLM (dynamic)** | **❌ Tasks vary by input** |

    **First hint of agency:** The orchestrator DYNAMICALLY decides which sub-tasks to create
    based on the specific complaint. A billing complaint might need 3 tasks;
    a technical complaint might need 4 different ones.

    **Why it is still NOT an Agent:**
    The plan is made ONCE upfront. Worker results do NOT feed back into the orchestrator.
    If a worker returns a surprising result, the orchestrator can't course-correct.
    A true agent would observe results and adapt its next actions accordingly (Phase 3).
    """)

st.markdown("---")

# ── Specialist definitions ─────────────────────────────────────────────────────

SPECIALIST_SYSTEMS = {
    "sentiment_analyst": (
        "You are a customer sentiment analyst. Analyse the emotional tone, urgency (1-10 scale), "
        "and key pain points. Be concise — 3 sentences max."
    ),
    "solution_researcher": (
        "You are a customer support policy expert. Identify the best resolution approach, "
        "relevant policy, and realistic resolution timeline. Be specific. 3 sentences max."
    ),
    "response_drafter": (
        "You are a customer support writer. Draft a professional, empathetic reply "
        "that directly addresses the issue. Under 80 words. Ready to send."
    ),
    "escalation_checker": (
        "You are an escalation specialist. Give a clear YES or NO on whether this needs "
        "manager escalation. State your reason in one sentence. Consider: financial impact, "
        "legal risk, repeated contact, and emotional state."
    ),
    "knowledge_updater": (
        "You are a knowledge base curator. Suggest one FAQ entry or knowledge base update "
        "that this complaint reveals is missing. Format: Question + Answer, under 50 words total."
    ),
}

SPECIALIST_ICONS = {
    "sentiment_analyst":  "😊",
    "solution_researcher": "🔍",
    "response_drafter":   "✍️",
    "escalation_checker": "🚨",
    "knowledge_updater":  "📚",
}

# ── Orchestrator ──────────────────────────────────────────────────────────────

def orchestrate(complaint: str) -> dict:
    """
    Orchestrator LLM — dynamically plans which specialists are needed.
    This is what makes 2d different: task list varies by input.
    """
    prompt = f"""You are the orchestrator of a customer support team.
Analyse this complaint and create a task plan. Choose ONLY the specialists truly needed.

Available specialists:
- sentiment_analyst    : tone, urgency, pain points
- solution_researcher  : best resolution, policy, timeline
- response_drafter     : customer-facing reply
- escalation_checker   : does this need manager escalation?
- knowledge_updater    : what FAQ is missing?

Rules:
- Choose 3-4 specialists relevant to THIS specific complaint
- Each task must have a specific instruction tailored to this complaint
- Return only valid JSON, no markdown

{{
  "complaint_summary": "one sentence",
  "tasks": [
    {{
      "id": 1,
      "specialist": "specialist_name",
      "instruction": "specific instruction for this complaint",
      "why": "why this specialist is needed here"
    }}
  ]
}}

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
        return {
            "complaint_summary": complaint[:80],
            "tasks": [
                {"id": 1, "specialist": "sentiment_analyst",
                 "instruction": "Analyse this complaint.", "why": "fallback"},
                {"id": 2, "specialist": "response_drafter",
                 "instruction": "Draft a reply.", "why": "fallback"},
            ],
        }


def run_worker(task: dict, complaint: str) -> dict:
    """A single worker — specialised LLM call for one task."""
    specialist = task["specialist"]
    system = SPECIALIST_SYSTEMS.get(specialist, "You are a helpful assistant.")
    prompt = f"""{task['instruction']}

Customer complaint:
\"\"\"{complaint}\"\"\""""

    try:
        response = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return {**task, "result": response.text.strip(), "status": "done"}
    except Exception as e:
        return {**task, "result": f"Error: {e}", "status": "error"}


def assemble(complaint: str, results: list[dict]) -> str:
    """Final assembly — orchestrator combines all worker outputs."""
    worker_reports = "\n\n".join(
        f"[{SPECIALIST_ICONS.get(r['specialist'], '•')} {r['specialist']}]:\n{r['result']}"
        for r in sorted(results, key=lambda x: x["id"])
    )
    prompt = f"""You are the orchestrator assembling a complete customer support package.
Based on the specialist reports, create a final structured package.

Format:
1. **SEND TO CUSTOMER** (ready-to-send reply)
2. **INTERNAL ACTIONS** (what the team must do next)
3. **ESCALATION** (Yes/No with brief reason)

Complaint: {complaint}

Specialist reports:
{worker_reports}

Final package:"""

    response = _call(client.models.generate_content, model=MODEL, contents=prompt)
    return response.text.strip()


# ── Examples ───────────────────────────────────────────────────────────────────

EXAMPLES = {
    "Billing dispute":   "I was charged $49.99 on March 3rd but cancelled my subscription on February 28th. I have the cancellation confirmation email. I want a full refund immediately — this is the third billing issue I've had with your company.",
    "Technical crisis":  "Your app crashed during my client presentation today and I lost 30 minutes of unsaved work. This is completely unacceptable for a professional tool. I've submitted three bug reports in the past month and nothing has been fixed.",
    "General feedback":  "I've been using your product for 2 years and love it overall. I wanted to flag that the onboarding for new team members is confusing — three of my colleagues gave up before completing setup. The tutorial videos are outdated.",
}

# ── UI ─────────────────────────────────────────────────────────────────────────

if "sel_2d" not in st.session_state:
    st.session_state.sel_2d = EXAMPLES["Billing dispute"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Quick examples:**")
    for label, text in EXAMPLES.items():
        if st.button(label, key=f"ex2d_{label}"):
            st.session_state.sel_2d = text
            st.rerun()
with col1:
    complaint = st.text_area(
        "Customer complaint:",
        value=st.session_state.sel_2d,
        height=110,
    )

st.markdown("---")

if st.button("▶  Run Orchestrator-Workers", type="primary", key="run_2d"):

    if not complaint.strip():
        st.warning("Please enter a complaint.")
        st.stop()

    # ── STEP 1 — Orchestrator plans ───────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 1 — 🎯 Orchestrator: Dynamic Task Planning")
        st.caption(
            "Orchestrator LLM reads the complaint and DECIDES which specialists to deploy. "
            "This task list is not hardcoded — it varies by input."
        )

        with st.spinner("Orchestrator analysing and planning…"):
            plan = orchestrate(complaint)

        st.markdown(f"**Complaint summary:** {plan.get('complaint_summary', '')}")
        st.markdown(f"**Tasks planned: {len(plan.get('tasks', []))}** "
                    f"*(chosen dynamically for this specific complaint)*")

        task_cols = st.columns(len(plan.get("tasks", [])))
        for col, task in zip(task_cols, plan.get("tasks", [])):
            icon = SPECIALIST_ICONS.get(task["specialist"], "•")
            with col:
                st.info(
                    f"**Task {task['id']}**\n\n"
                    f"{icon} `{task['specialist']}`\n\n"
                    f"*{task['why']}*"
                )

    st.markdown("<div style='text-align:center;font-size:1.5rem'>↓</div>",
                unsafe_allow_html=True)

    # ── STEP 2 — Workers execute in parallel ──────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 2 — 👷 Workers: Parallel Execution")
        st.caption("Each specialist runs simultaneously. YOUR code launches ThreadPoolExecutor.")

        tasks = plan.get("tasks", [])
        w_cols = st.columns(len(tasks))
        placeholders = {}
        for col, task in zip(w_cols, tasks):
            icon = SPECIALIST_ICONS.get(task["specialist"], "•")
            ph = col.empty()
            ph.info(f"{icon} **{task['specialist']}**\n\n⏳ running…")
            placeholders[task["id"]] = ph

        t_start = time.time()

        worker_results = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {
                executor.submit(run_worker, task, complaint): task["id"]
                for task in tasks
            }
            for future in as_completed(futures):
                result = future.result()
                worker_results.append(result)
                icon = SPECIALIST_ICONS.get(result["specialist"], "•")
                placeholders[result["id"]].success(
                    f"{icon} **{result['specialist']} ✓**\n\n{result['result'][:220]}"
                    + ("…" if len(result["result"]) > 220 else "")
                )

        t_elapsed = time.time() - t_start
        st.success(
            f"⚡ All {len(tasks)} workers completed in **{t_elapsed:.1f}s** (parallel). "
            f"Sequential would take ~**{t_elapsed * len(tasks):.1f}s**."
        )

    st.markdown("<div style='text-align:center;font-size:1.5rem'>↓</div>",
                unsafe_allow_html=True)

    # ── STEP 3 — Assembly ─────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### Step 3 — 🎯 Orchestrator: Assemble Final Package")
        st.caption("Orchestrator sees ALL worker results and assembles the final output.")

        with st.spinner("Assembling…"):
            package = assemble(complaint, worker_results)

        st.success(package)

    # ── Summary ───────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 What makes this different — and what's still missing for an Agent"):
        st.markdown(f"""
| Step | Who acts | What happens |
|---|---|---|
| **Orchestrator plans** | Orchestrator LLM | Dynamically chooses {len(tasks)} specialists for THIS complaint |
| **Workers execute** | {len(tasks)} Worker LLMs | Run in parallel, each focused on one task |
| **Assembly** | Orchestrator LLM | Combines all results into final package |

**What's new vs 2a–2c:** The task list is NOT hardcoded. The orchestrator decided which
specialists to use based on the complaint content.

**What's still missing for a true Agent:**
> The orchestrator planned once and never looked back.
> If the `escalation_checker` returned "YES — escalate immediately",
> the orchestrator didn't change its other tasks or add new ones.
> A real agent would **observe** that result and **adapt** its plan.
> That feedback loop is what Phase 3 adds.
""")

    st.markdown("---")
    st.markdown("### What's next → Phase 2e: Evaluator-Optimizer")
    st.markdown(
        "A Generator LLM produces output, an Evaluator LLM scores it, "
        "and the loop repeats until quality reaches a threshold. "
        "The first pattern with an **iterative feedback loop**."
    )
