# Architecture Diagram — Golden Prompt Reference
> Full layout specification for `ckm:arch-diagram` skill.
> Canonical source: architecture_diagram_golden_prompt_1.md (Template v1.0)

---

## The 4 Things to Fill In

| Placeholder | Example |
|---|---|
| `[YOUR_TOPIC_SLUG]` | `kubernetes`, `data_pipeline`, `mlops` |
| `[YOUR DIAGRAM TITLE]` | `Kubernetes Platform Architecture` |
| `[YOUR TAGLINE]` | `Scalable · Resilient · Observable · Self-Healing` |
| `[LAYER DEFINITIONS]` | See Layer Definition Guide below |

---

## The Golden Prompt

```
Create a high-quality architecture diagram as a self-contained HTML file
saved to ./output/[YOUR_TOPIC_SLUG]_architecture.html

DIAGRAM TOPIC: [YOUR DIAGRAM TITLE] — [YOUR TAGLINE]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYOUT RULES (do not deviate from these)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Use ONLY HTML <table> for all layout. No CSS flexbox, no CSS grid.
  Reason: the rendering engine (wkhtmltoimage) breaks on modern CSS layout.
- Body width: 1500px fixed.
- Outer structure: one <table> with two <td> columns.
    Left column:  1130px wide — contains all numbered layers stacked top to bottom.
    Right column: 320px wide  — contains all side panels stacked top to bottom.
  Both columns: vertical-align: top.
- No external fonts, no CDN links, no JavaScript. Must work fully offline.
  Use: font-family: Arial, sans-serif

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE BLOCK (above the two-column table)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Centered h1: diagram title (22px, bold)
- Subtitle line: tagline in small uppercase (11px, color #7a7870)
- Badge row: 4-6 colored pill badges naming the core frameworks/tools used
  Style: inline-block, border-radius:20px, colored background, white text, 11px

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEFT COLUMN — NUMBERED LAYERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Define [N] layers relevant to your topic. Each layer follows this exact structure:

LAYER WRAPPER:
  <div> with border-radius:10px, overflow:hidden, border:1px solid #D5D3CC,
  margin-bottom:8px, background:#fff

LAYER INNER = <table> with 2 <td> cells:
  Cell 1 — Label cell (width: 138px, vertical-align: middle):
    - Large faded number (20px, opacity 0.6)
    - Layer name in bold uppercase (11px)
    - Subtitle in small italic (9.5px, opacity 0.75)
    - Background = the layer's accent color, text = white

  Cell 2 — Body cell (fills remaining width, vertical-align: top, padding: 10px 12px):
    - Optional section title (9.5px, uppercase, color #9a9890)
    - Component boxes (see below)
    - Optional flow bar at the bottom

COMPONENT BOXES inside a layer:
  Use <table> with border-collapse:separate, border-spacing:6px
  Each box = <td> containing a <div> with:
    - border: 1px solid [color], border-radius: 7px, padding: 8px 9px
    - background tint matching the layer theme
    - Title: 11px bold
    - Bullet list: 9.5px, color #6a6860, no list-style, each item prefixed "· "
    - Optional small tag at bottom (monospace, 9px, pill shape)

  Number of columns per row = your choice (3, 4, or 5 fit well at 1130px)
  For 2-row grids (e.g. 10 items in 5 cols): add <tr style="height:7px"> spacer between rows

FLOW BAR (optional, at bottom of any layer body):
  <div> with background:#F2F1EC, border:1px solid #D5D3CC, border-radius:6px, padding:5px 10px
  Contains: bold label + sequence of small pill tags + orange arrows (→) between them
  Pill tag style: background:#fff, border:1px solid #D5D3CC, border-radius:3px,
    font-family:monospace, font-size:9px, padding:1px 6px

CONNECTOR BETWEEN LAYERS:
  <div style="text-align:left; padding:3px 0 3px 68px; color:#aaa; font-size:14px">↓</div>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RIGHT COLUMN — SIDE PANELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Define 3-4 side panels for cross-cutting concerns (observability, security,
deployment, governance, etc.). Each panel:

  PANEL WRAPPER:
    <div> with border:1px solid #D5D3CC, border-radius:9px, overflow:hidden, margin-bottom:8px

  PANEL HEADER:
    <div> with colored background, white text, 10.5px bold, uppercase, padding:7px 11px

  PANEL BODY:
    background:#fff, padding:8px 10px
    Contains 3-6 side items stacked vertically

  SIDE ITEM:
    <div style="display:table; width:100%; background:#F2F1EC; border:1px solid #D5D3CC;
      border-radius:5px; padding:5px 7px; margin-bottom:5px">
    Two table-cells inside:
      - Icon cell: width:22px, font-size:14px, vertical-align:top
      - Text cell: title (10px bold) + subtitle (9px, color #6a6860, margin-top:1px)

EXECUTION LOOP CARD (last item in right column):
  White background card showing the system's core execution cycle
  Steps connected by ↓ arrows, each step in a small box
  Last arrow is ↺ with a note "repeats until complete"
  Use colored borders on steps to match their layer accent color

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOTTOM BAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full-width bar below the two-column table:
  background: [darkest accent color], border-radius:9px, padding:10px 16px
  Rendered as a <table> with two <td> cells:
    Left cell: "BUSINESS OUTCOMES" or "REAL-WORLD USE" (white, bold, uppercase, width:90px)
    Right cell: 8-10 pill chips
  Pill style: background:rgba(255,255,255,0.13), border:1px solid rgba(255,255,255,0.25),
    border-radius:20px, padding:4px 11px, color:#fff, font-size:9.5px

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLOR SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Page background:        #F7F6F2
Default box background: #F2F1EC
Default box border:     #D5D3CC
Default text:           #1a1a18
Muted text:             #6a6860
Section label text:     #9a9890

Tinted box variants (assign one per thematic group of components):
  Blue   tint — background:#EAF2FA, border:#8BB5DC  (data / input components)
  Green  tint — background:#E6F5EE, border:#7DC4A0  (orchestration / flow components)
  Orange tint — background:#FEF2E3, border:#F0B462  (observability / output components)

Layer label accent colors — one per layer, dark and saturated:
  #1C3557  #0F5C3A  #B05C10  #5A3A8C  #2E4D7A  #2A2A2A  #7A1A1A

Side panel header colors — distinct from layer colors:
  #1C3557 (observability)  #8B1A1A (security)  #2D5A1B (deployment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[LAYER DEFINITIONS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<-- Replace this section with your actual layers. Use the format below -->

Layer 1 — [Layer Name] (accent color: #1C3557)
  Columns: 5
  Components: [Name], [Name], [Name], [Name], [Name]
  Each component has 3 bullet points describing what it does
  Flow bar: [Step 1] → [Step 2] → [Step 3]

Layer 2 — [Layer Name] (accent color: #0F5C3A)
  Columns: 3
  Components: [Name] (40% width), [Name] (30% width), [Name] (30% width)
  Include a status/flow bar showing the execution sequence

Layer 3 — [Layer Name] (accent color: #B05C10)
  Columns: 5, Rows: 2  (10 components total)
  Row 1: [Name], [Name], [Name], [Name], [Name]
  Row 2: [Name], [Name], [Name], [Name], [Name]

Layer 4 — [Layer Name] (accent color: #5A3A8C)
  Columns: 5
  Components: [Name], [Name], [Name], [Name], [Name]
  Use blue tint for first 2, green tint for middle 2, orange tint for last

Layer 5 — [Layer Name] (accent color: #2E4D7A)
  Columns: 4, Rows: 2  (8 components total)
  Row 1: [Name], [Name], [Name], [Name]
  Row 2: [Name], [Name], [Name], [Name]

Layer 6 — [Layer Name] (accent color: #2A2A2A)
  Columns: 4
  Components: [Name], [Name], [Name], [Name]
  Each component has model/version pills below the description

Side panel 1 — [Panel Name] (header: #1C3557)
  Items: [Name + description], [Name + description], [Name + description],
         [Name + description], [Name + description]

Side panel 2 — [Panel Name] (header: #8B1A1A)
  Items: [Name + description], [Name + description], [Name + description],
         [Name + description]

Side panel 3 — [Panel Name] (header: #2D5A1B)
  Items: [Name + description], [Name + description], [Name + description],
         [Name + description]

Execution loop steps (5 steps):
  Step 1: [Name] — [what happens]
  Step 2: [Name] — [what happens]
  Step 3: [Name] — [what happens]
  Step 4: [Name] — [what happens]
  Step 5: [Name] — [what happens]

Bottom bar label: "BUSINESS OUTCOMES"
Bottom bar pills: [Outcome 1], [Outcome 2], [Outcome 3], [Outcome 4],
                  [Outcome 5], [Outcome 6], [Outcome 7], [Outcome 8]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AFTER CREATING THE HTML, RUN THESE COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Check wkhtmltoimage is installed:
   which wkhtmltoimage || apt-get install -y wkhtmltopdf   (Linux/macOS)
   winget install wkhtmltopdf                               (Windows — then restart terminal)

2. Create output directory if it doesn't exist:
   mkdir -p ./output          (Linux/macOS)
   New-Item -ItemType Directory -Force ./output   (Windows PowerShell)

3. Convert HTML to JPEG:
   wkhtmltoimage --width 1540 --quality 95 --format jpeg \
     --enable-local-file-access \
     ./output/[YOUR_TOPIC_SLUG]_architecture.html \
     ./output/[YOUR_TOPIC_SLUG]_architecture.jpg

4. Confirm output exists and print file size:
   ls -lh ./output/[YOUR_TOPIC_SLUG]_architecture.jpg      (Linux/macOS)
   Get-Item ./output/[YOUR_TOPIC_SLUG]_architecture.jpg     (Windows PowerShell)
```

