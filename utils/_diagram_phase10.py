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
    """Returns (diagram_langgraph_workflows, diagram_langgraph_agents,
                diagram_langsmith, diagram_langchain)."""

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

    def diagram_langgraph_agents() -> bytes:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
        fig.patch.set_facecolor(C["bg"])

        def bx(ax, cx, cy, w, h, lines, fc, fs=7.5):
            p = FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.08",
                               facecolor=fc, edgecolor="white", linewidth=2, zorder=3)
            ax.add_patch(p)
            ax.text(cx, cy, "\n".join(lines), ha="center", va="center", fontsize=fs,
                    color="white", fontweight="bold", zorder=4,
                    multialignment="center", linespacing=1.3)

        def ar(ax, x1, y1, x2, y2, lbl="", col=None):
            col = col or C["arrow"]
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6,
                                        mutation_scale=12), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.1, (y1+y2)/2, lbl, fontsize=6, color=col, style="italic")

        for ax in axes:
            ax.set_xlim(0, 5); ax.set_ylim(0, 5.4); ax.axis("off")
            ax.set_facecolor(C["bg"])

        ax = axes[0]
        ax.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["dim"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 5.19, "What you built in Phase 3 (your loop)", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        bx(ax, 2.5, 4.4, 3.6, 0.48, ["while iteration < MAX_ITER:", "  response = llm(history)"], C["llm"])
        ar(ax, 2.5, 4.16, 2.5, 3.76)
        bx(ax, 2.5, 3.48, 3.6, 0.48, ["if not response.tool_calls: break"], C["agent_yes"])
        ar(ax, 2.5, 3.24, 2.5, 2.84, "tool call")
        bx(ax, 2.5, 2.56, 3.6, 0.48, ["result = execute_tool(call)", "history.append(result)"], C["tools"])
        ax.annotate("", xy=(0.7, 4.4), xytext=(0.7, 2.56),
                    arrowprops=dict(arrowstyle="-|>", color=C["loop"], lw=1.6,
                                    connectionstyle="arc3,rad=0"), zorder=5)
        ax.text(0.32, 3.48, "loop", fontsize=6.5, color=C["loop"], rotation=90, va="center")
        bx(ax, 2.5, 1.6, 3.6, 0.48, ["HITL: manual ~40 lines", "of checkpoint code"], C["agent_no"])
        ar(ax, 2.5, 1.36, 2.5, 0.96)
        bx(ax, 2.5, 0.68, 3.0, 0.44, ["return final_answer"], C["output"])

        ax = axes[1]
        ax.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38, boxstyle="round,pad=0.05",
                                    facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5, 5.19, "LangGraph — your loop as a typed graph", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        bx(ax, 2.5, 4.4, 3.8, 0.48,
           ["agent = create_react_agent(llm, tools,", "  checkpointer=MemorySaver())"], C["llm"])
        ar(ax, 2.5, 4.16, 2.5, 3.76, "auto loop")
        bx(ax, 2.5, 3.48, 3.8, 0.48,
           ["ToolNode handles all tool dispatch", "graph cycles automatically"], C["tools"])
        ar(ax, 2.5, 3.24, 2.5, 2.84)
        bx(ax, 2.5, 2.56, 3.8, 0.48,
           ["interrupt_before=['tools']", "# HITL = 2 lines"], C["agent_yes"])
        ar(ax, 2.5, 2.32, 2.5, 1.92)
        bx(ax, 2.5, 1.64, 3.8, 0.48,
           ["graph.stream(input, config)", "# yields each node result live"], C["memory"])
        ar(ax, 2.5, 1.40, 2.5, 1.00)
        bx(ax, 2.5, 0.72, 3.0, 0.44, ["final_state['messages']"], C["output"])
        ax.text(2.5, 0.12, "streaming  |  persistence  |  HITL=2 lines  |  recursion_limit guard",
                ha="center", fontsize=6.5, color=C["agent_yes"], style="italic")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    def diagram_langsmith() -> bytes:
        fig, ax = _fig()
        _agent_banner(ax, is_agent=False,
                      why="LangSmith wraps your agent — observability is infrastructure, not your code")
        ax.text(W/2, 3.75, "Phase 10c — LangSmith  (Phase 7 Observability, automated)",
                ha="center", fontsize=11, fontweight="bold", color="#1C2833")
        ax.text(W/2, 3.5,
                "set 3 env vars  |  every LangGraph call auto-traced  |  datasets + evals built in",
                ha="center", fontsize=8, color="#566573", style="italic")

        _box(ax, 1.2, 2.7, "Your\nAgent Code", C["llm"], w=1.2, h=0.52)
        _box(ax, 1.2, 1.8, "TraceCollector\n(Phase 7 manual)", C["dim"], w=1.4, h=0.52)
        _arrow(ax, 1.2, 2.44, 1.2, 2.07)
        _box(ax, 1.2, 0.9, "Spans dict\n(you manage)", C["dim"], w=1.4, h=0.52)
        _arrow(ax, 1.2, 1.54, 1.2, 1.17)
        ax.text(1.2, 0.58, "Phase 7 manual", ha="center", fontsize=7, color=C["dim"], style="italic")

        ax.text(W/2, 2.5, "vs", ha="center", fontsize=16, color=C["arrow"], fontweight="bold")

        _box(ax, 5.8, 2.7, "Your\nAgent Code", C["llm"], w=1.2, h=0.52)
        _box(ax, 5.8, 1.8, "LangSmith\nAuto-Tracer", C["agent_yes"], w=1.4, h=0.52)
        _arrow(ax, 5.8, 2.44, 5.8, 2.07,
               label="LANGCHAIN_TRACING_V2=true", color=C["agent_yes"])
        for y, lbl in [(1.28, "Prompts + responses"),
                       (1.0,  "Latency + tokens + cost"),
                       (0.72, "Tool calls + datasets")]:
            ax.text(5.8, y, lbl, ha="center", fontsize=7, color=C["agent_yes"])
        ax.text(5.8, 0.44, "automatic", ha="center", fontsize=7.5,
                color=C["agent_yes"], style="italic", fontweight="bold")

        _journey_bar(ax, current="Ph3", y=0.97)
        _agent_def_footer(ax)
        return _to_bytes(fig)

    def diagram_langchain() -> bytes:
        fig, ax = _fig()
        _agent_banner(ax, is_agent=False,
                      why="LangChain LCEL is Prompt Chaining (Phase 2a) as syntax sugar — same pattern, less plumbing")
        ax.text(W/2, 3.75, "Phase 10d — LangChain LCEL  (Phases 1+2+5 as composable pipes)",
                ha="center", fontsize=11, fontweight="bold", color="#1C2833")
        ax.text(W/2, 3.5,
                "prompt | llm | parser  =  Phase 2a Prompt Chaining with type-safe composition",
                ha="center", fontsize=8, color="#566573", style="italic")

        components = [
            ("ChatPrompt\nTemplate", C["input"],  0.7),
            ("ChatModel\n(any LLM)", C["llm"],    2.1),
            ("Output\nParser",       C["memory"], 3.5),
            ("RAG\nRetriever",       C["tools"],  4.9),
            ("Final\nOutput",        C["output"], 6.3),
        ]
        for label, col, cx in components:
            _box(ax, cx, 2.55, label, col, w=1.05, h=0.58)
        for i in range(len(components) - 1):
            _arrow(ax, components[i][2]+0.53, 2.55, components[i+1][2]-0.53, 2.55,
                   label="|", color=C["agent_yes"])

        ax.text(W/2, 1.88,
                "chain = prompt | llm | parser   # LCEL pipe operator",
                ha="center", fontsize=8.5, color="#1C2833", fontfamily="monospace",
                bbox=dict(facecolor="white", edgecolor=C["agent_yes"],
                          linewidth=1.5, boxstyle="round,pad=0.3"))

        mappings = [(0.7, "Phase 1a\nPlain LLM"), (2.1, "Phase 1b\nMemory"),
                    (3.5, "Phase 2a\nChaining"),  (4.9, "Phase 5a\nRAG")]
        for cx, lbl in mappings:
            ax.annotate("", xy=(cx, 2.24), xytext=(cx, 1.62),
                        arrowprops=dict(arrowstyle="-|>", color=C["dim"], lw=1.2), zorder=4)
            ax.text(cx, 1.48, lbl, ha="center", fontsize=6.5, color=C["dim"],
                    style="italic", multialignment="center")

        _journey_bar(ax, current="Ph3", y=0.97)
        _agent_def_footer(ax)
        return _to_bytes(fig)

    def diagram_framework_compare() -> bytes:
        """
        2-panel diagram for Phase 10f — Framework Comparison.
        Left:  abstraction vs agent-readiness landscape (bubble chart).
        Right: layered stack — what each framework adds over the one below.
        """
        import matplotlib.gridspec as gridspec

        fig = plt.figure(figsize=(13, 5.4))
        fig.patch.set_facecolor(C["bg"])
        gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.06)
        ax_l = fig.add_subplot(gs[0])
        ax_r = fig.add_subplot(gs[1])

        # ── shared helpers ────────────────────────────────────────────────────
        def bx(ax, cx, cy, w, h, lines, fc, fs=7.5, ec="white"):
            p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                               boxstyle="round,pad=0.08",
                               facecolor=fc, edgecolor=ec, linewidth=2, zorder=3)
            ax.add_patch(p)
            ax.text(cx, cy, "\n".join(lines) if isinstance(lines, list) else lines,
                    ha="center", va="center", fontsize=fs, color="white",
                    fontweight="bold", zorder=4, multialignment="center", linespacing=1.3)

        def ar(ax, x1, y1, x2, y2, lbl="", col=None, dashed=False):
            col = col or C["arrow"]
            ls = (0, (4, 3)) if dashed else "solid"
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6,
                                        mutation_scale=12, linestyle=ls), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.1, (y1+y2)/2, lbl, fontsize=6,
                        color=col, style="italic", zorder=6)

        # ── LEFT — Abstraction vs Agent-Readiness landscape ───────────────────
        ax_l.set_xlim(0, 5); ax_l.set_ylim(0, 5.4); ax_l.axis("off")
        ax_l.set_facecolor(C["bg"])

        # Header
        ax_l.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38,
                                      boxstyle="round,pad=0.05",
                                      facecolor=C["llm"], edgecolor="white",
                                      lw=1.5, zorder=2))
        ax_l.text(2.5, 5.19, "Framework Landscape — Abstraction vs Agent-Readiness",
                  ha="center", va="center", fontsize=8.5,
                  color="white", fontweight="bold")

        # Axis labels
        ax_l.text(0.15, 2.7, "MORE\nCONTROL", ha="center", fontsize=7,
                  color=C["dim"], rotation=90, va="center")
        ax_l.text(4.85, 2.7, "MORE\nCONVENIENCE", ha="center", fontsize=7,
                  color=C["dim"], rotation=90, va="center")
        ax_l.text(2.5, 0.12, "Single Agent  ◄─────────────────►  Multi-Agent",
                  ha="center", fontsize=7, color=C["dim"])
        # Dividing lines
        ax_l.axhline(2.7, color=C["dim"], lw=0.6, ls="--", alpha=0.4, zorder=1)
        ax_l.axvline(2.5, color=C["dim"], lw=0.6, ls="--", alpha=0.4, zorder=1)

        # Framework bubbles  (cx, cy, w, h, lines, color)
        BUBBLES = [
            (1.2, 1.5, 1.6, 0.62,  ["Raw SDK", "(Phases 1–9)"],         C["input"]),
            (1.5, 3.2, 1.7, 0.62,  ["LangChain LCEL", "(Phase 10d)"],   C["memory"]),
            (2.5, 3.8, 1.8, 0.62,  ["LangGraph", "(Phases 10a/10b)"],   C["agent_yes"]),
            (3.8, 4.3, 1.6, 0.62,  ["Google ADK", "(Phase 10e)"],       C["tools"]),
            (2.5, 2.0, 1.8, 0.50,  ["LangSmith", "(Phase 10c)"],        C["loop"]),
        ]
        for cx, cy, w, h, lines, fc in BUBBLES:
            bx(ax_l, cx, cy, w, h, lines, fc)

        # LangSmith annotation — wraps everything
        ax_l.text(2.5, 1.62, "observability layer — wraps all frameworks",
                  ha="center", fontsize=6, color=C["loop"], style="italic")

        # Phase anchor labels
        for cx, cy, lbl in [(1.2, 0.82, "Full control\nno boilerplate"),
                            (1.5, 2.60, "Pipelines\n+ RAG"),
                            (2.5, 3.18, "Agents + HITL\n+ Streaming"),
                            (3.8, 3.68, "Cloud multi-agent\nmanaged infra")]:
            ax_l.text(cx, cy, lbl, ha="center", fontsize=6, color=C["dim"],
                      style="italic", multialignment="center")

        # ── RIGHT — Layered stack ─────────────────────────────────────────────
        ax_r.set_xlim(0, 5); ax_r.set_ylim(0, 5.4); ax_r.axis("off")
        ax_r.set_facecolor(C["bg"])

        ax_r.add_patch(FancyBboxPatch((0, 5.0), 5, 0.38,
                                      boxstyle="round,pad=0.05",
                                      facecolor=C["agent_yes"], edgecolor="white",
                                      lw=1.5, zorder=2))
        ax_r.text(2.5, 5.19, "When to Add Each Layer",
                  ha="center", va="center", fontsize=8.5,
                  color="white", fontweight="bold")

        LAYERS = [
            (0.5,  0.85, 0.55, C["input"],     "RAW SDK",
             "Always start here — full visibility,\nno dependencies"),
            (1.45, 1.58, 0.55, C["agent_yes"], "+ LANGGRAPH",
             "Add when: HITL, persistence,\nstreaming, typed state needed"),
            (2.40, 2.30, 0.55, C["memory"],    "+ LCEL",
             "Add when: RAG pipelines, chaining\nwith streaming/batching needed"),
            (3.35, 3.02, 0.55, C["loop"],      "+ LANGSMITH",
             "Add when: production — need auto\ntracing, evals, cost dashboards"),
            (4.30, 3.74, 0.55, C["tools"],     "+ ADK",
             "Add when: multi-agent on\nGoogle Cloud infra at scale"),
        ]

        for i, (lx, ly, lh, col, label, note) in enumerate(LAYERS):
            # Full-width bar
            ax_r.add_patch(FancyBboxPatch((0.2, ly-lh/2), 4.6, lh,
                                          boxstyle="round,pad=0.06",
                                          facecolor=col, edgecolor="white",
                                          lw=1.5, alpha=0.92, zorder=3+i))
            ax_r.text(1.4, ly, label, ha="center", va="center", fontsize=8,
                      color="white", fontweight="bold", zorder=10+i)
            ax_r.text(3.1, ly, note, ha="center", va="center", fontsize=6.5,
                      color="white", zorder=10+i, multialignment="center",
                      linespacing=1.3)
            if i < len(LAYERS) - 1:
                ar(ax_r, 2.5, ly+lh/2, 2.5, LAYERS[i+1][1]-LAYERS[i+1][2]/2,
                   col=C["dim"])

        ax_r.text(2.5, 0.22, "Each layer is optional — Raw SDK alone can do everything",
                  ha="center", fontsize=6.8, color=C["dim"], style="italic")

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

    # ─────────────────────────────────────────────────────────────────────────
    # NEW: Memory & Persistence diagram (for 10b2)
    # ─────────────────────────────────────────────────────────────────────────
    def diagram_langgraph_memory() -> bytes:
        fig = plt.figure(figsize=(14, 7))
        fig.patch.set_facecolor(C["bg"])
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 14); ax.set_ylim(0, 7); ax.axis("off")
        ax.set_facecolor(C["bg"])

        L4 = "#6C3483"
        def bx(cx, cy, w, h, title, lines, col, fs=7.5):
            ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                         boxstyle="round,pad=0.06", facecolor=col, edgecolor="white", lw=1.5, zorder=3))
            ax.text(cx, cy+h/2-0.22, title, ha="center", va="center",
                    fontsize=fs, color="white", fontweight="bold", zorder=4)
            for i, ln in enumerate(lines):
                ax.text(cx, cy+h/2-0.48-i*0.22, ln, ha="center", fontsize=6.2,
                        color="white", alpha=0.9, zorder=4)
        def ar(x1, y1, x2, y2, lbl="", col=None):
            col = col or C["arrow"]
            ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5, mutation_scale=11), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.08,(y1+y2)/2+0.12, lbl, fontsize=6, color=col, style="italic")

        # Title bar
        ax.add_patch(FancyBboxPatch((0.1,6.4),13.8,0.5, boxstyle="round,pad=0.05",
                     facecolor="#6C3483", edgecolor="none", zorder=5))
        ax.text(7.0,6.65,"Layer 4 — Memory & Context  |  LangGraph Persistence + RAG",
                ha="center", va="center", fontsize=12, color="white", fontweight="bold", zorder=6)
        ax.text(7.0,6.22,"Phase cross-refs: → Phase 1b (memory) · Phase 5a (RAG) · Phase 5b (long-term memory)",
                ha="center", fontsize=7.5, color="#566573", zorder=3)

        # Checkpointer hierarchy (left panel)
        ax.add_patch(FancyBboxPatch((0.15,0.3),4.5,5.7, boxstyle="round,pad=0.08",
                     facecolor=L4, edgecolor="white", lw=1.5, alpha=0.12, zorder=1))
        ax.text(2.4,5.78,"Checkpointer Hierarchy", ha="center", fontsize=9,
                color=L4, fontweight="bold", zorder=3)
        ax.text(2.4,5.5,"Thread-ID scopes state per conversation", ha="center",
                fontsize=7, color="#566573", style="italic", zorder=3)
        CPKTS = [("InMemorySaver","dev/testing only\nno persistence after restart","#2471A3",4.75),
                 ("SqliteSaver","local prod · no infra\nbuilt-in Python · zero setup","#117A65",3.6),
                 ("RedisSaver","distributed · fast\nrequires Redis running","#CA6F1E",2.45),
                 ("PostgresSaver","enterprise prod\nrequires Postgres running","#1C2833",1.3)]
        for name, desc, col, cy in CPKTS:
            bx(2.4, cy, 3.8, 0.9, name, desc.split("\n"), col)
        ar(2.4,4.3,2.4,4.05,"upgrade", L4)
        ar(2.4,3.15,2.4,2.9,"upgrade", L4)
        ar(2.4,2.0,2.4,1.75,"upgrade", L4)
        ax.text(2.4,0.72,"Same API — swap by changing one import",
                ha="center", fontsize=7, color=L4, fontweight="bold", style="italic")

        # Memory types (right panels)
        ax.add_patch(FancyBboxPatch((5.0,3.5),8.7,2.5, boxstyle="round,pad=0.08",
                     facecolor=L4, edgecolor="white", lw=1.5, alpha=0.12, zorder=1))
        ax.text(9.35,5.75,"Memory Store vs Conversation Memory vs Vector Store",
                ha="center", fontsize=9, color=L4, fontweight="bold", zorder=3)
        bx(6.3, 4.72, 2.6, 1.6, "Memory Store",
           ["InMemoryStore / LangMem","Cross-session facts","User preferences","put/get/search API"], L4)
        bx(9.35, 4.72, 2.6, 1.6, "Conv. Memory",
           ["ConvBufferMemory","ConvSummaryMemory","MessagesPlaceholder","add_messages reducer"], "#7E5109")
        bx(12.35, 4.72, 2.2, 1.6, "Vector Store",
           ["FAISS · Chroma","pgvector · Qdrant","cosine search","→ Phase 5a RAG"], "#0E7A5A")

        # Thread ID concept
        ax.add_patch(FancyBboxPatch((5.0,0.3),8.7,3.0, boxstyle="round,pad=0.08",
                     facecolor="#1C2833", edgecolor="white", lw=1.5, alpha=0.10, zorder=1))
        ax.text(9.35,3.07,"Thread ID — Scoping State per Conversation",
                ha="center", fontsize=9, color="#1C2833", fontweight="bold", zorder=3)
        ax.text(9.35,2.78,"Each thread_id maintains independent state — same agent, different users/sessions",
                ha="center", fontsize=7, color="#566573", style="italic", zorder=3)
        bx(7.35, 1.75, 3.8, 1.5, "Thread-scoped state",
           ['config = {"configurable": {"thread_id": "user-123"}}',
            "agent.invoke(input, config)  # isolated",
            "Different thread_id = different state"], "#2471A3")
        bx(11.85, 1.75, 3.4, 1.5, "Use cases",
           ["Customer support: 1 thread per ticket",
            "Chatbot: 1 thread per user session",
            "Multi-user: thread_id = user_id"], "#1E8449")

        ax.text(9.35,0.48,"→ Phase 1b: you managed history manually. Checkpointer does this automatically per thread.",
                ha="center", fontsize=7.5, color="#1A5276", style="italic", fontweight="bold")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    # ─────────────────────────────────────────────────────────────────────────
    # NEW: Tools & Security diagram (for 10b3)
    # ─────────────────────────────────────────────────────────────────────────
    def diagram_langgraph_tools_security() -> bytes:
        fig = plt.figure(figsize=(14, 7))
        fig.patch.set_facecolor(C["bg"])
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 14); ax.set_ylim(0, 7); ax.axis("off")
        ax.set_facecolor(C["bg"])

        L5 = "#0E7A5A"; SEC = "#922B21"
        def bx(cx, cy, w, h, title, lines, col):
            ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                         boxstyle="round,pad=0.06", facecolor=col, edgecolor="white", lw=1.5, zorder=3))
            ax.text(cx, cy+h/2-0.22, title, ha="center", va="center",
                    fontsize=7.5, color="white", fontweight="bold", zorder=4)
            for i, ln in enumerate(lines):
                ax.text(cx, cy+h/2-0.46-i*0.22, ln, ha="center", fontsize=6.0,
                        color="white", alpha=0.9, zorder=4)
        def ar(x1, y1, x2, y2, lbl="", col=None):
            col = col or C["arrow"]
            ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5, mutation_scale=11), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.06,(y1+y2)/2+0.1, lbl, fontsize=6, color=col, style="italic")

        # Title
        ax.add_patch(FancyBboxPatch((0.1,6.4),13.8,0.5, boxstyle="round,pad=0.05",
                     facecolor="#0E7A5A", edgecolor="none", zorder=5))
        ax.text(7.0,6.65,"Layer 5 — Tools + Security & Governance",
                ha="center", va="center", fontsize=12, color="white", fontweight="bold", zorder=6)
        ax.text(7.0,6.22,"Phase cross-refs: → Phase 1c (tools) · Phase 4a (guardrails) · Phase 4b (HITL) · Phase 6b (MCP)",
                ha="center", fontsize=7.5, color="#566573", zorder=3)

        # LEFT: Tools flow
        ax.add_patch(FancyBboxPatch((0.15,0.3),7.6,5.7, boxstyle="round,pad=0.06",
                     facecolor=L5, edgecolor="none", alpha=0.10, zorder=1))
        ax.text(3.95,5.77,"Layer 5 — Tools (the Action Surface)",
                ha="center", fontsize=9, color=L5, fontweight="bold", zorder=3)

        # Tool categories
        for cx, ti, items in [
            (1.6, "Search Tools",    ["TavilySearch","SerpAPI","ArxivTool"]),
            (3.55,"Code Execution",  ["PythonREPL","ShellTool","E2B sandbox"]),
            (5.5, "API / HTTP",      ["RequestsTool","OpenAPI toolkit","@tool decorator"]),
            (7.15,"MCP Servers",     ["langchain_mcp","SSE/stdio","→ Phase 6b"]),
        ]:
            bx(cx, 4.8, 1.75, 1.0, ti, items, L5)

        # Tool call pattern
        ax.add_patch(FancyBboxPatch((0.3,3.1),7.3,1.4, boxstyle="round,pad=0.06",
                     facecolor="#0D1B2A", edgecolor=L5, lw=1.2, alpha=0.85, zorder=2))
        ax.text(3.95,4.32,"Tool Call Pattern — LLM.bind_tools() + ToolNode",
                ha="center", fontsize=8, color="white", fontweight="bold", zorder=4)
        FLOW = [("LLM decides","#2471A3"),("AIMessage\n(tool_calls)","#CA6F1E"),
                ("ToolNode\ndispatches",L5),("ToolMessage\nresult","#7D3C98"),("Back to\nLLM","#2471A3")]
        fxs = [1.0, 2.55, 4.1, 5.65, 7.2]
        for i, ((lbl,col),fx) in enumerate(zip(FLOW,fxs)):
            ax.add_patch(FancyBboxPatch((fx-0.65,3.25),1.3,0.95,
                         boxstyle="round,pad=0.05", facecolor=col, edgecolor="white", lw=1, zorder=4))
            ax.text(fx,3.72,lbl, ha="center", va="center",
                    fontsize=6.5, color="white", fontweight="bold", zorder=5, multialignment="center")
            if i < len(FLOW)-1:
                ax.annotate("", xy=(fxs[i+1]-0.66,3.72), xytext=(fx+0.66,3.72),
                            arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.2, mutation_scale=8), zorder=5)

        # @tool decorator
        bx(3.95, 2.2, 7.2, 1.4, "@tool decorator — defining tools for LangChain agents",
           ['@tool', 'def get_weather(city: str) -> str:',
            '    """Get current weather for a city."""  # docstring = tool description',
            '    return fetch_weather(city)  # Phase 1c tools work unchanged'], "#1C2833")

        ax.text(3.95,0.85,"→ Phase 1c tools (get_weather, get_stock_price, etc.) work unchanged — just add @tool",
                ha="center", fontsize=7.5, color="#117A65", fontweight="bold", style="italic")
        ax.text(3.95,0.55,"→ Phase 6b MCP: langchain_mcp_adapters wraps any MCP server as a LangChain tool",
                ha="center", fontsize=7.5, color="#1A5276", fontweight="bold", style="italic")

        # RIGHT: Security & Governance
        ax.add_patch(FancyBboxPatch((8.0,0.3),5.8,5.7, boxstyle="round,pad=0.06",
                     facecolor=SEC, edgecolor="none", alpha=0.10, zorder=1))
        ax.text(10.9,5.77,"Security & Governance",
                ha="center", fontsize=9, color=SEC, fontweight="bold", zorder=3)

        bx(10.9, 4.85, 5.3, 1.2, "Guard Agent — Pre-Tool-Call Check",
           ["Check before EVERY tool execution","Policy: is this tool call allowed?",
            "OAP policy engine · custom rules","→ Phase 4a Guardrails pattern in graph"], SEC)

        bx(10.9, 3.62, 5.3, 1.3, "HITL — Command(resume=...) Pattern",
           ["interrupt_before=['tools']  # pause before tool",
            "graph.invoke(None, config)  # approve: resume",
            "graph.update_state(config, override)  # reject",
            "→ Phase 4b HITL — same concept, newer API"], "#7E5109")

        bx(10.9, 2.42, 5.3, 1.1, "API Key Management",
           ["from langchain_core.utils import SecretStr",
            "api_key = SecretStr(os.getenv('GEMINI_API_KEY'))",
            "Never store keys in graph state — env vars only"], "#1A5276")

        bx(10.9, 1.28, 5.3, 1.0, "Audit Trails",
           ["LangSmith logs every run — full reproducibility",
            "GDPR-ready: export/delete run data",
            "→ Phase 7a Observability (automated)"], "#1E8449")

        ax.text(10.9,0.55,"Security is built into the architecture — not bolted on",
                ha="center", fontsize=7.5, color=SEC, fontweight="bold", style="italic")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    # ─────────────────────────────────────────────────────────────────────────
    # NEW: Platform & Agent Loop diagram (for 10b4)
    # ─────────────────────────────────────────────────────────────────────────
    def diagram_langgraph_platform() -> bytes:
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        fig.patch.set_facecolor(C["bg"])

        def bx(ax, cx, cy, w, h, lines, col, fs=7.5, ec="white"):
            ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                         boxstyle="round,pad=0.08", facecolor=col, edgecolor=ec, lw=1.8, zorder=3))
            ax.text(cx, cy, "\n".join(lines), ha="center", va="center",
                    fontsize=fs, color="white", fontweight="bold", zorder=4,
                    multialignment="center", linespacing=1.3)
        def ar(ax, x1, y1, x2, y2, lbl="", col=None):
            col = col or C["arrow"]
            ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, mutation_scale=12), zorder=5)
            if lbl:
                ax.text((x1+x2)/2+0.1,(y1+y2)/2, lbl, fontsize=6.5, color=col, style="italic")

        for ax in axes:
            ax.set_xlim(0,5); ax.set_ylim(0,7); ax.axis("off")
            ax.set_facecolor(C["bg"])

        # LEFT: LangGraph Agent Loop (explicit)
        ax = axes[0]
        ax.add_patch(FancyBboxPatch((0,6.6),5,0.38, boxstyle="round,pad=0.05",
                     facecolor="#7E5109", edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5,6.79,"LangGraph Agent Loop — Andrew Ng's 4 Patterns as a Graph",
                ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")

        LOOP = [("#2471A3","① PERCEIVE","State loaded from checkpointer",5.75),
                ("#1A6B3A","② REASON","LLM call: AIMessage(tool_calls)",4.75),
                ("#0E7A5A","③ ACT","ToolNode executes tool_calls",3.75),
                ("#CA6F1E","④ EVALUATE","conditional_edge(state) → next",2.75),
                ("#6C3483","⑤ PERSIST","State snapshot saved to checkpointer",1.75)]
        for col, step, desc, cy in LOOP:
            bx(ax, 2.5, cy, 4.5, 0.78, [step, desc], col)
            if cy > 1.75:
                ar(ax, 2.5, cy-0.39, 2.5, cy-0.61, col=C["dim"])

        # Loop-back arrow (persist → perceive)
        ax.annotate("", xy=(0.42, 5.75), xytext=(0.42, 1.75),
                    arrowprops=dict(arrowstyle="-|>", color=C["loop"], lw=2.0,
                                   connectionstyle="arc3,rad=0"), zorder=5)
        ax.text(0.12, 3.75, "loop\nuntil\ndone", ha="center", fontsize=7,
                color=C["loop"], fontweight="bold", rotation=90, va="center")

        ax.text(2.5, 1.08, "Reflection = Evaluate step routes back to Reason (Andrew Ng Pattern 1)",
                ha="center", fontsize=7, color="#6C3483", style="italic", fontweight="bold")
        ax.text(2.5, 0.72, "Planning = Reason step writes a plan before Act (Pattern 3)",
                ha="center", fontsize=7, color="#1A6B3A", style="italic", fontweight="bold")
        ax.text(2.5, 0.38, "Tool Use = Act step; Multi-Agent = Act delegates to sub-agent (Patterns 2 & 4)",
                ha="center", fontsize=6.8, color="#0E7A5A", style="italic", fontweight="bold")

        # RIGHT: LangGraph Platform
        ax = axes[1]
        ax.add_patch(FancyBboxPatch((0,6.6),5,0.38, boxstyle="round,pad=0.05",
                     facecolor="#1A5276", edgecolor="white", lw=1.5, zorder=2))
        ax.text(2.5,6.79,"LangGraph Platform — Production Infrastructure",
                ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")

        bx(ax, 2.5, 5.85, 4.5, 1.0,
           ["Studio UI — Visual Graph Debugger",
            "Visualise compiled graph structure",
            "Step-through debug: inspect state per node",
            "graph.get_graph().draw_mermaid_png()  # in Streamlit!"], "#1A5276")

        bx(ax, 2.5, 4.55, 4.5, 1.0,
           ["Deploy — 1-Click Production (GA May 2025)",
            "Autoscale managed infrastructure",
            "Background runs · Cron scheduling",
            "No DevOps: push graph → live endpoint"], "#0E6655")

        bx(ax, 2.5, 3.25, 4.5, 1.0,
           ["Durable Execution",
            "Resume after crash/timeout automatically",
            "Long-running agents (hours/days)",
            "checkpoint_at = every node (auto)"], "#7E5109")

        bx(ax, 2.5, 1.95, 4.5, 1.0,
           ["API Server — Auto-Generated",
            "REST + streaming SSE endpoint from graph",
            "POST /runs/stream  →  node events",
            "SDK clients: Python, JS, REST"], "#6C3483")

        ax.text(2.5, 1.12, "graph.get_graph().draw_mermaid_png() works today — no Platform account needed",
                ha="center", fontsize=7.5, color="#117A65", fontweight="bold", style="italic")
        ax.text(2.5, 0.72, "Deploy + Durable Execution require LangGraph Platform account",
                ha="center", fontsize=7, color="#922B21", style="italic")
        ax.text(2.5, 0.38, "Studio UI: free desktop app download (Mac/Windows) — highly recommended",
                ha="center", fontsize=7, color="#1A5276", fontweight="bold", style="italic")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig)
        return buf.getvalue()

    return (diagram_langgraph_workflows, diagram_langgraph_agents,
            diagram_langsmith, diagram_langchain, diagram_framework_compare,
            diagram_google_adk,
            diagram_lang_arch_map, diagram_langgraph_memory,
            diagram_langgraph_tools_security, diagram_langgraph_platform)
