"""
Progressive evolution diagrams for Phase 1 — The Augmented LLM.
Every diagram explicitly shows its position on the journey to an Agent.
Each function returns PNG bytes ready for st.image().
"""

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── Colour palette ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#F0F4F8",
    "input":     "#2471A3",   # blue       — user input
    "llm":       "#1A252F",   # dark navy  — LLM core
    "output":    "#1E8449",   # green      — output
    "memory":    "#7D3C98",   # purple     — memory
    "tools":     "#CA6F1E",   # orange     — tools
    "loop":      "#922B21",   # red        — agent loop
    "agent_yes": "#117A65",   # teal-green — AGENT confirmed
    "agent_no":  "#922B21",   # dark red   — NOT an agent
    "note_ok":   "#1A5276",
    "arrow":     "#5D6D7E",
    "dim":       "#AAB7B8",   # muted — already-learned blocks
}
W, H   = 7.0, 4.4          # figure data units (extra height for header/footer)
BOX_W, BOX_H = 1.55, 0.65


# ── Primitives ─────────────────────────────────────────────────────────────────

def _fig():
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.set_facecolor(C["bg"])
    fig.patch.set_facecolor(C["bg"])
    return fig, ax


def _box(ax, cx, cy, text, color, w=BOX_W, h=BOX_H, fontsize=9, dim=False):
    fc = C["dim"] if dim else color
    patch = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=fc, edgecolor="white", linewidth=2.0, zorder=3,
    )
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white" if not dim else "#ECEFF1",
            fontweight="bold", zorder=4, multialignment="center", linespacing=1.4)


def _arrow(ax, x1, y1, x2, y2, label="", color=None, dashed=False):
    color = color or C["arrow"]
    ls = (0, (4, 3)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                mutation_scale=14, linestyle=ls), zorder=5)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.08, label, ha="center", va="bottom",
                fontsize=7, color=color, style="italic", zorder=6)


def _bidir(ax, x1, y1, x2, y2, label_fwd="", label_back="", color=None):
    color = color or C["arrow"]
    dx = (y2-y1)*0.06
    dy = (x1-x2)*0.06
    _arrow(ax, x1+dx, y1+dy, x2+dx, y2+dy, label=label_fwd,  color=color)
    _arrow(ax, x2-dx, y2-dy, x1-dx, y1-dy, label=label_back, color=color)


def _badge(ax, cx, cy, text, color, fontsize=7):
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=color,
                      edgecolor="white", linewidth=1, zorder=5))


def _note(ax, x, y, text, color="#5D6D7E", fontsize=7.8):
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=color, style="italic", zorder=4)


