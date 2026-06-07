"""
Phase 10b — LangGraph Agents
Bridges Phase 3 (ReAct, Reflection, Planning) + Phase 4 (HITL) to LangGraph agent graphs.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10b — LangGraph Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.llm import MODEL
from utils.tools import get_weather, get_stock_price

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🤖 10b — LangGraph Agents")
st.caption(
    "Phase 3's ReAct, Reflection, and Planning patterns as LangGraph agent graphs. "
    "HITL drops from ~40 lines to 2. Streaming and persistence are free."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image("docs/images/arch_langgraph_agents.jpg",
         caption="Your Phase 3 loop → create_react_agent() → streaming, persistence, typed state, HITL in 2 lines",
         use_container_width=True)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 3 — ReAct · Reflection · Planning &amp; Phase 4 — HITL)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 3 you wrote a <code>while iteration &lt; MAX_ITER</code> loop: the agent thinks,
    calls a tool, reads the result, and decides whether to call another tool or stop.
    In LangGraph that loop becomes a cycle between two nodes — an <strong>agent node</strong>
    and a <strong>tools node</strong> — with the graph engine handling the cycling automatically.<br><br>
    The Phase 4 HITL checkpoint you built in ~40 lines (serialise state → show approval UI →
    resume) becomes a single parameter: <code>interrupt_before=["tools"]</code>.
    You are not learning new agent behaviour. You are seeing the exact same behaviour
    expressed as a graph instead of a while-loop.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What LangGraph adds to your Phase 3 agents"):
    st.markdown("""
**You already built every pattern in Phase 3.** LangGraph formalises them as typed graphs.

| Phase 3/4 Pattern | LangGraph Equivalent | Lines saved |
|---|---|---|
| ReAct loop (3a) | `create_react_agent(llm, tools)` | ~35 lines |
| Manual tool dispatch | `ToolNode` auto-detects and runs tools | ~15 lines |
| HITL checkpoint (4b) | `interrupt_before=["tools"]` | ~40 lines → 2 |
| `session_state` memory | `MemorySaver(checkpointer)` + `thread_id` | built-in |
| `while i < MAX_ITER` guard | `recursion_limit` on `compile()` | built-in |
| Streaming (not in Phase 3) | `graph.stream()` yields per-node | new capability |
| Reflection loop (3b) | Generate node → Critique node → conditional back-edge | graph pattern |
| Planning (3c) | Plan node → Execute nodes → Synthesize node | graph pattern |
| Code Execution (3d) | `ToolNode` wrapping a sandboxed Python executor tool | same ToolNode |

**The agent IS the same.** LangGraph handles the scaffolding so you write the logic.
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — LangGraph ReAct Agent"):
    st.code('''
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# 1. Define tools (same functions as Phase 3 — just decorated)
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    ...

# 2. Create agent — replaces your entire Think->Act->Observe loop
llm   = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
agent = create_react_agent(
    llm,
    tools=[get_weather, get_stock_price],
    checkpointer=MemorySaver(),        # Phase 1b memory, built-in
)

# 3. Run with streaming — each node result arrives as it completes
config = {"configurable": {"thread_id": "session-1"}}
for chunk in agent.stream({"messages": [("user", query)]}, config):
    print(chunk)   # yields: {"agent": {...}} then {"tools": {...}}

# ---- HITL: Phase 4b in 2 lines ------------------------------------------------
agent_hitl = create_react_agent(
    llm, tools=[get_weather],
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],        # pause BEFORE every tool call
)
# After interrupt, inspect state, then resume:
agent_hitl.invoke(None, config)        # None = continue from checkpoint
''', language="python")
    st.markdown("""
**What `create_react_agent` replaced:** the entire `while iteration < MAX_ITER` loop,
the `if not response.tool_calls: break` stop condition, and the manual `history.append(result)`
after each tool call. The agent behaviour is identical.

**What `interrupt_before` replaced:** Phase 4b's 40-line HITL checkpoint that had to
serialise state, present it for review, deserialise it, and inject the approval result.
""")

st.markdown("---")
st.markdown("### Interactive Demo")

tab_react, tab_reflect, tab_hitl, tab_super, tab_loop = st.tabs([
    "3a ReAct → LangGraph",
    "3b Reflection → Graph (live)",
    "4b HITL → interrupt_before",
    "6a Supervisor Agent",
    "Agent Loop — Ng's 4 Patterns",
])