---

## Layer Definition Guide

Pick the layers that make sense for your topic — remove or add as needed.

| Layer Type | When to Use | Typical Components |
|---|---|---|
| Entry / Input | How data or requests enter the system | UI, API, Events, Files, Streams |
| Orchestration | How work is routed and coordinated | Scheduler, Router, Workflow Engine |
| Processing / Agent | Where the actual work happens | Workers, Agents, Functions, Jobs |
| Memory / Storage | Where state and data are persisted | Cache, DB, Vector Store, Object Store |
| Integration / Tools | External systems the platform connects to | APIs, Queues, SaaS tools, Databases |
| Model / Intelligence | AI or ML components | LLMs, Classifiers, Embeddings, Rules |
| Infrastructure | Where everything runs | Cloud, Containers, Networking, DR |

---

## Side Panel Guide

| Panel Type | Header Color | Typical Items |
|---|---|---|
| Observability | `#1C3557` | Tracing, Metrics, Logs, Alerts, Dashboards |
| Security | `#8B1A1A` | Auth, Secrets, Policy, Audit, Encryption |
| Deployment | `#2D5A1B` | CI/CD, Rollback, Scaling, Environments |
| Governance | `#4A3500` | Compliance, Data Lineage, Access Control |
| Cost Management | `#2A2A2A` | Budgets, Quotas, Chargeback, Optimization |
| Developer Experience | `#2E4D7A` | SDKs, Docs, Local Dev, Debugging Tools |