def _agent_banner(ax, is_agent: bool, why: str):
    """
    Top banner: shows AGENT STATUS for this diagram.
    is_agent=True → green AGENT ✓ bar
    is_agent=False → red  NOT AN AGENT bar  + reason
    """
    color  = C["agent_yes"] if is_agent else C["agent_no"]
    icon   = "🤖  AGENT ✓"   if is_agent else "⚠   NOT AN AGENT"
    patch = FancyBboxPatch((0.1, 4.05), 6.8, 0.28,
                           boxstyle="round,pad=0.06",
                           facecolor=color, edgecolor="white",
                           linewidth=1.5, zorder=6)
    ax.add_patch(patch)
    ax.text(W/2, 4.19, f"{icon}  —  {why}",
            ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold", zorder=7)


def _agent_def_footer(ax, highlight_word: str = ""):
    """
    Bottom rule: always shows the definition of an Agent for context.
    """
    ax.plot([0.3, 6.7], [0.52, 0.52], color=C["dim"], lw=0.7, ls="--")
    full = ('Anthropic definition:  "An Agent is an LLM that '
            'dynamically directs its own processes and tool usage"')
    ax.text(W/2, 0.34, full,
            ha="center", va="center", fontsize=7.2,
            color="#5D6D7E", style="italic", zorder=4)


# Full course stops — (key, short_label, full_name)
_STOPS = [
    ("Ph1", "Ph1",  "Phase 1\nAug. LLM"),
    ("2a",  "2a",   "2a\nChaining"),
    ("2b",  "2b",   "2b\nRouting"),
    ("2c",  "2c",   "2c\nParallel"),
    ("2d",  "2d",   "2d\nOrchest."),
    ("2e",  "2e",   "2e\nEvaluator"),
    ("Ph3", "Ph3",  "Phase 3\nAgents"),
    ("4a",  "4a",   "4a\nCust.Sup."),
    ("4b",  "4b",   "4b\nCoding"),
    ("Ph5", "Ph5",  "Phase 5\nBest Prac."),
    ("end", "🤖",   "🤖\nAgent"),
]


def _journey_bar(ax, current: str, y: float = 0.72):
    """
    Draw a full-course progress bar.

    current: key from _STOPS indicating where we are now.
    Completed stops = filled grey dot.
    Current stop    = large orange/teal dot + bold label.
    Future stops    = hollow grey dot.
    """
    keys = [s[0] for s in _STOPS]
    cur_idx = keys.index(current) if current in keys else 0

    n  = len(_STOPS)
    xs = [0.35 + i * (6.30 / (n - 1)) for i in range(n)]

    # Connecting line
    ax.plot([xs[0], xs[-1]], [y, y], color=C["dim"], lw=1.0, zorder=1)

    # Header label
    ax.text(W / 2, y + 0.17,
            "Full Course Journey  —  you are here  ↓",
            ha="center", fontsize=6.5, color=C["dim"], style="italic")

    for i, (x, (key, short, full)) in enumerate(zip(xs, _STOPS)):
        if i < cur_idx:                        # completed
            fc, ec, ms = C["dim"], C["dim"], 7
            lc = C["dim"]
            fw = "normal"
        elif i == cur_idx:                     # current
            fc, ec, ms = C["tools"], C["tools"], 12
            lc = C["tools"]
            fw = "bold"
        else:                                   # future (placeholder)
            fc, ec, ms = C["bg"], C["dim"], 7
            lc = C["dim"]
            fw = "normal"

        ax.plot(x, y, marker="o", ms=ms,
                markerfacecolor=fc, markeredgecolor=ec,
                markeredgewidth=1.4, zorder=3)

        # Label below dot
        ax.text(x, y - 0.12, full if i == cur_idx else short,
                ha="center", va="top", fontsize=5.8 if i != cur_idx else 6.5,
                color=lc, fontweight=fw, multialignment="center", zorder=4)


def _to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 1a — Plain LLM
# ══════════════════════════════════════════════════════════════════════════════

def diagram_1a() -> bytes:
    fig, ax = _fig()

    # ── Agent status banner ────────────────────────────────────────────────────
    _agent_banner(ax, is_agent=False,
                  why="YOU send the message & read the reply — LLM makes no decisions")

    # ── Title ─────────────────────────────────────────────────────────────────
    ax.text(W/2, 3.75, "1a — Plain LLM  (the core building block)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5, "One message in · one reply out · completely stateless",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Boxes ─────────────────────────────────────────────────────────────────
    _box(ax, 1.2, 2.2, "User\nInput",   C["input"])
    _box(ax, 3.5, 2.2, "LLM\nModel",    C["llm"],   w=1.7)
    _box(ax, 5.8, 2.2, "Output\nReply", C["output"])

    _arrow(ax, 2.0,  2.2, 2.72, 2.2, label="prompt")
    _arrow(ax, 4.28, 2.2, 5.02, 2.2, label="reply")

    # ── Journey marker ────────────────────────────────────────────────────────
    _badge(ax, 3.5, 1.35, "Step 1 of 4 towards an Agent", C["llm"], fontsize=7.5)

    # ── Limitation ────────────────────────────────────────────────────────────
    _note(ax, W/2, 0.82,
          "⚠  No memory · no tools · no loop — cannot act autonomously",
          color=C["agent_no"])

    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 1b — + Memory
# ══════════════════════════════════════════════════════════════════════════════

def diagram_1b() -> bytes:
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="LLM still does nothing on its own — YOU control every call")

    ax.text(W/2, 3.75, "1b — + Memory  (Augmented LLM, step 1)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5, "Full conversation history replayed on every call",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Main row ──────────────────────────────────────────────────────────────
    _box(ax, 1.2, 2.55, "User\nInput",   C["input"])
    _box(ax, 3.5, 2.55, "LLM\nModel",    C["llm"],   w=1.7)
    _box(ax, 5.8, 2.55, "Output\nReply", C["output"])

    _arrow(ax, 2.0,  2.55, 2.72, 2.55, label="prompt")
    _arrow(ax, 4.28, 2.55, 5.02, 2.55, label="reply")

    # ── Memory ────────────────────────────────────────────────────────────────
    _box(ax, 3.5, 1.4, "Memory Buffer\n(conversation history)", C["memory"],
         w=2.2, h=0.6)
    _arrow(ax, 3.5, 1.7,  3.5, 2.22, label="history injected", color=C["memory"])
    _arrow(ax, 3.7, 2.22, 3.7, 1.7,  label="turn saved",       color=C["memory"],
           dashed=True)

    _badge(ax, 3.5, 0.88,
           "Step 2 of 4 — smarter LLM, but still not an Agent", C["memory"],
           fontsize=7.5)

    _note(ax, W/2, 0.7,
          "✓  Model remembers context  ·  ⚠  but YOU still decide when & what to ask",
          color=C["note_ok"])

    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 1c — + Tools
# ══════════════════════════════════════════════════════════════════════════════

def diagram_1c() -> bytes:
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="LLM picks the tool BUT you trigger the call & control the flow")

    ax.text(W/2, 3.75, "1c — + Tools  (Augmented LLM, step 2)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Model decides WHICH tool to call · your code executes it",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Main row ──────────────────────────────────────────────────────────────
    _box(ax, 1.0, 2.6,  "User\nInput",   C["input"])
    _box(ax, 3.5, 2.6,  "LLM\nModel",    C["llm"],   w=1.7)
    _box(ax, 6.0, 2.6,  "Output\nReply", C["output"])

    _arrow(ax, 1.78, 2.6, 2.62, 2.6, label="prompt")
    _arrow(ax, 4.38, 2.6, 5.22, 2.6, label="reply")

    # ── Memory (dimmed — from 1b) ──────────────────────────────────────────────
    _box(ax, 2.1, 1.45, "Memory\n(1b)", C["memory"], w=1.3, h=0.55, dim=True)
    _arrow(ax, 2.1, 1.72, 2.75, 2.27, color=C["dim"])

    # ── Tools (new) ───────────────────────────────────────────────────────────
    _box(ax, 5.05, 1.4,
         "Tools  (NEW ✚)\n🌤 Weather  📈 Stock\n🌍 Country  🎉 Holidays  📐 Units",
         C["tools"], w=2.8, h=0.72, fontsize=8)

    _bidir(ax, 4.25, 2.22, 4.8, 1.72,
           label_fwd="call", label_back="result", color=C["tools"])

    _badge(ax, 3.5, 0.88,
           "Step 3 of 4 — powerful, but flow is still YOU → LLM → done", C["tools"],
           fontsize=7.5)

    _note(ax, W/2, 0.7,
          "✓  LLM decides WHAT tool  ·  ⚠  but no loop — it acts once and stops",
          color=C["note_ok"])

    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 1d — Mini Agent  ✓  THIS IS AN AGENT
# ══════════════════════════════════════════════════════════════════════════════

def diagram_1d() -> bytes:
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="LLM decides its OWN next step (call tool / stop) — that is agency")

    ax.text(W/2, 3.75, "1d — Mini Agent  🤖  (this is where Agentic AI begins)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Model drives its own loop · thinks · acts · observes · decides when to stop",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Main flow ─────────────────────────────────────────────────────────────
    _box(ax, 0.85, 2.2, "Goal",          C["input"],  w=1.1,  h=0.6)
    _box(ax, 3.5,  2.2, "LLM\nModel",   C["llm"],    w=1.9,  h=0.8)   # same navy as 1a/1b/1c
    _box(ax, 6.15, 2.2, "Final\nAnswer", C["output"], w=1.35, h=0.6)

    _arrow(ax, 1.4,  2.2, 2.55, 2.2, label="goal")
    _arrow(ax, 4.45, 2.2, 5.47, 2.2, label="done ✓")

    # ── AGENT badge pinned ON the LLM box ─────────────────────────────────────
    _badge(ax, 3.5, 2.72, "🤖  Acting as AGENT", C["agent_yes"], fontsize=8)

    # ── Tool execution ────────────────────────────────────────────────────────
    _box(ax, 3.5, 1.1, "Execute Tool\n(Python code — your control)",
         C["tools"], w=2.8, h=0.6)

    _arrow(ax, 3.2, 1.82, 3.2, 1.4,  label="② call",   color=C["tools"])
    _arrow(ax, 3.8, 1.4,  3.8, 1.82, label="③ result", color=C["tools"])

    # ── Think step badge ──────────────────────────────────────────────────────
    _badge(ax, 3.5, 2.88, "① Think — call tool? or stop?", C["llm"], fontsize=7.5)

    # ── Feedback loop arrow ───────────────────────────────────────────────────
    ax.annotate("", xy=(1.85, 1.85), xytext=(1.85, 2.55),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_yes"], lw=1.8,
                                connectionstyle="arc3,rad=-0.55"), zorder=5)
    ax.text(1.0, 2.2, "↺ loop\nuntil\ndone", ha="center", fontsize=7.5,
            color=C["agent_yes"], fontweight="bold")

    # ── Key distinction box ───────────────────────────────────────────────────
    dist = FancyBboxPatch((0.1, 0.58), 6.8, 0.28,
                          boxstyle="round,pad=0.06",
                          facecolor="#EAF4EC", edgecolor=C["agent_yes"],
                          linewidth=1.5, zorder=3)
    ax.add_patch(dist)
    ax.text(W/2, 0.72,
            "Workflow = YOUR code decides the path   |   Agent = LLM decides the path",
            ha="center", va="center", fontsize=8,
            color=C["agent_yes"], fontweight="bold", zorder=4)

    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 2a — Prompt Chaining
# ══════════════════════════════════════════════════════════════════════════════

def diagram_2a() -> bytes:
    """Sequential chain: each LLM call output feeds the next input."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="YOUR code defines every step in the sequence — LLM does not decide what comes next")

    ax.text(W/2, 3.75, "2a — Prompt Chaining  (Workflow Pattern 1 of 5)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Each LLM call's output becomes the next call's input · sequence is fixed by your code",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Boxes ─────────────────────────────────────────────────────────────────
    _box(ax, 0.55, 2.2, "Customer\nComplaint", C["input"],  w=1.0, h=0.65)
    _box(ax, 1.9,  2.2, "LLM\nClassify",       C["llm"],   w=1.1, h=0.65)
    _box(ax, 3.1,  2.2, "Gate\n✓ / ✗",         C["loop"],  w=0.8, h=0.65)
    _box(ax, 4.3,  2.2, "LLM\nDraft Reply",     C["llm"],   w=1.1, h=0.65)
    _box(ax, 5.7,  2.2, "LLM\nPolish",          C["llm"],   w=1.0, h=0.65)
    _box(ax, 6.7,  2.2, "Final\nEmail",          C["output"],w=0.85,h=0.65)

    # ── Arrows ────────────────────────────────────────────────────────────────
    _arrow(ax, 1.05, 2.2, 1.34, 2.2)
    _arrow(ax, 2.45, 2.2, 2.7,  2.2)
    _arrow(ax, 3.5,  2.2, 3.74, 2.2)
    _arrow(ax, 4.85, 2.2, 5.2,  2.2)
    _arrow(ax, 6.2,  2.2, 6.27, 2.2)

    # ── Data labels below arrows ───────────────────────────────────────────────
    for x, lbl in [(1.2, "text"), (2.57, "category"), (3.62, "draft"), (5.02, "polished")]:
        ax.text(x, 1.82, lbl, ha="center", fontsize=7, color=C["arrow"],
                style="italic")

    # ── Gate stop path ────────────────────────────────────────────────────────
    ax.annotate("", xy=(3.1, 1.35), xytext=(3.1, 1.87),
                arrowprops=dict(arrowstyle="-|>", color=C["loop"], lw=1.5), zorder=5)
    ax.text(3.1, 1.18, "✗ stop\n(e.g. spam)", ha="center", fontsize=7,
            color=C["loop"], fontweight="bold")

    # ── Step badges ───────────────────────────────────────────────────────────
    for x, lbl in [(1.9, "Step 1"), (3.1, "Gate"), (4.3, "Step 2"), (5.7, "Step 3")]:
        _badge(ax, x, 2.72, lbl, C["llm"] if "Step" in lbl else C["loop"], fontsize=7)

    # ── Key note ──────────────────────────────────────────────────────────────
    ax.text(W/2, 1.42,
            "YOUR code wired Step1 → Gate → Step2 → Step3.  "
            "The LLM never decides what happens next — it only processes its own step.",
            ha="center", fontsize=7.8, color=C["note_ok"], style="italic")

    # ── Full course journey bar ────────────────────────────────────────────────
    _journey_bar(ax, current="2a", y=0.95)

    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 2b — Routing
# ══════════════════════════════════════════════════════════════════════════════

def diagram_2b() -> bytes:
    """Routing: classify input first, then send to exactly ONE specialist."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="Router + specialist are both predefined by YOUR code — model only classifies")

    ax.text(W/2, 3.75, "2b — Routing  (Workflow Pattern 2 of 5)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Classify input first · route to ONE specialist · other branches never run",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Input + Router ────────────────────────────────────────────────────────
    _box(ax, 3.5, 3.05, "User\nInput",      C["input"], w=1.3, h=0.55)
    _box(ax, 3.5, 2.35, "LLM\nRouter",      C["llm"],   w=1.3, h=0.55)
    _arrow(ax, 3.5, 2.77, 3.5, 2.63, label="message")

    # ── Four branches ─────────────────────────────────────────────────────────
    branch_xs   = [0.75, 2.25, 3.95, 5.55]
    branch_lbls = ["Billing\nSpecialist", "Technical\nSpecialist",
                   "General\nSpecialist", "Spam\n✗ Stop"]
    branch_cols = [C["tools"], C["memory"], C["note_ok"], C["loop"]]

    for bx, lbl, bc in zip(branch_xs, branch_lbls, branch_cols):
        _arrow(ax, 3.5, 2.07, bx, 1.73, color=C["dim"])
        _box(ax, bx, 1.42, lbl, bc, w=1.3, h=0.55, fontsize=8)

    # ── Only-one-runs note ────────────────────────────────────────────────────
    ax.text(W/2, 2.07, "↙  exactly ONE branch runs  ↘",
            ha="center", fontsize=7.5, color=C["arrow"], style="italic")

    # ── Response ──────────────────────────────────────────────────────────────
    for bx in branch_xs[:3]:
        _arrow(ax, bx, 1.14, bx, 0.9, color=C["dim"])
    _box(ax, 2.35, 0.72, "Specialist Response", C["output"], w=3.3, h=0.38, fontsize=8)

    # ── Key insight ───────────────────────────────────────────────────────────
    ax.text(W/2, 1.42,
            "2a chains ALL steps.  2b runs ONLY ONE branch.  "
            "Unused specialists = zero LLM cost.",
            ha="center", fontsize=7.5, color=C["note_ok"], style="italic")

    _journey_bar(ax, current="2b", y=0.95)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 2c — Parallelization
# ══════════════════════════════════════════════════════════════════════════════

def diagram_2c() -> bytes:
    """Two variants: Sectioning (split → parallel → merge) and Voting (replicate → parallel → vote)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    fig.patch.set_facecolor(C["bg"])

    titles = ["Variant A — Sectioning", "Variant B — Voting"]
    subtitles = [
        "Long input split into chunks · each summarised in parallel · results merged",
        "Same question asked N times in parallel · majority / consensus taken",
    ]

    for idx, (ax, title, subtitle) in enumerate(zip(axes, titles, subtitles)):
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 4.6)
        ax.axis("off")
        ax.set_facecolor(C["bg"])

        # ── Agent banner ──────────────────────────────────────────────────────
        banner_color = C["agent_no"]
        patch = FancyBboxPatch((0.05, 4.22), 4.9, 0.3,
                               boxstyle="round,pad=0.05",
                               facecolor=banner_color, edgecolor="white",
                               linewidth=1.5, zorder=6)
        ax.add_patch(patch)
        ax.text(2.5, 4.37, "⚠  NOT AN AGENT — YOUR code runs the parallel calls",
                ha="center", va="center", fontsize=7.5,
                color="white", fontweight="bold", zorder=7)

        ax.text(2.5, 4.1, title, ha="center", fontsize=10,
                fontweight="bold", color="#1C2833")
        ax.text(2.5, 3.85, subtitle, ha="center", fontsize=7.2,
                color="#566573", style="italic", multialignment="center")

        # ── Input ─────────────────────────────────────────────────────────────
        if idx == 0:
            input_lbl = "Long Input\n(document / feedback)"
        else:
            input_lbl = "Same Question\n(sent N times)"
        inp = FancyBboxPatch((1.5, 3.28), 2.0, 0.45,
                             boxstyle="round,pad=0.08",
                             facecolor=C["input"], edgecolor="white",
                             linewidth=1.5, zorder=3)
        ax.add_patch(inp)
        ax.text(2.5, 3.5, input_lbl, ha="center", va="center",
                fontsize=7.5, color="white", fontweight="bold", zorder=4)

        # ── Split/replicate arrows ─────────────────────────────────────────────
        for tx in [1.0, 2.5, 4.0]:
            ax.annotate("", xy=(tx, 2.72), xytext=(2.5, 3.28),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"],
                                        lw=1.3), zorder=5)

        # ── Parallel LLM boxes ────────────────────────────────────────────────
        parallel_label = "← run in PARALLEL (ThreadPoolExecutor)"
        ax.text(2.5, 2.63, parallel_label, ha="center", fontsize=7,
                color=C["tools"], style="italic", fontweight="bold")

        chunk_lbls = (["Chunk 1\nLLM", "Chunk 2\nLLM", "Chunk 3\nLLM"]
                      if idx == 0 else
                      ["LLM\nCall 1", "LLM\nCall 2", "LLM\nCall 3"])

        for i, (bx, lbl) in enumerate(zip([1.0, 2.5, 4.0], chunk_lbls)):
            p = FancyBboxPatch((bx - 0.6, 1.95), 1.2, 0.6,
                               boxstyle="round,pad=0.08",
                               facecolor=C["llm"], edgecolor="white",
                               linewidth=1.5, zorder=3)
            ax.add_patch(p)
            ax.text(bx, 2.25, lbl, ha="center", va="center",
                    fontsize=7.5, color="white", fontweight="bold", zorder=4)

        # ── Result boxes ──────────────────────────────────────────────────────
        result_lbls = (["Sum 1", "Sum 2", "Sum 3"]
                       if idx == 0 else
                       ["Ans 1", "Ans 2", "Ans 3"])
        result_col = C["tools"] if idx == 0 else C["memory"]

        for bx, lbl in zip([1.0, 2.5, 4.0], result_lbls):
            ax.annotate("", xy=(bx, 1.52), xytext=(bx, 1.95),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.2))
            p2 = FancyBboxPatch((bx - 0.5, 1.15), 1.0, 0.35,
                                boxstyle="round,pad=0.06",
                                facecolor=result_col, edgecolor="white",
                                linewidth=1.2, zorder=3)
            ax.add_patch(p2)
            ax.text(bx, 1.32, lbl, ha="center", va="center",
                    fontsize=7.5, color="white", fontweight="bold", zorder=4)

        # ── Merge / Vote ──────────────────────────────────────────────────────
        for bx in [1.0, 2.5, 4.0]:
            ax.annotate("", xy=(2.5, 0.88), xytext=(bx, 1.15),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.2))

        merge_lbl = "LLM\nMerge" if idx == 0 else "Majority\nVote"
        merge_col = C["tools"] if idx == 0 else C["loop"]
        mp = FancyBboxPatch((1.6, 0.5), 1.8, 0.4,
                            boxstyle="round,pad=0.08",
                            facecolor=merge_col, edgecolor="white",
                            linewidth=1.5, zorder=3)
        ax.add_patch(mp)
        ax.text(2.5, 0.7, merge_lbl, ha="center", va="center",
                fontsize=8, color="white", fontweight="bold", zorder=4)

        ax.annotate("", xy=(2.5, 0.18), xytext=(2.5, 0.5),
                    arrowprops=dict(arrowstyle="-|>", color=C["output"], lw=1.5))

        out_lbl = "Final Summary" if idx == 0 else "Final Answer"
        ax.text(2.5, 0.1, out_lbl, ha="center", va="center",
                fontsize=8, color=C["output"], fontweight="bold")

    # ── Shared journey bar ────────────────────────────────────────────────────
    bar_ax = fig.add_axes([0.03, 0.0, 0.94, 0.08])
    bar_ax.set_facecolor(C["bg"])
    bar_ax.set_xlim(0, 10)
    bar_ax.set_ylim(0, 1)
    bar_ax.axis("off")

    keys  = [s[0] for s in _STOPS]
    cur   = "2c"
    cur_i = keys.index(cur)
    xs    = [0.5 + i * (9.0 / (len(_STOPS) - 1)) for i in range(len(_STOPS))]

    bar_ax.plot([xs[0], xs[-1]], [0.55, 0.55], color=C["dim"], lw=1.0)
    bar_ax.text(5.0, 0.92, "Full Course Journey — you are here ↓",
                ha="center", fontsize=6.5, color=C["dim"], style="italic")

    for i, (x, (key, short, full)) in enumerate(zip(xs, _STOPS)):
        fc = C["tools"] if i == cur_i else (C["dim"] if i < cur_i else C["bg"])
        ec = C["tools"] if i == cur_i else C["dim"]
        ms = 10 if i == cur_i else 6
        bar_ax.plot(x, 0.55, "o", ms=ms, markerfacecolor=fc,
                    markeredgecolor=ec, markeredgewidth=1.2)
        lc = C["tools"] if i == cur_i else C["dim"]
        fw = "bold" if i == cur_i else "normal"
        bar_ax.text(x, 0.18, full if i == cur_i else short,
                    ha="center", va="top", fontsize=5.5,
                    color=lc, fontweight=fw, multialignment="center")

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 2d — Orchestrator-Workers
# ══════════════════════════════════════════════════════════════════════════════

def diagram_2d() -> bytes:
    """Orchestrator LLM plans tasks dynamically; Worker LLMs execute each one."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="Orchestrator plans ONCE upfront — no feedback loop, no course-correction")

    ax.text(W/2, 3.75, "2d — Orchestrator-Workers  (Workflow Pattern 4 of 5)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Orchestrator LLM dynamically plans sub-tasks · Workers execute in parallel · Orchestrator assembles",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Input ─────────────────────────────────────────────────────────────────
    _box(ax, 3.5, 3.1, "Goal / Complaint", C["input"], w=2.2, h=0.5)
    _arrow(ax, 3.5, 2.85, 3.5, 2.67)

    # ── Orchestrator ──────────────────────────────────────────────────────────
    _box(ax, 3.5, 2.42, "Orchestrator LLM\n(plans sub-tasks dynamically)", C["loop"],
         w=3.2, h=0.46)
    _badge(ax, 3.5, 2.75, "dynamically decides tasks ← first hint of agency", C["loop"],
           fontsize=7)

    # ── Workers ───────────────────────────────────────────────────────────────
    worker_xs = [0.85, 2.1, 3.5, 4.9, 6.15]
    worker_lbls = ["Sentiment\nAnalyst", "Solution\nResearcher",
                   "Response\nDrafter", "Escalation\nChecker", "Knowledge\nUpdater"]
    worker_col = C["llm"]

    for wx, wl in zip(worker_xs, worker_lbls):
        _arrow(ax, 3.5, 2.19, wx, 1.82, color=C["dim"])
        _box(ax, wx, 1.56, wl, worker_col, w=1.12, h=0.48, fontsize=7.5)

    ax.text(W/2, 2.07, "Workers run in parallel  →  each is a specialised LLM call",
            ha="center", fontsize=7.2, color=C["tools"], style="italic", fontweight="bold")

    # ── Results converge ──────────────────────────────────────────────────────
    for wx in worker_xs:
        _arrow(ax, wx, 1.32, 3.5, 1.0, color=C["dim"])

    _box(ax, 3.5, 0.78, "Orchestrator assembles\nfinal package", C["loop"],
         w=3.0, h=0.4)
    _arrow(ax, 3.5, 0.58, 3.5, 0.42, color=C["output"])
    ax.text(3.5, 0.33, "Final Output", ha="center", fontsize=8,
            color=C["output"], fontweight="bold")

    # ── NOT agent note ────────────────────────────────────────────────────────
    ax.text(W/2, 1.42,
            "⚠  Not an agent: plan made ONCE upfront. Worker results don't change the plan.",
            ha="center", fontsize=7.5, color=C["agent_no"], style="italic")

    _journey_bar(ax, current="2d", y=0.96)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 2e — Evaluator-Optimizer
# ══════════════════════════════════════════════════════════════════════════════

def diagram_2e() -> bytes:
    """Generator + Evaluator in a feedback loop until quality threshold is met."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="Loop structure is YOUR code — model cannot decide to exit differently or try new strategies")

    ax.text(W/2, 3.75, "2e — Evaluator-Optimizer  (Workflow Pattern 5 of 5)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Generator produces · Evaluator scores · loop repeats until threshold met",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Input ─────────────────────────────────────────────────────────────────
    _box(ax, 3.5, 3.1, "Complaint / Task", C["input"], w=2.2, h=0.48)
    _arrow(ax, 3.5, 2.86, 3.5, 2.7)

    # ── Loop boundary box ─────────────────────────────────────────────────────
    loop_patch = FancyBboxPatch((0.25, 0.88), 6.5, 1.75,
                                boxstyle="round,pad=0.1",
                                facecolor="#F8F4FF", edgecolor=C["memory"],
                                linewidth=2.0, linestyle="--", zorder=1)
    ax.add_patch(loop_patch)
    ax.text(0.48, 2.56, "↺ LOOP", ha="left", fontsize=8,
            color=C["memory"], fontweight="bold")

    # ── Generator ─────────────────────────────────────────────────────────────
    _box(ax, 1.8, 2.38, "Generator\nLLM", C["llm"], w=1.55, h=0.52)
    _arrow(ax, 2.58, 2.38, 3.18, 2.38, label="draft")

    # ── Draft response ────────────────────────────────────────────────────────
    _box(ax, 3.85, 2.38, "Draft\nResponse", C["tools"], w=1.3, h=0.52)
    _arrow(ax, 4.5, 2.38, 5.1, 2.38, label="evaluate")

    # ── Evaluator ─────────────────────────────────────────────────────────────
    _box(ax, 5.65, 2.38, "Evaluator\nLLM", C["loop"], w=1.35, h=0.52)

    # ── Score + feedback down ─────────────────────────────────────────────────
    _arrow(ax, 5.65, 2.12, 5.65, 1.62, label="score + feedback")
    _box(ax, 5.65, 1.38, "Score\n& Feedback", C["loop"], w=1.35, h=0.46)

    # ── Decision: score < threshold → loop back ───────────────────────────────
    ax.annotate("", xy=(1.8, 2.12), xytext=(5.65, 1.15),
                arrowprops=dict(arrowstyle="-|>", color=C["memory"], lw=1.8,
                                connectionstyle="arc3,rad=0.0"), zorder=5)
    ax.text(3.5, 0.97, "score < threshold  →  feed back to Generator",
            ha="center", fontsize=7.5, color=C["memory"],
            style="italic", fontweight="bold")

    # ── Exit: score >= threshold ──────────────────────────────────────────────
    _arrow(ax, 3.5, 0.88, 3.5, 0.52, color=C["output"])
    ax.text(0.55, 0.7, "score ≥ threshold", ha="left", fontsize=7.5,
            color=C["output"], fontweight="bold")
    _box(ax, 3.5, 0.35, "Final Response ✓", C["output"], w=2.2, h=0.38)

    _journey_bar(ax, current="2e", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3 — Autonomous Agent (ReAct)
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3() -> bytes:
    """Full autonomous agent: model controls its own Think → Act → Observe loop."""
    fig, ax = _fig()

    # ── AGENT ✓ banner ────────────────────────────────────────────────────────
    _agent_banner(ax, is_agent=True,
                  why="Model decides every next step — calls tools, observes results, decides when done")

    ax.text(W/2, 3.75, "Phase 3a — ReAct Agent  🤖",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "No predefined structure · model plans, acts, observes and loops until it decides the goal is met",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Goal input ────────────────────────────────────────────────────────────
    _box(ax, 3.5, 3.08, "Goal", C["input"], w=1.5, h=0.46)
    _arrow(ax, 3.5, 2.85, 3.5, 2.68)

    # ── Autonomous agent boundary ─────────────────────────────────────────────
    agent_box = FancyBboxPatch((0.3, 0.96), 6.4, 1.65,
                               boxstyle="round,pad=0.12",
                               facecolor="#EAF4EC", edgecolor=C["agent_yes"],
                               linewidth=2.5, zorder=1)
    ax.add_patch(agent_box)
    ax.text(0.55, 2.54, "🤖  AUTONOMOUS AGENT",
            ha="left", fontsize=8, color=C["agent_yes"], fontweight="bold")

    # ── ReAct triangle: Think → Act → Observe ─────────────────────────────────
    _box(ax, 2.0, 2.1, "① Think\n(reason)",  C["llm"],       w=1.4, h=0.52)
    _box(ax, 3.5, 1.35, "② Act\n(call tool)", C["tools"],     w=1.4, h=0.52)
    _box(ax, 5.0, 2.1, "③ Observe\n(result)", C["memory"],    w=1.4, h=0.52)

    # Think → Act
    _arrow(ax, 2.55, 1.88, 2.9, 1.62, label="chosen tool", color=C["tools"])
    # Act → Observe
    _arrow(ax, 4.1, 1.62, 4.45, 1.88, label="result",       color=C["memory"])
    # Observe → Think (loop back)
    _arrow(ax, 4.3, 2.25, 2.7, 2.25, label="adapt plan",    color=C["llm"])

    # ── "decides when done" exit arrow ────────────────────────────────────────
    ax.annotate("", xy=(3.5, 0.94), xytext=(3.5, 1.09),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_yes"], lw=1.8))
    ax.text(4.6, 1.02, "model decides → done",
            fontsize=7.5, color=C["agent_yes"], fontweight="bold", style="italic")

    _box(ax, 3.5, 0.72, "Final Answer", C["output"], w=2.0, h=0.38)

    # ── Tools available ───────────────────────────────────────────────────────
    ax.text(W/2, 1.62,
            "Tools: get_weather · get_stock_price · convert_units · get_country_info · "
            "get_public_holidays · calculator · check_even_odd",
            ha="center", fontsize=6.8, color=C["tools"], style="italic")

    _journey_bar(ax, current="Ph3", y=0.95)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3b — Guardrails
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3b() -> bytes:
    """Guardrails: input and output safety layers wrapping the agent."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Still an agent — guardrails are safety wrappers, not replacements for agency")

    ax.text(W/2, 3.75, "Phase 4a — Guardrails  🛡️",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Safety layers wrap the agent · input checked before the model · output checked before the user",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── User input ────────────────────────────────────────────────────────────
    _box(ax, 3.5, 3.1, "User Input", C["input"], w=1.8, h=0.46)
    _arrow(ax, 3.5, 2.87, 3.5, 2.68)

    # ── INPUT GUARDRAIL ───────────────────────────────────────────────────────
    inp_patch = FancyBboxPatch((0.3, 2.08), 6.4, 0.54,
                               boxstyle="round,pad=0.08",
                               facecolor="#FDEDEC", edgecolor=C["agent_no"],
                               linewidth=2.0, zorder=2)
    ax.add_patch(inp_patch)
    ax.text(3.5, 2.42, "🛡️  INPUT GUARDRAIL",
            ha="center", fontsize=9, color=C["agent_no"], fontweight="bold", zorder=3)
    ax.text(3.5, 2.2,
            "PII detection (regex)  ·  Prompt injection (LLM)  ·  Jailbreak (LLM)  ·  Harmful content (LLM)",
            ha="center", fontsize=7.2, color=C["agent_no"], style="italic", zorder=3)

    # ── Block path (input fails) ───────────────────────────────────────────────
    _arrow(ax, 0.62, 2.35, 0.62, 1.6, color=C["agent_no"])
    ax.text(0.62, 1.45, "BLOCKED\n✗", ha="center", fontsize=7.5,
            color=C["agent_no"], fontweight="bold")

    # ── Pass arrow ────────────────────────────────────────────────────────────
    _arrow(ax, 3.5, 2.08, 3.5, 1.92, label="PASS ✓", color=C["agent_yes"])

    # ── Agent ─────────────────────────────────────────────────────────────────
    _box(ax, 3.5, 1.65, "🤖  Autonomous Agent", C["agent_yes"], w=2.8, h=0.46)

    _arrow(ax, 3.5, 1.42, 3.5, 1.26, label="response", color=C["agent_yes"])

    # ── OUTPUT GUARDRAIL ──────────────────────────────────────────────────────
    out_patch = FancyBboxPatch((0.3, 0.72), 6.4, 0.48,
                               boxstyle="round,pad=0.08",
                               facecolor="#FEF9E7", edgecolor=C["tools"],
                               linewidth=2.0, zorder=2)
    ax.add_patch(out_patch)
    ax.text(3.5, 1.04, "🛡️  OUTPUT GUARDRAIL",
            ha="center", fontsize=9, color=C["tools"], fontweight="bold", zorder=3)
    ax.text(3.5, 0.84,
            "PII leak (regex)  ·  Policy compliance (LLM)  ·  Sensitive info check (LLM)",
            ha="center", fontsize=7.2, color=C["tools"], style="italic", zorder=3)

    # ── Flag path (output fails) ───────────────────────────────────────────────
    _arrow(ax, 6.38, 0.96, 6.38, 0.38, color=C["tools"])
    ax.text(6.38, 0.26, "FLAGGED\n⚠", ha="center", fontsize=7.5,
            color=C["tools"], fontweight="bold")

    _arrow(ax, 3.5, 0.72, 3.5, 0.5, color=C["output"])
    ax.text(3.5, 0.35, "Safe response delivered ✓",
            ha="center", fontsize=8, color=C["output"], fontweight="bold")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3c — Human-in-the-Loop
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3c() -> bytes:
    """HITL: agent pauses at a checkpoint, waits for human approval."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Agent pauses at checkpoints — human judgment overrides automation for high-stakes decisions")

    ax.text(W/2, 3.75, "Phase 4b — Human-in-the-Loop (HITL)  👤",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Agent runs autonomously · pauses at risk checkpoints · human decides · agent resumes or stops",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Input → Agent ──────────────────────────────────────────────────────────
    _box(ax, 1.0, 2.8, "Customer\nRequest", C["input"],  w=1.5, h=0.46)
    _box(ax, 3.0, 2.8, "Agent\nAnalyses",   C["llm"],    w=1.5, h=0.46)
    _arrow(ax, 1.75, 2.8, 2.25, 2.8, label="request")

    # ── Checkpoint diamond ────────────────────────────────────────────────────
    diamond_x, diamond_y = 3.0, 2.05
    from matplotlib.patches import Polygon
    d = 0.35
    diamond = Polygon(
        [[diamond_x, diamond_y+d], [diamond_x+d*1.5, diamond_y],
         [diamond_x, diamond_y-d], [diamond_x-d*1.5, diamond_y]],
        facecolor="#F5CBA7", edgecolor=C["tools"], linewidth=2, zorder=3
    )
    ax.add_patch(diamond)
    ax.text(diamond_x, diamond_y, "Risk\nCheck?", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#784212", zorder=4)
    _arrow(ax, 3.0, 2.57, 3.0, 2.4, color=C["tools"])

    # ── Low risk path (right) ──────────────────────────────────────────────────
    _arrow(ax, 3.52, 2.05, 4.8, 2.05, label="low risk", color=C["agent_yes"])
    _box(ax, 5.6, 2.05, "Auto\nResponse", C["agent_yes"], w=1.4, h=0.44)

    # ── High risk path (down → human review) ──────────────────────────────────
    _arrow(ax, 3.0, 1.7, 3.0, 1.5, label="high risk / uncertain", color=C["loop"])

    hitl_patch = FancyBboxPatch((1.0, 0.88), 4.0, 0.56,
                                boxstyle="round,pad=0.08",
                                facecolor="#FDEDEC", edgecolor=C["loop"],
                                linewidth=2.2, zorder=2)
    ax.add_patch(hitl_patch)
    ax.text(3.0, 1.3, "👤  HUMAN REVIEW  —  Approve / Reject / Modify",
            ha="center", va="center", fontsize=9,
            color=C["loop"], fontweight="bold", zorder=3)
    ax.text(3.0, 1.05, "Human sees: agent's reasoning · proposed action · risk factors · draft response",
            ha="center", va="center", fontsize=7, color=C["loop"],
            style="italic", zorder=3)

    # ── Three outcomes ────────────────────────────────────────────────────────
    out_xs  = [1.4,  3.0,  4.6]
    out_lbl = ["✅ Approve\n→ agent sends", "❌ Reject\n→ stop", "✏️ Modify\n→ edit + send"]
    out_col = [C["agent_yes"], C["agent_no"], C["tools"]]
    for ox, ol, oc in zip(out_xs, out_lbl, out_col):
        _arrow(ax, ox, 0.88, ox, 0.62, color=oc)
        ax.text(ox, 0.48, ol, ha="center", fontsize=7.5, color=oc,
                fontweight="bold", multialignment="center")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3d — RAG Agent
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3d() -> bytes:
    """RAG Agent: Retrieve → Augment → Generate, agent-controlled."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Agent decides when to search, what to search for, and how many times")

    ax.text(W/2, 3.75, "Phase 5a — RAG Agent  📚  (Retrieval-Augmented Generation)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Agent searches a knowledge base before answering · responses grounded in real documents",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── WITHOUT RAG (left) ────────────────────────────────────────────────────
    _box(ax, 1.0, 3.0, "User\nQuery",  C["input"], w=1.3, h=0.46)
    _arrow(ax, 1.0, 2.77, 1.0, 2.28, color=C["dim"])
    _box(ax, 1.0, 2.05, "LLM only\n(training data)", C["dim"], w=1.5, h=0.46)
    _arrow(ax, 1.0, 1.82, 1.0, 1.38, color=C["dim"])
    ax.text(1.0, 1.22, "⚠ Hallucination\nrisk — no domain\nknowledge",
            ha="center", fontsize=7.5, color=C["agent_no"],
            fontweight="bold", multialignment="center")
    ax.text(1.0, 3.28, "Without RAG", ha="center", fontsize=8,
            color=C["dim"], fontweight="bold")

    # Divider
    ax.plot([2.1, 2.1], [0.8, 3.45], color=C["dim"], lw=1.0, ls="--")

    # ── WITH RAG (right — Retrieve → Augment → Generate) ─────────────────────
    ax.text(4.7, 3.28, "With RAG Agent", ha="center", fontsize=8,
            color=C["agent_yes"], fontweight="bold")

    _box(ax, 3.3, 3.0, "User\nQuery",  C["input"], w=1.3, h=0.46)
    _arrow(ax, 3.3, 2.77, 3.3, 2.28, label="embed query")

    # ── R — Retrieve ──────────────────────────────────────────────────────────
    _box(ax, 3.3, 2.05, "① Retrieve\n(cosine search)", C["memory"], w=1.5, h=0.46)
    _arrow(ax, 5.5, 2.05, 4.05, 2.05, color=C["memory"])
    _box(ax, 6.0, 2.05, "Knowledge Base\n📄 Domain Docs", C["tools"], w=1.7, h=0.46)
    _badge(ax, 6.0, 1.72, "embeddings (text-embedding-004)", C["tools"], fontsize=6.5)

    _arrow(ax, 3.3, 1.82, 3.3, 1.38, label="top-K chunks")

    # ── A — Augment ───────────────────────────────────────────────────────────
    _box(ax, 3.3, 1.15, "② Augment\nquery + context", C["loop"], w=1.5, h=0.46)
    _arrow(ax, 3.3, 0.92, 3.3, 0.6, label="grounded prompt")

    # ── G — Generate ──────────────────────────────────────────────────────────
    _box(ax, 3.3, 0.42, "③ Generate\n(LLM + context)", C["llm"], w=1.5, h=0.4)
    _arrow(ax, 4.05, 0.42, 5.5, 0.42, color=C["agent_yes"])
    ax.text(5.85, 0.42, "✅ Grounded\nResponse",
            ha="center", va="center", fontsize=8,
            color=C["agent_yes"], fontweight="bold")

    # ── Agent loop note ───────────────────────────────────────────────────────
    ax.annotate("", xy=(3.3, 2.77), xytext=(4.6, 2.77),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_yes"], lw=1.4,
                                connectionstyle="arc3,rad=-0.4"))
    ax.text(4.6, 2.6, "agent may\nsearch again",
            ha="center", fontsize=6.5, color=C["agent_yes"], style="italic")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Agent Anatomy (component breakdown)
# ══════════════════════════════════════════════════════════════════════════════

def diagram_agent_anatomy() -> bytes:
    """
    Clean agent anatomy diagram.
    Layout (14 wide x 10 tall data units):
      Row 0 (y 9.2-9.8): title
      Row 1 (y 8.2-8.7): Instructions banner  — inside agent
      Row 2 (y 6.4-7.6): Memory | LLM/Brain | HITL  — inside agent
      Row 3 (y 4.6-5.6): KB/RAG | Tool Executor | A2A/MCP  — inside agent
      Guardrails: wraps rows 1-3  (y 4.2 - 9.0)
      Agent:      inner  (y 4.5 - 8.8)
      Row 4 (y 2.8-3.6): External: User  Agent  Response (left/center/right)
      Row 5 (y 1.0-2.0): External bottom: Docs | APIs | Other Agents
    All column centres: x = 2.8, 7.0, 11.2  (columns A B C)
    """
    W, H = 14.0, 10.0
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.set_facecolor("#F0F4F8")
    fig.patch.set_facecolor("#F0F4F8")

    # ── helpers ───────────────────────────────────────────────────────────────
    def bx(cx, cy, w, h, lines, fc, ec="white", lw=2.0, fs=8.5, z=4):
        p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                           boxstyle="round,pad=0.12",
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
        ax.add_patch(p)
        ax.text(cx, cy, "\n".join(lines), ha="center", va="center",
                fontsize=fs, color="white", fontweight="bold",
                zorder=z+1, multialignment="center", linespacing=1.5)

    def caption(cx, cy, txt, color="#566573"):
        ax.text(cx, cy, txt, ha="center", va="center",
                fontsize=6.8, color=color, style="italic", zorder=5)

    def arr(x1, y1, x2, y2, lbl="", color="#5D6D7E"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                    lw=1.8, mutation_scale=14), zorder=8)
        if lbl:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.12, lbl, ha="center", va="bottom",
                    fontsize=6.5, color=color, style="italic", zorder=9)

    def bidir(x1, y1, x2, y2, lbl_f="", lbl_b="", color="#5D6D7E"):
        dx, dy = (y2-y1)*0.06, (x1-x2)*0.06
        arr(x1+dx, y1+dy, x2+dx, y2+dy, lbl_f, color)
        arr(x2-dx, y2-dy, x1-dx, y1-dy, lbl_b, color)

    # ═══════════════════════════════════════════════════════════════════════════
    # TITLE
    # ═══════════════════════════════════════════════════════════════════════════
    ax.text(7.0, 9.65, "Anatomy of an Agent",
            ha="center", fontsize=15, fontweight="bold", color="#1C2833")
    ax.text(7.0, 9.32,
            'Anthropic: "An LLM enhanced with memory, tools and augmentations '
            'that dynamically directs its own processes"',
            ha="center", fontsize=8.5, color="#566573", style="italic")

    # ═══════════════════════════════════════════════════════════════════════════
    # GUARDRAILS OUTER BOUNDARY  (dashed red)
    # ═══════════════════════════════════════════════════════════════════════════
    g = FancyBboxPatch((1.1, 4.0), 11.8, 5.0,
                       boxstyle="round,pad=0.15",
                       facecolor="#FEF2F2", edgecolor=C["agent_no"],
                       linewidth=2.5, linestyle=(0, (6, 3)), zorder=1)
    ax.add_patch(g)
    ax.text(1.4, 8.9, "🛡️  GUARDRAILS  —  input safety + output safety  (Phase 4a)",
            ha="left", fontsize=8.5, color=C["agent_no"], fontweight="bold")

    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT INNER BOUNDARY  (solid green)
    # ═══════════════════════════════════════════════════════════════════════════
    a = FancyBboxPatch((1.45, 4.3), 11.1, 4.45,
                       boxstyle="round,pad=0.12",
                       facecolor="#EAF4EC", edgecolor=C["agent_yes"],
                       linewidth=2.5, zorder=2)
    ax.add_patch(a)
    ax.text(1.75, 8.65, "🤖  AGENT",
            ha="left", fontsize=9, color=C["agent_yes"], fontweight="bold")

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 1 — INSTRUCTIONS  (top banner inside agent)
    # ═══════════════════════════════════════════════════════════════════════════
    bx(7.0, 8.15, 10.2, 0.62,
       ["📋  Instructions / Persona  (System Prompt)",
        "Defines scope · persona · rules · what agent CAN and CANNOT do"],
       "#2E4057", fs=8.5, z=5)
    arr(7.0, 7.84, 7.0, 7.42, "defines behaviour", "#2E4057")

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 2 — MEMORY | LLM/BRAIN | HITL
    # ═══════════════════════════════════════════════════════════════════════════
    # Column A: Memory  (x=2.8)
    bx(2.8, 6.7, 3.2, 1.3,
       ["💾  Memory",
        "Short-term: context window",
        "Long-term: vector store",
        "Episodic: past sessions"],
       C["memory"], fs=8, z=5)
    caption(2.8, 5.97, "Phase 1b · 5b", C["memory"])

    # Column B: LLM / BRAIN  (x=7.0)
    bx(7.0, 6.7, 3.4, 1.5,
       ["🧠  LLM / BRAIN",
        "Gemini 2.5 Flash",
        "Reasons · Plans · Decides",
        "call tool | search KB",
        "ask human | stop"],
       C["llm"], lw=3.0, fs=8.5, z=6)
    caption(7.0, 5.91, "Phase 1a — the core building block", C["llm"])

    # Column C: HITL  (x=11.2)
    bx(11.2, 6.7, 3.2, 1.3,
       ["👤  HITL Checkpoint",
        "High-risk action pause",
        "Approve · Reject · Modify"],
       C["loop"], fs=8, z=5)
    caption(11.2, 5.97, "Phase 4b", C["loop"])

    # Memory ↔ LLM
    bidir(4.4, 6.8, 5.3, 6.8, "recall", "store", C["memory"])
    # LLM ↔ HITL
    bidir(8.7, 6.8, 9.6, 6.8, "flag", "decision", C["loop"])

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 3 — KB/RAG | TOOLS | A2A/MCP
    # ═══════════════════════════════════════════════════════════════════════════
    # Column A: KB / RAG
    bx(2.8, 5.0, 3.2, 0.85,
       ["📚  Knowledge Base  (RAG)",
        "Domain docs · embeddings · search"],
       C["tools"], fs=8, z=5)
    caption(2.8, 4.51, "Phase 5a", C["tools"])

    # Column B: Tool Executor
    bx(7.0, 5.0, 3.4, 0.85,
       ["🔧  Tool Executor",
        "weather · stock · APIs · calculator"],
       C["tools"], fs=8, z=5)
    caption(7.0, 4.51, "Phase 1c · 1d · 3a", C["tools"])

    # Column C: A2A / MCP
    bx(11.2, 5.0, 3.2, 0.85,
       ["🔗  A2A / MCP Interfaces",
        "Agent ↔ agent · agent ↔ tool server"],
       "#1A5276", fs=8, z=5)
    caption(11.2, 4.51, "Phase 6b (MCP) · 6c (A2A)", "#1A5276")

    # LLM → KB (retrieve), LLM → Tools (call), LLM → A2A (delegate)
    arr(4.4, 6.2, 3.5, 5.43, "retrieve", C["tools"])
    arr(7.0, 5.94, 7.0, 5.43, "call / result", C["tools"])
    arr(9.6, 6.2, 10.5, 5.43, "delegate", "#1A5276")

    # ═══════════════════════════════════════════════════════════════════════════
    # EXTERNAL ENTITIES  (outside guardrails)
    # ═══════════════════════════════════════════════════════════════════════════
    # User (far left)
    bx(0.55, 6.7, 1.1, 1.0, ["👤", "User"], C["input"], fs=9, z=7)
    bidir(1.1, 6.9, 1.45, 6.9, "query", "reply", C["input"])

    # Response label (far right) — just an output arrow indicator
    bx(13.45, 6.7, 1.1, 1.0, ["📤", "Response"], C["output"], fs=9, z=7)
    arr(12.8, 6.9, 13.0, 6.9, "", C["output"])
    arr(13.0, 6.5, 12.8, 6.5, "", C["output"])

    # Bottom row: domain docs, external APIs, other agents
    bx(2.8, 3.1, 3.2, 0.7, ["📄  Domain Documents", "policy · FAQ · specs"], "#778899", fs=7.5, z=4)
    arr(2.8, 4.51, 2.8, 3.45, "", C["tools"])

    bx(7.0, 3.1, 3.4, 0.7, ["🌐  External APIs", "Open-Meteo · Yahoo · REST APIs"], "#778899", fs=7.5, z=4)
    arr(7.0, 4.51, 7.0, 3.45, "", C["tools"])

    bx(11.2, 3.1, 3.2, 0.7, ["🤖  Other Agents", "A2A network · sub-agents"], "#778899", fs=7.5, z=4)
    arr(11.2, 4.51, 11.2, 3.45, "", "#1A5276")

    # ═══════════════════════════════════════════════════════════════════════════
    # LEGEND
    # ═══════════════════════════════════════════════════════════════════════════
    legend = [
        (C["llm"],       "LLM / Brain"),
        (C["memory"],    "Memory"),
        (C["tools"],     "Tools & KB"),
        (C["loop"],      "HITL"),
        ("#1A5276",      "Protocols"),
        (C["agent_no"],  "Guardrails"),
        (C["agent_yes"], "Agent boundary"),
    ]
    ax.text(7.0, 2.35, "Component legend:", ha="center", fontsize=8,
            color="#566573", fontweight="bold")
    total_w = (len(legend) - 1) * 1.95
    x0 = 7.0 - total_w / 2
    for i, (col, lbl) in enumerate(legend):
        lx = x0 + i * 1.95
        p = FancyBboxPatch((lx - 0.15, 1.85), 0.3, 0.25,
                           boxstyle="round,pad=0.03",
                           facecolor=col, edgecolor="white", linewidth=1, zorder=5)
        ax.add_patch(p)
        ax.text(lx, 1.65, lbl, ha="center", va="top",
                fontsize=6.5, color="#1C2833")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3e — LLM-as-Judge
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3e() -> bytes:
    """LLM-as-Judge: independent evaluation gate with three verdicts."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Agent answers · independent Judge evaluates · verdict routes the response")

    ax.text(W/2, 3.75, "Phase 4c — LLM-as-Judge  ⚖️",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Separate Judge LLM evaluates the agent's response · PASS · REVIEW · FAIL",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    # ── Question → Agent → Response ──────────────────────────────────────────
    _box(ax, 0.7,  2.55, "Question",   C["input"],  w=1.1, h=0.5)
    _box(ax, 2.1,  2.55, "Agent\nLLM", C["llm"],    w=1.2, h=0.5)
    _box(ax, 3.6,  2.55, "Response",   C["tools"],  w=1.3, h=0.5)

    _arrow(ax, 1.25, 2.55, 1.5, 2.55)
    _arrow(ax, 2.7,  2.55, 2.95, 2.55)

    # ── Judge (independent) ───────────────────────────────────────────────────
    _arrow(ax, 3.6, 2.3, 3.6, 1.82, label="evaluate", color=C["memory"])
    _box(ax, 3.6, 1.42,
         "⚖️  JUDGE LLM  (independent — separate context)",
         C["memory"], w=2.8, h=0.65)
    _badge(ax, 3.6, 1.9, "accuracy · groundedness · tone · completeness", C["memory"], fontsize=7)

    # ── Three verdict paths ───────────────────────────────────────────────────
    # PASS (left)
    _arrow(ax, 2.2, 1.42, 1.3, 0.88, color=C["agent_yes"])
    _box(ax, 0.85, 0.62, "✅ PASS\nDeliver to user",    C["agent_yes"], w=1.5, h=0.48, fontsize=8)

    # REVIEW (centre)
    _arrow(ax, 3.6, 1.09, 3.6, 0.88, color=C["tools"])
    _box(ax, 3.6,  0.62, "🟡 REVIEW\nEscalate to HITL", C["tools"],    w=1.5, h=0.48, fontsize=8)

    # FAIL (right)
    _arrow(ax, 5.0, 1.42, 5.95, 0.88, color=C["agent_no"])
    _box(ax, 6.3,  0.62, "❌ FAIL\nRetry / Fallback",   C["agent_no"], w=1.5, h=0.48, fontsize=8)

    # ── Contrast note ─────────────────────────────────────────────────────────
    ax.text(W/2, 2.92,
            "≠ 4a Guardrails (safety)    ≠ 2e Evaluator-Optimizer (improve)    = quality gate (route)",
            ha="center", fontsize=7.5, color=C["memory"], style="italic")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram 3f — Reflection Agent
# ══════════════════════════════════════════════════════════════════════════════

def diagram_3f() -> bytes:
    """Reflection: one LLM generates, then critiques its own output, then revises."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    fig.patch.set_facecolor(C["bg"])

    # ── Shared helpers ────────────────────────────────────────────────────────
    def bx(ax, cx, cy, w, h, lines, fc, ec="white", lw=2, fs=8, z=3):
        p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                           boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
        ax.add_patch(p)
        ax.text(cx, cy, "\n".join(lines), ha="center", va="center",
                fontsize=fs, color="white", fontweight="bold",
                zorder=z+1, multialignment="center", linespacing=1.4)

    def ar(ax, x1, y1, x2, y2, lbl="", color=C["arrow"]):
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                    mutation_scale=13), zorder=5)
        if lbl:
            ax.text((x1+x2)/2, (y1+y2)/2+0.08, lbl, ha="center",
                    fontsize=6.5, color=color, style="italic", zorder=6)

    # ══ PANEL 1 — Basic Self-Reflection ═════════════════════════════════════
    ax = axes[0]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.6); ax.axis("off")
    ax.set_facecolor(C["bg"])

    # Banner
    p = FancyBboxPatch((0, 4.25), 5, 0.3,
                       boxstyle="round,pad=0.05",
                       facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p)
    ax.text(2.5, 4.4, "🤖  AGENT  ✓  —  Variant A: Self-Reflection",
            ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold", zorder=5)

    ax.text(2.5, 4.1, "One LLM · generates then critiques its own output",
            ha="center", fontsize=7.5, color="#566573", style="italic")

    # Task input
    bx(ax, 2.5, 3.5, 2.6, 0.5, ["Task / Prompt"], C["input"], fs=8.5)
    ar(ax, 2.5, 3.25, 2.5, 2.9)

    # LLM (centre — same model for both generate + reflect)
    bx(ax, 2.5, 2.55, 3.0, 0.65,
       ["🧠  LLM (same model)",
        "plays BOTH roles: Generate + Reflect"],
       C["llm"], lw=2.5, fs=8)

    # Generate arrow (left down)
    ar(ax, 1.45, 2.22, 1.45, 1.72, "generate", C["llm"])
    bx(ax, 1.45, 1.45, 1.8, 0.48, ["Draft\nResponse"], C["tools"], fs=8)

    # Reflect arrow (right down)
    ar(ax, 3.55, 2.22, 3.55, 1.72, "reflect", C["memory"])
    bx(ax, 3.55, 1.45, 1.8, 0.48, ["Critique\n& Gaps"], C["memory"], fs=8)

    # Decision diamond
    from matplotlib.patches import Polygon
    d_x, d_y, d = 2.5, 0.9, 0.28
    ax.add_patch(Polygon(
        [[d_x, d_y+d], [d_x+d*1.6, d_y], [d_x, d_y-d], [d_x-d*1.6, d_y]],
        facecolor="#F5CBA7", edgecolor=C["tools"], lw=1.8, zorder=3))
    ax.text(d_x, d_y, "satisfied?", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#784212", zorder=4)

    # Arrows into decision
    ar(ax, 1.45, 1.21, 2.05, 0.9, "", C["tools"])
    ar(ax, 3.55, 1.21, 2.95, 0.9, "", C["memory"])

    # YES → Final Answer
    ar(ax, 2.5, 0.62, 2.5, 0.32, "YES", C["agent_yes"])
    ax.text(2.5, 0.17, "✅ Final Answer",
            ha="center", fontsize=8, color=C["agent_yes"], fontweight="bold")

    # NO → loop back to LLM
    ax.annotate("", xy=(0.55, 2.55), xytext=(0.55, 0.9),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_no"], lw=1.6,
                                connectionstyle="arc3,rad=0"), zorder=5)
    ar(ax, 0.55, 2.55, 1.0, 2.55, "NO → revise", C["agent_no"])

    # ══ PANEL 2 — Reflection with External Validation ════════════════════════
    ax = axes[1]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.6); ax.axis("off")
    ax.set_facecolor(C["bg"])

    p2 = FancyBboxPatch((0, 4.25), 5, 0.3,
                        boxstyle="round,pad=0.05",
                        facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p2)
    ax.text(2.5, 4.4, "🤖  AGENT  ✓  —  Variant B: External Validation",
            ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.1, "LLM generates · tool validates · LLM reflects on result",
            ha="center", fontsize=7.5, color="#566573", style="italic")

    bx(ax, 2.5, 3.5, 2.6, 0.5, ["Task / Prompt"], C["input"], fs=8.5)
    ar(ax, 2.5, 3.25, 2.5, 2.9)

    bx(ax, 2.5, 2.62, 3.0, 0.55, ["🧠  LLM", "Generate → Code / Content"], C["llm"], lw=2.5, fs=8)

    ar(ax, 2.5, 2.34, 2.5, 1.88, "output", C["llm"])

    bx(ax, 2.5, 1.6, 2.6, 0.52, ["🔧  External Validator", "run tests · lint · fact-check"], C["tools"], fs=7.5)

    # Validator → LLM (feedback loop)
    ax.annotate("", xy=(0.8, 2.62), xytext=(0.8, 1.6),
                arrowprops=dict(arrowstyle="-|>", color=C["memory"], lw=1.6,
                                connectionstyle="arc3,rad=0"), zorder=5)
    ar(ax, 0.8, 2.62, 1.0, 2.62, "errors / result", C["memory"])

    # Validator → Decision
    ar(ax, 2.5, 1.34, 2.5, 0.98, "", C["tools"])

    # Decision
    ax.add_patch(Polygon(
        [[2.5, 0.9+0.25], [2.5+0.4, 0.9], [2.5, 0.9-0.25], [2.5-0.4, 0.9]],
        facecolor="#F5CBA7", edgecolor=C["tools"], lw=1.8, zorder=3))
    ax.text(2.5, 0.9, "pass?", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#784212", zorder=4)

    ar(ax, 2.5, 0.65, 2.5, 0.32, "YES", C["agent_yes"])
    ax.text(2.5, 0.17, "✅ Validated Output",
            ha="center", fontsize=8, color=C["agent_yes"], fontweight="bold")
    ax.text(4.4, 0.9, "NO →\nreflect\n& fix", ha="center", fontsize=7,
            color=C["agent_no"], fontweight="bold")
    ax.annotate("", xy=(3.5, 1.6), xytext=(2.9, 0.9),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_no"], lw=1.4,
                                connectionstyle="arc3,rad=-0.3"), zorder=5)

    plt.tight_layout(pad=1.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Evolution overview — journey from LLM to Agent
# ══════════════════════════════════════════════════════════════════════════════

def diagram_overview() -> bytes:
    fig = plt.figure(figsize=(11, 7))
    fig.patch.set_facecolor(C["bg"])

    # ── Title ─────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.97,
             "Phase 1 — Building Blocks: The Road from Plain LLM  →  Agent",
             ha="center", fontsize=13, fontweight="bold", color="#1C2833")
    fig.text(0.5, 0.93,
             'Anthropic:  "The basic building block of agentic systems is an LLM '
             'enhanced with retrieval, tools, and memory"',
             ha="center", fontsize=8.5, color="#566573", style="italic")

    # ── 4 panels in a row ─────────────────────────────────────────────────────
    panels = [
        {
            "title":    "1a — Plain LLM",
            "body":     "Input → LLM → Output\n(stateless, one call)",
            "added":    "The bare building block",
            "agent":    False,
            "color":    C["llm"],
        },
        {
            "title":    "1b — + Memory",
            "body":     "Adds: conversation history\n(context-window replay)",
            "added":    "+ Memory Buffer",
            "agent":    False,
            "color":    C["memory"],
        },
        {
            "title":    "1c — + Tools",
            "body":     "Adds: function calling\n(model picks the tool)",
            "added":    "+ Real Tools",
            "agent":    False,
            "color":    C["tools"],
        },
        {
            "title":    "1d — Mini Agent 🤖",
            "body":     "Adds: autonomous loop\n(model drives itself)",
            "added":    "+ Agent Loop  →  AGENT ✓",
            "agent":    True,
            "color":    C["agent_yes"],
        },
    ]

    for i, p in enumerate(panels):
        left = 0.03 + i * 0.245
        ax = fig.add_axes([left, 0.22, 0.22, 0.62])
        ax.set_facecolor(C["bg"])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # Agent status strip at top
        status_color = C["agent_yes"] if p["agent"] else C["agent_no"]
        status_text  = "🤖 AGENT ✓" if p["agent"] else "⚠ Not an Agent"
        strip = FancyBboxPatch((0.0, 0.87), 1.0, 0.13,
                               boxstyle="round,pad=0.02",
                               facecolor=status_color, edgecolor="white",
                               linewidth=1.5, transform=ax.transAxes, zorder=4)
        ax.add_patch(strip)
        ax.text(0.5, 0.935, status_text, ha="center", va="center",
                transform=ax.transAxes, fontsize=8, color="white",
                fontweight="bold", zorder=5)

        # Title
        ax.text(0.5, 0.82, p["title"], ha="center", va="center",
                transform=ax.transAxes, fontsize=9, fontweight="bold",
                color="#1C2833")

        # Main body block
        body_patch = FancyBboxPatch((0.06, 0.40), 0.88, 0.37,
                                    boxstyle="round,pad=0.04",
                                    facecolor=p["color"], edgecolor="white",
                                    linewidth=2, transform=ax.transAxes, zorder=3)
        ax.add_patch(body_patch)
        ax.text(0.5, 0.585, p["body"], ha="center", va="center",
                transform=ax.transAxes, fontsize=8, color="white",
                fontweight="bold", multialignment="center", linespacing=1.5,
                zorder=4)

        # What's new badge
        badge_color = p["color"] if not p["agent"] else C["agent_yes"]
        ax.text(0.5, 0.22, f"✚  {p['added']}", ha="center", va="center",
                transform=ax.transAxes, fontsize=7.5,
                color=badge_color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                          edgecolor=badge_color, linewidth=1.5))

        # Arrow to next panel
        if i < 3:
            fig.text(left + 0.228, 0.535, "→", fontsize=18,
                     color=C["arrow"], fontweight="bold", va="center")

    # ── Bottom definition bar ─────────────────────────────────────────────────
    def_ax = fig.add_axes([0.03, 0.04, 0.94, 0.12])
    def_ax.set_facecolor("#EAF4EC")
    def_ax.axis("off")
    def_patch = FancyBboxPatch((0, 0), 1, 1,
                               boxstyle="round,pad=0.02",
                               facecolor="#EAF4EC", edgecolor=C["agent_yes"],
                               linewidth=1.5, transform=def_ax.transAxes)
    def_ax.add_patch(def_patch)
    def_ax.text(0.5, 0.65,
                "🔑  What makes something an AGENT?",
                ha="center", va="center", fontsize=9,
                color=C["agent_yes"], fontweight="bold",
                transform=def_ax.transAxes)
    def_ax.text(0.5, 0.25,
                'The LLM dynamically directs its OWN next step (call a tool, or stop). '
                ' In 1a–1c YOU control the flow. In 1d the LLM controls the flow → that is Agentic AI.',
                ha="center", va="center", fontsize=8,
                color="#1C2833", transform=def_ax.transAxes,
                multialignment="center")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 3e: Pattern Landscape (all 9 patterns)
