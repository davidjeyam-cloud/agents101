"""
Phase 7d — Stateful Task Management
Production patterns for long-running agent tasks:
task queues, checkpoint/resume, idempotency, dead-letter handling.
"""
import os, json, time, uuid
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils.llm import MODEL, _call
from utils.styles import phase_header, ACCENT_COMPLETE
from utils.trace import render_trace

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 7d — Stateful Task Management", page_icon="📋", layout="wide")

if not api_key:
    st.error("GEMINI_API_KEY not found."); st.stop()

client = genai.Client(api_key=api_key)

st.markdown(phase_header(
    "Phase 7d &nbsp;·&nbsp; Production Operations &nbsp;·&nbsp; Stateful Tasks",
    "📋 Stateful Task Management",
    "Long-running agent tasks need more than a function call — they need state, "
    "resumption, idempotency, and failure recovery. This phase covers the production patterns.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 Why stateful task management — what breaks without it?"):
    st.markdown("""
In every demo before Phase 7, an agent task is a single function call: send → wait → receive.
This works for tasks that complete in seconds. Production agents often run tasks that take
minutes, must survive server restarts, and need to be auditable.

**What breaks with stateless agents in production:**

| Scenario | Stateless failure | Stateful solution |
|---|---|---|
| Server restarts mid-task | Task lost — user never gets a result | Checkpoint state to DB; resume from last step |
| Same request submitted twice | Task runs twice — double charge, duplicate action | Idempotency key deduplicates |
| Step 4 of 7 fails | Entire task restarts from step 1 | Checkpoint at each step; resume from step 4 |
| 1,000 tasks arrive at once | Agent blocks synchronously; timeouts | Task queue decouples submission from execution |
| Task stuck for 30 minutes | No visibility; user gives up | Task lifecycle with status polling |

**The task lifecycle — every production agent task has these states:**

```
SUBMITTED ──► QUEUED ──► RUNNING ──► COMPLETED
                │              │
                │              ├──► FAILED ──► DEAD_LETTER
                │              │
                └──────────────┴──► CANCELLED
```

**Four production patterns this phase covers:**

| Pattern | Problem it solves | Key mechanism |
|---|---|---|
| **Task queue** | Decouple task submission from execution | Tasks submitted to a queue; workers pull and execute independently |
| **Checkpoint / resume** | Survive failures and restarts at any step | Save state after each step; on restart, load state and continue |
| **Idempotency** | Prevent duplicate execution | Each task has a unique key; second submission returns existing result |
| **Dead-letter handling** | Graceful failure recovery | Failed tasks after N retries go to a dead-letter store for human review |
""")

with st.expander("📐 Core Code Pattern — Stateful Task Manager"):
    st.code('''
import json, uuid, time
from pathlib import Path
from enum import Enum

class TaskState(str, Enum):
    SUBMITTED   = "submitted"
    RUNNING     = "running"
    COMPLETED   = "completed"
    FAILED      = "failed"
    DEAD_LETTER = "dead_letter"

class TaskCheckpoint:
    """Persist task state to disk (replace with Redis/DB in production)."""
    def __init__(self, task_id: str, store_path: str = "/tmp/tasks"):
        self.path = Path(store_path) / f"{task_id}.json"
        self.path.parent.mkdir(exist_ok=True)

    def save(self, state: dict) -> None:
        self.path.write_text(json.dumps(state, indent=2))

    def load(self) -> dict | None:
        return json.loads(self.path.read_text()) if self.path.exists() else None

    def delete(self) -> None:
        self.path.unlink(missing_ok=True)


def run_with_checkpoint(task_id: str, steps: list[callable]) -> dict:
    """
    Execute a multi-step task with checkpoint/resume.
    On failure, restart resumes from the last completed step.
    """
    ckpt = TaskCheckpoint(task_id)
    state = ckpt.load() or {
        "task_id":       task_id,
        "status":        TaskState.RUNNING,
        "completed_steps": [],
        "results":       {},
        "retry_count":   0,
    }

    for i, step_fn in enumerate(steps):
        step_name = step_fn.__name__
        if step_name in state["completed_steps"]:
            continue                              # ← already done; skip on resume

        try:
            result = step_fn(state["results"])
            state["results"][step_name] = result
            state["completed_steps"].append(step_name)
            ckpt.save(state)                      # ← checkpoint after every step
        except Exception as e:
            state["retry_count"] += 1
            state["status"] = TaskState.FAILED
            state["error"] = str(e)
            if state["retry_count"] >= 3:
                state["status"] = TaskState.DEAD_LETTER
            ckpt.save(state)
            raise

    state["status"] = TaskState.COMPLETED
    ckpt.save(state)
    return state["results"]


def idempotent_submit(idempotency_key: str, task_fn: callable) -> dict:
    """
    Run task_fn only once per idempotency_key.
    Second call with same key returns cached result without re-running.
    """
    ckpt = TaskCheckpoint(idempotency_key)
    existing = ckpt.load()
    if existing and existing.get("status") == TaskState.COMPLETED:
        return {"cached": True, "result": existing["results"]}  # ← deduplicated
    return {"cached": False, "result": task_fn()}
''', language="python")
    st.markdown("""
**What this replaces from earlier phases:**
- Phase 4b HITL stored approval state in `st.session_state` — that's lost on page refresh
- Phase 5b Long-term Memory persisted facts across sessions — tasks need the same for execution state
- LangGraph MemorySaver (Phase 10b) is one implementation of this pattern — `TaskCheckpoint` above is the raw equivalent

**Production stack for each component:**

| Component | Development | Production |
|---|---|---|
| Task queue | `asyncio.Queue` / in-memory | Redis Queue, Celery, AWS SQS, Google Pub/Sub |
| Checkpoint store | JSON files on disk | Redis, PostgreSQL, DynamoDB |
| Dead-letter | Log file | Dedicated DLQ topic + alerting |
| Task status API | Dict in memory | REST endpoint backed by DB |
""")

# ── Demo ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Live Demo — Multi-step agent task with checkpoint/resume simulation")
st.caption(
    "This demo simulates a 4-step agentic task (research → analyse → draft → review). "
    "You can introduce a failure at any step to see the checkpoint/resume pattern in action."
)

if "task_state" not in st.session_state:
    st.session_state.task_state = None
if "task_log" not in st.session_state:
    st.session_state.task_log = []

DEMO_TASKS = {
    "NexaBank product comparison": "Compare NexaBank's three savings products: NexaSaver (4.75% AER), NexaFlex ISA (4.2% AER tax-free), and NexaCurrent (0.1% cashback). Which is best for a customer with £10,000?",
    "Fraud response plan": "A customer reports £1,200 in unauthorised transactions. Draft a step-by-step response plan following NexaBank's fraud policy.",
    "Complaint escalation decision": "A customer has been waiting 9 weeks with no resolution. What are their rights and what should NexaBank's response be?",
}

col1, col2 = st.columns([2, 1])
with col1:
    task_input = st.text_area("Task:", value=list(DEMO_TASKS.values())[0], height=80, key="stm_task")
with col2:
    st.markdown("**Presets:**")
    for label, text in DEMO_TASKS.items():
        if st.button(label[:30] + "…", key=f"stm_{label[:15]}"):
            st.session_state.stm_input = text
            st.rerun()

col_a, col_b, col_c = st.columns(3)
with col_a:
    inject_failure = st.selectbox("Simulate failure at step:", ["None", "Step 2 — Analyse", "Step 3 — Draft"], key="stm_fail")
with col_b:
    task_id = st.text_input("Task ID (idempotency key):", value=f"task-{str(uuid.uuid4())[:8]}", key="stm_id")
with col_c:
    st.markdown(" ")
    resume_mode = st.checkbox("Resume from checkpoint (if exists)", value=False, key="stm_resume")

if st.button("▶  Submit Task", type="primary", key="run_stm"):
    if not task_input.strip():
        st.warning("Please enter a task.")
        st.stop()

    fail_at = None
    if inject_failure == "Step 2 — Analyse":
        fail_at = 1
    elif inject_failure == "Step 3 — Draft":
        fail_at = 2

    # Simulate checkpoint store in session state
    if not resume_mode or "stm_checkpoint" not in st.session_state:
        st.session_state.stm_checkpoint = {
            "task_id": task_id,
            "status": "running",
            "completed_steps": [],
            "results": {},
            "retry_count": 0,
        }
    state = st.session_state.stm_checkpoint

    STEPS = [
        ("Research",  f"Research this topic thoroughly in 3 bullet points:\n{task_input}"),
        ("Analyse",   "Based on the research above, identify the 2 most important considerations."),
        ("Draft",     "Write a concise 100-word response to the original task based on the analysis."),
        ("Review",    "Review the draft for accuracy, completeness, and tone. Output: APPROVED or suggest one improvement."),
    ]

    st.markdown("### Task Execution Trace")
    all_ok = True

    for i, (step_name, _) in enumerate(STEPS):
        if step_name in state["completed_steps"]:
            st.success(f"✅ Step {i+1} — {step_name}: **loaded from checkpoint** (skipped re-execution)")
            continue

        if fail_at == i:
            state["status"] = "failed"
            state["retry_count"] += 1
            st.session_state.stm_checkpoint = state
            st.error(f"❌ Step {i+1} — {step_name}: **SIMULATED FAILURE** (retry_count={state['retry_count']})")
            st.warning("Task checkpointed. Tick 'Resume from checkpoint' and re-submit to continue from this step.")
            all_ok = False
            break

        # Build prompt with prior results
        prompt_parts = []
        for prior_step, prior_result in state["results"].items():
            prompt_parts.append(f"{prior_step} output:\n{prior_result}")
        prompt_parts.append(f"Now: {STEPS[i][1]}")
        full_prompt = "\n\n".join(prompt_parts)

        with st.spinner(f"Step {i+1} — {step_name} running..."):
            resp = _call(
                client.models.generate_content,
                model=MODEL,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a NexaBank expert agent. Be concise and accurate."
                ),
            )
        result = resp.text.strip()
        state["results"][step_name] = result
        state["completed_steps"].append(step_name)
        st.session_state.stm_checkpoint = state

        with st.container(border=True):
            st.markdown(f"**Step {i+1} — {step_name}** ✅ checkpointed")
            st.markdown(result)

    if all_ok:
        state["status"] = "completed"
        st.session_state.stm_checkpoint = state
        st.toast("✅ Task complete — all 4 steps checkpointed", icon="📋")

        def _tab_state():
            st.markdown("**Final checkpoint state:**")
            st.json({
                "task_id": state["task_id"],
                "status": state["status"],
                "completed_steps": state["completed_steps"],
                "retry_count": state["retry_count"],
            })
        def _tab_pattern():
            st.markdown("**Checkpoint/resume in action:**")
            st.code(
                "for step in steps:\n"
                "    if step.name in state['completed_steps']:\n"
                "        continue  # already done — skip on resume\n"
                "    result = run_step(step)\n"
                "    state['completed_steps'].append(step.name)\n"
                "    checkpoint.save(state)  # persist after every step",
                language="python",
            )
        render_trace(("Checkpoint State", _tab_state), ("Resume Pattern", _tab_pattern))

st.markdown("---")
st.markdown("### What's next → Phase 8e — Enterprise Event-Driven Patterns")
st.markdown(
    "Stateful task management solves the execution layer. "
    "Phase 8e shows how enterprise systems **trigger** these tasks — "
    "using Kafka, event brokers, and event-driven architectures to connect agents to business systems."
)
