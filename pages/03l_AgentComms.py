"""Phase 6d -- Agent Communications Comparison"""
import streamlit as st, os, json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
st.set_page_config(page_title="Phase 6d -- Agent Communications", page_icon="🔗", layout="wide")
st.title("🔗 Phase 6d -- Agent Communication Patterns")
st.caption("Raw delegation vs MCP vs A2A -- when to use each and how they fit together")

if not api_key:
    st.error("GEMINI_API_KEY not found."); st.stop()

client = genai.Client(api_key=api_key)
from utils.diagrams import diagram_agent_comms
st.image(diagram_agent_comms(), use_container_width=True)

with st.expander("📖 The three patterns -- summary"):
    st.markdown("""
    | Pattern | Phase | What connects | Protocol | Best for |
    |---|---|---|---|---|
    | **Raw Delegation** | 6a | Agent to sub-agent (same codebase) | Python function call | Internal agents, fast, no overhead |
    | **MCP** | 6b | Agent to tool/resource server | JSON-RPC 2.0 (open standard) | External tools, swappable servers |
    | **A2A** | 6c | Agent to remote agent | HTTP + SSE (open standard) | Cross-org agents, async tasks |

    **They are complementary -- the full production stack uses all three:**
    ```
    User
      -> Root Agent  (internal raw delegation to sub-agents)
           -> Fraud Sub-Agent    (A2A server, receives tasks from root)
                -> Fraud Tools   (MCP client, calls fraud detection MCP server)
           -> Banking Sub-Agent  (A2A server)
                -> Rates API     (MCP client)
    ```
    """)

st.markdown("---")

tab_compare, tab_decision, tab_same_task = st.tabs([
    "📊 Full Comparison Table",
    "🗺️ Decision Guide",
    "🔧 Same Task, Three Ways",
])

with tab_compare:
    st.subheader("Full Comparison -- Raw Delegation vs MCP vs A2A")
    st.markdown("""
| Dimension | Raw Delegation (6a) | MCP (6b) | A2A (6c) |
|---|---|---|---|
| **What connects** | Root to sub-agent | Agent to tool server | Agent to agent |
| **Other side** | Sub-agent (full agent) | Tool server (no reasoning) | Remote agent (full agent) |
| **Protocol** | Python function call | JSON-RPC 2.0 | HTTP + SSE |
| **Open standard** | No (code-level) | Yes (Anthropic, Nov 2024) | Yes (Google, Apr 2025) |
| **Discovery** | Hardcoded in code | tools/list at runtime | Agent Card JSON |
| **Execution** | Synchronous | Synchronous | Async (task lifecycle) |
| **Streaming** | No | No | Yes (SSE) |
| **Mid-task input** | No | No | Yes (input-required) |
| **Latency** | Lowest (in-process) | Low (local server) | Higher (HTTP round-trips) |
| **Swap without code change** | No | Yes (new server) | Yes (new agent card) |
| **Cross-organisation** | No | Possible | Primary use case |
| **Authentication** | None (shared process) | Transport-level | OAuth 2.0, API keys |
| **When to use** | Same codebase, trusted | Tools, APIs, data sources | Remote agents, async work |
""")

with tab_decision:
    st.subheader("Decision Guide -- which pattern for which situation?")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### Raw Delegation (6a)")
            st.markdown("**Use when:**")
            st.success("""
- All agents in same codebase
- Low latency required
- Internal orchestration
- Prototyping / development
- Full control needed
""")
            st.markdown("**Avoid when:**")
            st.error("""
- External partners involved
- Tools need to be swapped
- Async work required
""")
    with col2:
        with st.container(border=True):
            st.markdown("### MCP (6b)")
            st.markdown("**Use when:**")
            st.success("""
- Connecting to tools/APIs/data
- Tools may change/update
- Multiple agents share tools
- Want standard audit log
- Non-Python tool servers
""")
            st.markdown("**Avoid when:**")
            st.error("""
- The other side has reasoning
- Need async / long-running work
- Need streaming progress
""")
    with col3:
        with st.container(border=True):
            st.markdown("### A2A (6c)")
            st.markdown("**Use when:**")
            st.success("""
- Delegating to another agent
- Cross-org / cross-vendor
- Long-running async tasks
- Need streaming progress
- Mid-task input requests
""")
            st.markdown("**Avoid when:**")
            st.error("""
- The other side is just a tool
- Latency is critical
- Simple synchronous calls
""")

    st.markdown("---")
    st.info("""
**The production recommendation (2025):**
Use all three layers together:
- **Internal agent routing** -> Raw Delegation (Phase 6a)
- **Tool/API connections** -> MCP (Phase 6b)
- **Cross-org agent delegation** -> A2A (Phase 6c)

Build agents that are both **A2A servers** (receive tasks from orchestrators)
and **MCP clients** (call their own tools via MCP).
""")

