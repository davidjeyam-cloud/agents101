"""
Phase 10b4 — LangGraph: Platform & Production
Layer 6 of the architecture diagram: Studio UI, Deploy/Durable Execution,
API Server pattern, draw_mermaid_png() on every graph, streaming, production checklist.
"""
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="10b4 — LangGraph Platform", page_icon="🚀", layout="wide")

from utils.diagrams import diagram_langgraph_platform
from utils.llm import MODEL, _client

st.title("🚀 10b4 — LangGraph: Platform & Production")
st.caption(
    "Layer 6: Studio UI, Deploy, Durable Execution, API Server, streaming, draw_mermaid_png(). "
    "How a graph built in 10a–10b3 becomes a deployed, observable, production service."
)

st.image(diagram_langgraph_platform(), use_container_width=True,
         caption="Layer 6 — Platform & Production: Agent Loop cycle (left) + Platform features (right)")

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Layer 6 — Platform & Production"):
    st.markdown("""
Once you have a working graph (Layers 1–5), LangGraph Platform provides four production primitives:

| Primitive | What it does | Phase equivalent |
|---|---|---|
| **Studio UI** | Visual graph debugger — see nodes, state, interrupts live | Phase 7a Observability (but visual + interactive) |
| **Deploy** | 1-click managed hosting — your graph becomes an API | Phase 7a (manual infra) |
| **Durable Execution** | Automatic retry + resume after crashes/restarts | Phase 7c Error Analysis |
| **API Server** | REST + WebSocket endpoints auto-generated from graph | Custom server wrapper in Phase 8a |

**`draw_mermaid_png()` — the most powerful learning tool:**
Any compiled LangGraph graph can render itself as a Mermaid diagram. This shows:
- Every node (circles)
- Every edge (arrows)
- Every conditional edge (branching arrows)
- Back-edges that create loops (Reflection cycle)
- START/END nodes

No external tool needed — it runs inline in Python or Streamlit.

**Streaming modes:**
```python
# values mode — full state after each node completes
for chunk in graph.stream(input, config, stream_mode="values"):
    print(chunk["messages"][-1])

# updates mode — only what changed each step
for node_name, state_delta in graph.stream(input, config, stream_mode="updates"):
    print(f"{node_name}: {state_delta}")

# messages mode — token-by-token from the LLM
async for msg, metadata in graph.astream_events(input, config, version="v2"):
    if msg.event == "on_chat_model_stream":
        print(msg.data["chunk"].content, end="", flush=True)
```
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — draw_mermaid_png + streaming + production deploy"):
    st.code('''
# ── draw_mermaid_png(): render any graph inline ───────────────────────────────
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, create_react_agent

# Build any graph
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route_fn)
builder.add_edge("tools", "agent")   # back-edge creates the loop
graph = builder.compile()

# Render the graph — PNG bytes — display in Streamlit
png_bytes = graph.get_graph().draw_mermaid_png()
st.image(png_bytes, caption="Compiled graph structure")

# For subgraphs (e.g. multi-agent with nested graphs):
png_bytes = graph.get_graph(xray=True).draw_mermaid_png()  # expand subgraphs inline

# ── Streaming — values mode ───────────────────────────────────────────────────
placeholder = st.empty()
full_response = ""
for chunk in graph.stream({"messages": [("user", query)]}, config,
                           stream_mode="values"):
    last = chunk["messages"][-1]
    if hasattr(last, "content") and last.content:
        full_response = last.content
        placeholder.markdown(full_response + "▌")   # streaming cursor
placeholder.markdown(full_response)

# ── Streaming — token-by-token (messages mode) ───────────────────────────────
import asyncio
async def stream_tokens():
    async for event in graph.astream_events(
        {"messages": [("user", query)]}, config, version="v2"
    ):
        if event["event"] == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                yield token

# ── Production deployment ─────────────────────────────────────────────────────
# Option 1: LangGraph Platform (managed) — langgraph.json + docker
# langgraph.json:
# {
#   "dependencies": ["."],
#   "graphs": {"my_agent": "./agent.py:graph"},
#   "env": ".env"
# }
# Then: langgraph build -t my-agent-image && langgraph up

# Option 2: FastAPI wrapper (self-hosted)
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class RunRequest(BaseModel):
    message: str
    thread_id: str = "default"

@app.post("/run")
async def run_agent(req: RunRequest):
    cfg = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke({"messages": [("user", req.message)]}, cfg)
    return {"response": result["messages"][-1].content}

# ── Durable Execution pattern ─────────────────────────────────────────────────
# With SqliteSaver/PostgresSaver: graph state survives process crash
# On restart: load checkpoint by thread_id and resume
from langgraph.checkpoint.sqlite import SqliteSaver
with SqliteSaver.from_conn_string("prod_checkpoints.db") as cp:
    graph = builder.compile(checkpointer=cp)
    # Process crash here → restart → same thread_id → resumes from last checkpoint
    result = graph.invoke(input, {"configurable": {"thread_id": "user-123"}})
''', language="python")
    st.markdown("""
**Why `draw_mermaid_png()` matters for learning:** The graph source code describes the *logic*.
The Mermaid rendering shows the *structure* — back-edges, conditional branches, subgraph boundaries.
When you add a Reflection cycle, the back-edge from `evaluate` → `generate` is immediately visible.
This is the fastest way to verify your graph topology before running it.

**Durable Execution vs Process-level resilience:** A basic graph with MemorySaver loses all state
if the process crashes. SqliteSaver/PostgresSaver write checkpoint after every node — the next
invocation with the same thread_id loads that state and continues. This is Phase 7c Error Analysis
made automatic.
""")

st.markdown("---")
st.markdown("### Interactive Demos")

tab_mermaid, tab_stream, tab_checklist = st.tabs([
    "draw_mermaid_png() — live graph rendering",
    "Streaming — values mode",
    "Production Readiness Checklist",
])

# ── TAB: Mermaid rendering ────────────────────────────────────────────────────
with tab_mermaid:
    st.markdown("**Render actual compiled LangGraph graphs as diagrams**")
    st.markdown("""
| Graph Type | What the Mermaid shows |
|---|---|
| Simple ReAct | agent → tools → agent loop + START/END |
| Reflection | agent → evaluate → (back to agent OR END) |
| HITL | agent → guard → hitl → tools → agent |
| Multi-Agent Supervisor | supervisor → worker_a / worker_b → supervisor |
""")
    graph_choice = st.selectbox(
        "Choose graph to visualise:",
        ["ReAct Agent (agent → tools loop)", "Reflection Agent (evaluate back-edge)", "HITL Agent (guard + interrupt)"],
        key="mermaid_choice"
    )
    if st.button("Render graph", key="render_mermaid"):
        try:
            from langgraph.graph import StateGraph, MessagesState, START, END
            from typing import Literal

            if graph_choice.startswith("ReAct"):
                def agent_n(state): return {}
                def route_n(state) -> Literal["tools", END]: return END
                b = StateGraph(MessagesState)
                b.add_node("agent", agent_n)
                b.add_node("tools", lambda s: {})
                b.add_edge(START, "agent")
                b.add_conditional_edges("agent", route_n, {"tools": "tools", END: END})
                b.add_edge("tools", "agent")
                g = b.compile()
                caption = "ReAct: agent→tools loop. The back-edge tools→agent creates the cycle."

            elif graph_choice.startswith("Reflection"):
                from typing_extensions import TypedDict
                from langgraph.graph import add_messages
                from typing import Annotated
                class RefState(TypedDict):
                    messages: Annotated[list, add_messages]
                    score: int
                def gen_n(state): return {}
                def eval_n(state): return {}
                def route_eval(state) -> Literal["generate", END]:
                    return END if state.get("score", 0) >= 7 else "generate"
                b = StateGraph(RefState)
                b.add_node("generate", gen_n)
                b.add_node("evaluate", eval_n)
                b.add_edge(START, "generate")
                b.add_edge("generate", "evaluate")
                b.add_conditional_edges("evaluate", route_eval, {"generate": "generate", END: END})
                g = b.compile()
                caption = "Reflection: generate→evaluate→(back-edge to generate OR end). The cycle IS Andrew Ng Pattern 1."

            else:  # HITL
                def agent_n(state): return {}
                def guard_n(state): return {}
                def hitl_n(state): return {}
                def route_guard(state) -> Literal["hitl", "tools", END]: return END
                b = StateGraph(MessagesState)
                b.add_node("agent", agent_n)
                b.add_node("guard", guard_n)
                b.add_node("hitl",  hitl_n)
                b.add_node("tools", lambda s: {})
                b.add_edge(START, "agent")
                b.add_edge("agent", "guard")
                b.add_conditional_edges("guard", route_guard,
                                        {"hitl": "hitl", "tools": "tools", END: END})
                b.add_edge("hitl",  "tools")
                b.add_edge("tools", "agent")
                g = b.compile()
                caption = "HITL: guard intercepts tool calls; high-risk ones route through hitl node (interrupt point)."

            png = g.get_graph().draw_mermaid_png()
            st.image(png, caption=caption, use_container_width=False)
            st.success("draw_mermaid_png() rendered from the actual compiled graph — not a static image")

        except ImportError as e:
            st.warning(f"LangGraph not installed — showing static Mermaid source instead.\n\n{e}")
            if graph_choice.startswith("ReAct"):
                st.code("""
graph TD
    __start__ --> agent
    agent -->|tool_calls| tools
    agent -->|no tool_calls| __end__
    tools --> agent
""", language="text")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB: Streaming ────────────────────────────────────────────────────────────
with tab_stream:
    st.markdown("**Streaming — see each step as it completes (values mode)**")
    st.markdown("""
| Streaming Mode | What you see | Best for |
|---|---|---|
| `stream_mode="values"` | Full state after each node | Debugging, seeing all messages |
| `stream_mode="updates"` | Only state delta per node | Efficient, large states |
| `astream_events(version="v2")` | Token-by-token from LLM | Chat UI, live typewriter effect |
| No streaming (`.invoke()`) | Final state only | Batch processing, tests |
""")
    query = st.text_input("Query to stream:", value="What is LangGraph used for?", key="stream_q")
    if st.button("Stream response (simulated steps)", key="run_stream"):
        try:
            client = _client()
            import time

            steps = [
                ("START", "Input received: " + query[:60]),
                ("agent",  "Reasoning about the query..."),
                ("tools",  "No tool needed — direct answer"),
                ("agent",  "Generating final response..."),
                ("END",    None),
            ]
            trace_lines = []
            progress = st.progress(0)
            step_placeholder = st.empty()

            for i, (node, desc) in enumerate(steps[:-1]):
                progress.progress((i + 1) / len(steps))
                step_placeholder.info(f"**Node: `{node}`** — {desc}")
                trace_lines.append(f"[{node}] {desc}")
                time.sleep(0.3)

            # Final LLM call
            r = client.models.generate_content(model=MODEL, contents=query)
            step_placeholder.empty()
            progress.progress(1.0)

            st.success(r.text)
            st.caption("In a real LangGraph .stream() call, each `chunk` above is one state update")

            with st.expander("🔬 Execution Trace — streaming steps"):
                for line in trace_lines:
                    st.code(line, language="text")
                st.code("stream_mode='values': each chunk = full state after node completes\n"
                        "To get token-by-token: use graph.astream_events(version='v2')", language="text")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB: Production checklist ─────────────────────────────────────────────────
with tab_checklist:
    st.markdown("**Production Readiness Checklist — before deploying a LangGraph agent**")

    checklist = {
        "🧠 State & Persistence": [
            ("Checkpointer configured", "SqliteSaver for single-server; PostgresSaver for distributed"),
            ("Thread ID strategy decided", "Per-user? Per-session? Per-conversation? Be explicit"),
            ("State schema complete", "All fields typed with `Annotated` + reducers where needed"),
        ],
        "🛡️ Security": [
            ("Guard Agent in place", "Pre-tool security check node, especially for destructive tools"),
            ("HITL on high-risk tools", "`interrupt_before` or `interrupt()` on send_email, delete_*, etc."),
            ("No secrets in state", "API keys, tokens never stored in graph state or messages"),
            ("Input validation", "User message validated before entering graph (Phase 4a Guardrails)"),
        ],
        "📊 Observability (Phase 7a)": [
            ("LangSmith tracing enabled", "`LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY` in env"),
            ("Thread IDs logged", "Correlate LangSmith traces to user sessions"),
            ("Token budgets set", "Max token limit per run, cost alerting"),
        ],
        "🔁 Resilience (Phase 7c)": [
            ("Retry logic on LLM calls", "`tenacity` wrapper or LangChain `with_retry()`"),
            ("Durable checkpointing", "State survives process crash + restarts"),
            ("Max iterations guard", "Loop termination condition — prevents infinite cycles"),
        ],
        "🚀 Deployment": [
            ("draw_mermaid_png() verified", "Visual topology check before deploy"),
            ("Streaming tested", "All stream modes tested, UI handles partial states"),
            ("Load test done", "Multiple concurrent threads with different thread_ids"),
        ],
    }

    for category, items in checklist.items():
        st.markdown(f"#### {category}")
        for item, note in items:
            col1, col2 = st.columns([3, 5])
            with col1:
                st.checkbox(item, key=f"chk_{item[:20]}")
            with col2:
                st.caption(note)

    st.markdown("---")
    st.markdown("**Studio UI setup (free, local):**")
    st.code("""
# Install LangGraph Studio (Mac/Windows desktop app)
# Download: https://studio.langchain.com/download
#
# In your project root, create langgraph.json:
# {
#   "dependencies": ["."],
#   "graphs": {"my_agent": "./pages/06b_LangGraph_Agents.py:graph"},
#   "env": ".env"
# }
#
# Then open LangGraph Studio → point to this directory
# → visual graph debugger with state inspection + time-travel debugging
""", language="text")

    st.info(
        "**What you get with LangGraph Studio (not available without install):**\n"
        "- Visual graph with live state overlaid on nodes\n"
        "- Click any past checkpoint → fork and replay from that point\n"
        "- Inspect `state['messages']` at each step\n"
        "- Manual interrupt + resume without code changes\n"
        "- Works with any graph that has a checkpointer attached"
    )

st.markdown("---")
st.markdown("### What's next → Phase 10c (enhanced) — LangSmith: Prompt Hub, Alerts & Governance")
st.markdown(
    "Adding Prompt Hub, Feedback API, and Governance/Audit trails to the existing Phase 10c LangSmith page. "
    "Then Phase 10d LangChain gets Structured Output and the @tool ecosystem."
)
