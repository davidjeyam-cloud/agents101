"""
Phase 3 — Autonomous Agent (ReAct pattern)
Model controls its own Think → Act → Observe loop.
No predefined structure — model decides every next step.
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

st.set_page_config(page_title="Phase 3 — Autonomous Agent", page_icon="🤖", layout="wide")
st.title("🤖 Phase 3 — Autonomous Agent")
st.caption("This is where Agentic AI begins — the model controls its own process")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_3
st.image(diagram_3(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is an Autonomous Agent — how is Phase 3 different from everything before?"):
    st.markdown("""
    > *"Agents are systems where LLMs dynamically direct their own processes and tool usage,
    > maintaining control over how they accomplish tasks."*
    > — Anthropic, Building Effective Agents

    **The fundamental shift:**

    | Phase 2 (Workflows) | Phase 3 (Agent) |
    |---|---|
    | YOU define the structure | Model defines the structure |
    | Fixed number of steps | Variable steps until model decides done |
    | Model only processes its assigned step | Model decides what step comes next |
    | Can't adapt to unexpected results | Adapts at each step based on observations |

    **The ReAct pattern (Reason + Act):**

    At every step, the agent:
    1. **Think** — reasons about what to do next given what it knows so far
    2. **Act** — calls a tool (or decides it's done)
    3. **Observe** — reads the result and updates its understanding
    4. **Repeat** — back to Think with new information

    **What's new vs 1d (mini-agent):**
    - Full tool set (7 tools, not 2)
    - Explicit visible reasoning trace (Thought shown at each step)
    - Model handles goals that require unpredictable sequences
    - The model can choose NOT to call a tool and still answer

    **Human-in-the-loop interrupt:**
    The slider lets you set max steps — a safety valve that prevents runaway loops.
    In production agents, human oversight checkpoints are critical.
    """)

with st.expander("📐 Core Code Pattern — ReAct Agent Loop"):
    st.code('''
# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
# Tell the model to output JSON with thought + action + done flag
SYSTEM = """
At every step output ONLY valid JSON:

To call a tool:
{"thought": "your reasoning", "action": "tool_name", "args": {...}, "done": false}

When goal is fully achieved:
{"thought": "I have everything needed", "done": true, "answer": "full answer here"}
"""

# ── AGENT LOOP ────────────────────────────────────────────────────────────────
convo    = client.chats.create(model=MODEL, config=GenerateContentConfig(
               system_instruction=SYSTEM, response_mime_type="application/json"))
response = convo.send_message(f"Goal: {goal}")

for step in range(max_steps):           # safety limit — human oversight
    data = json.loads(response.text)

    thought = data["thought"]           # ① model reasons about next step

    if data["done"]:                    # ③ model decided goal is achieved
        return data["answer"]

    action = data["action"]             # ② model chose a tool
    args   = data["args"]
    result = execute_tool(action, args) # YOUR code runs it — not the model

    # model observes result and decides next step
    response = convo.send_message(f"Tool result: {result}. Continue:")
''', language="python")
    st.markdown("""
**What makes this an Agent (not a Workflow):**
- The model writes the JSON at **every step** — it decides which tool, what args, and when to stop
- Your code only executes what the model requested — the model cannot run code directly
- The model can chain **any number of tools in any order** — no structure predefined by you
- `max_steps` is your safety valve — the only structure you control

**Why JSON format?** — Makes the model's reasoning explicit and parseable.
The `thought` field is the model's internal reasoning — this is the "Reason" in ReAct.
""")

st.markdown("---")

# ── Tools ─────────────────────────────────────────────────────────────────────

def calculator(a: float, b: float, operation: str) -> float:
    """Perform arithmetic. Args: a, b: numbers, operation: add/subtract/multiply/divide"""
    ops = {"add": a+b, "subtract": a-b, "multiply": a*b,
           "divide": a/b if b else float("nan")}
    return ops.get(operation, 0.0)

def check_even_odd(number: float) -> str:
    """Check if number is even or odd. Args: number: the integer to check"""
    return "even" if int(number) % 2 == 0 else "odd"

from utils.tools import (
    get_weather, get_stock_price, convert_units,
    get_country_info, get_public_holidays,
)

TOOL_MAP = {
    "get_weather":         get_weather,
    "get_stock_price":     get_stock_price,
    "convert_units":       convert_units,
    "get_country_info":    get_country_info,
    "get_public_holidays": get_public_holidays,
    "calculator":          calculator,
    "check_even_odd":      check_even_odd,
}

TOOL_ICONS = {
    "get_weather":         "🌤",
    "get_stock_price":     "📈",
    "convert_units":       "📐",
    "get_country_info":    "🌍",
    "get_public_holidays": "🎉",
    "calculator":          "🔢",
    "check_even_odd":      "🔢",
}

TOOL_DESCRIPTIONS = "\n".join([
    "- get_weather(city)                              → live weather (temp, humidity, wind)",
    "- get_stock_price(ticker)                        → live stock price + % change",
    "- convert_units(value, from_unit, to_unit)       → volume / length / weight conversion",
    "- get_country_info(country_name)                 → capital, population, currency, languages",
    "- get_public_holidays(country_code, year)        → list of holidays (e.g. 'GB', 2026)",
    "- calculator(a, b, operation)                    → add / subtract / multiply / divide",
    "- check_even_odd(number)                         → returns 'even' or 'odd'",
])

AGENT_SYSTEM = f"""You are an autonomous agent. Achieve the given goal step by step using tools.

{TOOL_DESCRIPTIONS}

At every step output ONLY valid JSON — no markdown, no extra text.

To call a tool:
{{"thought": "your reasoning about what to do next and why", "action": "tool_name", "args": {{"param": "value"}}, "done": false}}

When the goal is fully achieved:
{{"thought": "I have all the information needed to answer fully", "done": true, "answer": "your complete, detailed final answer"}}

Rules:
- ALWAYS use tools for live data — never answer from training memory
- Reason step by step in "thought" before acting
- Keep going until every part of the goal is addressed
- Only set done=true when you have a complete answer
"""


def execute_tool(name: str, args: dict) -> str:
    fn = TOOL_MAP.get(name)
    if not fn:
        return f"Unknown tool '{name}'. Available: {', '.join(TOOL_MAP)}"
    try:
        result = fn(**{str(k): v for k, v in args.items()})
        return str(result)
    except TypeError as e:
        return f"Wrong arguments for {name}: {e}"
    except Exception as e:
        return f"Tool error: {e}"


def run_agent(goal: str, max_steps: int) -> list[dict]:
    """Run the ReAct agent loop. Returns list of trace steps."""
    steps = []
    convo = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=AGENT_SYSTEM,
            response_mime_type="application/json",
        ),
    )

    response = _call(convo.send_message, f"Goal: {goal}")

    for _ in range(max_steps):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            steps.append({"type": "error", "content": f"JSON parse error: {response.text[:200]}"})
            break

        thought = data.get("thought", "")
        steps.append({"type": "thought", "content": thought})

        if data.get("done"):
            steps.append({"type": "answer", "content": data.get("answer", "Done.")})
            break

        action = data.get("action", "")
        args   = data.get("args", {})

        if not action:
            steps.append({"type": "error", "content": "Model returned done=false but no action."})
            break

        result = execute_tool(action, args)
        steps.append({"type": "action", "name": action, "args": args, "result": result})

        response = _call(
            convo.send_message,
            f"Tool result: {result}\n\nContinue with the goal:"
        )

    else:
        steps.append({
            "type": "error",
            "content": f"Max steps ({max_steps}) reached — agent stopped by safety limit."
        })

    return steps


# ── Tool palette ───────────────────────────────────────────────────────────────
st.markdown("#### 🧰 Agent's Tool Belt — 7 real tools")
tc = st.columns(7)
labels = [
    ("🌤", "get_weather", "city"),
    ("📈", "get_stock_price", "ticker"),
    ("📐", "convert_units", "value, from, to"),
    ("🌍", "get_country_info", "country"),
    ("🎉", "get_public_holidays", "code, year"),
    ("🔢", "calculator", "a, b, op"),
    ("🔢", "check_even_odd", "number"),
]
for col, (icon, name, sig) in zip(tc, labels):
    col.info(f"**{icon}**\n`{name}`\n({sig})")

st.markdown("---")

# ── UI ─────────────────────────────────────────────────────────────────────────

GOAL_EXAMPLES = {
    "Weather + convert":
        "What is the current weather in Tokyo? Convert the temperature to Fahrenheit, "
        "then check if the rounded temperature (in Fahrenheit) is even or odd.",

    "Country deep-dive":
        "Get information about Australia. Find all public holidays in Australia for 2026. "
        "Calculate how many holidays there are per 10 million population. Round to 2 decimal places.",

    "Stock comparison":
        "Get the current stock prices for AAPL and MSFT. "
        "Calculate the difference between the two prices. "
        "Then tell me which is more expensive and by how much.",

    "Multi-country":
        "Get the weather in London and Paris right now. "
        "Which city is warmer? By how many degrees Celsius? "
        "Also tell me the capital and population of both countries.",
}

if "sel_3" not in st.session_state:
    st.session_state.sel_3 = GOAL_EXAMPLES["Weather + convert"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Goal examples:**")
    for label, text in GOAL_EXAMPLES.items():
        if st.button(label, key=f"ex3_{label}"):
            st.session_state.sel_3 = text
            st.rerun()
    st.markdown("---")
    max_steps = st.slider("Max steps (safety limit):", 3, 12, 8, key="maxsteps_3")
    st.caption("Agent stops automatically at this limit — human oversight.")

with col1:
    goal = st.text_area(
        "Agent goal (give it a complex, multi-step task):",
        value=st.session_state.sel_3,
        height=120,
    )

st.markdown("---")

if st.button("▶  Run Agent", type="primary", key="run_3"):

    if not goal.strip():
        st.warning("Please enter a goal.")
        st.stop()

    st.markdown("### 🤖 Agent Running — ReAct Trace")
    st.caption(
        "Watch the agent Think → Act → Observe at each step. "
        "It decides every action — you gave it only the goal."
    )
    st.markdown("---")

    with st.spinner("Agent running autonomously…"):
        steps = run_agent(goal, max_steps)

    tool_count    = sum(1 for s in steps if s["type"] == "action")
    thought_count = sum(1 for s in steps if s["type"] == "thought")

    for i, step in enumerate(steps):

        if step["type"] == "thought":
            with st.container():
                st.markdown(
                    f"<div style='background:#EBF5FB;padding:10px 14px;"
                    f"border-left:4px solid #2471A3;border-radius:4px;margin:4px 0'>"
                    f"<b>💭 Thought {thought_count - sum(1 for s in steps[:i] if s['type']=='thought') + 1 - thought_count + sum(1 for s in steps[:i+1] if s['type']=='thought')}</b><br>"
                    f"{step['content']}</div>",
                    unsafe_allow_html=True,
                )

        elif step["type"] == "action":
            icon = TOOL_ICONS.get(step["name"], "🔧")
            st.success(
                f"**{icon} Action: `{step['name']}`**  *(live data — not from training)*"
            )
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Args sent:**")
                st.code("\n".join(f"{k} = {v!r}" for k, v in step["args"].items()),
                        language="python")
            with c2:
                st.markdown("**Observation (tool result):**")
                st.code(step["result"])

        elif step["type"] == "answer":
            st.markdown("---")
            st.markdown("### ✅ Agent decided: Goal achieved")
            st.success(step["content"])

        elif step["type"] == "error":
            st.error(f"⚠️ {step['content']}")

    st.markdown("---")
    st.caption(
        f"Agent completed: {thought_count} thinking steps · "
        f"{tool_count} tool calls · "
        f"{'✅ answered' if any(s['type']=='answer' for s in steps) else '⚠️ stopped at limit'}"
    )

    with st.expander("🔍 The critical difference from Phase 2"):
        st.markdown(f"""
**You gave the agent one goal. It decided everything else.**

- Which tools to call: ✅ agent decided
- In what order: ✅ agent decided
- How many steps: ✅ agent decided ({thought_count} steps)
- When to stop: ✅ agent decided

**Compare to Phase 2d (Orchestrator-Workers):**
In 2d, the orchestrator planned ALL tasks upfront and workers executed them.
The plan didn't change after workers reported results.

In Phase 3, the agent reads each tool result and decides the NEXT step based on it.
If `get_weather` returned an unexpected value, the agent could adapt its next call.
That real-time adaptation is what makes this a true autonomous agent.

**What the safety limit does:**
Setting max_steps = {max_steps} means your code stops the agent after {max_steps} iterations.
In production agents, this is a critical safety mechanism.
Agents without limits can loop indefinitely or take unintended actions.
""")

    st.markdown("---")
    st.markdown("### 3a — ReAct Agent complete")
    st.markdown("### What's next → Phase 3b: Reflection Agent")
    st.markdown(
        "**3b — Reflection Agent:** The same LLM critiques and improves its own output — "
        "Andrew Ng Pattern #1, the most universally applicable agentic improvement loop.\n\n"
        "**Then Phase 3c — Planning Agent:** Explicit Plan-and-Execute before acting — "
        "the complete software development agent from Appendix 1."
    )
