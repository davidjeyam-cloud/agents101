"""
Phase 10g — CrewAI
Role-based multi-agent crews: each agent has a role, backstory, and goal.
Maps to Phase 6a (Multi-Agent) and Phase 2d (Orchestrator-Workers).
CrewAI is NOT installed — concepts shown via st.code() + runnable raw SDK equivalents.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10g — CrewAI",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import phase_header, ACCENT_COMPLETE
from utils.llm import MODEL, _client, _call
from utils.trace import render_trace
from google.genai import types

st.markdown(phase_header(
    "Phase 10g &nbsp;·&nbsp; Frameworks Layer &nbsp;·&nbsp; Role-Based Crews",
    "🤝 CrewAI",
    "Role-based multi-agent framework — define agents as team members with a role, "
    "backstory, and goal. Crew handles task assignment, delegation, and execution.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 6a · 2d)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 6a you wrote a root orchestrator that delegated to specialist sub-agents.<br>
    In Phase 2d you wrote an orchestrator that planned once and assigned fixed worker roles.<br>
    <strong>CrewAI wraps both patterns</strong> — you define agents as team members
    (role + backstory + goal), assign tasks to them, and the crew handles execution.
    The patterns you built from scratch are now 5-line YAML declarations.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Diagram placeholder ────────────────────────────────────────────────────────
st.info(
    "📊 Diagram: CrewAI sits in the same 'abstraction' band as LangGraph and ADK "
    "but uses the role-based crew metaphor rather than graph nodes or agent types. "
    "See Phase 10f Framework Compare for the full landscape diagram."
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is CrewAI — and how does the crew metaphor work?"):
    st.markdown("""
CrewAI models a multi-agent system as a **work team** (crew).
Every component maps to a familiar workplace concept.

**The four building blocks:**

| CrewAI concept | What it is | Raw SDK equivalent (Phase 6a) |
|---|---|---|
| **Agent** | An autonomous LLM worker with a role, backstory, and goal | Sub-agent with a system prompt |
| **Task** | A discrete unit of work assigned to a specific agent | A query routed to a sub-agent |
| **Crew** | The assembled team of agents and their tasks | The root orchestrator + sub-agents |
| **Process** | How the crew executes (`sequential` / `hierarchical`) | Chaining vs root-delegates |

**What makes CrewAI's "role" unique:**

A CrewAI agent is not just a system prompt. It has:
- **Role** — job title: *"Senior Financial Analyst"*
- **Backstory** — context: *"10 years in banking, specialist in regulatory compliance"*
- **Goal** — objective: *"Produce accurate, evidence-based financial reports"*

The LLM uses all three to stay in character across multi-turn tasks. A plain system prompt
has no backstory — it tells the model WHAT to do, not WHO it is.

**Two execution modes:**

| Process | How it works | Maps to |
|---|---|---|
| `Process.sequential` | Tasks execute one after another; each agent gets the previous agent's output | Phase 2a Prompt Chaining — but with autonomous agents |
| `Process.hierarchical` | A manager LLM assigns tasks dynamically, can re-route | Phase 6a Root + Sub-Agents |

**Basic RAG vs Agentic RAG vs CrewAI RAG:**

CrewAI agents can be given tools (including search/RAG tools). The difference from Phase 5a
is that CrewAI wraps the entire multi-agent coordination — you do not write the
orchestration loop yourself.

**CrewAI vs LangGraph vs Google ADK:**

