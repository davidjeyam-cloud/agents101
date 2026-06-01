"""
Learning Insights — Key Q&A from the learning journey.
Captures conceptual questions and answers (not bug fixes or API issues).
"""

import streamlit as st

st.set_page_config(page_title="Learning Insights", page_icon="💡", layout="wide")

# ── Phase 0 header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#0D1117 0%,#0F1A2E 100%);
border-left:5px solid #00FF9F;border-radius:8px;padding:18px 24px;margin-bottom:24px'>
  <div style='font-size:0.65rem;font-weight:700;letter-spacing:3px;
              text-transform:uppercase;color:#00FF9F;margin-bottom:6px'>
    Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Concepts
  </div>
  <div style='font-size:1.7rem;font-weight:800;color:#E6EDF3;line-height:1.2'>
    💡 Learning Insights
  </div>
  <div style='font-size:0.88rem;color:#8B949E;margin-top:6px'>
    The <em>why</em> questions — the concepts that matter most as you progress through the course.
    Each answer came from a real question during implementation.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Table of contents ──────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#161B22;border:1px solid #21262D;border-radius:8px;
padding:16px 22px;margin-bottom:24px'>
  <div style='font-size:0.65rem;font-weight:700;letter-spacing:2px;
              text-transform:uppercase;color:#8B949E;margin-bottom:12px'>
    CONTENTS — 5 themes · 12 questions
  </div>
  <table style='width:100%;border-collapse:collapse;font-size:0.85rem'>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>1.&nbsp; 🤖 What is Agentic AI?</td>
      <td style='padding:5px 0;color:#8B949E'>3 questions &nbsp;·&nbsp; Model-agnostic, agent definition, workflow vs agent</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>2.&nbsp; 🧱 The Building Blocks</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; Phase 1 progression, function calling, 1c vs 1d, mini agent</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>3.&nbsp; 🧰 Tools and Memory</td>
      <td style='padding:5px 0;color:#8B949E'>2 questions &nbsp;·&nbsp; Real vs mock tools, history format</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>4.&nbsp; 📐 Diagrams and Visual Understanding</td>
      <td style='padding:5px 0;color:#8B949E'>2 questions &nbsp;·&nbsp; Agent banner, diagram-code sync</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>5.&nbsp; 🐍 Python and Streamlit</td>
      <td style='padding:5px 0;color:#8B949E'>1 question &nbsp;·&nbsp; st.tabs() and context managers</td>
    </tr>
  </table>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 1 — What is Agentic AI?
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🤖 1. What is Agentic AI?")

with st.expander("Q: Do I need a specific LLM provider to learn Agentic AI?"):
    st.markdown("""
**No — and this is an important first principle.**

The architectural patterns in the Anthropic article — prompt chaining, routing,
parallelization, orchestrator-workers, evaluator-optimizer, and agents — are
**100% model-agnostic**. They work with any LLM: Gemini, Claude, GPT, Llama, or any other.

This project uses Gemini 2.5 Flash (Google AI Studio, free tier) with no loss of learning value.
The patterns are about *how you compose LLM calls*, not which LLM you use.
To swap providers, you change one file: `utils/llm.py`.

**Takeaway:** Learn the patterns. The model is interchangeable.
""")

with st.expander("Q: Where does an Agent actually appear in this learning journey?"):
    st.markdown("""
The Anthropic article defines a clear progression:

| Stage | What it is | Who controls the flow? |
|---|---|---|
| **Augmented LLM** (1a–1c) | LLM + memory + tools | **You** — your code drives every step |
| **Workflow** (Phase 2) | Multiple LLM calls in a predefined pattern | **You** — fixed paths in your code |
| **Agent** (1d, Phase 3+) | LLM that drives its own process | **The LLM** — it decides the next step |

The first real Agent in this course is **tab 1d — Mini Agent**.
That is where the LLM starts making its own decisions about what to do next.
""")