# ══════════════════════════════════════════════════════════════════════════════

def diagram_pattern_compare() -> bytes:
    """Pattern Landscape: 9 patterns positioned by Complexity vs Autonomy."""
    from matplotlib.patches import Rectangle as Rect, Circle

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(C["dim"])
    ax.spines["bottom"].set_color(C["dim"])

    # Background zones
    ax.add_patch(Rect((0, 0), 6.5, 10, alpha=0.06, color="#2471A3", zorder=0))
    ax.add_patch(Rect((6.5, 0), 3.5, 10, alpha=0.06, color="#CA6F1E", zorder=0))
    ax.axvline(6.5, color=C["dim"], lw=1.2, linestyle="--", zorder=1)
    ax.text(3.25, 9.6, "Phase 2 — Workflow Patterns", ha="center",
            fontsize=10, color="#2471A3", fontweight="bold")
    ax.text(8.25, 9.6, "Phase 3 — Agent Patterns", ha="center",
            fontsize=10, color="#CA6F1E", fontweight="bold")

    # (name, x, y, color, badge)
    patterns = [
        ("Prompt\nChaining",       1.2, 1.5, "#2471A3", "2a"),
        ("Routing",                2.5, 2.5, "#1A9DB7", "2b"),
        ("Parallelization",        3.8, 1.8, "#117A65", "2c"),
        ("Orchestrator-\nWorkers", 5.6, 4.8, "#1E8449", "2d"),
        ("Evaluator-\nOptimizer",  4.5, 4.0, "#0E6655", "2e"),
        ("Reflection",             5.8, 7.2, "#922B21", "3b"),
        ("ReAct",                  7.2, 6.8, "#CA6F1E", "3a"),
        ("Planning",               8.0, 7.8, "#D35400", "3c"),
        ("Code\nExecution",        9.0, 9.0, "#784212", "3d"),
    ]

    for name, x, y, col, badge in patterns:
        circ = Circle((x, y), 0.58, color=col, alpha=0.88, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y + 0.08, badge, ha="center", va="center",
                fontsize=8, color="white", fontweight="bold", zorder=4)
        ax.text(x, y - 0.82, name, ha="center", va="top",
                fontsize=8, color="#1C2833", zorder=4, multialignment="center")

    ax.set_xlabel("Complexity  →", fontsize=11, color=C["arrow"], fontweight="bold", labelpad=6)
    ax.set_ylabel("Autonomy  →",   fontsize=11, color=C["arrow"], fontweight="bold", labelpad=6)
    ax.set_title("Pattern Landscape — 9 Core Agentic Patterns\nphase 2 workflows → phase 3 agents",
                 fontsize=12, fontweight="bold", color="#1C2833", pad=10)

    # Corner hints
    ax.text(0.2, 0.3, "simple · guided",  fontsize=7.5, color=C["dim"], style="italic")
    ax.text(9.8, 9.7, "complex · autonomous", fontsize=7.5, color="#CA6F1E",
            style="italic", ha="right", va="top", fontweight="bold")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 3c: Planning Agent (Plan-and-Execute)
