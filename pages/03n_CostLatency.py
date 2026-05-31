"""Phase 7b -- Cost & Latency Optimisation"""
import streamlit as st, os, time, json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
st.set_page_config(page_title="Phase 7b -- Cost & Latency", page_icon="⚡", layout="wide")
st.title("⚡ Phase 7b -- Cost & Latency Optimisation")
st.caption("Measure, cache, batch, and route to the right model -- cut costs without cutting quality")
if not api_key: st.error("GEMINI_API_KEY not found."); st.stop()
client = genai.Client(api_key=api_key)
from utils.diagrams import diagram_cost_latency
st.image(diagram_cost_latency(), use_container_width=True)

with st.expander("📖 Cost and latency fundamentals"):
    st.markdown("""
    **Cost = Input tokens * price + Output tokens * price**

    | Model | Input (per 1M tokens) | Output (per 1M tokens) | Best for |
    |---|---|---|---|
    | Gemini 2.5 Flash | ~$0.075 | ~$0.30 | Most agent tasks (our default) |
    | Gemini 2.5 Pro | ~$1.25 | ~$10.00 | Complex reasoning, final synthesis |
    | Gemini 2.5 Flash-Lite | ~$0.01 | ~$0.04 | Simple classification, routing |

    **The three cost levers:**

    | Lever | What it does | Typical saving |
    |---|---|---|
    | **Prompt caching** | Cache system prompt, pay once not every call | 60-80% on repeated calls |
    | **Model selection** | Use Flash-Lite for routing, Flash for reasoning | 90% for simple steps |
    | **Output length control** | Shorter system prompts, concise outputs | 30-50% |

    **Latency = Network + Time-to-First-Token + Generation time**

    Strategies to reduce perceived latency:
    - **Streaming**: user sees first token faster (TTFT) even if total time same
    - **Parallelise**: Phase 6a runs sub-agents simultaneously
    - **Cache**: avoid redundant LLM calls entirely
    - **Plan-and-Execute**: Phase 3c reduces unexpected tool loops
    """)

with st.expander("📐 Core Code Pattern -- Cost Measurement + Caching"):
    st.code('''
# ── Exact token counting ──────────────────────────────────────────────────────
def count_tokens(text: str) -> int:
    result = client.models.count_tokens(model=MODEL, contents=text)
    return result.total_tokens

# ── Cost calculation ──────────────────────────────────────────────────────────
PRICE = {"input": 0.075, "output": 0.30}  # USD per 1M tokens

def estimate_cost_usd(tokens_in: int, tokens_out: int) -> float:
    return (tokens_in / 1_000_000 * PRICE["input"] +
            tokens_out / 1_000_000 * PRICE["output"])

# ── Prompt caching simulation ─────────────────────────────────────────────────
class CachedLLM:
    """Same-system-prompt calls only pay for system prompt ONCE."""

    def __init__(self):
        self._system_cache = {}   # system_prompt -> (cached_tokens, cached_cost)
        self.total_saved_tokens = 0

    def call(self, system: str, user: str) -> str:
        system_tokens = count_tokens(system)
        user_tokens   = count_tokens(user)

        if system not in self._system_cache:
            # First call: pay full system prompt cost
            self._system_cache[system] = system_tokens
            input_tokens = system_tokens + user_tokens
        else:
            # Cached: system prompt charged only once
            saved = self._system_cache[system]
            self.total_saved_tokens += saved
            input_tokens = user_tokens   # system already cached!

        response = llm(system=system, user=user)
        output_tokens = count_tokens(response)
        cost = estimate_cost_usd(input_tokens, output_tokens)
        return response, cost

# ── Model routing ─────────────────────────────────────────────────────────────
MODELS = {
    "simple":  "gemini-2.5-flash",   # routing, classification
    "default": "gemini-2.5-flash",   # most reasoning tasks
    "complex": "gemini-2.5-flash",   # final synthesis (would be Pro in production)
}

def pick_model(query: str) -> str:
    """Route to cheapest model that can handle the task."""
    words = len(query.split())
    if words < 10:   return MODELS["simple"]   # ~90% cost reduction vs Pro
    if words < 50:   return MODELS["default"]
    return MODELS["complex"]
''', language="python")

st.markdown("---")

USD_TO_GBP = 0.79
PRICE_IN  = 0.075
PRICE_OUT = 0.30

