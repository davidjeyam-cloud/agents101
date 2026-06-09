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

from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🔬 10c — LangSmith")
st.caption(
    "Phase 7's manual TraceCollector replaced by 3 environment variables. "
    "Every LangGraph/LangChain call auto-traces — prompts, tokens, latency, cost, tool calls."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image("docs/images/arch_langsmith.jpg",
         caption="Manual TraceCollector (Phase 7) vs LangSmith auto-tracing — prompts, latency, cost, datasets, alerts, governance",
         use_container_width=True)

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

tab_compare, tab_setup, tab_eval, tab_hub, tab_alerts, tab_gov, tab_langfuse = st.tabs([
    "Phase 7 vs LangSmith",
    "Setup & Configuration",
    "Evaluation Framework",
    "Prompt Hub",
    "Alerts & Feedback",
    "Governance & Audit",
    "Langfuse",
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

# ── TAB: Prompt Hub ──────────────────────────────────────────────────────────
with tab_hub:
    st.markdown("**Prompt Hub — version-controlled, shareable prompts**")
    st.markdown("""
The Prompt Hub solves prompt drift: your agent's system prompt changes, but you don't know
when it changed or what the previous version was. Prompt Hub applies Git-style versioning to prompts.

| Without Prompt Hub | With Prompt Hub |
|---|---|
| Prompt in code as a string | Prompt stored in LangSmith UI |
| No history of changes | Full version history, diff between versions |
| Different prompt per environment | Pin a specific commit hash per env |
| Hard to A/B test prompts | Run evaluation on v1 vs v2 prompt |
| Shared via Slack or copy-paste | Shared via `hub.pull("owner/prompt-name")` |
""")
    st.code('''
# ── Push a prompt to Prompt Hub ───────────────────────────────────────────────
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

# Define your prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful agentic AI assistant. Be concise and precise."),
    ("user",   "{question}"),
])

# Push to Prompt Hub (creates a versioned entry at smith.langchain.com)
client.push_prompt("agents101/qa-assistant", object=prompt)
# → available at: https://smith.langchain.com/hub/your-name/agents101-qa-assistant

# ── Pull in any codebase — no local prompt strings ───────────────────────────
from langchain import hub

# Pull latest version
prompt = hub.pull("agents101/qa-assistant")

# Pin a specific commit (for production — never change unexpectedly)
prompt = hub.pull("agents101/qa-assistant:abc123def")

# Use exactly like any ChatPromptTemplate
chain = prompt | llm
result = chain.invoke({"question": "What is LangGraph?"})

# ── A/B test two prompt versions ─────────────────────────────────────────────
prompt_v1 = hub.pull("agents101/qa-assistant:v1")
prompt_v2 = hub.pull("agents101/qa-assistant:v2")

chain_v1 = prompt_v1 | llm
chain_v2 = prompt_v2 | llm

# Then run LangSmith evaluate() on both — compare scores side-by-side
''', language="python")

    if st.button("Show prompt versioning simulation", key="show_hub"):
        client = _client()
        import time
        versions = [
            {"version": "v1 (initial)", "prompt": "You are a helpful assistant.", "score": 0.71},
            {"version": "v2 (added concise)", "prompt": "You are a helpful assistant. Be concise.", "score": 0.78},
            {"version": "v3 (current)", "prompt": "You are a helpful agentic AI assistant. Be concise and precise.", "score": 0.89},
        ]
        for v in versions:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.code(f"[{v['version']}]\n{v['prompt']}", language="text")
            with col2:
                st.metric("Eval score", v['score'], delta=None)
        st.caption("Prompt Hub stores each change — you can roll back to v1 with hub.pull('name:v1')")

# ── TAB: Alerts & Feedback ────────────────────────────────────────────────────
with tab_alerts:
    st.markdown("**Alerts & Feedback API — production monitoring**")
    st.markdown("""
| Monitoring type | What it does | Trigger |
|---|---|---|
| **Latency alert** | Notify when p95 latency > threshold | `latency_ms > 5000` |
| **Error rate alert** | Notify when error % spikes | `error_rate > 5%` |
| **Cost alert** | Notify when daily spend exceeds budget | `daily_cost_usd > 10` |
| **Feedback API** | Collect thumbs-up/down from users | `client.create_feedback(run_id, ...)` |
| **Online eval** | Auto-score every production run | `evaluator runs continuously` |
""")
    st.code('''
# ── Feedback API — capture user ratings on production runs ────────────────────
from langsmith import Client
client = Client()

# After showing a response to the user:
def record_user_feedback(run_id: str, helpful: bool, comment: str = ""):
    client.create_feedback(
        run_id=run_id,
        key="user-helpful",
        score=1.0 if helpful else 0.0,
        comment=comment,
    )
    # → Appears in LangSmith UI as a feedback annotation on the run

# ── Get the run_id from a LangChain call ──────────────────────────────────────
from langchain_core.tracers.context import collect_runs

with collect_runs() as cb:
    result = chain.invoke({"question": "What is ReAct?"})
    run_id = cb.traced_runs[0].id

# After user clicks 👍 or 👎:
record_user_feedback(run_id, helpful=True, comment="Clear explanation")

# ── Online evaluator — score every production run automatically ───────────────
# Configured in LangSmith UI: Monitoring > Online Evaluations
# Fires your evaluator function on each new run as it arrives
# No batch job needed — continuous sampling

# ── Alert rules (set in LangSmith UI, not code) ───────────────────────────────
# Monitoring > Alerts > New Alert
# - Metric: p95_latency | Threshold: > 3000ms | Channel: Slack / Email
# - Metric: error_rate   | Threshold: > 5%    | Channel: PagerDuty
# - Metric: total_cost   | Threshold: > $5/hr | Channel: Email
''', language="python")

    if st.button("Simulate feedback capture", key="run_feedback"):
        import uuid
        fake_run_id = str(uuid.uuid4())
        st.json({
            "run_id": fake_run_id,
            "feedback_key": "user-helpful",
            "score": 1.0,
            "comment": "Clear and accurate explanation",
            "created_at": "2026-06-07T09:00:00Z",
            "project": "agents101",
        })
        st.caption(f"Feedback for run {fake_run_id[:8]}... recorded in LangSmith — "
                   "visible in run detail view alongside the trace")
        with st.expander("🔬 Execution Trace — feedback loop"):
            st.code(
                "User sees response → clicks 👍\n"
                "Frontend calls record_user_feedback(run_id, helpful=True)\n"
                "LangSmith annotates run with score=1.0\n"
                "LangSmith dashboard: avg feedback score = 0.84 over last 100 runs\n"
                "Alert: if avg drops below 0.6 → Slack notification fires", language="text"
            )

# ── TAB: Governance ────────────────────────────────────────────────────────────
with tab_gov:
    st.markdown("**Governance & Audit Trails — compliance and accountability**")
    st.markdown("""
Governance answers the question: *"What did the agent do, and why, and who authorised it?"*

| Governance need | LangSmith capability |
|---|---|
| Immutable audit log | Every run stored with inputs/outputs, timestamp, user |
| Who ran what | `run.metadata["user_id"]` tag on every trace |
| Prompt accountability | Prompt Hub + version pinning = "agent used prompt v3 at 14:32" |
| Cost accountability | Per-user, per-project cost breakdown |
| Compliance export | `client.list_runs()` → export as JSON/CSV |
| Data residency | LangSmith EU endpoint or self-hosted option |
""")
    st.code('''
# ── Tag runs with user/session metadata ───────────────────────────────────────
from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    metadata={
        "user_id":     "alice@company.com",
        "session_id":  "sess-abc123",
        "feature":     "fraud-detection-agent",
        "version":     "v2.1.0",
    },
    tags=["production", "fraud-detection"],
)
result = graph.invoke({"messages": [("user", query)]}, config)
# → All metadata attached to the LangSmith run — searchable, filterable

# ── Audit export — pull all runs for a user ───────────────────────────────────
from langsmith import Client
client = Client()

runs = client.list_runs(
    project_name="agents101-prod",
    filter=\'and(eq(metadata_key, "user_id"), eq(metadata_value, "alice@company.com"))\',
    start_time=datetime(2026, 6, 1),
)
for run in runs:
    print(run.id, run.inputs, run.outputs, run.total_tokens, run.total_cost)

# ── Data redaction — never log PII ────────────────────────────────────────────
# In .env: LANGCHAIN_HIDE_INPUTS=true  (hides prompt content from LangSmith)
# Use for regulated industries (healthcare, finance) where prompts contain PII
# Traces still show timing + tokens, but not message content

# ── Self-hosted LangSmith (enterprise) ───────────────────────────────────────
# docker run langchain/langsmith-backend + langchain/langsmith-frontend
# Point LANGCHAIN_ENDPOINT to your own server
# Full data residency — nothing leaves your network
os.environ["LANGCHAIN_ENDPOINT"] = "https://langsmith.your-company.com"
''', language="python")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Regulatory use cases:**")
        st.markdown("""
- **Financial services**: audit trail of every automated decision + human approval
- **Healthcare**: HIPAA — `LANGCHAIN_HIDE_INPUTS=true` to avoid PHI in logs
- **Legal**: immutable record of what the AI said, when, under which prompt version
- **Enterprise**: per-team cost allocation, quota management
""")
    with col2:
        st.markdown("**Governance checklist:**")
        items = [
            "Metadata tagging: user_id + session_id on every run",
            "Prompt Hub: all prompts versioned, no free-form strings in prod",
            "HITL audit: every interrupt + resume logged (10b3)",
            "LANGCHAIN_HIDE_INPUTS for sensitive data",
            "Alert on error rate > 5% and cost > budget",
            "Monthly audit export reviewed by compliance team",
        ]
        for item in items:
            st.checkbox(item, key=f"gov_{item[:15]}")

# ── TAB: Langfuse ─────────────────────────────────────────────────────────────
with tab_langfuse:
    st.markdown("**Langfuse — open-source, self-hostable LLM observability**")
    st.markdown(
        "Langfuse does for any LLM stack what LangSmith does for LangChain. "
        "It is fully open-source (MIT), self-hostable, and provider-agnostic — "
        "it works with raw Gemini SDK, OpenAI, Anthropic, or any LangChain/LangGraph chain."
    )

    st.markdown("""
| Feature | LangSmith | Langfuse |
|---|---|---|
| **Auto-tracing** | LangChain/LangGraph only (3 env vars) | Any LLM via `@observe` decorator or manual SDK |
| **Hosting** | SaaS (smith.langchain.com) or self-hosted enterprise | Cloud (cloud.langfuse.com) or self-host free (Docker) |
| **Open source** | No | Yes — MIT licence |
| **Prompt Hub** | Yes — versioned prompts | Yes — Langfuse Prompt Management |
| **Evals / scoring** | `evaluate()` + LLM-as-Judge | `langfuse.score()` + Datasets API |
| **LangGraph integration** | Native (auto-traced) | Via `CallbackHandler` or `@observe` |
| **Best for** | Teams already on LangChain/LangGraph | Any stack; open-source requirement; self-hosting |
""")

    st.markdown("#### Setup")
    st.code('''
pip install langfuse

# In .env:
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_SECRET_KEY=sk-lf-...
# LANGFUSE_HOST=https://cloud.langfuse.com   # or your self-hosted URL
''', language="bash")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Option 1 — `@observe` decorator (recommended)")
        st.code('''
from langfuse.decorators import observe, langfuse_context
from utils.llm import _client, MODEL

@observe()                           # wraps the function as a Langfuse trace
def run_agent(question: str) -> str:
    client = _client()
    resp = client.models.generate_content(
        model=MODEL, contents=question
    )
    answer = resp.text

    # Score the trace from inside the function
    langfuse_context.score_current_observation(
        name="relevance",
        value=0.9,
        comment="response is on-topic"
    )
    return answer

result = run_agent("What is ReAct?")
# -> trace appears at cloud.langfuse.com automatically
''', language="python")

    with col2:
        st.markdown("#### Option 2 — manual SDK tracing")
        st.code('''
from langfuse import Langfuse
from utils.llm import _client, MODEL

langfuse = Langfuse()   # reads env vars automatically

# Create a trace
trace = langfuse.trace(
    name="react-agent-run",
    user_id="user-123",
    metadata={"phase": "4e-evalops"},
)

# Add a span for the LLM call
span = trace.span(
    name="llm-call",
    input={"question": question},
)
client = _client()
resp = client.models.generate_content(model=MODEL, contents=question)
span.end(output={"answer": resp.text})

# Send an eval score back to the trace
langfuse.score(
    trace_id=trace.id,
    name="correctness",
    value=0.85,          # 0.0 – 1.0
    comment="Contains required facts"
)

langfuse.flush()         # ensure all events are sent before exit
''', language="python")

    st.markdown("#### LangGraph integration via CallbackHandler")
    st.code('''
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler()   # reads LANGFUSE_* env vars

# Pass as callback to any LangGraph invoke / stream call
result = graph.invoke(
    {"messages": [("user", query)]},
    config={"callbacks": [langfuse_handler]},
)
# -> every node, LLM call, and tool call is traced automatically
''', language="python")

    st.markdown("#### Langfuse Datasets — eval loop (equivalent to LangSmith evaluate())")
    st.code('''
from langfuse import Langfuse

langfuse = Langfuse()

# Create or get a dataset
dataset = langfuse.create_dataset(name="agents101-evals")

# Upload golden examples
langfuse.create_dataset_item(
    dataset_name="agents101-evals",
    input={"question": "What is RAG?"},
    expected_output={"answer": "Retrieve-Augment-Generate"},
)

# Run agent over the dataset
for item in langfuse.get_dataset("agents101-evals").items:
    with item.observe(run_name="gemini-2.5-flash-run-1") as trace_id:
        answer = run_agent(item.input["question"])   # your @observe-wrapped fn
        langfuse.score(
            trace_id=trace_id,
            name="correctness",
            value=1.0 if "Retrieve" in answer else 0.0,
        )
''', language="python")

    st.markdown("#### Self-hosting Langfuse (free, Docker)")
    st.code('''
# docker-compose.yml (minimal)
# services:
#   langfuse-server:
#     image: langfuse/langfuse:latest
#     ports: ["3000:3000"]
#     environment:
#       - DATABASE_URL=postgresql://...
#       - NEXTAUTH_SECRET=<random>
#       - SALT=<random>
#
# Then in .env:
# LANGFUSE_HOST=http://localhost:3000
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_SECRET_KEY=sk-lf-...
''', language="yaml")

    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        query_lf = st.text_input("Test query:", value="Explain LLM-as-Judge in one sentence",
                                 key="lf_query")
        if st.button("Run & trace with Langfuse", key="run_langfuse"):
            try:
                from langfuse.decorators import observe, langfuse_context
                @observe()
                def _lf_demo(q):
                    client = _client()
                    r = client.models.generate_content(model=MODEL, contents=q)
                    langfuse_context.score_current_observation(name="auto_score", value=0.9)
                    return r.text
                result_lf = _lf_demo(query_lf)
                st.success(result_lf)
                st.info("Trace sent to Langfuse — check your dashboard.")
            except Exception as e:
                st.error(f"Langfuse error: {e}")
    else:
        st.info(
            "Add `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` "
            "to your `.env` to enable live Langfuse tracing. "
            "Sign up free at https://cloud.langfuse.com or self-host with Docker."
        )

    with st.expander("🔬 Execution Trace — Langfuse concept summary"):
        st.code(
            "Langfuse vs LangSmith:\n"
            "  LangSmith  = native LangChain/LangGraph auto-tracing (3 env vars, zero code)\n"
            "  Langfuse   = any LLM stack, @observe decorator, self-hostable (MIT)\n\n"
            "Integration points:\n"
            "  @observe()              — trace any Python function automatically\n"
            "  CallbackHandler         — LangGraph node-level tracing via callbacks\n"
            "  langfuse.score()        — push eval scores back to any trace\n"
            "  Datasets API            — golden dataset + batch eval loop\n"
            "  Self-host               — full data residency, no SaaS dependency",
            language="text"
        )

st.markdown("---")
st.markdown("### What's next → Phase 10d — LangChain")
st.markdown(
    "Phase 1 memory management and Phase 5 RAG pipeline as LangChain LCEL. "
    "The pipe operator `prompt | llm | parser` is Prompt Chaining as syntax sugar. "
    "Now also includes Structured Output (`.with_structured_output()`) and the @tool ecosystem."
)