# ── TAB: ReAct ────────────────────────────────────────────────────────────────
with tab_react:
    st.markdown("**Phase 3a ReAct agent — manual vs LangGraph side-by-side**")
    query = st.text_input(
        "Query:",
        value="What is the weather in London and the stock price of AAPL?",
        key="lg_react_query",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### What you wrote in Phase 3a")
        st.code('''
while iteration < MAX_ITER:
    response = llm_with_tools(history)
    if not response.function_calls:
        break
    for call in response.function_calls:
        result = TOOL_MAP[call.name](**call.args)
        history.append({"role":"tool","content":result})
    iteration += 1
# ~35 lines of loop scaffolding''', language="python")

    with col2:
        st.markdown("#### LangGraph — `create_react_agent`")
        if st.button("Run LangGraph ReAct", key="run_lg_react"):
            try:
                from langgraph.prebuilt import create_react_agent
                from langgraph.checkpoint.memory import MemorySaver
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.tools import tool as lc_tool

                @lc_tool
                def weather_tool(city: str) -> str:
                    """Get current weather for a city."""
                    return get_weather(city)

                @lc_tool
                def stock_tool(ticker: str) -> str:
                    """Get stock price for a ticker symbol like AAPL, TSLA, GOOGL."""
                    return get_stock_price(ticker)

                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                )
                agent = create_react_agent(
                    llm, tools=[weather_tool, stock_tool],
                    checkpointer=MemorySaver(),
                )
                steps = []
                config = {"configurable": {"thread_id": "demo-react"}}
                with st.spinner("Running LangGraph ReAct agent..."):
                    for chunk in agent.stream(
                        {"messages": [("user", query)]}, config
                    ):
                        for node_name, node_data in chunk.items():
                            steps.append((node_name, node_data))
                            st.caption(f"✓ node `{node_name}`")

                final_msgs = steps[-1][1].get("messages", []) if steps else []
                if final_msgs:
                    st.success(final_msgs[-1].content)

                with st.expander("🔬 Execution Trace — node-by-node"):
                    for name, data in steps:
                        st.markdown(f"**Node: `{name}`**")
                        for m in data.get("messages", []):
                            role = getattr(m, "type", type(m).__name__)
                            content = str(getattr(m, "content", m))[:400]
                            st.code(f"[{role}] {content}", language="text")

            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("🔍 Translation — what each LangGraph piece replaced"):
        st.markdown("""
| Phase 3a manual | LangGraph equivalent |
|---|---|
| `while iteration < MAX_ITER:` | `recursion_limit` on `compile()` |
| `response = llm_with_tools(history)` | `agent_node` in the graph (auto-managed) |
| `if not response.function_calls: break` | Graph routes to `END` when no tool calls |
| `result = TOOL_MAP[name](**args)` | `ToolNode` dispatches automatically |
| `history.append(result)` | `MessagesState` accumulates automatically |
| Manual streaming not built-in | `agent.stream()` yields per-node live |
""")