| | CrewAI | LangGraph | Google ADK |
|---|---|---|---|
| **Mental model** | Team of role-playing agents | State machine graph | Typed agent classes |
| **Best for** | Quick multi-agent prototyping, role-based workflows | Production, checkpointing, HITL | Google Cloud, multi-agent types |
| **Learning curve** | Low — YAML config, intuitive | Medium — graph concepts | Medium — ADK SDK |
| **Control** | Lower — framework decides execution | Higher — you define every edge | Medium |
| **State persistence** | Built-in (short-term) | Built-in (long-term, DB-backed) | Session-scoped |
""")

with st.expander("📐 Core Code Pattern — CrewAI"):
    st.code('''
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool   # optional: gives agents web search

# ── 1. Define agents (who they are) ─────────────────────────────────────────
researcher = Agent(
    role        = "Senior Financial Research Analyst",
    backstory   = "15 years analysing UK retail banks. Expert in FCA regulations.",
    goal        = "Find accurate, specific information about NexaBank products.",
    tools       = [SerperDevTool()],   # agent can search the web
    verbose     = True,
)

writer = Agent(
    role        = "Customer Communications Specialist",
    backstory   = "Former NexaBank customer advisor, expert at plain English explanations.",
    goal        = "Transform research findings into clear, concise customer answers.",
    verbose     = True,
)

# ── 2. Define tasks (what each agent does) ──────────────────────────────────
research_task = Task(
    description       = "Find NexaBank's current savings rates, ISA limits, and mortgage options.",
    expected_output   = "Bullet-point summary of rates with exact figures.",
    agent             = researcher,      # assigned to researcher
)

writing_task = Task(
    description       = "Write a 150-word customer email explaining NexaBank's best savings options.",
    expected_output   = "Polished customer email, friendly tone, no jargon.",
    agent             = writer,          # assigned to writer
    context           = [research_task], # writer receives researcher's output
)

# ── 3. Assemble and run the crew ─────────────────────────────────────────────
crew = Crew(
    agents  = [researcher, writer],
    tasks   = [research_task, writing_task],
    process = Process.sequential,   # researcher first, then writer
    verbose = True,
)

result = crew.kickoff()
print(result.raw)   # the writer's final email
''', language="python")
    st.markdown("""
**What CrewAI handles for you (vs raw SDK in Phase 6a):**

| You wrote in Phase 6a | CrewAI does automatically |
|---|---|
| Root agent system prompt routing logic | `Process.sequential` / `Process.hierarchical` |
| Passing sub-agent output to next agent | `context=[previous_task]` |
| Tool registration per agent | `tools=[...]` on each Agent |
| Memory between tasks | Built-in `memory=True` on Crew |
| Output parsing + error handling | Framework-managed |

