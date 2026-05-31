"""
Learning Insights — Key Q&A from the learning journey.
Captures conceptual questions and answers (not bug fixes or API issues).
"""

import streamlit as st

st.set_page_config(page_title="Learning Insights", page_icon="💡", layout="wide")
st.title("💡 Learning Insights")
st.caption("Key questions and answers from the learning journey — the concepts that matter most.")

st.markdown("""
> These are the *why* questions — the ones that build understanding, not just working code.
> Each answer is something worth remembering as you progress through the phases.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 1 — What is Agentic AI?
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🤖 What is Agentic AI?")

with st.expander("Q: Do I need the Anthropic API specifically to learn Agentic AI?"):
    st.markdown("""
**No — and this is an important first principle.**

The architectural patterns in the Anthropic article — prompt chaining, routing,
parallelization, orchestrator-workers, evaluator-optimizer, and agents — are
**100% model-agnostic**. They work with any LLM: Gemini, Claude, GPT, Llama, or any other.

This project uses **Gemini 2.5 Flash** (Google AI Studio, free tier) with no loss of learning value.

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

The first time you see a real Agent in this course is **tab 1d — Mini Agent**.
That's where the LLM starts making its own decisions about what to do next.

Phases 4a and 4b (Customer Support Agent, Coding Agent) are where full production-style agents appear.
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

st.subheader("🧱 The Building Blocks — Phase 1")

with st.expander("Q: What is the significance of 1a (Plain LLM)? Why start so simple?"):
    st.markdown("""
**1a is deliberately the dumbest possible thing — and that is the point.**

```
User Input → [ LLM ] → Output
```

No memory. No tools. No loop. Just text in, text out.

**Why this matters for Agentic AI:**

Every complex agent you will ever build — no matter how sophisticated — reduces to
this one call at its core. The Anthropic article calls it the **foundational building block**.

The word *augmented* in "Augmented LLM" only has meaning if you first understand
the un-augmented version.

**The progression:**

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

**Why this matters for safety:**
This separation is what keeps agentic systems safe to build. The model is the brain.
Your code is the hands. The model cannot do anything your code doesn't allow it to do.

**The Google SDK gotcha learned here:**
By default, the SDK executes tool calls *automatically and silently*. The tool runs
but `response.function_calls` returns `None`. Always disable this:
```python
automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
```
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
| Memory between turns? | ✅ Yes | ❌ No (each run independent) |
| Is it an Agent? | ❌ No | ✅ Yes |

**The clearest example:**

**1c** — you ask *"What's the weather in Tokyo?"*
→ Model calls `get_weather` once → replies → waits for you

**1d** — you give the goal *"What is 42×38 and is it even or odd?"*
→ Model calls `calculator` → sees result → **decides on its own** to call `check_even_odd`
→ sees result → **decides it's done** → replies

You never told it to call two tools. It figured that out itself. That is agency.
""")

with st.expander("Q: Should there be a simple agent demo earlier — before the workflow patterns?"):
    st.markdown("""
**Yes — and that's why 1d (Mini Agent) was added to Phase 1.**

The original Anthropic article order is:
```
Augmented LLM → Workflows → Agents
```

Workflows (Phase 2) are actually *simpler* than full agents — they're just
orchestrated LLM calls with predefined paths. Agents come later because they're
more complex.

But without seeing *any* agent early, the workflow patterns feel abstract.

**The solution:** Tab 1d gives you a minimal agent — just two tools and a loop —
so you have the mental model of *"that's what an agent IS"* before Phase 2 shows
you structured ways to orchestrate LLM calls.

**The rule of thumb from the Anthropic article:**
> Start with the simplest solution. Only add agent complexity when the task
> genuinely requires it. Many tasks that seem to need agents can be solved
> with well-designed workflows.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 3 — Tools and Memory
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🧰 Tools and Memory")

with st.expander("Q: Why are real tools better than mock tools for learning?"):
    st.markdown("""
Mock tools confirm the *plumbing* works. Real tools confirm the *concept* works.

With a mock tool, you can't tell if the model genuinely chose to call it based on
the question, or if it just happened to match. With a real tool returning live data
(Tokyo weather, AAPL stock price), you can verify:

1. The model **decided** to call the tool (not hallucinate)
2. The tool **actually ran** (real HTTP request, real data)
3. The model **used the live data** in its reply

The tools built in this project (all free, no extra API keys):

| Tool | Source |
|---|---|
| `get_weather(city)` | Open-Meteo API |
| `get_stock_price(ticker)` | Yahoo Finance (yfinance) |
| `convert_units(value, from, to)` | Pure Python |
| `get_country_info(country)` | REST Countries API |
| `get_public_holidays(code, year)` | Nager Date API |
| `get_random_joke()` | Official Joke API (fallback) |

**The joke fallback is a deliberate design pattern** — when no tool applies,
your code (not the model) decides what to do. This is the agent safety principle:
you stay in control of every action.
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

**The history format the SDK requires:**
```python
[
    {"role": "user",  "parts": [{"text": "What is the capital of France?"}]},
    {"role": "model", "parts": [{"text": "Paris."}]},
    {"role": "user",  "parts": [{"text": "What language do they speak?"}]},
]
```
Note: `parts` must be a **list of dicts**, not a plain string.

**The cost of memory:**
Every past turn consumes tokens on every request. In production agents,
memory systems summarise or compress old turns to manage this cost.
This is an active area of agentic AI design.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 4 — Diagrams and Visual Learning
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("📐 Diagrams and Visual Understanding")

with st.expander("Q: The diagrams don't reference Agents — where is the Agent?"):
    st.markdown("""
This was a key observation that improved the entire diagram set.

**The original diagrams** showed the technical components (LLM, memory, tools, loop)
but didn't explicitly connect them to the concept of an Agent.

**The fix:** Every diagram now has an **Agent Status banner**:
- 🔴 Red banner on 1a, 1b, 1c: **"NOT AN AGENT"** — explains why
- 🟢 Green banner on 1d: **"AGENT ✓"** — explains why

Every diagram also carries the Anthropic definition at the bottom:
> *"An Agent is an LLM that dynamically directs its own processes and tool usage"*

**The principle:** In any agentic AI learning material, every diagram should
answer the question *"where is the agent in this picture?"* — otherwise the
diagram teaches architecture without teaching the core concept.
""")

with st.expander("Q: Should diagrams and code always be in sync?"):
    st.markdown("""
**Absolutely — a mismatch creates a false mental model.**

In this project, the 1c diagram showed Memory (from 1b) alongside Tools.
But the original 1c code created a fresh conversation on every button click
with no persistent history.

The diagram implied: *"1c has both memory AND tools."*
The code said: *"1c has only tools, no memory."*

**The fix:** The code was updated to match the diagram — 1c now maintains
`session_state` history across turns, exactly as the diagram showed.

**The rule:** If a diagram shows a component, the code must implement it.
If the code doesn't implement it, the diagram must not show it.
Diagrams are contracts, not aspirations.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 5 — Python and Streamlit
# ══════════════════════════════════════════════════════════════════════════════

st.subheader("🐍 Python and Streamlit Concepts")

with st.expander("Q: Is `tab` a Python construct?"):
    st.markdown("""
No — `st.tabs()` is a **Streamlit** construct. The `with` block is **native Python**.

```python
# st.tabs() is Streamlit — creates the tab UI
tab1, tab2, tab3 = st.tabs(["Tab A", "Tab B", "Tab C"])

# with is Python — scopes content to a tab
with tab1:
    st.write("This appears in Tab A")

with tab2:
    st.write("This appears in Tab B")
```

**The `with` statement** is Python's context manager protocol.
Streamlit uses it as a clean way to say *"everything inside this block
belongs to this container."*

The same pattern applies to all Streamlit containers:
- `with st.sidebar:` — puts content in the sidebar
- `with st.columns(...):` — puts content in a column
- `with st.expander(...):` — puts content in an expandable section
- `with st.tabs(...):` — puts content in a tab
""")

st.markdown("---")
st.markdown("""
*These insights are captured from the hands-on learning sessions.
Each one came from a real question during implementation — the best way to learn.*
""")