with tab_same_task:
    st.subheader("Same Task -- Three Communication Patterns")
    st.markdown("**Task:** Customer asks about international transfer fees to Japan")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### Raw Delegation (6a)")
            st.code('''
# Sub-agent defined as Python function
def international_specialist(query: str) -> str:
    """Handle SWIFT, fees, FX."""
    convo = client.chats.create(
        model=MODEL,
        config=GenerateContentConfig(
            tools=[get_country_info],
            system_instruction=INTL_SYSTEM,
        )
    )
    resp = convo.send_message(query)
    # sub-agent ReAct loop...
    return resp.text

# Root calls it directly
result = international_specialist(
    "Transfer fees to Japan?"
)
''', language="python")
            st.caption("Fast. No protocol. Sub-agent is in the same Python process.")

    with col2:
        with st.container(border=True):
            st.markdown("#### MCP (6b)")
            st.code('''
# MCP server exposes tool
class NexaBankMCPServer:
    def list_tools(self):
        return {"tools": [
            {"name": "get_fee_schedule",
             "inputSchema": {...}}
        ]}
    def call_tool(self, name, args):
        return fee_lookup(args["service"])

# Agent calls via MCP protocol
mcp = MCPClient(NexaBankMCPServer())
mcp.initialize()
mcp.list_tools()  # discover

result = mcp.call_tool(
    "get_fee_schedule",
    {"service": "international"}
)
# Uses JSON-RPC 2.0 messages
''', language="python")
            st.caption("Standard. Swappable. Tool server has no reasoning.")

    with col3:
        with st.container(border=True):
            st.markdown("#### A2A (6c)")
            st.code('''
# Discover agent
card = http_get(
    "agents.nexabank.com/intl"
    "/.well-known/agent.json"
)

# Submit task asynchronously
task = {"id": uuid4(), "message": {
    "role": "user",
    "parts": [{"type": "text",
               "text": "Fees to Japan?"}]
}}
resp = http_post(
    ".../tasks/send", task
)

# Stream results
for event in stream(task["id"]):
    if event["type"] == "artifact":
        result = event["artifact"]
# Remote agent has own reasoning
''', language="python")
            st.caption("Async. Standard. Remote agent has its own tools and reasoning.")

    if st.button("▶  Run all three on the same query", type="primary", key="run_three"):
        query = "What are the fees to send GBP 5,000 to Japan and how long does it take?"
        INTL_SYSTEM = ("You are NexaBank international banking specialist. "
                       "Fees: EU/EEA GBP 5, US/Aus/Canada GBP 15, others GBP 25. "
                       "Exchange rate: mid-market +0.5%. Timeline: 2-5 business days. "
                       "Max GBP 100,000 per transfer.")

        # 1. Raw delegation
        with st.spinner("Running raw delegation..."):
            raw_resp = _call(client.models.generate_content, model=MODEL, contents=query,
                             config=types.GenerateContentConfig(system_instruction=INTL_SYSTEM))
            raw_result = raw_resp.text.strip()

        # 2. MCP-style (simulate)
        mcp_result = ("Per NexaBank MCP fee schedule: Japan (non-EU/EEA/US/AU/CA) = GBP 25 fee. "
                      "Exchange rate: mid-market + 0.5%. Timeline: 2-5 business days. "
                      "For GBP 5,000: GBP 25 fee + ~GBP 25 FX margin = ~GBP 50 total cost.")

        # 3. A2A-style (simulate with same LLM)
        with st.spinner("Running A2A agent..."):
            a2a_resp = _call(client.models.generate_content, model=MODEL, contents=query,
                             config=types.GenerateContentConfig(
                                 system_instruction=INTL_SYSTEM + " You are responding via A2A protocol."))
            a2a_result = a2a_resp.text.strip()

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("**Raw Delegation result:**")
                st.info(raw_result[:250] + "..." if len(raw_result) > 250 else raw_result)
        with col2:
            with st.container(border=True):
                st.markdown("**MCP tool result:**")
                st.info(mcp_result)
        with col3:
            with st.container(border=True):
                st.markdown("**A2A agent result:**")
                st.info(a2a_result[:250] + "..." if len(a2a_result) > 250 else a2a_result)

        st.success("""
The CONTENT of the answers is similar -- but the ARCHITECTURE is different:
- Raw: sub-agent ran in Python, in-process, synchronous
- MCP: tool server returned data, no reasoning, synchronous
- A2A: remote agent reasoned independently, async, streamable
""")

st.markdown("---")
st.markdown("### Phase 6 Complete!")
st.markdown("""
You have now mastered all four agent communication layers:
- **6a Raw Delegation** -- internal multi-agent systems
- **6b MCP** -- standardised agent-to-tool connections (Anthropic, Nov 2024)
- **6c A2A** -- standardised agent-to-agent delegation (Google, Apr 2025)
- **6d** -- decision guide: use all three together in production

**What's next -> Phase 7a: Observability & Tracing**
Running agents at production scale requires visibility into every decision.
Phase 7 covers tracing, cost measurement, and error analysis.
""")
