"""Phase 6c -- A2A Agent-to-Agent Protocol"""
import streamlit as st, os, json, uuid
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
st.set_page_config(page_title="Phase 6c -- A2A Protocol", page_icon="📡", layout="wide")
st.title("📡 Phase 6c -- A2A: Agent-to-Agent Protocol")
st.caption("Google standard (Apr 2025) -- agents discover and delegate to other agents")

if not api_key:
    st.error("GEMINI_API_KEY not found."); st.stop()

client = genai.Client(api_key=api_key)
from utils.diagrams import diagram_a2a
st.image(diagram_a2a(), use_container_width=True)

with st.expander("📖 What is A2A and how does it differ from MCP?"):
    st.markdown("""
    **MCP vs A2A:**

    | | MCP (Phase 6b) | A2A (Phase 6c) |
    |---|---|---|
    | **Connects** | Agent to TOOL SERVER | Agent to AGENT |
    | **Other side** | Executes tools (no reasoning) | Autonomous agent with own LLM |
    | **Primitives** | tools, resources | tasks, messages, streaming |
    | **Discovery** | tools/list | Agent Card at /.well-known/agent.json |
    | **Execution** | Synchronous | Async task lifecycle |
    | **Mid-task input** | Not possible | Yes (input-required state) |
    | **Made by** | Anthropic (Nov 2024) | Google (Apr 2025) |

    **Task lifecycle:** `submitted` -> `working` -> `completed` / `failed` / `cancelled`

    **They are complementary:** use MCP for tools, A2A for delegating to other agents.
    """)

with st.expander("🏗️ A2A Architecture — client-server model and Agent Cards"):
    st.markdown("""
**Why A2A was needed — the problem it solves:**

Before A2A, every agent-to-agent integration was custom code. If you had three agents from
three teams, each needed bespoke connectors. A2A defines a standard so any A2A-compliant
agent can talk to any other — the same way HTTP standardised web communication.

**Client-Server model:**

| Role | What it does | Analogy |
|---|---|---|
| **A2A Server** | Exposes its capabilities, accepts tasks, streams results | A microservice with an API |
| **A2A Client** | Discovers servers, submits tasks, reads streamed results | A caller of that API |
| **Orchestrator** | Acts as both — client to sub-agents, server to its own caller | A middle-tier service |

**Agent Card — the discovery contract:**

The Agent Card at `/.well-known/agent.json` is how a client learns what an agent can do
before sending it anything. It is the A2A equivalent of an OpenAPI spec.

```json
{
  "name": "NexaBank Fraud Agent",
  "url": "https://agents.nexabank.com/fraud",
  "version": "1.0",
  "capabilities": { "streaming": true, "pushNotifications": false },
  "skills": [
    { "id": "fraud_report",  "name": "Report Fraud",        "description": "Handle suspected fraud" },
    { "id": "app_fraud",     "name": "APP Fraud PSR 2023",  "description": "Authorised push payment reimbursement" }
  ],
  "authentication": { "schemes": ["Bearer"] }
}
```

**Four things the Agent Card declares:**
1. **Identity** — name, URL, version
2. **Capabilities** — streaming support, push notifications
3. **Skills** — discrete tasks this agent can perform (like MCP tools, but for agent delegation)
4. **Authentication** — how callers must authenticate

**Key distinction — Skills vs MCP Tools:**

| | MCP Tool | A2A Skill |
|---|---|---|
| Executed by | Your code (deterministic) | Another autonomous agent (LLM reasoning) |
| Response type | Structured return value | Natural language + artifacts |
| Mid-task input | Not possible | Yes — agent can pause and ask |
| Example | `get_weather("London")` → JSON | `"Handle fraud case #1234"` → agent decides steps |
""")

with st.expander("📋 Task Lifecycle — the six states every A2A task moves through"):
    st.markdown("""
Every A2A task has an explicit lifecycle. The server streams state updates so the client
always knows exactly where the task is.

```
submitted ──► working ──► completed
                │
                ├──► input-required ──► (client sends input) ──► working
                │
                ├──► failed
                │
                └──► cancelled
```

| State | Meaning | Client action |
|---|---|---|
| `submitted` | Task received, queued | Wait |
| `working` | Agent is actively processing | Stream artifacts as they arrive |
| `input-required` | Agent is blocked — needs more info from client | Send a follow-up message |
| `completed` | Final artifact delivered | Read result, close stream |
| `failed` | Agent hit an unrecoverable error | Inspect error, retry or escalate |
| `cancelled` | Client or server cancelled the task | Clean up |

**Why `input-required` matters — human-in-the-loop over A2A:**

This state enables a genuinely agentic pattern: the sub-agent decides mid-task that it needs
clarification. The orchestrator can route that back to a human (HITL — Phase 4b) and then
resume the sub-agent with the answer. Basic RPC calls cannot do this.

**Streaming events the server sends:**

| Event type | When | Payload |
|---|---|---|
| `status-update` | State changes | `{"state": "working"}` |
| `artifact` | Partial or final output | `{"parts": [{"type": "text", "text": "..."}]}` |
| `error` | Failure details | `{"code": 500, "message": "..."}` |
""")

