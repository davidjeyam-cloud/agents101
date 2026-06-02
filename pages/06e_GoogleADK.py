"""
Phase 10e — Google ADK
Bridges Phases 2a (Sequential), 2c (Parallel), 3 (Loop), and 6a (Sub-agents)
to Google's Agent Development Kit.
"""
import os
import time
import concurrent.futures
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10e — Google ADK",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.diagrams import diagram_google_adk
from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🤖 10e — Google ADK")
st.caption(
    "Google's Agent Development Kit — SequentialAgent, ParallelAgent, and LoopAgent "
    "map directly to the workflow and agent patterns you built in Phases 2a, 2c, 3, and 6a."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(
    diagram_google_adk(),
    caption=(
        "Left: the raw Python patterns you built in Phases 2a, 2c, 3, and 6a. "
        "Right: ADK's typed agent classes that wrap those exact patterns."
    ),
    use_column_width=True,
)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 2a · 2c · 3 · 6a)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 2a you wrote <code>out2 = llm(prompt + out1)</code> — a sequential chain.<br>
    In Phase 2c you used <code>ThreadPoolExecutor</code> to run three LLM calls concurrently.<br>
    In Phase 3 you wrote <code>while not done: think → act → observe</code> — a reasoning loop.<br>
    In Phase 6a you delegated tasks from a root agent to specialist sub-agents.<br><br>
    Google ADK is those four patterns formalised as typed Python classes:
    <code>SequentialAgent</code>, <code>ParallelAgent</code>, <code>LoopAgent</code>, and
    composable <code>Agent</code> trees. The Runner handles execution and session management.
    <strong>Nothing is architecturally new — ADK is declarative syntax for patterns you already understand.</strong>
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept expander ──────────────────────────────────────────────────────────
with st.expander("📖 What is Google ADK — and what does it add over raw SDK?"):
    st.markdown("""
**Google ADK (Agent Development Kit)** is Google's open-source Python framework for composing
multi-agent systems. Released April 2025 alongside the A2A protocol.

| ADK Class | Phase Equivalent | What it adds over raw code |
|---|---|---|
| `SequentialAgent(sub_agents=[A,B,C])` | Phase 2a Prompt Chaining | Declarative, typed, re-runnable; no manual variable passing |
| `ParallelAgent(sub_agents=[A,B,C])` | Phase 2c Parallelization | Managed concurrency; results auto-merged into session |
| `LoopAgent(sub_agent=A, max_iterations=N)` | Phase 3 ReAct/Planning | Built-in loop with `escalate_to_parent` exit — replaces manual `while` loop |
| `Agent(tools=[...])` | Phase 1d Mini Agent | Same tool-calling loop with ADK orchestration |
| `Runner` | Your `while True` harness | Manages execution, sessions, event streaming |
| `InMemorySessionService` | `st.session_state` | Session store — per-run context management |

**What ADK adds that raw SDK doesn't have out of the box:**

| # | Capability | Raw SDK | ADK |
|---|---|---|---|
| 1 | Agent composition | Manual function calls | Typed class hierarchy — `Agent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` |
| 2 | Session management | Manual dict / st.session_state | `InMemorySessionService` or persistent stores |
| 3 | Event streaming | Manual yield | Built-in async event generator |
| 4 | Multi-agent routing | Manual `if/else` | Declarative sub-agent list |
| 5 | Loop exit condition | Manual `if done: break` | `escalate_to_parent=True` in any sub-agent |
| 6 | Google Cloud deploy | Custom containers | ADK deployment CLI — `adk deploy` |

**When ADK makes sense:**

| # | Use it | Skip it |
|---|---|---|
| 1 | Deploying multi-agent to Google Cloud | Single-agent tasks — SequentialAgent adds zero value for one step |
| 2 | Need managed session service and A2A routing | When full visibility into every LLM call matters more than DRY code |
| 3 | Want declarative composition of 5+ agents | When you need to swap LLM providers — ADK is Gemini-first |
| 4 | Team is already on Google Cloud infra | Small teams: dependency cost exceeds benefit |
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — SequentialAgent · ParallelAgent · LoopAgent"):
    st.code('''
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
import asyncio

# ── Base Agent (Phase 1d: Mini Agent with tools) ──────────────────────────────
researcher = Agent(
    name="researcher",
    model=LiteLlm(model="gemini/gemini-2.5-flash"),
    instruction="Research the given topic. Call tools if needed.",
    tools=[search_tool],
)

# ── SequentialAgent (Phase 2a: out2 = llm(prompt + out1)) ────────────────────
pipeline = SequentialAgent(
    name="research_pipeline",
    sub_agents=[researcher, summariser, formatter],
    # researcher output becomes summariser input, then formatter input
    # same as:  out2 = llm(step2_prompt + out1); out3 = llm(step3_prompt + out2)
)

# ── ParallelAgent (Phase 2c: ThreadPoolExecutor 3 calls) ─────────────────────
analyst = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[sentiment_agent, facts_agent, tone_agent],
    # all 3 run concurrently; results merged in session state
    # same as:  futures = [pool.submit(fn, x) for fn in [f1, f2, f3]]
)

# ── LoopAgent (Phase 3: while not done: think → act → observe) ───────────────
refiner = LoopAgent(
    name="quality_refiner",
    sub_agent=critique_agent,   # runs until critique_agent sets escalate_to_parent=True
    max_iterations=5,           # replaces your MAX_ITER guard
    # same as:  while iteration < MAX_ITER and not done: result = llm(critique_prompt + draft)
)

# ── Runner — executes any agent with session management ──────────────────────
session_service = InMemorySessionService()
runner = Runner(agent=pipeline, app_name="my_app", session_service=session_service)

async def run_agent(user_input: str) -> str:
    session = await session_service.create_session(app_name="my_app", user_id="user1")
    async for event in runner.run_async(
        user_id="user1",
        session_id=session.id,
        new_message=Content(role="user", parts=[Part(text=user_input)])
    ):
        if event.is_final_response():
            return event.content.parts[0].text
    return ""
''', language="python")
    st.markdown("""
**Key insight:** `SequentialAgent` is your Phase 2a chain — ADK passes context between
sub-agents automatically rather than you threading `out1` → `out2` → `out3` by hand.

**Loop insight:** `LoopAgent` replaces `while iteration < MAX_ITER and not done:` with a
declarative class. The sub-agent sets `escalate_to_parent=True` when it's satisfied — equivalent
to your `if response.strip().upper() == "DONE": break` guard.

**Trade-off:** ADK adds clean composition at the cost of learning the `Runner`/`Session` API
and taking a Gemini-first dependency. Raw SDK gives full visibility; ADK gives managed infrastructure.
""")

st.markdown("---")

# ── Interactive Demo ──────────────────────────────────────────────────────────
st.markdown("### Interactive Demo — ADK Patterns via Raw SDK Equivalents")
st.info(
    "These demos run the **exact same logic** as the ADK agent classes above — using the raw "
    "Gemini SDK you already know. Each tab shows the ADK class pattern alongside the raw "
    "equivalent so you can see precisely what ADK hides."
)

tab_seq, tab_par, tab_loop = st.tabs([
    "SequentialAgent (≡ Phase 2a)",
    "ParallelAgent (≡ Phase 2c)",
    "LoopAgent (≡ Phase 3)",
])

# ── TAB 1: Sequential ─────────────────────────────────────────────────────────
with tab_seq:
    st.markdown("**Phase 2a Prompt Chaining → ADK SequentialAgent — same 3-step pipeline, declarative syntax**")

    topic = st.text_input(
        "Topic to research:",
        value="The key difference between ReAct and Planning agents",
        key="seq_topic",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ADK Pattern")
        st.code('''
researcher  = Agent(name="researcher",
    instruction="Research this topic in 2 sentences.")
summariser  = Agent(name="summariser",
    instruction="Summarise the research for a beginner.")
formatter   = Agent(name="formatter",
    instruction="Add a 1-line takeaway at the end.")

pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[researcher, summariser, formatter]
)
runner = Runner(agent=pipeline, ...)
result = await runner.run_async(user_input=topic)
# ADK passes each agent's output to the next automatically''', language="python")

    with col2:
        st.markdown("#### Raw SDK Equivalent (runs here)")
        st.code('''
# Phase 2a: manual sequential chaining
out1 = llm("Research in 2 sentences: " + topic)
out2 = llm("Summarise for a beginner: " + out1)
out3 = llm("Add 1-line takeaway: " + out2)
# You pass output manually each step''', language="python")

    if st.button("▶ Run Sequential Pipeline", key="run_seq"):
        client = _client()
        steps, timings = [], []

        with st.spinner("Step 1 of 3 — Research..."):
            t0 = time.time()
            r1 = client.models.generate_content(
                model=MODEL,
                contents=f"Research the following topic in exactly 2 clear sentences: {topic}"
            )
            out1 = r1.text.strip()
            timings.append(time.time() - t0)
            steps.append(("🔬 Research", out1))

        with st.spinner("Step 2 of 3 — Summarise..."):
            t0 = time.time()
            r2 = client.models.generate_content(
                model=MODEL,
                contents=f"Summarise the following for a complete beginner in 1 sentence:\n\n{out1}"
            )
            out2 = r2.text.strip()
            timings.append(time.time() - t0)
            steps.append(("📝 Summarise", out2))

        with st.spinner("Step 3 of 3 — Format..."):
            t0 = time.time()
            r3 = client.models.generate_content(
                model=MODEL,
                contents=f"Take the following text and add a memorable 1-line takeaway at the end, prefixed with 'Takeaway:':\n\n{out2}"
            )
            out3 = r3.text.strip()
            timings.append(time.time() - t0)
            steps.append(("✅ Final Output", out3))

        st.success(out3)

        with st.expander("🔬 Execution Trace — 3-step sequential pipeline"):
            t1, t2, t3 = st.tabs(["① Research", "② Summarise", "③ Final"])
            for tab, (label, output), timing in zip([t1, t2, t3], steps, timings):
                with tab:
                    st.markdown(f"**{label}** — {timing:.2f}s")
                    st.code(output, language="text")
            st.code(
                f"Step 1: {timings[0]:.2f}s\n"
                f"Step 2: {timings[1]:.2f}s\n"
                f"Step 3: {timings[2]:.2f}s\n"
                f"Total:  {sum(timings):.2f}s",
                language="text"
            )

    with st.expander("🔍 ADK vs Raw — what SequentialAgent hides"):
        st.markdown("""
| Step | Phase 2a Raw | ADK SequentialAgent |
|---|---|---|
| Define agents | Python functions `fn_a(inp)`, `fn_b(inp)` | `Agent(name=..., instruction=...)` |
| Chain outputs | `out2 = fn_b(out1)` — explicit | ADK passes context between sub-agents automatically |
| Add/remove step | Edit function call chain | Add/remove from `sub_agents=[...]` list |
| Retry logic | Manual try/except per step | ADK handles retries in the Runner |
| Session context | Manual dict threading | `InMemorySessionService` holds state |

**ADK cost:** You lose direct visibility into how context is passed — debugging requires ADK's event log.
**ADK gain:** Adding a new step is one line in the `sub_agents` list, not a new variable and function call.
""")

# ── TAB 2: Parallel ───────────────────────────────────────────────────────────
with tab_par:
    st.markdown("**Phase 2c Parallelization → ADK ParallelAgent — same concurrent execution, managed merge**")

    par_topic = st.text_input(
        "Analyse this agent pattern:",
        value="ReAct agents",
        key="par_topic",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ADK Pattern")
        st.code('''
sentiment_agent = Agent(name="sentiment",
    instruction="Rate sentiment: Positive/Neutral/Negative + 1 reason.")
strength_agent  = Agent(name="strengths",
    instruction="List 2 key strengths in bullet points.")
weakness_agent  = Agent(name="weaknesses",
    instruction="List 2 key limitations in bullet points.")

analyst = ParallelAgent(
    name="analyst",
    sub_agents=[sentiment_agent, strength_agent, weakness_agent]
    # all 3 run concurrently — ADK manages threads
)
runner = Runner(agent=analyst, ...)
result = await runner.run_async(user_input=topic)
# ADK merges results into session automatically''', language="python")

    with col2:
        st.markdown("#### Raw SDK Equivalent (runs here)")
        st.code('''
# Phase 2c: manual ThreadPoolExecutor
def analyse(prompt, topic):
    return llm(f"{prompt}: {topic}").text

with ThreadPoolExecutor(max_workers=3) as pool:
    f1 = pool.submit(analyse, "Rate sentiment", topic)
    f2 = pool.submit(analyse, "2 strengths", topic)
    f3 = pool.submit(analyse, "2 limitations", topic)
    sentiment = f1.result()
    strengths  = f2.result()
    weaknesses = f3.result()
# You merge results manually''', language="python")

    if st.button("▶ Run Parallel Analysis", key="run_par"):
        client = _client()

        def call_llm(instruction: str, topic: str) -> tuple[str, float]:
            t0 = time.time()
            r = client.models.generate_content(
                model=MODEL,
                contents=f"{instruction}: {topic}"
            )
            return r.text.strip(), time.time() - t0

        instructions = [
            ("🎭 Sentiment",  "Rate the sentiment of this topic as Positive/Neutral/Negative and give 1 reason"),
            ("💪 Strengths",  "List exactly 2 key strengths of this pattern as bullet points"),
            ("⚠️ Limitations", "List exactly 2 key limitations of this pattern as bullet points"),
        ]

        with st.spinner("Running 3 analysis agents in parallel..."):
            t_start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                futures = {
                    label: pool.submit(call_llm, instr, par_topic)
                    for label, instr in instructions
                }
                results = {label: fut.result() for label, fut in futures.items()}
            wall_time = time.time() - t_start

        c1, c2, c3 = st.columns(3)
        for col, (label, (text, timing)) in zip([c1, c2, c3], results.items()):
            with col:
                st.markdown(f"**{label}** — {timing:.2f}s")
                st.info(text)

        with st.expander("🔬 Execution Trace — parallel concurrent execution"):
            st.markdown("**All 3 agents ran simultaneously. Wall-clock time ≈ slowest single call.**")
            for label, (text, timing) in results.items():
                st.markdown(f"**{label}:** {timing:.2f}s")
                st.code(text, language="text")
            st.code(
                f"Wall-clock total: {wall_time:.2f}s\n"
                f"Sum of serial times: {sum(t for _, t in results.values()):.2f}s\n"
                f"Speedup: {sum(t for _, t in results.values()) / wall_time:.1f}x",
                language="text"
            )

    with st.expander("🔍 ADK vs Raw — what ParallelAgent hides"):
        st.markdown("""
| Step | Phase 2c Raw | ADK ParallelAgent |
|---|---|---|
| Concurrency mechanism | `ThreadPoolExecutor(max_workers=N)` | ADK manages the thread pool internally |
| Submit tasks | `pool.submit(fn, arg)` for each agent | Agents listed in `sub_agents=[...]` |
| Collect results | `future.result()` per future | Results merged into session state automatically |
| Error handling | Manual try/except per future | ADK propagates errors via event stream |
| Add agent | New `pool.submit(...)` call | Add to `sub_agents` list |

**ADK cost:** Result merging is automatic but less transparent — you need to query session state to see individual outputs.
**ADK gain:** Thread management is handled; all agents share the same session context without you passing it.
""")

# ── TAB 3: Loop ───────────────────────────────────────────────────────────────
with tab_loop:
    st.markdown("**Phase 3 ReAct Loop → ADK LoopAgent — same iteration logic, declarative exit condition**")

    draft_topic = st.text_input(
        "Topic for iterative refinement:",
        value="What is a LoopAgent and when should you use one?",
        key="loop_topic",
    )
    max_iter = st.slider("Max iterations (ADK max_iterations equivalent):", 1, 4, 3, key="loop_iter")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ADK Pattern")
        st.code('''
# Sub-agent: refines AND decides when done
refine_agent = Agent(
    name="refiner",
    instruction="""
    Evaluate the draft. If quality >= 8/10, reply
    with ONLY the word DONE. Otherwise, return an
    improved version.
    ADK reads escalate_to_parent from agent output.
    """,
)

loop = LoopAgent(
    name="quality_loop",
    sub_agent=refine_agent,
    max_iterations=3,  # replaces while i < MAX_ITER
)
runner = Runner(agent=loop, ...)
result = await runner.run_async(user_input=draft)
# LoopAgent exits when refine_agent returns DONE
# or max_iterations is reached''', language="python")

    with col2:
        st.markdown("#### Raw SDK Equivalent (runs here)")
        st.code('''
# Phase 3: manual while loop with exit condition
draft = initial_draft(topic)
for iteration in range(MAX_ITER):
    critique = llm(critique_prompt + draft)
    if "DONE" in critique.upper():
        break                    # your exit condition
    draft = llm(refine_prompt + draft + critique)
    history.append(critique)
# You own the loop, exit condition, and history''', language="python")

    if st.button("▶ Run Loop Refinement", key="run_loop"):
        client = _client()
        iterations = []

        # Step 0: generate initial draft
        with st.spinner("Generating initial draft..."):
            r0 = client.models.generate_content(
                model=MODEL,
                contents=f"Write a 2-sentence answer to: {draft_topic}"
            )
            draft = r0.text.strip()
            iterations.append({"round": 0, "label": "Initial Draft", "output": draft, "verdict": "—"})

        # ADK LoopAgent equivalent: iterate until DONE or max
        for i in range(max_iter):
            with st.spinner(f"Iteration {i+1} of {max_iter} — critiquing and refining..."):
                critique_r = client.models.generate_content(
                    model=MODEL,
                    contents=(
                        f"You are a quality evaluator. Rate this answer on a scale of 1–10. "
                        f"If the quality is 8 or higher, reply with only the word DONE. "
                        f"Otherwise reply with an improved 2-sentence version.\n\n"
                        f"Answer to evaluate:\n{draft}"
                    )
                )
                response = critique_r.text.strip()

                if "DONE" in response.upper() and len(response) < 30:
                    iterations.append({"round": i+1, "label": f"Iteration {i+1}", "output": draft, "verdict": "✅ DONE — quality threshold met"})
                    break

                draft = response
                iterations.append({"round": i+1, "label": f"Iteration {i+1}", "output": draft, "verdict": f"🔄 Refined (iteration {i+1})"})
        else:
            iterations[-1]["verdict"] = f"⏱ Max iterations ({max_iter}) reached"

        st.success(f"**Final output after {len(iterations)-1} refinement(s):**\n\n{draft}")

        with st.expander("🔬 Execution Trace — loop iterations"):
            for it in iterations:
                st.markdown(f"**Round {it['round']}: {it['label']}** — {it['verdict']}")
                st.code(it["output"], language="text")
            st.code(
                f"Iterations used: {len(iterations)-1} of {max_iter} max\n"
                f"Exit reason: {iterations[-1]['verdict']}",
                language="text"
            )

    with st.expander("🔍 ADK vs Raw — what LoopAgent hides"):
        st.markdown("""
| Step | Phase 3 Raw | ADK LoopAgent |
|---|---|---|
| Loop structure | `for i in range(MAX_ITER):` | `max_iterations=N` parameter |
| Exit condition | `if done_signal in response: break` | Sub-agent sets `escalate_to_parent=True` |
| State between iterations | Manual history list you maintain | Session state managed by `InMemorySessionService` |
| Max iteration guard | Your `MAX_ITER` constant | `max_iterations` parameter — same concept, different syntax |
| Sub-agent logic | Function or class you write | `Agent(instruction=...)` — same prompt engineering |

**Identical mechanism:** Both run the sub-agent repeatedly and stop when a condition is met.
ADK's name for your `if done: break` is `escalate_to_parent=True`.
The session service replaces your manual history list.

**When LoopAgent adds value:** When you compose it with a SequentialAgent or ParallelAgent —
a LoopAgent as one step in a larger pipeline is far cleaner than a nested while-loop inside a function.
""")

st.markdown("---")
st.markdown("### What's next → Phase 10f — Framework Comparison")
st.markdown(
    "You've seen ADK's three agent types. Phase 10f asks the harder question: "
    "given a real production requirement, which of Raw SDK, LangGraph, LangChain, LangSmith, "
    "and ADK should you actually reach for — and why?"
)
