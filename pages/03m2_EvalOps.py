"""
Phase 4e — Eval Engineering & Ops
pass@k, deterministic eval, LLM-as-judge at scale, continuous eval ops loop,
EU AI Act / NIST AI RMF / ISO/IEC 42001 compliance.
Sits between Phase 4 (Trust & Safety) and Phase 5 (Knowledge & Memory).
"""
import os
import json
import math
import time
import streamlit as st
from dotenv import load_dotenv
from google.genai import types
from utils.llm import _call, MODEL, _client
from utils.trace import render_trace

load_dotenv()

st.set_page_config(
    page_title="4e — Eval Engineering & Ops",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📐 4e — Eval Engineering & Ops")
st.caption(
    "pass@k · deterministic eval · LLM-as-judge at scale · continuous eval loop · "
    "EU AI Act · NIST AI RMF · ISO/IEC 42001"
)

st.image("docs/images/arch_evalops.jpg", use_container_width=True,
         caption="Four layers: Deterministic Eval → LLM-as-Judge → Continuous Eval Ops Loop → Compliance & Governance")

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    &#128279; Building on Phase 4c (LLM-as-Judge) and Phase 4d (Eval Framework)</span><br><br>
    <span style='color:#1C2833'>
    Phase 4c gave you a judge for <em>one response</em>.
    Phase 4d gave you a golden dataset and a batch eval loop.
    Phase 4e turns eval into a <strong>continuous engineering discipline</strong>: pass@k to measure
    variance across multiple samples, an ops loop where every production failure automatically
    becomes a regression test, and the compliance evidence trail demanded by EU AI Act,
    NIST AI RMF, and ISO/IEC 42001.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Eval Engineering & Ops — the three layers"):
    st.markdown("""
**Three layers of eval maturity:**

| Layer | What you measure | When it runs | Phase |
|---|---|---|---|
| **Deterministic** | Exact facts, schema, format | On every run, in CI | 4e |
| **LLM-as-Judge** | Quality, tone, groundedness, safety | Batch + CI | 4c → 4e |
| **Eval Ops Loop** | Quality trend over time | Continuous | 4e |

---

**pass@k — what it means:**

Run your agent `k` times on the same input with temperature > 0.
Let `p` = probability a single run passes.
Then:

```
pass@k = P(at least 1 of k passes) = 1 − (1−p)^k
```

| p (single-run pass rate) | pass@1 | pass@3 | pass@5 | pass@10 |
|---|---|---|---|---|
| 0.50 | 50% | 87.5% | 96.9% | 99.9% |
| 0.30 | 30% | 65.7% | 83.2% | 97.2% |
| 0.10 | 10% | 27.1% | 41.0% | 65.1% |

**Why it matters:** a single eval run hides variance. If your agent passes 30% of
the time, pass@1 = 30% but pass@5 = 83% — best-of-5 looks production-ready even
though most individual runs fail. pass@k tells you the true capability ceiling.

**The eval ops flywheel:**
```
define golden dataset
    → run deterministic + LLM-judge + pass@k
    → score ≥ baseline? → ship / block PR
    → production failure? → add to dataset → repeat
```
The dataset only grows. Every sprint the bar rises automatically.

**Why regulators care:**

| Standard | Relevant clause | What they require |
|---|---|---|
| EU AI Act (2024) | Art. 9, Art. 15 | Documented accuracy/robustness testing for high-risk AI |
| NIST AI RMF | MEASURE 2.5, 2.6 | Repeatable eval procedures; results in risk register |
| ISO/IEC 42001 | Clause 9.1 | Monitoring & measurement of AI system performance |

Eval ops is not just good engineering — for regulated AI it is a legal requirement.
""")

with st.expander("📐 Core Code Pattern — pass@k + deterministic + eval ops loop"):
    st.code('''
import math, re, json
from utils.llm import _call, MODEL, _client

# ── pass@k calculation ────────────────────────────────────────────────────────
def pass_at_k(n_correct: int, k: int, n_total: int) -> float:
    """
    Unbiased estimator (Chen et al. 2021 HumanEval):
      pass@k = 1 - C(n_total-n_correct, k) / C(n_total, k)
    For small n_total, simpler: 1 - (1-p)^k where p = n_correct/n_total
    """
    if n_total - n_correct < k:
        return 1.0
    p = n_correct / n_total
    return 1.0 - (1.0 - p) ** k

# ── deterministic eval ────────────────────────────────────────────────────────
def deterministic_eval(response: str, expected_facts: list[str]) -> dict:
    hits = [f for f in expected_facts if f.lower() in response.lower()]
    return {
        "passed": len(hits) == len(expected_facts),
        "score":  len(hits) / len(expected_facts),
        "hits":   hits,
        "misses": [f for f in expected_facts if f not in hits],
    }

# ── LLM-as-judge ─────────────────────────────────────────────────────────────
JUDGE_SYS = """You are an impartial evaluator. Score the response on:
- correctness (0-5): does it answer the question accurately?
- groundedness (0-5): are claims supported, no hallucination?
- coherence (0-5): is it clear and well-structured?
Return ONLY JSON: {"correctness":N, "groundedness":N, "coherence":N, "reason":"..."}"""

def llm_judge(question: str, response: str) -> dict:
    client = _client()
    r = _call(client.models.generate_content,
              model=MODEL,
              contents=f"Question: {question}\\nResponse: {response}",
              config=types.GenerateContentConfig(
                  system_instruction=JUDGE_SYS,
                  response_mime_type="application/json"))
    return json.loads(r.text)

# ── eval ops loop — run k times, score each, compute pass@k ──────────────────
GOLDEN = [
    {"id": "Q1", "question": "What is RAG?",
     "facts": ["retrieve", "augment", "generate"]},
    {"id": "Q2", "question": "What is the ReAct pattern?",
     "facts": ["reason", "act"]},
]

def run_eval_suite(k: int = 3) -> dict:
    results = []
    client = _client()
    for item in GOLDEN:
        scores = []
        for _ in range(k):
            r = _call(client.models.generate_content,
                      model=MODEL, contents=item["question"])
            det = deterministic_eval(r.text, item["facts"])
            scores.append(det["passed"])
        n_correct = sum(scores)
        results.append({
            "id":      item["id"],
            "pass@1":  round(n_correct / k, 3),
            "pass@k":  round(pass_at_k(n_correct, k, k), 3),
            "k":       k,
        })
    return results

# ── eval ops loop: prod failure → regression test ─────────────────────────────
def capture_failure(question: str, bad_response: str, expected_facts: list[str]):
    """Call this whenever a production failure is detected."""
    new_test = {
        "id":       f"REGRESSION_{int(time.time())}",
        "question": question,
        "facts":    expected_facts,
        "source":   "production_failure",
        "bad_response": bad_response[:200],
    }
    # Append to GOLDEN (in production: write to versioned eval dataset store)
    GOLDEN.append(new_test)
    return new_test
''', language="python")
    st.markdown("""
**What this adds over Phase 4d:** Phase 4d ran the agent once per question.
`pass@k` runs it `k` times and measures the probability distribution — critical for
temperature > 0 agents where outputs vary. A single-run eval hides variance;
`pass@k` exposes it.

**The `capture_failure()` function is the flywheel:** every time production returns
a wrong answer, you call it. The golden dataset grows automatically. Your next eval
run measures whether your fix actually resolved it — and whether it introduced
any regressions. The dataset compounds over time.
""")

st.markdown("---")
st.markdown("### Interactive Demos")

tab_det, tab_passatk, tab_ops, tab_compliance = st.tabs([
    "Deterministic Eval",
    "pass@k Sampling",
    "Eval Ops Loop",
    "Compliance Evidence",
])

# ── TAB: Deterministic Eval ───────────────────────────────────────────────────
with tab_det:
    st.markdown("**Run deterministic fact-checking on a live agent response**")
    st.markdown("""
| Check type | How | Best for |
|---|---|---|
| Contains match | `expected.lower() in response.lower()` | Policy facts, numbers, product names |
| Regex | `re.search(pattern, response)` | Dates, codes, formatted values |
| Schema | `jsonschema.validate(output, schema)` | Structured / JSON outputs |
""")

    col1, col2 = st.columns(2)
    with col1:
        det_q = st.text_input("Question:", value="What does RAG stand for?", key="det_q")
        det_facts = st.text_area(
            "Required facts (one per line):",
            value="Retrieval\nAugmented\nGeneration",
            key="det_facts", height=90,
        )
    with col2:
        det_pattern = st.text_input(
            "Optional regex pattern (leave blank to skip):",
            value="", key="det_pattern",
            placeholder="e.g. \\bRAG\\b"
        )

    if st.button("Run deterministic eval", key="run_det"):
        client = _client()
        facts = [f.strip() for f in det_facts.strip().splitlines() if f.strip()]

        sys_prompt = "Answer the question concisely in 1-2 sentences."
        with st.spinner("Running agent..."):
            r = _call(client.models.generate_content, model=MODEL,
                      contents=det_q,
                      config=types.GenerateContentConfig(system_instruction=sys_prompt))
        response_text = r.text

        st.markdown("#### Agent response")
        st.info(response_text)

        hits = [f for f in facts if f.lower() in response_text.lower()]
        misses = [f for f in facts if f.lower() not in response_text.lower()]
        det_score = len(hits) / len(facts) if facts else 0
        verdict = "✅ PASS" if not misses else "❌ FAIL"

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Fact score", f"{det_score:.0%}")
        with col_b:
            st.metric("Hits", f"{len(hits)}/{len(facts)}")
        with col_c:
            st.markdown(f"### {verdict}")

        if hits:
            st.success("Found: " + " · ".join(hits))
        if misses:
            st.error("Missing: " + " · ".join(misses))

        if det_pattern:
            import re
            match = re.search(det_pattern, response_text, re.IGNORECASE)
            st.markdown(f"**Regex `{det_pattern}`:** {'✅ matched' if match else '❌ no match'}")

        render_trace("Deterministic Eval", [
            ("System prompt", sys_prompt),
            ("Question", det_q),
            ("Response", response_text),
            ("Facts checked", str(facts)),
            (f"Result (score={det_score:.2f})", f"hits={hits}, misses={misses} → {verdict}"),
        ])

# ── TAB: pass@k ───────────────────────────────────────────────────────────────
with tab_passatk:
    st.markdown("**Run the same question k times and measure pass@k variance**")
    st.markdown("""
| Metric | Formula | What it tells you |
|---|---|---|
| `pass@1` | p (single-run pass rate) | Most likely outcome in one try |
| `pass@k` | 1 − (1−p)^k | Probability at least one of k tries passes |
| `majority@k` | majority vote over k outputs | Best answer via consensus, not just first attempt |
""")

    col1, col2 = st.columns([3, 1])
    with col1:
        pk_q = st.text_input("Question:", value="Name the three steps of the ReAct pattern.", key="pk_q")
        pk_facts_raw = st.text_input("Required facts (comma-separated):", value="reason, act, observe", key="pk_facts")
    with col2:
        k_val = st.selectbox("k (number of runs):", [3, 5, 10], index=0, key="k_val")

    if st.button(f"Run {k_val} times & compute pass@k", key="run_passatk"):
        client = _client()
        pk_facts = [f.strip() for f in pk_facts_raw.split(",") if f.strip()]
        sys_p = "Answer concisely."
        responses = []
        passes = []
        progress = st.progress(0)

        for i in range(k_val):
            r = _call(client.models.generate_content, model=MODEL,
                      contents=pk_q,
                      config=types.GenerateContentConfig(
                          system_instruction=sys_p,
                          temperature=0.9,
                      ))
            text = r.text
            passed = all(f.lower() in text.lower() for f in pk_facts)
            responses.append(text)
            passes.append(passed)
            progress.progress((i + 1) / k_val)

        n_correct = sum(passes)
        p_single = n_correct / k_val
        p_at_k = 1.0 - (1.0 - p_single) ** k_val if p_single < 1 else 1.0

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("pass@1 (single-run rate)", f"{p_single:.0%}")
        with col_b:
            st.metric(f"pass@{k_val}", f"{p_at_k:.1%}")
        with col_c:
            st.metric("Correct runs", f"{n_correct}/{k_val}")

        if p_single < 0.5:
            st.warning(
                f"⚠ pass@1 = {p_single:.0%} — most individual runs fail. "
                f"Best-of-{k_val} hides this: pass@{k_val} = {p_at_k:.1%}. "
                "Lower temperature or improve the prompt before shipping."
            )
        else:
            st.success(f"pass@{k_val} = {p_at_k:.1%} — agent is consistently passing.")

        with st.expander(f"All {k_val} responses"):
            for i, (resp, passed) in enumerate(zip(responses, passes)):
                status = "✅" if passed else "❌"
                st.markdown(f"**Run {i+1}** {status}")
                st.caption(resp[:300])

        # pass@k table for different k values
        st.markdown("**pass@k for different k values (given this p):**")
        rows = []
        for kk in [1, 2, 3, 5, 10, 20]:
            pk = 1.0 - (1.0 - p_single) ** kk if p_single < 1 else 1.0
            rows.append({"k": kk, "pass@k": f"{pk:.1%}", "Interpretation": "individual run" if kk == 1 else f"best of {kk}"})
        st.table(rows)

        render_trace(f"pass@k (k={k_val})", [
            ("Question", pk_q),
            ("Required facts", str(pk_facts)),
            ("Runs", str(k_val)),
            ("Correct", f"{n_correct}/{k_val}"),
            (f"pass@1 / pass@{k_val}", f"{p_single:.2%} / {p_at_k:.2%}"),
        ])

# ── TAB: Eval Ops Loop ────────────────────────────────────────────────────────
with tab_ops:
    st.markdown("**Simulate the continuous eval ops flywheel**")
    st.markdown(
        "The standard operating loop: turn every production failure into a regression test. "
        "The eval dataset grows each time the agent fails. CI blocks regressions before they ship."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Step 1 — Run eval suite")
        st.markdown("Run your golden dataset + LLM judge, score against baseline.")

        if "eval_dataset" not in st.session_state:
            st.session_state.eval_dataset = [
                {"id": "Q1", "question": "What is RAG?",
                 "facts": ["retrieval", "augmented", "generation"]},
                {"id": "Q2", "question": "What is the ReAct pattern?",
                 "facts": ["reason", "act"]},
                {"id": "Q3", "question": "What does HITL stand for?",
                 "facts": ["human", "loop"]},
            ]
        if "eval_baseline" not in st.session_state:
            st.session_state.eval_baseline = 0.75
        if "eval_history" not in st.session_state:
            st.session_state.eval_history = []

        st.info(f"Dataset size: **{len(st.session_state.eval_dataset)}** questions | "
                f"Baseline: **{st.session_state.eval_baseline:.0%}**")

        if st.button("Run eval suite (CI gate simulation)", key="run_suite"):
            client = _client()
            results = []
            prog = st.progress(0)
            for i, item in enumerate(st.session_state.eval_dataset):
                r = _call(client.models.generate_content, model=MODEL,
                          contents=item["question"],
                          config=types.GenerateContentConfig(
                              system_instruction="Answer the question in 1-2 sentences."))
                passed = all(f.lower() in r.text.lower() for f in item["facts"])
                results.append({"id": item["id"], "passed": passed, "response": r.text})
                prog.progress((i + 1) / len(st.session_state.eval_dataset))

            overall = sum(r["passed"] for r in results) / len(results)
            gate_pass = overall >= st.session_state.eval_baseline

            col_x, col_y = st.columns(2)
            with col_x:
                st.metric("Overall score", f"{overall:.0%}")
            with col_y:
                st.metric("Baseline", f"{st.session_state.eval_baseline:.0%}")

            if gate_pass:
                st.success(f"✅ CI GATE PASSED ({overall:.0%} ≥ {st.session_state.eval_baseline:.0%}) — safe to merge")
            else:
                st.error(f"❌ CI GATE BLOCKED ({overall:.0%} < {st.session_state.eval_baseline:.0%}) — fix before merging")

            st.session_state.eval_history.append({
                "run": len(st.session_state.eval_history) + 1,
                "score": round(overall, 3),
                "dataset_size": len(st.session_state.eval_dataset),
                "gate": "PASS" if gate_pass else "BLOCK",
            })

            with st.expander("Per-question results"):
                for res in results:
                    icon = "✅" if res["passed"] else "❌"
                    st.markdown(f"**{res['id']}** {icon}: {res['response'][:150]}...")

    with col2:
        st.markdown("#### Step 2 — Capture a production failure")
        st.markdown("When an agent fails in production, add it as a regression test.")

        fail_q = st.text_input("Failed question:", value="What does LLM stand for?", key="fail_q")
        fail_facts = st.text_input("Expected facts (comma-separated):", value="large,language,model", key="fail_facts")

        if st.button("Capture failure → add to eval dataset", key="cap_fail"):
            facts = [f.strip() for f in fail_facts.split(",") if f.strip()]
            new_id = f"REG_{len(st.session_state.eval_dataset) + 1}"
            st.session_state.eval_dataset.append({
                "id": new_id,
                "question": fail_q,
                "facts": facts,
                "source": "production_failure",
            })
            st.success(
                f"✅ Regression test `{new_id}` added — dataset now has "
                f"**{len(st.session_state.eval_dataset)}** questions. "
                "Run the eval suite again to measure impact."
            )

        st.markdown("---")
        st.markdown("#### Eval run history")
        if st.session_state.eval_history:
            st.table(st.session_state.eval_history)
            scores = [h["score"] for h in st.session_state.eval_history]
            st.line_chart({"score": scores})
        else:
            st.caption("No runs yet — run the eval suite above.")

# ── TAB: Compliance Evidence ──────────────────────────────────────────────────
with tab_compliance:
    st.markdown("**Generate a compliance evidence summary for EU AI Act / NIST AI RMF / ISO 42001**")
    st.markdown("""
| Standard | Clause | What eval ops satisfies |
|---|---|---|
| **EU AI Act** | Art. 9 | Risk management system — continuous accuracy testing documented |
| **EU AI Act** | Art. 15 | Accuracy and robustness — metrics recorded per version |
| **NIST AI RMF** | MEASURE 2.5 | Evaluations are performed and documented |
| **NIST AI RMF** | MEASURE 2.6 | Evaluation results are used to improve the system |
| **ISO/IEC 42001** | Clause 9.1 | Monitoring and measurement of AI system performance |
""")

    col1, col2 = st.columns(2)
    with col1:
        sys_name = st.text_input("AI system name:", value="Agents101 RAG Agent", key="comp_sys")
        risk_level = st.selectbox("EU AI Act risk level:", ["High-risk", "Limited-risk", "Minimal-risk"], key="comp_risk")
        eval_method = st.multiselect(
            "Eval methods used:",
            ["Deterministic (exact match)", "LLM-as-Judge", "pass@k sampling", "Human review"],
            default=["Deterministic (exact match)", "LLM-as-Judge"],
            key="comp_methods",
        )
    with col2:
        baseline_score = st.slider("Current eval score:", 0.0, 1.0, 0.82, 0.01, key="comp_score")
        dataset_size = st.number_input("Eval dataset size:", min_value=1, value=len(st.session_state.get("eval_dataset", [])) or 10, key="comp_ds")
        eval_freq = st.selectbox("Eval frequency:", ["Every PR (CI)", "Daily", "Weekly", "On release"], key="comp_freq")

    if st.button("Generate compliance evidence summary", key="gen_compliance"):
        client = _client()
        compliance_prompt = f"""
You are a compliance documentation specialist. Generate a structured technical compliance summary
for an AI system evaluation programme. Use formal but concise language.

System: {sys_name}
EU AI Act risk level: {risk_level}
Eval methods: {', '.join(eval_method)}
Current score: {baseline_score:.0%}
Dataset size: {dataset_size} test cases
Eval frequency: {eval_freq}

Generate a compliance evidence summary covering:
1. EU AI Act Article 9 (risk management) and Article 15 (accuracy)
2. NIST AI RMF MEASURE function (2.5, 2.6)
3. ISO/IEC 42001 Clause 9.1 (monitoring and measurement)

For each standard, state: what is evidenced, what is the evidence, any gaps.
Format as a structured report with clear headers.
"""
        with st.spinner("Generating compliance summary..."):
            r = _call(client.models.generate_content, model=MODEL,
                      contents=compliance_prompt,
                      config=types.GenerateContentConfig(
                          system_instruction="You are a technical compliance documentation specialist."))

        st.markdown("#### Compliance Evidence Summary")
        st.markdown(r.text)

        render_trace("Compliance Evidence Generator", [
            ("System", sys_name),
            ("Risk level", risk_level),
            ("Eval methods", str(eval_method)),
            ("Score / dataset / frequency", f"{baseline_score:.0%} / {dataset_size} / {eval_freq}"),
            ("Generated summary (truncated)", r.text[:500] + "..."),
        ])

        st.download_button(
            "Download compliance summary (txt)",
            data=r.text,
            file_name=f"compliance_evidence_{sys_name.replace(' ', '_')}.txt",
            mime="text/plain",
        )

st.markdown("---")
st.markdown("### What's next → Phase 5a — RAG Agent")
st.markdown(
    "Eval ops gives you the quality gate. Phase 5 equips agents with external knowledge "
    "via Retrieval-Augmented Generation — the first major memory pattern beyond session state."
)
