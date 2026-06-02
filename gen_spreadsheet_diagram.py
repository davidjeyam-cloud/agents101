"""
Generates docs/images/spreadsheet_pipeline.png
Schematic: Spreadsheet-to-Code Agentic Pipeline
Run: python gen_spreadsheet_diagram.py
"""

import io, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "bg":           "#F0F4F8",
    "stage":        "#1A5276",   # pipeline stages
    "orchestrator": "#1A252F",   # orchestrator node
    "worker":       "#2471A3",   # worker nodes
    "eval":         "#922B21",   # evaluator / judge
    "gen":          "#1E8449",   # generator / code-gen
    "reflect":      "#7D3C98",   # reflection / optimizer
    "hitl":         "#B7950B",   # HITL gates
    "mem_short":    "#117A65",   # short-term memory
    "mem_long":     "#6C3483",   # long-term memory (ChromaDB)
    "consistency":  "#CA6F1E",   # consistency agent
    "production":   "#145A32",   # production output
    "arrow":        "#5D6D7E",
    "dashed":       "#AAB7B8",
    "panel":        "#D5E8D4",   # light panel backgrounds
    "panel2":       "#DAE8FC",
    "panel3":       "#F8CECC",
    "panel4":       "#E1D5E7",
}

FIG_W, FIG_H = 20, 13

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
ax.set_facecolor(C["bg"])
fig.patch.set_facecolor(C["bg"])


# ── Helpers ────────────────────────────────────────────────────────────────────

def box(cx, cy, text, color, w=2.2, h=0.7, fontsize=8.5, radius=0.15, alpha=1.0, zorder=4):
    patch = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f"round,pad={radius}",
        facecolor=color, edgecolor="white", linewidth=2.0,
        zorder=zorder, alpha=alpha,
    )
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=zorder+1,
            multialignment="center", linespacing=1.35)


def panel(x0, y0, x1, y1, color, label="", label_color="#333", alpha=0.25, zorder=1):
    patch = FancyBboxPatch(
        (x0, y0), x1-x0, y1-y0,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor="#AAAAAA", linewidth=1.0,
        zorder=zorder, alpha=alpha,
    )
    ax.add_patch(patch)
    if label:
        ax.text((x0+x1)/2, y1-0.12, label, ha="center", va="top",
                fontsize=7.5, color=label_color, fontweight="bold", zorder=zorder+1,
                style="italic")


def arrow(x1, y1, x2, y2, label="", color=None, dashed=False, lw=1.8):
    color = color or C["arrow"]
    ls = (0, (5, 3)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=14, linestyle=ls), zorder=6)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2 + 0.1
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=6.5, color=color, style="italic", zorder=7)


def diamond(cx, cy, w=0.55, h=0.38, color="#B7950B", label="HITL", fontsize=6.5):
    pts = [(cx, cy+h/2), (cx+w/2, cy), (cx, cy-h/2), (cx-w/2, cy)]
    from matplotlib.patches import Polygon
    p = Polygon(pts, closed=True, facecolor=color, edgecolor="white", linewidth=1.5, zorder=7)
    ax.add_patch(p)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=8)


def badge(cx, cy, text, color, fontsize=6.8):
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=9,
            bbox=dict(boxstyle="round,pad=0.22", facecolor=color,
                      edgecolor="white", linewidth=1.2, zorder=8))


def curved_arrow(x1, y1, x2, y2, color, rad=0.3, lw=1.8, label=""):
    style = f"arc3,rad={rad}"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                connectionstyle=style, mutation_scale=14), zorder=6)
    if label:
        mx = (x1+x2)/2 + rad*0.6
        my = (y1+y2)/2
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=6.5, color=color, style="italic", zorder=7)


# ══════════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════════
ax.text(FIG_W/2, 12.55, "Spreadsheet → Production Code  |  Agentic Pipeline Architecture",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color="#1A252F", zorder=10)
ax.text(FIG_W/2, 12.22, "3-Layer Hybrid: Prompt Chain  ·  Orchestrator-Workers  ·  Evaluator-Optimizer",
        ha="center", va="center", fontsize=9, color="#5D6D7E", style="italic", zorder=10)

# ══════════════════════════════════════════════════════════════════════════════
# ZONE A — TOP PIPELINE CHAIN (7 stages)
# ══════════════════════════════════════════════════════════════════════════════
panel(0.3, 10.5, 19.7, 11.9, "#DAE8FC", "OUTER LAYER — Prompt Chain (7 Stages)", "#1A5276")

