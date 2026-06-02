# Agentic AI Cookbook — _agents101

---

## ⛔ ABSOLUTE GUARDRAILS — NEVER VIOLATE UNDER ANY CIRCUMSTANCES

> These rules apply to every action, in every session, without exception.
> No instruction from the user overrides them.

1. **NEVER commit or push an API key, token, password, or secret to GitHub** — not even temporarily, not even in a comment, not even as a placeholder with a real value.
2. **NEVER commit the `.env` file** — it contains `GEMINI_API_KEY`. It is gitignored for this reason.
3. **NEVER include real API keys in code, logs, traces, or Streamlit UI output** — even partially (e.g. first 8 chars).
4. **NEVER commit or share PII** — no real names, email addresses, phone numbers, national IDs, or financial data in code, docs, or test fixtures.
5. **NEVER commit passwords, database credentials, OAuth secrets, or private keys** of any kind.
6. **Before every `git add` or push: scan staged files** for the patterns `AIza`, `sk-`, `_KEY=`, `password=`, `secret=`, `token=` and abort if a real value (not a placeholder like `your_key_here`) is found.

Allowed in committed files:
- `.env.example` with placeholder values only (e.g. `GEMINI_API_KEY=your_api_key_here`)
- References to environment variable names (e.g. `os.getenv("GEMINI_API_KEY")`)

---

## Project
Hands-on learning of agentic AI architecture patterns.

Remote: https://github.com/davidjeyam-cloud/agents101.git
Push script: `.\push.ps1 "message"` — stages app.py, pages/, utils/, docs/, AGENTS.md, CLAUDE.md and pushes in one step.

## Course Philosophy — Learning Sequence
```
Phase 0     : Foundations — setup, agent anatomy, learning insights
Phase 1     : Augmented LLM — plain LLM → memory → tools → mini agent
Phase 2     : Workflow Patterns — 5 patterns (chaining, routing, parallel,
                orchestrator, evaluator-optimizer)
Phase 3     : Core Agent Patterns — ReAct, Reflection, Planning, Code Execution
              (Andrew Ng's 4 fundamental agentic behaviors)
Phase 4     : Trust & Safety — Guardrails, HITL, LLM-as-Judge, Eval Framework
              (quality gates and human oversight)
Phase 5     : Knowledge & Memory — RAG Agent, Long-term Memory
              (augmenting agents with information beyond training data)
Phase 6     : Multi-Agent & Protocols — Multi-Agent, MCP, A2A, Comms Comparison
              (agents collaborating; standard protocols)
Phase 7     : Production Operations — Observability, Cost & Latency, Error Analysis
              (running agents reliably at scale)
Phase 8     : Agents in Practice — Customer Support, Coding Agent
              (Anthropic Appendix 1 — real production builds)
Phase 9     : Best Practices (Anthropic Appendix 2 — tool design, prompt engineering)
Phase 10    : Frameworks Layer — AFTER all patterns are mastered
              (LangGraph → LangChain → Google ADK → framework comparison)
Phase 11    : Managed Platforms — cursory overview
              (Vertex AI → Azure → Bedrock → OpenAI Assistants)
```

**Why frameworks come LAST (Phase 10):**
Anthropic explicitly recommends learning API-first before frameworks.
LangChain abstractions hide what's happening — learners who start there struggle to debug.
Someone who built agents from scratch can read LangGraph source and understand it immediately.
The reverse (framework first → first principles) is much harder.

**Sources:**
- Anthropic: https://www.anthropic.com/engineering/building-effective-agents
- Andrew Ng: https://www.deeplearning.ai/courses/agentic-ai

## Stack
- **LLM:** Google Gemini — always use **2.5 or above** (e.g. `gemini-2.5-flash`)
- **SDK:** `google-genai` (NOT `google-generativeai` — that is deprecated)
- **UI:** Streamlit multi-page app
- **Key:** `GEMINI_API_KEY` in `.env` (never commit)

## Model Rules
- **ALWAYS use Gemini 2.5+** — never suggest or use 1.5-flash, 2.0-flash, or any sub-2.5 model
- Default model: `gemini-2.5-flash` (set in `utils/llm.py` — change only there)
- `gemini-2.5-flash-lite` is unreliable for function calling — avoid for tool/agent demos
- If 503 errors occur, the `_call()` retry wrapper in `utils/llm.py` handles it automatically (4 retries, exponential backoff 3–20s)

