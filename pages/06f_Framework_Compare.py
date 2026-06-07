"""
Phase 10f — Framework Comparison
Raw SDK vs LangGraph vs LangChain LCEL vs LangSmith vs Google ADK.
Decision guide: when to add each layer and what you gain vs what you pay.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10f — Framework Compare",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("⚖️ 10f — Framework Compare")
st.caption(
    "Raw SDK vs LangGraph vs LangChain LCEL vs LangSmith vs Google ADK — "
    "when to add each layer, what it costs, and how to choose."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(
    "docs/images/arch_framework_compare.jpg",
    caption=(
        "Top: where each framework sits on the abstraction vs agent-readiness landscape. "
        "Bottom: the layered stack — Raw SDK is always the foundation; every other layer is optional."
    ),
    use_container_width=True,
)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 What you already know — and what this phase adds</span><br><br>
    <span style='color:#1C2833'>
    In Phases 1–9 you built everything with the Raw SDK: memory, tools, ReAct, Reflection,
    Planning, RAG, HITL, Guardrails, Multi-Agent, MCP, A2A, Observability, Cost tracking, Error Analysis.
    <strong>None of that required a framework.</strong><br><br>
    In Phases 10a–10d you saw the same patterns expressed in LangGraph, LangSmith, and LangChain LCEL.
    The patterns did not change — the plumbing did.<br><br>
    This page answers the question every engineer faces: <em>given a real production requirement,
    which of these do I actually reach for, and why?</em>
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept Expander ──────────────────────────────────────────────────────────
with st.expander("📖 What each framework does — and what it costs"):
    st.markdown("""
**The core principle:** Raw SDK is always sufficient. Frameworks solve recurring plumbing problems —
they do not unlock new capabilities. Choose a framework when the plumbing it replaces is painful enough
to justify the dependency.

| # | Framework | What it solves | What you give up |
|---|---|---|---|
| 1 | **Raw SDK** | Full control, zero abstraction, complete visibility into every call | You write all plumbing: history, loops, HITL, streaming, persistence |
| 2 | **LangGraph** | Typed state, automatic graph execution, HITL via `interrupt_before`, persistence via checkpointer, streaming built in | Graph mental model, new dependency, harder to debug node transitions |
| 3 | **LangChain LCEL** | Pipe syntax for chains, streaming/batching on any chain, Chroma RAG retriever | Extra dependency, abstraction over retriever internals, less control over embedding calls |
| 4 | **LangSmith** | Auto-tracing every call, datasets, LLM-as-Judge evals, cost/latency dashboards | Requires LangChain/LangGraph integration, external service dependency |
| 5 | **Google ADK** | Managed multi-agent on Google Cloud, built-in A2A, deployment infrastructure | Strong Google Cloud vendor lock-in, higher operational overhead |
| 6 | **CrewAI** (Phase 10g) | Role-based crews in ~20 lines; sequential/hierarchical process built-in; quick prototyping | Less fine-grained control than LangGraph; harder to debug mid-crew; abstraction hides agent communication |
| 7 | **AutoGen / AG2** | Conversational multi-agent debates; group chats; consensus-building between agents | High token cost per turn (every agent sees full conversation); Microsoft deprecated v1 in favour of AG2 |

**The hidden cost that tables don't show:**

