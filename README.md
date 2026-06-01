# Agentic AI Cookbook — agents101

A hands-on, interactive learning environment for agentic AI architecture patterns, built with **Google Gemini 2.5** and **Streamlit**.

Every concept is taught API-first — no framework magic hiding the mechanics — before optional framework layers are introduced at the end.

> **Philosophy:** Someone who built agents from scratch can read LangGraph source and understand it immediately. The reverse is much harder.  
> — Anthropic: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

---

## What's inside

40+ interactive pages across 12 phases, each with:
- A live architecture diagram
- A minimal code pattern snippet showing the core idea
- A runnable demo using real APIs (weather, stocks, currencies, holidays)
- An execution trace expander showing exact prompts and raw LLM responses
- A self-assessment quiz (Gemini JSON-mode MCQ)

---

## Course Map

### Phase 0 — Foundations
| Module | What you learn |
|---|---|
| Hello Gemini | API setup, verify key, first call |
| Agent Anatomy | Components: LLM + Memory + Tools + Action loop |
| Learning Insights | Course philosophy, API-first rationale |
| Quiz Hub | Dynamic MCQ across all phases, LLM-generated questions |

### Phase 1 — Augmented LLM
| Module | What you learn |
|---|---|
| 1a Plain LLM | Stateless generate_content call |
| 1b + Memory | Session history, multi-turn conversation |
| 1c + Tools | Real tool calls, manual function dispatch |
| 1d Mini Agent | Think → Act → Observe loop |

### Phase 2 — Workflow Patterns
| Module | What you learn |
|---|---|
| Prompt Chaining | Sequential steps, output feeds next stage |
| Routing | Classify intent, route to specialist handler |
| Parallelization | Concurrent calls, aggregation, voting |
| Orchestrator-Workers | Dynamic task decomposition, worker delegation |
| Evaluator-Optimizer | Generate → evaluate → improve loop |

### Phase 3 — Core Agent Patterns  *(Andrew Ng's 4 fundamentals)*
| Module | What you learn |
|---|---|
| ReAct Agent | Think → Act → Observe loop with real tools |
| Reflection | Self-critique and iterative improvement |
| Planning | Plan-and-Execute: upfront plan, step-by-step execution |
| Code Execution | Python REPL as a tool — agent writes and runs code |
| Pattern Decision Guide | All 9 patterns compared: when to use which |

### Phase 4 — Trust & Safety
| Module | What you learn |
|---|---|
| Guardrails | Input + output safety, PII detection, compliance filters |
| Human-in-the-Loop | Checkpoint, approve / reject / modify |
| LLM-as-Judge | Independent quality gate, PASS / REVIEW / FAIL scoring |
| Evaluation Framework | Systematic evals, test sets, metrics *(in progress)* |

### Phase 5 — Knowledge & Memory
| Module | What you learn |
|---|---|
| RAG Agent | Retrieve → Augment → Generate, cosine similarity search |
| Long-term Memory | ChromaDB vector store, semantic recall across sessions |

### Phase 6 — Multi-Agent & Protocols
| Module | What you learn |
|---|---|
| Multi-Agent | Root + Sub agents, parallel delegation |
| MCP | Model Context Protocol (Anthropic, Nov 2024) — full simulation |
| A2A | Agent-to-Agent Protocol (Google, Apr 2025) — Agent Cards, task lifecycle |
| Agent Comms | Raw vs MCP vs A2A: same task three ways, side-by-side comparison |

### Phase 7 — Production Operations
| Module | What you learn |
|---|---|
| Observability | TraceCollector, latency, token counts, cost dashboard |
| Cost & Latency | Token counting, caching simulation, model routing |
| Error Analysis | 5-type taxonomy, broken vs fixed, auto-diagnosis, fix playbook |

### Phase 8 — Agents in Practice  *(Anthropic Appendix 1)*
| Module | What you learn |
|---|---|
| Customer Support Agent | Full pipeline: guardrails + RAG + HITL + multi-agent |
| Coding Agent | GitHub issue → fix → test → iterate *(in progress)* |

### Phase 9 — Best Practices  *(Anthropic Appendix 2)*
Tool design, prompt engineering for tool-calling agents *(in progress)*

### Phase 10 — Frameworks Layer  *(after all patterns mastered)*
| Module | What you learn |
|---|---|
| LangGraph Workflows | Phase 2 patterns as StateGraph — typed state, streaming |
| LangGraph Agents | ReAct / Reflection / Planning + HITL via interrupt_before |
| LangSmith | Observability automated — auto-trace, datasets, eval runs |
| LangChain LCEL | Memory + chaining + RAG as pipe syntax |
| Google ADK | Multi-agent: sequential / parallel / loop *(in progress)* |
| Framework Comparison | LangGraph vs ADK vs raw SDK *(in progress)* |

### Phase 11 — Managed Platforms  *(cursory overview)*
Vertex AI · Azure AI Agent Service · AWS Bedrock · OpenAI Assistants *(in progress)*

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| LLM | Google Gemini 2.5 Flash | Best cost/quality; 1M token context |
| SDK | `google-genai` | Current SDK (google-generativeai is deprecated) |
| UI | Streamlit multi-page | Fast, interactive, no frontend boilerplate |
| Vector store | ChromaDB | Local, no infra needed for long-term memory |
| Real tools | Open-Meteo, yfinance, REST Countries, Nager Date | Free, no API key required |
| Diagrams | matplotlib (PNG) | Rendered inline via st.image |

---

## Running locally

```bash
git clone https://github.com/davidjeyam-cloud/agents101.git
cd agents101

# Install dependencies (use uv, not pip)
uv pip install -r requirements.txt

# Set your API key
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Launch
python -m streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

---

## Sources

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Andrew Ng — [Agentic AI (DeepLearning.AI)](https://www.deeplearning.ai/courses/agentic-ai)
