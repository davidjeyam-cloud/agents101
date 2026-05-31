"""
Phase 2c — Parallelization
Two variants: Sectioning (split → parallel → merge) and Voting (replicate → parallel → vote).
"""

import streamlit as st
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 2c — Parallelization", page_icon="⚡", layout="wide")
st.title("⚡ Phase 2c — Parallelization")
st.caption("Workflow Pattern 3 of 5 — from *Building Effective Agents*, Anthropic Engineering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_2c
st.image(diagram_2c(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Parallelization?"):
    st.markdown("""
    > *"LLM tasks can often be parallelised for greater efficiency... either by splitting
    > tasks into independent parallel workstreams, or by running the same task multiple times."*
    > — Anthropic, Building Effective Agents

    **Two variants:**

    | | Variant A — Sectioning | Variant B — Voting |
    |---|---|---|
    | **Input** | One large document | One question |
    | **Split how?** | Split into N chunks | Replicate N times |
    | **Parallel calls** | Each chunk processed independently | Same question, N calls |
    | **Combine how?** | Merge summaries into one report | Majority vote / synthesise |
    | **Use case** | Document too large for one prompt | High-stakes decision needing confidence |

    **Why it is NOT an Agent:**
    Your code explicitly launches the `ThreadPoolExecutor`, defines how many workers,
    and decides how to combine results. The LLMs only process their own piece.

    **Key benefit:**
    3 parallel calls take roughly the same wall-clock time as 1 call.
    Sequential would take 3×. Parallelism is free speed.
    """)

st.markdown("---")

tab_a, tab_b = st.tabs(["📄 Variant A — Sectioning", "🗳️ Variant B — Voting"])


# ══════════════════════════════════════════════════════════════════════════════
# Variant A — Sectioning
# ══════════════════════════════════════════════════════════════════════════════

with tab_a:
    st.subheader("Variant A — Sectioning")
    st.markdown("""
    A long customer feedback document is split into chunks.
    Each chunk is summarised **in parallel**. Results are merged by a final LLM call.
    """)

    SAMPLE_FEEDBACK = """Customer 1: I've been using the app for 6 months and overall it's fantastic. The speed has improved a lot since the last update. However, I keep getting logged out every few days which is really annoying. Please fix the session timeout issue.

Customer 2: Your billing system charged me twice in March. I raised a ticket 3 weeks ago and still haven't received my refund. This is unacceptable. The support team keeps telling me to wait but $49.99 is a significant amount. I want this resolved immediately or I'll dispute the charge with my bank.

Customer 3: Love the new dark mode feature! It's exactly what I needed for late-night use. The only suggestion I have is to add keyboard shortcuts — power users like me would benefit greatly. Also the search function could be faster.

Customer 4: The app crashed twice this week when I was in the middle of an important presentation. I lost 20 minutes of work. The auto-save feature doesn't seem to be working reliably. This is a professional tool and these crashes are damaging my credibility with clients.

Customer 5: Onboarding was smooth and the tutorial videos are very helpful. I did struggle a bit with the export to PDF feature — the formatting gets messed up for tables. Everything else is working well. Looking forward to the API integration you mentioned in the roadmap."""

    if "sel_2c_a" not in st.session_state:
        st.session_state.sel_2c_a = SAMPLE_FEEDBACK

    feedback_text = st.text_area(
        "Customer feedback document (will be split into chunks):",
        value=st.session_state.sel_2c_a,
        height=180,
    )

    chunk_size = st.slider("Words per chunk:", min_value=50, max_value=200,
                           value=100, step=25, key="chunk_size_2c")

    def split_into_chunks(text: str, max_words: int) -> list[str]:
        words = text.split()
        return [" ".join(words[i:i + max_words])
                for i in range(0, len(words), max_words) if words[i:i + max_words]]

    def summarise_chunk(args: tuple) -> tuple[int, str]:
        chunk_num, chunk_text = args
        prompt = f"""Extract key issues and sentiment from this customer feedback chunk.
Be concise — 2 sentences max. Include: main issue, sentiment (positive/negative/mixed).

Chunk:
\"\"\"{chunk_text}\"\"\"

Summary:"""
        try:
            response = _call(client.models.generate_content, model=MODEL, contents=prompt)
            return chunk_num, response.text.strip()
        except Exception as e:
            return chunk_num, f"Error: {e}"

    def merge_summaries(summaries: list[str]) -> str:
        combined = "\n\n".join(f"Section {i+1}: {s}" for i, s in enumerate(summaries))
        prompt = f"""You have {len(summaries)} section summaries from a customer feedback report.
Create a consolidated executive summary with:
- Top 3 recurring issues (ranked by frequency/severity)
- Overall sentiment
- 2 recommended action items

Section summaries:
{combined}

Executive summary:"""
        response = _call(client.models.generate_content, model=MODEL, contents=prompt)
        return response.text.strip()

    if st.button("▶  Run Parallel Sectioning", type="primary", key="run_2c_a"):
        chunks = split_into_chunks(feedback_text, chunk_size)

        if len(chunks) < 2:
            st.warning("Text too short to split. Reduce chunk size or add more text.")
            st.stop()

        st.markdown(f"**Document split into {len(chunks)} chunks — processing in parallel…**")

        # ── Parallel execution ─────────────────────────────────────────────────
        chunk_cols = st.columns(min(len(chunks), 4))
        placeholders = [col.empty() for col in chunk_cols[:len(chunks)]]

        for i, ph in enumerate(placeholders):
            ph.info(f"Chunk {i+1}\n⏳ running…")

        t_start = time.time()

        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            futures = {executor.submit(summarise_chunk, (i, c)): i
                       for i, c in enumerate(chunks)}
            chunk_summaries = {}
            for future in as_completed(futures):
                num, summary = future.result()
                chunk_summaries[num] = summary
                placeholders[num].success(f"**Chunk {num+1} ✓**\n\n{summary}")

        t_parallel = time.time() - t_start

        st.markdown("---")
        st.success(
            f"⚡ All {len(chunks)} chunks completed in **{t_parallel:.1f}s** (parallel).  "
            f"Sequential would take ~**{t_parallel * len(chunks):.1f}s**."
        )

        # ── Merge ──────────────────────────────────────────────────────────────
        st.markdown("#### Merging summaries → Final Report")
        with st.spinner("Merge LLM combining all summaries…"):
            ordered = [chunk_summaries[i] for i in range(len(chunks))]
            report = merge_summaries(ordered)

        with st.container(border=True):
            st.markdown("**📋 Executive Summary (merged from all chunks):**")
            st.success(report)

        with st.expander("🔍 What just happened"):
            st.markdown(f"""
| Step | How | Time saved |
|---|---|---|
| Split into {len(chunks)} chunks | `text.split()` — plain Python | — |
| Summarise each chunk | `ThreadPoolExecutor(max_workers={len(chunks)})` | ~{t_parallel*(len(chunks)-1):.1f}s |
| Merge summaries | Single LLM call | — |

**Total parallel LLM calls: {len(chunks)}** running simultaneously.
**Your code** launched them, waited for all, then called the merge LLM.
The LLMs never knew about each other.
""")


# ══════════════════════════════════════════════════════════════════════════════
# Variant B — Voting
# ══════════════════════════════════════════════════════════════════════════════

with tab_b:
    st.subheader("Variant B — Voting")
    st.markdown("""
    The same question is asked **3 times in parallel** from different perspectives.
    Results are synthesised into a single high-confidence answer.

    *Use case: High-stakes decisions where a single LLM response might be inconsistent.*
    """)

    VOTE_EXAMPLES = {
        "Refund policy":     "A customer bought our premium plan 45 days ago and says it doesn't meet their needs. Our policy is 30-day refunds. Should we grant a full refund, partial refund, or no refund?",
        "Escalation decision": "A customer has contacted support 5 times in 2 weeks about the same login bug. The bug is known and on the roadmap for next month. Should we escalate this customer to a senior engineer now or ask them to wait?",
        "Feature priority":  "We have two feature requests: (1) dark mode requested by 200 users, (2) API export requested by 15 enterprise users. Which should we prioritise?",
    }

    PERSPECTIVES = {
        "Customer-centric": "You prioritise customer satisfaction and long-term loyalty above short-term cost.",
        "Business-focused":  "You balance customer needs with business sustainability and policy consistency.",
        "Risk-aware":        "You consider precedent-setting risks — what happens if this decision is applied to all similar cases.",
    }

    if "sel_2c_b" not in st.session_state:
        st.session_state.sel_2c_b = VOTE_EXAMPLES["Refund policy"]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Quick examples:**")
        for label, text in VOTE_EXAMPLES.items():
            if st.button(label, key=f"vote_ex_{label}"):
                st.session_state.sel_2c_b = text
                st.rerun()
    with col1:
        question = st.text_area(
            "Decision question:",
            value=st.session_state.sel_2c_b,
            height=100,
        )

    def ask_perspective(args: tuple) -> tuple[str, str]:
        perspective, instruction, question = args
        prompt = f"""You are a customer support advisor. Answer the question below.
Keep your response to 3-4 sentences. Be direct and give a clear recommendation.

Question: {question}"""
        try:
            response = _call(
                client.models.generate_content,
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=instruction),
            )
            return perspective, response.text.strip()
        except Exception as e:
            return perspective, f"Error: {e}"

    def synthesise(question: str, votes: dict) -> str:
        formatted = "\n\n".join(
            f"**{p} view:** {v}" for p, v in votes.items()
        )
        prompt = f"""Three advisors answered the same question from different perspectives.
Synthesise their views into one balanced recommendation (3-5 sentences).
Note where they agree and acknowledge any key trade-off.

Question: {question}

{formatted}

Synthesised recommendation:"""
        response = _call(client.models.generate_content, model=MODEL, contents=prompt)
        return response.text.strip()

    if st.button("▶  Run Parallel Voting", type="primary", key="run_2c_b"):

        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        st.markdown("**Asking 3 advisors in parallel…**")

        v_cols = st.columns(3)
        v_placeholders = {p: col.empty() for p, col in zip(PERSPECTIVES, v_cols)}
        for p, ph in v_placeholders.items():
            ph.info(f"**{p}**\n\n⏳ thinking…")

        t_start = time.time()

        tasks = [(p, instr, question) for p, instr in PERSPECTIVES.items()]
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(ask_perspective, task): task[0] for task in tasks}
            votes = {}
            for future in as_completed(futures):
                perspective, answer = future.result()
                votes[perspective] = answer
                v_placeholders[perspective].success(f"**{perspective} ✓**\n\n{answer}")

        t_parallel = time.time() - t_start

        st.success(
            f"⚡ All 3 perspectives completed in **{t_parallel:.1f}s** (parallel). "
            f"Sequential would take ~**{t_parallel*3:.1f}s**."
        )

        st.markdown("---")
        st.markdown("#### Synthesising votes → Final Recommendation")

        with st.spinner("Synthesising…"):
            synthesis = synthesise(question, votes)

        with st.container(border=True):
            st.markdown("**🗳️ Synthesised Recommendation (majority consensus):**")
            st.success(synthesis)

        with st.expander("🔍 What just happened"):
            st.markdown(f"""
| Step | How |
|---|---|
| Ask 3 perspectives | `ThreadPoolExecutor(max_workers=3)` — all 3 run simultaneously |
| Collect results | `as_completed(futures)` — display each as it finishes |
| Synthesise | Single LLM call seeing all 3 responses |

**Why voting increases confidence:**
If all 3 perspectives agree → high confidence answer.
If they disagree → the synthesis highlights the trade-off honestly.
A single call might give a different answer on retry. 3 calls give a more stable result.
""")

    st.markdown("---")
    st.markdown("### What's next → Phase 2d: Orchestrator-Workers")
    st.markdown(
        "One **Orchestrator** LLM breaks a goal into sub-tasks, "
        "delegates each to a **Worker** LLM, then assembles the results. "
        "This is the first pattern where the structure isn't fully predefined — "
        "the orchestrator plans dynamically."
    )