# ══════════════════════════════════════════════════════════════════════════════

def diagram_planning() -> bytes:
    """Two-panel: ReAct (implicit) vs Plan-and-Execute (explicit plan first)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.patch.set_facecolor(C["bg"])

    def bx(ax, cx, cy, w, h, lines, fc, fs=8, z=3):
        p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                           boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor="white", linewidth=2, zorder=z)
        ax.add_patch(p)
        ax.text(cx, cy, "\n".join(lines), ha="center", va="center",
                fontsize=fs, color="white", fontweight="bold",
                zorder=z+1, multialignment="center", linespacing=1.4)

    def ar(ax, x1, y1, x2, y2, lbl="", color=C["arrow"]):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                    mutation_scale=13), zorder=5)
        if lbl:
            ax.text((x1+x2)/2, (y1+y2)/2+0.1, lbl, ha="center",
                    fontsize=6.5, color=color, style="italic", zorder=6)

    # ── LEFT PANEL: ReAct ────────────────────────────────────────────────────
    ax = axes[0]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off")
    ax.set_facecolor(C["bg"])
    p = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                       facecolor=C["llm"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p)
    ax.text(2.5, 4.6, "Phase 3a — ReAct  (implicit reasoning)",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.25, "Path EMERGES one step at a time — no upfront commitment",
            ha="center", fontsize=7.2, color="#566573", style="italic")

    bx(ax, 2.5, 3.6, 2.2, 0.5, ["Task"], C["input"], fs=9)
    ar(ax, 2.5, 3.35, 2.5, 2.98)

    for (lbl, col), y in zip([("Think", C["llm"]), ("Act (tool)", C["tools"]), ("Observe", C["memory"])],
                              [2.7, 1.95, 1.2]):
        bx(ax, 2.5, y, 2.2, 0.48, [lbl], col, fs=8.5)

    ar(ax, 2.5, 2.46, 2.5, 2.2, "decides", C["tools"])
    ar(ax, 2.5, 1.71, 2.5, 1.46, "new info", C["memory"])
    ax.annotate("", xy=(0.7, 2.7), xytext=(0.7, 1.2),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_no"], lw=1.6,
                                connectionstyle="arc3,rad=0"), zorder=5)
    ar(ax, 0.7, 2.7, 1.4, 2.7, "loop", C["agent_no"])
    ar(ax, 2.5, 0.96, 2.5, 0.62, "done", C["agent_yes"])
    ax.text(2.5, 0.38, "Answer (no written plan — reasoning is hidden)",
            ha="center", fontsize=7, color=C["agent_yes"], fontweight="bold")

    # ── RIGHT PANEL: Plan-and-Execute ────────────────────────────────────────
    ax = axes[1]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off")
    ax.set_facecolor(C["bg"])
    p2 = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                        facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p2)
    ax.text(2.5, 4.6, "Phase 3c — Plan-and-Execute  (explicit plan)",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.25, "Path COMMITTED upfront as a numbered plan — adapts on new results",
            ha="center", fontsize=7.2, color="#566573", style="italic")

    bx(ax, 2.5, 3.6, 2.2, 0.5, ["Task"], C["input"], fs=9)
    ar(ax, 2.5, 3.35, 2.5, 2.95)

    plan_box = FancyBboxPatch((0.4, 2.52), 4.2, 0.68,
                              boxstyle="round,pad=0.1",
                              facecolor=C["loop"], edgecolor="white", lw=2.5, zorder=3)
    ax.add_patch(plan_box)
    ax.text(2.5, 2.86, "PLANNER LLM writes explicit plan", ha="center",
            va="center", fontsize=8.5, color="white", fontweight="bold", zorder=4)
    ax.text(2.5, 2.63, "1. Research  2. Calculate  3. Compare  4. Recommend",
            ha="center", va="center", fontsize=7, color="#FDEBD0", zorder=4)

    ar(ax, 2.5, 2.52, 2.5, 2.2, "execute step by step", C["agent_yes"])

    for ex, el, ec in zip([0.85, 1.8, 2.75, 3.7],
                          ["Step 1\ntool", "Step 2\nLLM", "Step 3\ntool", "Step 4\nLLM"],
                          [C["tools"], C["llm"], C["tools"], C["llm"]]):
        bx(ax, ex, 1.75, 0.82, 0.68, [el], ec, fs=7.5)

    ax.plot([0.44, 4.11], [1.75, 1.75], color=C["dim"], lw=1, ls="--", zorder=1)
    ax.text(2.5, 1.22, "Results from each step feed into the next",
            ha="center", fontsize=7, color=C["tools"], style="italic")

    ar(ax, 2.5, 1.05, 2.5, 0.65, "synthesize", C["agent_yes"])
    ax.text(2.5, 0.38, "Grounded Answer  (plan visible before execution)",
            ha="center", fontsize=7, color=C["agent_yes"], fontweight="bold")

    plt.tight_layout(pad=1.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 3d: Code Execution Tool
# ══════════════════════════════════════════════════════════════════════════════

def diagram_code_exec() -> bytes:
    """Code Execution: agent writes Python, exec() runs it, output feeds back."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Agent decides to write code, reads output, decides next — owns the loop")

    ax.text(W/2, 3.75, "Phase 3d — Code Execution Tool  🐍",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Agent writes Python  ·  sandbox executes  ·  output observed  ·  agent iterates",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    _box(ax, 0.85, 2.8, "Task /\nGoal", C["input"], w=1.2, h=0.5)
    _arrow(ax, 1.45, 2.8, 1.82, 2.8)
    _box(ax, 2.6, 2.8, "Agent LLM\n(reason + write code)", C["llm"], w=1.8, h=0.55)
    _arrow(ax, 3.5, 2.53, 3.5, 2.05, label="Python code", color=C["tools"])

    code_box = FancyBboxPatch((2.1, 1.45), 2.8, 0.56,
                              boxstyle="round,pad=0.1",
                              facecolor=C["tools"], edgecolor="white", linewidth=2.5, zorder=3)
    ax.add_patch(code_box)
    ax.text(3.5, 1.73, "🐍  Python REPL  (exec() sandbox)",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=4)

    _arrow(ax, 3.5, 1.45, 3.5, 1.05, label="stdout / result", color=C["memory"])
    _box(ax, 3.5, 0.78, "Output\n(numbers, data, errors)", C["memory"], w=2.2, h=0.48)

    ax.annotate("", xy=(1.7, 2.53), xytext=(1.7, 0.78),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_yes"], lw=1.8,
                                connectionstyle="arc3,rad=0"), zorder=5)
    _arrow(ax, 1.7, 2.53, 2.0, 2.7, label="observe + decide", color=C["agent_yes"])

    _box(ax, 5.8, 2.15, "Final\nAnswer", C["output"], w=1.3, h=0.52)
    _arrow(ax, 4.5, 2.8, 5.15, 2.8, label="done", color=C["output"])
    _arrow(ax, 5.8, 2.8, 5.8, 2.42, color=C["output"])

    ax.text(W/2, 2.15,
            "run_python() is just another tool in the ReAct toolbox",
            ha="center", fontsize=7.5, color=C["note_ok"], style="italic")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 4d: Evaluation Framework