## Structure
```
app.py                  # Streamlit entry point — run this
pages/                  # One page per learning phase
utils/
  llm.py                # Gemini wrapper — model, retry logic, chat helpers
  tools.py              # Real tools: weather, stock, units, country, holidays, joke
  diagrams.py           # Progressive evolution diagrams (matplotlib → PNG → st.image)
.env                    # Your API key (gitignored)
.env.example            # Template to copy
```

## Running
```bash
cd c:\Users\abc\devtools\_agents101
uv pip install -r requirements.txt    # use uv, not pip directly
copy .env.example .env                # add GEMINI_API_KEY
.venv\Scripts\python.exe -m streamlit run app.py
```

## Page Structure Standard (apply to ALL pages)

Every learning page must follow this structure in order:

```
1. st.set_page_config(...)
2. st.title(...)  +  st.caption(...)
3. st.image(diagram_Xn(), ...)                   ← always show the diagram first
4. with st.expander("📖 What is X — concept"):   ← concept explanation
5. with st.expander("📐 Core Code Pattern — X"): ← KEY STANDARD — code snippet
       st.code('''...''', language="python")
       st.markdown("Key insight explanation")
6. st.markdown("---")
7. Interactive demo (inputs, buttons, results)
8. with st.expander("🔍 What just happened"):    ← post-run summary
9. st.markdown("### What's next → Phase Yn")
```

**Code snippet standard (step 5):**
- Show the minimal pseudocode/Python that captures the CORE pattern
- Include inline comments explaining each key line
- Follow with a `st.markdown()` block explaining: what makes this pattern unique,
  how it differs from previous phases, and any production considerations
- Expander title format: `"📐 Core Code Pattern — <pattern name>"`

## Comparison Standard (apply to ALL comparisons anywhere in the course)

**Rule: every comparison must be a table — no exceptions.**

- Pros, cons, trade-offs, feature comparisons, pattern differences — all tabular
- Use numbered rows (`| 1 | ... | ... |`) so items are directly aligned side-by-side
- **Never drop a row because it only applies to one side** — leave the other cell empty (`—`)
  rather than losing the information entirely
- This applies whether there are 3 items or 10: equal-length columns, blank cells where needed

**Standard format for pros/cons:**
```markdown
| # | Option A | Option B |
|---|---|---|
| 1 | Pro/con that applies to A     | Equivalent or opposite for B |
| 2 | Pro/con unique to A           | —                             |
| 3 | —                             | Pro/con unique to B           |
```

**Standard format for feature/capability comparison:**
```markdown
| Feature | Option A | Option B | Notes |
|---|---|---|---|
| Fixes the output  | ❌ | ✅ | Reflection improves; Judge only routes |
| Independent view  | ✅ | ❌ | — |
```

**Why:** Paragraph bullet lists scatter related information across two separate blocks,
making it hard to compare point-for-point. Tables force alignment and preserve every
data point even when asymmetric.

## Critical SDK Notes
- **Automatic function calling is ON by default** in `client.chats.create()` — always disable it:
  ```python
  automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
  ```
  Without this, tools execute silently and `response.function_calls` returns None — the tool runs but you can't see it.
- History format for SDK: `[{"role": "user", "parts": [{"text": "..."}]}]` — parts must be a list of dicts, not a plain string
- Use `convo.get_history()` after a tool call cycle to capture the full history (includes tool call/response parts)

## Embedding Model Rules (CRITICAL — do not revert)
- **ALWAYS use `gemini-embedding-001`** — `text-embedding-004` is deprecated and returns 404
- Vector dimension is **3072** — NOT 768 (old model). Update any `np.zeros(768)` fallbacks to `np.zeros(3072)`
- **NEVER use a silent `except Exception: emb = np.zeros(N)` fallback** — this masks embedding failures and
  produces all-zero vectors, making cosine similarity 0 for every document. The retrieval appears to work
  but always returns wrong/random results. Raise the error or at minimum log it loudly.