with st.expander("🔄 Sequential Chaining and Hierarchical Workflows"):
    st.markdown("""
A2A enables two multi-agent composition patterns beyond simple single-hop delegation.

**Sequential Chaining — output of one agent becomes input of next:**

```
Client
  └─► Agent A (Research)     ──artifact──►  Agent B (Summarise)  ──artifact──► Client
        submitted/working/completed          submitted/working/completed
```

Each agent in the chain is independent — they do not share memory or context.
The orchestrator explicitly passes Agent A's completed artifact as Agent B's task input.
This mirrors Phase 2a (Prompt Chaining) but with autonomous agents at each step instead of raw LLM calls.

**Hierarchical Workflows — multi-level delegation:**

```
Root Orchestrator
  ├─► Manager Agent A      (A2A)
  │     ├─► Worker Agent A1  (A2A)
  │     └─► Worker Agent A2  (A2A)
  └─► Manager Agent B      (A2A)
        └─► Worker Agent B1  (A2A)
```

Each level is a full A2A client-server pair. The Root sees only Manager A and Manager B —
it does not know about the workers. This gives you:
- **Encapsulation** — sub-teams can change their internal structure without the root knowing
- **Scalability** — each manager can spawn workers independently
- **Fault isolation** — one sub-tree failing does not cascade to others

| Pattern | When to use |
|---|---|
| **Single hop** | One specialist needed, task is self-contained |
| **Sequential chain** | Output of step N must feed step N+1 (pipeline) |
| **Parallel fan-out** | Multiple independent sub-tasks, merge results (Phase 6a Tab B) |
| **Hierarchical** | Complex tasks requiring sub-teams with their own coordination |
""")

with st.expander("🔒 Extensions and Security — advanced A2A concepts"):
    st.markdown("""
**Extensions — adding capabilities beyond the core spec:**

A2A is designed to be extensible. An agent can declare non-standard capabilities in its
Agent Card under `extensions`. Common extension patterns:

| Extension type | Purpose | Example |
|---|---|---|
| **Push notifications** | Server pushes status updates to client webhook (no polling) | `"pushNotifications": {"url": "https://..."}` |
| **Custom artifact types** | Return structured data beyond plain text | `{"type": "structured", "schema": {...}}` |
| **Rate limiting hints** | Agent declares its throughput limits | `"rateLimit": {"requestsPerMinute": 60}` |
| **Versioned skills** | Multiple versions of a skill running simultaneously | `"skillVersion": "2.1"` |

**Authentication — how A2A agents verify each other:**

The Agent Card declares which authentication schemes are supported.
The client must present credentials matching one of those schemes.

| Scheme | How it works | When to use |
|---|---|---|
| **Bearer token (JWT)** | Client sends `Authorization: Bearer <token>` | Internal microservices, service accounts |
| **OAuth 2.0** | Full OAuth flow, short-lived access tokens | Cross-organisation agent-to-agent calls |
| **API Key** | Simple `X-API-Key` header | Development, low-security internal use |
| **mTLS** | Mutual certificate authentication | High-security, regulated environments |

**Security threat model for A2A:**

| Threat | Risk | Mitigation |
|---|---|---|
| **Impersonation** | Malicious agent pretends to be a legitimate sub-agent | Verify Agent Card signature / mTLS |
| **Task injection** | Attacker crafts a task payload to hijack agent behaviour | Input validation, prompt guards on server side |
| **Result poisoning** | Compromised sub-agent returns malicious artifacts | Output validation before trusting results |
| **Over-delegation** | Orchestrator grants too much scope to sub-agents | Principle of least privilege in skill scoping |

**Key rule:** Never trust a sub-agent's output blindly.
Apply the same output guardrails (Phase 4a) to A2A artifacts that you apply to direct LLM responses.
""")