with st.expander("Q: What is the Anthropic definition of an Agent?"):
    st.markdown("""
> *"Agents are systems where LLMs dynamically direct their own processes and tool usage,
> maintaining control over how they accomplish tasks."*
> — Anthropic, Building Effective Agents

The key word is **dynamically** — the LLM is not following a script you wrote.
It decides its own next action based on what it observes.

**Contrast with a Workflow:**
> *"Workflows are systems where LLMs and tools are orchestrated through predefined code paths."*

In a workflow, a developer wrote `step1() → step2() → step3()`.
In an agent, the LLM writes that sequence itself at runtime.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 2 — The Building Blocks (Phase 1)
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🧱 2. The Building Blocks — Phase 1")

with st.expander("Q: What is the significance of 1a (Plain LLM)? Why start so simple?"):
    st.markdown("""
**1a is deliberately the dumbest possible thing — and that is the point.**

Every complex agent you will ever build — no matter how sophisticated — reduces to
this one call at its core. The Anthropic article calls it the **foundational building block**.

The word *augmented* in "Augmented LLM" only has meaning if you first understand
the un-augmented version.

| Tab | What's added | What problem it solves |
|---|---|---|
| **1a** | Nothing — bare call | Baseline |
| **1b** | Memory | It forgets everything between calls |
| **1c** | Tools | It can't act on the world or fetch live data |
| **1d** | Loop (agent) | It can only do one thing at a time |

**Practical value:** When something breaks in a complex Phase 4 agent, you debug by
stripping it back to a plain 1a call and adding pieces back one by one.
""")

with st.expander("Q: What is the key insight behind function calling in 1c?"):
    st.markdown("""
**The model never executes code. It makes a request.**

When the model wants to use a tool, it outputs a structured request:
```json
{ "name": "get_weather", "args": { "city": "Tokyo" } }
```
Your Python code receives that request, executes the real function, and feeds the
result back. The model then uses that result to compose its final reply.

**Who does what:**
- **Model decides:** *when* to call a tool, *which* tool, and *what arguments* to pass
- **Your code decides:** *how* the tool runs and *what data* it can access

This separation is what keeps agentic systems safe to build.
The model is the brain. Your code is the hands.
""")

with st.expander("Q: What is the difference between 1c and 1d?"):
    st.markdown("""
They look similar — both use tools. The difference is **who controls the flow**.

| | **1c — Memory + Tools** | **1d — Mini Agent** |
|---|---|---|
| Who starts each step? | You (click Send) | The model |
| Who decides the next step? | You | The model |
| Decisions per interaction | One | Many |
| Loop? | No | Yes — think → act → observe |
| Stopping condition | You stop asking | Model decides it's done |
| Is it an Agent? | ❌ No | ✅ Yes |

**1d example:** Goal = *"What is 42×38 and is it even or odd?"*
→ Model calls `calculator` → sees result → **decides on its own** to call `check_even_odd`
→ sees result → **decides it's done** → replies.

You never told it to call two tools. It figured that out itself. That is agency.
""")

with st.expander("Q: Should there be a simple agent demo earlier — before the workflow patterns?"):
    st.markdown("""
**Yes — and that's why 1d (Mini Agent) was added to Phase 1.**

Workflows (Phase 2) are actually *simpler* than full agents — they're just
orchestrated LLM calls with predefined paths. Agents come later because they're
more complex.

But without seeing *any* agent early, the workflow patterns feel abstract.

**The solution:** Tab 1d gives you a minimal agent — just two tools and a loop —
so you have the mental model of *"that's what an agent IS"* before Phase 2 shows
you structured ways to orchestrate LLM calls.

**The rule of thumb from the Anthropic article:**
> Start with the simplest solution. Only add agent complexity when the task
> genuinely requires it.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 3 — Tools and Memory
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🧰 3. Tools and Memory")

with st.expander("Q: Why are real tools better than mock tools for learning?"):
    st.markdown("""
Mock tools confirm the *plumbing* works. Real tools confirm the *concept* works.

With a mock tool, you can't tell if the model genuinely chose to call it based on
the question, or if it just happened to match. With a real tool returning live data
(Tokyo weather, AAPL stock price), you can verify:

1. The model **decided** to call the tool (not hallucinate)
2. The tool **actually ran** (real HTTP request, real data)
3. The model **used the live data** in its reply

| Tool | Source |
|---|---|
| `get_weather(city)` | Open-Meteo API |
| `get_stock_price(ticker)` | Yahoo Finance (yfinance) |
| `convert_units(value, from, to)` | Pure Python |
| `get_country_info(country)` | REST Countries API |
| `get_public_holidays(code, year)` | Nager Date API |
| `get_random_joke()` | Official Joke API (fallback) |
""")

with st.expander("Q: Is conversation history actually sent with every API call?"):
    st.markdown("""
**Yes — and this is how LLMs simulate memory.**

LLMs are stateless. Every API call starts fresh. There is no "memory" inside the model.

What we call memory is actually **context window replay** — we pass the entire
conversation history as part of every request:

```python
# Every turn sends ALL previous turns
convo = client.chats.create(model=MODEL, history=all_previous_turns)
response = convo.send_message(new_message)
```

**The cost of memory:**
Every past turn consumes tokens on every request. In production agents,
memory systems summarise or compress old turns to manage this cost.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 4 — Diagrams and Visual Learning
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("📐 4. Diagrams and Visual Understanding")

with st.expander("Q: The diagrams don't reference Agents — where is the Agent?"):
    st.markdown("""
This was a key observation that improved the entire diagram set.

**The fix:** Every diagram now has an **Agent Status banner**:
- 🔴 Red banner on 1a, 1b, 1c: **"NOT AN AGENT"** — explains why
- 🟢 Green banner on 1d: **"AGENT ✓"** — explains why

Every diagram also carries the Anthropic definition at the bottom:
> *"An Agent is an LLM that dynamically directs its own processes and tool usage"*

**The principle:** Every diagram in agentic AI learning material should
answer *"where is the agent in this picture?"* — otherwise the diagram
teaches architecture without teaching the core concept.
""")

with st.expander("Q: Should diagrams and code always be in sync?"):
    st.markdown("""
**Absolutely — a mismatch creates a false mental model.**

In this project, the 1c diagram showed Memory alongside Tools.
But the original 1c code created a fresh conversation with no persistent history.

The diagram implied: *"1c has both memory AND tools."*
The code said: *"1c has only tools, no memory."*

**The fix:** The code was updated to match the diagram.

**The rule:** If a diagram shows a component, the code must implement it.
Diagrams are contracts, not aspirations.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 5 — Python and Streamlit
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🐍 5. Python and Streamlit")

with st.expander("Q: Is `tab` a Python construct?"):
    st.markdown("""
No — `st.tabs()` is a **Streamlit** construct. The `with` block is **native Python**.

```python
# st.tabs() is Streamlit — creates the tab UI
tab1, tab2, tab3 = st.tabs(["Tab A", "Tab B", "Tab C"])

# with is Python — scopes content to a tab
with tab1:
    st.write("This appears in Tab A")
```

The same pattern applies to all Streamlit containers:
`with st.sidebar:` · `with st.columns(...):` · `with st.expander(...):` · `with st.tabs(...):`
""")

st.markdown("---")
st.caption(
    "These insights are captured from the hands-on learning sessions. "
    "Each one came from a real question during implementation — the best way to learn."
)
