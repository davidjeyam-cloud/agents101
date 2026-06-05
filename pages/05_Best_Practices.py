"""
Phase 9 — Best Practices (Anthropic Appendix 2)
Four interactive labs: Tool Design · Prompt Engineering · When NOT to Use Agents · Pre-flight Checklist
"""

import streamlit as st
from google import genai
from google.genai import types
from utils.llm import MODEL, _client, _call
from utils.diagrams import diagram_best_practices

st.set_page_config(
    page_title="Phase 9 — Best Practices",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.title("⚡ Phase 9 — Best Practices")
st.caption("Anthropic Appendix 2 · Three pillars that separate a demo agent from a production-ready one")
st.image(diagram_best_practices(), use_container_width=True)

# ── Concept expander ──────────────────────────────────────────────────────────
with st.expander("📖 What are Best Practices — and why does Anthropic dedicate an appendix to them?"):
    st.markdown("""
    Most agentic AI failures are **not model failures** — they are engineering failures.
    Anthropic's production teams identified three recurring root causes:

    | Root Cause | What Goes Wrong | The Fix |
    |---|---|---|
    | **Poorly designed tools** | LLM misuses the tool, calls it with wrong args, or ignores it entirely | Single responsibility, rich docstring, informative errors |
    | **Under-specified prompts** | Agent loops, guesses, goes out of scope, or never stops | Explicit rules, stopping conditions, negative constraints |
    | **Wrong pattern choice** | Agent used where a workflow would be cheaper, faster, and more reliable | Decision framework: agent only when truly needed |

    **The key insight:** An agent is only as good as the instructions and tools you give it.
    A well-engineered workflow will outperform a poorly-prompted agent every time.

    > *"The best agent is often no agent at all — a well-designed pipeline is simpler,
    faster, cheaper, and easier to debug."*  — Anthropic Engineering Blog
    """)

# ── Core Code Pattern expander ────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — Best-Practice Tool Design"):
    st.markdown("**The single most impactful practice: write tools that teach the model how to use them.**")
    col_bad, col_good = st.columns(2)
    with col_bad:
        st.markdown("#### ❌ Bad tool")
        st.code('''\
def get_data(query: str) -> dict:
    """Get data."""
    return fetch_from_api(query)
''', language="python")
        st.markdown("""
        **Problems:**
        - Vague name — "get_data" tells the LLM nothing
        - No docstring — LLM must guess when to call it
        - No parameter guidance — query format unknown
        - No error info — LLM can't handle failures
        """)
    with col_good:
        st.markdown("#### ✅ Good tool")
        st.code('''\
def get_account_balance(account_id: str) -> dict:
    """
    Retrieve the current balance for a NexaBank account.

    Use this when the user asks about their account balance,
    available funds, or current balance figure.
    Do NOT use for transaction history — use get_transactions().

    Args:
        account_id: NexaBank account ID in format ACC-XXXXXX

    Returns:
        {"balance": 1234.56, "currency": "GBP", "as_of": "2026-05-31"}
        {"error": "Account ACC-999999 not found"} on failure

    Example call: get_account_balance("ACC-123456")
    """
    result = fetch_from_api(account_id)
    if not result:
        return {"error": f"Account {account_id} not found"}
    return result
''', language="python")
        st.markdown("""
        **What this achieves:**
        - Clear name: LLM knows exactly what it's for
        - When to use / when NOT to use: reduces wrong calls
        - Parameter format with example: correct args every time
        - Typed error return: LLM can handle failures gracefully
        """)

    st.markdown("---")
    st.markdown("""
    **Why this matters:** The Google Gemini SDK generates the tool schema entirely from
    the Python function signature and docstring. A richer docstring directly becomes
    a richer schema — the LLM receives that context and uses it to decide *when* and
    *how* to call the tool. A one-line docstring and a paragraph docstring produce
    **measurably different tool-call accuracy** on the same queries.
    """)

st.markdown("---")

# ── Four tabs ─────────────────────────────────────────────────────────────────
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "🔧 Tool Design Lab",
    "✍️ Prompt Engineering Clinic",
    "🚦 When NOT to Use Agents",
    "✅ Pre-flight Checklist",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB A — Tool Design Lab
# ════════════════════════════════════════════════════════════════════════════
with tab_a:
    st.markdown("### Tool Design Lab")
    st.markdown(
        "See how tool docstring quality directly changes Gemini's behaviour. "
        "Both functions have **identical logic** — only the description differs."
    )

    st.markdown("#### The two tool versions")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**❌ Version A — poor description**")
        st.code('''\
def fetch_weather(city):
    """Get weather info."""
    # calls Open-Meteo API
    ...
''', language="python")
    with col2:
        st.markdown("**✅ Version B — production description**")
        st.code('''\
def get_weather(city: str) -> dict:
    """
    Get real-time weather for a city using Open-Meteo.

    Use this when the user asks about current weather,
    temperature, humidity, or wind conditions for any city.
    Do NOT use for forecasts — this returns current data only.

    Args:
        city: City name in English, e.g. "London" or "Tokyo"

    Returns:
        {"city": "London", "temperature_c": 18.2,
         "humidity_pct": 72, "wind_kph": 14.4}
        {"error": "City not found"} if lookup fails
    """
    ...
''', language="python")

    st.markdown("---")
    st.markdown("#### Live comparison — same query, both tools")

    query_a = st.text_input(
        "Query to test both tools with:",
        value="What should I wear today in London? Is it rainy?",
        key="tool_query",
    )

    if st.button("▶ Run Tool Design Comparison", type="primary", key="tool_btn"):
        from utils.tools import get_weather

        # Bad version: vague docstring (type hint still required by SDK schema parser)
        def fetch_weather_bad(city: str):
            """Get weather info."""
            return get_weather(city)

        # Good version: rich, production-quality docstring
        def get_weather_good(city: str) -> dict:
            """
            Get real-time weather for a city using Open-Meteo.

            Use this when the user asks about current weather,
            temperature, humidity, or wind conditions for any city.
            Do NOT use for forecasts — this returns current data only.

            Args:
                city: City name in English, e.g. "London" or "Tokyo"

            Returns:
                {"city": "London", "temperature_c": 18.2,
                 "humidity_pct": 72, "wind_kph": 14.4}
                {"error": "City not found"} if lookup fails
            """
            return get_weather(city)

        client = _client()
        results = {}
        traces = {}

        for label, tool_fn in [("A_bad", fetch_weather_bad), ("B_good", get_weather_good)]:
            sys_prompt = "You are a helpful weather assistant. Use tools when needed."
            config = types.GenerateContentConfig(
                tools=[tool_fn],
                system_instruction=sys_prompt,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            convo = client.chats.create(model=MODEL, config=config)
            resp1 = _call(convo.send_message, query_a)

            tool_used = False
            tool_result = None
            tool_call_detail = None

            if resp1.function_calls:
                tool_used = True
                fc = resp1.function_calls[0]
                tool_call_detail = {"name": fc.name, "args": dict(fc.args)}
                raw = tool_fn(**fc.args)
                tool_result = raw
                convo.send_message(
                    types.Part.from_function_response(name=fc.name, response={"result": raw})
                )
                resp2 = _call(convo.send_message, "")
                final = resp2.text
            else:
                final = resp1.text

            results[label] = {
                "final": final,
                "tool_used": tool_used,
                "tool_call": tool_call_detail,
                "tool_result": tool_result,
            }
            traces[label] = {"sys": sys_prompt, "user": query_a}

        # Display results side by side
        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            r = results["A_bad"]
            st.markdown("**Version A — poor description**")
            if r["tool_used"]:
                st.success(f"Tool called: `{r['tool_call']['name']}({r['tool_call']['args']})`")
            else:
                st.error("No tool call — LLM guessed or refused")
            st.info(r["final"])

        with col_r2:
            r = results["B_good"]
            st.markdown("**Version B — production description**")
            if r["tool_used"]:
                st.success(f"Tool called: `{r['tool_call']['name']}({r['tool_call']['args']})`")
            else:
                st.error("No tool call — LLM guessed or refused")
            st.info(r["final"])

        with st.expander("🔬 Execution Trace — exact prompts and tool calls"):
            t1, t2 = st.tabs(["Version A (bad)", "Version B (good)"])
            with t1:
                st.markdown("**System prompt:**")
                st.code(traces["A_bad"]["sys"], language="text")
                st.markdown("**User query:**")
                st.code(traces["A_bad"]["user"], language="text")
                st.markdown("**Tool call issued:**")
                r = results["A_bad"]
                st.code(str(r["tool_call"]) if r["tool_used"] else "None — no tool call made", language="text")
                st.markdown("**Tool result:**")
                st.code(str(r["tool_result"]) if r["tool_result"] else "N/A", language="text")
            with t2:
                st.markdown("**System prompt:**")
                st.code(traces["B_good"]["sys"], language="text")
                st.markdown("**User query:**")
                st.code(traces["B_good"]["user"], language="text")
                st.markdown("**Tool call issued:**")
                r = results["B_good"]
                st.code(str(r["tool_call"]) if r["tool_used"] else "None — no tool call made", language="text")
                st.markdown("**Tool result:**")
                st.code(str(r["tool_result"]) if r["tool_result"] else "N/A", language="text")

    with st.expander("📋 Tool Design Rules — full checklist"):
        st.markdown("""
        | # | Rule | Why it matters |
        |---|---|---|
        | 1 | **Single responsibility** — one tool, one job | LLM can match intent to tool precisely |
        | 2 | **Verb-noun name** — `get_balance`, not `data` | Name alone is part of the schema the LLM reads |
        | 3 | **When to use / when NOT to use** in docstring | Prevents the LLM calling the wrong tool for similar queries |
        | 4 | **Typed parameters with format example** | Reduces invalid arg errors dramatically |
        | 5 | **Explicit return schema** — include both success and error shapes | LLM can reason about and handle failures |
        | 6 | **Return structured errors, never raise** | Agents can't catch exceptions — they need a return value |
        | 7 | **Idempotent read tools** — `get_` never mutates | Safe to call multiple times if the agent retries |
        | 8 | **No side effects in get-tools** | Keeps the agent's observation loop trustworthy |
        """)


# ════════════════════════════════════════════════════════════════════════════
# TAB B — Prompt Engineering Clinic
# ════════════════════════════════════════════════════════════════════════════
with tab_b:
    st.markdown("### Prompt Engineering Clinic")
    st.markdown(
        "System prompts for agents are fundamentally different from chatbot prompts. "
        "See what changes when you go from a generic prompt to an agent-specific one."
    )

    PROMPTS = {
        "❌ Minimal (chatbot-style)": (
            "You are a helpful banking assistant. "
            "You have some tools available."
        ),
        "⚠️ Partial (names tools, no rules)": (
            "You are NexaBank's virtual assistant. "
            "You have access to account tools, stock price tools, and weather tools. "
            "Use them to help the customer."
        ),
        "✅ Production (Anthropic best practice)": (
            "You are NexaBank's virtual assistant.\n\n"
            "RULES:\n"
            "1. For ANY question about account balances or transactions: call get_stock_price() "
            "as a proxy for market data or use available tools — NEVER guess numbers.\n"
            "2. For weather-related travel advice: ALWAYS call get_weather() first.\n"
            "3. SCOPE: you handle ONLY banking and financial queries. "
            "For unrelated topics say: 'I handle banking queries only.'\n"
            "4. STOPPING: if you cannot answer with the available tools, say exactly: "
            "'I don't have the information needed to answer that.'\n"
            "5. NEVER fabricate account numbers, balances, or transaction details.\n\n"
            "Format: respond in plain English. Be concise. Cite the tool result you used."
        ),
    }

    st.markdown("#### The three prompt levels")
    for label, prompt in PROMPTS.items():
        with st.expander(label):
            st.code(prompt, language="text")

    st.markdown("---")
    selected_prompt_label = st.selectbox(
        "Choose a prompt level to test:",
        options=list(PROMPTS.keys()),
        key="prompt_select",
    )
    query_b = st.text_input(
        "Test query:",
        value="What's the weather like in Tokyo today? Should I take an umbrella?",
        key="prompt_query",
    )

    if st.button("▶ Run Prompt Clinic", type="primary", key="prompt_btn"):
        from utils.tools import get_weather, get_stock_price

        system = PROMPTS[selected_prompt_label]
        client = _client()
        config = types.GenerateContentConfig(
            tools=[get_weather, get_stock_price],
            system_instruction=system,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        convo = client.chats.create(model=MODEL, config=config)
        resp = _call(convo.send_message, query_b)

        tool_calls_made = []
        tool_results = []
        final_resp = resp

        if resp.function_calls:
            for fc in resp.function_calls:
                tool_calls_made.append({"name": fc.name, "args": dict(fc.args)})
                fn_map = {"get_weather": get_weather, "get_stock_price": get_stock_price}
                if fc.name in fn_map:
                    result = fn_map[fc.name](**fc.args)
                    tool_results.append(result)
                    convo.send_message(
                        types.Part.from_function_response(name=fc.name, response={"result": result})
                    )
            final_resp = _call(convo.send_message, "")

        st.markdown(f"**Prompt used:** `{selected_prompt_label}`")
        if tool_calls_made:
            st.success(f"Tools called: {[t['name'] for t in tool_calls_made]}")
        else:
            st.warning("No tools called — agent answered from training data (or refused)")
        st.info(final_resp.text)

        with st.expander("🔬 Execution Trace — system prompt, query, tool calls, raw response"):
            t1, t2, t3 = st.tabs(["① System Prompt", "② Tool Calls", "③ Raw Response"])
            with t1:
                st.code(system, language="text")
            with t2:
                if tool_calls_made:
                    for i, (call, result) in enumerate(zip(tool_calls_made, tool_results)):
                        st.markdown(f"**Call {i+1}:** `{call['name']}({call['args']})`")
                        st.code(str(result), language="text")
                else:
                    st.code("No tool calls made", language="text")
            with t3:
                st.code(final_resp.text, language="text")

    with st.expander("📋 Prompt Engineering Rules — full checklist"):
        st.markdown("""
        | # | Rule | Anti-pattern it prevents |
        |---|---|---|
        | 1 | **Explicit tool rules** — "ALWAYS call X before answering Y" | Agent answers from training memory instead of live data |
        | 2 | **Stopping condition** — exact phrase when unable to answer | Infinite loop or hallucinated answer when tools fail |
        | 3 | **Scope definition** — "you handle ONLY X" | Agent answers out-of-domain questions it shouldn't touch |
        | 4 | **Negative constraints** — "NEVER fabricate/guess X" | Hallucinated account numbers, balances, names |
        | 5 | **Output format** — plain English / JSON / bullet points | Inconsistent formatting that breaks downstream parsing |
        | 6 | **Numbered steps** for multi-step processes | Agent skips steps or reorders them |
        | 7 | **Tool disambiguation** — "use X not Y for Z" | Agent calls the wrong tool when two have similar names |
        | 8 | **Cite your source** — "mention which tool result you used" | Opaque answers with no audit trail |
        """)


# ════════════════════════════════════════════════════════════════════════════
# TAB C — When NOT to Use Agents
# ════════════════════════════════════════════════════════════════════════════
with tab_c:
    st.markdown("### When NOT to Use Agents")
    st.markdown(
        "The most expensive mistake in agentic AI is using an agent where a simpler pattern "
        "would be faster, cheaper, and more reliable. This advisor helps you make that call."
    )

    st.markdown("#### Decision framework")
    st.markdown("""
    | Condition | Verdict | Better choice |
    |---|---|---|
    | Steps are fixed and always the same | ❌ Don't use agent | Prompt Chaining |
    | Task is just classifying intent | ❌ Don't use agent | Routing (single LLM call) |
    | Sub-tasks are independent and known upfront | ❌ Don't use agent | Parallelization |
    | Response must arrive in < 2 seconds | ❌ Don't use agent | Single LLM call |
    | Steps depend on each other but are predetermined | ❌ Don't use agent | Orchestrator-Workers |
    | Quality needs iterative improvement with a known rubric | ❌ Don't use agent | Evaluator-Optimizer |
    | Steps are unknown until runtime, tools needed dynamically | ✅ Use agent | ReAct / Planning |
    | Task requires judgement calls mid-execution | ✅ Use agent | ReAct with HITL |
    | Multi-domain delegation needed at runtime | ✅ Use agent | Multi-Agent |
    """)

    st.markdown("---")
    st.markdown("#### Use-case advisor — describe your task, get a recommendation")

    use_case = st.text_area(
        "Describe what your agent needs to do:",
        placeholder=(
            "e.g. 'Read a PDF invoice, extract the total, check it against our database, "
            "and email the finance team if it exceeds £5,000.'"
        ),
        height=100,
        key="usecase_input",
    )

    if st.button("▶ Get Architecture Recommendation", type="primary", key="usecase_btn") and use_case.strip():
        sys_prompt = """\
You are an expert Agentic AI architect. Your job is to recommend the right architecture for a given task.
You deeply understand the trade-offs between: plain LLM, Prompt Chaining, Routing, Parallelization,
Orchestrator-Workers, Evaluator-Optimizer, ReAct Agent, Planning Agent, and Multi-Agent systems.

PHILOSOPHY: Recommend the SIMPLEST pattern that meets the requirements.
Agents introduce latency, cost, and unpredictability — only recommend one when genuinely needed.

Respond in this exact structure:
RECOMMENDATION: [pattern name]
VERDICT: Agent needed / No agent needed — use a workflow
REASON: [2-3 sentences explaining WHY this pattern fits, citing the specific characteristics of the task]
TRADE-OFF: [1 sentence on what you give up with this choice vs the next-simplest alternative]
WATCH OUT FOR: [1 specific failure mode or risk with this approach]
"""
        user_msg = f"Use case: {use_case}"
        client = _client()
        resp = _call(
            client.models.generate_content,
            model=MODEL,
            contents=user_msg,
            config=types.GenerateContentConfig(system_instruction=sys_prompt),
        )
        raw = resp.text

        # Parse and display
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                 for line in raw.splitlines() if ":" in line}

        verdict = lines.get("VERDICT", "")
        if "No agent" in verdict:
            st.warning(f"**{lines.get('RECOMMENDATION', 'Workflow')}**  —  {verdict}")
        else:
            st.success(f"**{lines.get('RECOMMENDATION', 'Agent')}**  —  {verdict}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Why this pattern:**")
            st.info(lines.get("REASON", raw))
            st.markdown("**Trade-off:**")
            st.info(lines.get("TRADE-OFF", "—"))
        with col2:
            st.markdown("**Watch out for:**")
            st.warning(lines.get("WATCH OUT FOR", "—"))

        with st.expander("🔬 Execution Trace — exact prompts and raw response"):
            t1, t2 = st.tabs(["① Prompts", "② Raw Response"])
            with t1:
                st.markdown("**System prompt:**")
                st.code(sys_prompt, language="text")
                st.markdown("**User message:**")
                st.code(user_msg, language="text")
            with t2:
                st.code(raw, language="text")


# ════════════════════════════════════════════════════════════════════════════
# TAB D — Pre-flight Checklist
# ════════════════════════════════════════════════════════════════════════════
with tab_d:
    st.markdown("### Pre-flight Checklist")
    st.markdown(
        "Before deploying any agent to production, it must pass all 10 checks. "
        "Tick what your agent has. Score < 8 = not ready."
    )

    CHECKS = [
        ("🔁 Max iterations guard", "Every agentic loop has a `while i < MAX_ITER` cap — no infinite loops possible"),
        ("🛡️ Input guardrails", "User input is validated/sanitised before reaching the LLM (PII, injection, content policy)"),
        ("🛡️ Output guardrails", "LLM responses are validated before being shown or acted upon"),
        ("🔧 Tools return errors, never raise", "All tools return `{\"error\": \"...message...\"}` on failure — no uncaught exceptions"),
        ("📋 Tools have rich docstrings", "Every tool has: purpose, when to use, when NOT to use, param format, return schema"),
        ("✍️ System prompt has explicit rules", "Prompt includes: tool rules, stopping condition, scope, negative constraints"),
        ("👤 HITL on irreversible actions", "Agent pauses for human approval before payments, cancellations, or deletions"),
        ("🔭 Every LLM call is traced", "All calls log: timestamp, latency, token count, cost — observable in production"),
        ("💥 Tested with adversarial inputs", "Tried injection attacks, out-of-scope queries, tool failures, and edge cases"),
        ("💰 Cost and latency measured", "You know the p50/p95 latency and cost-per-request before shipping"),
    ]

    checked = []
    for i, (title, description) in enumerate(CHECKS):
        col_check, col_desc = st.columns([1, 5])
        with col_check:
            val = st.checkbox(title, key=f"check_{i}")
            checked.append(val)
        with col_desc:
            st.caption(description)

    score = sum(checked)
    total = len(CHECKS)

    st.markdown("---")
    st.markdown(f"### Score: {score} / {total}")
    progress_val = score / total
    st.progress(progress_val)

    if score == total:
        st.success("## ✅ Production Ready — all checks pass. Ship it.")
        st.balloons()
    elif score >= 8:
        missing = [CHECKS[i][0] for i, v in enumerate(checked) if not v]
        st.warning(f"## ⚠️ Nearly Ready — {total - score} check(s) remaining")
        st.markdown("**Outstanding:**")
        for m in missing:
            st.markdown(f"- {m}")
    elif score >= 5:
        missing = [CHECKS[i][0] for i, v in enumerate(checked) if not v]
        st.error(f"## ❌ Not Ready — {total - score} critical gaps")
        st.markdown("**Prioritise these:**")
        for m in missing:
            st.markdown(f"- {m}")
    else:
        st.error("## 🚨 High Risk — do not deploy. Revisit the course phases and recheck.")

    st.markdown("---")
    st.markdown("#### Why each check matters")
    st.markdown("""
    | Check | What breaks without it |
    |---|---|
    | Max iterations guard | Agent loops forever, burns tokens, times out users |
    | Input guardrails | PII leaks, prompt injection overrides system behaviour |
    | Output guardrails | Harmful content reaches the user or downstream systems |
    | Tools return errors | Unhandled exception crashes the agent mid-task |
    | Rich tool docstrings | LLM misuses tools, calls wrong one, passes invalid args |
    | Explicit system prompt rules | Agent guesses, hallucinates, or goes out of scope |
    | HITL on irreversible actions | Autonomous agent makes irreversible mistakes |
    | All LLM calls traced | Production incident with no audit trail to debug |
    | Adversarial testing | First real user breaks it in ways you never anticipated |
    | Cost/latency measured | Surprise bill or SLA breach at scale |
    """)

st.markdown("---")

with st.expander("🎛️ Fine-tuning vs RAG vs Prompt Engineering — when to reach for each"):
    st.markdown("""
One of the most common architectural mistakes in production is reaching for fine-tuning when
prompting or RAG would solve the problem faster, cheaper, and more reliably.

**The three tools and what they actually change:**

| Approach | What it changes | Requires | Cost |
|---|---|---|---|
| **Prompt Engineering** | How the model interprets and responds to instructions | Good prompt design | Near-zero — just tokens |
| **RAG** (Phase 5a) | What factual knowledge the model has access to | Vector store + retrieval pipeline | Embedding + retrieval tokens |
| **Fine-tuning** (LoRA / QLoRA / IA3) | The model's weights — its internal "skill" | Training data + GPU compute + expertise | High — training run + infra |

**Decision guide — reach for each when:**

| Scenario | Reach for | Why |
|---|---|---|
| Agent answers incorrectly about YOUR org's policies/data | **RAG** | The model doesn't know your data — retrieve it |
| Agent uses the wrong tone, format, or persona | **Prompt Engineering** | Behaviour is a prompting problem, not a knowledge problem |
| Agent doesn't know how to do a NEW TASK TYPE it was never trained for | **Fine-tuning** | Adding a capability the base model lacks |
| Agent knows the task but ignores your output format | **Prompt Engineering** | Few-shot examples in the prompt almost always fix this |
| Agent needs to do something extremely fast with tiny model on-device | **Fine-tuning (QLoRA)** | Distil the capability into a small, quantised model |
| Agent needs real-time or frequently updated information | **RAG** | Fine-tuning bakes in stale knowledge at training time |
| Agent needs to reason in a specialised domain (legal, medical, code) | **RAG first, fine-tune if RAG insufficient** | RAG is cheaper and faster to iterate |

**The 80/20 rule of production agents:**

> In practice, 80% of "the model doesn't know this" problems are solved by better RAG.
> 15% are solved by better prompts. Only 5% genuinely require fine-tuning.

**Why fine-tuning is a last resort in agentic systems:**

1. **It doesn't help with current facts** — fine-tuned weights are static; RAG retrieves live data
2. **It's expensive to iterate** — a prompt change takes seconds; a fine-tuning run takes hours
3. **It breaks other capabilities** — fine-tuning can catastrophically forget unrelated skills
4. **You own the model** — hosting a fine-tuned open-source model adds infra responsibility

**When fine-tuning IS the right answer:**
- You need a very small, fast, cheap model for high-volume inference
- You're adding a genuinely new skill (not just knowledge)
- Your task has a very specific, repetitive format that prompting alone can't reliably produce
- You're in an air-gapped environment with no internet access for RAG

**LoRA / QLoRA / IA3 — what each optimises:**

| Technique | Memory | Speed | Use when |
|---|---|---|---|
| **LoRA** | Moderate savings | Moderate | Standard fine-tuning on a single GPU |
| **QLoRA** | Very high savings (4-bit) | Slower training | Large model on limited GPU memory |
| **IA3** | Minimal parameters changed | Fastest to train | Few-shot task adaptation, minimal data |

*Note: Implementing these requires a separate setup (HuggingFace `peft`, `transformers`, GPU compute)
— they are not part of this course's Gemini API stack. The decision framework above is the
architecturally relevant part for agent builders.*
""")

st.markdown("---")
st.markdown("### What's next → Phase 10 — Frameworks Layer")
st.caption(
    "Phase 10 applies everything you've built from scratch to LangGraph, LangChain, and Google ADK. "
    "You now have the foundation to read framework source code and understand it immediately."
)
