"""
Phase 3e — Core Agentic Patterns: Decision Guide
All 9 patterns side-by-side: when to use, LLM cost, real examples, risks.
"""

import json
import streamlit as st
from utils.llm import MODEL, _client, _call
from utils.diagrams import diagram_pattern_compare

st.set_page_config(
    page_title="3e — Pattern Decision Guide",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 1. Title ─────────────────────────────────────────────────────────────────
st.title("🗺️ 3e — Core Agentic Patterns: Decision Guide")
st.caption(
    "All 9 patterns from Phase 2 + Phase 3 — when to use, LLM call cost, "
    "real-world examples, and the risk of choosing the wrong one."
)

# ── 2. Diagram ───────────────────────────────────────────────────────────────
st.image(
    diagram_pattern_compare(),
    caption="Pattern Landscape — positioned by task complexity vs agent autonomy",
    use_column_width=True,
)

# ── 3. Concept ───────────────────────────────────────────────────────────────
with st.expander("📖 What is the Pattern Landscape — and why does pattern choice matter?"):
    st.markdown("""
The 9 patterns split into two families:

**Phase 2 — Workflow Patterns** (you define the flow)
The developer controls when each LLM call runs and how outputs chain.
The LLM executes a single step within a fixed structure. Lower autonomy, more predictable.

**Phase 3 — Agent Patterns** (the LLM drives the loop)
The LLM decides what to do next — call a tool, reflect, write code, or stop.
Higher autonomy, more capable on open-ended tasks, but harder to debug and more expensive.

**Why pattern choice matters:**

| Decision | Wrong pattern | Consequence |
|---|---|---|
| ReAct for a 3-step predictable pipeline | Prompt Chaining is enough | 5× more LLM calls, unpredictable path |
| Prompt Chaining for open-ended research | Can't adapt to unexpected results | Misses key information mid-run |
| Reflection for speed-critical output | Evaluator-Optimizer is lighter | Unnecessary self-loops, latency doubles |
| ReAct for number-crunching | Code Execution gives deterministic results | Hallucinated numbers |
| Planning for unpredictable data | Adaptive Planning or ReAct instead | Rigid plan fails when step 2 surprises |

**Rule of thumb:** start with the simplest pattern that works. Add complexity only when simpler patterns fail.
""")

# ── 4. Core Code Pattern ─────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — Pattern Selection Logic"):
    st.code('''
# Pattern selection decision tree — choose the simplest that works

def select_pattern(task):

    if task.steps_known and task.no_tools:
        return "Prompt Chaining"          # sequential, deterministic, cheapest

    if task.multiple_input_types:
        return "Routing"                  # classify first, specialise second

    if task.subtasks_independent:
        return "Parallelization"          # fan-out, majority vote, aggregate

    if task.needs_quality_iteration:
        return "Evaluator-Optimizer"      # generate → score → refine

    if task.complex_unknown_subtasks:
        return "Orchestrator-Workers"     # plan dynamically, delegate

    # ── Phase 3 — LLM owns the loop ──────────────────────────────────────────

    if task.needs_computation:
        return "Code Execution"           # deterministic; sandbox required

    if task.quality_is_critical:
        return "Reflection"               # critique yourself until threshold

    if task.structure_predictable and task.multi_step:
        return "Planning"                 # explicit plan before any execution

    if task.open_ended and task.live_data:
        return "ReAct"                    # most flexible, highest cost
''', language="python")
    st.markdown("""
**What makes this non-trivial:** the boundaries blur.
A task that *looks* like it needs ReAct often turns out to work fine with Prompt Chaining
once you enumerate the steps. Always ask: "can I write down the steps ahead of time?"
If yes → Planning or Chaining. If the answer changes mid-run → Adaptive Planning or ReAct.
""")

st.markdown("---")

# ── 5. Main comparison grid ──────────────────────────────────────────────────
st.markdown("### Full Comparison — All 9 Patterns")

tab_overview, tab_cost, tab_risk, tab_advisor = st.tabs([
    "📊 When to Use",
    "💰 Cost & Latency",
    "⚠️ Risks & Anti-patterns",
    "🤖 Pattern Advisor",
])

# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    st.markdown("""
| # | Pattern | Phase | Core Mechanism | Best When | Real-World Example |
|---|---|---|---|---|---|
| 1 | **Prompt Chaining** | 2a | Output of step N becomes input of step N+1 | Steps are fixed, sequential, and each depends on prior result | Blog pipeline: brief → outline → draft → SEO-optimise |
| 2 | **Routing** | 2b | Classify input, dispatch to specialised handler | Multiple distinct input types need different expertise | Support triage: billing query → billing agent, bug report → tech agent |
| 3 | **Parallelization** | 2c | Fan-out to N parallel workers, aggregate or vote | Subtasks are independent; consensus improves quality; speed matters | Security review: 3 LLMs independently scan same code, majority vote |
| 4 | **Evaluator-Optimizer** | 2e | Generate → evaluate score → refine → repeat | Output must hit a measurable quality threshold | Code gen: write → run tests → score → fix until all pass |
| 5 | **Orchestrator-Workers** | 2d | Orchestrator plans dynamically, delegates to specialists | Complex tasks with unknown subtask structure; specialist expertise needed | Research report: orchestrator delegates to web-search, analyst, writer agents |
| 6 | **ReAct** | 3a | Think → Act (tool call) → Observe → repeat | Open-ended tasks with live data; number of steps unknown upfront | Travel planner: searches flights, weather, visa rules iteratively |
| 7 | **Reflection** | 3b | Generate → critique (self or external) → refine | Output quality is critical; objective criteria can be checked | Legal draft: write → critique compliance gaps → revise → repeat |
| 8 | **Planning** | 3c | Explicit plan first → execute each step → synthesise | Multi-step tasks with predictable structure; explainability needed | Competitive analysis: plan steps (research A, research B, compare) then execute |
| 9 | **Code Execution** | 3d | Generate Python → exec in sandbox → observe → fix | Computations, data analysis, transformations requiring deterministic precision | Data pipeline: write pandas transforms → run → fix errors → run again |
""")

# ─────────────────────────────────────────────────────────────────────────────
with tab_cost:
    st.markdown("""
| # | Pattern | LLM Calls | Relative Cost | Latency Profile | Cost Driver |
|---|---|---|---|---|---|
| 1 | **Prompt Chaining** | = number of steps (usually 2–4) | 🟢 Low | Sequential — adds up | Each step is a full LLM call |
| 2 | **Routing** | 1 classifier + 1 handler = 2 | 🟢 Low | Fast (2 calls) | Classifier must be lightweight |
| 3 | **Parallelization** | N parallel + 1 aggregator | 🟡 Medium | Fast (parallel) | N scales with subtask count |
| 4 | **Evaluator-Optimizer** | 2 × iterations (gen + eval) | 🟡 Medium | Variable (loops) | Iterations multiply cost |
| 5 | **Orchestrator-Workers** | 1 orchestrator + N workers | 🟡 Medium-High | Parallel workers help | Orchestrator is a large context call |
| 6 | **ReAct** | ~2–3 per tool call × N calls | 🔴 High | Longest (sequential loops) | Unbounded — no plan means no stop |
| 7 | **Reflection** | 2 per cycle (gen + critique) | 🔴 High | Depends on cycles | Cycles multiply; diminishing returns |
| 8 | **Planning** | 1 planner + N executors + 1 synth | 🔴 High | Sequential execution | N executor calls with full context |
| 9 | **Code Execution** | Gen + debug loops | 🔴 High | Depends on errors | Sandbox execution is free; debug loops cost |
""")
    st.info(
        "💡 **Cost reduction strategies:** Cache the planner output in Planning (same plan, "
        "re-execute). Use a small model for Routing classifier. Cap iterations in "
        "Evaluator-Optimizer and Reflection. Set max_steps in ReAct."
    )

# ─────────────────────────────────────────────────────────────────────────────
with tab_risk:
    st.markdown("""
| # | Pattern | Key Risk | Failure Mode | When NOT to Use |
|---|---|---|---|---|
| 1 | **Prompt Chaining** | Error propagation | Bad step 1 corrupts all downstream steps silently | When task requires adapting to mid-run surprises |
| 2 | **Routing** | Misclassification | Query sent to wrong specialist — bad answer with false confidence | When input types overlap and ambiguity is common |
| 3 | **Parallelization** | Aggregation failure | Contradictory results with no clear majority — tiebreaker needed | When subtasks have hidden dependencies |
| 4 | **Evaluator-Optimizer** | Collusion / infinite loop | Generator + evaluator use same model — evaluator validates its own output | When threshold is not measurable or too high |
| 5 | **Orchestrator-Workers** | Over-delegation | Orchestrator creates redundant or conflicting tasks for workers | When subtasks are simple enough for Prompt Chaining |
| 6 | **ReAct** | Infinite tool loop | Agent calls same tool repeatedly without making progress | When task structure is predictable — use Planning instead |
| 7 | **Reflection** | Hallucinated critique | LLM invents flaws that don't exist or misses real ones | When speed matters or output quality is "good enough" |
| 8 | **Planning** | Rigid plan | Plan committed before data; unexpected step-2 result breaks all remaining steps | When task is exploratory and structure emerges dynamically |
| 9 | **Code Execution** | Unsafe code | Generated code with side effects, network calls, or infinite loops | Without a sandbox — never exec untrusted LLM code in production directly |
""")
    st.warning(
        "⚠️ **Cross-pattern risk:** Adding more complexity rarely fixes a problem that "
        "is really about prompt quality. Debug the prompt first, escalate to a more "
        "complex pattern only when the prompt is already optimised."
    )

# ─────────────────────────────────────────────────────────────────────────────
with tab_advisor:
    st.markdown("### Pattern Advisor — describe what you're building")
    st.markdown(
        "Describe your use case and get a pattern recommendation with reasoning, "
        "cost note, and the key risk to watch for."
    )

    ADVISOR_SYS = f"""You are a senior agentic AI architect.
A developer describes what they need to build. Recommend the best pattern from these 9:

Phase 2 — Workflow:
  Prompt Chaining  — sequential steps, each output feeds next input
  Routing          — classify input, dispatch to specialized handler
  Parallelization  — fan-out to N workers, aggregate or vote
  Evaluator-Optimizer — generate → score → refine loop
  Orchestrator-Workers — orchestrator plans + delegates to specialists

Phase 3 — Agent:
  ReAct            — Think → Tool → Observe loop (unknown number of steps)
  Reflection       — Generate → Critique → Refine (quality-focused)
  Planning         — explicit Plan upfront → Execute → Synthesize
  Code Execution   — generate Python → exec in sandbox → observe → fix

SELECTION RULES (apply in order):
1. Prefer Phase 2 over Phase 3 when task structure is known upfront
2. Use Code Execution only when deterministic computation is required
3. Planning beats ReAct when the number of steps is predictable
4. Parallelization beats Orchestrator-Workers when subtasks are independent
5. Reflection is for quality iteration, not live data retrieval
6. If multiple patterns fit, prefer the one with fewest LLM calls

Respond with ONLY this JSON (no extra text):
{{
  "pattern": "<exact pattern name>",
  "phase": "2 or 3",
  "confidence": "High | Medium | Low",
  "reason": "<2–3 sentences: why this pattern fits the use case>",
  "key_risk": "<1 sentence: main thing to watch out for>",
  "alternative": "<second-best pattern name: when to switch to it instead>"
}}"""

    examples = [
        "I need to generate a weekly market report: fetch stock prices, write a summary, then translate it to 3 languages.",
        "My agent needs to answer questions about company policy documents stored in a database.",
        "I want to automatically fix failing unit tests — read the error, write a fix, re-run, repeat.",
        "I'm building a customer service bot that handles billing, tech support, and general FAQs differently.",
    ]
    example_sel = st.selectbox("Try an example:", ["(type your own below)"] + examples)
    use_case = st.text_area(
        "Your use case:",
        value=example_sel if example_sel != "(type your own below)" else "",
        height=100,
        placeholder="e.g. I need to analyse a CSV file, compute statistics, and generate a written summary...",
    )

    adv_sys_used = adv_user_used = adv_raw = ""

    if st.button("🔍 Recommend a Pattern", type="primary"):
        if not use_case.strip():
            st.warning("Please describe your use case.")
        else:
            with st.spinner("Analysing your use case…"):
                adv_sys_used  = ADVISOR_SYS
                adv_user_used = f"Use case: {use_case}"
                try:
                    adv_raw, _ = _call(
                        _client().models,
                        adv_sys_used,
                        adv_user_used,
                        model=MODEL,
                        config={"response_mime_type": "application/json"},
                    )
                    rec = json.loads(adv_raw)
                except Exception as e:
                    st.error(f"Recommendation failed: {e}")
                    rec = None

            if rec:
                conf_color = {"High": "#d4edda", "Medium": "#fff3cd", "Low": "#f8d7da"}.get(
                    rec.get("confidence", ""), "#f0f4f8"
                )
                conf_border = {"High": "#28a745", "Medium": "#ffc107", "Low": "#dc3545"}.get(
                    rec.get("confidence", ""), "#ccc"
                )
                st.markdown(
                    f"<div style='background:{conf_color};border-left:6px solid {conf_border};"
                    f"padding:18px 24px;border-radius:6px;margin-bottom:12px'>"
                    f"<span style='font-size:1.6rem;font-weight:800;color:#1C2833'>"
                    f"✅ {rec.get('pattern')} &nbsp;"
                    f"<span style='font-size:1rem;font-weight:500;color:#555'>"
                    f"(Phase {rec.get('phase')} · {rec.get('confidence')} confidence)</span></span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Why this pattern:**")
                    st.info(rec.get("reason", ""))
                with col2:
                    st.markdown("**Key risk to watch:**")
                    st.warning(rec.get("key_risk", ""))

                st.markdown(
                    f"**If it doesn't fit:** try **{rec.get('alternative', '—')}**"
                )

        with st.expander("🔬 Execution Trace — exact prompt and raw response"):
            t1, t2 = st.tabs(["① Prompt sent to Gemini", "② Raw JSON response"])
            with t1:
                st.markdown("**System prompt:**")
                st.code(adv_sys_used or "(not run yet)", language="text")
                st.markdown("**User message:**")
                st.code(adv_user_used or "(not run yet)", language="text")
            with t2:
                st.code(adv_raw or "(not run yet)", language="json")

st.markdown("---")
st.markdown("### What's next → Phase 4 — Trust & Safety")
st.markdown(
    "Now that you can choose the right pattern, the next question is: "
    "how do you make it safe? "
    "Phase 4 covers **Guardrails** (4a), **Human-in-the-Loop** (4b), "
    "**LLM-as-Judge** (4c), and **Evaluation Frameworks** (4d)."
)
