"""
Phase 6a -- Multi-Agent Systems (Andrew Ng Pattern 4)
Root orchestrator routes to specialist sub-agents.
Each sub-agent is a full LLM agent with its own system prompt, tools, and reasoning loop.

Three tabs:
  A. Single Delegation  -- root picks one specialist, traces full chain
  B. Parallel           -- root fans out to multiple specialists, merges results
  C. Comparison         -- Multi-Agent vs Phase 2d Orchestrator-Workers
"""

import streamlit as st
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL
from utils.tools import get_country_info, get_public_holidays

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 6a -- Multi-Agent", page_icon="🤝", layout="wide")
st.title("🤝 Phase 6a -- Multi-Agent Systems")
st.caption("Andrew Ng Pattern 4 -- root orchestrator delegates to specialist sub-agents, each a full autonomous agent")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_multi_agent
st.image(diagram_multi_agent(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 Deep dive -- Multi-Agent vs everything before it"):
    st.markdown("""
    > *"Multi-agent architectures allow agents to specialise and work in parallel --
    > each agent can focus on one thing it does well."*
    > -- Andrew Ng, DeepLearning.AI Agentic AI Course

    ---

    ### What changed from Phase 2d (Orchestrator-Workers)?

    | Feature | Phase 2d Orchestrator-Workers | Phase 6a Multi-Agent |
    |---|---|---|
    | **Workers are** | LLM calls (stateless functions) | Full agents (own tools + reasoning) |
    | **Workers can** | Generate one response | Use tools, loop, replan, reflect |
    | **Orchestrator plans** | Once upfront, fixed | Dynamically based on responses |
    | **Worker autonomy** | Zero -- follows a script | High -- makes its own decisions |
    | **Feedback loop** | No -- linear flow | Yes -- sub-agent results influence routing |
    | **Failure handling** | Propagates upward | Sub-agent can retry independently |
    | **Is it an agent?** | Orchestrator: partially. Workers: No | All: Yes |

    ### The key distinction in one sentence:
    > Phase 2d workers are **called functions**. Phase 6a sub-agents are **autonomous agents that happen to be called.**

    ### How the root agent works:
    The root agent receives the user query and has **sub-agent delegation functions as tools**.
    It reasons like any ReAct agent -- but instead of calling `get_weather()`, it calls
    `banking_specialist("what rates do you offer?")`.

    The sub-agent then runs its OWN full agent loop -- possibly calling real tools,
    reflecting, replanning -- before returning its result to the root.

    ### NexaBank Multi-Agent Architecture:

    | Sub-Agent | Specialisation | Tools Available |
    |---|---|---|
    | **Banking Specialist** | Accounts, rates, savings, mortgages | NexaBank policy knowledge |
    | **Fraud Specialist** | Fraud detection, reporting, security, APP fraud | NexaBank security procedures |
    | **International Specialist** | SWIFT, fees, exchange rates, cross-border | `get_country_info`, NexaBank intl policy |
    | **Complaints Specialist** | Escalation, Ombudsman, resolution, compensation | NexaBank complaints procedure |

    ### What makes this Pattern 4 per Andrew Ng:
    - Agents **specialise** (each sub-agent is an expert in one domain)
    - Agents can run **in parallel** (independent work streams)
    - The system **scales** by adding more specialists, not by making one agent larger
    - Each sub-agent can itself **spawn sub-sub-agents** (recursive multi-agent)
    """)

with st.expander("📐 Core Code Pattern -- Multi-Agent with Delegation"):
    st.code('''
# ── Sub-agent factory ─────────────────────────────────────────────────────────
def run_sub_agent(name: str, system: str, tools: list, query: str, trace: list) -> str:
    """Create and run a specialist sub-agent. Returns final response text."""
    trace.append({"event": "sub_start", "agent": name, "query": query})

    config = types.GenerateContentConfig(
        tools=tools or [],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        system_instruction=system,
    )
    convo = client.chats.create(model=MODEL, config=config)
    response = _call(convo.send_message, query)

    # Sub-agent\'s own tool loop (it is a full ReAct agent)
    MAX_STEPS = 4
    for _ in range(MAX_STEPS):
        if not response.function_calls:
            break
        fc = response.function_calls[0]
        result = call_tool(fc.name, dict(fc.args))        # sub-agent calls real tools
        trace.append({"event": "tool_call", "agent": name, "tool": fc.name, "result": result[:100]})
        response = _call(convo.send_message,
                         types.Part.from_function_response(name=fc.name, response={"result": result}))

    trace.append({"event": "sub_result", "agent": name, "result": response.text[:200]})
    return response.text

# ── Root delegation tools (each wraps a sub-agent) ───────────────────────────
def banking_specialist(query: str) -> str:
    """Handle NexaBank account, savings, mortgage and rate questions."""
    return run_sub_agent("Banking", BANKING_SYSTEM, [], query, trace)

def fraud_specialist(query: str) -> str:
    """Handle fraud reporting, security alerts and APP fraud questions."""
    return run_sub_agent("Fraud", FRAUD_SYSTEM, [], query, trace)

def international_specialist(query: str) -> str:
    """Handle international transfers, SWIFT, fees and foreign currency."""
    return run_sub_agent("International", INTL_SYSTEM, [get_country_info], query, trace)

def complaints_specialist(query: str) -> str:
    """Handle complaints, escalation, Financial Ombudsman and compensation."""
    return run_sub_agent("Complaints", COMPLAINTS_SYSTEM, [], query, trace)

# ── Root orchestrator ─────────────────────────────────────────────────────────
root_config = types.GenerateContentConfig(
    tools=[banking_specialist, fraud_specialist, international_specialist, complaints_specialist],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    system_instruction=(
        "You are NexaBank\'s root orchestrator. Route each customer query to the "
        "right specialist. For complex queries, call multiple specialists and synthesize."
    ),
)
root_convo = client.chats.create(model=MODEL, config=root_config)
response = root_convo.send_message(user_query)

# Root\'s own delegation loop
while response.function_calls:
    fc = response.function_calls[0]
    specialist_result = call_specialist(fc.name, fc.args["query"])   # runs a sub-agent
    trace.append({"event": "root_delegation", "to": fc.name, "query": fc.args["query"]})
    response = root_convo.send_message(
        types.Part.from_function_response(name=fc.name, response={"result": specialist_result})
    )
final_answer = response.text
''', language="python")
    st.markdown("""
**Why delegation tools are the cleanest pattern:**
The root agent sees `banking_specialist(query)` as just another function.
It doesn\'t know or care that this function spins up a full LLM agent underneath.
The sub-agent is completely encapsulated -- change its implementation without touching root.

**The ReAct loop is at EVERY level:**
Root: Think (which specialist?) -> Act (call specialist) -> Observe (result) -> loop
Sub-agent: Think (how to answer?) -> Act (call tool) -> Observe (result) -> loop

**Connecting to Phase 2d:**
In Phase 2d, the Orchestrator called `generate_content(system=specialist_prompt)` -- a stateless call.
In Phase 6a, the root calls `banking_specialist(query)` which runs a full stateful agent conversation.
The difference: sub-agents can use tools, loop, and make their own decisions.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SUB-AGENT SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

BANKING_SYSTEM = """You are NexaBank's Banking Specialist agent.
You handle: accounts (NexaCurrent, NexaSaver, NexaFlex ISA), interest rates, mortgages, overdrafts.

Key NexaBank facts:
- NexaCurrent: no monthly fee, 0.1% cashback, overdraft up to GBP 2,000 at 39.9% EAR
- NexaSaver: 4.75% AER variable, minimum GBP 100
- NexaFlex ISA: 4.2% AER tax-free, annual allowance GBP 20,000
- Mortgages: 2yr fix 4.89%, 5yr fix 4.65%, 10yr fix 4.99% APRC; max LTV 95% FTB
- Overdraft buffer: GBP 1 (no charge under this)

Be specific, cite rates and policies. Recommend based on customer needs."""

FRAUD_SYSTEM = """You are NexaBank's Fraud Specialist agent.
You handle: fraud reporting, card fraud, APP fraud, account security, suspicious activity.

Key NexaBank facts:
- Report fraud: app (Report Fraud in Security), 0800 123 4567 (24/7), secure message
- Account frozen immediately on fraud report
- APP (Authorised Push Payment) fraud: report within 13 months, up to GBP 415,000 reimbursement (PSR 2023)
- Replacement card: 3-5 working days
- NexaBank will NEVER ask for PIN, full password, or to move money to a safe account

Respond urgently and calmly. Prioritise customer safety."""

INTL_SYSTEM = """You are NexaBank's International Banking Specialist agent.
You handle: international transfers, SWIFT, fees, exchange rates, foreign currency.
You have access to the get_country_info tool for country-specific details.

Key NexaBank facts:
- EU/EEA (SEPA): GBP 5 fee, 1-3 business days
- US/Canada/Australia: GBP 15 fee, 2-5 business days
- All other countries: GBP 25 fee, 2-5 business days
- Exchange rate: mid-market + 0.5% margin
- Max single transfer: GBP 100,000 (higher needs Enhanced Due Diligence)
- Payments above GBP 10,000 may be held 2 business days for AML review

Use get_country_info to provide country-specific context when relevant."""

COMPLAINTS_SYSTEM = """You are NexaBank's Complaints Specialist agent.
You handle: complaints, escalation paths, Financial Ombudsman Service, compensation.

Key NexaBank facts:
- Step 1: Contact NexaBank (phone, secure message, branch) -- aim to resolve in 3 business days
- Step 2: If unresolved after 8 weeks -- customer can go to Financial Ombudsman Service (FOS) FREE
- FOS contact: www.financial-ombudsman.org.uk or 0800 023 4567
- FCA contact: www.fca.org.uk/consumers
- Distress compensation: up to GBP 200 at NexaBank discretion
- FOS awards: up to GBP 375,000 for financial losses
- Final Response Letter issued within 8 weeks in all cases

Be empathetic, acknowledge the issue, and provide clear escalation steps."""

ROOT_SYSTEM = """You are NexaBank's root orchestrator agent.
Your job: receive the customer query, determine which specialist(s) can best help,
delegate to them, and synthesize a complete, coherent response.

Specialist routing guide:
- Account rates, savings, mortgages, overdrafts -> banking_specialist
- Fraud, card stolen, suspicious activity, APP fraud -> fraud_specialist
- International transfers, SWIFT, foreign payments -> international_specialist
- Complaints, escalation, Ombudsman -> complaints_specialist
- Mixed query -> call MULTIPLE specialists and combine answers

ALWAYS route to at least one specialist before responding.
After receiving specialist results, synthesize into a clear, professional customer response."""

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

AVAILABLE_TOOLS = {
    "get_country_info": get_country_info,
    "get_public_holidays": get_public_holidays,
}


def call_tool_fn(name: str, args: dict) -> str:
    fn = AVAILABLE_TOOLS.get(name)
    if not fn:
        return f"Tool {name} not available"
    try:
        return str(fn(**args))
    except Exception as e:
        return f"Tool error: {e}"


def run_sub_agent(name: str, system: str, tools: list, query: str, trace: list) -> tuple:
    """
    Run a specialist sub-agent.
    Returns (response_text, steps_taken) and populates trace.
    """
    trace.append({
        "event":   "sub_start",
        "agent":   name,
        "query":   query,
        "system":  system,
    })

    tool_configs = [t for t in tools] if tools else []
    config = types.GenerateContentConfig(
        tools=tool_configs if tool_configs else None,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        if tool_configs else None,
        system_instruction=system,
    )
    if not tool_configs:
        config = types.GenerateContentConfig(system_instruction=system)

    convo = client.chats.create(model=MODEL, config=config)
    response = _call(convo.send_message, query)

    steps = 0
    MAX_STEPS = 4
    for _ in range(MAX_STEPS):
        if not response.function_calls:
            break
        fc = response.function_calls[0]
        args = dict(fc.args)
        tool_result = call_tool_fn(fc.name, args)
        trace.append({
            "event":  "sub_tool",
            "agent":  name,
            "tool":   fc.name,
            "args":   args,
            "result": tool_result[:300],
        })
        steps += 1
        response = _call(
            convo.send_message,
            types.Part.from_function_response(name=fc.name, response={"result": tool_result}),
        )

    result_text = response.text.strip()
    trace.append({
        "event":  "sub_result",
        "agent":  name,
        "result": result_text,
        "steps":  steps,
    })
    return result_text, steps


def render_trace(trace: list):
    """Render the full multi-agent trace in the UI."""
    st.markdown("### 🔬 Full Execution Trace -- every decision and delegation")
    st.caption(
        "Read top to bottom: root decides -> delegates -> sub-agent runs -> "
        "result returns -> root synthesizes."
    )

    for i, event in enumerate(trace):
        ev = event["event"]

        if ev == "root_start":
            with st.container(border=True):
                st.markdown("#### 🤖 ROOT AGENT -- receives user query")
                st.info(f"**User query:** {event['query']}")
                st.code(ROOT_SYSTEM[:300] + "...", language="text")

        elif ev == "root_delegation":
            with st.container(border=True):
                st.markdown(f"#### 🤖 ROOT -> delegates to **{event['specialist']}**")
                st.warning(f"**Delegation query:** {event['query']}")
                st.caption("Root decided this specialist is best for this part of the task.")

        elif ev == "sub_start":
            with st.container(border=True):
                st.markdown(f"#### 👤 {event['agent']} SPECIALIST -- starts")
                st.info(f"**Received query:** {event['query']}")
                with st.expander(f"System prompt for {event['agent']} specialist"):
                    st.code(event["system"], language="text")

        elif ev == "sub_tool":
            with st.container(border=True):
                st.markdown(f"#### 🔧 {event['agent']} -- calls tool: `{event['tool']}`")
                st.code(f"Args: {json.dumps(event['args'])}\nResult: {event['result']}", language="text")

        elif ev == "sub_result":
            with st.container(border=True):
                st.markdown(f"#### ✅ {event['agent']} SPECIALIST -- returns result")
                st.success(event["result"])
                st.caption(f"Tool calls made by sub-agent: {event['steps']}")

        elif ev == "root_synthesis":
            with st.container(border=True):
                st.markdown("#### 🤖 ROOT AGENT -- synthesizes final answer")
                st.caption("Root has all specialist results. Composing final response.")

        elif ev == "final":
            with st.container(border=True):
                st.markdown("#### ? FINAL ANSWER delivered to customer")
                st.success(event["answer"])


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_a, tab_b, tab_c = st.tabs([
    "📋 Tab A -- Single Delegation",
    "🔧 Tab B -- Parallel Specialists",
    "📝 Tab C -- vs Orchestrator-Workers",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB A -- Single Delegation with full trace
# ════════════════════════════════════════════════════════════════════════════

with tab_a:
    st.subheader("Tab A -- Single Delegation with Full Execution Trace")
    st.markdown("""
    Root agent receives the query, decides which specialist to call, delegates,
    and synthesizes the result. Every step is visible in the trace below.
    """)

    TASKS_A = {
        "Savings rate inquiry (Banking Specialist)":
            "I have GBP 5,000 to save for 2 years. What NexaBank savings options do you recommend and what are the current rates?",
        "Fraud report (Fraud Specialist)":
            "Someone has made three unauthorized transactions on my card totalling GBP 680. What do I do right now?",
        "International transfer (International Specialist + tool)":
            "I need to send GBP 8,000 to my family in Japan. What are the fees, exchange rate, and how long will it take?",
        "Complaint escalation (Complaints Specialist)":
            "NexaBank still hasn't resolved my complaint after 10 weeks. What are my options and can I go to the Ombudsman?",
        "Mortgage query (Banking Specialist)":
            "I earn GBP 60,000 and want to buy a GBP 280,000 house. What mortgage can I get and what are current NexaBank rates?",
    }

    if "sel_ma_a" not in st.session_state:
        st.session_state.sel_ma_a = list(TASKS_A.keys())[0]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Scenarios:**")
        for label in TASKS_A:
            if st.button(label, key=f"maa_{label}"):
                st.session_state.sel_ma_a = label
                st.rerun()
    with col1:
        query_a = st.text_area("Customer query:", value=TASKS_A[st.session_state.sel_ma_a], height=90)

    if st.button("▶  Run Multi-Agent", type="primary", key="run_ma_a"):
        trace_a = []
        trace_a.append({"event": "root_start", "query": query_a})

        # ── Root agent setup ──────────────────────────────────────────────
        _delegations_a = {}

        def banking_specialist_a(query: str) -> str:
            """Handle NexaBank account, savings, mortgage and rate questions."""
            result, steps = run_sub_agent("Banking", BANKING_SYSTEM, [], query, trace_a)
            _delegations_a["Banking"] = {"query": query, "result": result}
            return result

        def fraud_specialist_a(query: str) -> str:
            """Handle fraud reporting, security alerts and APP fraud questions."""
            result, steps = run_sub_agent("Fraud", FRAUD_SYSTEM, [], query, trace_a)
            _delegations_a["Fraud"] = {"query": query, "result": result}
            return result

        def international_specialist_a(query: str) -> str:
            """Handle international transfers, SWIFT, fees and foreign currency questions."""
            result, steps = run_sub_agent("International", INTL_SYSTEM,
                                           [get_country_info], query, trace_a)
            _delegations_a["International"] = {"query": query, "result": result}
            return result

        def complaints_specialist_a(query: str) -> str:
            """Handle complaints, escalation to Financial Ombudsman and compensation questions."""
            result, steps = run_sub_agent("Complaints", COMPLAINTS_SYSTEM, [], query, trace_a)
            _delegations_a["Complaints"] = {"query": query, "result": result}
            return result

        root_cfg = types.GenerateContentConfig(
            tools=[banking_specialist_a, fraud_specialist_a,
                   international_specialist_a, complaints_specialist_a],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            system_instruction=ROOT_SYSTEM,
        )
        root_convo = client.chats.create(model=MODEL, config=root_cfg)

        with st.spinner("Root agent deciding routing..."):
            root_resp = _call(root_convo.send_message, query_a)

        MAX_ROOT = 5
        for _ in range(MAX_ROOT):
            if not root_resp.function_calls:
                break
            fc = root_resp.function_calls[0]
            spec_query = dict(fc.args).get("query", query_a)
            trace_a.append({
                "event":      "root_delegation",
                "specialist": fc.name.replace("_specialist_a", "").replace("_", " ").title(),
                "query":      spec_query,
            })
            with st.spinner(f"Delegating to {fc.name.replace('_specialist_a','').replace('_',' ').title()} specialist..."):
                spec_result = {
                    "banking_specialist_a":       banking_specialist_a,
                    "fraud_specialist_a":          fraud_specialist_a,
                    "international_specialist_a":  international_specialist_a,
                    "complaints_specialist_a":     complaints_specialist_a,
                }[fc.name](spec_query)

            root_resp = _call(
                root_convo.send_message,
                types.Part.from_function_response(name=fc.name, response={"result": spec_result}),
            )

        trace_a.append({"event": "root_synthesis"})
        trace_a.append({"event": "final", "answer": root_resp.text})

        # ── Render ────────────────────────────────────────────────────────
        specialists_used = list(_delegations_a.keys())
        st.info(
            f"🤖 Root delegated to: **{', '.join(specialists_used)}** | "
            f"{len([e for e in trace_a if e['event']=='sub_tool'])} tool call(s)"
        )

        with st.container(border=True):
            st.markdown("### ? Final Answer")
            st.success(root_resp.text)

        render_trace(trace_a)

        with st.expander("🔍 What just happened -- Multi-Agent breakdown"):
            st.markdown(f"""
| Component | What ran | Detail |
|---|---|---|
| **Root Agent** | Routing decision | Chose: {', '.join(specialists_used)} |
| **Sub-agent(s)** | Specialist reasoning | {len(specialists_used)} sub-agent(s) invoked |
| **Tool calls** | Sub-agent tools | {len([e for e in trace_a if e['event']=='sub_tool'])} call(s) across all sub-agents |
| **Root synthesis** | Final composition | Combined all specialist results |

**Key observation:** The root never answered directly from training data.
It always delegated to a specialist and synthesized from specialist results.
This is the pattern that enables **specialisation at scale**.
""")


# ════════════════════════════════════════════════════════════════════════════
# TAB B -- Parallel Delegation
# ════════════════════════════════════════════════════════════════════════════

with tab_b:
    st.subheader("Tab B -- Parallel Delegation (multiple specialists simultaneously)")
    st.markdown("""
    For complex queries that span multiple domains, the root fans out to **all relevant specialists
    in parallel** using Python threads. Results are collected and synthesized together.

    This is analogous to Phase 2c (Parallelization) -- but the "workers" are now full agents.
    """)

    TASKS_B = {
        "Fraud + international (2 specialists)":
            "My card has been used fraudulently in a foreign country. I need to: "
            "(1) report the fraud immediately, and (2) understand if there are fees for international "
            "transactions I approved before this happened.",
        "Savings + mortgage (2 specialists)":
            "I want to both save for a house deposit AND understand what mortgage I could get. "
            "I earn GBP 55,000 and have GBP 20,000 saved. What savings account should I use "
            "and what NexaBank mortgage am I likely to qualify for?",
        "Complaint + banking (2 specialists)":
            "NexaBank charged me incorrect overdraft fees for 3 months. I want to complain about this "
            "AND understand what my overdraft limit and charges should actually be.",
    }

    if "sel_ma_b" not in st.session_state:
        st.session_state.sel_ma_b = list(TASKS_B.keys())[0]

    col1, col2 = st.columns([2, 1])
    with col2:
        for label in TASKS_B:
            if st.button(label, key=f"mab_{label}"):
                st.session_state.sel_ma_b = label
                st.rerun()
    with col1:
        query_b = st.text_area("Complex query:", value=TASKS_B[st.session_state.sel_ma_b], height=90)

    st.markdown("**Select which specialists to call in parallel:**")
    cb1, cb2, cb3, cb4 = st.columns(4)
    use_banking = cb1.checkbox("Banking", value=True, key="par_banking")
    use_fraud   = cb2.checkbox("Fraud",   value=True, key="par_fraud")
    use_intl    = cb3.checkbox("International", value=False, key="par_intl")
    use_comps   = cb4.checkbox("Complaints",    value=False, key="par_comps")

    if st.button("▶  Run Parallel Multi-Agent", type="primary", key="run_ma_b"):
        selected = []
        if use_banking: selected.append(("Banking",       BANKING_SYSTEM,    []))
        if use_fraud:   selected.append(("Fraud",         FRAUD_SYSTEM,      []))
        if use_intl:    selected.append(("International", INTL_SYSTEM,       [get_country_info]))
        if use_comps:   selected.append(("Complaints",    COMPLAINTS_SYSTEM, []))

        if not selected:
            st.warning("Select at least one specialist.")
        else:
            trace_b = []
            st.markdown(f"**Running {len(selected)} specialists in parallel...**")
            prog = st.progress(0)

            results_b = {}

            def run_one(name, system, tools):
                result, steps = run_sub_agent(name, system, tools, query_b, trace_b)
                return name, result, steps

            with ThreadPoolExecutor(max_workers=len(selected)) as executor:
                futures = {executor.submit(run_one, n, s, t): n for n, s, t in selected}
                done_count = 0
                for future in as_completed(futures):
                    name, result, steps = future.result()
                    results_b[name] = {"result": result, "steps": steps}
                    done_count += 1
                    prog.progress(done_count / len(selected), text=f"{name} complete")

            prog.empty()

            # Show parallel results
            st.markdown("### Specialist Results (ran in parallel)")
            cols = st.columns(len(selected))
            col_map = {n: c for (n, _, _), c in zip(selected, cols)}
            for name, data in results_b.items():
                with col_map[name]:
                    st.markdown(f"**👤 {name} Specialist**")
                    st.info(data["result"])
                    st.caption(f"Tool calls: {data['steps']}")

            # Synthesis
            st.markdown("---")
            with st.spinner("Root synthesizing all specialist results..."):
                all_results_text = "\n\n".join(
                    f"=== {name} Specialist ===\n{data['result']}"
                    for name, data in results_b.items()
                )
                synth_resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=f"Customer query: {query_b}\n\nSpecialist responses:\n{all_results_text}\n\nSynthesize a complete, coherent response.",
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "You are NexaBank's root agent. Synthesize specialist responses "
                            "into one clear, professional customer answer. Don't repeat -- integrate. "
                            "Keep under 200 words."
                        )
                    ),
                )

            with st.container(border=True):
                st.markdown("### ? Synthesized Final Answer")
                st.success(synth_resp.text)

            with st.expander("🔬 Execution Trace -- parallel sub-agents"):
                st.markdown(f"""
| Aspect | Detail |
|---|---|
| **Specialists called** | {', '.join(results_b.keys())} |
| **Execution mode** | Parallel (ThreadPoolExecutor) |
| **Total tool calls** | {sum(d['steps'] for d in results_b.values())} |
| **Synthesis** | Root combined all results |
""")
                for event in trace_b:
                    if event["event"] == "sub_result":
                        st.markdown(f"**{event['agent']}:** {event['result'][:150]}...")


# ════════════════════════════════════════════════════════════════════════════
# TAB C -- Comparison: Multi-Agent vs Orchestrator-Workers
# ════════════════════════════════════════════════════════════════════════════

with tab_c:
    st.subheader("Tab C -- Multi-Agent vs Phase 2d Orchestrator-Workers")
    st.markdown("**The clearest way to understand what changed:**")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Phase 2d -- Orchestrator-Workers")
            st.code('''
# Orchestrator plans the tasks
orchestrator_plan = llm(
    system="Plan sub-tasks for this complaint.",
    user=complaint
)
# Workers are stateless LLM calls
for task in orchestrator_plan["tasks"]:
    worker_result = llm(
        system=f"You are a {task['role']}.",
        user=task["instruction"]   # fixed script
    )
    # Worker cannot call tools
    # Worker cannot loop or replan
    # Worker follows the script
results.append(worker_result)
''', language="python")
            st.warning("""
**Workers are:** stateless functions
**Workers can:** generate one response
**Worker autonomy:** zero -- follows script
**Tool calls:** root only
**Failure handling:** propagates upward
**Is each worker an agent?** NO
""")

    with col2:
        with st.container(border=True):
            st.markdown("### Phase 6a -- Multi-Agent")
            st.code('''
# Root delegates to sub-agents
def international_specialist(query):
    """Handle SWIFT, fees, exchange rates."""
    # Sub-agent has own conversation
    convo = client.chats.create(
        model=MODEL,
        config=GenerateContentConfig(
            tools=[get_country_info],  # OWN tools
            system_instruction=INTL_SYS,
        )
    )
    response = convo.send_message(query)
    # Sub-agent loops with tools
    while response.function_calls:
        fc = response.function_calls[0]
        result = get_country_info(**fc.args)
        response = convo.send_message(
            Part.from_function_response(...)
        )
    return response.text
''', language="python")
            st.success("""
**Sub-agents are:** full autonomous agents
**Sub-agents can:** call tools, loop, replan
**Sub-agent autonomy:** high -- own decisions
**Tool calls:** each sub-agent independently
**Failure handling:** sub-agent retries itself
**Is each sub-agent an agent?** YES
""")

    st.markdown("---")
    st.markdown("### Head-to-head comparison")
    st.markdown("""
| Dimension | 2d Orchestrator-Workers | 6a Multi-Agent |
|---|---|---|
| **Worker type** | LLM call (function) | Full agent (conversation) |
| **Tool access** | Root only | Each sub-agent independently |
| **Reasoning loop** | Single pass | Full ReAct loop per sub-agent |
| **Worker state** | Stateless | Stateful (own conversation history) |
| **Replanning** | Not possible | Sub-agent can replan mid-task |
| **Specialisation** | Prompt-level only | System prompt + tools + memory |
| **Parallelism** | Orchestrator decides | Each sub-agent runs independently |
| **Failure isolation** | Failure propagates | Sub-agent handles own failures |
| **Scalability** | Add more prompts | Add more specialist agents |
| **Phase** | 2d | 6a |
""")

    st.info("""
**The key evolution:**
Phase 2d: orchestrator controls workers like a manager giving specific instructions.
Phase 6a: root orchestrator delegates goals (not instructions) -- sub-agents figure out how.

Phase 2d worker: "Draft a response saying we're sorry about the 3-day delay."
Phase 6a sub-agent: "Handle this complaint." (sub-agent decides HOW to handle it)
""")

st.markdown("---")

with st.expander("🐝 Advanced topology — Agent Swarms (2026 emerging pattern)"):
    st.markdown("""
Phase 6a uses a **centralised orchestrator** — one root agent coordinates all sub-agents.
Agent Swarms are a fundamentally different topology: **no central coordinator**.
Each agent acts independently on local information, and collective behaviour emerges.

**The three multi-agent topologies:**

| Topology | Coordinator | How decisions are made | When to use |
|---|---|---|---|
| **Orchestrator-Workers** (Phase 2d) | Central orchestrator | Orchestrator plans and assigns | Known, fixed workflow |
| **Root + Sub-Agents** (Phase 6a, this page) | Root agent with LLM reasoning | Root delegates based on task content | Dynamic routing, specialist agents |
| **Swarm** | None — fully decentralised | Each agent acts independently; results aggregated | Massively parallel, fault-tolerant tasks |

**How a Swarm works:**

```
Question ──► Agent 1 ──► Partial answer
         ──► Agent 2 ──► Partial answer   ──► Aggregator ──► Final answer
         ──► Agent 3 ──► Partial answer
         ──► Agent N ──► Partial answer
```

- All N agents receive the same task simultaneously
- Each agent works independently, no cross-communication
- An aggregator (could be another LLM) merges all partial answers
- Individual agent failures do not stop the swarm

**When swarms outperform orchestrators:**

| Scenario | Why swarm wins |
|---|---|
| **Document review at scale** | 100 agents each review 1 document — 100x faster than sequential |
| **Ensemble reasoning** | Multiple agents reason independently — vote on answer removes hallucination bias |
| **Fault tolerance needed** | If 10% of agents fail, 90% still complete — no single point of failure |
| **Embarrassingly parallel tasks** | No dependencies between sub-tasks — no benefit to coordination overhead |

**When orchestrators outperform swarms:**

| Scenario | Why orchestrator wins |
|---|---|
| **Sequential pipeline** | Step N depends on output of step N-1 — swarm cannot handle dependencies |
| **Dynamic routing** | Different sub-tasks need different specialists — orchestrator picks the right one |
| **State management** | Complex shared state across steps — central coordinator tracks it correctly |

**2026 scale:** Kimi K2.6 demonstrated coordinating up to 1,000 parallel agents on a single task.
The practical barrier is cost — N LLM calls per task, but cost per token keeps falling.

**Relation to this course:**
- Phase 6a Tab B (Parallel Specialists) is the simplest form of a swarm — fan-out + merge
- True swarms add: agent-level routing, fault tolerance, voting/aggregation logic
- CrewAI (Phase 10g) supports swarm-style execution with `Process.hierarchical`
""")

st.markdown("---")
st.markdown("### What's next -> Phase 6b: MCP Protocol")
st.markdown(
    "Multi-agent pattern is clear -- now standardise HOW agents connect to tools. "
    "**MCP (Anthropic, Nov 2024):** any agent discovers any tool server at runtime "
    "via a standard protocol. Swap servers without touching agent code."
)
