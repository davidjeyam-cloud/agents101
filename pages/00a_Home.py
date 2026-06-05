"""
Home — Agentic AI Cookbook learning portal.
Professional neon-themed layout.
"""

import streamlit as st
from utils.styles import apply_theme

st.set_page_config(page_title="Agentic AI Cookbook", page_icon="🤖", layout="wide")

# ── Home-specific CSS (global theme injected by app.py via apply_theme) ─────────
st.markdown("""
<style>

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0D1117 0%, #0F1A2E 50%, #0D1117 100%);
    border: 1px solid #00D4FF;
    border-radius: 16px;
    padding: 44px 48px 36px 48px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(0,212,255,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #00D4FF;
    background: linear-gradient(90deg, #00FF9F 0%, #00D4FF 50%, #B47FFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 6px 0;
    line-height: 1.2;
}
.hero-sub {
    color: #8B949E;
    font-size: 1.05rem;
    margin: 0 0 24px 0;
}
.hero-tags { display: flex; gap: 10px; flex-wrap: wrap; }
.hero-tag {
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.3);
    color: #00D4FF;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── Stat cards ── */
.stats-row { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
.stat-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 18px 24px;
    flex: 1;
    min-width: 130px;
    text-align: center;
}
.stat-num {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-label { color: #8B949E; font-size: 0.75rem; letter-spacing: 0.5px; }
.stat-green .stat-num { color: #00FF9F; text-shadow: 0 0 20px rgba(0,255,159,0.4); }
.stat-blue  .stat-num { color: #00D4FF; text-shadow: 0 0 20px rgba(0,212,255,0.4); }
.stat-orange .stat-num { color: #FFB347; text-shadow: 0 0 20px rgba(255,179,71,0.4); }
.stat-purple .stat-num { color: #B47FFF; text-shadow: 0 0 20px rgba(180,127,255,0.4); }

/* ── Section headers ── */
.section-hdr {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 14px 0;
}
.section-hdr-line { flex: 1; height: 1px; background: #CBD5E0; }
.section-hdr-text {
    color: #8B949E;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    white-space: nowrap;
}
.section-hdr-dot {
    width: 8px; height: 8px; border-radius: 50%;
    flex-shrink: 0;
}

/* ── Phase cards grid ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 8px;
}
.pcard {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 14px 16px;
    transition: transform 0.15s, box-shadow 0.15s;
    cursor: default;
}
.pcard:hover { transform: translateY(-2px); }

.pcard-complete {
    border-color: rgba(0,255,159,0.35);
    box-shadow: 0 0 14px rgba(0,255,159,0.08);
}
.pcard-progress {
    border-color: rgba(255,179,71,0.5);
    box-shadow: 0 0 18px rgba(255,179,71,0.15);
}
.pcard-priority {
    border-color: rgba(255,99,132,0.35);
    box-shadow: 0 0 14px rgba(255,99,132,0.08);
}
.pcard-coming { border-color: #21262D; opacity: 0.55; }
.pcard-future { border-color: #21262D; opacity: 0.35; }

.pcard-phase {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.pcard-title { font-size: 0.88rem; font-weight: 600; color: #E6EDF3; margin-bottom: 7px; line-height: 1.3; }
.pcard-desc  { font-size: 0.72rem; color: #8B949E; line-height: 1.4; }

/* ── Badges ── */
.badge {
    display: inline-block;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 20px;
    margin-bottom: 6px;
}
.b-done  { background:rgba(0,255,159,0.12); color:#00FF9F; border:1px solid rgba(0,255,159,0.4); }
.b-now   { background:rgba(255,179,71,0.15); color:#FFB347; border:1px solid rgba(255,179,71,0.5); }
.b-hot   { background:rgba(255,99,132,0.12); color:#FF6384; border:1px solid rgba(255,99,132,0.4); }
.b-soon  { background:rgba(100,110,120,0.12); color:#6E7681; border:1px solid #3D444D; }
.b-fw    { background:rgba(180,127,255,0.12); color:#B47FFF; border:1px solid rgba(180,127,255,0.4); }
.b-cloud { background:rgba(0,212,255,0.08); color:#00D4FF; border:1px solid rgba(0,212,255,0.3); }

/* ── Progress bar ── */
.prog-bar-wrap { background:#161B22; border-radius:8px; height:8px; margin: 6px 0 20px 0; overflow:hidden; }
.prog-bar-fill {
    height:100%;
    border-radius:8px;
    background: linear-gradient(90deg, #00FF9F, #00D4FF);
    box-shadow: 0 0 8px rgba(0,255,159,0.5);
}

/* ── Learning path ── */
.path-arrow {
    text-align:center;
    color:#9CA3AF;
    font-size:1.2rem;
    margin: 4px 0;
    letter-spacing: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🤖 Agentic AI Cookbook</div>
  <div class="hero-sub">
    Hands-on implementation of every Agentic AI pattern — from first principles to production frameworks
  </div>
  <div class="hero-tags">
    <span class="hero-tag">Gemini 2.5 Flash</span>
    <span class="hero-tag">Anthropic Patterns</span>
    <span class="hero-tag">Andrew Ng Patterns</span>
    <span class="hero-tag">Banking Context</span>
    <span class="hero-tag">Live Demos</span>
    <span class="hero-tag">Free Tier</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────────
total    = 47  # all phase cards on this page
complete = 41  # Ph0(3)+Ph1(1)+Ph2(5)+Ph3(5)+Ph4(4)+Ph5(2)+Ph6(4)+Ph7(4)+Ph8(5)+Ph9(1)+Ph10(7)
in_prog  = 0
coming   = total - complete - in_prog  # 6 remaining: 8b + all Phase 11
pct      = int(complete / total * 100)

st.markdown(f"""
<div class="stats-row">
  <div class="stat-card stat-green">
    <div class="stat-num">{complete}</div>
    <div class="stat-label">PHASES COMPLETE</div>
  </div>
  <div class="stat-card stat-orange">
    <div class="stat-num">{in_prog}</div>
    <div class="stat-label">IN PROGRESS</div>
  </div>
  <div class="stat-card stat-blue">
    <div class="stat-num">{coming}</div>
    <div class="stat-label">COMING NEXT</div>
  </div>
  <div class="stat-card stat-purple">
    <div class="stat-num">{pct}%</div>
    <div class="stat-label">COURSE PROGRESS</div>
  </div>
</div>
<div class="prog-bar-wrap">
  <div class="prog-bar-fill" style="width:{pct}%"></div>
</div>
""", unsafe_allow_html=True)

# ── Helper to render a section ─────────────────────────────────────────────────
def section(label: str, dot_color: str):
    st.markdown(f"""
    <div class="section-hdr">
      <div class="section-hdr-dot" style="background:{dot_color}; box-shadow:0 0 6px {dot_color}"></div>
      <div class="section-hdr-text">{label}</div>
      <div class="section-hdr-line"></div>
    </div>""", unsafe_allow_html=True)

def card(phase: str, title: str, desc: str, badge: str, badge_cls: str, card_cls: str, phase_color: str):
    return f"""
    <div class="pcard {card_cls}">
      <span class="badge {badge_cls}">{badge}</span>
      <div class="pcard-phase" style="color:{phase_color}">{phase}</div>
      <div class="pcard-title">{title}</div>
      <div class="pcard-desc">{desc}</div>
    </div>"""

def grid(*cards):
    st.markdown(f'<div class="cards-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

# ── Recommended next ───────────────────────────────────────────────────────────
st.markdown("""
<div style="background:rgba(255,179,71,0.06);border:1px solid rgba(255,179,71,0.3);
border-radius:12px;padding:16px 20px;margin-bottom:24px;">
  <div style="color:#FFB347;font-size:0.7rem;font-weight:700;letter-spacing:2px;
              text-transform:uppercase;margin-bottom:10px;">
    &#9654; Recommended Learning Path — Next 3 Steps
  </div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:180px;background:rgba(255,99,132,0.08);border:1px solid rgba(255,99,132,0.3);
                border-radius:8px;padding:10px 14px;">
      <div style="color:#FF6384;font-size:0.65rem;font-weight:700;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:4px;">Step 1 — Phase 8b</div>
      <div style="color:#E6EDF3;font-size:0.85rem;font-weight:600;">Coding Agent</div>
      <div style="color:#8B949E;font-size:0.72rem;margin-top:3px;">
        The one remaining Phase 8 page — GitHub issue to fix, full autonomous coding loop
      </div>
    </div>
    <div style="flex:1;min-width:180px;background:rgba(255,179,71,0.08);border:1px solid rgba(255,179,71,0.3);
                border-radius:8px;padding:10px 14px;">
      <div style="color:#FFB347;font-size:0.65rem;font-weight:700;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:4px;">Step 2 — Phase 100</div>
      <div style="color:#E6EDF3;font-size:0.85rem;font-weight:600;">Quiz Hub</div>
      <div style="color:#8B949E;font-size:0.72rem;margin-top:3px;">
        Test your knowledge across all 16 phases — Gemini-powered fresh questions every run
      </div>
    </div>
    <div style="flex:1;min-width:180px;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
                border-radius:8px;padding:10px 14px;">
      <div style="color:#00D4FF;font-size:0.65rem;font-weight:700;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:4px;">Step 3 — Phase 11</div>
      <div style="color:#E6EDF3;font-size:0.85rem;font-weight:600;">Managed Platforms</div>
      <div style="color:#8B949E;font-size:0.72rem;margin-top:3px;">
        Vertex AI · Azure · Bedrock · OpenAI Assistants — production deployment overviews
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOUNDATIONS ────────────────────────────────────────────────────────────────
section("PHASE 0 — FOUNDATIONS", "#00FF9F")
grid(
    card("Phase 0", "Hello Gemini",
         "API setup · first live LLM call · verify everything works",
         "Complete", "b-done", "pcard-complete", "#00FF9F"),
    card("Phase 0", "Agent Anatomy",
         "What is inside an agent · memory · tools · HITL · A2A · MCP interfaces",
         "Complete", "b-done", "pcard-complete", "#00FF9F"),
    card("Phase 0", "Learning Insights",
         "Course philosophy · Anthropic + Andrew Ng sources · why API-first",
         "Complete", "b-done", "pcard-complete", "#00FF9F"),
)

# ── AUGMENTED LLM ──────────────────────────────────────────────────────────────
section("PHASE 1 — AUGMENTED LLM", "#00FF9F")
grid(
    card("Phase 1", "Augmented LLM",
         "1a Plain LLM · 1b Memory · 1c Tools · 1d Mini Agent — evolution to agency",
         "Complete", "b-done", "pcard-complete", "#00FF9F"),
)

# ── WORKFLOW PATTERNS ──────────────────────────────────────────────────────────
section("PHASE 2 — WORKFLOW PATTERNS", "#00D4FF")
grid(
    card("2a", "Prompt Chaining",
         "Sequential steps · gate checks · each output feeds the next",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("2b", "Routing",
         "Classify first · route to one specialist · unused branches = zero cost",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("2c", "Parallelization",
         "Sectioning + Voting · ThreadPoolExecutor · parallel LLM calls",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("2d", "Orchestrator-Workers",
         "Orchestrator plans dynamically · workers execute in parallel",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("2e", "Evaluator-Optimizer",
         "Generator + Evaluator loop · iterate until quality threshold",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
)

# ── CORE AGENT PATTERNS ────────────────────────────────────────────────────────
section("PHASE 3 — CORE AGENT PATTERNS  ·  Complete", "#B47FFF")
grid(
    card("3a", "ReAct Agent",
         "Think → Act → Observe loop · JSON reasoning · model controls its own process",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("3b", "Reflection Agent",
         "Andrew Ng Pattern 1 · self-critique loop · code validation · structured critique",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("3c", "Planning Agent",
         "Andrew Ng Pattern 3 · explicit Plan-and-Execute · adaptive replanning mid-run",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("3d", "Code Execution Tool",
         "Andrew Ng Pattern 2 extension · Python REPL as tool · agent writes + runs code",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("3e", "Pattern Decision Guide",
         "All 9 patterns compared · when to use each · decision flowchart · trade-off tables",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
)

# ── TRUST & SAFETY ─────────────────────────────────────────────────────────────
section("PHASE 4 — TRUST & SAFETY  ·  Complete", "#FF6384")
grid(
    card("4a", "Guardrails",
         "Input + output safety · PII detection · prompt injection · financial compliance",
         "Complete", "b-done", "pcard-complete", "#FF6384"),
    card("4b", "Human-in-the-Loop",
         "Checkpoint pattern · approve / reject / modify · audit trail · risk gating",
         "Complete", "b-done", "pcard-complete", "#FF6384"),
    card("4c", "LLM-as-Judge",
         "Independent quality gate · 4-criteria scoring · PASS / REVIEW / FAIL routing",
         "Complete", "b-done", "pcard-complete", "#FF6384"),
    card("4d", "Evaluation Framework",
         "Systematic evals · golden datasets · metrics · regression testing across versions",
         "Complete", "b-done", "pcard-complete", "#FF6384"),
)

# ── KNOWLEDGE & MEMORY ─────────────────────────────────────────────────────────
section("PHASE 5 — KNOWLEDGE & MEMORY  ·  Complete", "#FFB347")
grid(
    card("5a", "RAG Agent",
         "Retrieve → Augment → Generate · gemini-embedding-001 · cosine search · grounded answers",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
    card("5b", "Long-term Memory",
         "Vector store · in-memory · gemini-embedding-001 · semantic recall across sessions",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
)

# ── MULTI-AGENT & PROTOCOLS ────────────────────────────────────────────────────
section("PHASE 6 — MULTI-AGENT & PROTOCOLS  ·  Complete", "#00D4FF")
grid(
    card("6a", "Multi-Agent",
         "Andrew Ng Pattern 4 · root + sub-agents · parallel delegation · vs Orchestrator-Workers",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("6b", "MCP Protocol",
         "Anthropic Nov 2024 · JSON-RPC · initialize/list_tools/call_tool · swappable servers",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("6c", "A2A Protocol",
         "Google Apr 2025 · Agent Card · task lifecycle · submit/stream/complete",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
    card("6d", "Agent Comms",
         "Raw vs MCP vs A2A · decision guide · production architecture · same task 3 ways",
         "Complete", "b-done", "pcard-complete", "#00D4FF"),
)

# ── PRODUCTION OPERATIONS ──────────────────────────────────────────────────────
section("PHASE 7 — PRODUCTION OPERATIONS  ·  Complete", "#5D6D7E")
grid(
    card("7a", "Observability & Tracing",
         "TraceCollector · latency · token counts · cost per query · JSON trace log",
         "Complete", "b-done", "pcard-complete", "#5D6D7E"),
    card("7b", "Cost & Latency",
         "count_tokens() · prompt caching sim · model routing · latency breakdown",
         "Complete", "b-done", "pcard-complete", "#5D6D7E"),
    card("7c", "Error Analysis",
         "5-type taxonomy · broken vs fixed · auto-diagnosis · fix playbook",
         "Complete", "b-done", "pcard-complete", "#5D6D7E"),
    card("7d", "Stateful Task Management",
         "Checkpoint/resume · idempotency · dead-letter queue · task lifecycle states",
         "Complete", "b-done", "pcard-complete", "#5D6D7E"),
)

# ── AGENTS IN PRACTICE ─────────────────────────────────────────────────────────
section("PHASE 8 — AGENTS IN PRACTICE  ·  5 of 6 complete", "#FFB347")
grid(
    card("8a", "Customer Support Agent",
         "Full pipeline: 4a+5b+5a+3a+4c+4b+7a — all patterns combined in one production system",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
    card("8a.1", "Elite Multi-Agent System",
         "All 13 patterns simultaneously: MCP + A2A + Reflection + Planning + Code Exec + RAG + Memory",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
    card("8b", "Coding Agent",
         "GitHub issue → write fix → run tests → iterate · full autonomous loop",
         "Coming", "b-soon", "pcard-coming", "#6E7681"),
    card("8c", "Computer Use Agents",
         "Screenshot → action loop · Playwright pattern · sandboxing · visual perception",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
    card("8d", "Multimodal Agents",
         "Image Q&A · document extraction · chart analysis · Gemini vision input",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
    card("8e", "Enterprise Event-Driven",
         "Kafka consumer/producer · fan-out · dead-letter · event replay · async patterns",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
)

# ── BEST PRACTICES ─────────────────────────────────────────────────────────────
section("PHASE 9 — BEST PRACTICES  ·  Anthropic Appendix 2", "#FFB347")
grid(
    card("9", "Best Practices",
         "Tool design · prompt engineering · fine-tuning vs RAG decision guide · pre-flight checklist",
         "Complete", "b-done", "pcard-complete", "#FFB347"),
)

# ── FRAMEWORKS ─────────────────────────────────────────────────────────────────
section("PHASE 10 — FRAMEWORKS LAYER  ·  Complete", "#B47FFF")
st.markdown("""<div style="background:rgba(180,127,255,0.05);border:1px solid rgba(180,127,255,0.2);
border-radius:10px;padding:12px 16px;margin-bottom:12px;color:#8B949E;font-size:0.82rem;line-height:1.6">
&#128161; <strong style="color:#B47FFF">Why frameworks come last:</strong>
Anthropic and Andrew Ng both recommend learning API-first.
By Phase 10 you understand every pattern — frameworks become an acceleration, not a crutch.
You can read LangGraph, CrewAI, and ADK source code and understand exactly what they do.
</div>""", unsafe_allow_html=True)
grid(
    card("10a", "LangGraph — Workflows",
         "Phase 2 patterns as typed StateGraph · nodes · edges · conditional branching",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10b", "LangGraph — Agents",
         "create_react_agent · HITL via interrupt_before · checkpointing · streaming",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10c", "LangSmith",
         "Auto-tracing · golden dataset evals · cost dashboards · regression runs",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10d", "LangChain LCEL",
         "Pipe syntax · Phase 1b memory · Phase 2a chaining · Phase 5a RAG as 4 components",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10e", "Google ADK",
         "SequentialAgent · ParallelAgent · LoopAgent · sub-agent delegation",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10g", "CrewAI",
         "Role-based crews · role + backstory + goal · Process.sequential / hierarchical",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
    card("10f", "Framework Comparison",
         "LangGraph vs CrewAI vs ADK vs AutoGen vs raw SDK · decision guide · trade-offs",
         "Complete", "b-done", "pcard-complete", "#B47FFF"),
)

# ── MANAGED PLATFORMS ──────────────────────────────────────────────────────────
section("PHASE 11 — MANAGED PLATFORMS  ·  cursory overview", "#00D4FF")
st.markdown("""<div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
border-radius:10px;padding:12px 16px;margin-bottom:12px;color:#8B949E;font-size:0.82rem;line-height:1.6">
&#9729; <strong style="color:#00D4FF">When to stop building infrastructure:</strong>
Managed platforms handle scaling, availability, and tooling for you.
Overview only — enough to evaluate which platform fits your production needs.
</div>""", unsafe_allow_html=True)
grid(
    card("11a", "Vertex AI Agents",
         "Google's managed agent engine · production hosting · Gemini native",
         "Cloud", "b-cloud", "pcard-future", "#00D4FF"),
    card("11b", "Azure AI Agent",
         "Microsoft's agent service · enterprise integration · OpenAI models",
         "Cloud", "b-cloud", "pcard-future", "#00D4FF"),
    card("11c", "AWS Bedrock",
         "Amazon's agent framework · multi-model · Claude + Titan + tools",
         "Cloud", "b-cloud", "pcard-future", "#00D4FF"),
    card("11d", "OpenAI Assistants",
         "Threads · runs · file search · code interpreter · vector stores",
         "Cloud", "b-cloud", "pcard-future", "#00D4FF"),
    card("11e", "Platform Comparison",
         "Decision guide · cost model · vendor lock-in · when to use which",
         "Cloud", "b-cloud", "pcard-future", "#00D4FF"),
)

# ── Learning path summary ──────────────────────────────────────────────────────
st.markdown("""
<div class="path-arrow">— — — — — — — — — — — — — — — — —</div>
<div style="text-align:center; padding: 20px 0 8px 0; color:#8B949E; font-size:0.8rem; letter-spacing:1px;">
  FIRST PRINCIPLES
  <span style="color:#21262D; margin:0 16px">&#8594;&#8594;&#8594;</span>
  PATTERNS
  <span style="color:#21262D; margin:0 16px">&#8594;&#8594;&#8594;</span>
  FRAMEWORKS
  <span style="color:#21262D; margin:0 16px">&#8594;&#8594;&#8594;</span>
  MANAGED PLATFORMS
</div>
""", unsafe_allow_html=True)