# ══════════════════════════════════════════════════════════════════════════════

def diagram_evals() -> bytes:
    """Evaluation: golden dataset -> agent -> judge -> metrics -> report."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=False,
                  why="YOUR testing pipeline runs the agent — the agent under test is not in control here")

    ax.text(W/2, 3.75, "Phase 4d — Evaluation Framework  📊",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Golden dataset  ·  agent answers each  ·  Judge scores each  ·  metrics aggregated",
            ha="center", fontsize=8.2, color="#566573", style="italic")

    _box(ax, 0.72, 2.55, "Golden\nDataset\n10 Q+A\npairs", C["input"], w=1.15, h=1.5, fontsize=7.5)

    for y_off, lbl in [(.45, "Q1"), (0.0, "Q5"), (-.45, "Q10")]:
        _arrow(ax, 1.3, 2.55+y_off, 1.65, 2.55+y_off, label=lbl, color=C["dim"])

    _box(ax, 2.3, 2.55, "Agent\nanswers\neach Q", C["llm"], w=1.0, h=1.5, fontsize=7.5)
    _arrow(ax, 2.8, 2.55, 3.15, 2.55, color=C["arrow"])

    _box(ax, 3.8, 2.55, "Judge\n(4c)\nscores\neach", C["memory"], w=1.0, h=1.5, fontsize=7.5)
    _arrow(ax, 4.3, 2.55, 4.65, 2.55, color=C["arrow"])

    _box(ax, 5.4, 3.1,  "Pass rate\n& avg",     C["agent_yes"], w=1.35, h=0.52, fontsize=7.5)
    _box(ax, 5.4, 2.45, "Failures\n& gaps",     C["agent_no"],  w=1.35, h=0.52, fontsize=7.5)
    _box(ax, 5.4, 1.8,  "Regression\ndelta",    C["tools"],     w=1.35, h=0.52, fontsize=7.5)

    ax.text(W/2, 1.22,
            "Golden dataset = the contract your agent must honour on every code change",
            ha="center", fontsize=7.8, color=C["note_ok"], style="italic")

    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 5b: Long-term Memory
# ══════════════════════════════════════════════════════════════════════════════

def diagram_long_memory() -> bytes:
    """Context-window (ephemeral) vs vector store (persistent across sessions)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.patch.set_facecolor(C["bg"])

    def bx(ax, cx, cy, w, h, txt, fc, fs=8, z=3):
        p = FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor="white", linewidth=2, zorder=z)
        ax.add_patch(p)
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=fs,
                color="white", fontweight="bold", zorder=z+1, multialignment="center", linespacing=1.4)

    def ar(ax, x1, y1, x2, y2, lbl="", color=C["arrow"]):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, mutation_scale=13), zorder=5)
        if lbl:
            ax.text((x1+x2)/2, (y1+y2)/2+0.1, lbl, ha="center",
                    fontsize=6.5, color=color, style="italic", zorder=6)

    for idx, ax in enumerate(axes):
        ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off"); ax.set_facecolor(C["bg"])

    # LEFT: ephemeral
    ax = axes[0]
    FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                   facecolor=C["agent_no"], edgecolor="white", lw=1.5, zorder=4)
    p = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                       facecolor=C["agent_no"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p)
    ax.text(2.5, 4.6, "Phase 1b  Context Window  (ephemeral)",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.22, "Lives only for the current session -- gone when it ends",
            ha="center", fontsize=7.2, color="#566573", style="italic")
    for i, lbl in enumerate(["Session 1", "Session 2"]):
        y = 3.55 - i * 1.65
        bx(ax, 2.5, y, 3.2, 0.48, f"{lbl}: messages", C["input"] if i == 0 else C["llm"], fs=8)
        ar(ax, 2.5, y-0.24, 2.5, y-0.62)
        bx(ax, 2.5, y-0.88, 3.2, 0.48, "LLM responds", C["llm"], fs=8)
        ax.text(2.5, y-1.22, "GONE -- session ended", ha="center",
                fontsize=7, color=C["agent_no"], fontweight="bold")
    ax.text(2.5, 0.32, "Every conversation starts fresh -- no cross-session learning",
            ha="center", fontsize=7, color=C["agent_no"], style="italic")

    # RIGHT: persistent
    ax = axes[1]
    p2 = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                        facecolor=C["agent_yes"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p2)
    ax.text(2.5, 4.6, "Phase 5b  Vector Store  (persistent)",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.22, "Memories survive sessions -- semantically searchable",
            ha="center", fontsize=7.2, color="#566573", style="italic")
    bx(ax, 1.4, 3.65, 2.1, 0.46, "New fact or interaction", C["input"], fs=7.5)
    ar(ax, 1.4, 3.42, 1.4, 3.08, "embed", C["memory"])
    bx(ax, 1.4, 2.82, 2.1, 0.46, "3072-dim vector", C["memory"], fs=7.5)
    ar(ax, 1.4, 2.59, 1.4, 2.26, "store", C["memory"])
    vs = FancyBboxPatch((0.3, 1.65), 4.4, 0.56, boxstyle="round,pad=0.1",
                        facecolor=C["tools"], edgecolor="white", lw=2.5, zorder=3)
    ax.add_patch(vs)
    ax.text(2.5, 1.93, "Vector Store  (ChromaDB / in-memory)",
            ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=4)
    bx(ax, 3.6, 3.65, 2.1, 0.46, "New query", C["input"], fs=7.5)
    ar(ax, 3.6, 3.42, 3.6, 3.08, "embed query", C["memory"])
    bx(ax, 3.6, 2.82, 2.1, 0.46, "query vector", C["memory"], fs=7.5)
    ar(ax, 3.6, 2.59, 3.6, 2.26, "cosine search", C["memory"])
    ar(ax, 3.6, 1.65, 3.6, 1.28, "top-K recalled", C["agent_yes"])
    bx(ax, 3.6, 1.02, 2.1, 0.46, "Relevant memories\ninjected into prompt", C["agent_yes"], fs=7.5)
    ax.text(2.5, 0.32, "Agent remembers customers and preferences across sessions",
            ha="center", fontsize=6.8, color=C["agent_yes"], style="italic")

    plt.tight_layout(pad=1.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0); plt.close(fig); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 6a: Multi-Agent