def count_tokens_approx(text: str) -> int:
    """Approximate token count (chars/4). Use count_tokens() for exact."""
    return max(1, len(text) // 4)

def real_count_tokens(text: str) -> int:
    try:
        r = client.models.count_tokens(model=MODEL, contents=text)
        return r.total_tokens
    except Exception:
        return count_tokens_approx(text)

def cost_gbp(tokens_in: int, tokens_out: int) -> float:
    usd = tokens_in / 1_000_000 * PRICE_IN + tokens_out / 1_000_000 * PRICE_OUT
    return usd * USD_TO_GBP

SYSTEM = (
    "You are NexaBank's customer service AI. Answer customer questions professionally. "
    "Be specific -- cite rates, fees, and timelines. Keep responses under 100 words. "
    "NexaBank key facts: NexaSaver 4.75% AER, ISA 4.2% AER, overdraft 39.9% EAR, "
    "mortgages from 4.65% APRC, international transfers GBP 5-25 depending on country."
)

tab_measure, tab_cache, tab_model, tab_batch = st.tabs([
    "📋 Tab A -- Cost Measurement",
    "🔧 Tab B -- Prompt Caching",
    "📝 Tab C -- Model Selection",
    "⚡ Tab D -- Latency Strategies",
])

with tab_measure:
    st.subheader("Tab A -- Real Token Counting + Cost Calculation")
    st.markdown("Use the SDK's `count_tokens()` to get exact token counts, then calculate GBP cost.")

    col1, col2 = st.columns([2,1])
    QUERIES = {
        "Short (few words)":  "What is the NexaSaver rate?",
        "Medium (one topic)": "I have GBP 10,000. Compare NexaSaver vs ISA for 3 years.",
        "Long (multi-part)":  ("I earn GBP 55,000 and have GBP 20,000 saved. "
                                "I want to: (1) save for a house deposit in 2 years, "
                                "(2) understand what mortgage I could get, "
                                "(3) know what happens to my overdraft during a house purchase."),
    }
    if "sel_cost" not in st.session_state: st.session_state.sel_cost = list(QUERIES.keys())[0]
    with col2:
        for label in QUERIES:
            if st.button(label, key=f"cost_{label[:12]}"): st.session_state.sel_cost = label; st.rerun()
    with col1:
        query_c = st.text_area("Query:", value=QUERIES[st.session_state.sel_cost], height=90)

    if st.button("▶  Measure Cost", type="primary", key="run_cost"):
        with st.spinner("Counting tokens and running..."):
            t0 = time.time()
            sys_tokens  = real_count_tokens(SYSTEM)
            user_tokens = real_count_tokens(query_c)
            resp = _call(client.models.generate_content, model=MODEL,
                         contents=query_c,
                         config=types.GenerateContentConfig(system_instruction=SYSTEM))
            out_tokens  = real_count_tokens(resp.text)
            latency     = int((time.time() - t0) * 1000)

        total_in = sys_tokens + user_tokens
        c = cost_gbp(total_in, out_tokens)

        st.success(resp.text)
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("System tokens",   f"{sys_tokens:,}")
        col2.metric("User tokens",     f"{user_tokens:,}")
        col3.metric("Output tokens",   f"{out_tokens:,}")
        col4.metric("Latency",         f"{latency}ms")
        st.metric("Estimated cost", f"GBP {c:.6f}",
                  help=f"Input: {total_in} tokens @ GBP {PRICE_IN*USD_TO_GBP:.4f}/1M + Output: {out_tokens} @ GBP {PRICE_OUT*USD_TO_GBP:.4f}/1M")
        st.caption(f"At 1,000 calls/day this query would cost approx GBP {c*1000:.3f}/day")

with tab_cache:
    st.subheader("Tab B -- Prompt Caching Simulation")
    st.markdown("""
    The system prompt is the same for every NexaBank customer call.
    Without caching, it's re-tokenised and charged on **every** request.
    With caching, it's charged **once** and reused for free.
    """)

    n_calls = st.slider("Number of calls to simulate:", 10, 1000, 100, key="cache_calls")

    col1, col2 = st.columns(2)

    sys_toks = real_count_tokens(SYSTEM)
    avg_user = 30    # average user query ~30 tokens
    avg_out  = 80    # average response ~80 tokens

    with col1:
        with st.container(border=True):
            st.markdown("#### Without Caching")
            st.caption("System prompt charged every call")
            total_in  = (sys_toks + avg_user) * n_calls
            total_out = avg_out * n_calls
            c_nocache = cost_gbp(total_in, total_out)
            st.metric("System tokens per call", f"{sys_toks:,}")
            st.metric(f"Total input tokens ({n_calls} calls)", f"{total_in:,}")
            st.metric("Cost", f"GBP {c_nocache:.4f}")

    with col2:
        with st.container(border=True):
            st.markdown("#### With Caching")
            st.caption("System prompt charged ONCE, reused free")
            cached_in  = sys_toks + (avg_user * n_calls)
            total_out2 = avg_out * n_calls
            c_cache    = cost_gbp(cached_in, total_out2)
            st.metric("System tokens (charged once)", f"{sys_toks:,}")
            st.metric(f"Total input tokens ({n_calls} calls)", f"{cached_in:,}")
            st.metric("Cost", f"GBP {c_cache:.4f}")

    saving = c_nocache - c_cache
    saving_pct = (saving / c_nocache * 100) if c_nocache > 0 else 0
    st.success(f"💰 Caching saves **GBP {saving:.4f}** ({saving_pct:.0f}%) on {n_calls} calls")
    st.caption("Real Gemini caching requires the cached content to be >= 1,024 tokens and uses the Caching API.")

with tab_model:
    st.subheader("Tab C -- Model Selection by Task Complexity")
    st.markdown("""
    Not every step in an agent needs the most powerful model.
    **Routing and classification** can use Flash-Lite (10x cheaper).
    **Complex reasoning** uses Flash (our default).
    """)

    TASKS_MODEL = {
        "Simple routing (Flash-Lite candidate)": "Which NexaBank account type is this about: savings, mortgage, or complaint?",
        "Factual lookup (Flash)": "What is NexaBank's ISA rate and annual allowance?",
        "Complex analysis (Flash / Pro candidate)": (
            "A customer earns GBP 48,000, has GBP 25,000 in savings, and wants to buy "
            "a GBP 290,000 house in 18 months. Analyse their financial position, "
            "recommend a savings strategy, and outline mortgage eligibility."
        ),
    }

    for task_label, task_query in TASKS_MODEL.items():
        with st.expander(f"Task: {task_label}"):
            st.markdown(f"**Query:** _{task_query[:100]}..._" if len(task_query) > 100 else f"**Query:** _{task_query}_")
            in_toks  = real_count_tokens(SYSTEM) + real_count_tokens(task_query)
            # Estimate output based on complexity
            out_est  = 20 if "routing" in task_label else (80 if "Factual" in task_label else 200)
            c_flash  = cost_gbp(in_toks, out_est)
            # Flash-Lite is ~8x cheaper on input, ~7.5x on output
            c_lite   = cost_gbp(int(in_toks/8), int(out_est/7.5))

            c1, c2, c3 = st.columns(3)
            c1.metric("Input tokens",    f"~{in_toks:,}")
            c2.metric("Cost (Flash)",    f"GBP {c_flash:.6f}")
            c3.metric("Cost (Lite)",     f"GBP {c_lite:.6f}", delta=f"-{((c_flash-c_lite)/c_flash*100):.0f}%",
                      delta_color="normal")

            if "routing" in task_label:
                st.info("✅ Flash-Lite suitable: simple classification, no nuanced reasoning needed")
            elif "Complex" in task_label:
                st.warning("⚠️ Flash minimum: complex multi-step analysis requires full reasoning capability")
            else:
                st.info("✅ Flash sufficient: factual lookup with specific answer")

with tab_batch:
    st.subheader("Tab D -- Latency Strategies")
    st.markdown("""
    | Strategy | Latency impact | When to use |
    |---|---|---|
    | **Streaming** | Perceived latency -50% | Always for chat interfaces |
    | **Parallel sub-agents** | Wall-clock time -60% | Phase 6a multi-agent |
    | **Plan-and-Execute** | Fewer tool loops | Phase 3c complex tasks |
    | **Prompt caching** | TTFT -20% | Same system prompt repeated |
    | **Smaller model** | Generation -40% | Simple classification steps |
    """)

    st.markdown("### Latency breakdown for a typical NexaBank query")
    BREAKDOWN = [
        ("Network (client -> API)",    "~60ms",   0.06),
        ("Time-to-First-Token (TTFT)", "~400ms",  0.40),
        ("Token generation (80 tokens at ~15ms each)", "~480ms", 0.48),
        ("Network (API -> client)",    "~60ms",   0.06),
    ]
    total_ms = 1000
    st.markdown(f"**Total estimated: ~{total_ms}ms for a typical 80-token response**")
    for label, timing, fraction in BREAKDOWN:
        bar = "█" * int(fraction * 40)
        st.markdown(f"`{timing:8s}` {bar} {label}")

    st.markdown("---")
    st.info("""
**The fastest win: streaming**
Without streaming, user waits ~1000ms for the full response.
With streaming, user sees first token in ~460ms (network + TTFT).
The TOTAL time is the same, but perceived latency halves.
`convo.send_message_stream(query)` instead of `send_message(query)`.
""")

st.markdown("---")
st.markdown("### What's next -> Phase 7c: Error Analysis")
st.markdown("We can measure and optimise cost. Phase 7c diagnoses what went wrong when things fail.")