**Key insight:** The coordination code you wrote in Phase 6a (100+ lines) becomes
CrewAI config (~20 lines). The agents still do the same work — the plumbing disappeared.
""")

# ── Live Demo — Raw SDK simulation ────────────────────────────────────────────
st.markdown("---")
st.markdown("## Live Demo — Crew pattern using raw Gemini SDK")
st.caption(
    "CrewAI is not installed (follows the course pattern — raw SDK first, frameworks second). "
    "This demo implements the identical researcher→writer sequential crew using the Gemini SDK directly."
)

DEMO_TOPICS = {
    "Best savings account": "What is the best NexaBank savings account for a customer with £8,000?",
    "Mortgage overview":    "Summarise NexaBank's mortgage options for a first-time buyer.",
    "Complaint escalation": "Explain NexaBank's complaint process and when a customer can go to the FOS.",
    "Fraud protection":     "What protections does NexaBank offer for APP fraud and how does PSR 2023 apply?",
}

if "sel_crewai" not in st.session_state:
    st.session_state.sel_crewai = list(DEMO_TOPICS.values())[0]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Example topics:**")
    for label, text in DEMO_TOPICS.items():
        if st.button(label, key=f"crew_{label}"):
            st.session_state.sel_crewai = text
            st.rerun()
with col1:
    topic = st.text_area("Customer question for the crew:", value=st.session_state.sel_crewai, height=90)

col_a, col_b = st.columns(2)
with col_a:
    researcher_role = st.text_input(
        "Researcher role:",
        value="Senior NexaBank Financial Research Analyst",
    )
with col_b:
    writer_role = st.text_input(
        "Writer role:",
        value="NexaBank Customer Communications Specialist",
    )

if st.button("▶  Run Crew (Researcher → Writer)", type="primary", key="run_crewai"):
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    client = _client()

    # ── Agent 1: Researcher ────────────────────────────────────────────────────
    researcher_sys = (
        f"You are a {researcher_role}. "
        "Your job is to research the question thoroughly and produce a factual bullet-point summary. "
        "Be specific — include exact figures, policy names, and relevant conditions. "
        "NexaBank context: NexaSaver 4.75% AER, ISA 4.2% AER, mortgages from 4.65% APRC, "
        "refunds up to £500 auto-processed, complaints escalate to FOS after 8 weeks, "
        "APP fraud reimbursement up to £415,000 under PSR 2023."
    )
    researcher_prompt = f"Research this customer question thoroughly:\n\n{topic}"

    with st.spinner("Agent 1 — Researcher working..."):
        r1 = _call(
            client.models.generate_content,
            model=MODEL,
            contents=researcher_prompt,
            config=types.GenerateContentConfig(system_instruction=researcher_sys),
        )
    research_output = r1.text.strip()

    with st.container(border=True):
        st.markdown(f"#### Agent 1 — {researcher_role}")
        st.markdown("**Research findings:**")
        st.markdown(research_output)

    st.markdown(
        "<div style='text-align:center;font-size:1.2rem;margin:8px 0'>"
        "↓ researcher output passed as context to writer</div>",
        unsafe_allow_html=True,
    )

    # ── Agent 2: Writer ────────────────────────────────────────────────────────
    writer_sys = (
        f"You are a {writer_role}. "
        "You receive research findings and transform them into a clear, friendly customer response. "
        "Use plain English, no jargon. Keep it under 150 words. Be warm and specific."
    )
    writer_prompt = (
        f"Customer question: {topic}\n\n"
        f"Research findings from the analyst:\n{research_output}\n\n"
        "Write a clear, friendly customer response based on these findings."
    )

    with st.spinner("Agent 2 — Writer working..."):
        r2 = _call(
            client.models.generate_content,
            model=MODEL,
            contents=writer_prompt,
            config=types.GenerateContentConfig(system_instruction=writer_sys),
        )
    writer_output = r2.text.strip()

    with st.container(border=True):
        st.markdown(f"#### Agent 2 — {writer_role}")
        st.markdown("**Final customer response:**")
        st.success(writer_output)

    st.toast("✅ Crew complete — 2 agents, sequential execution", icon="🤝")

    # ── Execution Trace ────────────────────────────────────────────────────────
    def _tab_researcher():
        st.markdown("**System prompt (role + backstory):**")
        st.code(researcher_sys, language="text")
        st.markdown("**Task (user message):**")
        st.code(researcher_prompt, language="text")
        st.markdown("**Raw output:**")
        st.code(research_output, language="text")

    def _tab_writer():
        st.markdown("**System prompt (role + backstory):**")
        st.code(writer_sys, language="text")
        st.markdown("**Task (includes researcher's output as context):**")
        st.code(writer_prompt, language="text")
        st.markdown("**Raw output:**")
        st.code(writer_output, language="text")

    def _tab_crew():
        st.markdown("**Crew execution flow:**")
        st.code(
            "Process.sequential\n"
            "  └─► Task 1 → Agent 1 (Researcher)\n"
            "        output ──► injected as context\n"
            "  └─► Task 2 → Agent 2 (Writer)\n"
            "        output ──► final result",
            language="text",
        )
        st.markdown("""
**CrewAI equivalent:**
```python
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
)
result = crew.kickoff()
```
The framework handles everything between the two agents automatically.
        """)

    render_trace(
        ("Agent 1 — Researcher", _tab_researcher),
        ("Agent 2 — Writer",     _tab_writer),
        ("Crew Flow",            _tab_crew),
    )

st.markdown("---")
st.markdown("### What's next → Phase 10f: Framework Compare")
st.markdown(
    "Now that you have seen LangGraph, LangSmith, LangChain, Google ADK, and CrewAI — "
    "Phase 10f compares all of them side-by-side and gives a decision guide for "
    "which to reach for in a real production scenario."
)