# ══════════════════════════════════════════════════════════════════════════════

def diagram_multi_agent() -> bytes:
    """Root orchestrator + 4 specialist sub-agents."""
    fig, ax = _fig()
    _agent_banner(ax, is_agent=True,
                  why="Root decides who delegates to whom -- sub-agents make their own tool decisions")
    ax.text(W/2, 3.75, "Phase 6a -- Multi-Agent  (Root + Sub-Agents)",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Root orchestrator routes to specialist sub-agents, each with own tools and reasoning",
            ha="center", fontsize=8.2, color="#566573", style="italic")
    _box(ax, 3.5, 3.1, "User Query", C["input"], w=1.6, h=0.44)
    _arrow(ax, 3.5, 2.88, 3.5, 2.7)
    root = FancyBboxPatch((1.85, 2.26), 3.3, 0.44, boxstyle="round,pad=0.1",
                          facecolor=C["loop"], edgecolor="white", linewidth=2.5, zorder=3)
    ax.add_patch(root)
    ax.text(3.5, 2.48, "ROOT AGENT  --  decides who handles this",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=4)
    sub_xs   = [0.65, 2.15, 3.65, 5.35]
    sub_lbls = ["Banking\nSpecialist", "Fraud\nSpecialist", "International\nSpecialist", "Complaints\nSpecialist"]
    sub_tools = ["rates\naccounts", "detection\nreporting", "SWIFT\ncountry", "escalation\nombudsman"]
    sub_cols  = [C["llm"], C["agent_no"], C["tools"], C["memory"]]
    for sx, sl, st2, sc in zip(sub_xs, sub_lbls, sub_tools, sub_cols):
        _arrow(ax, 3.5, 2.26, sx, 1.88, color=C["dim"])
        _box(ax, sx, 1.62, sl, sc, w=1.1, h=0.5, fontsize=7.5)
        ax.text(sx, 1.22, st2, ha="center", fontsize=6.5, color=sc,
                style="italic", multialignment="center")
    ax.text(W/2, 1.78, "each sub-agent: own system prompt, own tools, own reasoning loop",
            ha="center", fontsize=7.2, color=C["loop"], style="italic")
    for sx in sub_xs:
        _arrow(ax, sx, 0.97, 3.5, 0.72, color=C["dim"])
    _box(ax, 3.5, 0.52, "Synthesized Answer", C["output"], w=2.2, h=0.36)
    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 6b: MCP Protocol
# ══════════════════════════════════════════════════════════════════════════════

def diagram_mcp() -> bytes:
    """MCP client-server: agent discovers and calls tools via protocol."""
    fig, ax = _fig()
    _agent_banner(ax, is_agent=True,
                  why="Agent discovers tools dynamically from any MCP server -- not hardcoded")
    ax.text(W/2, 3.75, "Phase 6b -- MCP: Model Context Protocol  (Anthropic, Nov 2024)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Standard for agent-to-tool connections  |  discover tools at runtime  |  swappable servers",
            ha="center", fontsize=8.2, color="#566573", style="italic")
    # Client
    cb = FancyBboxPatch((0.1, 0.95), 2.6, 2.35, boxstyle="round,pad=0.1",
                        facecolor="#EAF4EC", edgecolor=C["agent_yes"], linewidth=2, zorder=1)
    ax.add_patch(cb)
    ax.text(1.4, 3.22, "MCP CLIENT (Agent)", ha="center", fontsize=8,
            color=C["agent_yes"], fontweight="bold")
    _box(ax, 1.4, 2.65, "LLM\n(Gemini 2.5 Flash)", C["llm"], w=2.0, h=0.5, fontsize=7.5)
    _box(ax, 1.4, 1.82, "MCP Client Layer\n(tool discovery)", C["agent_yes"], w=2.0, h=0.5, fontsize=7.5)
    _arrow(ax, 1.4, 2.4, 1.4, 2.08, color=C["agent_yes"])
    # Server
    sb = FancyBboxPatch((4.3, 0.95), 2.6, 2.35, boxstyle="round,pad=0.1",
                        facecolor="#FEF9E7", edgecolor=C["tools"], linewidth=2, zorder=1)
    ax.add_patch(sb)
    ax.text(5.6, 3.22, "MCP SERVER (Tool Provider)", ha="center", fontsize=8,
            color=C["tools"], fontweight="bold")
    _box(ax, 5.6, 2.65, "Tool Registry\npolicy, fees, accounts", C["tools"], w=2.0, h=0.5, fontsize=7.5)
    _box(ax, 5.6, 1.82, "Resources\n(docs, prompts)", C["memory"], w=2.0, h=0.5, fontsize=7.5)
    # Protocol messages
    _arrow(ax, 2.7, 2.15, 4.3, 2.15, label="1. initialize + list_tools()", color=C["agent_yes"])
    _arrow(ax, 4.3, 1.95, 2.7, 1.95, label="   tools schema returned", color=C["tools"])
    _arrow(ax, 2.7, 1.72, 4.3, 1.72, label="2. call_tool(name, args)", color=C["tools"])
    _arrow(ax, 4.3, 1.52, 2.7, 1.52, label="   result JSON", color=C["memory"])
    ax.text(W/2, 0.68,
            "Same agent works with ANY MCP server -- swap servers without changing agent code",
            ha="center", fontsize=7.5, color=C["note_ok"], style="italic")
    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 6c: A2A Protocol
# ══════════════════════════════════════════════════════════════════════════════

