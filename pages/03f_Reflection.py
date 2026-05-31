"""
Phase 3b — Reflection Agent  (Andrew Ng Core Pattern #1)
One LLM generates output, then critiques its own output, then revises — until satisfied.
Three variants:
  A. Self-Reflection (banking response quality)
  B. Code Reflection with External Validation (Python + test runner)
  C. Structured Critique (formal critique doc → targeted rewrite)
"""

import streamlit as st
import os
import json
import textwrap
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 3b — Reflection Agent", page_icon="🔄", layout="wide")
st.title("🔄 Phase 3b — Reflection Agent")
st.caption("Andrew Ng Core Pattern #1 — the most universally applicable agentic improvement loop")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_3f
st.image(diagram_3f(), use_container_width=True)

# ── Comprehensive Concept ──────────────────────────────────────────────────────
with st.expander("📖 Deep dive — Reflection Pattern (Andrew Ng Core Pattern #1)", expanded=False):
    st.markdown("""
    > *"The reflection design pattern has an LLM reflect on its own output and make revisions.
    > This can dramatically improve quality across many tasks."*
    > — Andrew Ng, DeepLearning.AI Agentic AI Course

    ---

    ### What makes Reflection different from everything else

    | Pattern | Who critiques? | Loop? | Andrew Ng |
    |---|---|---|---|
    | Phase 2e — Evaluator-Optimizer | **Two separate LLMs** (Generator ≠ Evaluator) | ✅ Loop | ❌ Not this |
    | Phase 4c — LLM-as-Judge | **Separate Judge LLM** | ❌ Single eval | ❌ Not this |
    | **Phase 3b — Reflection** | **Same LLM** — generates then reflects | ✅ Loop | ✅ **This!** |

    **The core insight:** The same model that wrote the output knows more about why it made
    certain choices than any external evaluator. When prompted to "review your answer critically",
    LLMs often find real mistakes they wouldn't have caught in a single pass.

    ---

    ### Why does Reflection work?

    1. **LLMs are trained to critique** — they've seen millions of code reviews, essay feedback,
       and editorial notes. They're surprisingly good at identifying issues.

    2. **Self-consistency** — the model can check whether different parts of its output are
       consistent with each other (something hard for an external judge without full context).

    3. **Iterative refinement mirrors how humans work** — first draft is rarely the best draft.

    4. **Low cost** — the reflection call is often shorter than the generation call.
       2-3 iterations typically capture most of the quality gain.

    ---

    ### Three variants of Reflection

    #### Variant A — Pure Self-Reflection
    ```
    Generate → Critique own output → Revise → Critique → Revise → ... → Done
    ```
    No external tools. The agent judges quality against criteria it sets for itself.
    Best for: writing, explanations, customer communications.

    #### Variant B — Reflection with External Validation
    ```
    Generate code → Run tests → Reflect on failures → Fix → Run tests → ... → All pass
    ```
    External tool provides objective feedback (tests pass/fail, linter results, API calls).
    Best for: code generation, SQL, structured data extraction.
    **This is Andrew Ng's most powerful variant** — the external tool makes quality objective.

    #### Variant C — Structured Critique
    ```
    Generate draft → Produce formal critique document → Revise addressing each critique point
    ```
    Instead of free-form reflection, the agent first writes a bullet-point critique,
    then treats each point as a specific revision task.
    Best for: long documents, research reports, complex plans.

    ---

    ### When to use Reflection (and when not to)

    **Use Reflection when:**
    - Output quality matters more than latency (each reflection = extra API call)
    - The task has clear quality criteria the model can self-evaluate
    - First drafts are consistently missing something (common in complex tasks)
    - External validation is available (best case — makes quality objective)

    **Don't use Reflection when:**
    - Latency is critical (each iteration adds time)
    - The task is simple and first drafts are almost always correct
    - You have a good LLM-as-Judge (Phase 4c) already in place — less need for self-reflection

    ---

    ### Reflection vs Human reflection — the analogy

    When a developer writes code, they mentally trace through it before submitting.
    When a writer finishes a draft, they re-read it looking for gaps.
    Reflection gives LLMs the same "second pass" — and research shows 2-3 iterations
    often match or exceed what a single-pass prompted output achieves with a much
    larger / more expensive model.

    Andrew Ng cites this as one of the most practical improvements available
    at minimal engineering cost.
    """)

