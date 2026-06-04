"""Phase 7a -- Observability & Tracing"""
import streamlit as st, os, time, json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL
from utils.tools import get_country_info, get_weather

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
st.set_page_config(page_title="Phase 7a -- Observability", page_icon="🔭", layout="wide")
st.title("🔭 Phase 7a -- Observability & Tracing")
st.caption("Wrap every LLM call with a tracer -- capture latency, tokens, cost, tool calls, decisions")
if not api_key: st.error("GEMINI_API_KEY not found."); st.stop()
client = genai.Client(api_key=api_key)
from utils.diagrams import diagram_observability
st.image(diagram_observability(), use_container_width=True)

with st.expander("📖 What is Observability and why does every production agent need it?"):
    st.markdown("""
    > *"You can't improve what you can't measure."* -- Peter Drucker

    **The problem without observability:**
    An agent answers a question. Was it fast? Was it cheap? Did it use the right tool?
    Did it hallucinate? Without tracing, you have no idea.

    **What observability gives you:**

    | Signal | What you measure | Why it matters |
    |---|---|---|
    | **Latency** | Time per LLM call, per tool, total | SLA compliance, user experience |
    | **Token count** | Input + output tokens per call | Cost calculation, context window usage |
    | **Cost** | Estimated GBP cost per query | Budget tracking, ROI per interaction |
    | **Tool calls** | Which tools, how many times, success rate | Agent quality, tool reliability |
    | **Decisions** | What routing choices were made | Audit trail, debugging |
    | **Errors** | What failed and when | Reliability, SLA breaches |

    **The TraceCollector pattern:**
    A thin wrapper around every `_call()` that records timing and metadata.
    The agent code doesn't change -- tracing is added at the infrastructure level.

    **Connecting to other phases:**
    - Phase 3b Execution Trace: same concept, shown per-run for learning
    - Phase 4d Evals: traces become training data for the golden dataset
    - Phase 7b Cost: traces provide the token counts needed for cost calculation
    - Phase 7c Errors: traces are the evidence for failure diagnosis
    """)

