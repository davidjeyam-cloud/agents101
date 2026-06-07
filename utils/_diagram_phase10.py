"""
Phase 10 diagram functions — appended to diagrams.py at import time via __init__.
Kept separate to avoid the multi-match problem in the large diagrams.py file.
"""
# These functions are injected into utils.diagrams by utils/__init__.py
# Do NOT import this file directly — use: from utils.diagrams import diagram_langgraph_*

import io
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def _ph10_diagrams(C, W, H, _fig, _box, _arrow, _agent_banner, _journey_bar,
                   _agent_def_footer, _to_bytes):
    """Returns (diagram_langgraph_workflows, diagram_google_adk, diagram_lang_arch_map).

    diagram_langgraph_agents / _memory / _tools_security / _platform / diagram_langsmith /
    diagram_langchain / diagram_framework_compare were replaced by static
    arch-diagram-skill JPEGs in docs/images/arch_*.jpg —
    see pages 06b, 06a1, 06a2, 06a3, 06c, 06d, 06f."""

    def diagram_langgraph_workflows() -> bytes:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
        fig.patch.set_facecolor(C["bg"])

        def bx(ax, cx, cy, w, h, lines, fc, fs=8):
            p = FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.08",
                               facecolor=fc, edgecolor="white", linewidth=2, zorder=3)
            ax.add_patch(p)
            ax.text(cx, cy, "\n".join(lines), ha="center", va="center", fontsize=fs,
                    color="white", fontweight="bold", zorder=4,
                    multialignment="center", linespacing=1.3)

        def ar(ax, x1, y1, x2, y2, lbl=""):
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.6,
                                        mutation_scale=12), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.08, (y1+y2)/2, lbl, fontsize=6.5,
                        color=C["arrow"], style="italic")

        for ax in axes:
            ax.set_xlim(0, 5); ax.set_ylim(0, 5.2); ax.axis("off")
            ax.set_facecolor(C["bg"])

        ax = axes[0]
        ax.add_patch(FancyBboxPatch((0, 4.8), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["dim"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 4.99, "What you built in Phase 2 (raw Python)", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        bx(ax, 2.5, 4.22, 3.6, 0.44, ["task = classify(input)"], C["input"])
        ar(ax, 2.5, 4.0, 2.5, 3.60)
        bx(ax, 2.5, 3.30, 3.6, 0.44, ["out1 = llm(step1_prompt)"], C["llm"])
        ar(ax, 2.5, 3.08, 2.5, 2.68)
        bx(ax, 2.5, 2.38, 3.6, 0.44, ["out2 = llm(step2_prompt + out1)"], C["memory"])
        ar(ax, 2.5, 2.16, 2.5, 1.76)
        bx(ax, 2.5, 1.46, 3.6, 0.44, ["out3 = llm(step3_prompt + out2)"], C["tools"])
        ar(ax, 2.5, 1.24, 2.5, 0.84)
        bx(ax, 2.5, 0.54, 3.0, 0.40, ["return out3"], C["output"])
        ax.text(2.5, 0.1, "manual dict-passing  |  no typed state  |  no streaming",
                ha="center", fontsize=6.5, color=C["dim"], style="italic")

        ax = axes[1]
        ax.add_patch(FancyBboxPatch((0, 4.8), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 4.99, "LangGraph — same logic, better plumbing", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        bx(ax, 2.5, 4.22, 3.8, 0.44, ["graph = StateGraph(State)"], C["input"])
        ar(ax, 2.5, 4.0, 2.5, 3.60)
        bx(ax, 2.5, 3.30, 3.8, 0.52, ["node_A   graph.add_node('A', fn_A)"], C["llm"])
        ar(ax, 2.5, 3.04, 2.5, 2.64)
        bx(ax, 2.5, 2.34, 3.8, 0.52, ["node_B   graph.add_edge('A','B')"], C["memory"])
        ar(ax, 2.5, 2.08, 2.5, 1.68)
        bx(ax, 2.5, 1.38, 3.8, 0.52, ["node_C   graph.add_edge('B','C')"], C["tools"])
        ar(ax, 2.5, 1.12, 2.5, 0.72)
        bx(ax, 2.5, 0.44, 3.8, 0.44, ["compiled = graph.compile(checkpointer)"], C["agent_yes"])
        ax.text(2.5, 0.05, "typed state  |  streaming  |  persistence  |  HITL-ready",
                ha="center", fontsize=6.5, color=C["agent_yes"], style="italic")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    def diagram_google_adk() -> bytes:
        """
        2-panel diagram for Phase 10e — Google ADK.
        Left:  The 3 raw patterns you already built (Phases 2a / 2c / 3).
        Right: ADK's 3 agent types that wrap those exact patterns.
        """
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
        fig.patch.set_facecolor(C["bg"])

        def bx(ax, cx, cy, w, h, lines, fc, fs=7.5):
            p = FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.08",
                               facecolor=fc, edgecolor="white", linewidth=2, zorder=3)
            ax.add_patch(p)
            ax.text(cx, cy, "\n".join(lines) if isinstance(lines, list) else lines,
                    ha="center", va="center", fontsize=fs, color="white",
                    fontweight="bold", zorder=4, multialignment="center", linespacing=1.3)

        def ar(ax, x1, y1, x2, y2, lbl="", col=None):
            col = col or C["arrow"]
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6,
                                        mutation_scale=12), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.12, (y1+y2)/2, lbl,
                        fontsize=6, color=col, style="italic")

        for ax in axes:
            ax.set_xlim(0, 5); ax.set_ylim(0, 5.4); ax.axis("off")
            ax.set_facecolor(C["bg"])

        # ── LEFT — raw patterns ────────────────────────────────────────────────
        ax = axes[0]
        ax.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["dim"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 5.19, "What you built in Phases 2a · 2c · 3 (raw Python)",
                ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")

        # Sequential (Phase 2a)
        bx(ax, 2.5, 4.38, 4.0, 0.50,
           ["Phase 2a — Prompt Chaining",
            "out2 = llm(prompt + out1)  # step by step"],
           C["input"], fs=7)
        ax.text(0.38, 4.38, "→ ADK", ha="center", fontsize=6.5,
                color=C["input"], style="italic")

        ar(ax, 2.5, 4.12, 2.5, 3.78)

        # Parallel (Phase 2c)
        bx(ax, 2.5, 3.48, 4.0, 0.50,
           ["Phase 2c — Parallelization",
            "ThreadPoolExecutor: 3 calls at once"],
           C["memory"], fs=7)
        ax.text(0.38, 3.48, "→ ADK", ha="center", fontsize=6.5,
                color=C["memory"], style="italic")

        ar(ax, 2.5, 3.22, 2.5, 2.88)

        # Loop (Phase 3)
        bx(ax, 2.5, 2.58, 4.0, 0.50,
           ["Phase 3 — ReAct / Planning",
            "while not done: think → act → observe"],
           C["loop"], fs=7)
        ax.text(0.38, 2.58, "→ ADK", ha="center", fontsize=6.5,
                color=C["loop"], style="italic")

        ar(ax, 2.5, 2.32, 2.5, 1.98)

        # Sub-agents (Phase 6a)
        bx(ax, 2.5, 1.68, 4.0, 0.50,
           ["Phase 6a — Multi-Agent",
            "root.delegate(sub_agent, task)"],
           C["tools"], fs=7)
        ax.text(0.38, 1.68, "→ ADK", ha="center", fontsize=6.5,
                color=C["tools"], style="italic")

        ax.text(2.5, 0.48, "every pattern written as imperative Python  ·  you own all orchestration",
                ha="center", fontsize=6.5, color=C["dim"], style="italic")

        # ── RIGHT — ADK agent types ────────────────────────────────────────────
        ax = axes[1]
        ax.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 5.19, "Google ADK — same patterns as typed agent classes",
                ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")

        # SequentialAgent
        bx(ax, 2.5, 4.38, 4.2, 0.50,
           ["SequentialAgent(sub_agents=[A, B, C])",
            "runs A → B → C in order, passing output"],
           C["input"], fs=7)
        ax.text(0.38, 4.38, "≡ 2a", ha="center", fontsize=8,
                color=C["input"], fontweight="bold")

        ar(ax, 2.5, 4.12, 2.5, 3.78, col=C["arrow"])

        # ParallelAgent
        bx(ax, 2.5, 3.48, 4.2, 0.50,
           ["ParallelAgent(sub_agents=[A, B, C])",
            "runs A, B, C concurrently, merges results"],
           C["memory"], fs=7)
        ax.text(0.38, 3.48, "≡ 2c", ha="center", fontsize=8,
                color=C["memory"], fontweight="bold")

        ar(ax, 2.5, 3.22, 2.5, 2.88, col=C["arrow"])

        # LoopAgent
        bx(ax, 2.5, 2.58, 4.2, 0.50,
           ["LoopAgent(sub_agent=A, max_iterations=5)",
            "loops A until escalate_to_parent=True"],
           C["loop"], fs=7)
        ax.text(0.38, 2.58, "≡ 3", ha="center", fontsize=8,
                color=C["loop"], fontweight="bold")

        ar(ax, 2.5, 2.32, 2.5, 1.98, col=C["arrow"])

        # Runner
        bx(ax, 2.5, 1.68, 4.2, 0.50,
           ["Runner(agent=root, session_service=InMemorySessionService())",
            "executes agent + manages sessions + events"],
           C["agent_yes"], fs=7)
        ax.text(0.38, 1.68, "Infra", ha="center", fontsize=7,
                color=C["agent_yes"], fontweight="bold")

        ax.text(2.5, 0.48,
                "ADK provides: typed orchestration  ·  session service  ·  event streaming",
                ha="center", fontsize=6.5, color=C["agent_yes"], style="italic")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    # ─────────────────────────────────────────────────────────────────────────
    # NEW: Full Architecture Map (for 10a anchor)
    # ─────────────────────────────────────────────────────────────────────────
    def diagram_lang_arch_map() -> bytes:
        """
        Full LangChain + LangGraph architecture map in the style of the reference
        diagram: 6 layers with side panels (LangSmith, Security, Platform, Agent Loop).
        Each layer annotated with which course phase covers it.
        """
        fig = plt.figure(figsize=(18, 11))
        fig.patch.set_facecolor("#F0F4F8")
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 18); ax.set_ylim(0, 11)
        ax.axis("off"); ax.set_facecolor("#F0F4F8")

        # Color palette
        L1 = "#1B4F72"; L2 = "#1A6B3A"; L3 = "#A84300"
        L4 = "#6C3483"; L5 = "#0E7A5A"; L6 = "#1C2833"
        LS = "#117A65"; SEC = "#922B21"; PLT = "#1A5276"; AGL = "#7E5109"

        def srect(x, y, w, h, col, alpha=1.0, ec="white"):
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                         facecolor=col, edgecolor=ec, lw=1.2, alpha=alpha, zorder=2))

        def sbox(cx, cy, w, h, title, lines, col, fs_title=7.5, fs_body=6.0):
            srect(cx - w/2, cy - h/2, w, h, col, alpha=0.92)
            ax.text(cx, cy + h/2 - 0.22, title, ha="center", va="center",
                    fontsize=fs_title, color="white", fontweight="bold", zorder=4)
            for i, ln in enumerate(lines):
                ax.text(cx, cy + h/2 - 0.46 - i*0.21, ln, ha="center",
                        fontsize=fs_body, color="white", alpha=0.92, zorder=4)

        def llabel(y_bot, h, num, name, col):
            srect(0.08, y_bot, 1.9, h, col, alpha=0.95)
            ax.text(1.03, y_bot + h*0.66, num, ha="center", va="center",
                    fontsize=18, color="white", fontweight="bold", zorder=4)
            ax.text(1.03, y_bot + h*0.33, name, ha="center", va="center",
                    fontsize=7, color="white", fontweight="bold", zorder=4,
                    multialignment="center", linespacing=1.3)

        # ── Title ──────────────────────────────────────────────────────────────
        ax.add_patch(FancyBboxPatch((0.08, 10.35), 13.8, 0.57,
                     boxstyle="round,pad=0.05", facecolor="#0D1B2A", edgecolor="none", zorder=5))
        ax.text(7.0, 10.64, "LangChain + LangGraph  —  Agentic AI Architecture",
                ha="center", va="center", fontsize=15, color="white", fontweight="bold", zorder=6)
        ax.text(7.0, 10.23, "STATEFUL  ·  GRAPH-DRIVEN  ·  TOOL-USING  ·  PRODUCTION-READY",
                ha="center", fontsize=8, color="#566573", zorder=3)

        # ── Layer layout: (y_bot, height, num, label, colour) ──────────────────
        LAYERS = [(8.4, 1.8, "1", "ENTRY\nLAYER", L1),
                  (6.1, 2.2, "2", "ORCHESTRATION\nLAYER", L2),
                  (3.9, 2.1, "3", "AGENT\nNODES", L3),
                  (2.5, 1.3, "4", "MEMORY &\nCONTEXT", L4),
                  (1.2, 1.2, "5", "TOOLS\nLAYER", L5),
                  (0.1, 1.0, "6", "MODEL\nLAYER", L6)]
        for yb, h, num, name, col in LAYERS:
            ax.add_patch(FancyBboxPatch((2.05, yb), 11.6, h, boxstyle="round,pad=0.04",
                         facecolor=col, edgecolor="none", alpha=0.10, zorder=1))
            llabel(yb, h, num, name, col)
            ax.plot([0.08, 13.75], [yb, yb], color="#CBD5E1", lw=0.5, zorder=1)

        # ── Layer 1: Entry ──────────────────────────────────────────────────────
        for cx, ti, items in [
            (3.2,  "Web / API",       ["REST/GraphQL", "FastAPI+LangServe", "Studio UI"]),
            (5.3,  "Chat Interface",  ["HumanMessage", "BaseMessage schema", "Streaming tokens"]),
            (7.4,  "Scheduled/Event", ["Cron triggers", "Webhooks", "LangGraph Crons"]),
            (9.5,  "Document Loader", ["DocumentLoader", "TextSplitter", "PDF/CSV/HTML"]),
            (11.9, "LangSmith Entry", ["Trace at entry", "Cost per run", "LANGCHAIN_V2"]),
        ]:
            sbox(cx, 9.32, 1.95, 1.05, ti, items, L1)

        # ── Layer 2: Orchestration ──────────────────────────────────────────────
        sbox(3.8,  7.95, 3.0, 1.0, "StateGraph / MessageGraph",
             ["compile() → runnable graph", "add_node/edge/conditional_edges", "START/END sentinels · Subgraphs"], L2)
        sbox(7.3,  7.95, 2.8, 1.0, "Shared State (TypedDict)",
             ["Annotated fields with reducers", "add_messages reducer (append)", "Snapshot at every node step"], L2)
        sbox(10.5, 7.95, 2.8, 1.0, "Conditional Routing",
             ["LLM-decided conditional edges", "Map-reduce parallel fan-out", "Deferred nodes (v0.4+)"], L2)
        # Execution flow bar
        ax.add_patch(FancyBboxPatch((2.1, 6.18), 11.55, 0.68,
                     boxstyle="round,pad=0.04", facecolor="#0D1B2A", edgecolor="none", alpha=0.72, zorder=2))
        FLOW = [("START","#2471A3"), ("intent_class",L2), ("planner_node",L2),
                ("cond_edge?","#CA6F1E"), ("agent_node",L3), ("tool_node",L5), ("END","#1E8449")]
        fxs = [2.75, 4.25, 5.8, 7.35, 8.9, 10.4, 11.75]
        for i, ((lbl, col), fx) in enumerate(zip(FLOW, fxs)):
            w = max(0.85, len(lbl)*0.088 + 0.28)
            ax.add_patch(FancyBboxPatch((fx-w/2, 6.28), w, 0.44,
                         boxstyle="round,pad=0.05", facecolor=col, edgecolor="white", lw=0.8, zorder=4))
            ax.text(fx, 6.5, lbl, ha="center", va="center",
                    fontsize=6.5, color="white", fontweight="bold", zorder=5)
            if i < len(FLOW)-1:
                ax.annotate("", xy=(fxs[i+1]-max(0.85,len(FLOW[i+1][0])*0.088+0.28)/2-0.01, 6.5),
                            xytext=(fx+w/2+0.01, 6.5),
                            arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.1, mutation_scale=7), zorder=5)

        # ── Layer 3: Agent Nodes ────────────────────────────────────────────────
        ROW1 = [(3.0,"Research Agent",["Multi-source docs","web+LangSmith","→ Ph 7a"]),
                (4.85,"Planner Agent",["Plan-and-execute","s1 planning node","→ Ph 3c"]),
                (6.7,"Code Agent",["Code generation","PythonREPL tool","→ Ph 3d"]),
                (8.55,"Supervisor Agent",["Routes sub-agents","aggregates results","→ Ph 6a"]),
                (10.4,"Guard Agent",["Prompt injection","OAP policy check","→ Ph 4a"]),
                (12.25,"ReAct Agent",["create_react_agent","reason+act+observe","→ Ph 3a"])]
        for cx, ti, items in ROW1:
            sbox(cx, 5.55, 1.7, 1.0, ti, items, L3)
        ROW2 = [(3.85,"Web Agent",["Tavily+SerpAPI","BraveSearch","real-time news"]),
                (5.7,"Data Analyst",["SQL agent","pandas+charts","structured out"]),
                (7.55,"Writer Agent",["Report writing","Pydantic schema","structured out"]),
                (9.4,"Crew Coord.",["Role-based crew","async multi-agent","CrewAI → Ph 10g"]),
                (11.25,"Each node:",["Receives State","Acts (tool call)","Returns State"])]
        for cx, ti, items in ROW2:
            sbox(cx, 4.35, 1.7, 0.85, ti, items, "#2C3E50")

        # ── Layer 4: Memory & Context ───────────────────────────────────────────
        for cx, ti, items in [
            (3.15,"Checkpointer",["MemorySaver → SqliteSaver","RedisSaver → PostgresSaver","Thread-scoped snapshots"]),
            (5.6,"Memory Store",["InMemoryStore (short)","LangMem cross-session","User prefs + history"]),
            (8.05,"Vector Store (RAG)",["FAISS · Chroma · pgvector","Similarity search + MMR","→ Phase 5a course"]),
            (10.5,"Conv. Memory",["ConvBufferMemory","ConvSummaryMemory","add_messages reducer"]),
            (12.65,"Knowledge Graph",["Entity extraction","Neo4j + LangChain","GraphRAG patterns"]),
        ]:
            sbox(cx, 3.14, 2.1, 1.02, ti, items, L4)

        # ── Layer 5: Tools ──────────────────────────────────────────────────────
        for cx, ti, items in [
            (2.9, "Search Tools",["TavilySearch","SerpAPI · ArxivTool","→ live web search"]),
            (4.8, "Code Execution",["PythonREPL","ShellTool · E2B","Docker executor"]),
            (6.7, "API / HTTP",["RequestsTool","OpenAPI toolkit","@tool decorator"]),
            (8.6, "File Tools",["ReadFileTool","WriteFileTool","FileManagement"]),
            (10.5,"MCP Servers",["langchain_mcp_adapters","any MCP as tool","SSE / stdio"]),
            (12.4,"ToolNode",["Auto-routes calls","LLM.bind_tools()","→ Phase 1c"]),
        ]:
            sbox(cx, 1.83, 1.75, 1.0, ti, items, L5)

        # ── Layer 6: Model Layer ────────────────────────────────────────────────
        for cx, ti, items in [
            (3.4,"Chat LLMs",["Gemini 2.5 Flash","Claude Sonnet · GPT-4o","tool calling required"]),
            (6.15,"Embedding Models",["gemini-embedding-001","text-embedding-3","HuggingFace"]),
            (8.9,"Structured Output",["Pydantic models","TypedDict · JSON Schema",".with_structured_output()"]),
            (11.65,"Guardrail Models",["NeMo Guardrails","Guardrails AI","toxicity + bias"]),
        ]:
            sbox(cx, 0.63, 2.45, 0.84, ti, items, L6)

        # ── RIGHT PANELS ────────────────────────────────────────────────────────
        # LangSmith
        srect(13.85, 7.45, 4.05, 2.87, LS, alpha=0.92)
        ax.text(15.87, 10.18, "LangSmith Observability", ha="center",
                fontsize=8.5, color="white", fontweight="bold", zorder=5)
        for y, t in [(9.8,"Tracing: every node, LLM, tool call"), (9.42,"Evaluation: datasets + LLM-as-Judge"),
                     (9.04,"Cost/Latency: per run, per project"),(8.66,"Alerts: regression + feedback loop"),
                     (8.28,"Prompt Hub: version + hub.pull()"), (7.9, "→ Phase 7a (automated)")]:
            ax.text(14.0, y, "  "+t, fontsize=6.7, color="white", zorder=5, va="center")
        # Security
        srect(13.85, 5.7, 4.05, 1.65, SEC, alpha=0.88)
        ax.text(15.87, 7.2, "Security & Governance", ha="center",
                fontsize=8.5, color="white", fontweight="bold", zorder=5)
        for y, t in [(6.8,"API Key: env vars + SecretStr"),(6.42,"Guardrails: NeMo integration"),
                     (6.04,"HITL: Command(resume=...) pattern"),(5.8, "Audit: LangSmith full reproducibility")]:
            ax.text(14.0, y, "  "+t, fontsize=6.7, color="white", zorder=5, va="center")
        # LangGraph Platform
        srect(13.85, 3.9, 4.05, 1.7, PLT, alpha=0.88)
        ax.text(15.87, 5.45, "LangGraph Platform", ha="center",
                fontsize=8.5, color="white", fontweight="bold", zorder=5)
        for y, t in [(5.05,"Deploy: 1-click, autoscale (GA May 2025)"),(4.65,"Durable: resume after crash"),
                     (4.25,"Studio UI: visual graph debugger"),(4.0, "API Server: REST+SSE from graph")]:
            ax.text(14.0, y, "  "+t, fontsize=6.7, color="white", zorder=5, va="center")
        # Agent Loop
        srect(13.85, 0.1, 4.05, 3.7, AGL, alpha=0.88)
        ax.text(15.87, 3.65, "LangGraph Agent Loop", ha="center",
                fontsize=8.5, color="white", fontweight="bold", zorder=5)
        loop_steps = [("Perceive",L1,"State loaded from checkpointer"),
                      ("Reason",  L2,"LLM call → AIMessage(tool_calls)"),
                      ("Act",     L5,"ToolNode executes tool_calls"),
                      ("Evaluate",L3,"conditional_edge → agent or END"),
                      ("Persist", L4,"State snapshot saved to checkpointer")]
        ly_positions = [3.1, 2.52, 1.94, 1.36, 0.78]
        for (step, scol, desc), ly in zip(loop_steps, ly_positions):
            ax.add_patch(FancyBboxPatch((13.95, ly-0.22), 3.85, 0.44,
                         boxstyle="round,pad=0.05", facecolor=scol, edgecolor="white",
                         lw=0.8, alpha=0.9, zorder=4))
            ax.text(14.5, ly, step, ha="left", va="center",
                    fontsize=7.5, color="white", fontweight="bold", zorder=5)
            ax.text(17.75, ly, desc, ha="right", va="center",
                    fontsize=6.2, color="white", zorder=5)
            if ly > 0.78:
                next_ly = ly_positions[ly_positions.index(ly)+1]
                ax.annotate("", xy=(15.87, next_ly+0.23), xytext=(15.87, ly-0.22),
                            arrowprops=dict(arrowstyle="-|>", color="white", lw=0.9,
                                           mutation_scale=7), zorder=5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    return (diagram_langgraph_workflows, diagram_google_adk, diagram_lang_arch_map)
