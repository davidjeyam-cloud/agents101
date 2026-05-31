"""
Phase 10c — LangSmith
Bridges Phase 7 (Observability, Cost & Latency, Error Analysis) to LangSmith auto-tracing.
Phase 4d Eval Framework → LangSmith datasets + evaluator runs.
"""
import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10c — LangSmith",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.diagrams import diagram_langsmith
from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🔬 10c — LangSmith")
st.caption(
    "Phase 7's manual TraceCollector replaced by 3 environment variables. "
    "Every LangGraph/LangChain call auto-traces — prompts, tokens, latency, cost, tool calls."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(diagram_langsmith(),
         caption="Phase 7 manual TraceCollector vs LangSmith auto-tracing",
         use_column_width=True)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 7 — Observability &amp; Phase 4d — Eval Framework)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 7 you wired a <code>TraceCollector</code> around every LLM call — manually recording
    timestamps, token counts, latency, and estimated cost into a spans dictionary.
    LangSmith is that same flight recorder, but it is built into the aircraft.
    You set three environment variables and it records everything automatically — every prompt,
    every response, every tool call, every token, every cost — without touching your agent code.<br><br>
    The evaluation loop you built manually in Phase 4d (golden test set → run agent → judge each
    answer → aggregate pass rate) is exactly what LangSmith's <code>evaluate()</code> does,
    with version comparison and a dashboard on top.
    Phase 7 taught you <em>why</em> this matters.  LangSmith gives you the production tool.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What LangSmith is — and what it replaces from Phase 7"):
    st.markdown("""
**LangSmith is observability infrastructure for LangChain and LangGraph.**
It captures everything your Phase 7 `TraceCollector` captured — automatically.

| Phase 7 Manual | LangSmith Equivalent |
|---|---|
| `TraceCollector.start_span(name)` | Auto-traced — no code needed |
| `span["latency_ms"] = elapsed` | Shown in trace dashboard automatically |
| `span["input_tokens"] = count_tokens(prompt)` | Token counts captured per call |
| `span["estimated_cost"] = tokens * rate` | Cost calculated and aggregated |
| Phase 7c Error Analysis: compare broken vs fixed | Side-by-side trace diff in UI |
| Phase 4d Eval Framework: manual golden dataset + judge | LangSmith datasets + evaluator runs |

**Setup is 3 environment variables — no code changes:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-langsmith-key>
LANGCHAIN_PROJECT=agents101
```

Once set, **every LangChain/LangGraph call is automatically traced** — including all
the agents from Phase 10b. No decorator, no wrapper, no TraceCollector subclass.

**LangSmith also covers Phase 4d Eval Framework:**
- Create a dataset of (input, expected output) pairs — your golden test set
- Run your agent over the dataset
- LLM-as-Judge (Phase 4c) scores each run automatically
- Compare runs across versions (regression testing)
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — LangSmith tracing + evaluation"):
    st.code('''
import os
# Step 1: set env vars (or add to .env)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]    = "ls-..."
os.environ["LANGCHAIN_PROJECT"]    = "agents101"

# Step 2: run any LangChain/LangGraph code — it auto-traces
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm    = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
prompt = ChatPromptTemplate.from_messages([("user", "{question}")])
chain  = prompt | llm

result = chain.invoke({"question": "What is agentic AI?"})
# -> trace appears at smith.langchain.com/projects/agents101

# ── Evaluation (Phase 4d replacement) ────────────────────────────────────────
from langsmith import Client
from langsmith.evaluation import evaluate

client = Client()

# Create a golden dataset
dataset = client.create_dataset("agentic-ai-evals")
client.create_examples(
    inputs=[{"question": "What is RAG?"}, {"question": "What is ReAct?"}],
    outputs=[{"answer": "Retrieve-Augment-Generate"}, {"answer": "Reason and Act"}],
    dataset_id=dataset.id,
)

# Define evaluator (LLM-as-Judge from Phase 4c)
def correctness_evaluator(run, example):
    score = judge_llm(run.outputs["output"], example.outputs["answer"])
    return {"key": "correctness", "score": score}

# Run evaluation
results = evaluate(
    lambda inputs: {"output": chain.invoke(inputs)},
    data=dataset.name,
    evaluators=[correctness_evaluator],
)
''', language="python")
    st.markdown("""
**What Phase 7 gave you:** understanding of WHY observability matters — what latency,
tokens, and cost tracking enables. **What LangSmith gives you:** the production tooling
that captures all of it automatically. You understand the dashboard because you built it by hand.

**Phase 4d connection:** `evaluate()` is your manual evaluation loop (test set + judge score +
aggregate metrics) automated and stored with version comparison.
""")

st.markdown("---")

# ── Interactive demo ──────────────────────────────────────────────────────────
st.markdown("### Interactive Demo")

tab_compare, tab_setup, tab_eval = st.tabs([
    "Phase 7 vs LangSmith",
    "Setup & Configuration",
    "Evaluation Framework",
])

# ── TAB: Compare ─────────────────────────────────────────────────────────────
with tab_compare:
    st.markdown("**Side-by-side: what Phase 7 captured manually vs what LangSmith auto-captures**")

    col1, col2 = st.columns(2)
    query = st.text_input("Test query:", value="What is the difference between ReAct and Planning agents?",
                          key="ls_query")

    with col1:
        st.markdown("#### Phase 7 — Manual TraceCollector")
        if st.button("Run with manual trace", key="run_manual_trace"):
            import time
            client = _client()
            start = time.time()
            with st.spinner("Running with manual trace..."):
                resp = client.models.generate_content(model=MODEL, contents=query)
            elapsed = round((time.time() - start) * 1000)

            # Simulate Phase 7 manual span
            span = {
                "call":         "generate_content",
                "latency_ms":   elapsed,
                "input_chars":  len(query),
                "output_chars": len(resp.text),
                "model":        MODEL,
            }
            st.success(resp.text[:400] + "...")
            st.markdown("**Manual span captured:**")
            st.json(span)
            st.caption("You wrote TraceCollector to capture this — ~60 lines in Phase 7")

    with col2:
        st.markdown("#### LangSmith — Auto-captured")
        langsmith_key = os.getenv("LANGCHAIN_API_KEY", "")
        if langsmith_key:
            if st.button("Run with LangSmith tracing", key="run_ls_trace"):
                try:
                    os.environ["LANGCHAIN_TRACING_V2"] = "true"
                    os.environ["LANGCHAIN_PROJECT"] = "agents101-demo"
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        google_api_key=os.getenv("GEMINI_API_KEY"),
                    )
                    import time
                    start = time.time()
                    with st.spinner("Running with LangSmith auto-trace..."):
                        result = llm.invoke(query)
                    elapsed = round((time.time() - start) * 1000)
                    st.success(result.content[:400] + "...")
                    st.info(
                        f"Trace auto-captured in ~{elapsed}ms. "
                        f"View at: https://smith.langchain.com/projects/agents101-demo"
                    )
                    st.caption(
                        "LangSmith captured: full prompt, response, latency, token count, "
                        "cost — automatically. 0 extra lines of code."
                    )
                except Exception as e:
                    st.error(f"LangSmith error: {e}")
        else:
            st.info(
                "Add `LANGCHAIN_API_KEY=ls-...` to your `.env` to enable live LangSmith tracing. "
                "Get a free key at smith.langchain.com"
            )
            st.markdown("**What LangSmith auto-captures (without any code changes):**")
            st.json({
                "run_id":       "uuid-auto-generated",
                "name":         "ChatGoogleGenerativeAI",
                "inputs":       {"messages": [{"role": "user", "content": query[:80] + "..."}]},
                "outputs":      {"generations": [{"text": "(response text)"}]},
                "latency_ms":   "(measured automatically)",
                "prompt_tokens":  "(counted by LangSmith)",
                "completion_tokens": "(counted by LangSmith)",
                "total_cost_usd":  "(calculated from model pricing)",
                "tags":         ["agents101-demo"],
            })

    with st.expander("🔍 What just happened — Translation"):
        st.markdown("""
| Phase 7 Manual | LangSmith Auto |
|---|---|
| `span = {}; start = time.time()` | Not needed |
| `span["latency_ms"] = elapsed * 1000` | Auto-measured |
| `span["input_tokens"] = count_tokens(prompt)` | Auto-counted |
| `span["output_tokens"] = count_tokens(response)` | Auto-counted |
| `span["cost"] = tokens * COST_PER_TOKEN` | Auto-calculated from model |
| `collector.spans.append(span)` | Auto-stored in LangSmith project |
| Custom dashboard in Streamlit | smith.langchain.com dashboard |
""")

# ── TAB: Setup ────────────────────────────────────────────────────────────────
with tab_setup:
    st.markdown("**How to enable LangSmith in 60 seconds**")

    st.markdown("**Step 1 — Get a free API key:**")
    st.code("# Go to: https://smith.langchain.com → Sign up → Settings → API Keys", language="text")

    st.markdown("**Step 2 — Add to your `.env`:**")
    st.code("""LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-your-key-here
LANGCHAIN_PROJECT=agents101""", language="bash")

    st.markdown("**Step 3 — Run any existing LangChain/LangGraph code — no changes needed.**")

    st.markdown("**What gets traced automatically:**")
    st.markdown("""
- Every `ChatGoogleGenerativeAI.invoke()` call
- Every `chain.invoke()` and `chain.stream()`
- Every LangGraph node execution (per-node timing)
- Every tool call within an agent
- Token counts and cost per call
- Full input/output at every step
""")

    st.markdown("**For local-only tracing (no cloud, no API key):**")
    st.code('os.environ["LANGCHAIN_TRACING_V2"] = "local"', language="python")

    st.markdown("**Viewing traces:**")
    st.code("""
# In Python — get run URLs programmatically:
from langsmith import Client
client = Client()
runs = list(client.list_runs(project_name="agents101", limit=5))
for r in runs:
    print(r.name, r.total_tokens, r.total_cost, r.url)
""", language="python")

# ── TAB: Evaluation ───────────────────────────────────────────────────────────
with tab_eval:
    st.markdown("**Phase 4d Eval Framework → LangSmith `evaluate()`**")

    st.markdown("""
| Phase 4d Manual | LangSmith Equivalent |
|---|---|
| `test_cases = [{"q": ..., "expected": ...}]` | `client.create_dataset("name")` |
| Loop: `for case in test_cases: answer = agent(case["q"])` | `evaluate(agent_fn, data=dataset_name)` |
| `score = judge_llm(answer, expected)` | `evaluators=[correctness_fn]` |
| Manual aggregate: `pass_rate = sum(scores)/len(scores)` | Auto-aggregated in LangSmith UI |
| CSV export / manual comparison | Version comparison across experiment runs |
""")

    st.code('''
from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator

client = Client()

# Create your golden dataset (equivalent to Phase 4d test set)
dataset = client.create_dataset(
    "agents101-patterns-eval",
    description="Tests for agentic AI pattern understanding"
)
client.create_examples(
    inputs=[
        {"question": "When should you use ReAct over Prompt Chaining?"},
        {"question": "What is the key risk of Reflection with the same model?"},
    ],
    outputs=[
        {"answer": "When the number of steps is unknown and live data is needed"},
        {"answer": "The LLM may hallucinate critiques or miss real flaws"},
    ],
    dataset_id=dataset.id,
)

# Run evaluation — LangSmith calls your agent on each example
results = evaluate(
    lambda inputs: chain.invoke(inputs),   # your agent/chain
    data="agents101-patterns-eval",
    evaluators=[
        LangChainStringEvaluator("correctness"),   # built-in LLM-as-Judge
    ],
    experiment_prefix="v1-baseline",
)
# -> Results visible at smith.langchain.com with per-example scores
''', language="python")

    st.info(
        "**Phase 4d insight:** You built the eval loop manually to understand WHY systematic "
        "evaluation matters. LangSmith automates the loop and adds version tracking — "
        "you can compare 'v1-baseline' vs 'v2-improved' to measure progress."
    )

    with st.expander("🔬 Execution Trace"):
        st.markdown("**What LangSmith captures per evaluation run:**")
        st.json({
            "experiment": "v1-baseline",
            "dataset": "agents101-patterns-eval",
            "examples_run": 2,
            "pass_rate": "1/2 = 50%",
            "evaluator": "correctness (LLM-as-Judge)",
            "trace_url": "https://smith.langchain.com/...",
            "per_example": [
                {"input": "When should you use ReAct...", "score": 0.9, "verdict": "PASS"},
                {"input": "What is the key risk...", "score": 0.6, "verdict": "REVIEW"},
            ]
        })

st.markdown("---")
st.markdown("### What's next → Phase 10d — LangChain")
st.markdown(
    "Phase 1 memory management and Phase 5 RAG pipeline as LangChain LCEL. "
    "The pipe operator `prompt | llm | parser` is Prompt Chaining as syntax sugar."
)
