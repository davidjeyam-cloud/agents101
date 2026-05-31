"""
Phase 3c -- Planning Agent (Plan-and-Execute)
Andrew Ng Pattern 3: agent writes an explicit numbered plan before acting.
The plan is a visible artefact -- unlike ReAct's implicit step-by-step reasoning.
Two tabs:
  A. Plan + Execute  -- standard Plan-and-Execute with real tools
  B. Adaptive Replanning -- plan revised mid-execution when results change
"""

import streamlit as st
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL
from utils.tools import get_country_info, get_public_holidays

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 3c -- Planning Agent", page_icon="🗺️", layout="wide")
st.title("🗺️ Phase 3c -- Planning Agent")
st.caption("Andrew Ng Pattern 3 -- write an explicit plan first, then execute step by step")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_planning
st.image(diagram_planning(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Plan-and-Execute -- and how does it differ from ReAct?"):
    st.markdown("""
    > *"Planning enables the agent to think ahead about what steps it needs to take
    > before actually taking them."* -- Andrew Ng, DeepLearning.AI Agentic AI Course

    **Three patterns that involve multi-step reasoning -- all different:**

    | Pattern | Phase | How it decides what to do next | Plan visible? |
    |---|---|---|---|
    | **ReAct** | 3a | One thought at a time -- emergent path | No |
    | **Orchestrator-Workers** | 2d | Orchestrator plans ONCE upfront, no feedback | Partially |
    | **Plan-and-Execute** | 3c | Explicit numbered plan upfront -- adapts on results | **Yes** |

    **What makes Plan-and-Execute unique:**
    - The plan is a **first-class artefact** -- you can read it, show it to users, log it
    - Agent commits to a structure before burning tokens on execution
    - **Adaptive replanning** -- if step 3 reveals something unexpected, the agent can revise steps 4-6
    - Works better than ReAct for tasks where the full scope is known upfront

    **Two phases:**
    1. **PLAN** -- LLM reads the task and writes a numbered JSON plan with rationale for each step
    2. **EXECUTE** -- LLM executes one step at a time, using tools, feeding results into the next step

    **When to use Planning over ReAct:**

    | Situation | Use ReAct | Use Planning |
    |---|---|---|
    | Task scope is unknown upfront | Yes | No |
    | Complex multi-part task with known structure | No | Yes |
    | User needs to see/approve the plan | No | Yes |
    | Steps have dependencies (step 3 needs step 2's output) | Implicit | Explicit |
    | Mid-task replanning needed | Hard | Built-in |
    """)

with st.expander("📐 Core Code Pattern -- Plan-and-Execute"):
    st.code('''
# ── PHASE 1: PLAN ─────────────────────────────────────────────────────────────
plan_json = llm(
    system="You are a planning agent. Create a numbered execution plan.",
    user=f"""Task: {task}

Return JSON:
{{
  "goal": "one sentence",
  "steps": [
    {{"step": 1, "description": "...", "tool": "none|get_country_info|...",
      "tool_args": {{}}, "rationale": "why this step"}}
  ]
}}"""
)
plan = json.loads(plan_json)
# plan["steps"] is now a visible, inspectable artefact

# ── PHASE 2: EXECUTE ──────────────────────────────────────────────────────────
completed = []
for step in plan["steps"]:
    # Call tool if needed
    tool_result = ""
    if step["tool"] != "none":
        tool_result = call_tool(step["tool"], step["tool_args"])

    # LLM executes the step using plan context + previous results
    result = llm(
        system="Execute this step. Use completed results as context.",
        user=f"""Goal: {plan["goal"]}
Full plan: {json.dumps(plan["steps"])}
Completed: {json.dumps(completed)}
Current step: {step["description"]}
Tool result: {tool_result}

Return JSON: {{"result": "...", "key_facts": [...], "needs_replan": false}}"""
    )
    completed.append({"step": step["step"], **json.loads(result)})

    # Adaptive replanning -- if this step changes the picture
    if json.loads(result).get("needs_replan"):
        plan["steps"] = replan(plan, completed)  # LLM revises remaining steps

# ── PHASE 3: SYNTHESIZE ───────────────────────────────────────────────────────
final_answer = llm(
    system="Synthesize all step results into a comprehensive response.",
    user=f"Goal: {plan['goal']}\\nAll results: {json.dumps(completed)}"
)
''', language="python")
    st.markdown("""
**Why Plan-and-Execute beats ReAct for complex multi-part tasks:**
ReAct's implicit reasoning means each thought step has no memory of the overall plan.
With an explicit plan, every execution step knows its purpose within the whole task.

**Adaptive replanning:**
If step 3's tool result reveals something unexpected (e.g., a customer is flagged for EDD),
the agent can revise steps 4-6 before executing them -- not possible in vanilla ReAct.

**Production use:** HITL integration -- show the plan to a human before executing.
The human can edit the plan before the agent acts. Connects Phase 4b (HITL) + Phase 3c (Planning).
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

TOOLS_AVAILABLE = {
    "get_country_info": get_country_info,
    "get_public_holidays": get_public_holidays,
}

TOOL_SCHEMAS = """Available tools:
- get_country_info(country: str) -> returns capital, population, currency, languages
- get_public_holidays(country_code: str, year: int) -> returns list of public holidays"""

PLANNER_SYS = f"""You are NexaBank's strategic planning agent.
Given a complex customer advisory task, create a detailed execution plan.

{TOOL_SCHEMAS}

Return ONLY valid JSON:
{{
  "goal": "one sentence summary",
  "steps": [
    {{
      "step": 1,
      "description": "what to do",
      "rationale": "why this step is needed",
      "tool": "none|get_country_info|get_public_holidays",
      "tool_args": {{}},
      "expected_output": "what this step should produce"
    }}
  ]
}}
Create 4-6 focused steps. Each step must produce a discrete, usable result."""

EXECUTOR_SYS = """You are NexaBank's execution agent.
Execute one step of a plan. Use completed step results as context.
Be specific -- cite NexaBank policies and facts where relevant.
Return ONLY valid JSON:
{{
  "step": N,
  "result": "detailed result of this step (2-4 sentences)",
  "key_facts": ["specific fact 1", "specific fact 2"],
  "needs_replan": false,
  "replan_reason": ""
}}"""

REPLANNER_SYS = """You are NexaBank's adaptive planning agent.
A step result has revealed that the remaining plan needs revision.
Update only the REMAINING steps (keep completed steps as-is).
Return ONLY valid JSON array of the revised remaining steps (same format as original plan steps)."""

SYNTHESIZER_SYS = """You are NexaBank's customer advisor writing a final comprehensive response.
Synthesize ALL step results into a professional, structured answer.
Be specific -- cite the actual facts from each step.
Format with clear sections. Keep under 300 words."""


def call_tool(tool_name: str, tool_args: dict) -> str:
    fn = TOOLS_AVAILABLE.get(tool_name)
    if not fn:
        return f"Tool '{tool_name}' not available."
    try:
        return str(fn(**tool_args))
    except Exception as e:
        return f"Tool error: {e}"


def llm_json(system: str, user: str) -> dict:
    resp = _call(
        client.models.generate_content,
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
        ),
    )
    return json.loads(resp.text)


def llm_text(system: str, user: str) -> str:
    resp = _call(
        client.models.generate_content,
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text.strip()


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIOS
# ══════════════════════════════════════════════════════════════════════════════

TASKS_A = {
    "International relocation (uses country tool)":
        "A NexaBank customer is relocating to Australia next month. "
        "Create a step-by-step financial transition plan covering: "
        "(1) best NexaBank account for international use, "
        "(2) how to send money internationally and the fees, "
        "(3) key facts about Australia relevant to banking, "
        "(4) a prioritised action checklist before and after the move.",

    "Savings strategy (multi-criteria analysis)":
        "I have GBP 15,000 to invest. Compare NexaBank's options: "
        "NexaSaver (4.75% AER variable), NexaFlex ISA (4.2% AER tax-free). "
        "Create a plan that: analyses each option, estimates 3-year returns, "
        "considers UK tax implications, and gives a clear recommendation.",

    "House purchase plan (complex multi-step)":
        "I want to buy a GBP 320,000 house in 18 months. I earn GBP 55,000 "
        "and have GBP 30,000 saved. Create a complete plan: "
        "(1) how much deposit I need and how much to save monthly, "
        "(2) which NexaBank savings account suits the goal, "
        "(3) mortgage affordability and NexaBank mortgage options, "
        "(4) month-by-month action plan.",
}

TASKS_B = {
    "EDD trigger (plan adapts mid-execution)":
        "A new customer from Nigeria wants to open a NexaBank account and "
        "immediately transfer GBP 12,000 to start. "
        "Assess this request step by step: account suitability, "
        "transfer feasibility, and compliance requirements.",

    "Holiday planning with banking (uses holidays tool)":
        "A customer is planning a 3-week trip to Japan in 2026 and wants "
        "NexaBank advice on: best payment methods abroad, currency exchange, "
        "travel insurance through NexaBank, and important Japan dates to avoid for banking.",
}

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_a, tab_b = st.tabs([
    "📋 Tab A -- Plan + Execute",
    "🔧 Tab B -- Adaptive Replanning",
])


# ════════════════════════════════════════════════════════════════════════════════
# TAB A -- Standard Plan-and-Execute
# ════════════════════════════════════════════════════════════════════════════════

with tab_a:
    st.subheader("Tab A -- Standard Plan-and-Execute")
    st.markdown("""
    Agent writes an explicit numbered plan **before** doing any work.
    You can read the plan, understand the intent, and watch each step execute.
    """)

    if "sel_plan_a" not in st.session_state:
        st.session_state.sel_plan_a = list(TASKS_A.keys())[0]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Scenarios:**")
        for label in TASKS_A:
            if st.button(label, key=f"pa_{label}"):
                st.session_state.sel_plan_a = label
                st.rerun()
    with col1:
        task_a = st.text_area("Task:", value=TASKS_A[st.session_state.sel_plan_a], height=110)

    if st.button("▶  Generate Plan + Execute", type="primary", key="run_plan_a"):

        # ── PHASE 1: PLAN ────────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### 📋 Phase 1 -- PLAN")
            st.caption("LLM reads the full task and writes a numbered plan before touching any tool.")
            with st.spinner("Planner writing plan..."):
                try:
                    plan = llm_json(PLANNER_SYS, f"Task: {task_a}")
                except Exception as e:
                    st.error(f"Plan generation failed: {e}")
                    st.stop()

            st.success(f"**Goal:** {plan.get('goal', '')}")
            st.markdown(f"**Plan: {len(plan.get('steps', []))} steps**")

            for s in plan.get("steps", []):
                tool_badge = f"  `tool: {s['tool']}`" if s.get("tool") and s["tool"] != "none" else ""
                with st.expander(
                    f"Step {s['step']}: {s['description'][:70]}...{tool_badge}",
                    expanded=True,
                ):
                    st.markdown(f"**Why:** {s.get('rationale', '')}")
                    st.markdown(f"**Expected output:** {s.get('expected_output', '')}")
                    if s.get("tool") and s["tool"] != "none":
                        st.info(f"Tool: `{s['tool']}({s.get('tool_args', {})})`")

        st.markdown(
            "<div style='text-align:center;font-size:1.2rem;margin:6px 0'>"
            "? plan committed -- now execute step by step</div>",
            unsafe_allow_html=True,
        )

        # ── PHASE 2: EXECUTE ─────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### ⚡ Phase 2 -- EXECUTE")
            st.caption("Each step runs in order. Tool results are injected before the LLM reasons.")

            completed = []
            steps = plan.get("steps", [])

            for s in steps:
                with st.container(border=True):
                    st.markdown(f"**Step {s['step']}: {s['description']}**")

                    tool_result = ""
                    if s.get("tool") and s["tool"] != "none":
                        with st.spinner(f"Calling {s['tool']}..."):
                            tool_result = call_tool(s["tool"], s.get("tool_args", {}))
                        st.code(f"Tool: {s['tool']}({s.get('tool_args',{})})\nResult: {tool_result[:300]}", language="text")

                    exec_user = f"""Goal: {plan['goal']}
Full plan: {json.dumps(steps, indent=2)}
Completed so far: {json.dumps(completed, indent=2)}
Current step {s['step']}: {s['description']}
Tool result: {tool_result if tool_result else 'No tool used -- reason through this step.'}

Execute this step and return JSON."""

                    with st.spinner(f"Executing step {s['step']}..."):
                        try:
                            step_result = llm_json(EXECUTOR_SYS, exec_user)
                        except Exception as e:
                            step_result = {"step": s["step"], "result": f"Error: {e}",
                                          "key_facts": [], "needs_replan": False}

                    st.info(step_result.get("result", ""))
                    if step_result.get("key_facts"):
                        for fact in step_result["key_facts"]:
                            st.caption(f"✨ {fact}")

                    step_result["_tool"]        = s.get("tool", "none")
                    step_result["_tool_args"]   = s.get("tool_args", {})
                    step_result["_tool_result"] = tool_result[:300] if tool_result else ""
                    completed.append(step_result)

        st.markdown(
            "<div style='text-align:center;font-size:1.2rem;margin:6px 0'>"
            "? all steps complete -- synthesizing final answer</div>",
            unsafe_allow_html=True,
        )

        # ── PHASE 3: SYNTHESIZE ───────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### ? Phase 3 -- FINAL ANSWER")
            synth_user = (
                f"Goal: {plan['goal']}\n\n"
                f"Step results:\n{json.dumps(completed, indent=2)}"
            )
            with st.spinner("Synthesizing final answer..."):
                final = llm_text(SYNTHESIZER_SYS, synth_user)
            st.success(final)

        # ── Trace ─────────────────────────────────────────────────────────────
        with st.expander("🔬 Execution Trace -- prompts and step-by-step outputs"):
            st.markdown("**Planner system prompt:**")
            st.code(PLANNER_SYS, language="text")
            st.markdown("**Plan (JSON artefact):**")
            st.code(json.dumps(plan, indent=2), language="json")
            st.markdown("**Executor system prompt:**")
            st.code(EXECUTOR_SYS, language="text")
            st.markdown("**All step results (JSON):**")
            st.code(json.dumps(completed, indent=2), language="json")

        with st.expander("🔍 What just happened -- Plan-and-Execute breakdown"):
            tool_step_count = sum(1 for s in steps if s.get("tool") and s["tool"] != "none")
            st.markdown(f"""
| Phase | What ran | Actual output | LLM calls |
|---|---|---|---|
| **1 — Plan** | Planner LLM read the full task | {len(steps)}-step numbered plan with rationale | 1 |
| **2 — Execute** | Each step ran in sequence | {len(completed)} steps completed, results chained | {len(completed)} |
| **2b — Tools** | {tool_step_count} tool call(s) fired | Raw API data injected into executor context | 0 (tool, not LLM) |
| **3 — Synthesize** | Final LLM assembled all step results | Structured answer delivered to user | 1 |
""")

            st.markdown("---")
            st.markdown("**Step-by-step: what tool was called and what came back**")

            # Build per-step rows
            header = "| Step | Tool Called | Arguments | Raw Tool Result | Agent Conclusion |"
            divider = "|---|---|---|---|---|"
            rows = [header, divider]
            for c in completed:
                tool      = c.get("_tool", "none")
                args      = c.get("_tool_args", {})
                raw       = c.get("_tool_result", "")
                result    = c.get("result", "")
                step_num  = c.get("step", "?")

                tool_cell   = f"`{tool}`" if tool and tool != "none" else "—"
                args_cell   = str(args) if args else "—"
                raw_cell    = (raw[:120] + "…") if len(raw) > 120 else (raw if raw else "—")
                result_cell = (result[:120] + "…") if len(result) > 120 else result

                rows.append(f"| **Step {step_num}** | {tool_cell} | {args_cell} | {raw_cell} | {result_cell} |")

            st.markdown("\n".join(rows))

            st.markdown("""
---
**Key insight:** The plan is committed before any tokens are spent on execution.
Every execution step knows its purpose within the whole plan — unlike ReAct where each
Think step is unaware of the overall structure.
""")


# ════════════════════════════════════════════════════════════════════════════════
# TAB B -- Adaptive Replanning
# ════════════════════════════════════════════════════════════════════════════════

with tab_b:
    st.subheader("Tab B -- Adaptive Replanning")
    st.markdown("""
    Mid-execution, a step result reveals something unexpected.
    The agent **revises the remaining plan** before continuing -- impossible in vanilla ReAct.

    **Watch for:** The "needs_replan" flag triggers a new planner call that rewrites
    remaining steps based on what was just discovered.
    """)

    if "sel_plan_b" not in st.session_state:
        st.session_state.sel_plan_b = list(TASKS_B.keys())[0]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Scenarios:**")
        for label in TASKS_B:
            if st.button(label, key=f"pb_{label}"):
                st.session_state.sel_plan_b = label
                st.rerun()
    with col1:
        task_b = st.text_area("Task:", value=TASKS_B[st.session_state.sel_plan_b], height=110)

    st.info(
        "💡 These scenarios are designed so that an early step result changes the picture -- "
        "triggering the agent to rewrite remaining steps. Watch the plan evolve."
    )

    if st.button("▶  Run Adaptive Planning", type="primary", key="run_plan_b"):

        # ── Initial plan ─────────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### 📋 Phase 1 -- INITIAL PLAN")
            with st.spinner("Writing initial plan..."):
                try:
                    plan_b = llm_json(PLANNER_SYS, f"Task: {task_b}")
                except Exception as e:
                    st.error(f"Plan failed: {e}")
                    st.stop()

            st.success(f"**Goal:** {plan_b.get('goal', '')}")
            for s in plan_b.get("steps", []):
                st.markdown(f"- **Step {s['step']}:** {s['description']}")

        # ── Execute with replanning ───────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### ⚡ Phase 2 -- EXECUTE (with adaptive replanning)")

            completed_b = []
            steps_b = plan_b.get("steps", [])
            replan_count = 0

            for i, s in enumerate(steps_b):
                with st.container(border=True):
                    st.markdown(f"**Step {s['step']}: {s['description']}**")

                    tool_result_b = ""
                    if s.get("tool") and s["tool"] != "none":
                        with st.spinner(f"Tool: {s['tool']}..."):
                            tool_result_b = call_tool(s["tool"], s.get("tool_args", {}))
                        st.code(f"{s['tool']}({s.get('tool_args',{})})\n-> {tool_result_b[:200]}", language="text")

                    exec_user_b = f"""Goal: {plan_b['goal']}
Full plan: {json.dumps(steps_b, indent=2)}
Completed: {json.dumps(completed_b, indent=2)}
Current step {s['step']}: {s['description']}
Tool result: {tool_result_b if tool_result_b else 'No tool used.'}

IMPORTANT: If this step reveals information that changes what the REMAINING steps should do,
set needs_replan=true and explain why in replan_reason.
Return JSON."""

                    with st.spinner(f"Executing step {s['step']}..."):
                        try:
                            result_b = llm_json(EXECUTOR_SYS, exec_user_b)
                        except Exception as e:
                            result_b = {"step": s["step"], "result": f"Error: {e}",
                                       "key_facts": [], "needs_replan": False}

                    st.info(result_b.get("result", ""))
                    for fact in result_b.get("key_facts", []):
                        st.caption(f"✨ {fact}")
                    completed_b.append(result_b)

                    # ── REPLAN if needed ──────────────────────────────────────
                    if result_b.get("needs_replan") and i < len(steps_b) - 1:
                        replan_count += 1
                        st.warning(
                            f"🔄 **REPLAN TRIGGERED:** {result_b.get('replan_reason', '')}\n\n"
                            "Agent is revising remaining steps..."
                        )
                        replan_user = f"""Original goal: {plan_b['goal']}
Completed steps: {json.dumps(completed_b, indent=2)}
Remaining original steps: {json.dumps(steps_b[i+1:], indent=2)}
Reason for replanning: {result_b.get('replan_reason', '')}

Revise the remaining steps to account for this new information.
Return JSON array of revised steps (same format)."""
                        with st.spinner("Replanning remaining steps..."):
                            try:
                                new_steps = llm_json(REPLANNER_SYS, replan_user)
                                if isinstance(new_steps, list):
                                    steps_b = steps_b[:i+1] + new_steps
                                    st.success(f"✅ Plan revised -- {len(new_steps)} new remaining steps:")
                                    for ns in new_steps:
                                        st.markdown(f"  - **Step {ns.get('step','?')}:** {ns.get('description','')}")
                            except Exception as e:
                                st.error(f"Replanning failed: {e}")

        # ── Synthesize ────────────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### ? Phase 3 -- FINAL ANSWER")
            synth_b = (
                f"Goal: {plan_b['goal']}\n\n"
                f"Step results (plan was revised {replan_count} time(s)):\n"
                f"{json.dumps(completed_b, indent=2)}"
            )
            with st.spinner("Synthesizing..."):
                final_b = llm_text(SYNTHESIZER_SYS, synth_b)
            st.success(final_b)
            st.caption(f"Plan was revised {replan_count} time(s) during execution.")

        with st.expander("🔍 What just happened -- Adaptive Replanning"):
            st.markdown(f"""
| Event | Detail |
|---|---|
| Initial steps | {len(plan_b.get('steps', []))} |
| Replan triggers | {replan_count} |
| Steps completed | {len(completed_b)} |

**Why replanning matters:**
A fixed plan (like Phase 2d Orchestrator-Workers) would have continued with the original steps
even after a step revealed that they are no longer appropriate.
Adaptive replanning makes the agent responsive to what it discovers mid-task.
""")

st.markdown("---")
st.markdown("### What's next -> Phase 3d: Code Execution Tool")
st.markdown(
    "Andrew Ng Pattern 2 extension: the agent's 'tools' include a **Python REPL** -- "
    "it writes code, executes it, reads the output, and iterates. "
    "Closes the loop from Reflection Variant B with the full agent pattern."
)
