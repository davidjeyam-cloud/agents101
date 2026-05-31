"""
Quiz Hub — dynamically generated MCQ tests for every completed phase.
Questions are generated fresh each session by Gemini using phase seed concepts.
"""

import streamlit as st
from utils.quiz import PHASE_SEEDS, generate_questions

st.set_page_config(
    page_title="Quiz Hub — Agentic AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def _init():
    defaults = {
        "qhub_state":     "selecting",   # selecting | generating | in_quiz | complete
        "qhub_phase":     None,          # phase key e.g. "3"
        "qhub_questions": [],            # list of question dicts
        "qhub_idx":       0,             # current question index
        "qhub_answers":   {},            # {idx: chosen_option_int}
        "qhub_feedback":  False,         # whether feedback is shown for current q
        "qhub_progress":  {},            # {phase_key: {score_pct, correct, total}}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📝 Quiz Hub")
st.caption("Test your understanding of each phase — questions generated fresh by Gemini from phase seed concepts")

# ---------------------------------------------------------------------------
# Cross-phase progress bar (always visible at top)
# ---------------------------------------------------------------------------
progress = st.session_state.qhub_progress
if progress:
    st.markdown("### Your Progress")
    cols = st.columns(len(progress))
    for col, (pkey, pdata) in zip(cols, progress.items()):
        phase = PHASE_SEEDS[pkey]
        pct = pdata["score_pct"]
        badge = "🏆" if pct >= 90 else ("⭐⭐" if pct >= 70 else "📚")
        col.metric(
            label=f"{phase['icon']} {phase['title']}",
            value=f"{pct:.0f}%",
            delta=f"{pdata['correct']}/{pdata['total']} correct {badge}",
        )
    st.markdown("---")

# ---------------------------------------------------------------------------
# STATE: selecting
# ---------------------------------------------------------------------------
if st.session_state.qhub_state == "selecting":
    st.markdown("### Select a Phase to Quiz")

    completed = {k: v for k, v in PHASE_SEEDS.items() if v["status"] == "complete"}

    col_left, col_right = st.columns([1, 2])

    with col_left:
        phase_options = {
            f"{v['icon']} {v['title']}": k
            for k, v in completed.items()
        }
        selected_label = st.selectbox(
            "Phase",
            options=list(phase_options.keys()),
            label_visibility="collapsed",
        )
        selected_key = phase_options[selected_label]
        phase_data = completed[selected_key]

        num_q = st.slider("Questions per quiz", min_value=6, max_value=12, value=10, step=2)

        if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
            st.session_state.qhub_phase = selected_key
            st.session_state.qhub_num_q = num_q
            st.session_state.qhub_state = "generating"
            st.rerun()

    with col_right:
        # Show what concepts will be tested
        st.markdown(f"**{phase_data['icon']} {phase_data['title']}** — what will be tested:")
        for concept in phase_data["concepts"]:
            st.markdown(f"- {concept}")

        st.markdown("---")
        st.markdown("**How it works:**")
        st.markdown(
            "Gemini reads the concept seeds above and generates fresh MCQ questions "
            "using JSON mode — different wording each time, same core concepts. "
            "You get immediate feedback after each answer."
        )

# ---------------------------------------------------------------------------
# STATE: generating
# ---------------------------------------------------------------------------
elif st.session_state.qhub_state == "generating":
    phase_key = st.session_state.qhub_phase
    phase_data = PHASE_SEEDS[phase_key]
    num_q = st.session_state.get("qhub_num_q", 10)

    with st.spinner(f"Gemini is generating {num_q} questions for {phase_data['title']}…"):
        try:
            questions = generate_questions(phase_key, num_q)
            st.session_state.qhub_questions = questions
            st.session_state.qhub_idx = 0
            st.session_state.qhub_answers = {}
            st.session_state.qhub_feedback = False
            st.session_state.qhub_state = "in_quiz"
            st.rerun()
        except Exception as e:
            st.error(f"Question generation failed: {e}")
            if st.button("← Back to phase selection"):
                st.session_state.qhub_state = "selecting"
                st.rerun()

# ---------------------------------------------------------------------------
# STATE: in_quiz
# ---------------------------------------------------------------------------
elif st.session_state.qhub_state == "in_quiz":
    questions = st.session_state.qhub_questions
    idx = st.session_state.qhub_idx
    total = len(questions)
    phase_key = st.session_state.qhub_phase
    phase_data = PHASE_SEEDS[phase_key]

    # — Progress bar —
    progress_pct = idx / total
    st.progress(progress_pct, text=f"Question {idx + 1} of {total}  ·  {phase_data['icon']} {phase_data['title']}")

    q = questions[idx]
    type_badge = {
        "scenario":   "🟢 Scenario — which approach & why",
        "tradeoff":   "🟣 Trade-off — X vs Y under constraint",
        "failure":    "🔴 Failure Mode — what breaks & why",
        "rootcause":  "🟠 Root Cause — find the flaw",
        "design":     "🔵 Design Decision — justify the architecture",
        # legacy fallbacks
        "recall":       "🔵 Recall",
        "comprehension":"🟢 Comprehension",
        "code":         "🟠 Code",
        "compare":      "🟣 Compare",
        "debug":        "🔴 Debug",
    }.get(q["type"], "⚪ Question")

    st.markdown(f"&nbsp;&nbsp;{type_badge}", unsafe_allow_html=True)
    st.markdown(f"### {q['q']}")

    answered = idx in st.session_state.qhub_answers

    if not answered:
        # Show radio — but only if not yet answered
        chosen = st.radio(
            "Choose your answer:",
            options=list(range(4)),
            format_func=lambda i: f"{chr(65+i)}.  {q['opts'][i]}",
            key=f"q_radio_{idx}",
            label_visibility="collapsed",
        )
        if st.button("✅ Submit Answer", type="primary"):
            st.session_state.qhub_answers[idx] = chosen
            st.session_state.qhub_feedback = True
            st.rerun()
    else:
        # Show answer with feedback
        chosen = st.session_state.qhub_answers[idx]
        correct = q["ans"]
        is_correct = chosen == correct

        # — Big bold result announcement —
        if is_correct:
            st.markdown(
                "<div style='background:#d4edda;border-left:6px solid #28a745;"
                "padding:18px 24px;border-radius:6px;margin-bottom:16px'>"
                "<span style='font-size:2rem;font-weight:800;color:#155724'>✅ Correct!</span>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            correct_text = q["opts"][correct]
            st.markdown(
                f"<div style='background:#f8d7da;border-left:6px solid #dc3545;"
                f"padding:18px 24px;border-radius:6px;margin-bottom:16px'>"
                f"<span style='font-size:2rem;font-weight:800;color:#721c24'>❌ Incorrect</span><br>"
                f"<span style='font-size:1.1rem;font-weight:600;color:#721c24'>"
                f"Correct answer: &nbsp;<u>{chr(65+correct)}. {correct_text}</u>"
                f"</span></div>",
                unsafe_allow_html=True,
            )

        # — Options recap (all four, highlighted) —
        st.markdown("**Options:**")
        for i, opt in enumerate(q["opts"]):
            if i == correct and i == chosen:
                st.success(f"**{chr(65+i)}.  {opt}**  ← your answer ✓")
            elif i == correct:
                st.success(f"**{chr(65+i)}.  {opt}**  ← correct answer")
            elif i == chosen:
                st.error(f"**{chr(65+i)}.  {opt}**  ← your answer")
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{chr(65+i)}.  {opt}")

        # — Grounded explanation —
        if q.get("explain"):
            st.markdown(
                f"<div style='background:#fff3cd;border-left:6px solid #ffc107;"
                f"padding:14px 20px;border-radius:6px;margin-top:14px'>"
                f"<span style='font-size:1rem;font-weight:700;color:#856404'>💡 Why this is correct:</span><br>"
                f"<span style='font-size:1rem;color:#533f03'>{q['explain']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Next / Finish
        if idx + 1 < total:
            if st.button("Next Question →", type="primary"):
                st.session_state.qhub_idx = idx + 1
                st.session_state.qhub_feedback = False
                st.rerun()
        else:
            if st.button("🏁 See Results", type="primary"):
                # Calculate and store score
                answers = st.session_state.qhub_answers
                correct_count = sum(
                    1 for i, q in enumerate(questions) if answers.get(i) == q["ans"]
                )
                pct = round(correct_count / total * 100, 1)
                st.session_state.qhub_progress[phase_key] = {
                    "score_pct": pct,
                    "correct":   correct_count,
                    "total":     total,
                }
                st.session_state.qhub_state = "complete"
                st.rerun()

    # — Abort button —
    st.markdown("---")
    if st.button("← Quit quiz", type="secondary"):
        st.session_state.qhub_state = "selecting"
        st.rerun()

# ---------------------------------------------------------------------------
# STATE: complete
# ---------------------------------------------------------------------------
elif st.session_state.qhub_state == "complete":
    questions = st.session_state.qhub_questions
    answers   = st.session_state.qhub_answers
    phase_key = st.session_state.qhub_phase
    phase_data = PHASE_SEEDS[phase_key]
    total = len(questions)
    correct_count = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["ans"])
    pct = correct_count / total * 100

    # — Score banner —
    if pct >= 90:
        st.balloons()
        st.success(f"## 🏆 Outstanding!  {correct_count}/{total} correct — {pct:.0f}%")
        verdict = "You've mastered this phase. Move on confidently."
    elif pct >= 70:
        st.success(f"## ⭐⭐ Good work!  {correct_count}/{total} correct — {pct:.0f}%")
        verdict = "Solid understanding. Review the questions you missed."
    else:
        st.warning(f"## 📚 Keep studying  {correct_count}/{total} correct — {pct:.0f}%")
        verdict = "Revisit the phase material, then retake the quiz."

    st.markdown(f"**{verdict}**")
    st.markdown(f"Phase: {phase_data['icon']} **{phase_data['title']}**")
    st.markdown("---")

    # — Score breakdown by question type —
    from collections import defaultdict
    type_scores: dict[str, list] = defaultdict(list)
    for i, q in enumerate(questions):
        type_scores[q["type"]].append(1 if answers.get(i) == q["ans"] else 0)

    st.markdown("### Score by Question Type")
    type_cols = st.columns(len(type_scores))
    type_labels = {
        "scenario":     "🟢 Scenario",
        "tradeoff":     "🟣 Trade-off",
        "failure":      "🔴 Failure Mode",
        "rootcause":    "🟠 Root Cause",
        "design":       "🔵 Design",
        # legacy fallbacks
        "recall":       "🔵 Recall",
        "comprehension":"🟢 Comprehension",
        "code":         "🟠 Code",
        "compare":      "🟣 Compare",
        "debug":        "🔴 Debug",
    }
    for col, (qtype, scores) in zip(type_cols, type_scores.items()):
        label = type_labels.get(qtype, qtype.title())
        type_pct = sum(scores) / len(scores) * 100
        col.metric(label=label, value=f"{type_pct:.0f}%", delta=f"{sum(scores)}/{len(scores)}")

    st.markdown("---")

    # — Question review —
    st.markdown("### Full Review")
    for i, q in enumerate(questions):
        chosen = answers.get(i)
        is_correct = chosen == q["ans"]
        icon = "✅" if is_correct else "❌"
        type_tag = type_labels.get(q["type"], q["type"])

        with st.expander(f"{icon} Q{i+1}  ·  {type_tag}  ·  {q['q'][:80]}{'…' if len(q['q'])>80 else ''}"):
            st.markdown(f"**{q['q']}**")
            for j, opt in enumerate(q["opts"]):
                if j == q["ans"] and j == chosen:
                    st.success(f"✅ **{chr(65+j)}. {opt}** ← Your answer — Correct")
                elif j == q["ans"]:
                    st.success(f"✅ **{chr(65+j)}. {opt}** ← Correct answer")
                elif j == chosen:
                    st.error(f"❌ **{chr(65+j)}. {opt}** ← Your answer")
                else:
                    st.markdown(f"&nbsp;&nbsp;{chr(65+j)}. {opt}")
            if q.get("explain"):
                st.info(f"💡 **Why:** {q['explain']}")

    st.markdown("---")

    # — Action buttons —
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Retake This Phase", use_container_width=True):
            st.session_state.qhub_state = "generating"
            st.rerun()
    with col2:
        if st.button("🗺️ Try Another Phase", use_container_width=True):
            st.session_state.qhub_state = "selecting"
            st.rerun()
    with col3:
        if pct < 90:
            st.info(f"💡 Tip: Review **{phase_data['title']}** then retake to hit 90%+")
        else:
            completed_phases = list(PHASE_SEEDS.keys())
            current_idx = completed_phases.index(phase_key) if phase_key in completed_phases else -1
            if current_idx < len(completed_phases) - 1:
                next_key = completed_phases[current_idx + 1]
                next_title = PHASE_SEEDS[next_key]["title"]
                st.success(f"🚀 Ready for: **{next_title}**")