| # | Concern | Detail |
|---|---|---|
| 1 | Debugging | Framework abstractions hide errors — a node failure in LangGraph gives a different traceback than a raw SDK call |
| 2 | Version drift | LangChain/LangGraph release frequently; breaking changes are common — raw SDK is more stable |
| 3 | Testability | Raw SDK functions are plain Python — trivial to unit test; LangGraph nodes need graph context |
| 4 | Portability | LCEL and LangGraph tie you to LangChain's model wrappers; switching LLM providers requires adapter changes |
| 5 | Learning curve | LangGraph's StateGraph + conditional edges + checkpointers takes ~1 day to internalise |
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — Same task, 3 implementations"):
    st.markdown("**Task:** Summarise a passage in 3 bullet points, then translate the summary to French.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Raw SDK — Phase 2a Chaining")
        st.code('''
# Step 1: summarise
r1 = client.models.generate_content(
    model=MODEL,
    contents=f"Summarise in 3 bullets:\\n{passage}",
)
summary = r1.text

# Step 2: translate
r2 = client.models.generate_content(
    model=MODEL,
    contents=f"Translate to French:\\n{summary}",
)
french = r2.text
''', language="python")
        st.caption("2 explicit calls. Every line visible. No dependencies.")

    with col2:
        st.markdown("#### LangGraph — as a StateGraph")
        st.code('''
from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict):
    passage: str
    summary: str
    french: str

def summarise(s):
    r = llm.invoke(
        f"Summarise in 3 bullets:\\n{s['passage']}"
    )
    return {"summary": r.content}

def translate(s):
    r = llm.invoke(
        f"Translate to French:\\n{s['summary']}"
    )
    return {"french": r.content}

g = StateGraph(S)
g.add_node("summarise", summarise)
g.add_node("translate", translate)
g.set_entry_point("summarise")
g.add_edge("summarise", "translate")
g.add_edge("translate", END)
chain = g.compile()

result = chain.invoke({"passage": passage})
''', language="python")
        st.caption("Same 2 calls. Typed state, streaming, HITL-ready. ~3x more code for this task.")

    with col3:
        st.markdown("#### LangChain LCEL — as a pipe chain")
        st.code('''
from langchain_core.prompts import (
    ChatPromptTemplate
)
from langchain_core.output_parsers import (
    StrOutputParser
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)
parser = StrOutputParser()

summarise = (
    ChatPromptTemplate.from_template(
        "Summarise in 3 bullets:\\n{passage}"
    ) | llm | parser
)
translate = (
    ChatPromptTemplate.from_template(
        "Translate to French:\\n{summary}"
    ) | llm | parser
)
chain = (
    summarise
    | (lambda s: {"summary": s})
    | translate
)
french = chain.invoke({"passage": passage})
''', language="python")
        st.caption("Pipe syntax, streaming built-in. LangChain model wrapper required.")

    st.markdown("""
**Key insight:** All three produce identical outputs. The Raw SDK version is the shortest
and most debuggable. LangGraph pays off when you need HITL or persistence. LCEL pays off
when you have 5+ chain steps or need `.stream()` with no extra code.
""")

st.markdown("---")

# ── Interactive Demo ──────────────────────────────────────────────────────────
st.markdown("### Interactive Demo")