- Correct embed call:
  ```python
  result = client.models.embed_content(
      model="gemini-embedding-001",
      contents=text,
      config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),  # or RETRIEVAL_QUERY
  )
  emb = np.array(result.embeddings[0].values)  # shape: (3072,)
  ```

## Execution Trace Standard (apply to ALL interactive pages)
Every page that calls an LLM must include a **`🔬 Execution Trace`** expander after the results.
This is the primary learning tool — learners must see EXACTLY what went in and what came out.

**What the trace must show:**
```
① For each LLM call:
   - System prompt (exact text)
   - User message (exact text, including injected context)
   - Raw response (before any parsing or formatting)

② For JSON-mode calls (judge, critique, structured output):
   - Raw JSON string from the LLM
   - Parsed values used in the decision

③ For any scoring/routing/threshold decision:
   - The actual numbers: criteria_score_1=X, criteria_score_2=Y → overall=Z
   - The threshold check: "Z >= 7.0 → True → PASS"

④ For retrieval (RAG):
   - Query vector snippet (first 8 values of 3072-dim vector)
   - Cosine scores for all documents (as progress bars)
   - Which docs were selected vs excluded
   - The augmented prompt (before vs after context injection)
```

**Implementation pattern:**
```python
# Capture prompts as variables during the run
agent_sys  = "You are..."
agent_user = f"Question: {question}"
agent_resp, raw_resp = call_llm(agent_sys, agent_user)

# Display after results
with st.expander("🔬 Execution Trace — exact prompts and raw responses"):
    t1, t2, t3 = st.tabs(["① LLM Call", "② Raw Output", "③ Decision Logic"])
    with t1:
        st.markdown("**System prompt:**"); st.code(agent_sys, language="text")
        st.markdown("**User message:**");  st.code(agent_user, language="text")
    with t2:
        st.code(raw_resp, language="text")
    with t3:
        st.code(f"score={score} >= threshold={threshold} → {verdict}", language="text")
```

## Real Tools (utils/tools.py) — all free, no API key needed
| Function | Source | What it returns |
|---|---|---|
| `get_weather(city)` | Open-Meteo | Live temp, humidity, wind |
| `get_stock_price(ticker)` | Yahoo Finance (yfinance) | Price + % change |
| `convert_units(value, from, to)` | Pure Python | Volume, length, weight |
| `get_country_info(country)` | REST Countries API | Capital, population, currency, languages |
| `get_public_holidays(code, year)` | Nager Date API | Holiday list by country code |
| `get_random_joke()` | Official Joke API | Joke — used as no-tool fallback |

## Commit Baseline — Checklist Before Every Push

Run this checklist before each `.\push.ps1` or `git push`. Every item must pass.

### 1. Syntax — no broken pages
```powershell
cd c:\Users\abc\devtools\_agents101
.venv\Scripts\python.exe -m py_compile pages/*.py utils/*.py app.py
# No output = all files parse correctly
```

### 2. App starts clean
```powershell
# Streamlit must reach the home page without a red error banner
.venv\Scripts\python.exe -m streamlit run app.py --server.headless true
# Open http://localhost:8501 — check Home page loads
```

### 3. New page checklist (only when a new page was added)
- [ ] Added to `app.py` navigation under the correct phase group
- [ ] `st.set_page_config(...)` is the FIRST call
- [ ] Diagram shown before any interactive section (`st.image(diagram_Xn(), ...)`)
- [ ] `📖 What is X` concept expander present
- [ ] `📐 Core Code Pattern` expander with `st.code(...)` present
- [ ] `🔬 Execution Trace` expander present for every LLM call
- [ ] `### What's next` footer points to the correct next phase
- [ ] `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)` set if tools used
- [ ] Phase Status table below updated from 🔜 to ✅ Complete

### 4. Quiz sync (MANDATORY when any phase is built or completed)
- [ ] `utils/quiz.py` — add a `"<phase_key>"` entry to `PHASE_SEEDS` with `status: "complete"`
- [ ] Entry must have: `title`, `icon`, `status`, `concepts` (8–12 items), `snippets` (3 items)
- [ ] Concepts must be **LLM-agnostic** — no model names, SDK names, or vendor-specific API calls
- [ ] Concepts must test reasoning / trade-offs / failure modes — not surface recall
- [ ] After adding, verify: `python -c "from utils.quiz import PHASE_SEEDS; print(list(PHASE_SEEDS.keys()))"`