# ── TAB: Reflection (live demo) ───────────────────────────────────────────────
with tab_reflect:
    st.markdown("**Andrew Ng Pattern 1 — Reflection as a LangGraph cycle: Generate → Critique → loop**")
    st.markdown("""
| Phase 3b Manual | LangGraph Equivalent | What it replaces |
|---|---|---|
| `output = generate(task)` | `generate_node(state)` updates state | Manual function call |
| `critique = evaluate(output)` | `critique_node(state)` writes score + feedback | Manual evaluation call |
| `while score < threshold:` | Conditional back-edge: critique → generate | The entire while loop |
| `if score >= threshold: break` | `router_fn` returns `END` | The break condition |
| `MAX_CYCLES` guard | `recursion_limit` on `compile()` | Your manual counter |

**Andrew Ng's Reflection in the LangGraph Agent Loop:**
The `Evaluate` step in Perceive→Reason→Act→**Evaluate**→Persist IS this reflection pattern.
When `conditional_edge(state)` routes back to `Reason` instead of `END`, the agent reflects.
""")
    st.code('''
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ReflectState(TypedDict):
    task: str
    output: str
    score: int
    feedback: str
    cycles: int

def generate_node(state: ReflectState):
    prompt = state["task"]
    if state.get("feedback"):                        # incorporate feedback on 2nd+ cycle
        prompt += f"\\n\\nPrevious critique: {state['feedback']}\\nImprove based on this."
    result = llm.invoke(prompt)
    return {"output": result.content, "cycles": state.get("cycles", 0) + 1}

def critique_node(state: ReflectState):
    r = llm.invoke(
        f"Score this output 1-10 (one digit only first), then one sentence critique:\\n{state['output']}"
    )
    text = r.content.strip()
    score = int(text[0]) if text[0].isdigit() else 5
    feedback = text[2:].strip() if len(text) > 2 else "needs improvement"
    return {"score": score, "feedback": feedback}

def router(state: ReflectState) -> str:
    if state["score"] >= 7 or state["cycles"] >= 3:
        return END          # good enough or max cycles reached
    return "generate"       # loop back: Andrew Ng's reflection cycle

g = StateGraph(ReflectState)
g.add_node("generate", generate_node)
g.add_node("critique", critique_node)
g.add_edge(START, "generate")
g.add_edge("generate", "critique")
g.add_conditional_edges("critique", router, {"generate": "generate", END: END})
app = g.compile(recursion_limit=10)   # replaces your MAX_CYCLES guard
''', language="python")

    st.markdown("#### Live Demo — run the reflection loop and watch every cycle")
    reflect_task = st.text_input(
        "Task for reflection agent:",
        value="Explain why agentic AI is different from regular LLM calls in 2 sentences.",
        key="reflect_task",
    )
    threshold = st.slider("Score threshold (stop when score ≥ this):", 5, 9, 7, key="reflect_thresh")

    if st.button("Run Reflection Loop", key="run_reflect"):
        try:
            from langgraph.graph import StateGraph, START, END
            from langchain_google_genai import ChatGoogleGenerativeAI
            from typing import TypedDict
            import os

            class ReflectState(TypedDict):
                task: str; output: str; score: int; feedback: str; cycles: int

            llm_r = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                           google_api_key=os.getenv("GEMINI_API_KEY"))

            def generate_node(state):
                prompt = state["task"]
                if state.get("feedback"):
                    prompt += f"\n\nPrevious critique: {state['feedback']}\nImprove based on this."
                r = llm_r.invoke(prompt)
                return {"output": r.content, "cycles": state.get("cycles", 0) + 1}

            def critique_node(state):
                r = llm_r.invoke(
                    f"Score 1-10 (first digit only), then one sentence critique:\n{state['output']}"
                )
                txt = r.content.strip()
                score = int(txt[0]) if txt[0].isdigit() else 5
                fb = txt[2:].strip() if len(txt) > 2 else "needs improvement"
                return {"score": score, "feedback": fb}

            def router(state):
                if state["score"] >= threshold or state["cycles"] >= 3:
                    return END
                return "generate"

            g = StateGraph(ReflectState)
            g.add_node("generate", generate_node)
            g.add_node("critique", critique_node)
            g.add_edge(START, "generate")
            g.add_edge("generate", "critique")
            g.add_conditional_edges("critique", router, {"generate": "generate", END: END})
            app = g.compile(recursion_limit=10)

            steps = []
            with st.spinner("Running reflection loop..."):
                for chunk in app.stream({
                    "task": reflect_task, "output": "", "score": 0,
                    "feedback": "", "cycles": 0
                }):
                    for node_name, data in chunk.items():
                        steps.append((node_name, data))
                        if node_name == "generate":
                            st.caption(f"🔄 Cycle {data.get('cycles','?')} — generate")
                        elif node_name == "critique":
                            st.caption(f"  📊 Score: **{data.get('score','?')}** — {data.get('feedback','')[:80]}")

            final_output = ""
            final_score = 0
            for name, data in steps:
                if name == "generate" and data.get("output"):
                    final_output = data["output"]
                if name == "critique" and data.get("score"):
                    final_score = data["score"]

            st.success(final_output)
            total_cycles = sum(1 for n, _ in steps if n == "generate")
            st.caption(f"Completed in **{total_cycles}** cycle(s) — final score: **{final_score}/10**")

            # Graph visualisation
            try:
                png = app.get_graph().draw_mermaid_png()
                with st.expander("📊 Compiled graph structure (draw_mermaid_png)"):
                    st.image(png, caption="Actual LangGraph compiled graph — the back-edge IS the reflection loop")
            except Exception:
                pass

            with st.expander("🔬 Execution Trace — every cycle"):
                for i, (name, data) in enumerate(steps):
                    st.markdown(f"**Step {i+1} — node `{name}`**")
                    if name == "generate":
                        st.code(f"output: {data.get('output','')[:300]}", language="text")
                    else:
                        st.code(f"score: {data.get('score')}  feedback: {data.get('feedback','')}", language="text")

        except Exception as e:
            st.error(f"Error: {e}")

    st.info("**Andrew Ng Pattern 1:** The conditional back-edge from `critique → generate` IS the Reflection loop. "
            "`draw_mermaid_png()` above shows it as an actual cycle in the graph — "
            "the same back-arrow you'd draw on a whiteboard.")