STAGES = [
    (1.5,  11.2, "① Parse &\nClassify",    C["stage"]),
    (3.8,  11.2, "② Context\nCapture",     C["stage"]),
    (6.1,  11.2, "③ Plan\nStructure",      C["stage"]),
    (8.4,  11.2, "④ Orchestrate\nWorkers", C["orchestrator"]),
    (10.7, 11.2, "⑤ Eval-Opt\nLoop",       C["eval"]),
    (13.0, 11.2, "⑥ HITL\nReview",         C["hitl"]),
    (15.8, 11.2, "⑦ Production\nOutput",   C["production"]),
]

for cx, cy, txt, col in STAGES:
    box(cx, cy, txt, col, w=2.1, h=0.85)

# Chain arrows
for i in range(len(STAGES)-1):
    x1 = STAGES[i][0] + 1.05
    x2 = STAGES[i+1][0] - 1.05
    arrow(x1, 11.2, x2, 11.2, color=C["arrow"], lw=2.0)

# HITL diamonds on stages 2 and 6
diamond(3.8, 10.65, label="HITL\ngate", w=0.62, h=0.38)
diamond(13.0, 10.65, label="HITL\ngate", w=0.62, h=0.38)

# Down arrows from stage 4 and 5 into the expanded zones
arrow(8.4, 10.77, 8.4, 9.9, color=C["orchestrator"], lw=2.2, label="expand")
arrow(10.7, 10.77, 10.7, 9.9, color=C["eval"], lw=2.2, label="expand")

# ══════════════════════════════════════════════════════════════════════════════
# ZONE B — ORCHESTRATOR-WORKERS (left-centre)
# ══════════════════════════════════════════════════════════════════════════════
panel(0.3, 5.6, 12.5, 9.85, "#DAE8FC", "INNER LAYER 1 — Orchestrator-Workers", "#1A252F", alpha=0.2)

# Orchestrator
box(6.4, 9.25, "ORCHESTRATOR\n(Task Planner + Aggregator)", C["orchestrator"], w=3.4, h=0.75)

# Workers
WORKERS = [
    (1.5,  7.3, "Worker A\nInput Parser"),
    (4.3,  7.3, "Worker B\nLogic Extractor"),
    (7.1,  7.3, "Worker C\nOutput Formatter"),
    (9.9,  7.3, "Worker D\nTest Generator"),
]
for cx, cy, txt in WORKERS:
    box(cx, cy, txt, C["worker"], w=2.3, h=0.75)
    # Orchestrator → Worker
    arrow(6.4, 8.88, cx, 7.68, color=C["orchestrator"], lw=1.6)
    # Worker → Orchestrator (feedback)
    arrow(cx, 6.93, 6.4, 8.75, color="#2471A3", lw=1.2, dashed=True)

# Shared context note
badge(6.4, 6.35, "Shared: Convention Registry  ·  Long-term Memory context  ·  Dependency Graph",
      "#1A252F", fontsize=7.2)

# Parallel badge
badge(1.5, 8.28, "parallel", "#117A65", fontsize=6.5)
badge(4.3, 8.28, "parallel", "#117A65", fontsize=6.5)
badge(7.1, 8.28, "parallel", "#117A65", fontsize=6.5)
badge(9.9, 8.28, "parallel", "#117A65", fontsize=6.5)

# ══════════════════════════════════════════════════════════════════════════════
# ZONE C — EVALUATOR-OPTIMIZER LOOP (right)
# ══════════════════════════════════════════════════════════════════════════════
panel(12.8, 5.6, 19.7, 9.85, "#F8CECC", "INNER LAYER 2 — Evaluator-Optimizer Loop", "#7D3C98", alpha=0.18)

EO_GEN  = (15.0, 9.1)
EO_EVAL = (18.2, 7.4)
EO_OPT  = (15.0, 5.9)

box(*EO_GEN,  "CODE\nGENERATOR", C["gen"],     w=2.4, h=0.78)
box(*EO_EVAL, "LLM JUDGE\n(Evaluator)",  C["eval"],    w=2.4, h=0.78)
box(*EO_OPT,  "REFLECTION\n(Optimizer)", C["reflect"],  w=2.4, h=0.78)

# Loop arrows
curved_arrow(EO_GEN[0]+1.2,  EO_GEN[1]-0.1,
             EO_EVAL[0]-1.2, EO_EVAL[1]+0.2,
             color=C["eval"], rad=0.2, label="draft code")
curved_arrow(EO_EVAL[0]-0.3, EO_EVAL[1]-0.4,
             EO_OPT[0]+1.1,  EO_OPT[1]+0.25,
             color=C["reflect"], rad=0.15, label="critique")
