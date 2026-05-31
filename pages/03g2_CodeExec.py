"""
Phase 3d -- Code Execution Tool (Python REPL as agent tool)
Andrew Ng Pattern 2 extension: agent writes Python code, executes it, reads output, iterates.
run_python() is simply another tool in the ReAct toolbox.
"""

import streamlit as st
import os
import io
import json
import contextlib
import traceback
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 3d -- Code Execution", page_icon="🐍", layout="wide")
st.title("🐍 Phase 3d -- Code Execution Tool")
st.caption("Agent writes Python, executes it in a sandbox, reads the output, and iterates")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_code_exec
st.image(diagram_code_exec(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Code Execution as an agent tool?"):
    st.markdown("""
    > *"Tool use includes writing and executing code -- the agent can write a program,
    > run it, and use the output to continue reasoning."*
    > -- Andrew Ng, DeepLearning.AI Agentic AI Course

    **Key insight:** `run_python()` is just another entry in the agent's tool list.
    The ReAct loop from Phase 3a is unchanged -- except one tool now executes code.

    | Tool | What it does |
    |---|---|
    | `get_weather(city)` | Returns live weather data |
    | `get_country_info(country)` | Returns country facts |
    | **`run_python(code)`** | **Executes Python and returns stdout** |

    **Why code execution unlocks a new class of tasks:**

    | Without code execution | With code execution |
    |---|---|
    | LLM must approximate arithmetic | Exact calculation via Python |
    | No data manipulation | Can sort, filter, transform data |
    | Reflection Variant B tests were separate | Agent self-tests its own code |
    | Can only describe algorithms | Can write and run algorithms |

    **How it works:**
    1. Agent writes Python code as its "Act" step
    2. Code runs in `exec()` with stdout captured
    3. Output returned as tool result
    4. Agent observes output, continues reasoning
    5. Agent may write more code if needed (loop continues)

    **Connection to Phase 3b Reflection Variant B:**
    Variant B ran tests EXTERNALLY and fed failures back to the agent.
    Phase 3d puts the REPL *inside* the agent -- the agent decides when to run code and what to run.
    """)

with st.expander("📐 Core Code Pattern -- Code Execution Tool"):
    st.code('''
import io, contextlib

# ── The run_python tool ───────────────────────────────────────────────────────
def run_python(code: str) -> str:
    """Execute Python in a sandboxed namespace. Returns stdout or error."""
    namespace = {}
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured):
            exec(compile(code, "<agent_code>", "exec"), namespace)
        output = captured.getvalue()
        return output.strip() if output.strip() else "Executed (no output)"
    except Exception as e:
        return f"Error: {e}"

# ── Register as agent tool ────────────────────────────────────────────────────
def run_python_tool(code: str) -> str:
    """
    Execute Python code and return the printed output.
    Use print() to produce output. Import standard library modules as needed.
    Args:
        code: Python code. Use print() to show results.
    """
    return run_python(code)

# ── ReAct loop -- identical to Phase 3a, run_python is just another tool ─────
config = GenerateContentConfig(
    tools=[run_python_tool, get_weather, get_country_info],
    automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
    system_instruction="For calculations, ALWAYS write and run Python. Never approximate.",
)
convo = client.chats.create(model=MODEL, config=config)
response = convo.send_message(task)

while response.function_calls:
    fc = response.function_calls[0]
    if fc.name == "run_python_tool":
        result = run_python(fc.args["code"])   # sandboxed exec
    else:
        result = call_other_tool(fc.name, fc.args)

    response = convo.send_message(
        Part.from_function_response(name=fc.name, response={"result": result})
    )
# final response.text is the interpreted answer
''', language="python")
    st.markdown("""
**Why this beats asking the LLM to calculate:**
LLMs approximate arithmetic. Python is exact. For financial figures this matters --
a 0.1% error on a GBP 200,000 mortgage is GBP 200/year.

**Production note:** Always sandbox execution. Production systems use Docker containers
or cloud sandboxes (e.g. Google Code Execution API, E2B). Never give filesystem or
network access to agent-written code without explicit review -- connects to Phase 4b HITL.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Core sandbox
# ══════════════════════════════════════════════════════════════════════════════

def run_python(code: str) -> str:
    namespace = {"__builtins__": __builtins__}
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured):
            exec(compile(code, "<agent_code>", "exec"), namespace)
        output = captured.getvalue()
        return output.strip() if output.strip() else "Executed successfully (no print output)"
    except Exception:
        return f"Error:\n{traceback.format_exc(limit=3)}"


def run_python_tool(code: str) -> str:
    """
    Execute Python code in a sandbox and return the printed output.
    Use print() to show results. Standard library modules available.
    Do not use file I/O or network calls.

    Args:
        code: Python code string. Must use print() to produce visible output.
    """
    return run_python(code)


AGENT_SYSTEM = (
    "You are NexaBank's computational analysis agent. "
    "For ANY task involving calculations, comparisons, or financial projections, "
    "ALWAYS write and execute Python code to get exact answers -- never estimate mentally. "
    "Use print() to show your working and results. "
    "After running code, interpret the numbers and explain what they mean for the customer."
)

TASKS = {
    "Compound interest comparison":
        "Compare two NexaBank savings options for a customer with GBP 10,000 over 5 years:\n"
        "Option A: NexaSaver at 4.75% AER compounded annually\n"
        "Option B: NexaFlex ISA at 4.2% AER compounded annually (tax-free)\n"
        "The customer pays 20% income tax. Show year-by-year balances and which is better.",

    "Mortgage affordability calculator":
        "A customer earns GBP 52,000/year and wants a NexaBank mortgage.\n"
        "NexaBank lends up to 4.5x annual salary.\n"
        "Calculate: max loan size, monthly repayments for a GBP 200,000 loan "
        "on each NexaBank term (2yr fix 4.89% APRC, 5yr fix 4.65% APRC, 10yr fix 4.99% APRC), "
        "and total interest paid over each full term.",

    "Savings goal planner":
        "A customer wants GBP 25,000 for a house deposit in 3 years.\n"
        "They have GBP 8,000 now and can save GBP 500/month.\n"
        "NexaSaver: 4.75% AER compounded monthly.\n"
        "Will they reach the goal? If not, what monthly saving is required?",

    "Overdraft cost analysis":
        "A customer uses their NexaBank arranged overdraft: GBP 350 for 7 days, "
        "then GBP 200 for another 14 days. Rate: 39.9% EAR.\n"
        "Calculate exact interest cost for each period and total. "
        "Also show what the cost would be at 1, 2, 3, 6, and 12 months at GBP 350.",

    "ISA vs savings net return":
        "A higher-rate taxpayer (40%) has GBP 20,000 for 4 years.\n"
        "NexaSaver: 4.75% AER (interest taxed at 40%).\n"
        "NexaFlex ISA: 4.2% AER (fully tax-free).\n"
        "Calculate net annual returns for each, cumulative totals, and find the breakeven year.",
}

# ── UI ────────────────────────────────────────────────────────────────────────

if "sel_code" not in st.session_state:
    st.session_state.sel_code = list(TASKS.keys())[0]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Tasks:**")
    for label in TASKS:
        if st.button(label, key=f"ce_{label}"):
            st.session_state.sel_code = label
            st.rerun()
    st.markdown("---")
    max_steps = st.slider("Max code execution steps:", 2, 8, 5, key="ce_steps")
    show_raw = st.checkbox("Show raw code in trace", value=True)
with col1:
    task = st.text_area(
        "Computational task:",
        value=TASKS[st.session_state.sel_code],
        height=130,
    )

st.markdown("---")

if st.button("▶  Run Code Execution Agent", type="primary", key="run_ce"):

    if not task.strip():
        st.warning("Enter a task.")
        st.stop()

    config = types.GenerateContentConfig(
        tools=[run_python_tool],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        system_instruction=AGENT_SYSTEM,
    )
    convo = client.chats.create(model=MODEL, config=config)

    with st.spinner("Agent starting..."):
        response = _call(convo.send_message, task)

    steps_log = []
    step_count = 0

    st.markdown("### 🔬 Agent Execution Trace")
    st.markdown("---")

    while step_count < max_steps:
        if not response.function_calls:
            break

        fc = response.function_calls[0]
        code = fc.args.get("code", "")
        step_count += 1

        with st.container(border=True):
            st.markdown(f"#### 🐍 Step {step_count} -- Agent writes + runs Python")

            if show_raw:
                st.markdown("**Code written by agent:**")
                st.code(code, language="python")

            with st.spinner("Executing in sandbox..."):
                output = run_python(code)

            steps_log.append({"type": "code", "content": code})
            steps_log.append({"type": "output", "content": output})

            st.markdown("**Sandbox output:**")
            if "Error:" in output:
                st.error(output)
                st.caption("Agent will reflect on this error and try a fix.")
            else:
                st.success(output)
                st.caption("Agent observes this output and decides what to do next.")

        response = _call(
            convo.send_message,
            types.Part.from_function_response(
                name=fc.name, response={"result": output}
            ),
        )

    # ── Final answer ───────────────────────────────────────────────────────
    st.markdown("---")
    with st.container(border=True):
        st.markdown("#### ? Final Answer -- Agent Interpretation")
        st.caption("Agent explains what the numbers mean for the customer.")
        st.success(response.text)

    # ── Stats + trace ──────────────────────────────────────────────────────
    code_steps = [s for s in steps_log if s["type"] == "code"]
    error_outputs = [s for s in steps_log if s["type"] == "output" and "Error:" in s["content"]]

    with st.expander("🔍 What just happened -- Code Execution breakdown"):
        st.markdown(f"""
| Step | What happened | Count |
|---|---|---|
| **Code written** | Agent composed Python code | {len(code_steps)} |
| **Executions** | Sandbox ran exec() and captured stdout | {len(code_steps)} |
| **Errors encountered** | Code that produced an error (agent fixed) | {len(error_outputs)} |

**ReAct loop unchanged:** The agent used the exact same Think -> Act -> Observe loop as
Phase 3a. The only difference is `run_python_tool` is now in the tool list.

**Why exact calculation matters:**
LLMs hallucinate numbers. For GBP 200,000 mortgages over 25 years, even 0.1% errors
compound into thousands of pounds of wrong advice. Python gives exact IEEE 754 results.

**Connecting patterns:**
- Phase 3a (ReAct): same loop, different tools
- Phase 3b Variant B (Reflection): similar but code + tests run externally
- Phase 3c (Planning): can include a "run_python" step in the plan
""")

    with st.expander("🔬 Execution Trace -- all code blocks"):
        code_count = 0
        for s in steps_log:
            if s["type"] == "code":
                code_count += 1
                st.markdown(f"**Code block {code_count}:**")
                st.code(s["content"], language="python")
            elif s["type"] == "output":
                label = "❌ Output:" if "Error:" in s["content"] else "✅ Output:"
                st.markdown(f"**{label}**")
                if "Error:" in s["content"]:
                    st.error(s["content"])
                else:
                    st.info(s["content"])

st.markdown("---")
st.markdown("### What's next -> Phase 4a: Guardrails")
st.markdown(
    "Phase 3 (Core Agent Patterns) is now complete. "
    "Phase 4 adds safety and quality layers. "
    "**4a Guardrails:** input + output safety -- PII detection, prompt injection blocking, "
    "and financial compliance rules wrapping every agent response."
)