# ── TAB: HITL ─────────────────────────────────────────────────────────────────
with tab_hitl:
    st.markdown("**Phase 4b HITL → `interrupt_before` — 40 lines → 2**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Phase 4b — Manual HITL")
        st.code('''
# ~40 lines: check, serialise, render UI,
# await approval, deserialise, continue
if action["type"] in IRREVERSIBLE_ACTIONS:
    st.session_state["pending"] = action
    st.session_state["hitl"]    = "waiting"
    # ... render approval UI ...
    if approved:
        result = execute_action(action)
    else:
        result = "Cancelled"''', language="python")

    with col2:
        st.markdown("#### LangGraph — `interrupt_before`")
        st.code('''
# 2 lines of HITL configuration:
agent = create_react_agent(
    llm, tools,
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],   # line 1

)
# Agent stops before every tool call.
# Inspect: agent.get_state(config)
# Resume:
agent.invoke(None, config)        # line 2
# Override tool call:
# agent.update_state(config, new_state)
# agent.invoke(None, config)''', language="python")

    st.markdown("""
| Phase 4b Manual | LangGraph `interrupt_before` |
|---|---|
| Check action type in blocklist | `interrupt_before=["tools"]` intercepts all tool calls |
| Serialise pending state to session | Checkpointer handles state automatically |
| Render approval UI, wait | `graph.get_state(config)` exposes pending action |
| If approved: continue | `graph.invoke(None, config)` — resume |
| If rejected: cancel | `graph.update_state(config, override)` + resume |
| ~40 lines | 2 lines |
""")
    st.success(
        "The HITL concept is identical. The implementation is not. "
        "`interrupt_before` is the single biggest productivity gain LangGraph offers over raw agents."
    )

    with st.expander("🔬 Execution Trace — HITL flow"):
        st.code('''
# Full HITL flow with LangGraph:

config = {"configurable": {"thread_id": "hitl-demo"}}

# 1. Start — agent will stop before calling any tool
result = agent.invoke({"messages": [("user", "Check AAPL stock")]}, config)
# result["__interrupt__"] shows what the agent wants to do

# 2. Inspect what the agent planned
snapshot = agent.get_state(config)
print("Agent wants to call:", snapshot.next)

# 3a. Approve — resume as-is
final = agent.invoke(None, config)

# 3b. Reject — inject override message
from langchain_core.messages import HumanMessage
agent.update_state(config, {"messages": [HumanMessage("Skip the tool, just say you don't know")]})
final = agent.invoke(None, config)
''', language="python")

