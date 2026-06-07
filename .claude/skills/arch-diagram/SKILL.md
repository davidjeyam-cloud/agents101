---
name: ckm:arch-diagram
description: "Generate production-quality HTML architecture diagrams using table-only layout (wkhtmltoimage-safe). Layered structure: color-coded component boxes, numbered layer labels, side panels (observability, security, deployment), execution loop card, flow bars, bottom bar. Outputs self-contained HTML + JPEG. Inputs: topic slug, diagram title, tagline, layer definitions. Use for: system architecture docs, course diagrams, project overviews, technical presentations."
argument-hint: "[topic-slug] [title] -- [tagline]"
license: MIT
metadata:
  author: agents101
  version: "1.0.0"
---

# Architecture Diagram Generator

Create production-quality layered architecture diagrams as self-contained HTML → JPEG.

## When to Use

- System or platform architecture documentation
- Course / learning material diagrams (like the Phase 10 LangGraph arch map)
- Project overview visuals for README or presentations
- Technical design documents requiring consistent visual style
- Any time you need a diagram that matches the layered style of the reference diagrams in this project

## Invocation

```
/ckm:arch-diagram [topic-slug] [title] -- [tagline]
```

**Examples:**
```
/ckm:arch-diagram agentic-ai "Agentic AI Architecture" -- "Perceive · Reason · Act · Evaluate · Persist"
/ckm:arch-diagram rag-pipeline "RAG Pipeline Architecture" -- "Retrieve · Augment · Generate · Evaluate"
/ckm:arch-diagram customer-support "Customer Support Agent" -- "Scalable · Safe · Observable · Grounded"
```

**Without arguments** — Claude gathers the 4 required inputs interactively.

## The 4 Required Inputs

| # | Input | Example |
|---|---|---|
| 1 | `topic-slug` | `agentic-ai`, `rag-pipeline`, `mlops` |
| 2 | `title` | `Agentic AI Architecture` |
| 3 | `tagline` | `Perceive · Reason · Act · Evaluate · Persist` |
| 4 | `[LAYER DEFINITIONS]` | See `references/golden-prompt.md` Layer Definition Guide |

If layer definitions are not provided as arguments, ask the user to describe the layers
OR infer them from the topic if sufficient context is available.

## Workflow

1. **Parse arguments** — extract slug, title, tagline from `$ARGUMENTS`
2. **Load the golden prompt** — read `references/golden-prompt.md` for the full layout spec
3. **Gather layer definitions** — from arguments, conversation context, or ask the user
4. **Generate HTML** — write to `./output/[slug]_architecture.html`
   - MUST use `<table>` only — NO CSS flexbox, NO CSS grid (wkhtmltoimage breaks on modern CSS)
   - Body width: 1500px fixed
   - Follow color system, layer structure, and component box spec exactly from `references/golden-prompt.md`
5. **Convert to JPEG** — attempt wkhtmltoimage conversion:
   ```
   wkhtmltoimage --width 1540 --quality 95 --format jpeg --enable-local-file-access \
     ./output/[slug]_architecture.html ./output/[slug]_architecture.jpg
   ```
   On Windows without wkhtmltoimage: confirm HTML is complete and note the install path.
6. **Confirm** — report output path and file size

## The One Rule That Never Changes

> **Use ONLY HTML `<table>` for all layout. No CSS flexbox, no CSS grid.**

wkhtmltoimage silently breaks on modern CSS layout. The output looks collapsed.
Tables are ugly in source but the rendered output is indistinguishable.

## Output Convention

| File | Path |
|---|---|
| HTML diagram | `./output/[slug]_architecture.html` |
| JPEG export | `./output/[slug]_architecture.jpg` |

Create the `./output/` directory if it does not exist before writing.

## Layer Design Guide (Quick Reference)

| Layer Type | Accent Color | Typical Components |
|---|---|---|
| Entry / Input | `#1C3557` | UI, API, Events, Files, Streams |
| Orchestration | `#0F5C3A` | Scheduler, Router, Workflow Engine |
| Processing / Agent | `#B05C10` | Workers, Agents, Functions, Jobs |
| Memory / Storage | `#5A3A8C` | Cache, DB, Vector Store, Object Store |
| Integration / Tools | `#2E4D7A` | APIs, Queues, SaaS tools |
| Model / Intelligence | `#2A2A2A` | LLMs, Classifiers, Embeddings, Rules |
| Infrastructure | `#7A1A1A` | Cloud, Containers, Networking, DR |

## Side Panel Guide (Quick Reference)

| Panel | Header Color | Items |
|---|---|---|
| Observability | `#1C3557` | Tracing, Metrics, Logs, Alerts |
| Security | `#8B1A1A` | Auth, Secrets, Policy, Audit |
| Deployment | `#2D5A1B` | CI/CD, Rollback, Scaling |
| Governance | `#4A3500` | Compliance, Data Lineage, Access Control |

## Execution Loop Patterns (for the right-column loop card)

| System type | Loop |
|---|---|
| Agent / AI | Perceive → Reason → Act → Evaluate → Persist → ↺ |
| Data pipeline | Ingest → Validate → Transform → Load → Monitor → ↺ |
| Request-Response | Receive → Validate → Process → Respond → Log → ↺ |
| CI/CD | Trigger → Build → Test → Deploy → Verify → ↺ |

## Color System

```
Page background:        #F7F6F2
Default box background: #F2F1EC
Default box border:     #D5D3CC
Default text:           #1a1a18
Muted text:             #6a6860
Section label text:     #9a9890

Blue  tint — bg:#EAF2FA  border:#8BB5DC  (data / input)
Green tint — bg:#E6F5EE  border:#7DC4A0  (orchestration / flow)
Orange tint — bg:#FEF2E3  border:#F0B462  (observability / output)
```

## Post-Generation Iteration

After creating the diagram, offer these follow-up actions:

- **Add a layer:** "Add Layer N called '[Name]' with accent color [hex] and components [A, B, C]"
- **Change a color:** "Change Layer 3's accent color to [hex]"
- **Add a component:** "Add '[Name]' to Layer 2 with bullets [x, y, z] using orange tint"
- **Adjust spacing:** "Tighten padding — reduce box padding to 5px and border-spacing to 4px"

## References

| Topic | File |
|---|---|
| Full Golden Prompt Template | `references/golden-prompt.md` |
| Layer definitions guide | `references/golden-prompt.md#layer-definition-guide` |
| Side panel guide | `references/golden-prompt.md#side-panel-guide` |
| Filled example (DevOps) | `references/golden-prompt.md#filled-example--devops-platform` |
| Iteration prompts | `references/golden-prompt.md#iteration-prompts` |