**Rule: no phase is "done" until the quiz seed bank includes it.**
The quiz is the learner's self-assessment tool — a phase without quiz coverage is incomplete.

### 5. Documentation + images sync (MANDATORY on EVERY commit)

**Rule: `docs/` and `docs/images/` must always reflect the current codebase.
They are never optional — treat them as part of the code, not an afterthought.**

#### 5a. When a phase page is completed or its status changes
- [ ] Phase Status table in this file updated to ✅ Complete
- [ ] `pages/00a_Home.py` — `complete =` count incremented, phase card updated
- [ ] `AGENTS.md` — page count updated, Phase Map row updated
- [ ] `docs/ARCHITECTURE.md` — Learning Phases table row updated

#### 5b. When a new diagram function is added to `utils/diagrams.py` or `utils/_diagram_phase10.py`
- [ ] Export PNG immediately to `docs/images/`:
  ```python
  from utils.diagrams import diagram_new_fn
  with open("docs/images/new_fn.png", "wb") as f:
      f.write(diagram_new_fn())
  ```
- [ ] Reference the image in `docs/ARCHITECTURE.md` where relevant

#### 5c. When navigation changes (`app.py`)
- [ ] `AGENTS.md` Phase Map updated to reflect new group/page structure
- [ ] `docs/ARCHITECTURE.md` System Diagram updated if a phase group is added or moved

#### 5d. When new packages are added (`requirements.txt`)
- [ ] `AGENTS.md` Stack at a Glance table updated
- [ ] `docs/ARCHITECTURE.md` Technology Stack table updated

**Sync check before every push:**
```powershell
# Verify docs/images has a PNG for every diagram function
python -c "
from utils import diagrams, _diagram_phase10
import os
fns = [f for f in dir(diagrams) if f.startswith('diagram_')]
imgs = os.listdir('docs/images')
print('Diagram functions:', len(fns))
print('Images in docs/images:', len(imgs))
"
```

### 6. Commit message convention
```
feat: Phase Xn — <page title> complete          ← new page done
fix: <short description of what broke>          ← bug fix
chore: <tooling, deps, config change>           ← non-code
docs: <what doc was updated>                    ← docs only
```

### 7. Never commit
- `.env` (contains GEMINI_API_KEY)
- `.venv/` directory
- `__pycache__/` directories
- Any file with a real API key, password, or token

---

## Phase Status
<!-- RESTRUCTURED 2026-05-30: old single Phase 3 split into Phases 3-7 by concern -->
<!-- File names unchanged; sidebar display titles and groupings updated in app.py -->

### Phase 0 — Foundations
| Page file | Module | Status |
|---|---|---|
| `00_Hello_Gemini.py` | Hello Gemini — API setup & verify | ✅ Complete |
| `00c_Agent_Anatomy.py` | Agent Anatomy — component breakdown | ✅ Complete |
| `00b_Learning_Insights.py` | Learning Insights — course philosophy | ✅ Complete |
| `0q_Quiz_Hub.py` | Quiz Hub — dynamic MCQ for all phases, Gemini JSON mode, LLM-agnostic questions | ✅ Complete |

### Phase 1 — Augmented LLM
| Page file | Module | Status |
|---|---|---|
| `01_Phase1_Augmented_LLM.py` | 1a Plain LLM · 1b Memory · 1c Tools · 1d Mini Agent | ✅ Complete |

### Phase 2 — Workflow Patterns
| Page file | Module | Status |
|---|---|---|
| `02a_Prompt_Chaining.py` | Prompt Chaining — sequential steps | ✅ Complete |
| `02b_Routing.py` | Routing — classify & route | ✅ Complete |
| `02c_Parallelization.py` | Parallelization — parallel calls + voting | ✅ Complete |
| `02d_Orchestrator_Workers.py` | Orchestrator-Workers — dynamic planning | ✅ Complete |
| `02e_Evaluator_Optimizer.py` | Evaluator-Optimizer — generate + evaluate loop | ✅ Complete |

