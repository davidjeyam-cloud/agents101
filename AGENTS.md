# Agentic AI Cookbook — _agents101

> Canonical project index (wshobson/agents pattern — 150-line canonical entry point).  
> Read this before anything else. Deep detail lives in `docs/` and `CLAUDE.md`.

---

## What This Is

A hands-on, self-paced agentic AI learning curriculum built as a **Streamlit multi-page app**.
Each page is a live interactive demo of one architectural pattern. Learners run real agents —
they don't just read about them.

**Primary sources:**
- Anthropic: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Andrew Ng: [DeepLearning.AI Agentic AI course](https://www.deeplearning.ai/courses/agentic-ai)

---

## Quick Start

```bash
cd c:\Users\abc\devtools\_agents101
uv pip install -r requirements.txt
copy .env.example .env          # add GEMINI_API_KEY
.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://localhost:8501** → start at **Phase 0 → Home**.

---

## Stack at a Glance

| What | How |
|---|---|
| LLM | Google Gemini 2.5 Flash (`gemini-2.5-flash`) |
| SDK | `google-genai` (NOT `google-generativeai` — deprecated) |
| UI | Streamlit multi-page (`app.py` → `pages/`) |
| Diagrams | `utils/diagrams.py` + `utils/_diagram_phase10.py` → matplotlib → PNG |
| Tools | `utils/tools.py` — 6 real APIs, no key needed |
| Embeddings | `gemini-embedding-001`, 3072 dimensions |
| Frameworks (Ph10) | `langgraph`, `langchain`, `langchain-google-genai`, `langsmith` |
| Key env var | `GEMINI_API_KEY` in `.env` |

---

## Phase Map (34 pages complete)

```
Phase 0   Foundations       Hello Gemini · Agent Anatomy · Learning Insights
Phase 1   Augmented LLM     Plain LLM → +Memory → +Tools → Mini Agent
Phase 2   Workflows         Chaining · Routing · Parallelization · Orchestrator · Evaluator
Phase 3   Core Agents       ReAct · Reflection · Planning · Code Exec · Pattern Guide
Phase 4   Trust & Safety    Guardrails · HITL · LLM-as-Judge · (Eval Framework 🔜)
Phase 5   Knowledge         RAG Agent · Long-term Memory
Phase 6   Multi-Agent       Multi-Agent · MCP · A2A · Agent Comms
Phase 7   Production Ops    Observability · Cost & Latency · Error Analysis
Phase 8   In Practice       Customer Support · Elite Multi-Agent · (Coding Agent 🔜)
Phase 9   Best Practices    Tool Design · Prompt Engineering · When NOT to use agents
Phase 10  Frameworks        LangGraph Workflows ✅ · LangGraph Agents ✅ · LangSmith ✅ · LangChain ✅
                            Google ADK 🔜 · Framework Compare 🔜
Phase 11  Platforms  🔜     Vertex AI · Azure · Bedrock · OpenAI Assistants
─────────────────────────────────────────────────────────────────────────────
Self Assessment             Quiz Hub — dynamic MCQ covering all phases
```

---

## Key Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit entry + navigation (edit to add/reorder pages) |
| `utils/llm.py` | Gemini wrapper — model, retry logic (`_call`), chat helpers |
| `utils/tools.py` | 6 real tool functions (weather, stocks, units, country, holidays, joke) |
| `utils/diagrams.py` | Architecture diagrams Phases 0–9 → PNG bytes |
| `utils/_diagram_phase10.py` | Phase 10 diagram functions (LangGraph, LangSmith, LCEL) → PNG bytes |
| `utils/quiz.py` | Phase seed concepts + Gemini MCQ generator (phases 0–10) |
| `CLAUDE.md` | Full project instructions for Claude Code (source of truth) |
| `docs/ARCHITECTURE.md` | System overview, stack, design principles |
| `docs/DECISIONS.md` | Architecture Decision Records (why Gemini, why API-first, etc.) |
| `docs/patterns.md` | All 9 agent patterns reference — mechanism, cost, examples, risks |

---

## Critical Rules (do not break)

1. **Always use `gemini-2.5-flash`** — never 1.5-flash, 2.0-flash, or lite for tool demos
2. **Always set** `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`
3. **Never use** `text-embedding-004` — use `gemini-embedding-001` (3072-dim)
4. **Never silent** `except Exception: emb = np.zeros(N)` — raise or log loudly
5. **Every interactive page** must include a `🔬 Execution Trace` expander
6. **Every comparison** must be a Markdown table — never bullet-list pros/cons
7. **Quiz sync is mandatory** — no phase is done until `utils/quiz.py` PHASE_SEEDS includes it

---

## Architecture Decision Records

| ADR | Decision | Why |
|---|---|---|
| [ADR-001](docs/DECISIONS.md#adr-001-llm-choice--google-gemini-25-flash) | Gemini 2.5 Flash | Free tier, function calling, reliable JSON mode |
| [ADR-002](docs/DECISIONS.md#adr-002-frameworks-come-last-phase-10) | Frameworks last (Phase 10) | API-first builds real understanding; Anthropic recommendation |
| [ADR-003](docs/DECISIONS.md#adr-003-streamlit-as-ui-layer) | Streamlit UI | Zero JS, pure Python, session state, zero boilerplate |
| [ADR-004](docs/DECISIONS.md#adr-004-diagrams-as-matplotlib-png-not-mermaid-or-d3) | matplotlib diagrams | No Node.js, no CDN, consistent style, Python-native |
| [ADR-005](docs/DECISIONS.md#adr-005-automatic-function-calling-must-be-disabled) | Disable auto tool calling | Visibility — learners must see every tool call |
| [ADR-006](docs/DECISIONS.md#adr-006-embeddings--gemini-embedding-001-at-3072-dimensions) | gemini-embedding-001 (3072-dim) | text-embedding-004 is deprecated (404) |

---

## GitHub

Repository: https://github.com/davidjeyam-cloud/agents101  
Issues and contributions welcome.
