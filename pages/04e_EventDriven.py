"""
Phase 8e — Enterprise Event-Driven Patterns
How AI agents integrate into Kafka / event-broker ecosystems.
Architecture patterns: event trigger, async response, fan-out, dead-letter.
Simulation demo — no live Kafka required.
"""
import os, json, uuid, time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils.llm import MODEL, _call
from utils.styles import phase_header, ACCENT_COMPLETE
from utils.trace import render_trace

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 8e — Event-Driven AI", page_icon="⚡", layout="wide")

if not api_key:
    st.error("GEMINI_API_KEY not found."); st.stop()

client = genai.Client(api_key=api_key)

st.markdown(phase_header(
    "Phase 8e &nbsp;·&nbsp; Agents in Practice &nbsp;·&nbsp; Enterprise Integration",
    "⚡ Enterprise Event-Driven Patterns",
    "How agents integrate into Kafka, event brokers, and microservice ecosystems. "
    "The agent as event consumer, processor, and producer.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 Why event-driven — and how do agents fit in?"):
    st.markdown("""
Every phase so far triggered agents synchronously: a user clicks a button → agent runs → user waits.
In enterprise systems, most agent triggering is **asynchronous and event-driven**.

A banking transaction completes → an event fires → an agent analyses it for fraud → result published
to another topic → downstream systems read the verdict. No user waited synchronously.

**The enterprise reality in 2026:**

> Apache Kafka is the de facto standard for event-driven integration at enterprise scale.
> 40%+ of Fortune 1000 companies run production agent workflows triggered by events.
> — Enterprise Agentic AI Landscape 2026

**How agents slot into an event-driven architecture:**

```
External Event                 Event Broker (Kafka)          Agent                    Downstream
──────────────                 ────────────────────          ─────                    ──────────
Transaction completed  ──────► transactions.completed  ──►  Fraud Agent  ──────────► fraud.verdicts
Customer complaint     ──────► complaints.new          ──►  Triage Agent ──────────► complaints.triaged
Document uploaded      ──────► documents.received      ──►  Parse Agent  ──────────► documents.parsed
Sensor anomaly         ──────► iot.anomalies           ──►  Diag. Agent  ──────────► maintenance.alerts
```

**Agents as event consumers AND producers:**

| Role | What the agent does | Kafka term |
|---|---|---|
| **Consumer** | Reads events from a topic and processes them | Consumer group |
| **Producer** | Publishes results as new events to output topics | Producer |
| **Processor** | Reads, transforms, publishes — the full pipeline | Stream processor |

**Why this matters for agents specifically:**

| Concern | Synchronous API call | Event-driven |
|---|---|---|
| **Throughput** | One agent blocks while processing | Queue buffers thousands of events; agents process in parallel |
| **Decoupling** | Caller must wait for agent to finish | Caller fires event and continues; agent processes when ready |
| **Resilience** | Agent failure = request lost | Event stays in topic until acknowledged; retried automatically |
| **Replay** | No — call is gone | Yes — Kafka retains events; re-run agent over past events |
| **Observability** | Log individual calls | Full event stream audit trail, with timestamps and offsets |
""")

with st.expander("🏗️ Four key integration patterns"):
    st.markdown("""
**Pattern 1 — Event Trigger (simplest)**
```
[Business System] ──► [Kafka Topic] ──► [Agent Consumer] ──► [Result]
```
Agent wakes up only when an event arrives. Does nothing otherwise. Like a webhook but durable.

---

**Pattern 2 — Async Request-Response**
```
[Client] ──► [requests.topic] ──► [Agent] ──► [responses.topic] ──► [Client polls]
```
Client publishes a request event with a `correlation_id`, then polls a response topic for the matching ID.
The agent processes asynchronously and publishes the result. Client and agent never directly communicate.

---

**Pattern 3 — Fan-Out (parallel agents)**
```
[Event] ──► [Topic]
              ├──► [Agent A — Fraud check]      ──► fraud.verdicts
              ├──► [Agent B — Compliance check] ──► compliance.flags
              └──► [Agent C — Risk score]       ──► risk.scores
```
One event triggers multiple independent agents simultaneously. Results published to separate topics.
An aggregator agent reads all three output topics and makes a final decision.

---

**Pattern 4 — Dead-Letter Queue**
```
[Topic] ──► [Agent] ──► FAILS ──► [Retry 1] ──► FAILS ──► [Retry 2] ──► FAILS ──► [DLQ Topic]
```
After N retries, unprocessable events go to a dead-letter topic. A human or recovery agent inspects them.
This prevents one bad event from blocking the entire queue.

---

**Pattern 5 — Event Sourcing with Agent Replay**
```
[All events stored in Kafka] ──► [Agent replays from offset 0] ──► Rebuild full state
```
Because Kafka retains all events, you can re-run the agent over historical data — for debugging,
auditing, or deploying a new agent version that reprocesses past events with improved logic.
""")

with st.expander("📐 Core Code Pattern — Agent as Kafka Consumer/Producer"):
    st.code('''
from kafka import KafkaConsumer, KafkaProducer   # pip install kafka-python
import json, logging

# ── Agent Consumer: reads events, calls LLM, publishes results ────────────────
def run_fraud_agent(bootstrap_servers: str = "localhost:9092"):
    consumer = KafkaConsumer(
        "transactions.completed",                # input topic
        bootstrap_servers=bootstrap_servers,
        group_id="fraud-agent-group",            # consumer group — Kafka tracks offset
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    for message in consumer:                     # blocks until event arrives
        event = message.value
        transaction_id = event["transaction_id"]

        try:
            # ── Call the AI agent ─────────────────────────────────────────────
            verdict = analyse_transaction(event)

            # ── Publish result to output topic ────────────────────────────────
            producer.send("fraud.verdicts", value={
                "transaction_id": transaction_id,
                "verdict":        verdict["verdict"],
                "confidence":     verdict["confidence"],
                "reason":         verdict["reason"],
                "processed_at":   time.time(),
            })
            consumer.commit()                    # acknowledge: event processed

        except Exception as e:
            logging.error(f"Failed to process {transaction_id}: {e}")
            # Kafka will retry after session timeout — or route to DLQ after N retries

def analyse_transaction(event: dict) -> dict:
    """Call the LLM agent to assess fraud risk."""
    prompt = (
        f"Analyse this transaction for fraud risk:\\n{json.dumps(event, indent=2)}\\n\\n"
        "Return JSON: {verdict: CLEAR|SUSPICIOUS|FRAUD, confidence: 0.0-1.0, reason: str}"
    )
    response = llm_client.generate(prompt, response_format="json")
    return json.loads(response.text)
''', language="python")
    st.markdown("""
**What this replaces from earlier phases:**
- Phase 2d Orchestrator-Workers used function calls — this uses Kafka topics as the coordination layer
- Phase 6c A2A used HTTP for agent-to-agent — event-driven uses a message broker (more resilient at scale)
- Phase 7a Observability traced individual calls — Kafka gives a full stream audit trail automatically

**Production broker options:**

| Broker | Best for | Key strength |
|---|---|---|
| **Apache Kafka** | High-throughput, persistent event streams | Replay, consumer groups, retention |
| **Google Pub/Sub** | GCP deployments | Managed, serverless scaling |
| **AWS SQS / EventBridge** | AWS deployments | Deep AWS integration, serverless |
| **RabbitMQ** | Complex routing, legacy AMQP | Flexible routing, multiple protocols |
| **Redis Streams** | Low-latency, simple queues | Fast, simple, already in most stacks |
""")

# ── Demo ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Live Demo — Event-driven agent pipeline simulation")
st.caption(
    "This simulates an event-driven fraud detection pipeline. "
    "Events are 'published' to a simulated broker; the agent 'consumes' and processes each one. "
    "In production, replace the in-memory broker with Kafka."
)

# Simulated in-memory event broker
if "event_queue" not in st.session_state:
    st.session_state.event_queue = []
if "processed_events" not in st.session_state:
    st.session_state.processed_events = []

SAMPLE_EVENTS = [
    {"transaction_id": f"TXN-{str(uuid.uuid4())[:8]}", "amount": 850, "merchant": "Amazon UK",
     "location": "London", "card_present": False, "time": "02:14 AM", "currency": "GBP"},
    {"transaction_id": f"TXN-{str(uuid.uuid4())[:8]}", "amount": 12, "merchant": "Tesco Express",
     "location": "Manchester", "card_present": True, "time": "08:45 AM", "currency": "GBP"},
    {"transaction_id": f"TXN-{str(uuid.uuid4())[:8]}", "amount": 4500, "merchant": "Unknown Vendor",
     "location": "Lagos, Nigeria", "card_present": False, "time": "03:02 AM", "currency": "USD"},
    {"transaction_id": f"TXN-{str(uuid.uuid4())[:8]}", "amount": 35, "merchant": "Costa Coffee",
     "location": "Birmingham", "card_present": True, "time": "09:15 AM", "currency": "GBP"},
]

col_pub, col_proc = st.columns([1, 1])

with col_pub:
    st.markdown("### 📤 Event Publisher (simulated business system)")
    st.caption("In production: your core banking system publishes to `transactions.completed` Kafka topic.")

    event_topic = st.selectbox("Target topic:", ["transactions.completed", "complaints.new", "documents.received"])

    if st.button("Publish all 4 sample events", key="pub_events"):
        for event in SAMPLE_EVENTS:
            event["topic"] = event_topic
            event["offset"] = len(st.session_state.event_queue)
            st.session_state.event_queue.append(event)
        st.success(f"Published 4 events to `{event_topic}`")

    st.markdown(f"**Queue depth:** `{len(st.session_state.event_queue)}` events pending")
    if st.session_state.event_queue:
        st.json(st.session_state.event_queue[0])
        st.caption("↑ Next event to be consumed")

with col_proc:
    st.markdown("### 🤖 Agent Consumer (fraud detection agent)")
    st.caption("In production: agent group reads from Kafka, processes, publishes to `fraud.verdicts`.")

    SYSTEM_FRAUD = (
        "You are a fraud detection agent for NexaBank. "
        "Analyse transaction events for fraud risk. "
        "Consider: unusual amount, foreign location, night-time, card not present. "
        "Return JSON only: {verdict: CLEAR|SUSPICIOUS|FRAUD, confidence: 0.0-1.0, reason: string}"
    )

    if st.button("▶  Process next event from queue", type="primary", key="proc_event"):
        if not st.session_state.event_queue:
            st.warning("Queue empty — publish events first.")
            st.stop()

        event = st.session_state.event_queue.pop(0)
        with st.spinner(f"Processing event {event['transaction_id']}..."):
            resp = _call(
                client.models.generate_content,
                model=MODEL,
                contents=f"Analyse this transaction event:\n{json.dumps(event, indent=2)}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_FRAUD,
                    response_mime_type="application/json",
                ),
            )
        try:
            result = json.loads(resp.text)
        except json.JSONDecodeError:
            result = {"verdict": "ERROR", "confidence": 0, "reason": resp.text[:100]}

        processed = {**event, "agent_verdict": result, "published_to": "fraud.verdicts"}
        st.session_state.processed_events.insert(0, processed)

        colour = {"CLEAR": "green", "SUSPICIOUS": "orange", "FRAUD": "red"}.get(result.get("verdict", ""), "blue")
        st.markdown(
            f"<div style='border-left:4px solid {colour};padding:8px 14px;background:#f8f9fa;border-radius:4px'>"
            f"<b>{result.get('verdict','?')}</b> ({result.get('confidence', 0):.0%}) — "
            f"{result.get('reason','')}"
            f"</div>", unsafe_allow_html=True
        )
        st.caption(f"Published to `fraud.verdicts` | offset: {event.get('offset', '?')}")

    if st.button("▶  Process ALL remaining events", key="proc_all"):
        if not st.session_state.event_queue:
            st.warning("Queue empty.")
            st.stop()
        count = 0
        while st.session_state.event_queue:
            event = st.session_state.event_queue.pop(0)
            with st.spinner(f"Processing {event['transaction_id']}..."):
                resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=f"Analyse:\n{json.dumps(event, indent=2)}",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_FRAUD,
                        response_mime_type="application/json",
                    ),
                )
            try:
                result = json.loads(resp.text)
            except Exception:
                result = {"verdict": "ERROR", "confidence": 0, "reason": "parse error"}
            st.session_state.processed_events.insert(0, {**event, "agent_verdict": result})
            count += 1
        st.toast(f"✅ Processed {count} events", icon="⚡")
        st.rerun()

