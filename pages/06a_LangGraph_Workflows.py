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

from utils.diagrams import diagram_langgraph_workflows
from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🕸️ 10a — LangGraph Workflows")
st.caption(
    "Phase 2's 5 workflow patterns reimplemented as LangGraph state graphs. "
    "Same logic, typed state, built-in streaming and persistence."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(diagram_langgraph_workflows(),
         caption="Left: the raw Python you wrote in Phase 2. Right: LangGraph doing the same thing.",
         use_column_width=True)

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

    with col1:
        st.markdown("#### What you wrote in Phase 2a")
        if st.button("Run Manual", key="run_manual"):
            client = _client()
            def call(prompt):
                r = client.models.generate_content(model=MODEL, contents=prompt)
                return r.text.strip()
            with st.spinner("Running manual chain..."):
                outline = call(f"Write a 3-point blog outline for: {topic}")
                draft   = call(f"Write a short intro paragraph from this outline:\n{outline}")
                final   = call(f"Tighten this paragraph to 2 sentences:\n{draft}")
            raw_trace = [("outline_prompt", f"Write a 3-point blog outline for: {topic}", outline),
                         ("draft_prompt",   f"Write a short intro paragraph from outline", draft),
                         ("polish_prompt",  "Tighten to 2 sentences", final)]
            st.success(final)
            st.caption("3 sequential LLM calls, manual result-passing")

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
st.markdown("### What's next → Phase 10b — LangGraph Agents")
st.markdown(
    "Phase 3's ReAct, Reflection, Planning, and HITL patterns as LangGraph agent graphs. "
    "`interrupt_before` replaces 40 lines of manual HITL code."
)