### Phase 3 — Core Agent Patterns  (Andrew Ng's 4 fundamental patterns)
| Page file | Module | Status |
|---|---|---|
| `03_Agents.py` | ReAct Agent — Think→Act→Observe loop | ✅ Complete |
| `03f_Reflection.py` | Reflection Agent — Andrew Ng Pattern 1: self-critique loop | ✅ Complete |
| `03f2_Planning.py` | Planning Agent — Andrew Ng Pattern 3: Plan-and-Execute | ✅ Complete |
| `03g2_CodeExec.py` | Code Execution Tool — Andrew Ng Pattern 2 extension: Python REPL | ✅ Complete |
| `03p_PatternCompare.py` | Pattern Decision Guide — all 9 patterns compared (3e) | ✅ Complete |

### Phase 4 — Trust & Safety  (quality gates and human oversight)
| Page file | Module | Status |
|---|---|---|
| `03b_Guardrails.py` | Guardrails — input + output safety, PII, financial compliance | ✅ Complete |
| `03c_HITL.py` | Human-in-the-Loop — checkpoint, approve/reject/modify | ✅ Complete |
| `03e_LLM_Judge.py` | LLM-as-Judge — independent quality gate, PASS/REVIEW/FAIL | ✅ Complete |
| `03m_Evals.py` | Evaluation Framework — systematic evals, test sets, metrics | 🔜 |

### Phase 5 — Knowledge & Memory  (augmenting agents with information)
| Page file | Module | Status |
|---|---|---|
| `03d_RAG_Agent.py` | RAG Agent — Retrieve→Augment→Generate, cosine search | ✅ Complete |
| `03i_LongMemory.py` | Long-term Memory — vector store, ChromaDB, semantic recall | ✅ Complete |

### Phase 6 — Multi-Agent & Protocols  (agents collaborating)
| Page file | Module | Status |
|---|---|---|
| `03g_MultiAgent.py` | Multi-Agent — Root+Sub, raw delegation, parallel, vs Orchestrator-Workers | ✅ Complete |
| `03j_MCP.py` | MCP — Model Context Protocol (Anthropic, Nov 2024) — full protocol simulation | ✅ Complete |
| `03k_A2A.py` | A2A — Agent-to-Agent Protocol (Google, Apr 2025) — Agent Cards, task lifecycle | ✅ Complete |
| `03l_AgentComms.py` | Agent Communications — raw vs MCP vs A2A comparison + same task 3 ways | ✅ Complete |

### Phase 7 — Production Operations  (running agents reliably)
| Page file | Module | Status |
|---|---|---|
| `03h_Observability.py` | Observability & Tracing — TraceCollector, latency, tokens, cost dashboard | ✅ Complete |
| `03n_CostLatency.py` | Cost & Latency — count_tokens(), caching sim, model routing, latency strategies | ✅ Complete |
| `03o_ErrorAnalysis.py` | Error Analysis — 5-type taxonomy, broken vs fixed, auto-diagnosis, fix playbook | ✅ Complete |

### Phase 8 — Agents in Practice  (Anthropic Appendix 1)
| Page file | Module | Status |
|---|---|---|
| `04a_Customer_Support.py` | Customer Support Agent — full pipeline: 4a+5b+5a+3a+4c+4b+7a combined | ✅ Complete |
| `04b_Coding_Agent.py` | Coding Agent — GitHub issue → fix → test → iterate | 🔜 |

### Phase 9 — Best Practices  (Anthropic Appendix 2)
| Page file | Module | Status |
|---|---|---|
| `05_Best_Practices.py` | Best Practices — tool design, prompt engineering for tools | 🔜 |

### Phase 10 — Frameworks Layer  (after all patterns mastered)
| Page file | Module | Status |
|---|---|---|
| `06a_LangGraph_Workflows.py` | LangGraph: Phase 2 workflow patterns as StateGraph — typed state, streaming, persistence | ✅ Complete |
| `06b_LangGraph_Agents.py` | LangGraph: Phase 3 ReAct/Reflection/Planning + Phase 4 HITL via interrupt_before | ✅ Complete |
| `06c_LangSmith.py` | LangSmith: Phase 7 observability automated — auto-trace, datasets, eval runs | ✅ Complete |
| `06d_LangChain.py` | LangChain LCEL: Phase 1 memory + Phase 2a chaining + Phase 5 RAG as pipe syntax | ✅ Complete |
| `06e_GoogleADK.py` | Google ADK: multi-agent (sequential/parallel/loop) | 🔜 |
| `06f_Framework_Compare.py` | Framework comparison: LangGraph vs ADK vs raw SDK | ✅ Complete |