---

## Execution Loop Guide

| Pattern | Loop |
|---|---|
| Request-Response | Receive → Validate → Process → Respond → Log |
| Agent / AI | Perceive → Reason → Act → Evaluate → Persist → ↺ |
| Data pipeline | Ingest → Validate → Transform → Load → Monitor → ↺ |
| Event-driven | Listen → Parse → Route → Execute → Acknowledge → ↺ |
| CI/CD | Trigger → Build → Test → Deploy → Verify → ↺ |

---

## Filled Example — DevOps Platform

Complete `[LAYER DEFINITIONS]` fill-in for reference:

```
Layer 1 — Source Layer (accent color: #1C3557)
  Columns: 4
  Components:
    - Git Repositories: mono/multi-repo, branch strategy, commit hooks
    - Feature Branches: short-lived branches, PR workflow, code review
    - Trunk / Main: protected branch, merge rules, version tags
    - Dependency Registry: npm / PyPI / Maven, private packages, SBOM
  Flow bar: Code Commit → PR Opened → Review Passed → Merged to Trunk

Layer 2 — CI Layer (accent color: #0F5C3A)
  Columns: 4
  Components:
    - Build: compile, lint, SAST scan, artifact creation
    - Unit Tests: coverage gates, test reports, flaky test detection
    - Container Build: Dockerfile, image scan, registry push
    - Quality Gate: coverage %, vulnerability threshold, approval check
  Flow bar: Trigger → Build → Test → Scan → Gate → Artifact

Layer 3 — CD Layer (accent color: #B05C10)
  Columns: 4
  Components:
    - Staging Deploy: helm upgrade, smoke tests, synthetic monitoring
    - Integration Tests: API tests, contract tests, performance baseline
    - Approval Gate: manual sign-off, change ticket, compliance check
    - Production Deploy: blue/green, canary rollout, feature flags
  Flow bar: Artifact → Staging → Test → Approve → Canary → Full Rollout

Layer 4 — Runtime Layer (accent color: #5A3A8C)
  Columns: 5
  Components:
    - Kubernetes: pods, deployments, HPA, node pools
    - Service Mesh: mTLS, traffic shaping, retries, circuit breaker
    - Config Management: ConfigMaps, Secrets, environment overlays
    - Secrets Manager: Vault / AWS Secrets, rotation, audit
    - API Gateway: rate limiting, auth, routing, caching

Layer 5 — Observability Layer (accent color: #2E4D7A)
  Columns: 5
  Components:
    - Metrics: Prometheus, custom counters, SLI dashboards
    - Logs: structured JSON, log aggregation, retention policy
    - Traces: distributed tracing, span analysis, latency breakdown
    - Alerts: PagerDuty, severity levels, runbook links
    - Dashboards: Grafana, service health, error budgets

Side panel 1 — Security & Compliance (header: #8B1A1A)
  Items:
    - SAST / DAST: static + dynamic code scanning at every build
    - Container Scanning: CVE checks, base image policy enforcement
    - RBAC: role-based access to clusters, namespaces, secrets
    - Audit Logs: immutable trail of all deploy and access events

Side panel 2 — Cost & Capacity (header: #2A2A2A)
  Items:
    - Resource Quotas: namespace-level CPU and memory limits
    - Autoscaling: HPA + cluster autoscaler, scale-to-zero
    - Cost Allocation: per-team chargeback, reserved vs spot usage
    - Waste Detection: idle workload alerts, rightsizing recommendations

Side panel 3 — Developer Experience (header: #2E4D7A)
  Items:
    - Local Dev: Docker Compose, kind cluster, hot reload
    - CLI Tooling: unified deploy CLI, environment switcher
    - Docs Portal: runbooks, ADRs, onboarding guides
    - Self-Service: internal platform portal, environment provisioning

Execution loop steps:
  Step 1: Commit  — developer pushes code, PR triggers pipeline
  Step 2: Build   — compile, test, scan, produce verified artifact
  Step 3: Deploy  — promote through staging → production gates
  Step 4: Monitor — metrics, logs, traces checked against SLOs
  Step 5: Respond — alert fires, on-call acts, hotfix or rollback

Bottom bar label: "DORA METRICS"
Bottom bar pills:
  Deploy Frequency, Lead Time for Change, Change Failure Rate,
  Mean Time to Recovery, SLO Compliance, Security Posture Score,
  Cost per Deploy, Developer Satisfaction
```

---

## Iteration Prompts

After the diagram is generated, use these short follow-up prompts:

**Add a layer:**
```
Add a new Layer N called "[Name]" with accent color #3a3a3a below Layer N-1 in
./output/[slug]_architecture.html. It should have 4 components: [A], [B], [C], [D].
Re-run wkhtmltoimage and confirm the new file size.
```

**Adjust spacing:**
```
In ./output/[slug]_architecture.html, reduce padding inside all component divs
from 8px to 5px and border-spacing from 6px to 4px. Re-render and confirm.
```

**Change a color:**
```
Change Layer 3's accent color from #B05C10 to #7A1A1A in
./output/[slug]_architecture.html. Re-render and confirm.
```

**Add a component to an existing layer:**
```
Add a sixth component called "[Name]" to Layer 2 in
./output/[slug]_architecture.html. Bullets: [x], [y], [z].
Use orange tint (background:#FEF2E3, border:#F0B462). Re-render and confirm.
```

---

*Template v1.0 — compatible with Claude Code + wkhtmltoimage 0.12.6+*
