"""
Agent Anatomy — what makes up an Agent, its components, and interfaces.
Reference page: come back to this at any point in the course.
"""

import streamlit as st

st.set_page_config(page_title="Agent Anatomy", page_icon="🔬", layout="wide")

# ── Phase 0 header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#0D1117 0%,#0F1A2E 100%);
border-left:5px solid #00FF9F;border-radius:8px;padding:18px 24px;margin-bottom:24px'>
  <div style='font-size:0.65rem;font-weight:700;letter-spacing:3px;
              text-transform:uppercase;color:#00FF9F;margin-bottom:6px'>
    Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Reference
  </div>
  <div style='font-size:1.7rem;font-weight:800;color:#E6EDF3;line-height:1.2'>
    🔬 Agent Anatomy
  </div>
  <div style='font-size:0.88rem;color:#8B949E;margin-top:6px'>
    What is inside an agent — its internal components, external interfaces, and how
    each maps to a phase in this course. Bookmark and return to this page as you progress.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Diagram ─────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_agent_anatomy
st.image(diagram_agent_anatomy(), use_container_width=True)

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
        with st.expander("🔧 Tools — the agent's hands", expanded=True):
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
| **MCP tools** | Standardised tool servers | Phase 6b |

```python
# Always disable auto-calling to see each step
automatic_function_calling=AutomaticFunctionCallingConfig(disable=True)
```

**Course phase:** Phase 1c → 1d → 3a → 3d
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
    st.caption("When each component is introduced and where it is fully built in the course.")
    st.markdown("""
| Component | First introduced | Fully built | Phase |
|---|---|---|---|
| 🧠 LLM Brain (bare call) | Phase 1a | Phase 1a | 1 |
| 💾 Context-window Memory | Phase 1b | Phase 1b + 1c | 1 |
| 🔧 Tools (function calling) | Phase 1c | Phase 1c + 1d | 1 |
| 📋 Instructions / Persona | Phase 1c | Every phase onwards | 1 |
| 🔄 Agent Loop (ReAct) | Phase 1d (mini) | Phase 3a | 3 |
| 🛡️ Guardrails | Phase 4a | Phase 4a | 4 |
| 👤 HITL Checkpoint | Phase 4b | Phase 4b | 4 |
| 🔍 LLM-as-Judge | Phase 4c | Phase 4c | 4 |
| 🤔 Reflection | Phase 3b | Phase 3b | 3 |
| 📚 Knowledge Base (RAG) | Phase 5a | Phase 5a | 5 |
| 🧠 Long-term Memory | Phase 5b | Phase 5b | 5 |
| 👥 Multi-Agent | Phase 2d | Phase 6a | 6 |
| 🔗 MCP Protocol | Phase 6b | Phase 6b | 6 |
| 🔗 A2A Protocol | Phase 6c | Phase 6c | 6 |
| 📊 Observability | Phase 7a | Phase 7a | 7 |
| ⚖️ Complete Production Agent | Phase 8a | Phase 8a + 8b | 8 |
""")

st.markdown("---")
st.info(
    "💡 **This page is a reference** — bookmark it and return as you work through each phase. "
    "Each component in the diagram above becomes hands-on code in its corresponding phase."
)