def diagram_a2a() -> bytes:
    """A2A: agent discovers remote agent via Agent Card, submits task."""
    fig, ax = _fig()
    _agent_banner(ax, is_agent=True,
                  why="Both sides are full agents -- neither controls the other, they communicate as peers")
    ax.text(W/2, 3.75, "Phase 6c -- A2A: Agent-to-Agent Protocol  (Google, Apr 2025)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Standard for agent-to-agent delegation  |  Agent Card discovery  |  Task lifecycle",
            ha="center", fontsize=8.2, color="#566573", style="italic")
    _box(ax, 1.1, 2.55, "Calling Agent\n(Orchestrator)", C["llm"], w=1.8, h=0.88, fontsize=8)
    card = FancyBboxPatch((2.9, 2.82), 1.5, 0.56, boxstyle="round,pad=0.08",
                          facecolor="#FEF9E7", edgecolor=C["tools"], linewidth=1.8, zorder=3)
    ax.add_patch(card)
    ax.text(3.65, 3.1, "Agent Card\n(discovery JSON)", ha="center", va="center",
            fontsize=7.5, color=C["tools"], fontweight="bold", zorder=4)
    _box(ax, 5.9, 2.55, "Remote Agent\n(Fraud Specialist)", C["agent_yes"], w=1.8, h=0.88, fontsize=8)
    _arrow(ax, 2.0, 2.82, 2.9, 3.0, label="1. GET /.well-known/agent.json", color=C["tools"])
    _arrow(ax, 2.9, 2.88, 2.0, 2.7, label="Agent Card returned", color=C["tools"])
    _arrow(ax, 2.0, 2.35, 4.95, 2.35, label="2. POST /tasks/send  {task payload}", color=C["loop"])
    _arrow(ax, 4.95, 2.15, 2.0, 2.15, label="   {id, status: submitted}", color=C["memory"])
    _arrow(ax, 2.0, 1.92, 4.95, 1.92, label="3. GET /tasks/{id}  (poll or stream)", color=C["loop"])
    _arrow(ax, 4.95, 1.72, 2.0, 1.72, label="   {status: completed, result}", color=C["agent_yes"])
    ax.text(W/2, 1.28,
            "MCP = agent talks to a TOOL SERVER  |  A2A = agent talks to another AGENT",
            ha="center", fontsize=7.8, color=C["note_ok"], style="italic", fontweight="bold")
    ax.text(W/2, 1.08,
            "The remote agent has its own reasoning, tools, and memory -- it is not just a function",
            ha="center", fontsize=7.2, color="#566573", style="italic")
    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 6d: Agent Communications Comparison
# ══════════════════════════════════════════════════════════════════════════════

def diagram_agent_comms() -> bytes:
    """Three communication patterns side by side."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    fig.patch.set_facecolor(C["bg"])
    panels = [
        {
            "title": "Raw Delegation (6a)",
            "sub": "Direct Python call\nto sub-agent function",
            "color": C["llm"],
            "steps": [
                ("Agent decides to delegate", C["llm"]),
                ("sub_agent_fn(query) called", C["tools"]),
                ("sub-agent runs + returns", C["llm"]),
                ("root synthesizes result", C["agent_yes"]),
            ],
            "note": "Fast. No overhead.\nSame codebase, trusted agents.",
        },
        {
            "title": "MCP Protocol (6b)",
            "sub": "Discover tools from server\nat runtime via standard",
            "color": C["tools"],
            "steps": [
                ("initialize + list_tools()", C["tools"]),
                ("LLM picks from tool list", C["llm"]),
                ("call_tool(name, args)", C["tools"]),
                ("result as JSON schema", C["agent_yes"]),
            ],
            "note": "Standardised. Swappable servers.\nAgent-to-tool connections.",
        },
        {
            "title": "A2A Protocol (6c)",
            "sub": "Discover remote agent\nvia Agent Card, send task",
            "color": C["agent_yes"],
            "steps": [
                ("GET agent.json (card)", C["agent_yes"]),
                ("POST /tasks/send", C["loop"]),
                ("poll or stream status", C["memory"]),
                ("result + full provenance", C["agent_yes"]),
            ],
            "note": "Cross-org standard. Streaming.\nAgent-to-agent delegation.",
        },
    ]
    for ax, panel in zip(axes, panels):
        ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off"); ax.set_facecolor(C["bg"])
        hdr = FancyBboxPatch((0, 4.4), 5, 0.36, boxstyle="round,pad=0.05",
                             facecolor=panel["color"], edgecolor="white", lw=1.5, zorder=4)
        ax.add_patch(hdr)
        ax.text(2.5, 4.6, panel["title"], ha="center", va="center",
                fontsize=9, color="white", fontweight="bold", zorder=5)
        ax.text(2.5, 4.2, panel["sub"], ha="center", fontsize=7,
                color="#566573", style="italic", multialignment="center")
        for j, ((sl, sc), y) in enumerate(zip(panel["steps"], [3.52, 2.82, 2.12, 1.42])):
            sp = FancyBboxPatch((0.4, y-0.22), 4.2, 0.44, boxstyle="round,pad=0.06",
                               facecolor=sc, edgecolor="white", lw=1.5, zorder=3)
            ax.add_patch(sp)
            ax.text(2.5, y, sl, ha="center", va="center", fontsize=7.5,
                    color="white", fontweight="bold", zorder=4, multialignment="center")
            if j < 3:
                ax.annotate("", xy=(2.5, y-0.57), xytext=(2.5, y-0.22),
                            arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.2), zorder=5)
        nb = FancyBboxPatch((0.2, 0.38), 4.6, 0.65, boxstyle="round,pad=0.08",
                            facecolor="#F8F9FA", edgecolor=panel["color"], linewidth=1.5, zorder=2)
        ax.add_patch(nb)
        ax.text(2.5, 0.7, panel["note"], ha="center", va="center", fontsize=6.8,
                color="#1C2833", multialignment="center", zorder=3)
    plt.tight_layout(pad=1.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0); plt.close(fig); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 7a: Observability & Tracing
# ══════════════════════════════════════════════════════════════════════════════

def diagram_observability() -> bytes:
    """Agent with trace collector layer, metrics flowing to dashboard."""
    fig, ax = _fig()
    _agent_banner(ax, is_agent=True,
                  why="Agent still decides everything -- tracer is a passive observer, not a controller")
    ax.text(W/2, 3.75, "Phase 7a -- Observability & Tracing",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5,
            "Wrap every LLM call -- capture latency, tokens, cost, tool calls, decisions",
            ha="center", fontsize=8.2, color="#566573", style="italic")
    _box(ax, 0.72, 2.55, "User\nQuery", C["input"], w=1.05, h=0.5)
    _arrow(ax, 1.25, 2.55, 1.62, 2.55)
    agent_box = FancyBboxPatch((1.65, 2.1), 3.4, 0.9, boxstyle="round,pad=0.1",
                               facecolor="#EAF4EC", edgecolor=C["agent_yes"], linewidth=2, zorder=2)
    ax.add_patch(agent_box)
    ax.text(3.35, 2.88, "Agent  (ReAct loop)", ha="center", fontsize=8,
            color=C["agent_yes"], fontweight="bold")
    _box(ax, 2.38, 2.38, "Think", C["llm"],    w=0.98, h=0.44, fontsize=8)
    _box(ax, 3.35, 2.38, "Act",   C["tools"],  w=0.88, h=0.44, fontsize=8)
    _box(ax, 4.22, 2.38, "Obs",   C["memory"], w=0.88, h=0.44, fontsize=8)
    _arrow(ax, 5.05, 2.55, 5.42, 2.55, label="response")
    _box(ax, 5.85, 2.55, "Answer", C["output"], w=1.0, h=0.5)
    tracer = FancyBboxPatch((1.48, 1.48), 3.75, 0.5, boxstyle="round,pad=0.08",
                            facecolor="#FEF9E7", edgecolor=C["tools"], linewidth=2,
                            linestyle="--", zorder=3)
    ax.add_patch(tracer)
    ax.text(3.35, 1.73, "TRACE COLLECTOR  --  latency | tokens | cost | tool calls",
            ha="center", va="center", fontsize=7.8, color=C["tools"], fontweight="bold", zorder=4)
    _arrow(ax, 3.35, 2.1, 3.35, 1.98, color=C["tools"])
    _arrow(ax, 3.35, 1.48, 3.35, 1.15, color=C["tools"])
    _box(ax, 3.35, 0.9, "Trace Store\n(structured logs)", C["tools"], w=2.2, h=0.42, fontsize=7.5)
    _arrow(ax, 4.46, 0.9, 5.1, 0.9, color=C["memory"])
    _box(ax, 5.65, 0.9, "Dashboard\n& Alerts", C["memory"], w=1.2, h=0.42, fontsize=7.5)
    ax.text(W/2, 1.3, "Tracer is a passive wrapper -- agent behaviour is unchanged, every call is now logged",
            ha="center", fontsize=7.2, color=C["note_ok"], style="italic")
    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 7b: Cost & Latency
# ══════════════════════════════════════════════════════════════════════════════

def diagram_cost_latency() -> bytes:
    """Cost breakdown + caching + latency components."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.patch.set_facecolor(C["bg"])

    def bx(ax, cx, cy, w, h, txt, fc, fs=8, z=3):
        p = FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor="white", linewidth=2, zorder=z)
        ax.add_patch(p)
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=fs,
                color="white", fontweight="bold", zorder=z+1, multialignment="center", linespacing=1.4)

    ax = axes[0]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off"); ax.set_facecolor(C["bg"])
    FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                   facecolor=C["loop"], edgecolor="white", lw=1.5, zorder=4)
    p0 = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                        facecolor=C["loop"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p0)
    ax.text(2.5, 4.6, "Cost = Input Tokens + Output Tokens",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    ax.text(2.5, 4.2, "Optimise both -- input tokens dominate in most agentic calls",
            ha="center", fontsize=7.2, color="#566573", style="italic")
    bx(ax, 1.4, 3.55, 2.2, 0.58, "INPUT\nSystem prompt + history", C["input"], fs=7.5)
    bx(ax, 3.7, 3.55, 1.3, 0.58, "OUTPUT\nResponse", C["output"], fs=7.5)
    ax.text(2.5, 3.08, "System prompt repeats on EVERY call -- biggest saving target",
            ha="center", fontsize=7, color=C["note_ok"], style="italic")
    cb = FancyBboxPatch((0.3, 2.45), 4.4, 0.48, boxstyle="round,pad=0.08",
                        facecolor=C["agent_yes"], edgecolor="white", lw=2, zorder=3)
    ax.add_patch(cb)
    ax.text(2.5, 2.69, "Prompt Caching -- system prompt charged ONCE, reused for free",
            ha="center", va="center", fontsize=7.8, color="white", fontweight="bold", zorder=4)
    bx(ax, 1.5, 1.9, 2.4, 0.62, "Without cache:\nFull prompt every call", C["agent_no"], fs=7.5)
    bx(ax, 3.7, 1.9, 1.8, 0.62, "With cache:\n60-80% saving", C["agent_yes"], fs=7.5)
    bx(ax, 1.1, 0.9, 1.7, 0.5, "Flash-Lite\nLowest cost", "#5D6D7E", fs=7.5)
    bx(ax, 2.5, 0.9, 1.7, 0.5, "Flash\nBest value", C["tools"], fs=7.5)
    bx(ax, 3.9, 0.9, 1.7, 0.5, "Pro\nHighest quality", C["loop"], fs=7.5)
    ax.text(2.5, 0.44, "Match model to task complexity", ha="center", fontsize=7,
            color="#566573", style="italic")

    ax = axes[1]
    ax.set_xlim(0, 5); ax.set_ylim(0, 4.8); ax.axis("off"); ax.set_facecolor(C["bg"])
    p1 = FancyBboxPatch((0, 4.45), 5, 0.3, boxstyle="round,pad=0.05",
                        facecolor=C["memory"], edgecolor="white", lw=1.5, zorder=4)
    ax.add_patch(p1)
    ax.text(2.5, 4.6, "Latency = Network + TTFT + Generation",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    components = [
        ("Network round-trip",    "~50-200ms",          C["dim"]),
        ("Time to First Token",   "~200-800ms (TTFT)",  C["input"]),
        ("Token generation",      "~20-100ms/token",    C["llm"]),
        ("Tool execution",        "~100ms-2s/tool",     C["tools"]),
        ("Agent loop overhead",   "Multiplied per step",C["loop"]),
    ]
    for i, (label, timing, col) in enumerate(components):
        y = 3.62 - i * 0.6
        sp = FancyBboxPatch((0.3, y-0.22), 4.4, 0.44, boxstyle="round,pad=0.06",
                            facecolor=col, edgecolor="white", lw=1.5, zorder=3)
        ax.add_patch(sp)
        ax.text(2.5, y, f"{label}  [{timing}]", ha="center", va="center",
                fontsize=7.5, color="white", fontweight="bold", zorder=4, multialignment="center")

    ax.text(2.5, 0.65, "Streaming: user sees first token faster even if total time same",
            ha="center", fontsize=7, color=C["note_ok"], style="italic")
    ax.text(2.5, 0.42, "Parallelise sub-agents (Phase 6a) to reduce wall-clock time",
            ha="center", fontsize=7, color=C["note_ok"], style="italic")

    plt.tight_layout(pad=1.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0); plt.close(fig); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 7c: Error Analysis
# ══════════════════════════════════════════════════════════════════════════════

def diagram_error_analysis() -> bytes:
    """5-type failure taxonomy with detection and fix layers."""
    fig, ax = _fig()
    _agent_banner(ax, is_agent=False,
                  why="Error analysis runs on traces -- the agent under review is not active here")
    ax.text(W/2, 3.75, "Phase 7c -- Error Analysis & Debugging",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(W/2, 3.5, "5-type taxonomy  |  detect from traces  |  fix playbook per type",
            ha="center", fontsize=8.2, color="#566573", style="italic")
    failures = [
        ("Hallucination",      "Invents facts\nnot in context",   C["agent_no"]),
        ("Tool Loop",          "Same tool\nrepeatedly",           C["loop"]),
        ("Context Overflow",   "Conversation\ntoo long",          C["memory"]),
        ("Prompt Injection",   "User hijacks\nsystem prompt",     "#8B0000"),
        ("Logic Error",        "Misinterprets\ntool result",      C["input"]),
    ]
    xs = [0.6, 1.72, 3.5, 5.28, 6.4]
    for (label, desc, col), x in zip(failures, xs):
        _box(ax, x, 2.42, label, col, w=1.02, h=0.62, fontsize=7.5)
        ax.text(x, 1.95, desc, ha="center", fontsize=6.5, color=col,
                style="italic", multialignment="center")
    ax.text(W/2, 2.78, "FAILURE TAXONOMY", ha="center", fontsize=7.5,
            color="#5D6D7E", fontweight="bold")
    det = FancyBboxPatch((0.2, 1.42), 6.6, 0.38, boxstyle="round,pad=0.06",
                         facecolor=C["tools"], edgecolor="white", lw=2, zorder=3)
    ax.add_patch(det)
    ax.text(3.5, 1.61, "Detect via: trace logs  |  LLM-as-Judge (4c)  |  eval suite regressions (4d)",
            ha="center", va="center", fontsize=7.8, color="white", fontweight="bold", zorder=4)
    fix = FancyBboxPatch((0.2, 0.92), 6.6, 0.42, boxstyle="round,pad=0.06",
                         facecolor=C["agent_yes"], edgecolor="white", lw=2, zorder=3)
    ax.add_patch(fix)
    ax.text(3.5, 1.13, "Fix: RAG grounding  |  max_steps guard  |  summarisation  |  guardrails  |  prompt redesign",
            ha="center", va="center", fontsize=7.5, color="white", fontweight="bold", zorder=4)
    ax.text(W/2, 0.65, "Each failure maps to a known fix -- diagnose from trace, apply fix, re-run eval suite",
            ha="center", fontsize=7.2, color=C["note_ok"], style="italic")
    _journey_bar(ax, current="Ph3", y=0.97)
    _agent_def_footer(ax)
    return _to_bytes(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 8a: Customer Support Agent (full pipeline)
# ══════════════════════════════════════════════════════════════════════════════

def diagram_customer_support() -> bytes:
    """Full NexaBank support pipeline — all components from Phases 3-7."""
    fig, ax = plt.subplots(figsize=(14, 5.2))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5.2)
    ax.axis("off"); ax.set_facecolor(C["bg"])
    fig.patch.set_facecolor(C["bg"])

    ax.text(7.0, 4.95, "Phase 8a -- NexaBank Customer Support Agent  (all Phases 3-7 combined)",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(7.0, 4.68, "Input Guardrails  ->  Memory Recall  ->  RAG  ->  Agent  ->  Judge  ->  HITL?  ->  Output Guardrails  ->  Delivered",
            ha="center", fontsize=8, color="#566573", style="italic")

    # Pipeline components
    STEPS = [
        (0.7,  "User\nMessage",        C["input"],     ""),
        (2.0,  "Input\nGuardrails",    C["agent_no"],  "4a"),
        (3.4,  "Memory\nRecall",       C["memory"],    "5b"),
        (4.8,  "RAG\nLookup",          C["tools"],     "5a"),
        (6.2,  "Agent\n(ReAct+Tools)", C["llm"],       "3a"),
        (7.6,  "LLM\nas-Judge",        C["memory"],    "4c"),
        (9.0,  "HITL\nif REVIEW",      C["loop"],      "4b"),
        (10.4, "Output\nGuardrail",    C["agent_no"],  "4a"),
        (11.8, "Trace\nLog",           C["tools"],     "7a"),
        (13.2, "Delivered\n✓",         C["agent_yes"], ""),
    ]

    for i, (x, lbl, col, phase) in enumerate(STEPS):
        p = FancyBboxPatch((x-0.58, 2.65), 1.16, 0.8, boxstyle="round,pad=0.08",
                           facecolor=col, edgecolor="white", linewidth=2, zorder=3)
        ax.add_patch(p)
        ax.text(x, 3.05, lbl, ha="center", va="center", fontsize=7,
                color="white", fontweight="bold", zorder=4, multialignment="center", linespacing=1.4)
        if phase:
            pb = FancyBboxPatch((x-0.3, 2.52), 0.6, 0.22, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=col, linewidth=1.2, zorder=5)
            ax.add_patch(pb)
            ax.text(x, 2.63, phase, ha="center", va="center", fontsize=6.5,
                    color=col, fontweight="bold", zorder=6)
        if i < len(STEPS) - 1:
            ax.annotate("", xy=(STEPS[i+1][0]-0.58, 3.05), xytext=(x+0.58, 3.05),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.4), zorder=5)

    # Block path from input guardrails
    ax.annotate("", xy=(2.0, 2.35), xytext=(2.0, 2.65),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_no"], lw=1.4), zorder=5)
    ax.text(2.0, 2.2, "BLOCK", ha="center", fontsize=7, color=C["agent_no"], fontweight="bold")

    # HITL paths
    ax.text(9.0, 2.2, "Approve /\nModify / Reject", ha="center", fontsize=6.5,
            color=C["loop"], multialignment="center")
    ax.annotate("", xy=(9.0, 2.35), xytext=(9.0, 2.65),
                arrowprops=dict(arrowstyle="-|>", color=C["loop"], lw=1.2), zorder=5)

    # What each step contributes (below pipeline)
    notes = [
        (2.0,  "PII · injection\nblocking"),
        (3.4,  "Past interactions\ncustomer context"),
        (4.8,  "Policy docs\ngrounding"),
        (6.2,  "Answer with\nreal tools"),
        (7.6,  "PASS/REVIEW\n/FAIL gate"),
        (9.0,  "Human decides\nhigh-risk cases"),
        (10.4, "Output safety\ncheck"),
        (11.8, "Latency · tokens\ncost logged"),
    ]
    for x, note in notes:
        ax.text(x, 1.9, note, ha="center", fontsize=6, color="#566573",
                style="italic", multialignment="center", linespacing=1.4)

    ax.text(7.0, 1.28, "Every component is a phase you already know -- 8a is the integration, not new concepts",
            ha="center", fontsize=7.5, color=C["note_ok"], style="italic", fontweight="bold")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0); plt.close(fig); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram — Phase 8a.1: Elite Multi-Agent System
# ══════════════════════════════════════════════════════════════════════════════

def diagram_elite_agent() -> bytes:
    """Full architecture: pipeline + 4 A2A specialists + 2 MCP servers + all patterns."""
    fig, ax = plt.subplots(figsize=(14, 7.0))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7.0)
    ax.axis("off"); ax.set_facecolor(C["bg"])
    fig.patch.set_facecolor(C["bg"])

    ax.text(7.0, 6.78, "Phase 8a.1  --  NexaBank Elite Multi-Agent System  (all patterns active)",
            ha="center", fontsize=12, fontweight="bold", color="#1C2833")
    ax.text(7.0, 6.52,
            "4a Guardrails  |  5b Memory  |  3c Planning  |  6a Root  |  6c A2A  |  6b MCP  |"
            "  3b Reflect  |  3d Code  |  5a RAG  |  4c Judge  |  4b HITL  |  7a Trace",
            ha="center", fontsize=7.5, color="#566573", style="italic")

    # ── PIPELINE ROW ─────────────────────────────────────────────────────────
    PIPE = [
        (0.55,  "Guard\n4a",   C["agent_no"]),
        (1.55,  "Memory\n5b",  C["memory"]),
        (2.55,  "Plan\n3c",    C["loop"]),
        (3.85,  "ROOT\n6a",    C["llm"]),
        (9.55,  "Judge\n4c",   C["memory"]),
        (10.7,  "HITL\n4b",   C["loop"]),
        (11.85, "Guard\n4a",   C["agent_no"]),
        (13.0,  "Trace\n7a",   C["tools"]),
    ]
    for x, lbl, col in PIPE:
        p = FancyBboxPatch((x-0.48, 5.55), 0.96, 0.72, boxstyle="round,pad=0.07",
                           facecolor=col, edgecolor="white", linewidth=1.8, zorder=3)
        ax.add_patch(p)
        ax.text(x, 5.91, lbl, ha="center", va="center", fontsize=7,
                color="white", fontweight="bold", zorder=4, multialignment="center", linespacing=1.3)
        if x < 3.2:
            ax.annotate("", xy=(x+0.65, 5.91), xytext=(x+0.48, 5.91),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.2), zorder=5)
    # ROOT -> specialists arrow down
    ax.annotate("", xy=(3.85, 5.2), xytext=(3.85, 5.55),
                arrowprops=dict(arrowstyle="-|>", color=C["llm"], lw=1.5), zorder=5)
    # specialists -> judge arrow up
    ax.annotate("", xy=(9.55, 5.55), xytext=(9.55, 5.2),
                arrowprops=dict(arrowstyle="-|>", color=C["memory"], lw=1.5), zorder=5)
    for x in [9.55, 10.7, 11.85, 13.0]:
        if x < 13.0:
            ax.annotate("", xy=(x+0.63, 5.91), xytext=(x+0.48, 5.91),
                        arrowprops=dict(arrowstyle="-|>", color=C["arrow"], lw=1.2), zorder=5)
    # Dotted line ROOT to judge area
    ax.plot([4.33, 9.07], [5.91, 5.91], color=C["dim"], lw=1.2, ls=(0,(4,3)), zorder=2)
    ax.text(6.7, 6.08, "A2A delegation", ha="center", fontsize=6.5, color=C["dim"], style="italic")

    # ── 4 SPECIALIST BOXES ───────────────────────────────────────────────────
    SPECS = [
        (1.55,  "Banking\nSpecialist", C["llm"],
         ["MCP: Rates Server", "run_python() 3d", "Reflection 3b"]),
        (4.55,  "Fraud\nSpecialist",   C["agent_no"],
         ["MCP: Policy Server", "get_weather()", "RAG 5a"]),
        (7.55,  "International\nSpecialist", C["tools"],
         ["MCP: Fee Server", "get_country_info()", "get_public_holidays()"]),
        (10.55, "Complaints\nSpecialist",    C["memory"],
         ["MCP: Policy Server", "RAG 5a", "Reflection 3b"]),
    ]
    for x, lbl, col, tools in SPECS:
        # Agent Card badge (A2A)
        cb = FancyBboxPatch((x-1.1, 4.72), 2.2, 0.26, boxstyle="round,pad=0.04",
                            facecolor=col, edgecolor="white", lw=1.5, alpha=0.25, zorder=2)
        ax.add_patch(cb)
        ax.text(x, 4.85, "A2A Agent Card", ha="center", va="center", fontsize=6.2,
                color=col, fontweight="bold", zorder=3)

        sb = FancyBboxPatch((x-1.1, 3.85), 2.2, 0.85, boxstyle="round,pad=0.08",
                            facecolor=col, edgecolor="white", lw=2.0, zorder=3)
        ax.add_patch(sb)
        ax.text(x, 4.28, lbl, ha="center", va="center", fontsize=8,
                color="white", fontweight="bold", zorder=4, multialignment="center", linespacing=1.4)

        # tools below
        for j, t in enumerate(tools):
            ty = 3.58 - j * 0.38
            tb = FancyBboxPatch((x-1.05, ty-0.15), 2.1, 0.30, boxstyle="round,pad=0.04",
                                facecolor="#F0F4F8", edgecolor=col, lw=1.2, zorder=3)
            ax.add_patch(tb)
            ax.text(x, ty, t, ha="center", va="center", fontsize=6.2,
                    color=col, fontweight="bold", zorder=4)

        # arrow from root to specialist
        ax.annotate("", xy=(x, 4.7), xytext=(3.85, 5.55) if x < 6 else (9.55, 5.55),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2,
                                    connectionstyle="arc3,rad=0"), zorder=5)

    # ── MCP SERVER BOXES ─────────────────────────────────────────────────────
    mcp1 = FancyBboxPatch((0.3, 1.08), 4.5, 0.72, boxstyle="round,pad=0.08",
                          facecolor="#FEF9E7", edgecolor=C["tools"], lw=2, linestyle="--", zorder=2)
    ax.add_patch(mcp1)
    ax.text(2.55, 1.72, "MCP Policy Server  (NexaBank KB -- 10 docs, free, in-process)",
            ha="center", va="center", fontsize=7.5, color=C["tools"], fontweight="bold", zorder=3)
    ax.text(2.55, 1.28, "search_policies(query)  |  get_policy(doc_id)  -- cosine search over embedded KB",
            ha="center", va="center", fontsize=6.5, color="#566573", zorder=3)

    mcp2 = FancyBboxPatch((5.1, 1.08), 4.5, 0.72, boxstyle="round,pad=0.08",
                          facecolor="#FEF9E7", edgecolor=C["loop"], lw=2, linestyle="--", zorder=2)
    ax.add_patch(mcp2)
    ax.text(7.35, 1.72, "MCP Data Server  (NexaBank rates + fees, hardcoded, no API key)",
            ha="center", va="center", fontsize=7.5, color=C["loop"], fontweight="bold", zorder=3)
    ax.text(7.35, 1.28, "get_rates(type)  |  get_fees(service)  |  get_limits()",
            ha="center", va="center", fontsize=6.5, color="#566573", zorder=3)

    mcp3 = FancyBboxPatch((9.8, 1.08), 3.9, 0.72, boxstyle="round,pad=0.08",
                          facecolor="#EAF4EC", edgecolor=C["agent_yes"], lw=2, linestyle="--", zorder=2)
    ax.add_patch(mcp3)
    ax.text(11.75, 1.72, "Free API Tools  (no key needed)",
            ha="center", va="center", fontsize=7.5, color=C["agent_yes"], fontweight="bold", zorder=3)
    ax.text(11.75, 1.28, "get_weather()  |  get_country_info()  |  get_public_holidays()  |  run_python()",
            ha="center", va="center", fontsize=6.2, color="#566573", zorder=3)

    ax.text(7.0, 0.65, "MCP servers are pure Python in-process objects -- no external service, no API key, same free tools as Phase 1d",
            ha="center", fontsize=7.2, color=C["note_ok"], style="italic", fontweight="bold")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0); plt.close(fig); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Diagram Phase 9 — Best Practices
