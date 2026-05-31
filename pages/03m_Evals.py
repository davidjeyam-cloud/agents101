"""
Phase 4d -- Evaluation Framework
Systematic quality measurement: golden dataset, LLM-as-Judge at scale,
regression testing, pass rate and failure analysis.
"""

import streamlit as st
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 4d -- Evaluation Framework", page_icon="📊", layout="wide")
st.title("📊 Phase 4d -- Evaluation Framework")
st.caption("Systematic quality measurement -- golden dataset, LLM-as-Judge at scale, regression testing")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_evals
st.image(diagram_evals(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is an Evaluation Framework -- and why does every production agent need one?"):
    st.markdown("""
    > *"Evaluating AI agents is one of the most important and underrated engineering tasks.
    > Without evals, you're flying blind -- you don't know if your changes helped or hurt."*

    **The three patterns that evaluate responses -- all different:**

    | Pattern | Phase | When it runs | Who triggers it | Purpose |
    |---|---|---|---|---|
    | **Evaluator-Optimizer** | 2e | Inside the agent loop | The agent | Quality improvement during generation |
    | **LLM-as-Judge** | 4c | After each response | Your pipeline | Route one response: PASS / REVIEW / FAIL |
    | **Evaluation Framework** | 4d | In CI / on demand | Developer | Measure quality across many responses |

    **What an Evaluation Framework adds:**
    - **Scale:** evaluates 10 / 100 / 1000 questions in one run
    - **Regression testing:** detects when a change breaks something that used to work
    - **Trends:** track quality over time as the agent evolves
    - **Golden dataset:** a curated set of questions with known correct answers

    **The golden dataset:**
    A "golden dataset" is a set of question-answer pairs where you know what a correct response
    must contain. It's the contract your agent must honour.

    **Three types of evaluation:**

    | Type | How | Best for |
    |---|---|---|
    | **Exact match** | Response must contain specific strings | Policy facts, numbers, names |
    | **LLM-as-Judge** | Independent LLM scores the response | Tone, completeness, groundedness |
    | **Human eval** | Human reviews a sample | Edge cases, novel failures |

    This page implements exact-match fact checking + LLM-as-Judge scoring.
    """)

with st.expander("📐 Core Code Pattern -- Evaluation Framework"):
    st.code('''
# ── Golden dataset ────────────────────────────────────────────────────────────
GOLDEN = [
    {
        "id": "Q1",
        "question": "What is the NexaSaver interest rate?",
        "expected_facts": ["4.75%", "AER"],   # response must contain these
        "category": "Product Knowledge",
    },
    # ... more questions
]

# ── Run agent on each question ────────────────────────────────────────────────
results = []
for item in GOLDEN:
    response = run_agent(item["question"])

    # Exact-match check
    facts_found = [f for f in item["expected_facts"] if f.lower() in response.lower()]
    fact_score  = len(facts_found) / len(item["expected_facts"])

    # LLM-as-Judge score (reuses Phase 4c judge)
    judge_result = judge(item["question"], response)

    results.append({
        "id":          item["id"],
        "question":    item["question"],
        "response":    response,
        "fact_score":  fact_score,
        "judge_score": judge_result["overall"],
        "verdict":     judge_result["verdict"],
        "facts_found": facts_found,
        "facts_missed": [f for f in item["expected_facts"] if f not in facts_found],
    })

# ── Aggregate metrics ─────────────────────────────────────────────────────────
pass_rate    = sum(1 for r in results if r["verdict"] == "PASS") / len(results)
avg_score    = sum(r["judge_score"] for r in results) / len(results)
avg_facts    = sum(r["fact_score"]  for r in results) / len(results)
failures     = [r for r in results if r["verdict"] == "FAIL"]

# ── Regression: compare with previous run ────────────────────────────────────
if previous_run:
    delta_pass  = pass_rate - previous_run["pass_rate"]
    regressions = [r["id"] for r in results
                   if r["verdict"] != "PASS"
                   and previous_run["by_id"][r["id"]]["verdict"] == "PASS"]
''', language="python")
    st.markdown("""
**Why golden datasets matter:**
Every time you change the agent's system prompt, tools, or model, some questions that
previously PASSed may start FAILing. Without a golden dataset, you won't know until
a customer reports a problem.

**The eval feedback loop:**
Run evals -> identify failures -> fix agent -> run evals again -> confirm improvement.
This is the same loop as Phase 3b Reflection, but at the SYSTEM level, not the response level.

**Connecting to other phases:**
- Phase 4c LLM-as-Judge: used here at scale for each response
- Phase 7a Observability: production traces become the source of new golden dataset items
- Phase 3b Reflection: same improvement loop but automated across many questions
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# NexaBank Golden Dataset
# ══════════════════════════════════════════════════════════════════════════════

GOLDEN_DATASET = [
    {
        "id": "Q01", "category": "Savings",
        "question": "What interest rate does the NexaSaver account offer?",
        "expected_facts": ["4.75%", "AER"],
        "difficulty": "Easy",
    },
    {
        "id": "Q02", "category": "ISA",
        "question": "What is the annual ISA allowance and the NexaFlex ISA rate?",
        "expected_facts": ["20,000", "4.2%"],
        "difficulty": "Easy",
    },
    {
        "id": "Q03", "category": "Refund",
        "question": "How long does a NexaBank refund take for amounts under GBP 500?",
        "expected_facts": ["3", "5", "working days"],
        "difficulty": "Easy",
    },
    {
        "id": "Q04", "category": "Refund",
        "question": "A customer wants a refund of GBP 750. What is the process and timeline?",
        "expected_facts": ["500", "manager", "5", "10"],
        "difficulty": "Medium",
    },
    {
        "id": "Q05", "category": "Fraud",
        "question": "How should a customer report suspected fraud to NexaBank?",
        "expected_facts": ["0800", "app", "frozen"],
        "difficulty": "Easy",
    },
    {
        "id": "Q06", "category": "Overdraft",
        "question": "What is NexaBank's arranged overdraft interest rate?",
        "expected_facts": ["39.9%", "EAR"],
        "difficulty": "Easy",
    },
    {
        "id": "Q07", "category": "International",
        "question": "What are the fees for sending money to Australia from NexaBank?",
        "expected_facts": ["15", "SWIFT", "2", "5"],
        "difficulty": "Medium",
    },
    {
        "id": "Q08", "category": "Complaints",
        "question": "If NexaBank does not resolve a complaint in 8 weeks, what can the customer do?",
        "expected_facts": ["Ombudsman", "FOS", "free"],
        "difficulty": "Medium",
    },
    {
        "id": "Q09", "category": "Mortgage",
        "question": "What is the NexaBank 5-year fixed mortgage rate?",
        "expected_facts": ["4.65%", "APRC"],
        "difficulty": "Easy",
    },
    {
        "id": "Q10", "category": "AML",
        "question": "At what transaction amount does NexaBank trigger Enhanced Due Diligence?",
        "expected_facts": ["10,000"],
        "difficulty": "Hard",
    },
]

POLICY_CONTEXT = """
NexaBank key facts:
- NexaSaver: 4.75% AER variable, min balance GBP 100
- NexaFlex ISA: 4.2% AER tax-free, annual allowance GBP 20,000
- Refunds under GBP 500: auto, 3-5 working days. Over GBP 500: manager approval, 5-10 working days.
- Fraud: report via app, 0800 123 4567 (24/7), account frozen immediately
- Arranged overdraft: 39.9% EAR
- International transfers: EU/EEA GBP 5 (SEPA), US/Canada/Australia GBP 15, others GBP 25. SWIFT 2-5 days.
- Complaints: resolve in 3 days; unresolved after 8 weeks -> Financial Ombudsman Service (FOS) free of charge
- Mortgages: 2yr fix 4.89% APRC, 5yr fix 4.65% APRC, 10yr fix 4.99% APRC
- AML/EDD triggered: transactions above GBP 10,000, PEPs, high-risk countries
"""

# ── Agent and Judge ────────────────────────────────────────────────────────────

def run_agent(question: str, use_context: bool = True) -> str:
    ctx = f"\n\nPolicy reference:\n{POLICY_CONTEXT}" if use_context else ""
    resp = _call(
        client.models.generate_content,
        model=MODEL,
        contents=f"Customer question: {question}{ctx}",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are NexaBank's AI assistant. Answer customer questions accurately. "
                "Be specific -- cite rates, timelines, and policies. Keep under 80 words."
            )
        ),
    )
    return resp.text.strip()


def judge_response(question: str, response: str) -> dict:
    prompt = f"""You are an expert quality judge for a banking AI.
Rate this response on four criteria (1-10 each):
- accuracy: factually correct, no hallucinations
- groundedness: cites specific NexaBank policies/rates
- tone: professional, empathetic, appropriate
- completeness: addresses all parts of the question

Return ONLY JSON:
{{"accuracy": N, "groundedness": N, "tone": N, "completeness": N,
  "overall": N.N, "verdict": "PASS|REVIEW|FAIL",
  "feedback": "one sentence"}}

PASS if overall >= 7.0, REVIEW if >= 5.0, FAIL if < 5.0.

Question: {question}
Response: \"\"\"{response}\"\"\"
"""
    try:
        result = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(result.text)
        scores = [float(data.get(c, 5)) for c in ["accuracy", "groundedness", "tone", "completeness"]]
        data["overall"] = round(sum(scores) / len(scores), 1)
        if data["overall"] >= 7.0:
            data["verdict"] = "PASS"
        elif data["overall"] >= 5.0:
            data["verdict"] = "REVIEW"
        else:
            data["verdict"] = "FAIL"
        return data
    except Exception as e:
        return {"accuracy": 5, "groundedness": 5, "tone": 5, "completeness": 5,
                "overall": 5.0, "verdict": "REVIEW", "feedback": f"Judge error: {e}"}


def check_facts(response: str, expected_facts: list) -> tuple:
    found = [f for f in expected_facts if f.lower() in response.lower()]
    missed = [f for f in expected_facts if f.lower() not in response.lower()]
    return found, missed


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"**Golden dataset:** {len(GOLDEN_DATASET)} NexaBank Q&A pairs with known required facts")

with st.expander("📖 View golden dataset"):
    for item in GOLDEN_DATASET:
        st.markdown(
            f"**{item['id']}** `[{item['category']} | {item['difficulty']}]`  "
            f"{item['question']}  "
            f"*Required facts: {', '.join(item['expected_facts'])}*"
        )

st.markdown("---")

tab_run, tab_regression = st.tabs([
    "📊 Run Evaluation Suite",
    "🔁 Regression Testing",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: Run Eval Suite
# ════════════════════════════════════════════════════════════════════════════

with tab_run:
    st.subheader("Run the full evaluation suite")
    st.markdown("""
    Runs the NexaBank agent against all 10 golden dataset questions.
    Each response is checked for required facts AND scored by LLM-as-Judge.
    """)

    col1, col2 = st.columns([1, 1])
    with col1:
        use_context = st.checkbox(
            "Inject policy context into agent (disable to simulate hallucination)",
            value=True,
        )
    with col2:
        run_subset = st.selectbox(
            "Run:",
            ["All 10 questions", "Easy questions only (6)", "Hard questions only (4)"],
        )

    if st.button("▶  Run Evaluation Suite", type="primary", key="run_evals"):
        if run_subset == "Easy questions only (6)":
            subset = [q for q in GOLDEN_DATASET if q["difficulty"] == "Easy"]
        elif run_subset == "Hard questions only (4)":
            subset = [q for q in GOLDEN_DATASET if q["difficulty"] != "Easy"]
        else:
            subset = GOLDEN_DATASET

        results = []
        progress = st.progress(0, text="Running evaluation...")

        for i, item in enumerate(subset):
            progress.progress((i + 1) / len(subset), text=f"Evaluating {item['id']}...")

            with st.spinner(f"Running {item['id']}..."):
                response = run_agent(item["question"], use_context=use_context)
                judge_result = judge_response(item["question"], response)
                found, missed = check_facts(response, item["expected_facts"])

            results.append({
                **item,
                "response":    response,
                "judge":       judge_result,
                "facts_found": found,
                "facts_missed": missed,
                "fact_score":  len(found) / len(item["expected_facts"]) if item["expected_facts"] else 1.0,
            })

        progress.empty()

        # ── Metrics dashboard ─────────────────────────────────────────────
        st.markdown("### 📊 Evaluation Results")

        pass_count   = sum(1 for r in results if r["judge"]["verdict"] == "PASS")
        review_count = sum(1 for r in results if r["judge"]["verdict"] == "REVIEW")
        fail_count   = sum(1 for r in results if r["judge"]["verdict"] == "FAIL")
        avg_score    = round(sum(r["judge"]["overall"] for r in results) / len(results), 2)
        avg_facts    = round(sum(r["fact_score"] for r in results) / len(results) * 100, 1)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("? PASS",    pass_count,   f"{pass_count/len(results)*100:.0f}%")
        c2.metric("🟡 REVIEW", review_count, f"{review_count/len(results)*100:.0f}%")
        c3.metric("? FAIL",    fail_count,   f"{fail_count/len(results)*100:.0f}%")
        c4.metric("Avg Score", f"{avg_score}/10")
        c5.metric("Fact Coverage", f"{avg_facts}%")

        # ── Per-question results ───────────────────────────────────────────
        st.markdown("### Per-question breakdown")

        for r in results:
            verdict = r["judge"]["verdict"]
            icon = "?" if verdict == "PASS" else ("•" if verdict == "REVIEW" else "?")
            score = r["judge"]["overall"]
            fact_pct = int(r["fact_score"] * 100)

            with st.expander(
                f"{icon} {r['id']} [{r['category']} | {r['difficulty']}]  "
                f"Score: {score}/10  |  Facts: {fact_pct}%  |  {verdict}  -- "
                f"{r['question'][:60]}...",
                expanded=(verdict != "PASS"),
            ):
                col_q, col_r = st.columns([1, 1])
                with col_q:
                    st.markdown("**Question:**")
                    st.info(r["question"])
                    st.markdown("**Required facts:**")
                    for f in r["expected_facts"]:
                        found = f in r["facts_found"]
                        st.markdown(f"{'✅' if found else '❌'} `{f}` {'found' if found else 'MISSING'}")
                with col_r:
                    st.markdown("**Agent response:**")
                    if verdict == "PASS":
                        st.success(r["response"])
                    elif verdict == "REVIEW":
                        st.warning(r["response"])
                    else:
                        st.error(r["response"])

                st.markdown("**Judge scores:**")
                sc1, sc2, sc3, sc4 = st.columns(4)
                for col, crit in zip([sc1, sc2, sc3, sc4],
                                     ["accuracy", "groundedness", "tone", "completeness"]):
                    s = r["judge"].get(crit, 0)
                    col.metric(crit.capitalize(), f"{s}/10",
                               delta="ok" if s >= 7 else "low",
                               delta_color="normal" if s >= 7 else "inverse")

                if r["judge"].get("feedback"):
                    st.caption(f"⚖️ Judge: {r['judge']['feedback']}")

        # ── Failure analysis ───────────────────────────────────────────────
        failures = [r for r in results if r["judge"]["verdict"] == "FAIL"]
        if failures:
            st.markdown("### ? Failure Analysis")
            st.error(f"{len(failures)} question(s) FAILED -- agent should not deliver these responses")
            for r in failures:
                with st.container(border=True):
                    st.markdown(f"**{r['id']}: {r['question']}**")
                    st.markdown("Missing facts: " + ", ".join(f"`{f}`" for f in r["facts_missed"]))
                    st.error(r["response"])
                    st.caption(f"Fix: ensure agent has access to the relevant policy section")
        else:
            st.success("✅ No failures -- all questions PASSED or REVIEW")

        # ── Save results to session state for regression tab ───────────────
        st.session_state["last_eval_results"] = {
            "pass_rate":  pass_count / len(results),
            "avg_score":  avg_score,
            "avg_facts":  avg_facts,
            "by_id":      {r["id"]: r for r in results},
            "context":    use_context,
            "n":          len(results),
        }
        st.caption("Results saved -- switch to the Regression Testing tab to compare runs.")

        with st.expander("🔬 Execution Trace -- what just ran"):
            st.markdown(f"""
| Step | What ran | Detail |
|---|---|---|
| **Agent** | NexaBank banking agent | {len(results)} questions answered |
| **Fact check** | String matching against expected facts | Avg coverage: {avg_facts}% |
| **Judge** | LLM-as-Judge (Phase 4c) called {len(results)} times | Avg score: {avg_score}/10 |
| **Policy context** | {'Injected into agent' if use_context else 'NOT injected (hallucination test)'} | {'Context helps with factual accuracy' if use_context else 'No context reveals hallucination risk'} |

**Why run evals without context?**
Try disabling policy context to see how the agent performs on training data alone.
This reveals which facts are hallucination risks -- those facts need RAG (Phase 5a).
""")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: Regression Testing
# ════════════════════════════════════════════════════════════════════════════

with tab_regression:
    st.subheader("Regression Testing -- compare two runs")
    st.markdown("""
    A regression test confirms that a change (new system prompt, new context, new model)
    did not break questions that previously PASSED.

    **Workflow:**
    1. Run the eval suite with **policy context ON** (baseline)
    2. Modify something (disable context, change prompt, etc.)
    3. Run the eval suite again
    4. Compare -- did anything regress?
    """)

    if "last_eval_results" not in st.session_state:
        st.info(
            "ℹ️ No eval results yet. Run the evaluation suite in Tab 1 first, "
            "then come back here to compare."
        )
    else:
        prev = st.session_state["last_eval_results"]
        st.success(
            f"✅ Previous run saved: {prev['n']} questions, "
            f"pass rate {prev['pass_rate']*100:.0f}%, "
            f"avg score {prev['avg_score']}/10, "
            f"context {'ON' if prev['context'] else 'OFF'}"
        )

        st.markdown("**Now run a second configuration to compare:**")

        col1, col2 = st.columns([1, 1])
        with col1:
            use_context_b = st.checkbox("Inject policy context (new run)", value=False,
                                        key="reg_ctx")
        with col2:
            st.caption("Tip: uncheck context to simulate the agent running without RAG")

        if st.button("▶  Run Comparison", type="primary", key="run_regression"):

            results_b = []
            prog = st.progress(0)

            for i, item in enumerate(GOLDEN_DATASET):
                prog.progress((i + 1) / len(GOLDEN_DATASET))
                with st.spinner(f"Running {item['id']}..."):
                    response = run_agent(item["question"], use_context=use_context_b)
                    judge_result = judge_response(item["question"], response)
                    found, missed = check_facts(response, item["expected_facts"])
                results_b.append({
                    **item,
                    "response":     response,
                    "judge":        judge_result,
                    "facts_found":  found,
                    "facts_missed": missed,
                    "fact_score":   len(found) / len(item["expected_facts"]) if item["expected_facts"] else 1.0,
                })
            prog.empty()

            pass_b   = sum(1 for r in results_b if r["judge"]["verdict"] == "PASS")
            score_b  = round(sum(r["judge"]["overall"] for r in results_b) / len(results_b), 2)
            facts_b  = round(sum(r["fact_score"] for r in results_b) / len(results_b) * 100, 1)

            # ── Delta display ──────────────────────────────────────────────
            st.markdown("### 🔁 Regression Report")

            col_a, col_b, col_d = st.columns(3)
            with col_a:
                st.markdown("**Baseline (context ON)**")
                st.metric("Pass rate",    f"{prev['pass_rate']*100:.0f}%")
                st.metric("Avg score",    f"{prev['avg_score']}/10")
                st.metric("Fact coverage",f"{prev['avg_facts']}%")
            with col_b:
                st.markdown(f"**New run (context {'ON' if use_context_b else 'OFF'})**")
                st.metric("Pass rate",    f"{pass_b/len(results_b)*100:.0f}%")
                st.metric("Avg score",    f"{score_b}/10")
                st.metric("Fact coverage",f"{facts_b}%")
            with col_d:
                st.markdown("**Delta**")
                pr_delta = pass_b/len(results_b) - prev['pass_rate']
                sc_delta = score_b - prev['avg_score']
                ft_delta = facts_b - prev['avg_facts']
                st.metric("Pass rate",    f"{pr_delta*100:+.0f}pp",
                          delta_color="normal" if pr_delta >= 0 else "inverse")
                st.metric("Avg score",    f"{sc_delta:+.2f}",
                          delta_color="normal" if sc_delta >= 0 else "inverse")
                st.metric("Fact coverage",f"{ft_delta:+.1f}pp",
                          delta_color="normal" if ft_delta >= 0 else "inverse")

            # ── Regressions ────────────────────────────────────────────────
            regressions = [
                r for r in results_b
                if r["judge"]["verdict"] != "PASS"
                and prev["by_id"].get(r["id"], {}).get("judge", {}).get("verdict") == "PASS"
            ]
            improvements = [
                r for r in results_b
                if r["judge"]["verdict"] == "PASS"
                and prev["by_id"].get(r["id"], {}).get("judge", {}).get("verdict") != "PASS"
            ]

            if regressions:
                st.error(f"? {len(regressions)} regression(s) -- questions that PASSED before and now FAIL/REVIEW:")
                for r in regressions:
                    prev_v = prev["by_id"][r["id"]]["judge"]["verdict"]
                    st.markdown(
                        f"- **{r['id']}** `{r['question'][:60]}...`  "
                        f"{prev_v} -> **{r['judge']['verdict']}**"
                    )
                    st.caption(f"  Missing: {', '.join(r['facts_missed'])}")
            else:
                st.success("✅ No regressions -- no question that previously PASSED now fails")

            if improvements:
                st.success(f"✅ {len(improvements)} improvement(s) -- questions that now PASS that didn't before:")
                for r in improvements:
                    st.markdown(f"- **{r['id']}** `{r['question'][:60]}...`")

st.markdown("---")
st.markdown("### What's next -> Phase 5a: RAG Agent")
st.markdown(
    "Phase 4 (Trust & Safety) is now complete. "
    "Phase 5 augments agents with external knowledge. "
    "**5a RAG Agent:** Retrieve -> Augment -> Generate -- agent searches a knowledge base "
    "before answering, grounding responses in real documents rather than training data."
)