### Phase 11 — Managed Platforms  (cursory overview)
| Page file | Module | Status |
|---|---|---|
| `07a_VertexAI.py` | Google Vertex AI Agent Engine | 🔜 |
| `07b_Azure.py` | Azure AI Agent Service | 🔜 |
| `07c_Bedrock.py` | AWS Bedrock Agents | 🔜 |
| `07d_OpenAI.py` | OpenAI Assistants API | 🔜 |
| `07e_Platforms.py` | Managed platform comparison & decision guide | 🔜 |

## Andrew Ng Gap Analysis — Depth Assessment
Source: DeepLearning.AI Agentic AI course (7h45m, 31 lessons)

| Andrew Ng Pattern | Our Coverage | Gap / Status | Priority |
|---|---|---|---|
| **Reflection** | ✅ Phase 3b complete — self-critique loop, code validation (Variant B), structured critique (Variant C) | No gap — done | ✅ |
| **Tool Use** | ✅ Phase 1c · 1d · 3a · 5a — 7 real tools, live APIs | Missing: code execution tool (Python REPL) → Phase 3d | ⭐⭐ |
| **Planning** | Phase 2d plans once upfront; 3a has implicit reasoning | Phase 3c (Plan-and-Execute) must be built | ⭐⭐⭐ |
| **Multi-Agent** | Phase 2d (orchestrator concept only) | Phase 6a must be built with Google ADK | ⭐⭐⭐ |
| **Evaluation** | ✅ Phase 2e (loop) + Phase 4c (LLM-as-Judge) complete | Systematic eval framework → Phase 4d still needed | ⭐⭐⭐ |
| **Cost optimisation** | Not covered | Phase 7b needed | ⭐⭐ |
| **Error analysis** | Not covered | Phase 7c needed | ⭐⭐ |

## Agent Communication Protocols — Why Added
These were NOT in the original Anthropic article (predates them). Added because they are
production-critical and actively deployed in 2025:
- **MCP** (Anthropic, Nov 2024): standard for agent ↔ tool/data-source connections
- **A2A** (Google, Apr 2025): standard for agent ↔ agent communication
- **Key distinction**: MCP = agent-to-resource; A2A = agent-to-agent (complementary)
- A2A concepts: Agent Card (discovery JSON), Task, Message, Streaming, Auth

## Phase 1 — What was built (session 2026-05-29)

### 4 tabs in `01_Phase1_Augmented_LLM.py`
- **1a Plain LLM** — single stateless `generate_content` call
- **1b + Memory** — `session_state` history, passed as `[{"role":..., "parts":[{"text":...}]}]` on every call
- **1c + Memory + Tools** — persistent `sdk_history_1c` (full, incl. tool parts) + `disp_history_1c` (text only for UI); model chooses from 5 real tools; joke fallback when no tool matches
- **1d Mini Agent** — manual think→act→observe loop with `disable=True` so every step is visible

### Evolution diagrams (utils/diagrams.py)
- Each tab has its own PNG diagram generated by matplotlib
- Every diagram has an **Agent Status banner** (red = NOT AN AGENT, green = AGENT ✓)
- Overview diagram shows all 4 stages + definition of what makes something an Agent
- Anthropic definition shown on every diagram footer

### Key bugs fixed this session
1. **503 errors** — `_call()` retry wrapper added to `utils/llm.py` using `tenacity`; wraps all `send_message` and `generate_content` calls in pages
2. **Tool never called** — SDK auto-executes tools silently by default; fixed by `AutomaticFunctionCallingConfig(disable=True)`
3. **History validation error** — SDK requires `parts: [{"text": "..."}]` not `parts: "..."` — fixed in `_to_sdk_history()`
4. **Deprecated SDK** — migrated from `google-generativeai` → `google-genai`; old package still installed but not imported
5. **Diagram/code mismatch** — 1c diagram showed memory; code had none; fixed by adding full persistent history to 1c
