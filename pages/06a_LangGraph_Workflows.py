"""
Phase 10a — LangGraph Workflows
Bridges Phase 2 (Workflow Patterns) to LangGraph StateGraph.
Every Phase 2 pattern reimplemented as a typed state graph.
"""
import os
import json
import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator

load_dotenv()

st.set_page_config(
    page_title="10a — LangGraph Workflows",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.diagrams import diagram_lang_arch_map
from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🕸️ 10a — LangGraph Workflows")
st.caption(
    "Phase 2's 5 workflow patterns reimplemented as LangGraph state graphs. "
    "Same logic, typed state, built-in streaming and persistence."
)

# ── Architecture Map anchor ────────────────────────────────────────────────────
with st.expander("🗺️ Full Architecture Map — LangChain + LangGraph (read this first)", expanded=False):
    st.image(diagram_lang_arch_map(), use_container_width=True,
             caption="LangChain + LangGraph Agentic AI Architecture — every layer maps to course phases you already built")
    st.markdown("""
**How to read this diagram — course cross-reference:**

| Layer | What it is | Course phases that cover it | This Phase 10 page |
|---|---|---|---|
| **1 — Entry** | How requests enter the system (API, chat, docs) | Phase 1 (Augmented LLM) | —  |
| **2 — Orchestration** | StateGraph, conditional routing, subgraphs | Phase 2 (Workflow Patterns) | **10a — this page** |
| **3 — Agent Nodes** | ReAct, Reflection, Supervisor, Guard, Planner | Phase 3 (Core Agents) | **10b** |
| **4 — Memory & Context** | Checkpointers, Memory Store, Vector Store | Phase 1b, 5a, 5b | **10b2** |
| **5 — Tools** | @tool, ToolNode, MCP adapters, Guard Agent | Phase 1c, 4a, 4b, 6b | **10b3** |
| **6 — Model Layer** | Chat LLMs, Embeddings, Structured Output | Throughout course | **10d** |
| **LangSmith panel** | Auto-tracing, evals, Prompt Hub | Phase 7a, 4d | **10c** |
| **Platform panel** | Deploy, Studio UI, Durable Execution | Phase 7 (Production) | **10b4** |
| **Agent Loop panel** | Perceive→Reason→Act→Evaluate→Persist | Andrew Ng's 4 patterns | **10b + 10b4** |

**Key insight:** You have already built every concept in this diagram — in Phases 1–9 using raw Python.
Phase 10 shows you the same patterns expressed through the LangChain/LangGraph framework layer.
""")

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image("docs/images/arch_langgraph_workflows.jpg",
         caption="Phase 2's 5 workflow patterns mapped to their LangGraph StateGraph equivalents.",
         use_container_width=True)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 2 — Workflow Patterns)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 2 you wrote each workflow step as a Python function and wired them together by
    passing variables: <code>out2 = llm(prompt + out1)</code>. That <em>is</em> a LangGraph workflow —
    your functions become <strong>nodes</strong>, your variable-passing becomes <strong>edges</strong>,
    and the shared result dict becomes a typed <strong>State</strong>.<br><br>
    Think of it like this: Phase 2 was a relay race where runners hand off a baton manually.
    LangGraph is the same race — same runners, same baton — but now there is a timing system,
    a replay button, and a built-in pause for a coach to intervene.
    The race does not change. The infrastructure around it does.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is LangGraph — and what does it add over Phase 2?"):
    st.markdown("""
**LangGraph is NOT a new concept.** It is a graph execution engine that formalises the
Phase 2 workflow patterns you already built manually.

| Phase 2 Manual | LangGraph Equivalent |
|---|---|
| `result = step1(input)` then `result2 = step2(result)` | Linear graph: `node_A → node_B` |
| `if route == 'A': handler_A(input)` | Conditional edge: `classify_node → {A: node_A, B: node_B}` |
| `ThreadPoolExecutor` fan-out | Fan-out edges to parallel nodes |
| `while score < threshold:` loop | Cycle: `generate → evaluate → (loop or END)` |
| Orchestrator delegates to workers | Subgraph delegation |

**What LangGraph adds over your manual Phase 2 code:**

| Feature | Phase 2 Manual | LangGraph |
|---|---|---|
| Shared state | You pass dicts manually | TypedDict — typed, validated |
| Streaming | Not built-in | `graph.stream()` yields per-node |
| Persistence | Not built-in | `checkpointer=MemorySaver()` |
| HITL-ready | Manual checkpoint code | `interrupt_before=["node"]` |
| Visualisation | Not built-in | `graph.get_graph().draw_mermaid()` |

**Key insight:** LangGraph's `StateGraph` is your manual for-loop over workflow steps
with typed state, streaming, and persistence bolted on. The patterns are identical.
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — LangGraph StateGraph"):
    st.code('''
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Define typed shared state (replaces manual dict-passing)
class BlogState(TypedDict):
    topic: str
    outline: str
    draft: str
    final: str

# 2. Define nodes — each is just a function that updates state
def outline_node(state: BlogState) -> BlogState:
    state["outline"] = llm(f"Write outline for: {state['topic']}")
    return state

def draft_node(state: BlogState) -> BlogState:
    state["draft"] = llm(f"Write draft from outline: {state['outline']}")
    return state

def polish_node(state: BlogState) -> BlogState:
    state["final"] = llm(f"Polish this draft: {state['draft']}")
    return state

# 3. Build the graph — add nodes and edges
graph = StateGraph(BlogState)
graph.add_node("outline", outline_node)
graph.add_node("draft",   draft_node)
graph.add_node("polish",  polish_node)
graph.add_edge(START,     "outline")
graph.add_edge("outline", "draft")
graph.add_edge("draft",   "polish")
graph.add_edge("polish",  END)

# 4. Compile and run
app = graph.compile()
result = app.invoke({"topic": "Agentic AI in 2025"})

# Compare to Phase 2a manual:
# out1 = llm(outline_prompt)
# out2 = llm(draft_prompt + out1)
# out3 = llm(polish_prompt + out2)
''', language="python")
    st.markdown("""
**What changed from Phase 2a:** The logic is identical. LangGraph gives you a typed
`BlogState` dict so each node's inputs and outputs are validated. The graph structure
is declarative — you describe connections, the engine handles execution order.

**Production win:** Add `checkpointer=MemorySaver()` to `compile()` and the graph state
is persisted across interrupts — enabling HITL without any extra code.
""")

st.markdown("---")

# ── Interactive demo ──────────────────────────────────────────────────────────
st.markdown("### Interactive Demo — Phase 2 Pattern Side-by-Side")

tab_chain, tab_route, tab_eval = st.tabs([
    "2a Prompt Chaining → LangGraph",
    "2b Routing → Conditional Edge",
    "2e Evaluator-Optimizer → Cycle",
])

# ── TAB: Chaining ─────────────────────────────────────────────────────────────
with tab_chain:
    st.markdown("**Same blog pipeline — manual Phase 2a vs LangGraph**")
    topic = st.text_input("Blog topic:", value="Why agentic AI changes software development", key="lg_topic")

    col1, col2 = st.columns(2)
    raw_trace = lg_trace = []

    # Session state for manual chain results (persists across reruns)
    if "manual_2a_rows" not in st.session_state:
        st.session_state.manual_2a_rows = None

    with col1:
        st.markdown("#### What you wrote in Phase 2a")
        if st.button("Run Manual", key="run_manual"):
            client = _client()
            def call(prompt):
                r = client.models.generate_content(model=MODEL, contents=prompt)
                return r.text.strip()
            with st.spinner("Running manual chain..."):
                p1 = f"Write a 3-point blog outline for: {topic}"
                outline = call(p1)
                p2 = f"Write a short intro paragraph from this outline:\n{outline}"
                draft   = call(p2)
                p3 = f"Tighten this paragraph to 2 sentences:\n{draft}"
                final   = call(p3)
            raw_trace = [("outline_prompt", p1, outline),
                         ("draft_prompt",   p2, draft),
                         ("polish_prompt",  p3, final)]
            st.session_state.manual_2a_rows = [
                {"Step": "1 — Outline", "Input sent to LLM": p1,      "Output received": outline},
                {"Step": "2 — Draft",   "Input sent to LLM": p2,      "Output received": draft},
                {"Step": "3 — Polish",  "Input sent to LLM": p3,      "Output received": final},
            ]
            st.success(final)
            st.caption("3 sequential LLM calls — output of each step feeds the next")

        if st.session_state.manual_2a_rows:
            st.markdown("**What was passed in and what came back — per step:**")
            st.dataframe(
                st.session_state.manual_2a_rows,
                use_container_width=True,
                column_config={
                    "Step": st.column_config.TextColumn("Step", width=120),
                    "Input sent to LLM": st.column_config.TextColumn(
                        "Input sent to LLM", width="large"),
                    "Output received": st.column_config.TextColumn(
                        "Output received", width="large"),
                },
            )

    with col2:
        st.markdown("#### LangGraph StateGraph")
        if st.button("Run LangGraph", key="run_lg"):
            try:
                from langgraph.graph import StateGraph, START, END
                from langchain_google_genai import ChatGoogleGenerativeAI

                class BlogState(TypedDict):
                    topic: str
                    outline: str
                    draft: str
                    final: str

                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                )

                def outline_node(state: BlogState):
                    r = llm.invoke(f"Write a 3-point blog outline for: {state['topic']}")
                    return {"outline": r.content}

                def draft_node(state: BlogState):
                    r = llm.invoke(f"Write a short intro paragraph from this outline:\n{state['outline']}")
                    return {"draft": r.content}

                def polish_node(state: BlogState):
                    r = llm.invoke(f"Tighten this paragraph to 2 sentences:\n{state['draft']}")
                    return {"final": r.content}

                g = StateGraph(BlogState)
                g.add_node("outline", outline_node)
                g.add_node("draft",   draft_node)
                g.add_node("polish",  polish_node)
                g.add_edge(START, "outline")
                g.add_edge("outline", "draft")
                g.add_edge("draft",   "polish")
                g.add_edge("polish",  END)

                app = g.compile()

                lg_steps = []
                with st.spinner("Running LangGraph..."):
                    for step in app.stream({"topic": topic, "outline": "", "draft": "", "final": ""}):
                        node_name = list(step.keys())[0]
                        lg_steps.append((node_name, step[node_name]))
                        st.caption(f"✓ node `{node_name}` complete")

                final_state = lg_steps[-1][1]
                st.success(final_state.get("final", ""))
                st.caption("Same 3 LLM calls — but streaming per-node, typed state")
                lg_trace = lg_steps

            except Exception as e:
                st.error(f"LangGraph error: {e}")

    with st.expander("🔍 What just happened — Translation"):
        st.markdown("""
| Phase 2a Manual | LangGraph Equivalent | What changed |
|---|---|---|
| `out1 = call(prompt1)` | `outline_node(state)` | Function updates typed state dict |
| `out2 = call(prompt2 + out1)` | `draft_node(state)` | State automatically carries `outline` |
| `out3 = call(prompt3 + out2)` | `polish_node(state)` | State automatically carries `draft` |
| Manual `add_edge` logic | `graph.add_edge("outline","draft")` | Declared, not imperative |
| No streaming | `app.stream(input)` | Each node result yields immediately |
""")

    with st.expander("🔬 Execution Trace"):
        st.code(f"LangGraph steps: {[s[0] for s in lg_trace] if lg_trace else '(not run)'}", language="text")

# ── TAB: Routing ──────────────────────────────────────────────────────────────
with tab_route:
    st.markdown("**Phase 2b Routing → LangGraph conditional edge**")
    st.markdown("""
| Phase 2b Manual | LangGraph Equivalent |
|---|---|
| `route = classify(input)` | `classify_node(state)` writes `state["route"]` |
| `if route == 'A': handler_A(input)` | `add_conditional_edges("classify", router_fn, {A: "node_A", B: "node_B"})` |
| Handler returns result | Destination node updates state |
""")
    st.code('''
def classify_node(state):
    category = llm(f"Classify as TECHNICAL or GENERAL: {state['query']}")
    return {"route": category.strip()}

def router_fn(state):            # returns node name to go to
    return state["route"]

graph.add_conditional_edges(
    "classify",
    router_fn,
    {"TECHNICAL": "tech_handler", "GENERAL": "general_handler"}
)
''', language="python")
    st.info("**Key insight:** The routing logic is identical to Phase 2b. LangGraph just makes the branching explicit in the graph structure rather than an if/else block.")

# ── TAB: Evaluator-Optimizer ──────────────────────────────────────────────────
with tab_eval:
    st.markdown("**Phase 2e Evaluator-Optimizer → LangGraph cycle**")
    st.markdown("""
| Phase 2e Manual | LangGraph Equivalent |
|---|---|
| `while score < threshold and i < MAX:` | Conditional back-edge from evaluate → generate |
| `draft = generate(prompt)` | `generate_node(state)` |
| `score = evaluate(draft)` | `evaluate_node(state)` writes `state["score"]` |
| `if score >= threshold: break` | `router_fn` returns `END` when `state["score"] >= threshold` |
| `MAX_ITER` guard | `recursion_limit` on `graph.compile()` |
""")
    st.code('''
def generate_node(state):
    state["draft"] = llm(state["task"])
    state["iteration"] = state.get("iteration", 0) + 1
    return state

def evaluate_node(state):
    score_text = llm(f"Score 1-10: {state['draft']}")
    state["score"] = int(score_text.strip()[0])
    return state

def route_after_eval(state):
    if state["score"] >= 7 or state["iteration"] >= 3:
        return END
    return "generate"   # loop back

graph.add_conditional_edges("evaluate", route_after_eval,
                            {"generate": "generate", END: END})
app = graph.compile(recursion_limit=10)   # replaces while i < MAX_ITER
''', language="python")
    st.info("**Key insight:** The `recursion_limit` replaces your manual `while i < MAX_ITER` guard. The loop structure is identical — LangGraph just makes the cycle a first-class graph edge.")

st.markdown("---")

# ── State Management deep-dive ────────────────────────────────────────────────
with st.expander("📐 State Management — Annotated fields, reducers, and the add_messages pattern"):
    st.markdown("""
**Why reducers matter:** When a graph node returns a value, LangGraph needs to know
*how* to merge it into the shared state. By default it overwrites. A **reducer** changes that.

| State field type | What happens on update | Use case |
|---|---|---|
| Plain `str`, `int` | Overwritten — last write wins | counters, scores, current status |
| `Annotated[list, operator.add]` | Appended — each update extends the list | collecting results across parallel nodes |
| `Annotated[list, add_messages]` | Messages appended, deduped by ID | conversation history (the standard pattern) |
""")
    st.code('''
from typing import TypedDict, Annotated
import operator
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

# ── Option 1: plain field (overwrites) ────────────────────────────────────────
class SimpleState(TypedDict):
    score: int          # each node that sets score= overwrites the previous value

# ── Option 2: Annotated list (appends) ───────────────────────────────────────
class CollectState(TypedDict):
    results: Annotated[list, operator.add]   # parallel nodes each contribute
    # node A returns {"results": ["A done"]}
    # node B returns {"results": ["B done"]}
    # final state: {"results": ["A done", "B done"]}  ← merged, not overwritten

# ── Option 3: add_messages (the standard for chat agents) ────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # handles HumanMessage/AIMessage/ToolMessage
    # add_messages also deduplicates by message id — safe for streaming

# ── Every LangGraph agent uses this pattern: ──────────────────────────────────
from langgraph.prebuilt import create_react_agent
# create_react_agent uses MessagesState internally — which is just:
# class MessagesState(TypedDict):
#     messages: Annotated[list, add_messages]
''', language="python")
    st.info("**Phase 1b connection:** You manually did `history.append(turn)` on every call. "
            "`add_messages` is that exact append — but declared once in the state type and applied automatically.")

# ── Subgraphs ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Advanced Patterns — Subgraphs and Map-Reduce")
tab_sub, tab_mr = st.tabs(["🔲 Subgraphs — Modular Composition", "🔀 Map-Reduce — Parallel Fan-Out"])

with tab_sub:
    st.markdown("**Subgraphs** let you nest one `StateGraph` inside another — modular composition at graph level.")
    st.markdown("""
| Phase 2d Manual | Subgraph Equivalent |
|---|---|
| `orchestrator_fn()` calls `worker_fn()` directly | Parent graph node delegates to compiled sub-graph |
| Worker result returned as dict | Sub-graph has its own `State` and `START/END` |
| No isolation between orchestrator and workers | Sub-graph state is encapsulated |
| Difficult to reuse worker logic | Sub-graph compiles once, reused anywhere |
""")
    st.code('''
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# ── Sub-graph: a complete workflow in itself ──────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    summary: str

def search_node(state: ResearchState):
    return {"summary": f"Search results for: {state['topic']}"}

def summarise_node(state: ResearchState):
    return {"summary": f"Summary: {state['summary'][:100]}"}

research_sg = StateGraph(ResearchState)
research_sg.add_node("search",    search_node)
research_sg.add_node("summarise", summarise_node)
research_sg.add_edge(START, "search")
research_sg.add_edge("search", "summarise")
research_sg.add_edge("summarise", END)
research_compiled = research_sg.compile()   # ← a complete runnable

# ── Parent graph: treats sub-graph as a node ──────────────────────────────────
class PaperState(TypedDict):
    topic: str
    summary: str     # passed in/out of sub-graph
    final_paper: str

def write_node(state: PaperState):
    return {"final_paper": f"Paper about {state['topic']}:\\n\\n{state['summary']}"}

parent = StateGraph(PaperState)
parent.add_node("research", research_compiled)   # ← sub-graph as a node
parent.add_node("write",    write_node)
parent.add_edge(START,      "research")
parent.add_edge("research", "write")
parent.add_edge("write",    END)
app = parent.compile()
result = app.invoke({"topic": "Agentic AI", "summary": "", "final_paper": ""})
''', language="python")
    st.info("**Key insight:** `research_compiled` is just another node to the parent graph. "
            "You can share, version, and test sub-graphs independently — the same modular design "
            "you would use in any software system.")

    # Live demo
    if st.button("Run subgraph demo", key="run_subgraph"):
        try:
            from langgraph.graph import StateGraph, START, END
            from langchain_google_genai import ChatGoogleGenerativeAI
            from typing import TypedDict
            import os

            class ResearchState(TypedDict):
                topic: str; summary: str

            class PaperState(TypedDict):
                topic: str; summary: str; final_paper: str

            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                         google_api_key=os.getenv("GEMINI_API_KEY"))

            def search_node(state):
                r = llm.invoke(f"Give 3 bullet-point facts about: {state['topic']}")
                return {"summary": r.content}

            def write_node(state):
                r = llm.invoke(f"Write a 2-sentence paper intro using these facts:\n{state['summary']}")
                return {"final_paper": r.content}

            sg = StateGraph(ResearchState)
            sg.add_node("search", search_node)
            sg.add_edge(START, "search"); sg.add_edge("search", END)
            sg_compiled = sg.compile()

            pg = StateGraph(PaperState)
            pg.add_node("research", sg_compiled)
            pg.add_node("write", write_node)
            pg.add_edge(START, "research"); pg.add_edge("research", "write"); pg.add_edge("write", END)
            app = pg.compile()

            topic = st.session_state.get("subgraph_topic", "Agentic AI in 2026")
            with st.spinner("Running parent → sub-graph → write..."):
                steps = []
                for chunk in app.stream({"topic": topic, "summary": "", "final_paper": ""}):
                    for node, data in chunk.items():
                        steps.append((node, data))
                        st.caption(f"✓ node `{node}` complete")

            final = steps[-1][1]
            st.success(final.get("final_paper", ""))
            with st.expander("🔬 Execution Trace — subgraph flow"):
                for name, data in steps:
                    st.markdown(f"**Node `{name}`:** {list(data.keys())}")
        except Exception as e:
            st.error(f"Error: {e}")

    topic_in = st.text_input("Topic:", value="Agentic AI in 2026", key="subgraph_topic")

with tab_mr:
    st.markdown("**Map-Reduce** fans out to N parallel nodes, each writes to an `Annotated[list]` field, "
                "then a reducer merges all results automatically.")
    st.markdown("""
| Phase 2c Manual | LangGraph Map-Reduce |
|---|---|
| `ThreadPoolExecutor` fan-out | `Send()` API fans out dynamically |
| Manual `results.append(r)` in each thread | `Annotated[list, operator.add]` reducer merges |
| Fixed number of workers | Dynamic: N determined at runtime |
| Manual merge step | Merge is automatic via reducer |
""")
    st.code('''
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
import operator

class MapState(TypedDict):
    topics: list[str]                            # input: N topics
    summaries: Annotated[list, operator.add]     # reducer: each node appends

class WorkerState(TypedDict):
    topic: str
    summaries: Annotated[list, operator.add]

# Fan-out function: returns a Send() for each item ─── this IS the map
def fan_out(state: MapState):
    return [Send("summarise", {"topic": t, "summaries": []}) for t in state["topics"]]

# Worker node: processes ONE item, appends to shared list
def summarise(state: WorkerState):
    summary = llm(f"Summarise in 1 sentence: {state['topic']}")
    return {"summaries": [summary]}              # list — reducer appends this

# Reduce node: all summaries already merged by reducer
def aggregate(state: MapState):
    combined = "\\n".join(f"• {s}" for s in state["summaries"])
    return {"summaries": [f"COMBINED:\\n{combined}"]}

g = StateGraph(MapState)
g.add_node("summarise", summarise)
g.add_node("aggregate", aggregate)
g.add_conditional_edges(START, fan_out, ["summarise"])   # dynamic fan-out
g.add_edge("summarise", "aggregate")
g.add_edge("aggregate", END)
app = g.compile()

result = app.invoke({"topics": ["ReAct","Reflection","Planning"], "summaries": []})
# result["summaries"] = ["• ReAct: ...", "• Reflection: ...", "• Planning: ...", "COMBINED: ..."]
''', language="python")
    st.info("**Key insight:** The `Annotated[list, operator.add]` reducer is what enables safe parallel writes. "
            "Each worker node runs independently and returns `{\"summaries\": [its_result]}`. "
            "LangGraph merges all the lists automatically — no locks, no race conditions.")

st.markdown("---")
st.markdown("### What's next → Phase 10b — LangGraph Agents")
st.markdown(
    "Phase 3's ReAct, Reflection, Planning, and HITL patterns as LangGraph agent graphs. "
    "`interrupt_before` replaces 40 lines of manual HITL code."
)