# ── Output topic (processed results) ──────────────────────────────────────────
if st.session_state.processed_events:
    st.markdown("---")
    st.markdown("### 📥 Output Topic — `fraud.verdicts`")
    st.caption("In production: downstream systems consume from this topic — risk engine, case management, customer comms.")
    for ev in st.session_state.processed_events[:5]:
        verdict = ev.get("agent_verdict", {})
        v = verdict.get("verdict", "?")
        colour = {"CLEAR": "#059669", "SUSPICIOUS": "#D97706", "FRAUD": "#DC2626"}.get(v, "#666")
        st.markdown(
            f"<div style='border-left:3px solid {colour};padding:6px 12px;margin:4px 0;"
            f"background:#fafafa;border-radius:3px;font-size:0.85rem'>"
            f"<b>{ev['transaction_id']}</b> · £{ev['amount']} @ {ev['merchant']} · "
            f"<span style='color:{colour};font-weight:700'>{v}</span> "
            f"({verdict.get('confidence', 0):.0%})"
            f"</div>", unsafe_allow_html=True
        )

    if st.button("Clear processed events", key="clear_proc"):
        st.session_state.processed_events = []
        st.rerun()

st.markdown("---")
with st.expander("🔍 What just happened — event-driven pattern"):
    st.markdown("""
| Component | Production equivalent | What it did in this demo |
|---|---|---|
| **Event publisher** | Core banking system → Kafka `transactions.completed` | Button adds events to in-memory list |
| **Event broker** | Kafka topic (durable, ordered, replayable) | `st.session_state.event_queue` list |
| **Agent consumer** | Consumer group reading from topic | Button pops event, calls Gemini |
| **Output publisher** | Agent → Kafka `fraud.verdicts` | Result appended to processed list |
| **Downstream consumer** | Risk engine, case management, comms | `fraud.verdicts` display table |

**The key architectural property demonstrated:**
The publisher and the agent are **completely decoupled**. The publisher doesn't know the agent exists.
The agent doesn't know who published the event. They communicate only through the topic.
This means: swap the fraud agent for a better model, add a second consumer, replay historical events —
none of this requires changes to the publisher.
""")

st.markdown("---")
st.markdown("### What's next → Phase 9 — Best Practices")
st.markdown(
    "You have now seen agents in the full production stack: "
    "stateful tasks (7d), multimodal inputs (8d), and enterprise event integration (8e). "
    "Phase 9 covers the Anthropic best practices for tool design and prompt engineering "
    "that tie all of this together."
)