tab_guide, tab_compare, tab_task = st.tabs([
    "🗺️ Decision Guide",
    "📊 Feature Comparison Tables",
    "🔄 Same Task — Raw SDK Live",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Decision Guide
# ──────────────────────────────────────────────────────────────────────────────
with tab_guide:
    st.markdown(
        "Describe your project requirements and get a framework recommendation "
        "with justification — generated by Gemini."
    )

    SCENARIOS = {
        "Custom scenario (type below)": "",
        "Simple chatbot — no tools, no persistence": (
            "I need a simple chatbot. Single-turn or multi-turn conversation. "
            "No tool calls, no persistence across browser sessions, no streaming needed. "
            "Team is small, minimising dependencies is important."
        ),
        "ReAct agent with HITL approval before every tool call": (
            "I need a ReAct agent that calls 3-4 external APIs as tools. "
            "Before each tool call I need a human to approve or reject it. "
            "Results must persist across page refreshes. I need streaming output."
        ),
        "RAG pipeline over a document corpus": (
            "I need a retrieval-augmented generation pipeline. "
            "Users upload documents, they get chunked and embedded. "
            "On each query, top-3 chunks are retrieved and injected into the prompt. "
            "I also need to stream the response token by token to the UI."
        ),
        "Production multi-agent system on Google Cloud": (
            "I need 5 specialised agents collaborating on complex research tasks. "
            "The system runs on Google Cloud. I need deployment, scaling, monitoring, "
            "and inter-agent communication handled by the infrastructure."
        ),
        "Existing Phase 7 observability — want to automate it": (
            "I already have a working agent built with the Raw SDK. "
            "I manually collect traces, latency, and token counts (Phase 7). "
            "I want automatic tracing, a visual dashboard, and LLM-as-Judge evals "
            "run against a golden dataset without writing the eval loop myself."
        ),
        "Multi-agent team — quick prototype, role-based": (
            "I need a multi-agent system with 3-4 specialised agents (researcher, analyst, writer). "
            "Each agent has a distinct role and should stay in character. "
            "I want to prototype quickly — willing to sacrifice fine-grained control for speed. "
            "Sequential execution is fine for now."
        ),
        "Conversational agent debate — consensus from multiple LLMs": (
            "I need multiple AI agents to debate a complex question and reach consensus. "
            "Each agent has a different perspective. "
            "I want them to exchange messages in a group chat until they agree. "
            "Research/experimentation environment, not production."
        ),
    }

    preset = st.selectbox("Pick a scenario or describe your own:", list(SCENARIOS.keys()))
    default_text = SCENARIOS[preset]
    requirements = st.text_area(
        "Your requirements:",
        value=default_text,
        height=120,
        placeholder="Describe what your system needs to do, what constraints you have...",
        key="guide_req",
    )

    if st.button("Get Framework Recommendation", key="guide_btn", type="primary"):
        if not requirements.strip():
            st.warning("Please describe your requirements first.")
        else:
            with st.spinner("Analysing requirements..."):
                sys_prompt = """You are a senior AI engineering architect with deep experience
building production agentic systems. You know exactly when each framework layer earns its place
and when it adds unnecessary complexity.

The frameworks available are:
1. Raw SDK — the LLM provider's own client library. No abstraction.
2. LangGraph — workflow/agent graphs with typed state, streaming, persistence, HITL.
3. LangChain LCEL — pipe syntax for chains, streaming, RAG retriever integration.
4. LangSmith — observability layer: auto-tracing, datasets, evals. Wraps LangGraph/LCEL.
5. Google ADK — managed multi-agent platform on Google Cloud infrastructure.
6. CrewAI — role-based multi-agent crews; sequential/hierarchical process; quick prototyping.
7. AutoGen/AG2 — conversational multi-agent debates; group chats; consensus-building.

Your recommendation must be specific: name exactly which framework(s) to use and which to skip.
Explain the single most important reason to add each recommended framework.
Explain the single most important cost or trade-off of each recommended framework.
End with a one-sentence 'start here' instruction."""

                user_msg = (
                    f"My requirements:\n{requirements}\n\n"
                    "Recommend which frameworks to use (from the 7 above), which to skip, and why.\n"
                    "Be direct and opinionated. Use this format:\n\n"
                    "**Recommended stack:** [list frameworks]\n"
                    "**Skip:** [list what to skip and why]\n\n"
                    "For each recommended framework:\n"
                    "- **Why add it:** [single most important reason]\n"
                    "- **Cost:** [single most important trade-off]\n\n"
                    "**Start here:** [one clear first action]"
                )

                try:
                    response = _client().models.generate_content(
                        model=MODEL,
                        contents=user_msg,
                        config={"system_instruction": sys_prompt},
                    )
                    rec_text = response.text
                    st.markdown("### Recommendation")
                    st.markdown(rec_text)

                    with st.expander("🔬 Execution Trace — exact prompts and raw response"):
                        t1, t2 = st.tabs(["① Prompts", "② Raw Response"])
                        with t1:
                            st.markdown("**System prompt:**")
                            st.code(sys_prompt, language="text")
                            st.markdown("**User message:**")
                            st.code(user_msg, language="text")
                        with t2:
                            st.code(rec_text, language="text")
                except Exception as e:
                    st.error(f"Error: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Feature Comparison Tables
# ──────────────────────────────────────────────────────────────────────────────
with tab_compare:
    st.markdown("#### Feature Comparison — Raw SDK vs LangGraph vs LCEL vs LangSmith vs ADK")

    st.markdown("""
| # | Feature | Raw SDK | LangGraph | LangChain LCEL | LangSmith | Google ADK |
|---|---|---|---|---|---|---|
| 1 | ReAct agent loop | Manual while-loop | create_react_agent() | Not designed for it | — | Built-in |
| 2 | HITL before tool call | ~40 lines | interrupt_before (2 lines) | Not supported | — | Supported |
| 3 | Streaming output | generate_content_stream() | graph.stream() | chain.stream() | — | Supported |
| 4 | Persistent state | Manual (DB / session) | MemorySaver / checkpointer | Not built-in | — | Managed |
| 5 | RAG retriever | Manual cosine loop | Via LangChain integration | Chroma built-in | — | Supported |
| 6 | Auto tracing | Manual TraceCollector | Not automatic | Not automatic | 3 env vars | Not automatic |
| 7 | Eval against datasets | Manual | Manual | Manual | evaluate() built-in | Manual |
| 8 | Multi-agent | Manual (Phase 6) | Multi-graph supported | Not designed for it | — | Managed |
| 9 | Lines for simple chain | ~4 | ~25 | ~12 | n/a | ~20+ |
| 10 | External dependencies | 0 | langgraph | langchain-core + adapters | langsmith + LCEL | google-adk |
| 11 | LLM portability | Any provider | Any via LangChain wrapper | Any via LangChain wrapper | Any | Google Cloud LLMs |
| 12 | Debuggability | Highest — plain Python | Node graph errors | Chain abstraction | Visual UI | Managed opacity |
""")

    st.markdown("#### When to Use — Decision Rules")
    st.markdown("""
| # | If you need... | Reach for... | Skip... |
|---|---|---|---|
| 1 | Simple chatbot, Q&A, single-step tasks | Raw SDK only | Everything else |
| 2 | HITL approval before tool calls | + LangGraph | LCEL (not designed for it) |
| 3 | Persistent memory across sessions | + LangGraph checkpointer | Manual DB wiring |
| 4 | RAG pipeline with streaming | + LangChain LCEL + Chroma | LangGraph (overkill for linear RAG) |
| 5 | Production tracing + cost dashboards | + LangSmith | Manual TraceCollector |
| 6 | LLM-as-Judge evals on a dataset | + LangSmith evaluate() | Manual eval loop |
| 7 | 5+ agents on Google Cloud | + Google ADK | LangGraph (wrong deployment target) |
| 8 | Maximum debuggability | Raw SDK only | All frameworks |
| 9 | Team unfamiliar with LangChain | Raw SDK + LangGraph only | LCEL (extra learning curve) |
| 10 | Framework-agnostic, portable code | Raw SDK only | LCEL / ADK (vendor coupling) |
""")

    st.markdown("#### Code Complexity — Approximate lines for common tasks")
    st.markdown("""
| # | Task | Raw SDK | LangGraph | LangChain LCEL |
|---|---|---|---|---|
| 1 | Single LLM call | 3 | 20 | 8 |
| 2 | 2-step chain | 6 | 30 | 15 |
| 3 | ReAct agent (5 tools) | 35 | 8 | Not applicable |
| 4 | HITL before tool | 40 | 2 | Not applicable |
| 5 | RAG pipeline | 25 | 30 | 18 |
| 6 | Streaming chain | 8 | 12 | 6 |
| 7 | Auto-traced call | 40+ | 3 (with LangSmith) | 3 (with LangSmith) |
""")
    st.caption("Line counts are approximate — the point is relative complexity, not exact counts.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Same Task Live (Raw SDK)
# ──────────────────────────────────────────────────────────────────────────────
with tab_task:
    st.markdown(
        "**Same task — Summarise + Translate — run live via Raw SDK.**  "
        "The LangGraph and LCEL versions produce identical output; "
        "their code is shown in the Core Code Pattern expander above."
    )

    passage = st.text_area(
        "Passage to summarise:",
        value=(
            "Agentic AI systems combine large language models with memory, tools, and control flow "
            "to create systems that can plan, act, and adapt over multiple steps. Unlike single-turn "
            "chatbots, agents maintain context, call external APIs, and decide dynamically what to "
            "do next based on what they observe. This makes them powerful for complex tasks like "
            "research, coding assistance, and workflow automation — but also harder to debug and "
            "more expensive to run than simple pipelines."
        ),
        height=130,
        key="task_passage",
    )

    target_lang = st.selectbox(
        "Translate summary to:",
        ["French", "Spanish", "German", "Japanese", "Arabic", "Hindi"],
        key="task_lang",
    )

    if st.button("Run — Summarise then Translate", key="task_btn", type="primary"):
        sys1 = "You are a precise technical writer. Return only the requested format, no preamble."
        usr1 = f"Summarise the following passage in exactly 3 bullet points:\n\n{passage}"
        try:
            with st.spinner("Step 1 — Summarising..."):
                r1 = _client().models.generate_content(
                    model=MODEL,
                    contents=usr1,
                    config={"system_instruction": sys1},
                )
                summary = r1.text

            sys2 = f"You are a professional translator. Translate text to {target_lang} accurately. Return only the translation."
            usr2 = f"Translate to {target_lang}:\n\n{summary}"
            with st.spinner(f"Step 2 — Translating to {target_lang}..."):
                r2 = _client().models.generate_content(
                    model=MODEL,
                    contents=usr2,
                    config={"system_instruction": sys2},
                )
                translation = r2.text

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Step 1 — Summary (English)**")
                st.info(summary)
            with col_b:
                st.markdown(f"**Step 2 — Translation ({target_lang})**")
                st.success(translation)

            st.caption(
                "A LangGraph StateGraph and an LCEL chain would produce this identical output. "
                "The difference is only in how the plumbing is expressed — not what the LLM does."
            )

            with st.expander("🔬 Execution Trace — 2 raw SDK calls"):
                t1, t2, t3 = st.tabs([
                    "① Call 1 — Summarise",
                    "② Call 2 — Translate",
                    "③ Framework Equivalent Code",
                ])
                with t1:
                    st.markdown("**System prompt:**"); st.code(sys1, language="text")
                    st.markdown("**User message:**"); st.code(usr1, language="text")
                    st.markdown("**Raw response:**"); st.code(summary, language="text")
                with t2:
                    st.markdown("**System prompt:**"); st.code(sys2, language="text")
                    st.markdown("**User message:**"); st.code(usr2, language="text")
                    st.markdown("**Raw response:**"); st.code(translation, language="text")
                with t3:
                    st.markdown("**LangGraph equivalent (pseudocode):**")
                    st.code("""\
class State(TypedDict):
    passage: str; summary: str; translation: str

def summarise_node(s): return {"summary": llm.invoke(summarise_prompt.format(**s)).content}
def translate_node(s): return {"translation": llm.invoke(translate_prompt.format(**s)).content}

graph = StateGraph(State)
graph.add_node("summarise", summarise_node)
graph.add_node("translate", translate_node)
graph.set_entry_point("summarise")
graph.add_edge("summarise", "translate")
graph.add_edge("translate", END)
chain = graph.compile()
result = chain.invoke({"passage": passage})
# Gain: streaming, typed state, HITL-ready, persistence.
# Cost: ~25 lines vs 6.""", language="python")

                    st.markdown("**LCEL equivalent (pseudocode):**")
                    st.code(f"""\
summarise_chain = (
    ChatPromptTemplate.from_template("Summarise in 3 bullets:\\n{{passage}}")
    | llm | StrOutputParser()
)
translate_chain = (
    ChatPromptTemplate.from_template("Translate to {target_lang}:\\n{{summary}}")
    | llm | StrOutputParser()
)
full_chain = summarise_chain | (lambda s: {{"summary": s}}) | translate_chain
result = full_chain.invoke({{"passage": passage}})
# Gain: .stream() built-in, .batch() for bulk runs.
# Cost: LangChain dependency, model wrapper, harder to unit test.""", language="python")

        except Exception as e:
            st.error(f"Error: {e}")

# ── What's next ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
### What's next

You have now completed the entire Frameworks Layer (Phase 10):

| Phase | Module | Status |
|---|---|---|
| 10a | LangGraph Workflows | Complete |
| 10b | LangGraph Agents | Complete |
| 10c | LangSmith | Complete |
| 10d | LangChain LCEL | Complete |
| 10f | Framework Compare | Complete |

**Phase 11 — Managed Platforms** gives a cursory overview of cloud-hosted agent services:
Vertex AI Agent Engine · Azure AI Agent Service · AWS Bedrock Agents · OpenAI Assistants API.
These abstract even the framework layer — you trade control for operational simplicity.
""")
