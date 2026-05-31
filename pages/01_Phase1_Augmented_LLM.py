"""
Phase 1 — The Augmented LLM
Four progressive demos: plain call → + memory → + tools → mini agent
"""

import streamlit as st
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call   # retry wrapper — handles 503 silently

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="Phase 1 — Augmented LLM", page_icon="🧠", layout="wide")
st.title("🧠 Phase 1 — The Augmented LLM")
st.caption("The foundational building block of every agentic system — *Building blocks, workflows, and agents* (Anthropic article §3)")

if not api_key:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

with st.expander("📐 Evolution Overview — all 4 stages at a glance"):
    st.markdown("""
    > *"The basic building block of agentic systems is an LLM enhanced with augmentations
    > such as retrieval, tools, and memory."*
    > — Anthropic, Building Effective Agents
    """)
    from utils.diagrams import diagram_overview
    st.image(diagram_overview(), use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "1a — Plain LLM",
    "1b — + Memory",
    "1c — + Tools",
    "1d — Mini Agent ⚡",
])


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1a — Plain LLM
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("1a — Plain LLM Call")
    from utils.diagrams import diagram_1a
    st.image(diagram_1a(), use_container_width=True)
    st.markdown("""
    The simplest possible call: **one message in, one reply out**.
    No history. No tools. The model answers from its training data alone.
    """)

    prompt_1a = st.text_input(
        "Message:",
        value="Explain what a large language model is in 2 sentences.",
        key="prompt_1a",
    )

    if st.button("Send", key="send_1a", type="primary"):
        with st.spinner("Calling Gemini 2.5 Flash..."):
            try:
                response = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=prompt_1a,
                )
                st.markdown("**Reply:**")
                st.info(response.text)

                with st.expander("🔍 Code + Key Limitation"):
                    st.code(
                        '''from google import genai

client = genai.Client(api_key=YOUR_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here",
)
print(response.text)
''',
                        language="python",
                    )
                    st.warning(
                        "**Limitation:** Ask a follow-up question in a new call "
                        "and the model won't remember this answer. "
                        "Every call is stateless. → Fix: **Memory (tab 1b)**"
                    )
            except Exception as e:
                st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1b — + Memory
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("1b — + Memory (Conversation History)")
    from utils.diagrams import diagram_1b
    st.image(diagram_1b(), use_container_width=True)
    st.markdown("""
    We pass the **entire conversation history** on every call.
    The model can now refer back to anything said earlier.

    > The model has no real memory — we *simulate* it by replaying the history each time.
    > This is called **context-window memory**, the simplest memory pattern.
    """)

    if "history_1b" not in st.session_state:
        st.session_state.history_1b = []  # list of {"role": "user"/"model", "parts": "text"}

    for turn in st.session_state.history_1b:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.write(turn["parts"])

    if not st.session_state.history_1b:
        st.info(
            "**Try this:** Ask *'What is the capital of France?'* "
            "then ask *'What language do they speak there?'* — "
            "the second question has no context on its own."
        )

    user_input = st.chat_input("Type a message…", key="chat_1b")

    def _to_sdk_history(history: list[dict]) -> list[dict]:
        """Convert simple {role, parts: str} dicts to SDK-expected {role, parts: [str]} format."""
        return [{"role": t["role"], "parts": [{"text": t["parts"]}]} for t in history]

    if user_input:
        st.session_state.history_1b.append({"role": "user", "parts": user_input})
        with st.spinner("Calling Gemini with full history…"):
            try:
                # history = all turns except the one we're sending now
                convo = client.chats.create(
                    model=MODEL,
                    history=_to_sdk_history(st.session_state.history_1b[:-1]),
                )
                response = _call(convo.send_message, user_input)
                st.session_state.history_1b.append(
                    {"role": "model", "parts": response.text}
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.history_1b:
        _, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Clear chat", key="clear_1b"):
                st.session_state.history_1b = []
                st.rerun()

        with st.expander("🔍 What's actually being sent to the model each turn"):
            st.json(st.session_state.history_1b)
            st.markdown("""
**Key insight:** The `history` list grows with every turn.
You are paying for those tokens on every request — this is the cost of memory.
In production agents, memory systems summarise or compress old turns to manage this.
""")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1c — + Memory + Tools  (diagram and code in sync)
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("1c — + Memory + Tools")
    from utils.diagrams import diagram_1c
    st.image(diagram_1c(), use_container_width=True)
    st.markdown("""
    Builds on 1b: conversation history is sent with **every request** (memory) AND
    the model picks the right real-time tool for each question.
    If no tool applies — it cracks a joke as a fallback.
    """)
    st.warning(
        "**⚠️ 1c architectural rule — ONE tool call per message.**\n\n"
        "In a real Augmented LLM workflow, **your code** orchestrates the steps. "
        "The model calls at most one tool, returns the result, and waits for **you** "
        "to decide what to ask next.\n\n"
        "For multi-step tasks (e.g. weather → check humidity → get holidays → multiply), "
        "you must send **separate follow-up messages** — one step at a time.\n\n"
        "👉 Compare this with **tab 1d** where the agent handles the entire chain in one goal."
    )

    # ── Tool palette ─────────────────────────────────────────────────────────
    st.markdown("#### 🧰 Available Tools")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.info("**🌤 get_weather(city)**\nLive weather via Open-Meteo\n*(no API key)*")
        st.info("**🌍 get_country_info(country)**\nCapital, population, currency\n*(REST Countries)*")
    with tc2:
        st.info("**📈 get_stock_price(ticker)**\nLive price via Yahoo Finance\n*(no API key)*")
        st.info("**🎉 get_public_holidays(code, year)**\nHolidays by country code\n*(Nager Date API)*")
    with tc3:
        st.info("**📐 convert_units(value, from, to)**\nVolume · Length · Weight\n*(pure Python)*")
        st.warning("**😂 get_random_joke()**\nFallback — fires when no tool matches")

    st.markdown("---")

    from utils.tools import (
        get_weather, get_stock_price, convert_units,
        get_country_info, get_public_holidays, get_random_joke,
    )

    TOOL_MAP = {
        "get_weather":         get_weather,
        "get_stock_price":     get_stock_price,
        "convert_units":       convert_units,
        "get_country_info":    get_country_info,
        "get_public_holidays": get_public_holidays,
    }

    # ── Persistent memory — same pattern as 1b ────────────────────────────────
    # sdk_history  = full history including tool call/response parts (sent to API)
    # disp_history = user messages + model text replies only (shown in UI)
    if "sdk_history_1c"  not in st.session_state:
        st.session_state.sdk_history_1c  = []
    if "disp_history_1c" not in st.session_state:
        st.session_state.disp_history_1c = []

    # ── Show conversation so far ──────────────────────────────────────────────
    for turn in st.session_state.disp_history_1c:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.write(turn["text"])
            if turn["role"] == "model" and turn.get("used_tool"):
                st.caption(f"✅ Step 1 real tool: `{turn['used_tool']}` | ⚠️ remaining steps from training data")
            elif turn["role"] == "model":
                st.caption("⚠️ No tool used — answered entirely from training data")

    if not st.session_state.disp_history_1c:
        st.info(
            "**Try a multi-turn conversation:** Ask the weather in Tokyo, "
            "then ask *'Is that hotter or cooler than London?'* — "
            "the model remembers the Tokyo answer."
        )

    prompt_1c = st.chat_input(
        "Ask anything — model picks the tool and remembers context…",
        key="chat_1c",
    )

    if prompt_1c:
        st.session_state.disp_history_1c.append({"role": "user", "text": prompt_1c})

        with st.spinner("Calling Gemini with memory + tools…"):
            try:
                config = types.GenerateContentConfig(
                    tools=list(TOOL_MAP.values()),
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                    system_instruction=(
                        "You are a helpful assistant with memory and real-time tools. "
                        "Use the appropriate tool for weather, stocks, unit conversion, "
                        "country info, or public holidays. "
                        "Only answer directly if no tool applies."
                    ),
                )
                # ── Pass full history so model remembers previous turns ───────
                convo = client.chats.create(
                    model=MODEL,
                    history=st.session_state.sdk_history_1c,
                    config=config,
                )
                response = _call(convo.send_message, prompt_1c)

                # ── ONE tool call only — YOU orchestrate the next step ────────
                # This is what distinguishes 1c (workflow) from 1d (agent).
                # An agent loops autonomously; a workflow stops and waits for you.
                tool_steps = []
                for _ in range(1):   # hard cap: one tool call per message
                    if not response.function_calls:
                        break
                    fc     = response.function_calls[0]
                    args   = dict(fc.args)
                    fn     = TOOL_MAP.get(fc.name)
                    result = fn(**args) if fn else f"Unknown tool: {fc.name}"
                    tool_steps.append({"name": fc.name, "args": args, "result": result})
                    response = _call(
                        convo.send_message,
                        types.Part.from_function_response(
                            name=fc.name, response={"result": result}
                        ),
                    )

                final_text = response.text

                # ── Save full SDK history (includes tool call parts) ──────────
                st.session_state.sdk_history_1c = convo.get_history()
                used_tool = tool_steps[0]["name"] if tool_steps else None
                st.session_state.disp_history_1c.append(
                    {"role": "model", "text": final_text, "used_tool": used_tool}
                )

                # ── Show this turn's tool activity ────────────────────────────
                if tool_steps:
                    step = tool_steps[0]
                    st.success(f"🔧 **Real Tool Called:** `{step['name']}` *(live data — verified)*")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Arguments sent:**")
                        st.code(
                            "\n".join(f"{k} = {v!r}" for k, v in step["args"].items()),
                            language="python",
                        )
                    with c2:
                        st.markdown("**Real data returned:**")
                        st.code(step["result"])

                    st.error(
                        "⚠️ **Only the step above used a real tool.**\n\n"
                        "Everything else in the model's reply below — the even/odd check, "
                        "public holidays, population, multiplication — came from the model's "
                        "**training data, not real tools**. It may be incorrect or outdated.\n\n"
                        "This is the 1c limitation: **your code called ONE tool then stopped.** "
                        "The model filled in the rest from memory.\n\n"
                        "👉 In **tab 1d**, every step above would be a verified real tool call."
                    )
                else:
                    joke = get_random_joke()
                    st.warning("No tool matched — joke fallback fired 😂")
                    setup, *punchline = joke.split("\n...")
                    st.markdown(f"> {setup}")
                    st.markdown(f"> **{('...'.join(punchline)).strip()}**")

                st.rerun()

            except Exception as e:
                st.session_state.disp_history_1c.pop()   # remove unsent user msg
                st.error(f"Error: {e}")

    # ── Controls ──────────────────────────────────────────────────────────────
    if st.session_state.disp_history_1c:
        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Clear chat", key="clear_1c"):
                st.session_state.sdk_history_1c  = []
                st.session_state.disp_history_1c = []
                st.rerun()
        with st.expander("🔍 What's being sent to the model — full SDK history"):
            st.caption("Includes user turns, tool call parts, tool response parts, model replies")
            st.json([str(h) for h in st.session_state.sdk_history_1c])

    with st.expander("🔍 Key insight — Memory + Tools combined"):
        st.markdown("""
- **Memory** (from 1b): full SDK history passed on every call — model remembers context
- **Tools**: model decides which tool to call; your code executes it
- **Two separate histories**: `sdk_history` (full, sent to API) and `disp_history` (text only, shown in UI)
- **Fallback**: if no tool fires → `get_random_joke()` runs directly from your code

This is the complete **Augmented LLM** — memory + tools working together.
""")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1d — Mini Agent
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("1d — Mini Agent ⚡")
    from utils.diagrams import diagram_1d
    st.image(diagram_1d(), use_container_width=True)
    st.markdown("""
    **What makes something an *agent* rather than a single tool call?**

    An agent runs a **loop**: think → act → observe the result → think again —
    until *the model itself* decides it's done.

    This mini agent has two tools and a goal. Watch it reason through multiple steps autonomously.
    """)

    with st.expander("📐 The Agent Loop"):
        st.code(
            """# The core pattern — every agent is this loop

response = model.send_message(goal)

while response has a tool call:
    tool, args = extract_tool_call(response)
    result      = execute(tool, args)          # your code runs this
    response    = model.send_message(result)   # model sees the result

final_answer = response.text                   # model decided to stop
""",
            language="python",
        )
        st.markdown("""
**Workflow vs Agent — the key difference:**
- **Workflow:** *your code* decides what happens next (fixed path)
- **Agent:** *the model* decides what happens next (dynamic path)
""")

    def calculator(a: float, b: float, operation: str) -> float:
        """
        Perform basic arithmetic on two numbers.

        Args:
            a: First number
            b: Second number
            operation: One of 'add', 'subtract', 'multiply', 'divide'
        """
        ops = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else float("nan"),
        }
        return ops.get(operation, 0.0)

    def check_even_odd(number: float) -> str:
        """
        Determine whether a number is even or odd.

        Args:
            number: The integer to classify
        """
        return "even" if int(number) % 2 == 0 else "odd"

    from utils.tools import (
        get_weather, get_stock_price, convert_units,
        get_country_info, get_public_holidays, get_random_joke,
    )

    # ── Tool palette ──────────────────────────────────────────────────────────
    st.markdown("#### 🧰 All Tools Available to the Agent")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.info("**🔢 calculator**\nArithmetic (add/sub/mul/div)")
        st.info("**🌤 get_weather**\nLive weather by city")
    with p2:
        st.info("**🔢 check_even_odd**\nClassify a number")
        st.info("**📈 get_stock_price**\nLive stock price")
    with p3:
        st.info("**🌍 get_country_info**\nCapital, population, currency")
        st.info("**📐 convert_units**\nVolume · Length · Weight")
    with p4:
        st.info("**🎉 get_public_holidays**\nHolidays by country & year")
        st.warning("**😂 get_random_joke**\nFallback if no tool fits")

    # ── Persistent memory — same two-history pattern as 1c ───────────────────
    if "sdk_history_1d"  not in st.session_state:
        st.session_state.sdk_history_1d  = []
    if "disp_history_1d" not in st.session_state:
        st.session_state.disp_history_1d = []

    # ── Show conversation so far ──────────────────────────────────────────────
    for turn in st.session_state.disp_history_1d:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.write(turn["text"])

    if not st.session_state.disp_history_1d:
        st.info(
            "**Memory is active across runs.** Ask a follow-up like "
            "*'What is the weather in Tokyo?'* then *'Is that hotter than Chennai?'* "
            "— the agent remembers the Tokyo answer."
        )

    goal = st.text_input(
        "Agent goal — ask anything, the agent picks and chains tools:",
        value="What is 42 multiplied by 38, and is that result even or odd?",
        key="goal_1d",
    )
    st.caption(
        "Try multi-tool goals: "
        "*'What's the weather in Chennai and convert 30°C to Fahrenheit?'* · "
        "*'Tell me about Japan and its public holidays in 2026'* · "
        "*'What is TSLA stock price and is that number even or odd?'* · "
        "*'What is 42×38 and is it even or odd?'*"
    )

    if st.button("Run Agent", key="run_1d", type="primary"):
        with st.spinner("Agent thinking — may chain multiple tools…"):
            try:
                ALL_TOOLS = [
                    calculator, check_even_odd,
                    get_weather, get_stock_price, convert_units,
                    get_country_info, get_public_holidays,
                ]
                config = types.GenerateContentConfig(
                    tools=ALL_TOOLS,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True   # manual loop so every step is visible
                    ),
                    system_instruction=(
                        "You are a helpful agent with access to real-time tools and memory. "
                        "Always use tools to answer — never guess or answer from memory. "
                        "Chain multiple tool calls if the goal requires it. "
                        "For arithmetic always use calculator. "
                        "For weather always use get_weather. "
                        "Decide each next step based on what you have learned so far."
                    ),
                )
                # ── Pass full history so agent remembers previous runs ─────────
                convo = client.chats.create(
                    model=MODEL,
                    history=st.session_state.sdk_history_1d,
                    config=config,
                )
                response = _call(convo.send_message, goal)

                tool_map = {
                    "calculator":          calculator,
                    "check_even_odd":      check_even_odd,
                    "get_weather":         get_weather,
                    "get_stock_price":     get_stock_price,
                    "convert_units":       convert_units,
                    "get_country_info":    get_country_info,
                    "get_public_holidays": get_public_holidays,
                }
                steps = []
                MAX_STEPS = 8

                for _ in range(MAX_STEPS):
                    if not response.function_calls:
                        steps.append({"type": "final", "text": response.text})
                        break

                    fc = response.function_calls[0]
                    args = dict(fc.args)
                    result = tool_map.get(fc.name, lambda **_: "unknown tool")(**args)

                    steps.append({
                        "type": "tool",
                        "name": fc.name,
                        "args": args,
                        "result": result,
                    })

                    response = _call(
                        convo.send_message,
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"result": str(result)},
                        )
                    )

                # Display the loop steps
                st.markdown("### Agent Loop — Step by Step")
                st.markdown("---")

                tool_count = sum(1 for s in steps if s["type"] == "tool")

                if tool_count == 0:
                    # No tools called — model answered from training data
                    joke = get_random_joke()
                    st.info(
                        "**No tool was called.** The agent answered from training data "
                        "(answer may be outdated or approximate). "
                        "Since no real-time tool was used, here's your consolation joke 😂"
                    )
                    final_step = next((s for s in steps if s["type"] == "final"), None)
                    if final_step:
                        st.markdown("**Agent's answer (from training data — not live):**")
                        st.warning(final_step["text"])
                    st.markdown("---")
                    st.markdown("**😂 Joke Fallback:**")
                    setup, *punchline = joke.split("\n...")
                    st.markdown(f"> {setup}")
                    st.markdown(f"> **{('...'.join(punchline)).strip()}**")
                else:
                    for i, step in enumerate(steps, start=1):
                        if step["type"] == "tool":
                            st.success(
                                f"**🤖 Agent decided — Step {i}: call `{step['name']}`** "
                                f"*(model chose this tool autonomously — live data)*"
                            )
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("**Arguments the agent sent:**")
                                st.code(
                                    "\n".join(f"{k} = {v!r}" for k, v in step["args"].items()),
                                    language="python",
                                )
                            with c2:
                                st.markdown("**Real data returned:**")
                                st.code(step["result"])
                            if i < tool_count:
                                st.caption(
                                    f"↓ Agent observed the result above and decided to call the next tool…"
                                )
                        else:
                            st.markdown(f"**🤖 Agent decided — Step {i}: done. Final Answer.**")
                            st.info(step["text"])

                # ── Save history so next run has full context ─────────────────
                final_text = next(
                    (s["text"] for s in steps if s["type"] == "final"), ""
                )
                st.session_state.sdk_history_1d  = convo.get_history()
                st.session_state.disp_history_1d.append(
                    {"role": "user",  "text": goal}
                )
                st.session_state.disp_history_1d.append(
                    {"role": "model", "text": final_text}
                )

                st.markdown("---")
                st.caption(
                    f"Agent completed in {len(steps)} steps "
                    f"({tool_count} real tool call(s) + 1 final answer). "
                    f"History now has {len(st.session_state.sdk_history_1d)} turns."
                )

            except Exception as e:
                st.error(f"Error: {e}")

    # ── Controls ──────────────────────────────────────────────────────────────
    if st.session_state.disp_history_1d:
        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Clear history", key="clear_1d"):
                st.session_state.sdk_history_1d  = []
                st.session_state.disp_history_1d = []
                st.rerun()
        with st.expander("🔍 Full SDK history sent to agent each run"):
            st.caption("Includes user goals, tool call parts, tool response parts, model replies")
            st.json([str(h) for h in st.session_state.sdk_history_1d])


# ── What's next ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### What's next → Phase 2: Workflow Patterns")
st.markdown(
    "Now that you understand the building block, we'll compose it into patterns: "
    "**Chaining → Routing → Parallelization → Orchestrator-Workers → Evaluator-Optimizer**"
)