with st.expander("📐 Core Code Pattern — Reflection Loop"):
    st.code('''
# ══ VARIANT A: Pure Self-Reflection ════════════════════════════════════════

def generate(task: str) -> str:
    return llm(system="You are an expert. Complete this task.", user=task)

def reflect(task: str, response: str) -> dict:
    """SAME LLM — different prompt — critiques its own output."""
    return llm(
        system="You are a critical reviewer. Find specific issues in this response.",
        user=f"""Task: {task}
Response to review: {response}

Identify: (1) factual errors (2) missing information (3) unclear sections (4) tone issues
Return JSON: {{"satisfied": true/false, "issues": [...], "feedback": "..."}}"""
    )

def revise(task: str, response: str, critique: str) -> str:
    return llm(
        system="You are an expert revising your work based on feedback.",
        user=f"Task: {task}\\nCurrent response: {response}\\nFeedback: {critique}\\nImproved version:"
    )

# The reflection loop
response = generate(task)
for iteration in range(max_iterations):         # agent controls exit
    critique = reflect(task, response)           # same LLM, new perspective
    if critique["satisfied"]:                    # agent decides when done
        break
    response = revise(task, response, critique["feedback"])

# ══ VARIANT B: Reflection with External Validation ═════════════════════════

code = generate_code(task)
for iteration in range(max_iterations):
    test_result = run_tests(code)               # OBJECTIVE external feedback
    if test_result["all_passed"]:               # tests don't lie
        break
    reflection = reflect_on_errors(             # LLM interprets the errors
        code=code,
        errors=test_result["failures"]
    )
    code = fix_code(code, reflection)

# ══ VARIANT C: Structured Critique ════════════════════════════════════════

draft = generate(task)
critique_doc = generate_structured_critique(draft)   # formal bullet-point critique
final = revise_with_critique(draft, critique_doc)     # targeted rewrite per point
''', language="python")
    st.markdown("""
**Why the same LLM critiques better than you might expect:**
The generation call builds up context about why certain choices were made.
The reflection call — using the same model — draws on that context to identify
what's missing or inconsistent. An external judge has to infer this.

**The "satisfied" exit condition:**
The agent decides when it's done — not your code. This is what makes it an AGENT
rather than a fixed N-iteration loop. The model may stop after 1 iteration or 5.

**Connecting to Phase 4c (LLM-as-Judge):**
You can combine both: use Reflection for self-improvement, then LLM-as-Judge as a
final quality gate before delivery. Andrew Ng recommends this for production systems.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def llm_call(system: str, user: str, json_mode: bool = False) -> str:
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if json_mode else None,
    )
    response = _call(
        client.models.generate_content,
        model=MODEL,
        contents=user,
        config=config,
    )
    return response.text.strip()

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_a, tab_b, tab_c = st.tabs([
    "🔄 Variant A — Self-Reflection",
    "🔧 Variant B — Code + External Validation",
    "📝 Variant C — Structured Critique",
])


# ════════════════════════════════════════════════════════════════════════
# VARIANT A — Self-Reflection on banking response quality
# ════════════════════════════════════════════════════════════════════════

with tab_a:
    st.subheader("Variant A — Pure Self-Reflection")
    st.markdown("""
    Agent generates a banking response, then critiques it, then revises.
    Same LLM plays both Generator and Critic — no external tools or separate evaluators.
    Agent decides when it's satisfied.
    """)

    SCENARIOS_A = {
        "Complex refund question":
            "I bought an annual subscription 35 days ago for £199. I've barely used it and "
            "I've also had several technical issues that weren't resolved. Can I get a refund? "
            "What are my options and what's the process?",
        "Overdraft inquiry":
            "I keep getting close to my overdraft limit. Can you explain exactly how the "
            "interest is calculated, what happens if I go over, and how I can increase my limit?",
        "Investment advice request":
            "I have £50,000 to invest and I'm not sure whether to put it in a cash ISA, "
            "a stocks and shares ISA, or keep it in my savings account. What do you recommend?",
        "Complaint about charges":
            "I was charged £5 for an unarranged overdraft last month even though I was only "
            "£3 over my limit for one day. This seems unfair. Can you explain the charges and "
            "can I get a refund? I've been a customer for 10 years.",
    }

    if "sel_3f_a" not in st.session_state:
        st.session_state.sel_3f_a = SCENARIOS_A["Complex refund question"]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Scenarios:**")
        for label, text in SCENARIOS_A.items():
            if st.button(label, key=f"sc3fa_{label}"):
                st.session_state.sel_3f_a = text
                st.rerun()
        st.markdown("---")
        max_iter_a = st.slider("Max reflection iterations:", 1, 5, 3, key="iter_a")
    with col1:
        task_a = st.text_area("Customer question:",
                              value=st.session_state.sel_3f_a, height=100)

    if st.button("▶  Run Self-Reflection", type="primary", key="run_3f_a"):
        iterations_a = []

        # ── Initial generation ────────────────────────────────────────────────
        _gen_sys = (
            "You are NexaBank's customer service agent. "
            "Answer customer questions professionally. "
            "Be specific about policies, rates, and timelines. "
            "Keep responses under 120 words."
        )
        _gen_user_0 = f"Customer question: {task_a}"
        with st.spinner("Generating initial response…"):
            response_a = llm_call(system=_gen_sys, user=_gen_user_0)
        iterations_a.append({
            "type": "draft", "content": response_a, "iteration": 0,
            "system": _gen_sys, "user": _gen_user_0,
        })

        # ── Reflection loop ───────────────────────────────────────────────────
        _crit_sys = (
            "You are a senior quality reviewer for a banking AI. "
            "Critically evaluate responses for: accuracy, completeness, "
            "tone, actionability, and policy compliance. Be specific."
        )
        _rev_sys = (
            "You are NexaBank's customer service agent revising your response. "
            "Address every piece of feedback specifically. "
            "Keep the revised response under 150 words."
        )

        for i in range(max_iter_a):
            _crit_user = f"""Task: {task_a}

Current response:
\"\"\"{response_a}\"\"\"

Review this response critically. Return JSON only:
{{
  "satisfied": true/false,
  "quality_score": 1-10,
  "issues": ["specific issue 1", "specific issue 2"],
  "missing": ["what is not addressed"],
  "strengths": ["what is good"],
  "feedback": "one paragraph of specific improvement instructions"
}}"""
            with st.spinner(f"Reflection iteration {i+1}/{max_iter_a} — critiquing…"):
                critique_raw = llm_call(system=_crit_sys, user=_crit_user, json_mode=True)
            try:
                critique_a = json.loads(critique_raw)
            except Exception:
                critique_a = {"satisfied": True, "quality_score": 8,
                              "issues": [], "missing": [], "strengths": [],
                              "feedback": ""}

            iterations_a.append({
                "type":     "critique",
                "content":  critique_a,
                "raw_json": critique_raw,
                "system":   _crit_sys,
                "user":     _crit_user,
                "iteration": i + 1,
            })

            if critique_a.get("satisfied"):
                break

            # ── Revise ────────────────────────────────────────────────────────
            _rev_user = f"""Original question: {task_a}

Your previous response:
\"\"\"{response_a}\"\"\"

Reviewer feedback:
{critique_a.get('feedback', '')}

Specific issues to fix:
{chr(10).join(f"- {issue}" for issue in critique_a.get('issues', []))}

Missing information to add:
{chr(10).join(f"- {m}" for m in critique_a.get('missing', []))}

Write an improved response:"""
            with st.spinner(f"Reflection iteration {i+1} — revising…"):
                response_a = llm_call(system=_rev_sys, user=_rev_user)
            iterations_a.append({
                "type":      "revision",
                "content":   response_a,
                "system":    _rev_sys,
                "user":      _rev_user,
                "iteration": i + 1,
            })

        # ── Display all iterations ─────────────────────────────────────────────
        st.markdown("### Reflection Trace")
        st.markdown("---")

        draft_num = 0
        for item in iterations_a:
            if item["type"] == "draft":
                st.markdown("**✍️ Initial Draft (before reflection):**")
                st.warning(item["content"])

            elif item["type"] == "critique":
                c = item["content"]
                score = c.get("quality_score", "?")
                satisfied = c.get("satisfied", False)
                icon = "✅" if satisfied else "🔍"
                st.markdown(
                    f"**{icon} Reflection {item['iteration']} — "
                    f"Agent self-critique  (score: {score}/10, "
                    f"satisfied: {satisfied}):**"
                )
                col_l, col_r = st.columns(2)
                with col_l:
                    if c.get("issues"):
                        st.markdown("Issues found:")
                        for issue in c["issues"]:
                            st.markdown(f"  ⚠️ {issue}")
                    if c.get("missing"):
                        st.markdown("Missing:")
                        for m in c["missing"]:
                            st.markdown(f"  ➕ {m}")
                with col_r:
                    if c.get("strengths"):
                        st.markdown("Strengths:")
                        for s in c["strengths"]:
                            st.markdown(f"  ✓ {s}")
                if c.get("feedback"):
                    st.caption(f"Improvement instructions: _{c['feedback'][:200]}_")

            elif item["type"] == "revision":
                draft_num += 1
                st.markdown(f"**✍️ Revised Draft {draft_num}:**")
                st.info(item["content"])

        # ── Final answer ───────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### ✅ Final Reflected Response")
        final_a = next(
            (it["content"] for it in reversed(iterations_a) if it["type"] in ("draft", "revision")),
            ""
        )
        st.success(final_a)

        # ── Stats ──────────────────────────────────────────────────────────────
        n_reflections = sum(1 for it in iterations_a if it["type"] == "critique")
        n_revisions   = sum(1 for it in iterations_a if it["type"] == "revision")
        st.caption(
            f"Reflection iterations: {n_reflections} · "
            f"Revisions made: {n_revisions} · "
            f"Agent stopped: {'satisfied ✓' if iterations_a[-1].get('content', {}).get('satisfied') else 'max iterations'}"
        )

        # ── Execution Trace ────────────────────────────────────────────────────
        with st.expander("🔬 Execution Trace — exact prompts, raw JSON, and loop decisions"):
            st.caption(
                "Every prompt sent to the LLM and every raw response. "
                "Same model, two different system prompts — that is the entire mechanism of Reflection."
            )
            for item in iterations_a:
                itype = item["type"]
                it_num = item["iteration"]

                if itype == "draft":
                    st.markdown(f"#### Iteration 0 — Initial Generation")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**System prompt (Generator role):**")
                        st.code(item.get("system", ""), language="text")
                    with col2:
                        st.markdown("**User message:**")
                        st.code(item.get("user", ""), language="text")
                    st.markdown("**Response:**")
                    st.info(item["content"])

                elif itype == "critique":
                    satisfied = item["content"].get("satisfied", False)
                    score     = item["content"].get("quality_score", "?")
                    st.markdown(
                        f"#### Iteration {it_num} — Critique  "
                        f"(score: {score}/10, satisfied: {satisfied})"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**System prompt (Critic role — same LLM, different persona):**")
                        st.code(item.get("system", ""), language="text")
                    with col2:
                        st.markdown("**User message (includes current response for self-review):**")
                        st.code(item.get("user", "")[:800] + ("..." if len(item.get("user","")) > 800 else ""), language="text")
                    st.markdown("**Raw JSON output from LLM:**")
                    st.code(item.get("raw_json", json.dumps(item["content"], indent=2)), language="json")
                    decision = "STOP — satisfied" if satisfied else "CONTINUE — not satisfied, revise"
                    st.markdown(f"**Loop decision:** `satisfied={satisfied}` → **{decision}**")

                elif itype == "revision":
                    st.markdown(f"#### Iteration {it_num} — Revision")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**System prompt (Generator role — same as initial):**")
                        st.code(item.get("system", ""), language="text")
                    with col2:
                        st.markdown("**User message (includes previous response + critique feedback):**")
                        st.code(item.get("user", "")[:800] + ("..." if len(item.get("user","")) > 800 else ""), language="text")
                    st.markdown("**Revised response:**")
                    st.success(item["content"])

                st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
# VARIANT B — Code Reflection with External Validation
# ════════════════════════════════════════════════════════════════════════

with tab_b:
    st.subheader("Variant B — Code Reflection with External Validation")
    st.markdown("""
    Agent writes a Python function. We run it against test cases.
    Agent reflects on failures, fixes the code, and re-runs — until all tests pass.

    **Why this is Andrew Ng's most powerful variant:**
    Tests are objective — they either pass or fail. No subjective quality judgement needed.
    The external validator gives the agent concrete, unambiguous feedback.
    """)

    st.info("""
**Common question: isn't Variant B the same as LLM-as-Judge (4c)?**
Both involve external evaluation of the output — but they differ on every axis that matters:
""")
    st.markdown("""
| Dimension | Reflection Variant B | LLM-as-Judge (4c) |
|---|---|---|
| **Who evaluates?** | Deterministic tool — Python `exec()` + test runner; pass/fail is objective | Another LLM — probabilistic, can itself hallucinate scores |
| **Does it fix the output?** | ✅ YES — agent reflects on failures and rewrites until tests pass | ❌ NO — routes the original response as-is (deliver / HITL / fallback) |
| **Is there a loop?** | ✅ YES — iterate until all tests pass or max iterations hit | ❌ NO — single evaluation, one verdict, done |
| **Who does the work?** | The agent itself — self-correction after reading test failures | Your pipeline code — external routing decision, agent untouched |
| **End result** | A working, validated piece of code | A routing verdict about the original response |

**The analogy that makes it clear:**
- **Variant B** = developer writes code → runs unit tests → reads failures → fixes → runs again → repeats until green.
  The test runner is the external validator, but the *developer* (agent) does all the fixing.
- **LLM-as-Judge** = code reviewer reads finished code and marks PASS / FAIL / NEEDS REVISION — but hands it back without rewriting anything.

**Core distinction in one sentence:** Variant B uses an external tool to *anchor* the reflection loop — the agent still self-corrects.
LLM-as-Judge uses an external LLM to *terminate* evaluation — nothing gets fixed automatically.
""")

    CODING_TASKS = {
        "Compound interest calculator":
            "Write a Python function `compound_interest(principal, annual_rate, years, n)` "
            "that calculates the final amount using compound interest formula: "
            "A = P * (1 + r/n)^(n*t). "
            "principal=float, annual_rate=float (e.g. 0.05 for 5%), years=int, n=int (compounding per year).",

        "Loan monthly payment":
            "Write a Python function `monthly_payment(principal, annual_rate, months)` "
            "that calculates the fixed monthly payment for a loan using the standard formula: "
            "M = P * [r(1+r)^n] / [(1+r)^n - 1] where r = annual_rate/12.",

        "Age from date of birth":
            "Write a Python function `calculate_age(dob_str)` that takes a date string "
            "in 'YYYY-MM-DD' format and returns the person's age in years as an integer. "
            "Use the datetime module.",

        "Palindrome check":
            "Write a Python function `is_palindrome(s)` that returns True if the string s "
            "is a palindrome (same forwards and backwards, ignoring spaces and case), "
            "False otherwise.",
    }

    TEST_CASES = {
        "Compound interest calculator": [
            ("compound_interest(1000, 0.05, 1, 1)", 1050.0, 0.01),
            ("compound_interest(1000, 0.05, 1, 12)", 1051.16, 0.05),
            ("compound_interest(5000, 0.03, 10, 4)", 6734.0, 10.0),
        ],
        "Loan monthly payment": [
            ("monthly_payment(100000, 0.05, 360)", 536.82, 1.0),
            ("monthly_payment(200000, 0.04, 240)", 1211.96, 1.0),
        ],
        "Age from date of birth": [
            ("is_valid_dob", None, None),  # special — just check it runs
        ],
        "Palindrome check": [
            ("is_palindrome('racecar')", True, None),
            ("is_palindrome('hello')", False, None),
            ("is_palindrome('A man a plan a canal Panama')", True, None),
        ],
    }

    if "sel_3f_b" not in st.session_state:
        st.session_state.sel_3f_b = "Compound interest calculator"

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Coding tasks:**")
        for label in CODING_TASKS:
            if st.button(label, key=f"sc3fb_{label}"):
                st.session_state.sel_3f_b = label
                st.rerun()
        max_iter_b = st.slider("Max fix iterations:", 1, 5, 3, key="iter_b")
    with col1:
        selected_task_b = st.session_state.sel_3f_b
        st.markdown(f"**Task:** {CODING_TASKS[selected_task_b]}")

    def run_code_tests(code: str, task_name: str) -> dict:
        """Execute generated code and run test cases. Safe exec in try/except."""
        namespace = {}
        results = []
        compile_error = None

        try:
            exec(compile(code, "<string>", "exec"), namespace)  # noqa: S102
        except Exception as e:
            compile_error = str(e)
            return {
                "compile_error": compile_error,
                "all_passed": False,
                "results": [],
                "summary": f"Compilation/runtime error: {compile_error}",
            }

        for test_expr, expected, tolerance in TEST_CASES.get(task_name, []):
            if expected is None:
                results.append({"test": test_expr, "status": "skip", "note": "manual check"})
                continue
            try:
                actual = eval(test_expr, namespace)  # noqa: S307
                if tolerance is not None:
                    passed = abs(float(actual) - float(expected)) <= tolerance
                else:
                    passed = actual == expected
                results.append({
                    "test": test_expr,
                    "expected": expected,
                    "actual": actual,
                    "passed": passed,
                    "status": "pass" if passed else "fail",
                })
            except Exception as e:
                results.append({
                    "test": test_expr,
                    "status": "error",
                    "error": str(e),
                    "passed": False,
                })

        all_passed = all(r.get("passed", False) or r.get("status") == "skip"
                         for r in results)
        failures = [r for r in results if not r.get("passed") and r.get("status") != "skip"]
        return {
            "compile_error": None,
            "all_passed": all_passed,
            "results": results,
            "summary": (
                f"All {len(results)} tests passed ✓"
                if all_passed
                else f"{len(failures)}/{len(results)} tests failed"
            ),
        }

    if st.button("▶  Run Code Reflection", type="primary", key="run_3f_b"):
        iterations_b = []

        # ── Initial code generation ───────────────────────────────────────────
        with st.spinner("Generating initial code…"):
            code_b = llm_call(
                system=(
                    "You are an expert Python programmer. Write clean, correct code. "
                    "Output ONLY the Python function(s) — no explanation, no markdown, no backticks."
                ),
                user=CODING_TASKS[selected_task_b],
            )
            # Strip markdown if present
            if "```" in code_b:
                lines = code_b.split("\n")
                code_b = "\n".join(l for l in lines if not l.strip().startswith("```"))

        iterations_b.append({"type": "code", "content": code_b, "iteration": 0})

        # ── Test-reflect-fix loop ─────────────────────────────────────────────
        for i in range(max_iter_b):
            test_result = run_code_tests(code_b, selected_task_b)
            iterations_b.append({
                "type": "test_result",
                "content": test_result,
                "iteration": i + 1,
            })

            if test_result["all_passed"]:
                break

            # ── Reflect on failures ───────────────────────────────────────────
            failure_detail = "\n".join(
                f"- {r['test']}: expected {r.get('expected','?')}, "
                f"got {r.get('actual', r.get('error','?'))}"
                for r in test_result["results"]
                if not r.get("passed") and r.get("status") != "skip"
            )
            compile_note = f"\nCompile error: {test_result['compile_error']}" \
                           if test_result["compile_error"] else ""

            with st.spinner(f"Iteration {i+1} — reflecting on test failures…"):
                fixed_code = llm_call(
                    system=(
                        "You are an expert Python programmer debugging your own code. "
                        "Output ONLY the corrected Python function(s) — no explanation, no markdown."
                    ),
                    user=f"""Task: {CODING_TASKS[selected_task_b]}

Your current code:
{code_b}

Test failures:{compile_note}
{failure_detail}

Reflect on what is wrong and write a corrected version:""",
                )
                if "```" in fixed_code:
                    lines = fixed_code.split("\n")
                    fixed_code = "\n".join(l for l in lines if not l.strip().startswith("```"))

            code_b = fixed_code
            iterations_b.append({
                "type": "code",
                "content": code_b,
                "iteration": i + 1,
            })

        # ── Display ────────────────────────────────────────────────────────────
        st.markdown("### Reflection Trace — Code + Tests")
        st.markdown("---")

        for item in iterations_b:
            if item["type"] == "code":
                label = "Initial Code" if item["iteration"] == 0 else f"Fixed Code (iteration {item['iteration']})"
                st.markdown(f"**✍️ {label}:**")
                st.code(item["content"], language="python")

            elif item["type"] == "test_result":
                tr = item["content"]
                if tr["all_passed"]:
                    st.success(f"✅ Tests: **{tr['summary']}** — reflection loop exits")
                else:
                    st.error(f"❌ Tests: **{tr['summary']}** — agent reflects and fixes")
                    for r in tr["results"]:
                        status = r.get("status", "?")
                        if status == "pass":
                            st.caption(f"  ✓ {r['test']} → {r.get('actual','')}")
                        elif status in ("fail", "error"):
                            st.caption(
                                f"  ✗ {r['test']} → expected {r.get('expected','?')}, "
                                f"got {r.get('actual', r.get('error','?'))}"
                            )

        # ── Final result ───────────────────────────────────────────────────────
        st.markdown("---")
        final_tr = next(
            (it["content"] for it in reversed(iterations_b) if it["type"] == "test_result"), {}
        )
        if final_tr.get("all_passed"):
            st.success(f"### ✅ All tests pass — validated output")
        else:
            st.warning(f"### ⚠️ Max iterations reached — {final_tr.get('summary', '')}")

        n_fixes = sum(1 for it in iterations_b if it["type"] == "code") - 1
        st.caption(f"Code generations: {n_fixes + 1} · Fix iterations: {n_fixes}")


# ════════════════════════════════════════════════════════════════════════
# VARIANT C — Structured Critique
# ════════════════════════════════════════════════════════════════════════

with tab_c:
    st.subheader("Variant C — Structured Critique")
    st.markdown("""
    Instead of free-form self-reflection, the agent produces a **formal critique document**
    with numbered issues, then rewrites the response addressing each point specifically.

    **Why structured critique is more reliable:**
    Free-form reflection can be vague ("make it better"). A structured critique forces
    the agent to identify specific, addressable issues before revising — more like how
    a professional editor works.
    """)

    DOC_TASKS = {
        "Customer apology letter":
            "Write a professional apology letter to a customer who waited 6 weeks for a refund "
            "of £420 and had to call 4 times with no resolution. The refund has now been processed.",

        "Product feature announcement":
            "Write an email to NexaBank customers announcing a new feature: "
            "real-time spending notifications with category breakdown (food, transport, shopping, etc.). "
            "The feature launches in 2 weeks and is free for all account holders.",

        "Risk disclosure statement":
            "Write a risk disclosure for NexaBank's new Stocks & Shares ISA product. "
            "Investments can go up or down. Maximum annual investment £20,000. "
            "Platform fee 0.45% per year. No guaranteed returns.",

        "Fraud alert message":
            "Write a fraud alert message to send to a customer whose card was used in an "
            "unusual transaction of £850 at an electronics store in a different city. "
            "The card has been frozen. Ask them to confirm if the transaction was theirs.",
    }

    if "sel_3f_c" not in st.session_state:
        st.session_state.sel_3f_c = "Customer apology letter"

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Document tasks:**")
        for label in DOC_TASKS:
            if st.button(label, key=f"sc3fc_{label}"):
                st.session_state.sel_3f_c = label
                st.rerun()
    with col1:
        selected_doc = st.session_state.sel_3f_c
        st.markdown(f"**Task:** {DOC_TASKS[selected_doc]}")

    if st.button("▶  Run Structured Critique", type="primary", key="run_3f_c"):

        _c1_sys = (
            "You are a professional banking communications writer. "
            "Write clear, empathetic, regulatory-compliant communications. "
            "Keep responses under 200 words."
        )
        _c1_user = DOC_TASKS[selected_doc]

        # ── Step 1: Generate initial draft ────────────────────────────────────
        with st.spinner("Generating initial draft…"):
            draft_c = llm_call(system=_c1_sys, user=_c1_user)

        with st.container(border=True):
            st.markdown("#### ✍️ Step 1 — Initial Draft")
            st.warning(draft_c)

        _c2_sys  = (
            "You are a senior editor for a UK bank's communications team. "
            "Your critique must be specific, actionable, and numbered. "
            "Focus on: clarity, empathy, regulatory compliance, completeness, tone."
        )
        _c2_user = f"""Task: {DOC_TASKS[selected_doc]}

Draft to critique:
\"\"\"{draft_c}\"\"\"

Write a structured critique with numbered points. For each point state:
- What the specific problem is
- Why it matters
- What the fix should be

Also note strengths. End with an overall quality verdict (1-10)."""

        # ── Step 2: Generate structured critique ──────────────────────────────
        with st.spinner("Generating structured critique document…"):
            critique_doc = llm_call(system=_c2_sys, user=_c2_user)

        with st.container(border=True):
            st.markdown("#### 🔍 Step 2 — Structured Critique Document")
            st.info(critique_doc)

        _c3_sys  = (
            "You are a professional banking communications writer revising your draft. "
            "Address EVERY numbered point in the critique. "
            "Keep the revision under 220 words."
        )
        _c3_user = f"""Task: {DOC_TASKS[selected_doc]}

Original draft:
\"\"\"{draft_c}\"\"\"

Critique to address:
{critique_doc}

Write a revised version that addresses every critique point:"""

        # ── Step 3: Targeted rewrite ───────────────────────────────────────────
        with st.spinner("Rewriting based on critique…"):
            final_c = llm_call(system=_c3_sys, user=_c3_user)

        with st.container(border=True):
            st.markdown("#### ✅ Step 3 — Revised Draft (post structured critique)")
            st.success(final_c)

        # ── Side by side comparison ────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Before vs After — Side by Side")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**Before (initial draft):**")
            st.warning(draft_c)
        with cb:
            st.markdown("**After (structured critique applied):**")
            st.success(final_c)

        with st.expander("🔍 Why structured critique outperforms free-form reflection"):
            st.markdown("""
**Free-form reflection risk:** The agent might produce vague improvement advice like
"make it more empathetic" without specifics on how.

**Structured critique forces specificity:** By requiring numbered points with:
- What the problem is
- Why it matters
- How to fix it

...the revision step becomes a targeted editing task, not a guessing game.

**In practice:** Teams at Anthropic and OpenAI use structured critique prompts
as part of multi-agent review pipelines for high-stakes content (legal, medical, financial).
The structure ensures every identified issue gets addressed, not just the most obvious ones.
""")

        with st.expander("🔬 Execution Trace — all 3 prompts and responses"):
            st.caption("The three distinct LLM calls that power Variant C, each with a different role.")
            steps = [
                ("① Generator (Writer)", _c1_sys, _c1_user, draft_c, "warning"),
                ("② Critic (Editor)", _c2_sys, _c2_user, critique_doc, "info"),
                ("③ Reviser (same Writer, critique in hand)", _c3_sys, _c3_user, final_c, "success"),
            ]
            for label, sys_p, usr_p, response, color in steps:
                st.markdown(f"#### {label}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**System prompt (defines role):**")
                    st.code(sys_p, language="text")
                with col2:
                    st.markdown("**User message (the task input):**")
                    st.code(usr_p[:600] + ("..." if len(usr_p) > 600 else ""), language="text")
                st.markdown("**Response:**")
                getattr(st, color)(response)
                st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON TABLE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### Reflection vs Related Patterns — Complete Comparison")
st.markdown("""
| Feature | 2e Evaluator-Optimizer | 4c LLM-as-Judge | 3b Reflection |
|---|---|---|---|
| **How many LLMs?** | 2 (Generator + Evaluator) | 2 (Agent + Judge) | **1** (same LLM both roles) |
| **Loop?** | ✅ Until threshold | ❌ Once | ✅ Until satisfied |
| **Who exits loop?** | Your threshold (code) | N/A | **Agent decides** |
| **External validation?** | ❌ | ❌ | ✅ Variant B (tests, linters) |
| **Feedback source** | Separate evaluator LLM | Separate judge LLM | **Self** |
| **Best for** | Quality improvement workflow | Quality gate / routing | Any task needing refinement |
| **Andrew Ng core pattern?** | ❌ | ❌ | ✅ **Pattern #1** |
| **Cost** | Medium (2 LLMs × N) | Low (1 extra call) | Low-Medium (1 LLM × N) |
""")

st.markdown("---")
st.markdown("### ⚖️ LLM-as-Judge (4c) vs Reflection (3b) — Deep Comparison")
st.caption(
    "Two patterns that both improve response quality — but through entirely different mechanisms. "
    "Understanding the difference is key to choosing the right tool in production."
)

with st.expander("📖 Full pros & cons — when to use each and when to combine", expanded=True):

    st.markdown("**Core idea — LLM-as-Judge (4c):** A *separate, independent* LLM evaluates the output after it is produced.")
    st.markdown("**Core idea — Reflection (3b):** The *same LLM* generates, critiques, and revises its own output in a loop.")
    st.markdown("")

    st.markdown("#### ✅ Pros")
    st.markdown("""
| # | ⚖️ LLM-as-Judge (Phase 4c) | 🔄 Reflection (Phase 3b) |
|---|---|---|
| 1 | **Independent perspective** — judge has no memory of generation; evaluates exactly what the user sees | **Actually fixes the output** — each iteration produces an improved version, not just a verdict |
| 2 | **No echo chamber** — different prompt (optionally different model) avoids self-reinforcing bias | **Self-consistency checks** — same model spots internal contradictions missed in a single pass |
| 3 | **Explicit scoring** — structured scores (accuracy, tone, completeness) you can log, trend, and alert on | **Understands its own reasoning** — knows why it made choices; critique is more targeted than an external view |
| 4 | **Routing built-in** — PASS → deliver, REVIEW → HITL, FAIL → fallback; pipeline knows what to do next | **Flexible stopping** — agent decides when satisfied; 1 iteration for easy tasks, more for hard ones |
| 5 | **Predictable latency** — exactly one extra LLM call regardless of output quality | **External validation (Variant B)** — tests/linters give objective pass/fail; quality becomes unambiguous |
| 6 | **Works on anyone's output** — evaluates responses from any agent, human, or external system | **No extra model needed** — same LLM plays both roles; simpler infrastructure, lower base cost |
| 7 | **Calibratable** — tune thresholds and criteria per use-case without touching the agent | **Andrew Ng Pattern #1** — one of the most universally applicable agentic improvements available |
""")

    st.markdown("#### ❌ Cons")
    st.markdown("""
| # | ⚖️ LLM-as-Judge (Phase 4c) | 🔄 Reflection (Phase 3b) |
|---|---|---|
| 1 | **Does not fix the problem** — FAIL triggers a fallback; the bad response is never actually improved | **Sycophancy risk** — model may convince itself its first answer was correct and exit too quickly |
| 2 | **Judge can hallucinate** — judge is also an LLM; can score incorrectly on nuanced or domain-specific criteria | **Echo chamber** — same model, same biases; systematic factual errors will not be caught |
| 3 | **No context about WHY** — sees only input + output, not the agent's reasoning; misses subtle intent errors | **Latency multiplier** — each iteration adds a full round-trip; 3 iterations = 3× generation time |
| 4 | **Criteria must be pre-defined** — must specify what "good" means upfront; doesn't adapt to novel failure modes | **"Satisfied" can be gamed** — model may declare itself satisfied to exit the loop rather than do the work |
| 5 | **Extra cost per response** — second LLM call on every response, even when quality is already high | **No structured output by default** — critique is narrative; harder to log, trend, or alert on |
| 6 | **Threshold tuning burden** — setting PASS/REVIEW/FAIL thresholds requires calibration data | **No routing** — reflection improves but doesn't decide what happens next (HITL, fallback, etc.) |
| 7 | — | **Diminishing returns** — quality gain from iteration 3+ is often marginal; hard to know when to stop |
""")

st.markdown("---")

# ── Head-to-head decision table ─────────────────────────────────────────────────
st.markdown("#### Head-to-head — pick the right tool for the job")
st.markdown("""
| Situation | Use Judge | Use Reflection | Use Both |
|---|:---:|:---:|:---:|
| Need to route response to HITL / fallback | ✅ | ❌ | ✅ |
| Need to actually improve the response | ❌ | ✅ | ✅ |
| Evaluating output from a third-party system | ✅ | ❌ | — |
| Code generation with test cases | ❌ | ✅ (Variant B) | — |
| High-stakes content (legal, financial, medical) | ✅ | ✅ | ✅ |
| Latency is critical (< 1s response) | ✅ | ❌ | ❌ |
| Want systematic quality metrics over time | ✅ | ❌ | ✅ |
| Domain facts may be wrong (hallucination risk) | ✅ | ⚠️ risky | ✅ |
| Long-form document quality (report, letter) | ❌ | ✅ (Variant C) | ✅ |
| Production pipeline with SLA requirements | ✅ | ⚠️ with max_iter cap | ✅ |
""")

st.info("""
**The production recommendation (Andrew Ng + Anthropic):**
Use **Reflection first** to self-improve the response, then **LLM-as-Judge as the final gate** before delivery.
Reflection raises the floor; Judge ensures nothing slips through.
The REVIEW verdict from Judge feeds directly into the HITL queue (Phase 4b) for human oversight.

`Generate → Reflect (N iterations) → Judge → PASS: deliver | REVIEW: HITL | FAIL: fallback`
""")

st.markdown("---")
st.markdown("### What's next → Phase 3c : Planning Agent")
st.markdown(
    "Andrew Ng Pattern #3: agent creates an explicit written plan (numbered steps, dependencies) "
    "**before** executing — then can revise the plan mid-execution if results change. "
    "Different from ReAct (implicit reasoning) — the plan is a visible artefact."
)