# ── TAB: Supervisor Agent ─────────────────────────────────────────────────────
with tab_super:
    st.markdown("**Phase 6a Multi-Agent → LangGraph Supervisor pattern**")
    st.markdown("""
In Phase 6a you built a Root + Sub-agent system manually — the root delegated tasks by calling
sub-agent functions directly. The **Supervisor Agent** pattern in LangGraph formalises this:
a Supervisor node uses an LLM to dynamically route tasks to specialist worker nodes.

| Phase 6a Manual | LangGraph Supervisor |
|---|---|
| `root.delegate(sub_agent, task)` | Supervisor node returns `{"next": "worker_name"}` |
| `if result == "done": break` | `conditional_edge` routes to `END` when supervisor says "FINISH" |
| Manual worker dispatch | `conditional_edges` maps supervisor decision → worker node |
| Sequential or ad-hoc parallel | Supervisor decides order dynamically per task |
""")
    st.code('''
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

WORKERS = ["researcher", "writer", "reviewer"]

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str        # which worker to call next

def supervisor_node(state: SupervisorState):
    """LLM decides which worker to call next, or FINISH."""
    decision = llm.invoke(
        f"Given this task, which worker should act next: {WORKERS} or FINISH?\\n"
        f"Conversation so far: {state['messages'][-3:]}"
    )
    next_worker = decision.content.strip()
    return {"next": next_worker, "messages": [decision]}

def researcher_node(state: SupervisorState):
    r = llm.invoke(f"Research this topic: {state['messages'][0].content}")
    return {"messages": [r]}

def writer_node(state: SupervisorState):
    r = llm.invoke(f"Write a report based on: {state['messages'][-1].content}")
    return {"messages": [r]}

def reviewer_node(state: SupervisorState):
    r = llm.invoke(f"Review and improve: {state['messages'][-1].content}")
    return {"messages": [r]}

def route_next(state: SupervisorState) -> Literal["researcher","writer","reviewer","__end__"]:
    if state["next"] == "FINISH":
        return "__end__"
    return state["next"]

g = StateGraph(SupervisorState)
g.add_node("supervisor", supervisor_node)
g.add_node("researcher", researcher_node)
g.add_node("writer",     writer_node)
g.add_node("reviewer",   reviewer_node)

g.add_edge(START,        "supervisor")
g.add_conditional_edges("supervisor", route_next)   # supervisor decides who goes next
g.add_edge("researcher", "supervisor")              # all workers report back to supervisor
g.add_edge("writer",     "supervisor")
g.add_edge("reviewer",   "supervisor")
app = g.compile()
''', language="python")

    if st.button("Run Supervisor Agent demo", key="run_supervisor"):
        try:
            from langgraph.graph import StateGraph, START, END
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, AIMessage
            from typing import TypedDict, Annotated, Literal
            from langgraph.graph.message import add_messages
            import os

            WORKERS = ["researcher", "writer"]

            class SupState(TypedDict):
                messages: Annotated[list, add_messages]
                next: str

            llm_s = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                           google_api_key=os.getenv("GEMINI_API_KEY"))
            topic = st.session_state.get("supervisor_topic", "Why does agentic AI matter?")

            def supervisor_node(state):
                history = "\n".join(
                    f"{m.type}: {m.content[:120]}" for m in state["messages"][-4:]
                )
                r = llm_s.invoke(
                    f"You are a supervisor. Workers available: {WORKERS}.\n"
                    f"Task: {state['messages'][0].content}\n"
                    f"History so far:\n{history}\n\n"
                    f"Reply with ONLY the next worker name ({', '.join(WORKERS)}) or FINISH."
                )
                nxt = r.content.strip().split()[0]
                if nxt not in WORKERS:
                    nxt = "FINISH"
                return {"next": nxt, "messages": [r]}

            def researcher_node(state):
                r = llm_s.invoke(f"Research in 2 sentences: {state['messages'][0].content}")
                return {"messages": [r]}

            def writer_node(state):
                last = next((m.content for m in reversed(state["messages"])
                             if m.type == "ai" and len(m.content) > 20), "")
                r = llm_s.invoke(f"Write a crisp 1-paragraph summary based on:\n{last}")
                return {"messages": [r]}

            def route_next(state) -> Literal["researcher", "writer", "__end__"]:
                nxt = state.get("next", "FINISH")
                if nxt in WORKERS:
                    return nxt
                return "__end__"

            g = StateGraph(SupState)
            g.add_node("supervisor", supervisor_node)
            g.add_node("researcher", researcher_node)
            g.add_node("writer",     writer_node)
            g.add_edge(START, "supervisor")
            g.add_conditional_edges("supervisor", route_next)
            g.add_edge("researcher", "supervisor")
            g.add_edge("writer",     "supervisor")
            app = g.compile(recursion_limit=12)

            steps = []
            with st.spinner("Running supervisor multi-agent system..."):
                for chunk in app.stream({"messages": [HumanMessage(content=topic)], "next": ""}):
                    for node, data in chunk.items():
                        steps.append((node, data))
                        st.caption(f"✓ node `{node}` → next: `{data.get('next','—')}`")

            last_msg = ""
            for _, data in reversed(steps):
                msgs = data.get("messages", [])
                for m in reversed(msgs):
                    if hasattr(m, "content") and len(m.content) > 30:
                        last_msg = m.content; break
                if last_msg: break
            st.success(last_msg or "Done.")

            try:
                png = app.get_graph().draw_mermaid_png()
                with st.expander("📊 Compiled supervisor graph"):
                    st.image(png, caption="Supervisor routes dynamically to workers — all report back")
            except Exception:
                pass

            with st.expander("🔬 Execution Trace — supervisor routing decisions"):
                for name, data in steps:
                    nxt = data.get("next", "")
                    msgs = data.get("messages", [])
                    last_content = msgs[-1].content[:150] if msgs else ""
                    st.code(f"[{name}] next={nxt!r}  →  {last_content}", language="text")
        except Exception as e:
            st.error(f"Error: {e}")

    topic_s = st.text_input("Topic:", value="Why does agentic AI matter?", key="supervisor_topic")
    st.markdown("""
| Pattern | Supervisor Agent | Orchestrator-Workers (Phase 2d) |
|---|---|---|
| Planning | Dynamic — supervisor LLM decides each step | Static — orchestrator plans all steps upfront |
| Worker count | Variable per task | Fixed at design time |
| Feedback loop | Workers report back; supervisor re-evaluates | Workers return results; orchestrator assembles once |
| When to use | Complex tasks needing adaptive routing | Predictable multi-step workflows |
""")

