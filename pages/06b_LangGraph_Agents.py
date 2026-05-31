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

from utils.diagrams import diagram_langgraph_agents
from utils.llm import MODEL
from utils.tools import get_weather, get_stock_price

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🤖 10b — LangGraph Agents")
st.caption(
    "Phase 3's ReAct, Reflection, and Planning patterns as LangGraph agent graphs. "
    "HITL drops from ~40 lines to 2. Streaming and persistence are free."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(diagram_langgraph_agents(),
         caption="Phase 3 manual ReAct loop vs LangGraph agent graph — same behaviour, less scaffolding",
         use_column_width=True)

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

tab_react, tab_reflect, tab_hitl = st.tabs([
    "3a ReAct → LangGraph",
    "3b Reflection → Graph",
    "4b HITL → interrupt_before",
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
        st.markdown("#### Phase 3a — Manual (what you wrote)")
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

# ── TAB: Reflection ───────────────────────────────────────────────────────────
with tab_reflect:
    st.markdown("**Phase 3b Reflection → LangGraph Generate → Critique → loop**")
    st.markdown("""
| Phase 3b Manual | LangGraph Equivalent |
|---|---|
| `output = generate(task)` | `generate_node(state)` |
| `critique = evaluate(output)` | `critique_node(state)` |
| `while score < threshold:` | Conditional back-edge: critique → generate |
| `if score >= threshold: break` | `router_fn` returns `END` |
| `MAX_CYCLES` guard | `recursion_limit` |
""")
    st.code('''
class ReflectState(TypedDict):
    task: str; output: str; score: int; cycles: int

def generate_node(state):
    state["output"] = llm(f"Complete: {state['task']}")
    state["cycles"] = state.get("cycles", 0) + 1
    return state

def critique_node(state):
    r = llm(f"Score 1-10 then critique: {state['output']}")
    state["score"] = int(r.strip()[0])
    return state

def router(state):
    if state["score"] >= 7 or state["cycles"] >= 3:
        return END
    return "generate"          # loop back for improvement

g = StateGraph(ReflectState)
g.add_node("generate", generate_node)
g.add_node("critique", critique_node)
g.add_edge(START, "generate")
g.add_edge("generate", "critique")
g.add_conditional_edges("critique", router, {"generate": "generate", END: END})
app = g.compile(recursion_limit=10)
''', language="python")
    st.info(
        "**Key insight:** The conditional back-edge IS your `while score < threshold` loop. "
        "The graph structure makes the iteration path explicit and auditable — "
        "you can inspect every cycle in LangSmith (Phase 10c)."
    )

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

st.markdown("---")
st.markdown("### What's next → Phase 10c — LangSmith")
st.markdown(
    "Your Phase 7 manual `TraceCollector` replaced by 3 environment variables. "
    "Every LangGraph call — including all the streaming steps above — auto-traces."
)