with st.expander("📐 Core Code Pattern -- TraceCollector"):
    st.code('''
import time

class TraceCollector:
    """Wraps LLM calls and captures timing, tokens, cost, tool calls."""

    PRICE_INPUT_PER_1M  = 0.075   # USD per 1M input tokens (Gemini 2.5 Flash)
    PRICE_OUTPUT_PER_1M = 0.30    # USD per 1M output tokens

    def __init__(self):
        self.spans = []   # one span per LLM call

    def traced_call(self, fn, *args, **kwargs) -> any:
        """Wrap a single LLM call with tracing."""
        span = {
            "start":    time.time(),
            "fn":       fn.__name__,
            "tokens_in":  0,
            "tokens_out": 0,
            "cost_usd":   0.0,
            "error":    None,
        }
        try:
            result = fn(*args, **kwargs)
            span["latency_ms"] = int((time.time() - span["start"]) * 1000)
            # Estimate tokens from text length (chars / 4 ~ tokens)
            if hasattr(result, "text"):
                span["tokens_out"] = len(result.text) // 4
            span["cost_usd"] = (
                span["tokens_in"]  / 1_000_000 * self.PRICE_INPUT_PER_1M +
                span["tokens_out"] / 1_000_000 * self.PRICE_OUTPUT_PER_1M
            )
            return result
        except Exception as e:
            span["error"] = str(e)
            raise
        finally:
            self.spans.append(span)

    @property
    def total_latency_ms(self):
        return sum(s.get("latency_ms", 0) for s in self.spans)

    @property
    def total_cost_usd(self):
        return sum(s.get("cost_usd", 0) for s in self.spans)

# ── Usage ─────────────────────────────────────────────────────────────────────
tracer = TraceCollector()

# Replace every _call() with tracer.traced_call()
response = tracer.traced_call(convo.send_message, user_query)

# After run: inspect spans
for span in tracer.spans:
    print(f"{span['fn']}: {span['latency_ms']}ms | ${span['cost_usd']:.6f}")
''', language="python")
    st.markdown("""
**The key principle:** Tracing is non-invasive. The agent code stays identical.
You wrap `_call()` once and every call is logged.

**Token estimation:** We use `len(text) // 4` as a rough estimate.
For exact counts, use `client.models.count_tokens(model=MODEL, contents=text).total_tokens`.
The estimate is accurate enough for dashboards; use exact for billing.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TraceCollector implementation
# ══════════════════════════════════════════════════════════════════════════════

PRICE_INPUT_PER_1M  = 0.075   # USD Gemini 2.5 Flash (approximate)
PRICE_OUTPUT_PER_1M = 0.30
USD_TO_GBP = 0.79

class TraceCollector:
    def __init__(self):
        self.spans = []
        self.tool_calls = []

    def traced_call(self, fn, *args, **kwargs):
        span = {"fn": fn.__qualname__, "start": time.time(),
                "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0,
                "latency_ms": 0, "error": None, "tool": None}
        try:
            result = fn(*args, **kwargs)
            span["latency_ms"] = int((time.time() - span["start"]) * 1000)
            if hasattr(result, "text") and result.text:
                span["tokens_out"] = max(1, len(result.text) // 4)
            # Estimate input tokens from args
            for a in args:
                if isinstance(a, str):
                    span["tokens_in"] += max(1, len(a) // 4)
            span["cost_usd"] = (
                span["tokens_in"]  / 1_000_000 * PRICE_INPUT_PER_1M +
                span["tokens_out"] / 1_000_000 * PRICE_OUTPUT_PER_1M
            )
            return result
        except Exception as e:
            span["error"] = str(e)
            span["latency_ms"] = int((time.time() - span["start"]) * 1000)
            raise
        finally:
            self.spans.append(span)

    def record_tool(self, name: str, latency_ms: int, success: bool):
        self.tool_calls.append({"tool": name, "latency_ms": latency_ms, "success": success})

    @property
    def total_latency_ms(self): return sum(s["latency_ms"] for s in self.spans)
    @property
    def total_cost_usd(self): return sum(s["cost_usd"] for s in self.spans)
    @property
    def total_tokens_in(self): return sum(s["tokens_in"] for s in self.spans)
    @property
    def total_tokens_out(self): return sum(s["tokens_out"] for s in self.spans)
    @property
    def error_count(self): return sum(1 for s in self.spans if s["error"])


AGENT_SYSTEM = (
    "You are NexaBank's customer advisor. "
    "Answer questions accurately about NexaBank products and policies. "
    "Be specific -- cite rates, fees and timelines. Keep responses under 100 words."
)

TASKS = {
    "Simple question (low cost)":
        "What is the NexaSaver interest rate?",
    "Multi-tool question (higher cost)":
        "I want to send money to Australia and also understand your savings rates. Can you help with both?",
    "Complex analysis (highest cost)":
        "I earn GBP 50,000, have GBP 15,000 saved, and want to buy a house in 2 years. "
        "What NexaBank savings account should I use and what mortgage might I qualify for?",
    "Fraud + international (2 topics)":
        "My card was used fraudulently in Japan. I need to report the fraud AND understand the fees for my upcoming planned transfer to Japan.",
}

tab_single, tab_compare, tab_dashboard = st.tabs([
    "📋 Tab A -- Single Run Trace",
    "🔧 Tab B -- Compare Queries",
    "📝 Tab C -- Observability Dashboard",
])

with tab_single:
    st.subheader("Tab A -- Run an agent with full tracing")
    st.markdown("See exactly what was measured for every LLM call: timing, tokens, cost.")

    if "sel_obs" not in st.session_state: st.session_state.sel_obs = list(TASKS.keys())[0]
    col1, col2 = st.columns([2,1])
    with col2:
        for label in TASKS:
            if st.button(label, key=f"obs_{label[:15]}"): st.session_state.sel_obs = label; st.rerun()
    with col1:
        query_a = st.text_area("Query:", value=TASKS[st.session_state.sel_obs], height=90)

    if st.button("▶  Run with Tracing", type="primary", key="run_obs"):
        if not query_a.strip():
            st.warning("Please enter a query.")
            st.stop()
        tracer = TraceCollector()
        config = types.GenerateContentConfig(system_instruction=AGENT_SYSTEM)
        convo = client.chats.create(model=MODEL, config=config)

        with st.spinner("Running agent with tracing..."):
            response = tracer.traced_call(convo.send_message, query_a)

        tracer.spans[0]["tokens_in"] += len(AGENT_SYSTEM) // 4  # add system prompt tokens

        # Display trace
        with st.container(border=True):
            st.markdown("### ? Answer")
            st.success(response.text)

        st.markdown("### 📊 Trace Data")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Latency",  f"{tracer.total_latency_ms} ms")
        col2.metric("Input Tokens",   f"~{tracer.total_tokens_in:,}")
        col3.metric("Output Tokens",  f"~{tracer.total_tokens_out:,}")
        col4.metric("Est. Cost (GBP)",f"GBP {tracer.total_cost_usd * USD_TO_GBP:.5f}")

        with st.expander("🔬 Per-span trace (one row per LLM call)"):
            for i, span in enumerate(tracer.spans, 1):
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Span {i}:** `{span['fn']}`")
                    c2.metric("Latency",  f"{span['latency_ms']} ms")
                    c3.metric("Tokens in/out", f"{span['tokens_in']} / {span['tokens_out']}")
                    c4.metric("Cost", f"GBP {span['cost_usd']*USD_TO_GBP:.6f}")
                    if span["error"]: st.error(f"Error: {span['error']}")

        with st.expander("🔍 What this trace would look like in production"):
            trace_json = {
                "trace_id": "tr-nexabank-001",
                "model": MODEL,
                "query": query_a[:80] + "...",
                "spans": [{"fn": s["fn"], "latency_ms": s["latency_ms"],
                            "tokens_in": s["tokens_in"], "tokens_out": s["tokens_out"],
                            "cost_usd": round(s["cost_usd"], 8)} for s in tracer.spans],
                "totals": {
                    "latency_ms": tracer.total_latency_ms,
                    "tokens_in": tracer.total_tokens_in,
                    "tokens_out": tracer.total_tokens_out,
                    "cost_usd": round(tracer.total_cost_usd, 8),
                    "cost_gbp": round(tracer.total_cost_usd * USD_TO_GBP, 8),
                    "error_count": tracer.error_count,
                },
            }
            st.code(json.dumps(trace_json, indent=2), language="json")

with tab_compare:
    st.subheader("Tab B -- Compare traces across different query types")
    st.markdown("See how cost and latency vary with query complexity.")

    if st.button("▶  Run all 4 query types and compare", type="primary", key="run_obs_compare"):
        results = []
        prog = st.progress(0)
        for i, (label, query) in enumerate(TASKS.items()):
            prog.progress((i+1)/len(TASKS), text=f"Running: {label[:40]}...")
            tracer = TraceCollector()
            config = types.GenerateContentConfig(system_instruction=AGENT_SYSTEM)
            convo = client.chats.create(model=MODEL, config=config)
            try:
                resp = tracer.traced_call(convo.send_message, query)
                tracer.spans[0]["tokens_in"] += len(AGENT_SYSTEM) // 4
                results.append({
                    "label": label, "query": query, "answer": resp.text,
                    "latency_ms": tracer.total_latency_ms,
                    "tokens_in": tracer.total_tokens_in,
                    "tokens_out": tracer.total_tokens_out,
                    "cost_gbp": tracer.total_cost_usd * USD_TO_GBP,
                })
            except Exception as e:
                results.append({"label": label, "error": str(e), "latency_ms": 0,
                                 "cost_gbp": 0, "tokens_in": 0, "tokens_out": 0})
        prog.empty()

        st.markdown("### Comparison Table")
        st.markdown("""
| Query Type | Latency | Tokens In | Tokens Out | Cost (GBP) |
|---|---|---|---|---|""")
        for r in results:
            st.markdown(
                f"| {r['label'][:35]} | {r['latency_ms']}ms | ~{r['tokens_in']} | ~{r['tokens_out']} | GBP {r['cost_gbp']:.5f} |"
            )

        st.markdown("---")
        for r in results:
            if "answer" in r:
                with st.expander(f"Answer: {r['label']}"):
                    st.info(r["answer"])

with tab_dashboard:
    st.subheader("Tab C -- What a production observability dashboard looks like")
    st.markdown("""
    In production, every trace is written to a log store (e.g. BigQuery, Elasticsearch, LangSmith).
    A dashboard aggregates across all agent runs to show operational health.
    """)

    st.markdown("### Simulated NexaBank Agent Dashboard (last 100 calls)")
    import random
    random.seed(42)
    sim_latencies   = [random.randint(180, 1200) for _ in range(100)]
    sim_costs       = [random.uniform(0.00001, 0.0008) * USD_TO_GBP for _ in range(100)]
    sim_errors      = [1 if random.random() < 0.04 else 0 for _ in range(100)]
    sim_tool_calls  = [random.randint(0, 3) for _ in range(100)]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Calls",     "100")
    c2.metric("Avg Latency",     f"{int(sum(sim_latencies)/len(sim_latencies))}ms")
    c3.metric("P95 Latency",     f"{sorted(sim_latencies)[94]}ms")
    c4.metric("Error Rate",      f"{sum(sim_errors)}%")
    c5.metric("Avg Cost/Query",  f"GBP {sum(sim_costs)/len(sim_costs):.5f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Latency distribution (ms):**")
        buckets = {"<300ms": 0, "300-600ms": 0, "600ms-1s": 0, ">1s": 0}
        for l in sim_latencies:
            if l < 300: buckets["<300ms"] += 1
            elif l < 600: buckets["300-600ms"] += 1
            elif l < 1000: buckets["600ms-1s"] += 1
            else: buckets[">1s"] += 1
        for bucket, count in buckets.items():
            bar = "█" * (count // 3)
            st.markdown(f"`{bucket:12s}` {bar} {count}")

    with col2:
        st.markdown("**Tool call distribution:**")
        tool_dist = {str(i): sim_tool_calls.count(i) for i in range(4)}
        for n_tools, count in tool_dist.items():
            bar = "█" * (count // 3)
            st.markdown(f"`{n_tools} tool call(s)` {bar} {count}")

    st.markdown("**Key observability tools in production:**")
    st.markdown("""
| Tool | What it traces | Phase connection |
|---|---|---|
| **LangSmith** | LangChain/LangGraph traces natively | Phase 10c |
| **OpenTelemetry** | Any Python code, vendor-neutral | Standard practice |
| **Google Cloud Trace** | Vertex AI agents natively | Phase 11a |
| **Custom JSON logging** | What we built here -- portable | This page |
""")

st.markdown("---")
st.markdown("### What's next -> Phase 7b: Cost & Latency")
st.markdown("Traces give us the data. Phase 7b shows how to ACT on it -- caching, batching, model selection.")
