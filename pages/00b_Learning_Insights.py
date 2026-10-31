"""
Learning Insights — Key Q&A from the learning journey.
Captures conceptual questions and answers across all phases.
"""

import streamlit as st
from utils.styles import phase_header, ACCENT_COMPLETE

st.set_page_config(page_title="Learning Insights", page_icon="💡", layout="wide")

st.markdown(phase_header(
    "Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Concepts",
    "💡 Learning Insights",
    "The <em>why</em> questions — concepts that matter most across the full course. "
    "Each answer came from a real question during implementation.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Table of contents ──────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#161B22;border:1px solid #21262D;border-radius:8px;
padding:16px 22px;margin-bottom:24px'>
  <div style='font-size:0.65rem;font-weight:700;letter-spacing:2px;
              text-transform:uppercase;color:#8B949E;margin-bottom:12px'>
    CONTENTS — 10 themes · 37 questions · All phases covered
  </div>
  <table style='width:100%;border-collapse:collapse;font-size:0.85rem'>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>1.&nbsp; 🤖 Agentic AI Fundamentals</td>
      <td style='padding:5px 0;color:#8B949E'>3 questions &nbsp;·&nbsp; Model-agnostic, agent definition, workflow vs agent</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>2.&nbsp; 🧱 Phase 1 — Augmented LLM</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; Plain LLM, function calling, 1c vs 1d, mini agent</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>3.&nbsp; 🔀 Phase 2 — Workflow Patterns</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; 5 patterns, when to use each, parallelism, orchestration</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>4.&nbsp; 🔄 Phase 3 — Core Agent Patterns</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; ReAct, Reflection, Planning, Code Execution (Andrew Ng)</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>5.&nbsp; 🛡️ Phase 4 — Trust &amp; Safety</td>
      <td style='padding:5px 0;color:#8B949E'>5 questions &nbsp;·&nbsp; Guardrails, HITL, LLM-as-Judge, Evals, EvalOps</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>6.&nbsp; 🧠 Phase 5 — Knowledge &amp; Memory</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; RAG, embeddings, vector stores, long-term memory</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>7.&nbsp; 🤝 Phase 6 — Multi-Agent &amp; Protocols</td>
      <td style='padding:5px 0;color:#8B949E'>5 questions &nbsp;·&nbsp; Multi-agent, MCP, A2A, ACP/ANP, protocol distinctions</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>8.&nbsp; 🏭 Phase 7 — Production Operations</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; Observability, cost, latency, error taxonomy</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>9.&nbsp; 🛠️ Phase 10 — Frameworks Layer</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; Why frameworks last, LangGraph, LangSmith, choosing a framework</td>
    </tr>
    <tr>
      <td style='padding:5px 12px 5px 0;color:#E6EDF3;font-weight:600'>10.&nbsp; 🐍 Tools, Memory &amp; Python</td>
      <td style='padding:5px 0;color:#8B949E'>4 questions &nbsp;·&nbsp; Real tools, context window memory, SDK gotchas, Streamlit</td>
    </tr>
  </table>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 1 — Agentic AI Fundamentals
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🤖 1. Agentic AI Fundamentals")

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

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 2 — Phase 1: Augmented LLM
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🧱 2. Phase 1 — Augmented LLM")

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

with st.expander("Q: What is the difference between 1c (Tools) and 1d (Mini Agent)?"):
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

with st.expander("Q: Why is a mini agent added to Phase 1 rather than waiting until Phase 3?"):
    st.markdown("""
Workflows (Phase 2) are actually *simpler* than full agents — they're just
orchestrated LLM calls with predefined paths. Agents come later because they're more complex.

But without seeing *any* agent early, the workflow patterns feel abstract.

**The solution:** Tab 1d gives you a minimal agent — just two tools and a loop —
so you have the mental model of *"that's what an agent IS"* before Phase 2 shows you
structured ways to orchestrate LLM calls.

**The rule of thumb from the Anthropic article:**
> Start with the simplest solution. Only add agent complexity when the task genuinely requires it.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 3 — Phase 2: Workflow Patterns
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🔀 3. Phase 2 — Workflow Patterns")

with st.expander("Q: When should I use a Workflow instead of a full Agent?"):
    st.markdown("""
**Default to Workflows. Only graduate to Agents when the task demands it.**

This is the core Anthropic recommendation. Workflows are:
- Predictable — the path through your code is fixed
- Debuggable — every step is visible and testable
- Cheaper — no extra reasoning loops

Use a full Agent only when the task genuinely requires the LLM to decide
*what to do next* based on intermediate results.

| Signal | Workflow | Agent |
|---|---|---|
| Steps known in advance | ✅ | — |
| Steps depend on intermediate output | — | ✅ |
| Deterministic output needed | ✅ | — |
| Open-ended exploration required | — | ✅ |
| Latency/cost sensitive | ✅ | — |
""")

with st.expander("Q: What is the most important insight about the 5 workflow patterns?"):
    st.markdown("""
**They solve different failure modes, not different task types.**

| Pattern | The failure mode it solves |
|---|---|
| **Prompt Chaining** | Single prompt tries to do too much at once — quality degrades |
| **Routing** | One-size-fits-all prompts handle every case the same way |
| **Parallelization** | Sequential calls where order doesn't matter — wastes latency |
| **Orchestrator-Workers** | You can't predict all sub-tasks upfront — hard-coded lists fail |
| **Evaluator-Optimizer** | First attempt is good enough — quality plateau |

Choosing the right pattern means identifying **what is breaking** in your naive approach,
not just matching your task description to a pattern name.
""")

with st.expander("Q: How does voting in the Parallelization pattern reduce hallucination?"):
    st.markdown("""
**Majority voting exploits the independence of parallel LLM calls.**

When you run the same question through 3 separate LLM calls:
- If the model is confident about the answer, all 3 agree → high confidence result
- If the model is uncertain, calls diverge → you detect uncertainty rather than pick one answer

```python
# 3 independent calls — same question, no shared state
results = [llm(question) for _ in range(3)]
# Majority vote or aggregation
answer = Counter(results).most_common(1)[0][0]
```

This works because LLM hallucinations are often inconsistent — the same wrong answer
rarely comes up identically three times. Agreement signals reliability; disagreement
signals you should fall back to human review.
""")

with st.expander("Q: What is the difference between Orchestrator-Workers and Multi-Agent?"):
    st.markdown("""
They look similar but differ in **who plans vs who executes**:

| | Orchestrator-Workers (Phase 2) | Multi-Agent (Phase 6) |
|---|---|---|
| **Orchestrator** | One LLM that plans and delegates | A root agent that spawns sub-agents |
| **Workers** | Specialised LLM calls for sub-tasks | Fully autonomous sub-agents with their own tools |
| **Communication** | Orchestrator → Worker → back to orchestrator | Root → Sub-agent (sub-agent may spawn further agents) |
| **Autonomy of sub-units** | Workers just execute, no agency | Sub-agents can reason, loop, and make decisions |
| **When to use** | Dynamic sub-tasks, single coordinator | Tasks requiring independent agents collaborating |

**Rule of thumb:** If workers just *execute* delegated tasks → Orchestrator-Workers.
If workers need to *reason and decide* independently → Multi-Agent.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 4 — Phase 3: Core Agent Patterns (Andrew Ng)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🔄 4. Phase 3 — Core Agent Patterns (Andrew Ng's 4 Fundamentals)")

with st.expander("Q: What is the ReAct pattern and why does it matter?"):
    st.markdown("""
**ReAct = Reason + Act — interleaved thinking and tool use.**

The key insight is that reasoning *before* acting dramatically improves agent reliability.
Without the Thought step, agents jump to tool calls and often pick the wrong tool or arguments.

```
Thought: The user wants weather in Tokyo. I should call get_weather with city=Tokyo.
Action: get_weather(city="Tokyo")
Observation: {"temp": 28, "humidity": 65}
Thought: I have the data. I can answer now.
Final Answer: Tokyo is currently 28°C with 65% humidity.
```

**Why it matters:** The Thought trace is also your debug window.
You can read exactly what the agent *believed* at each step — invaluable in production.
""")

with st.expander("Q: How is Reflection different from a second LLM call?"):
    st.markdown("""
**Reflection is a second LLM call — but the critic has a different role than the generator.**

The key is **role separation**:
- **Generator** is told to produce output (optimistic, creative)
- **Critic** is told to find flaws (skeptical, rigorous)

Without role separation, asking the same model to critique its own output produces
shallow self-review. The model rationalises rather than critiques.

```python
draft = llm(system="You are a writer.", user=task)
critique = llm(system="You are a strict editor. Find all flaws.", user=draft)
revised = llm(system="You are a writer.", user=f"Original: {draft}\nCritique: {critique}\nRevise.")
```

**Andrew Ng's insight:** Even a single reflection loop significantly improves output quality.
Multiple iterations yield diminishing returns — 2–3 cycles is usually optimal.
""")

with st.expander("Q: Why does Planning (Plan-and-Execute) outperform ReAct for complex tasks?"):
    st.markdown("""
**Planning separates thinking from doing — preventing the agent from getting lost.**

In ReAct, the agent reasons one step at a time. For a 10-step task, it can drift:
each Thought only sees the immediate step, and the agent loses sight of the overall goal.

Plan-and-Execute solves this by front-loading all reasoning:

```
PLAN PHASE:  LLM outputs a full numbered plan (all steps upfront)
EXECUTE PHASE: Each step runs against the plan — agent always knows where it is
REPLAN TRIGGER: If a step fails, the planner revises the remaining steps
```

**When to use each:**
| | ReAct | Plan-and-Execute |
|---|---|---|
| Task length | Short (1–3 steps) | Long (4+ steps) |
| Steps predictable? | No | Partially |
| Needs full-plan audit? | No | Yes (compliance, HITL) |
""")

with st.expander("Q: What makes Code Execution (Python REPL) a fundamentally different tool?"):
    st.markdown("""
**Code execution is deterministic. All other tools are I/O. That is a qualitative difference.**

When an LLM calls `get_weather("Tokyo")`, it trusts an external API.
When it writes and executes Python, it *verifies* its own reasoning:

```python
# LLM writes this, REPL executes it, result fed back
code = "import math; result = math.sqrt(144); print(result)"
# Output: 12.0  ← deterministic, verifiable
```

**Why this matters:**
- Math errors are caught instantly (12 × 12 = 144, not 145)
- Data transformations are exact, not approximated
- The agent can iterate on its own code until the output is correct

**The danger:** The REPL can execute arbitrary code. Always sandbox.
Never run a code execution agent with filesystem or network access in production
without explicit containment.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 5 — Phase 4: Trust & Safety
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🛡️ 5. Phase 4 — Trust & Safety")

with st.expander("Q: Why must guardrails run on BOTH input AND output?"):
    st.markdown("""
**Input guardrails prevent bad instructions from reaching the LLM.
Output guardrails catch bad content the LLM generates despite good instructions.**

Neither alone is sufficient:

| Risk | Input guardrail | Output guardrail |
|---|---|---|
| Prompt injection ("ignore all instructions") | ✅ Catches | — |
| Jailbreak in disguised form | ✅ Catches | ✅ Catches (if it slips through) |
| Hallucinated financial advice | — | ✅ Catches |
| PII in generated text | — | ✅ Catches |
| Toxic output from benign input | — | ✅ Catches |

**The defence-in-depth rule:** Assume the input guardrail will sometimes fail.
The output guardrail is your last line of defence before the user sees the response.
""")

with st.expander("Q: When does Human-in-the-Loop (HITL) make sense, and when does it not?"):
    st.markdown("""
**HITL is the right call when the cost of an error exceeds the cost of a delay.**

| Trigger | Example | HITL? |
|---|---|---|
| Irreversible action | Delete customer record | ✅ Always |
| High financial value | Approve refund > £500 | ✅ Always |
| Sensitive data access | Read medical records | ✅ Always |
| Novel situation | First time this case pattern seen | ✅ Yes |
| Routine, reversible | Classify support ticket | ❌ No |
| High-volume, low-stakes | Auto-tag blog posts | ❌ No |

**The design principle:** Don't add HITL as a safety blanket. Each checkpoint adds latency
and human fatigue. Precisely target it at actions where the LLM's error rate ×
the cost of that error exceeds your acceptable risk threshold.
""")

with st.expander("Q: How is LLM-as-Judge different from Reflection?"):
    st.markdown("""
**Reflection is the agent critiquing itself. LLM-as-Judge is an independent evaluator.**

| | Reflection | LLM-as-Judge |
|---|---|---|
| Who critiques? | Same model, critic role | Separate model instance |
| Sees the same biases? | Yes (shared weights) | Potentially no (can use different model) |
| Purpose | Improve this output | Gate: pass / review / fail |
| Output | Revised draft | Score + verdict |
| Used for | Generation quality | Evaluation quality |

**The independence principle:** A judge that was involved in generating the output
cannot evaluate it objectively. In production, use a different model or at minimum
a fresh context with no knowledge of the generation process.
""")

with st.expander("Q: What is the most important rule about building an eval framework?"):
    st.markdown("""
**Build the test set BEFORE building the system — not after.**

This is the most commonly violated rule in ML engineering.

If you build the system first, you unconsciously tune it to pass whatever cases you can think of.
The eval then confirms your assumptions rather than testing them.

**The right order:**
1. Define success criteria (what does "good" look like?)
2. Collect golden examples (input → expected output)
3. Build the system
4. Run evals — score against the golden set
5. Improve and re-run

**Minimum viable eval set:** 20–50 examples covering normal cases, edge cases,
and known failure modes. Even 20 well-chosen examples catch more regressions
than 1000 randomly sampled ones.
""")

with st.expander("Q: What is pass@k and why does it matter for production eval?"):
    st.markdown("""
**pass@k measures whether your agent can produce at least one correct answer in k tries.**

This matters because LLMs are stochastic — the same prompt gives different outputs.

| Metric | What it measures | When to use |
|---|---|---|
| **pass@1** | First answer is correct | User-facing apps (no retries) |
| **pass@3** | At least 1 of 3 is correct | Systems that can sample and pick best |
| **pass@10** | At least 1 of 10 is correct | Research / capability assessment |

**The production implication:** A model with pass@1=0.6 and pass@3=0.9 may be
more useful with a sampling + judge architecture than a model with pass@1=0.8
in a single-shot system — depending on latency tolerance.

**The eval ops flywheel:** pass@k scores improve over time as you:
collect failures → fix prompts → re-eval → collect new failures → repeat.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 6 — Phase 5: Knowledge & Memory
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🧠 6. Phase 5 — Knowledge & Memory")

with st.expander("Q: What problem does RAG actually solve?"):
    st.markdown("""
**RAG solves knowledge cutoff and hallucination on private/recent information.**

LLMs are trained on data up to a cutoff date. They cannot know:
- Your company's internal documents
- Events after training cutoff
- Real-time data (prices, inventory, tickets)

RAG (Retrieve-Augment-Generate) solves this by:
1. **Retrieve** — find relevant documents from your corpus using semantic search
2. **Augment** — inject those documents into the LLM's context
3. **Generate** — LLM answers grounded in your actual documents

**The key insight:** The LLM doesn't need to *know* the answer. It needs to *read* it
from documents you provide at inference time. This is fundamentally more reliable than
asking it to recall from training.
""")

with st.expander("Q: Why is semantic similarity better than keyword search for retrieval?"):
    st.markdown("""
**Keyword search matches words. Semantic search matches meaning.**

"What is the refund policy?" will not keyword-match a document that says
"Customers may return items within 30 days for a full credit."

Embeddings convert both query and document into vectors in a high-dimensional space
where semantically similar content is geometrically close:

```python
# Query and document land near each other in 3072-dim space
query_vec  = embed("refund policy")       # → [0.12, -0.34, ...]
doc_vec    = embed("return items 30 days") # → [0.14, -0.31, ...]
similarity = cosine_similarity(query_vec, doc_vec)  # → 0.91 (high)
```

**The gotcha:** Silent embedding failures (returning zero vectors) make cosine similarity
0 for every document — retrieval appears to work but always returns random results.
Always validate embedding output shape and magnitude.
""")

with st.expander("Q: What is the difference between session memory and long-term memory?"):
    st.markdown("""
| | Session Memory (Phase 1b) | Long-term Memory (Phase 5b) |
|---|---|---|
| **Storage** | Python list in `st.session_state` | Vector database (ChromaDB) |
| **Lifetime** | Until browser tab closes | Persists across restarts |
| **Retrieval** | All of it, every time | Semantic search — only relevant parts |
| **Scale** | ~100 turns before context limit | Millions of entries |
| **Use case** | Current conversation | User preferences, past interactions, knowledge |

**The key insight:** Long-term memory is just RAG over your own past conversation history.
The architecture is identical — embed the memory, store in a vector DB, retrieve by similarity.
The only difference is *what* you embed (past turns vs documents).
""")

with st.expander("Q: Why does the embedding dimension (3072 vs 768) matter so much?"):
    st.markdown("""
**Using the wrong dimension produces all-zero fallback vectors — silent failure.**

When the model `gemini-embedding-001` returns 3072-dimensional vectors but your
fallback is `np.zeros(768)`, dimension mismatch means:

1. Cosine similarity computation silently fails or gives nonsense
2. Every retrieval returns the same "closest" document (by accident)
3. The app appears to work — results look plausible but are actually random

**The rule:** Never use a silent `except Exception: emb = np.zeros(N)` fallback.
This masks embedding failures and makes debugging nearly impossible.

```python
# Wrong — silent fallback hides the error
try:
    emb = embed(text)
except:
    emb = np.zeros(768)  # NEVER DO THIS

# Right — fail loudly
emb = embed(text)  # Let it raise; log the error clearly
```
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 7 — Phase 6: Multi-Agent & Protocols
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🤝 7. Phase 6 — Multi-Agent & Protocols")

with st.expander("Q: When does a multi-agent system outperform a single sophisticated agent?"):
    st.markdown("""
**Multi-agent wins when tasks are too large for a single context window,
or when independent perspectives reduce error.**

| Use case | Single agent | Multi-agent |
|---|---|---|
| Task fits in one context | ✅ Simpler | Overkill |
| Task requires 50+ tool calls | Context overflow | ✅ Parallelise across agents |
| Independent review needed | Self-review bias | ✅ Separate generator + reviewer |
| Specialised domains | One model does everything | ✅ Domain-specific sub-agents |
| Speed-critical parallel work | Sequential | ✅ Parallel sub-agents |

**The cost:** Multi-agent systems are harder to debug. When a task fails,
the error may be in the root agent, a sub-agent, their communication, or task decomposition.
Build single-agent first. Graduate to multi-agent only when you hit its limits.
""")

with st.expander("Q: What is MCP and what problem does it solve?"):
    st.markdown("""
**MCP (Model Context Protocol, Anthropic Nov 2024) standardises how agents connect to tools and data.**

Before MCP, every agent-tool integration was custom: different APIs, different auth,
different data formats. MCP is the USB-C of agentic AI — one standard connector.

```
Agent ←── MCP ──→ Tool Server (filesystem, database, API, IDE, browser)
```

**What MCP provides:**
- Standard JSON-RPC protocol for tool discovery and invocation
- Transport: stdio (local) or HTTP-SSE (remote)
- Tools, Resources (data sources), and Prompts (reusable templates)

**Key distinction — MCP is agent-to-resource, not agent-to-agent.**
An agent uses MCP to call a tool. It uses A2A to talk to another agent.
""")

with st.expander("Q: What is A2A and how does it complement MCP?"):
    st.markdown("""
**A2A (Agent-to-Agent Protocol, Google Apr 2025) standardises how agents talk to each other.**

| | MCP | A2A |
|---|---|---|
| **What connects** | Agent ↔ Tool/Resource | Agent ↔ Agent |
| **Discovery** | Server manifest | Agent Card (JSON file at /.well-known/agent.json) |
| **Transport** | stdio / HTTP-SSE | HTTP + Server-Sent Events + JSON-RPC |
| **Auth** | API keys / OAuth | OAuth 2.0 |
| **Task lifecycle** | Single call | submitted → working → completed / failed |

**They are complementary, not competing:**
An A2A sub-agent uses MCP to connect to its tools.
The root agent uses A2A to delegate to the sub-agent.

**The emerging stack:** Root Agent → A2A → Sub-Agent → MCP → Tool Server
""")

with st.expander("Q: What are ACP and ANP, and should I learn them now?"):
    st.markdown("""
**ACP and ANP are emerging protocols — watch but don't build on them yet.**

| Protocol | By | Focus | Status |
|---|---|---|---|
| **ACP** (Agent Communication Protocol) | BeeAI / IBM / Linux Foundation | REST-native agent comms; simpler than A2A | Early adoption |
| **ANP** (Agent Network Protocol) | Open community | Decentralised P2P agent discovery via DID | Experimental |

**ACP** is designed to complement MCP: where MCP handles tool connections,
ACP handles agent-to-agent communication over plain REST (no SSE required).

**ANP** takes a decentralised approach — agents discover each other via
Decentralised Identifiers (DIDs) rather than a central registry.

**For production today:** MCP + A2A are the two that matter.
ACP and ANP are worth monitoring for 2026–2027 standardisation.
""")

with st.expander("Q: Why do agent communication protocols matter — can't agents just use REST?"):
    st.markdown("""
**They CAN use plain REST. Protocols matter when you need interoperability at scale.**

A custom REST integration works when you control both ends.
It breaks when:
- You want to swap out an agent from a different vendor
- A third-party tool wants to expose itself to any agent (not just yours)
- You need standard auth, error codes, and streaming across vendors

**The USB analogy again:** Every device had proprietary chargers until USB standardised.
MCP and A2A do for agent integrations what USB did for hardware connections —
any MCP-compatible tool works with any MCP-compatible agent, from any vendor.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 8 — Phase 7: Production Operations
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🏭 8. Phase 7 — Production Operations")

with st.expander("Q: What is the minimum viable observability setup for a production agent?"):
    st.markdown("""
**Three things: trace ID, latency, and cost per request.**

Without these you cannot answer: *"Why did this request fail?"* or *"Why did costs spike?"*

| Signal | What it tells you | How to capture |
|---|---|---|
| **Trace ID** | Which request failed (correlates across logs) | Generate UUID at request start |
| **Latency per step** | Where time is spent (LLM call, tool, retrieval) | Timestamp before/after each step |
| **Token count + cost** | Cost per user, per task type | `client.models.count_tokens()` + model pricing |
| **Tool call outcome** | Which tools succeed/fail | Wrap every tool call in try/except + log |

**The observability payoff:** Once you have traces, a spike in cost becomes
*"Tool X is being called 10× per request instead of 1×"* — actionable in minutes,
not days of log archaeology.
""")

with st.expander("Q: What are the most effective cost reduction strategies for LLM agents?"):
    st.markdown("""
**In order of impact (highest ROI first):**

1. **Prompt caching** — cache system prompts that don't change per request.
   Can cut 60–80% of input token cost for long system prompts.

2. **Model routing** — use a smaller/cheaper model for simple tasks,
   reserve the large model for complex reasoning.
   ```python
   model = "gemini-2.5-flash-lite" if is_simple(task) else "gemini-2.5-flash"
   ```

3. **Context compression** — summarise old conversation turns rather than
   sending the full history every time.

4. **Tool output truncation** — tool results can be verbose (e.g. full API response).
   Extract only what the agent needs before feeding back.

5. **Early stopping** — detect "I don't need more steps" in the agent loop
   rather than always running to max_iterations.
""")

with st.expander("Q: What are the 5 error types in production agents and how do you fix each?"):
    st.markdown("""
| Error type | Example | Fix |
|---|---|---|
| **LLM refusal** | Model refuses a valid request | Rewrite system prompt; reduce sensitive framing |
| **Tool failure** | API timeout, 404, wrong args | Retry with backoff; validate args before call |
| **Format error** | JSON parse fails on LLM output | Use structured output / JSON mode; add schema validation |
| **Context overflow** | History too long for context window | Compress history; use summarisation |
| **Loop / no-progress** | Agent repeats same action | Add max_iterations; detect repeat action in loop |

**The meta-lesson:** Each error type needs a *different* fix strategy.
Treating all errors as "the LLM made a mistake" leads to prompt-tweaking
that doesn't address the root cause.
""")

with st.expander("Q: Why can't you just add retries to fix agent errors?"):
    st.markdown("""
**Retries fix transient failures. They worsen systematic failures.**

If a tool times out occasionally → retry with backoff → ✅ correct fix.

If the LLM consistently generates malformed JSON → retry → same bad JSON × 3,
then fail more expensively and with more latency.

**The retry decision tree:**
```
Is the error deterministic?
├── Yes (same input → same bad output) → Fix the root cause, not the retry count
└── No (flaky network, 503, rate limit) → Retry with exponential backoff is correct
```

**The `_call()` wrapper in `utils/llm.py`** uses tenacity with 4 retries and
3–20s exponential backoff — appropriate for the 503 transient failures from
overloaded Gemini endpoints, not for logic errors.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 9 — Phase 10: Frameworks Layer
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🛠️ 9. Phase 10 — Frameworks Layer")

with st.expander("Q: Why do frameworks come LAST — after all patterns are mastered?"):
    st.markdown("""
**This is the Anthropic recommendation, and it is counterintuitive.**

Most people want to start with LangChain or LangGraph because they feel productive faster.
The problem: frameworks hide what is happening.

- A LangGraph `StateGraph` is a workflow orchestrator — but if you haven't built one from scratch,
  you don't know what the framework is saving you from.
- A LangChain RAG chain is just embed → search → inject → generate —
  but if you haven't built that loop manually, debugging a chain failure is opaque.

**The test:** Can you read LangGraph source code and understand it?
If you built the Phase 2–5 patterns by hand, yes. If you started with LangGraph, usually no.

**The reward for learning order:** When LangGraph's checkpointer fails in production,
you debug it as a persistence mechanism, not a black box. Framework-first learners
typically restart from scratch or give up.
""")

with st.expander("Q: What does LangGraph add that a raw Phase 3 agent loop doesn't have?"):
    st.markdown("""
**LangGraph adds type-safe state, persistence, streaming, and a visualisable graph structure.**

| Feature | Raw agent loop | LangGraph StateGraph |
|---|---|---|
| State schema | Python dict (no validation) | TypedDict with type checking |
| Persistence | None (lost on crash) | Checkpointer (SQLite / Postgres / Redis) |
| Streaming | Manual print statements | `.stream()` with event types |
| Visualisation | None | `draw_mermaid_png()` — literal graph diagram |
| Human-in-the-loop | Custom flag + pause logic | `interrupt()` + `Command(resume=...)` |
| Multi-thread | Manual | Thread ID scoping built in |

**When LangGraph is worth it:** When you need persistence across crashes,
streaming for real-time UI, or graph visualisation for debugging complex flows.
For simple agents, the overhead is not justified.
""")

with st.expander("Q: LangGraph vs CrewAI vs Google ADK — how do I choose?"):
    st.markdown("""
| Framework | Best for | Avoid when |
|---|---|---|
| **LangGraph** | Fine-grained control, custom state machines, production hardening | You want a quick setup; you're not using LangChain ecosystem |
| **CrewAI** | Role-based crews where human org structure maps to agent structure | You need dynamic sub-task planning; high-volume production |
| **Google ADK** | Google Cloud native, Vertex AI integration, multi-agent pipelines | You're not on GCP; you need cross-cloud portability |
| **Raw SDK** | Learning, prototyping, full control, no dependency overhead | You need persistence, streaming, multi-thread out of the box |

**The honest answer:** For most production systems, LangGraph + LangSmith is the
most battle-tested open-source choice. CrewAI is excellent for role-based simulations.
ADK wins if you're already in the Google Cloud ecosystem.
""")

with st.expander("Q: What does LangSmith add to a production LangGraph deployment?"):
    st.markdown("""
**LangSmith is the observability layer that LangGraph itself doesn't provide.**

LangGraph traces execution but doesn't store, query, or alert on it.
LangSmith fills that gap:

| Capability | LangGraph | LangSmith |
|---|---|---|
| Execution tracing | ✅ (in-process) | ✅ (stored, queryable) |
| Token cost tracking | ❌ | ✅ |
| Prompt versioning | ❌ | ✅ (Prompt Hub) |
| Dataset + eval runs | ❌ | ✅ |
| User feedback capture | ❌ | ✅ (thumbs up/down API) |
| Alerts on regressions | ❌ | ✅ |

**Auto-tracing:** Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY=ls-...`
and every LangGraph run is automatically captured. No code changes needed.

**The pairing:** LangGraph for the agent, LangSmith for the operations layer.
They're designed as a pair — not competitors.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Theme 10 — Tools, Memory & Python Gotchas
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🐍 10. Tools, Memory & Python Gotchas")

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

with st.expander("Q: What is the most dangerous SDK default in the Gemini google-genai SDK?"):
    st.markdown("""
**Automatic function calling is ON by default — and it silently hides tool calls.**

When you create a chat with tools and don't explicitly disable auto-execution:

```python
# DANGEROUS default behaviour
convo = client.chats.create(model=MODEL, config={"tools": [my_tools]})
response = convo.send_message("What's the weather in Tokyo?")
# response.function_calls → None  (tool ran but you can't see it happened)
```

The tool executes silently. `response.function_calls` returns `None`.
From the code's perspective, it looks like the model answered directly.

**The fix — always set this:**
```python
config=types.GenerateContentConfig(
    tools=[my_tools],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)
```

Without this, every tool-use demo in this course would appear to work while actually
bypassing the learning objective (seeing the Think→Act→Observe loop).
""")

with st.expander("Q: Is `tab` a Python construct? What about `with`?"):
    st.markdown("""
`st.tabs()` is a **Streamlit** construct. The `with` block is **native Python**.

```python
# st.tabs() is Streamlit — creates the tab UI
tab1, tab2, tab3 = st.tabs(["Tab A", "Tab B", "Tab C"])

# with is Python — scopes content to a tab
with tab1:
    st.write("This appears in Tab A")
```

The same pattern applies to all Streamlit containers:
`with st.sidebar:` · `with st.columns(...):` · `with st.expander(...):` · `with st.tabs(...):`

**Deeper Python note:** `with` invokes the context manager protocol (`__enter__` / `__exit__`).
Streamlit containers implement this protocol to route `st.*` calls to the correct UI region.
""")

st.markdown("---")
st.caption(
    "These insights are captured from the hands-on learning sessions across all phases. "
    "Each one came from a real question during implementation — the best way to learn. "
    "10 themes · 37 questions · Phases 0–10."
)