with st.expander("📐 Core Code Pattern -- A2A"):
    st.code('''
# Agent Card at /.well-known/agent.json
AGENT_CARD = {
    "name": "NexaBank Fraud Agent",
    "url": "https://agents.nexabank.com/fraud",
    "capabilities": {"streaming": True},
    "skills": [{"id": "fraud_report", "name": "Report Fraud"}],
}

# 1. Discover
card = http_get("/.well-known/agent.json")

# 2. Submit task
task = {"id": str(uuid.uuid4()),
        "message": {"role": "user", "parts": [{"type": "text", "text": "Customer fraud report..."}]}}
http_post("/tasks/send", task)

# 3. Stream results
for event in http_get_stream(f"/tasks/{task_id}/stream"):
    if event["type"] == "status-update": print(event["status"]["state"])
    elif event["type"] == "artifact":    print(event["artifact"]["parts"][0]["text"])
''', language="python")

st.markdown("---")

AGENT_CARDS = {
    "fraud": {"name": "NexaBank Fraud Agent", "url": "https://agents.nexabank.com/fraud",
              "capabilities": {"streaming": True},
              "skills": [{"id": "fraud_report","name":"Report Fraud"},{"id":"app_fraud","name":"APP Fraud PSR 2023"}]},
    "banking": {"name": "NexaBank Banking Agent", "url": "https://agents.nexabank.com/banking",
                "capabilities": {"streaming": True},
                "skills": [{"id":"account_advice","name":"Account Advice"},{"id":"rate_lookup","name":"Rate Lookup"}]},
    "complaints": {"name": "NexaBank Complaints Agent", "url": "https://agents.nexabank.com/complaints",
                   "capabilities": {"streaming": False},
                   "skills": [{"id":"complaint_log","name":"Log Complaint"},{"id":"escalate_fos","name":"Escalate to FOS"}]},
}
AGENT_SYSTEMS = {
    "fraud": "You are NexaBank Fraud Agent. Handle urgently: app/0800 123 4567, account frozen immediately, APP fraud PSR 2023 up to GBP 415,000.",
    "banking": "You are NexaBank Banking Agent. NexaSaver 4.75% AER, ISA 4.2% AER, mortgages from 4.65% APRC.",
    "complaints": "You are NexaBank Complaints Agent. Resolve in 3 days. FOS after 8 weeks (free). Compensation up to GBP 200. Be empathetic.",
}

class A2AServer:
    def __init__(self, agent_id, log):
        self.agent_id = agent_id
        self.card = AGENT_CARDS[agent_id]
        self.system = AGENT_SYSTEMS[agent_id]
        self.log = log

    def get_card(self):
        self.log.append({"step":"1. Discovery","dir":"CLIENT->SERVER",
                          "req":f"GET {self.card['url']}/.well-known/agent.json","resp":self.card})
        return self.card

    def send_task(self, text):
        tid = str(uuid.uuid4())[:8]
        self.log.append({"step":"2. Send Task","dir":"CLIENT->SERVER",
                          "req":{"id":tid,"message":{"role":"user","parts":[{"type":"text","text":text}]}},
                          "resp":{"id":tid,"status":{"state":"submitted"}}})
        return {"id": tid, "text": text}

    def execute(self, task):
        self.log.append({"step":"3. Working","dir":"SERVER->CLIENT (stream)",
                          "event":{"type":"status-update","status":{"state":"working"}}})
        resp = _call(client.models.generate_content, model=MODEL, contents=task["text"],
                     config=types.GenerateContentConfig(system_instruction=self.system))
        result = resp.text.strip()
        self.log.append({"step":"4. Completed","dir":"SERVER->CLIENT (stream)",
                          "event":{"type":"artifact",
                                   "artifact":{"parts":[{"type":"text","text":result[:80]+"..."}]},
                                   "status":{"state":"completed"}}})
        return result

tab_flow, tab_demo, tab_compare = st.tabs(["📋 Tab A -- Protocol Flow","🔧 Tab B -- Orchestrator + A2A","📝 Tab C -- MCP vs A2A"])

