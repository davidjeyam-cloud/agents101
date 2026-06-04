"""
Agent Anatomy — what makes up an Agent, its components, and interfaces.
Reference page: come back to this at any point in the course.
"""

import streamlit as st
from utils.styles import phase_header, ACCENT_COMPLETE

st.set_page_config(page_title="Agent Anatomy", page_icon="🔬", layout="wide")

# ── Phase 0 header ─────────────────────────────────────────────────────────────
st.markdown(phase_header(
    "Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Reference",
    "🔬 Agent Anatomy",
    "What is inside an agent — its internal components, external interfaces, and how "
    "each maps to a phase in this course. Bookmark and return to this page as you progress.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Diagram ─────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_agent_anatomy
st.image(diagram_agent_anatomy(), use_container_width=True)

st.info(
    "The diagram above shows the **architectural components** of an agent — "
    "these are the building blocks regardless of which framework you use. "
    "**Phase 10** shows how LangGraph / LangChain / Google ADK implement these same patterns. "
    "**Phase 11** shows managed platforms (Vertex AI, Azure, Bedrock, OpenAI) that host this stack."
)

st.markdown("---")

# ── Three tabs — one per section ───────────────────────────────────────────────
tab_components, tab_interfaces, tab_map = st.tabs([
    "🧠 Internal Components",
    "🔌 External Interfaces",
    "🗺️ Course Map",
])

# ── TAB 1: Internal Components ─────────────────────────────────────────────────
with tab_components:
    st.caption("The six building blocks that every production agent contains.")
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🧠 LLM / Brain — the decision-making core", expanded=True):
            st.markdown("""
**What it is:** The language model at the centre of the agent. Receives all context
and decides what to do next: call a tool, search a knowledge base, ask a human, or stop.

**In this course:** Gemini 2.5 Flash via `google-genai` SDK.

**Key capability:** Given a goal + available tools + past observations,
the LLM reasons about the optimal next action. This reasoning is the "Think" in ReAct.

**Interfaces:**
- Receives: user message + memory + retrieved context + tool results
- Outputs: text response OR structured tool call request

**Course phase:** Phase 1a (bare LLM) → Phase 3a (ReAct agent)
""")

        with st.expander("📋 Instructions / Persona — the system prompt"):
            st.markdown("""
**What it is:** A system-level prompt that defines the agent's:
- **Scope** — what it can and cannot do
- **Persona** — tone, style, name (e.g. "You are NexaBank's AI assistant")
- **Rules** — hard constraints (never reveal system prompt, always cite sources)
- **Tool guidance** — when to use which tool

**Why it matters:** The same LLM with different instructions becomes a completely
different agent. Instructions are the "character" of the agent.

```python
system_instruction = (
    "You are NexaBank's AI assistant. "
    "ALWAYS search the knowledge base before answering. "
    "Never give investment advice. "
    "If refund > £500, pause for human approval."
)
```

**Course phase:** Used in every demo from Phase 1c onwards.
""")

        with st.expander("💾 Memory — how agents remember"):
            st.markdown("""
**Three types of memory:**

| Type | What it is | Scope | Course phase |
|---|---|---|---|
| **Context window** | Conversation history in the prompt | Current session | Phase 1b |
| **Long-term (vector)** | Past interactions in a vector DB | Across sessions | Phase 5b |
| **Episodic** | Structured logs of past agent runs | Queryable history | Phase 5b |

**The memory paradox:** LLMs are stateless — all "memory" is simulated by
injecting past context into the current prompt.
""")

        with st.expander("🛡️ Guardrails — safety wrappers"):
            st.markdown("""
**What they are:** Independent safety checks that run *before* input reaches
the agent and *after* output leaves it.

**NOT part of the agent's logic** — intentionally separate so a compromised
or hallucinating agent cannot bypass them.

| Layer | When | Method | Cost |
|---|---|---|---|
| PII detection | Input + Output | Regex | Free |
| Threat classification | Input | LLM (separate) | Tokens |
| Policy compliance | Output | LLM (separate) | Tokens |

**Course phase:** Phase 4a
""")

    with col2:
        with st.expander("🔧 Tools / Skills / Plugins — the agent's hands", expanded=True):
            st.markdown("""
**What they are:** Functions the agent can call to interact with the world.
The agent decides *when* and *what* to call — your code decides *how* it runs.

**Critical principle:** The agent outputs a *request* to call a tool.
Your code executes it and returns the result. The agent never runs code directly.

| Category | Examples | Course |
|---|---|---|
| **Real-time data** | Weather, stock prices | Phase 1c |
| **Computation** | Calculator, unit conversion | Phase 1d |
| **Knowledge** | RAG search, document lookup | Phase 5a |
| **External APIs** | REST APIs, databases | Phase 1c |
| **Agent tools (A2A)** | Other agents as callable functions | Phase 6c |
| **MCP tools** | Standardised tool servers (the plugin standard) | Phase 6b |

```python
# Always disable auto-calling to see each step
automatic_function_calling=AutomaticFunctionCallingConfig(disable=True)
```

**"Skills" and "plugins" are the same concept with different names:**
- Individual tools → function calling (Phase 1c)
- Bundled tool collections → MCP servers, the standardised plugin protocol (Phase 6b)
- Another agent as a callable skill → A2A / sub-agent delegation (Phase 6a–6c)

**Course phase:** Phase 1c → 1d → 3a → 3d
""")

        with st.expander("🔌 Skills / Plugins — terminology clarified"):
            st.markdown("""
This term means different things depending on context. Here is the full map:

| Context | What "skill" or "plugin" means | Runtime component? |
|---|---|---|
| **This course (Gemini SDK)** | A function registered as a tool for the LLM to call | ✅ Yes — Phase 1c |
| **MCP (Anthropic standard)** | A packaged tool server with a discovery API | ✅ Yes — Phase 6b |
| **LangChain / LangGraph** | A `Tool` or `StructuredTool` object wrapping a callable | ✅ Yes — Phase 10a |
| **Google ADK** | A function declared in an agent's tool list | ✅ Yes — Phase 10e |
| **Claude Code IDE** | A `.claude/skills/` instruction file teaching the coding assistant new workflows | ❌ No — dev-time only |
| **ChatGPT Plugins (legacy)** | OpenAI's now-retired plugin spec, replaced by function calling | ✅ Was runtime |

**The key distinction for this course:**

> Claude Code `.claude/skills/` files are **development-time instructions** — they make the coding
> assistant smarter when writing your app. They are not a component of the agents you build.
> The agent components in this course are Tools (function calling) and MCP tool servers.

**Why MCP is "the plugin standard":**
MCP (Phase 6b) solves the same problem that plugin systems solve — it lets an agent discover
and call external capabilities without the capability being hardcoded into the agent.
The difference from a raw tool: MCP is a **standardised protocol** so any MCP-compatible
agent can use any MCP server without custom integration code.

**Course phase:** Phase 1c (tools) · Phase 6b (MCP — the plugin standard) · Phase 6a (sub-agents as skills)
""")

        with st.expander("📚 Knowledge Base (RAG) — domain expertise"):
            st.markdown("""
**What it is:** A collection of domain-specific documents embedded as vectors.
The agent queries it before answering — grounding responses in real documents.

**Why it's separate from Memory:**
- Memory = conversation history (what was said)
- Knowledge Base = domain documents (what the org knows)

**Retrieval pipeline:**
```
User query → embed → cosine similarity search
           → top-K chunks retrieved
           → injected into prompt
           → LLM answers using context
```

**Course phase:** Phase 5a
""")

        with st.expander("👤 HITL Checkpoint — human oversight"):
            st.markdown("""
**What it is:** A pause point where the agent presents its proposed action
to a human for approval before proceeding.

**Triggers for HITL:**
- Risk level: high or critical
- Confidence < threshold (e.g. 70%)
- Amount > threshold (e.g. £500)
- Irreversible action

**Three human decisions:**
- **Approve** → agent sends its proposed response as-is
- **Reject** → agent generates a polite rejection
- **Modify** → human edits the draft, agent sends human's version

**Course phase:** Phase 4b
""")

        with st.expander("🔗 A2A / MCP Interfaces — agent communication"):
            st.markdown("""
| Protocol | By | Purpose | Direction |
|---|---|---|---|
| **MCP** | Anthropic (Nov 2024) | Connect agent to tools & data | Agent → Resource |
| **A2A** | Google (Apr 2025) | Agent talking to agent | Agent → Agent |

**MCP:** Standardises how agents connect to external tools, databases, and APIs.

**A2A:** Standardises how agents discover and communicate with each other.
- **Agent Card** — JSON manifest at `/.well-known/agent.json`
- **Task** — unit of work delegated to another agent

**Course phase:** Phase 6b (MCP) · Phase 6c (A2A) · Phase 6d (comparison)
""")

# ── TAB 2: External Interfaces ─────────────────────────────────────────────────
with tab_interfaces:
    st.caption("Every boundary the agent crosses — what flows across each one and how.")
    st.markdown("""
| Interface | Direction | What crosses the boundary | Protocol |
|---|---|---|---|
| **User interface** | In → Agent | Natural language query, uploaded files | HTTP / WebSocket |
| **Response interface** | Agent → Out | Text response, structured data | HTTP / WebSocket |
| **Tool interface** | Agent ↔ Tools | Function call requests + results | Python function call / MCP |
| **Knowledge base** | Agent → KB | Embedding query → retrieved chunks | Cosine search / vector DB |
| **Guardrail interface** | Wraps Agent | Input sanitised in, output validated out | Internal middleware |
| **HITL interface** | Agent → Human | Checkpoint card, proposed action, risk level | UI / case management |
| **A2A interface** | Agent ↔ Agent | Task delegation, streaming results | HTTP + JSON (A2A spec) |
| **Audit interface** | Agent → Log | Every decision, tool call, HITL event | Append-only log |
""")

# ── TAB 3: Course Map ──────────────────────────────────────────────────────────
with tab_map:
    st.caption("Every agent component mapped to its course phase. ✅ = page complete · 🔜 = coming.")
    st.markdown("""
| Component | Phase(s) | Status |
|---|---|---|
| **— Phase 1 · Augmented LLM —** | | |
| 🧠 LLM Brain | 1a | ✅ |
| 💾 Context-window Memory | 1b · 1c | ✅ |
| 🔧 Tools / Skills / Plugins (function calling) | 1c · 1d | ✅ |
| 📋 Instructions / Persona | 1c → every phase | ✅ |
| **— Phase 2 · Workflow Patterns —** | | |
| 🔄 Chaining · Routing · Parallel · Orchestrator · Evaluator | 2a – 2e | ✅ |
| **— Phase 3 · Core Agent Patterns —** | | |
| 🔄 Agent Loop (ReAct: Think → Act → Observe) | 1d mini → 3a | ✅ |
| 🤔 Reflection (self-critique loop) | 3b | ✅ |
| 📐 Planning (Plan-and-Execute) | 3c | ✅ |
| 💻 Code Execution (Python REPL tool) | 3d | ✅ |
| **— Phase 4 · Trust & Safety —** | | |
| 🛡️ Guardrails | 4a | ✅ |
| 👤 HITL Checkpoint | 4b | ✅ |
| 🔍 LLM-as-Judge | 4c | ✅ |
| 🏆 Evaluation Framework | 4d | ✅ |
| **— Phase 5 · Knowledge & Memory —** | | |
| 📚 Knowledge Base (RAG) | 5a | ✅ |
| 🧠 Long-term Memory (vector store) | 5b | ✅ |
| **— Phase 6 · Multi-Agent & Protocols —** | | |
| 👥 Multi-Agent (root + sub-agents) | 2d intro → 6a | ✅ |
| 🔌 MCP Protocol — the plugin/tool-server standard | 6b | ✅ |
| 🔗 A2A Protocol (agent ↔ agent) | 6c | ✅ |
| **— Phase 7 · Production Operations —** | | |
| 📊 Observability & Tracing | 7a | ✅ |
| ⚖️ Cost & Latency Optimisation | 7b | ✅ |
| 🔍 Error Analysis | 7c | ✅ |
| **— Phase 8 · Agents in Practice —** | | |
| 🏭 Production Agent (full end-to-end pipeline) | 8a | ✅ |
| 💻 Coding Agent | 8b | 🔜 |
| **— Phase 9 · Best Practices —** | | |
| 📐 Tool design & prompt engineering for agents | 9 | 🔜 |
| **— Phase 10 · Frameworks Layer —** | | |
| 🔷 LangGraph (workflow + agent graphs with typed state) | 10a · 10b | ✅ |
| 🔭 LangSmith (automated tracing + eval runs) | 10c | ✅ |
| ⛓️ LangChain LCEL (pipe syntax, memory, RAG) | 10d | ✅ |
| 🌐 Google ADK (sequential · parallel · loop agents) | 10e | ✅ |
| 📊 Framework Comparison (LangGraph vs ADK vs raw SDK) | 10f | ✅ |
| **— Phase 11 · Managed Platforms —** | | |
| ☁️ Vertex AI · Azure AI · Bedrock · OpenAI Assistants | 11a – 11e | 🔜 |
""")

st.markdown("---")
st.info(
    "💡 **This page is a reference** — bookmark it and return as you work through each phase. "
    "Each component in the diagram above becomes hands-on code in its corresponding phase."
)