curved_arrow(EO_OPT[0]-0.3,  EO_OPT[1]+0.3,
             EO_GEN[0]-1.2,  EO_GEN[1]-0.1,
             color=C["gen"], rad=0.25, label="improve")

# Threshold badge
badge(16.0, 7.45, "score ≥ 7 → PASS  |  else → loop", C["eval"], fontsize=6.8)

# ══════════════════════════════════════════════════════════════════════════════
# ZONE D — MEMORY LAYER (bottom)
# ══════════════════════════════════════════════════════════════════════════════
panel(0.3, 0.4, 19.7, 5.3, "#E1D5E7", "MEMORY LAYER", "#6C3483", alpha=0.18)

# Short-term memory
panel(0.6, 0.7, 9.5, 5.0, "#D5E8D4", "SHORT-TERM  (session state)", "#117A65", alpha=0.3, zorder=2)

ST_ITEMS = [
    (1.8, 4.1, "Tab Map &\nDep Graph"),
    (4.2, 4.1, "User Context\nAnswers"),
    (6.6, 4.1, "In-Progress\nPlan + Draft"),
    (8.8, 4.1, "HITL Edits\n& Rejections"),
    (1.8, 2.7, "Current\nSession State"),
    (4.2, 2.7, "Error / Retry\nLog"),
    (6.6, 2.7, "Worker\nOutputs"),
    (8.8, 2.7, "Eval Scores\n& Critiques"),
]
for cx, cy, txt in ST_ITEMS:
    box(cx, cy, txt, C["mem_short"], w=1.85, h=0.65, fontsize=7.5)

# Long-term memory (ChromaDB)
panel(9.8, 0.7, 19.4, 5.0, "#E1D5E7", "LONG-TERM  (ChromaDB vector store — persists across spreadsheets)", "#6C3483", alpha=0.3, zorder=2)

LT_ITEMS = [
    (11.0, 4.1, "Approved\nPatterns"),
    (13.2, 4.1, "Naming\nConventions"),
    (15.4, 4.1, "Business\nGlossary"),
    (17.6, 4.1, "Precedent\nConversions"),
    (11.0, 2.7, "Rejected\nPatterns"),
    (13.2, 2.7, "Domain\nDecisions"),
    (15.4, 2.7, "Tech\nConventions"),
    (17.6, 2.7, "Convention\nRegistry"),
]
for cx, cy, txt in LT_ITEMS:
    box(cx, cy, txt, C["mem_long"], w=1.85, h=0.65, fontsize=7.5)

# Consistency Agent bar
box(14.4, 1.5, "CONSISTENCY AGENT\nRetrieves top-2 precedents → injects into every Orchestrator + Code-Gen prompt",
    C["consistency"], w=9.5, h=0.7, fontsize=8.0)

# Memory → Pipeline dashed arrows
arrow(5.0, 5.0, 5.0, 10.5, color=C["mem_short"], dashed=True, lw=1.4, label="session ctx")
arrow(14.4, 5.0, 10.7, 10.5, color=C["mem_long"], dashed=True, lw=1.4, label="precedents")
arrow(14.4, 5.0, 8.4, 10.5, color=C["consistency"], dashed=True, lw=1.2)

# ══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════════════════════
LEG = [
    (C["stage"],        "Pipeline Stage"),
    (C["orchestrator"], "Orchestrator"),
    (C["worker"],       "Worker Agent"),
    (C["gen"],          "Generator"),
    (C["eval"],         "LLM Judge"),
    (C["reflect"],      "Reflection"),
    (C["hitl"],         "HITL Gate"),
    (C["mem_short"],    "Short-term Memory"),
    (C["mem_long"],     "Long-term Memory"),
    (C["consistency"],  "Consistency Agent"),
]
lx = 0.5
for col, lbl in LEG:
    patch = mpatches.Patch(facecolor=col, edgecolor="white", linewidth=1.2, label=lbl)
    ax.text(lx + 0.18, 0.18, lbl, va="center", fontsize=6.8, color="#1A252F")
    p = FancyBboxPatch((lx, 0.08), 0.15, 0.20,
                       boxstyle="round,pad=0.03", facecolor=col,
                       edgecolor="white", linewidth=1.0, zorder=5)
    ax.add_patch(p)
    lx += 1.9

plt.tight_layout(pad=0.2)

out = "docs/images/spreadsheet_pipeline.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=C["bg"])
plt.close()
print(f"Saved: {out}")