with tab_flow:
    st.subheader("Tab A -- A2A Protocol Flow (step-by-step JSON messages)")
    col1, col2 = st.columns([1,1])
    with col1:
        target = st.selectbox("Target agent:", list(AGENT_CARDS.keys()), key="a2a_tgt")
    DEMO = {"fraud":"Customer reports GBP 850 unauthorised transactions overnight.",
            "banking":"I have GBP 25,000. Best NexaBank savings account?",
            "complaints":"My complaint has been ignored for 9 weeks. What are my options?"}
    with col2:
        task_text = st.text_area("Task:", value=DEMO[target], height=70, key="a2a_task")

    if st.button("▶  Run A2A Protocol", type="primary", key="run_a2a"):
        log = []
        srv = A2AServer(target, log)

        with st.spinner("Step 1: Fetching Agent Card..."):
            card = srv.get_card()
        with st.container(border=True):
            st.markdown("#### Step 1 -- Agent Card Discovery")
            st.success(f"**{card['name']}** | {card['url']}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Skills:**")
                for s in card["skills"]: st.markdown(f"- `{s['id']}`: {s['name']}")
            with c2:
                st.markdown("**Capabilities:**")
                for k, v in card["capabilities"].items(): st.markdown(f"- {k}: `{v}`")
            with st.expander("Agent Card JSON"): st.code(json.dumps(card, indent=2), language="json")

        with st.spinner("Step 2: Submitting task..."):
            task = srv.send_task(task_text)
        with st.container(border=True):
            st.markdown(f"#### Step 2 -- Task Submitted `id: {task['id']}`")
            st.info("Status: `submitted`")

        with st.spinner("Step 3+4: Remote agent working..."):
            result = srv.execute(task)
        with st.container(border=True):
            st.markdown("#### Steps 3+4 -- Working -> Completed")
            st.info("Stream event: `status-update` state=`working`")
            st.success(f"Stream event: `artifact` (completed)\n\n{result}")

        with st.expander("🔬 Full A2A protocol log"):
            for entry in log:
                with st.expander(f"{entry['step']} -- {entry['dir']}"):
                    payload = {k:v for k,v in entry.items() if k not in ("step","dir")}
                    st.code(json.dumps(payload, indent=2), language="json")

with tab_demo:
    st.subheader("Tab B -- Orchestrator routes via A2A")
    ORCH_TASKS = {
        "Fraud -> fraud agent": "My card was stolen, used for GBP 1,200. Urgent.",
        "Savings -> banking agent": "I have GBP 30,000. Best NexaBank savings option?",
        "Complaint -> complaints agent": "Unresolved complaint for 3 months.",
    }
    if "sel_a2a_o" not in st.session_state: st.session_state.sel_a2a_o = list(ORCH_TASKS.keys())[0]
    col1, col2 = st.columns([2,1])
    with col2:
        for label in ORCH_TASKS:
            if st.button(label, key=f"ao_{label[:12]}"): st.session_state.sel_a2a_o = label; st.rerun()
    with col1:
        orch_q = st.text_area("Query:", value=ORCH_TASKS[st.session_state.sel_a2a_o], height=70)

    if st.button("▶  Run A2A Delegation", type="primary", key="run_a2a_orch"):
        routing = _call(client.models.generate_content, model=MODEL,
                        contents=f"Query: {orch_q}\nAgents: fraud, banking, complaints\nOne word only.",
                        config=types.GenerateContentConfig(system_instruction="Reply with ONE word: fraud, banking, or complaints."))
        chosen = routing.text.strip().lower()
        if chosen not in AGENT_CARDS: chosen = "banking"

        orch_log = []
        srv2 = A2AServer(chosen, orch_log)
        card2 = srv2.get_card()
        task2 = srv2.send_task(orch_q)
        result2 = srv2.execute(task2)

        col1, col2 = st.columns([1,1])
        with col1:
            with st.container(border=True):
                st.markdown(f"**Routed to:** `{chosen}` agent")
                st.markdown(f"**{card2['name']}**")
                for s in card2["skills"]: st.markdown(f"- {s['name']}")
        with col2:
            with st.container(border=True):
                st.markdown("**Result via A2A:**")
                st.success(result2)

        with st.expander("🔬 A2A message log"):
            for entry in orch_log:
                payload = {k:v for k,v in entry.items() if k not in ("step","dir")}
                st.code(json.dumps(payload, indent=2), language="json")

with tab_compare:
    st.subheader("Tab C -- MCP vs A2A")
    st.markdown("""
| Dimension | MCP | A2A |
|---|---|---|
| Other side has reasoning? | No | Yes |
| Synchronous? | Yes | No (async) |
| Progress streaming? | No | Yes |
| Mid-task input? | No | Yes |
| Discovery | tools/list | Agent Card |
| Use for | Tools, APIs, data | Other agents |
""")
    st.info("""
**Production architecture uses both together:**
```
Orchestrator  (A2A client)
  -> Fraud Agent    (A2A server + MCP client -> fraud tools via MCP)
  -> Banking Agent  (A2A server + MCP client -> rates API via MCP)
```
A2A handles agent delegation. MCP handles tool connections. Both layers work together.
""")

st.markdown("---")
st.markdown("### What's next -> Phase 6d: Agent Communications Comparison")
st.markdown("Compare raw delegation, MCP, and A2A -- when to use each in production.")