# ══════════════════════════════════════════════════════════════════════════════

def diagram_best_practices() -> bytes:
    """Three-pillar framework: Tool Design · Prompt Engineering · System Design."""
    fig, ax = _fig()

    _agent_banner(ax, is_agent=True,
                  why="Best practices are what separate a demo from a production-ready agent")

    ax.text(W / 2, 3.76, "Phase 9  --  Best Practices  (Anthropic Appendix 2)",
            ha="center", fontsize=11, fontweight="bold", color="#1C2833")
    ax.text(W / 2, 3.52,
            "Three pillars every agent needs before production · Source: Anthropic engineering blog",
            ha="center", fontsize=8, color="#566573", style="italic")

    PILLARS = [
        (1.2, C["tools"],  "Tool Design",        ["Single responsibility", "Clear name & docstring", "Informative errors", "Predictable schema"]),
        (3.5, C["memory"], "Prompt Engineering",  ["Explicit tool rules", "Stopping conditions", "Negative constraints", "Scope limitation"]),
        (5.8, C["input"],  "System Design",       ["Know when NOT to use", "Max iteration guard", "HITL for risky ops", "Test adversarially"]),
    ]

    for cx, col, title, items in PILLARS:
        _box(ax, cx, 3.08, title, col, w=2.0, h=0.36, fontsize=8.5)
        for i, item in enumerate(items):
            iy = 2.60 - i * 0.46
            bg = FancyBboxPatch((cx - 0.92, iy - 0.17), 1.84, 0.33,
                                boxstyle="round,pad=0.06",
                                facecolor="#FDFEFE", edgecolor=col,
                                linewidth=1.0, zorder=2, alpha=0.85)
            ax.add_patch(bg)
            ax.text(cx, iy, item, ha="center", va="center",
                    fontsize=7.5, color="#1C2833", zorder=3)
        ax.annotate("", xy=(cx, 0.82), xytext=(cx, 0.62),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5), zorder=4)

    ax.plot([1.2, 5.8], [0.82, 0.82], color=C["arrow"], lw=1.5, zorder=3)

    result = FancyBboxPatch((2.35, 0.14), 2.3, 0.46,
                            boxstyle="round,pad=0.1",
                            facecolor=C["agent_yes"], edgecolor="white",
                            linewidth=2, zorder=4)
    ax.add_patch(result)
    ax.text(3.5, 0.37, "Production-Ready Agent  ✓",
            ha="center", va="center", fontsize=9,
            color="white", fontweight="bold", zorder=5)
    ax.annotate("", xy=(3.5, 0.60), xytext=(3.5, 0.82),
                arrowprops=dict(arrowstyle="-|>", color=C["agent_yes"], lw=2.0), zorder=5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

# ── Phase 10 diagrams — loaded from _diagram_phase10.py ──────────────────────
from utils._diagram_phase10 import _ph10_diagrams as _ph10

(diagram_langgraph_workflows,
 diagram_langgraph_agents,
 diagram_langsmith,
 diagram_langchain,
 diagram_framework_compare) = _ph10(
    C, W, H, _fig, _box, _arrow, _agent_banner, _journey_bar,
    _agent_def_footer, _to_bytes)
