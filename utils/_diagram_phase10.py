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

    return (diagram_langgraph_workflows, diagram_langgraph_agents,
            diagram_langsmith, diagram_langchain)