# ── TAB: Agent Loop — Andrew Ng's 4 Patterns ──────────────────────────────────
with tab_loop:
    st.image("docs/images/arch_langgraph_platform.jpg", use_container_width=True,
             caption="The LangGraph Agent Loop (Perceive → Reason → Act → Evaluate → Persist) and Platform infrastructure")

    st.markdown("""
### The LangGraph Agent Loop — Andrew Ng's 4 Patterns Unified

The diagram's **LangGraph Agent Loop** (Perceive → Reason → Act → Evaluate → Persist) is the
unified framework that captures ALL of Andrew Ng's four fundamental agentic patterns:

| Loop Step | Andrew Ng Pattern | Phase in this course | How it maps |
|---|---|---|---|
| **Perceive** | All patterns | Phase 1b (memory) | Load state from checkpointer — the history the agent knows |
| **Reason** | Reflection (Pattern 1) | Phase 3b | LLM thinks: what to do next, or critiques its own output |
| **Act** | Tool Use (Pattern 2) | Phase 1c, 3a | ToolNode executes the chosen tool call |
| **Reason → Plan → Act** | Planning (Pattern 3) | Phase 3c | Reason step writes a plan; Act executes one plan step |
| **Act → delegate sub-agent** | Multi-Agent (Pattern 4) | Phase 6a | Act step calls a sub-agent instead of a tool |
| **Evaluate → back to Reason** | Reflection (Pattern 1) | Phase 3b | Conditional edge loops back → the reflection cycle |
| **Persist** | All patterns | Phase 5b (long-term) | Checkpointer saves state — next turn starts from here |
""")

    st.code('''
# The 5 loop steps in LangGraph code
# ─────────────────────────────────────────────────────────────────────────────

# ① PERCEIVE — state loaded automatically from checkpointer each invocation
config = {"configurable": {"thread_id": "session-1"}}
# agent.invoke(input, config) → LangGraph loads state[thread_id] before running

# ② REASON — agent node: LLM decides next action
def agent_node(state):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}              # AIMessage with or without tool_calls

# ③ ACT — ToolNode executes tool_calls from the AIMessage
from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools=[get_weather, get_stock_price])

# ④ EVALUATE — conditional edge decides: loop or end?
def should_continue(state) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if last.tool_calls:                          # more tools to call → stay in loop
        return "tools"
    return "__end__"                             # done → exit

# For REFLECTION: evaluate score → route back to generate node
def reflection_router(state) -> Literal["generate", "__end__"]:
    if state["score"] >= threshold:
        return "__end__"                         # good enough → exit
    return "generate"                            # improve → loop back (Andrew Ng Pattern 1)

# ⑤ PERSIST — checkpointer saves state automatically after every node
agent = create_react_agent(llm, tools, checkpointer=MemorySaver())
# Every invocation: MemorySaver reads state → run → MemorySaver writes state
''', language="python")

    with st.expander("🔍 Why this loop is the foundation of everything"):
        st.markdown("""
| If you only have... | You get | Phase |
|---|---|---|
| Perceive + Reason | Plain LLM with memory | Phase 1b |
| + Act | Augmented LLM with tools | Phase 1c |
| + the loop (no Evaluate) | ReAct agent | Phase 3a |
| + Evaluate routing back | Reflection agent | Phase 3b |
| + Reason writes plan first | Planning agent | Phase 3c |
| + Act delegates to sub-agent | Multi-agent system | Phase 6a |
| + Persist (SqliteSaver) | Production agent with durable memory | Phase 10b2 |
| + LangSmith | Observability without code changes | Phase 10c |

**The loop is not new.** You built every one of these in earlier phases.
LangGraph just makes the loop a first-class construct in the graph — explicit, observable, and resumable.
""")

st.markdown("---")
st.markdown("### What's next → Phase 10b2 — LangGraph Memory & Persistence")
st.markdown(
    "Your Phase 7 manual `TraceCollector` replaced by 3 environment variables. "
    "Every LangGraph call — including all the streaming steps above — auto-traces."
)
