"""
Phase 6b -- MCP: Model Context Protocol (Anthropic, Nov 2024)
Standard for agent-to-tool/data-source connections.
We simulate the MCP protocol with Python classes and show real JSON messages,
then wire a real LLM agent as the MCP client.
"""

import streamlit as st
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 6b -- MCP Protocol", page_icon="🔌", layout="wide")
st.title("🔌 Phase 6b -- MCP: Model Context Protocol")
st.caption("Anthropic standard (Nov 2024) -- standardises how agents connect to tools and data sources")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_mcp
st.image(diagram_mcp(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is MCP and why does it matter?"):
    st.markdown("""
    > *"MCP is an open protocol that standardises how applications provide context to LLMs."*
    > -- Anthropic, November 2024

    **The problem MCP solves:**
    Before MCP, every agent had its own custom way to connect to tools.
    A weather tool for Agent A couldn't be used by Agent B without rewriting the integration.
    MCP standardises the connection -- any agent that speaks MCP can use any MCP server.

    **The three core concepts:**

    | Concept | What it is | Analogy |
    |---|---|---|
    | **MCP Server** | Exposes tools, resources, and prompts via standard protocol | USB socket |
    | **MCP Client** | Agent that discovers and calls server capabilities | USB plug |
    | **Protocol** | JSON-RPC messages: initialize, list_tools, call_tool | USB standard |

    **Two key roles MCP servers play:**

    | Role | Example | MCP primitive |
    |---|---|---|
    | **Tools** | Run a calculation, search a DB, call an API | `tools/list`, `tools/call` |
    | **Resources** | Expose documents, database rows, file contents | `resources/list`, `resources/read` |

    **MCP vs direct tool calls (Phase 1c):**

    | | Phase 1c Direct | Phase 6b MCP |
    |---|---|---|
    | Tools defined | In Python code | On MCP server (separate process/service) |
    | Discovery | Hardcoded in agent config | `list_tools()` at runtime |
    | Swap tools | Change agent code | Replace MCP server URL |
    | Multi-agent | Agent A's tools only | Any agent uses any server |
    | Protocol | SDK-specific | Open standard (JSON-RPC 2.0) |

    **MCP vs A2A (Phase 6c):**
    - **MCP:** agent connects to a **tool/resource server** (the server is not an agent)
    - **A2A:** agent connects to another **agent** (the other side has its own reasoning)
    - They are complementary: use MCP for tools, A2A for agents

    **Real-world MCP servers (as of 2025):**
    - Anthropic Claude Desktop connects to local MCP servers for filesystem, browser
    - GitHub MCP server: let any agent read/write repos via standard protocol
    - Google Workspace MCP: agents access Drive, Calendar, Gmail
    - NexaBank could expose its policy API as an MCP server -- any agent bank-aware
    """)

with st.expander("📐 Core Code Pattern -- MCP Protocol (simulated)"):
    st.code('''
# ── MCP Server (NexaBank Policy Server) ──────────────────────────────────────
class NexaBankMCPServer:
    """Simulates an MCP server. Real servers use JSON-RPC 2.0 over stdio or HTTP."""

    def initialize(self):
        """MCP initialize handshake -- server announces capabilities."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": {"name": "nexabank-policy", "version": "1.0.0"}
        }

    def list_tools(self):
        """MCP tools/list -- server declares what tools it exposes."""
        return {
            "tools": [
                {
                    "name": "get_account_rates",
                    "description": "Get NexaBank account interest rates",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"account_type": {"type": "string"}},
                        "required": ["account_type"]
                    }
                },
                {
                    "name": "get_fee_schedule",
                    "description": "Get NexaBank fee schedule for a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"service": {"type": "string"}},
                        "required": ["service"]
                    }
                },
            ]
        }

    def call_tool(self, name: str, arguments: dict) -> dict:
        """MCP tools/call -- server executes the tool and returns result."""
        if name == "get_account_rates":
            return {"content": [{"type": "text", "text": self._get_rates(arguments["account_type"])}]}
        elif name == "get_fee_schedule":
            return {"content": [{"type": "text", "text": self._get_fees(arguments["service"])}]}
        return {"isError": True, "content": [{"type": "text", "text": "Tool not found"}]}

# ── MCP Client (the Agent side) ───────────────────────────────────────────────
class MCPClient:
    """Simulates an MCP client. Connects to an MCP server and exposes its tools to an LLM."""

    def __init__(self, server: NexaBankMCPServer):
        self.server = server
        # 1. Handshake
        self.server_info = server.initialize()
        # 2. Discover tools
        self.tools_schema = server.list_tools()["tools"]

    def call_tool(self, name: str, arguments: dict) -> str:
        """3. Call a tool via MCP protocol."""
        result = self.server.call_tool(name, arguments)
        return result["content"][0]["text"]

# ── Wire to LLM agent ─────────────────────────────────────────────────────────
mcp_client = MCPClient(NexaBankMCPServer())

# Convert MCP tool schemas to callable Python functions for the SDK
def get_account_rates(account_type: str) -> str:
    """Get NexaBank account interest rates. Args: account_type (str)"""
    return mcp_client.call_tool("get_account_rates", {"account_type": account_type})

def get_fee_schedule(service: str) -> str:
    """Get NexaBank fee schedule for a service. Args: service (str)"""
    return mcp_client.call_tool("get_fee_schedule", {"service": service})

# LLM agent uses MCP-backed tools -- identical to Phase 1c but tools come from server
config = GenerateContentConfig(
    tools=[get_account_rates, get_fee_schedule],   # backed by MCP server
    automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
    system_instruction="You are a NexaBank advisor. Use tools to get accurate information.",
)
convo = client.chats.create(model=MODEL, config=config)
''', language="python")
    st.markdown("""
**The key insight:**
The LLM agent (Phase 6b) and the LLM agent (Phase 1c) are IDENTICAL in code.
The only difference: in Phase 1c, tools are Python functions defined in the agent codebase.
In Phase 6b, the same functions are thin wrappers around `mcp_client.call_tool()`.

**Why this matters for production:**
- Swap the NexaBank policy MCP server for an updated version -- agent automatically gets new tools
- Deploy the MCP server independently, scale it separately from the agent
- Audit all tool calls at the MCP protocol layer -- one log captures all agent interactions
- Multiple agents (banking bot, fraud bot, HR bot) all share one MCP server
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# MCP Server implementation (simulation)
# ══════════════════════════════════════════════════════════════════════════════

class NexaBankMCPServer:
    """
    Simulates a NexaBank Policy MCP Server.
    In production this would be a separate process communicating via stdio or HTTP+SSE.
    """
    SERVER_NAME = "nexabank-policy-server"
    PROTOCOL_VERSION = "2024-11-05"

    def initialize(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                },
                "serverInfo": {
                    "name": self.SERVER_NAME,
                    "version": "1.0.0",
                },
            },
        }

    def list_tools(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "get_account_rates",
                        "description": "Get current NexaBank interest rates for a specific account type",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "account_type": {
                                    "type": "string",
                                    "enum": ["NexaSaver", "NexaFlex_ISA", "NexaCurrent", "mortgage"],
                                    "description": "Account type to get rates for",
                                }
                            },
                            "required": ["account_type"],
                        },
                    },
                    {
                        "name": "get_fee_schedule",
                        "description": "Get NexaBank fee schedule for a service category",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service": {
                                    "type": "string",
                                    "enum": ["international_transfer", "overdraft", "refund", "mortgage_application"],
                                    "description": "Service category",
                                }
                            },
                            "required": ["service"],
                        },
                    },
                    {
                        "name": "get_policy",
                        "description": "Get NexaBank policy details for a topic",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string",
                                    "enum": ["refund", "fraud", "complaints", "aml", "account_closure"],
                                    "description": "Policy topic",
                                }
                            },
                            "required": ["topic"],
                        },
                    },
                ]
            },
        }

    def list_resources(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "result": {
                "resources": [
                    {
                        "uri":         "nexabank://policy/terms",
                        "name":        "Terms and Conditions",
                        "description": "Full NexaBank terms and conditions document",
                        "mimeType":    "text/plain",
                    },
                    {
                        "uri":         "nexabank://policy/fee-schedule-2026",
                        "name":        "Fee Schedule 2026",
                        "description": "Complete fee schedule effective January 2026",
                        "mimeType":    "text/plain",
                    },
                ]
            },
        }

    def call_tool(self, name: str, arguments: dict) -> dict:
        tool_results = {
            ("get_account_rates", "NexaSaver"):      "NexaSaver: 4.75% AER variable. Minimum balance GBP 100. No withdrawal penalty.",
            ("get_account_rates", "NexaFlex_ISA"):   "NexaFlex ISA: 4.2% AER tax-free. Annual allowance GBP 20,000. Transfers from other ISAs accepted.",
            ("get_account_rates", "NexaCurrent"):    "NexaCurrent: 0.1% cashback on purchases. No monthly fee. Overdraft available at 39.9% EAR.",
            ("get_account_rates", "mortgage"):       "Mortgages: 2yr fix 4.89% APRC, 5yr fix 4.65% APRC, 10yr fix 4.99% APRC. Max LTV 95% FTB.",
            ("get_fee_schedule", "international_transfer"): "EU/EEA (SEPA): GBP 5. US/Canada/Australia: GBP 15. Other: GBP 25. Exchange rate: mid-market + 0.5%.",
            ("get_fee_schedule", "overdraft"):       "Arranged overdraft: 39.9% EAR. GBP 1 daily buffer (no charge). Unarranged: GBP 5/day max.",
            ("get_fee_schedule", "refund"):          "Refunds under GBP 500: auto, 3-5 working days. Over GBP 500: manager approval, 5-10 days.",
            ("get_fee_schedule", "mortgage_application"): "Mortgage application: free. Valuation fee: GBP 300-600 (property dependent). Legal fees separate.",
            ("get_policy", "refund"):         "Full refund within 30 days. Disputed transactions: report within 120 days. International refunds up to 15 days.",
            ("get_policy", "fraud"):          "Report immediately via app/0800 123 4567. Account frozen instantly. APP fraud: PSR 2023, up to GBP 415,000 reimbursement.",
            ("get_policy", "complaints"):     "Target resolution: 3 business days. Final Response Letter within 8 weeks. Then Financial Ombudsman Service (free).",
            ("get_policy", "aml"):            "EDD triggered: transactions > GBP 10,000, PEPs, high-risk countries. SAR filed with NCA if suspicious. Account may be suspended.",
            ("get_policy", "account_closure"):"Close via app/online/branch. 5 working days. Joint accounts need both holders' consent. Final statement within 10 days.",
        }
        key1 = arguments.get("account_type") or arguments.get("service") or arguments.get("topic")
        result_text = tool_results.get((name, key1), f"No data for {name}({key1})")
        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [{"type": "text", "text": result_text}],
                "isError": False,
            },
        }

    def read_resource(self, uri: str) -> dict:
        resources = {
            "nexabank://policy/terms": "NexaBank Terms and Conditions 2026. [Full document would be here...]",
            "nexabank://policy/fee-schedule-2026": "NexaBank Fee Schedule 2026. [Full schedule would be here...]",
        }
        return {
            "jsonrpc": "2.0",
            "result": {
                "contents": [{"uri": uri, "mimeType": "text/plain", "text": resources.get(uri, "Resource not found")}]
            },
        }


# ── MCP Client ─────────────────────────────────────────────────────────────────
class MCPClient:
    """Simulates an MCP client (the agent side). Discovers tools from a server."""

    def __init__(self, server: NexaBankMCPServer, protocol_log: list):
        self.server       = server
        self.log          = protocol_log
        self.server_info  = None
        self.available_tools = []
        self.available_resources = []
        self._handshake()

    def _handshake(self):
        """Step 1: initialize handshake."""
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
               "params": {"protocolVersion": "2024-11-05",
                          "clientInfo": {"name": "nexabank-agent", "version": "1.0"}}}
        self.log.append({"direction": "->", "method": "initialize", "payload": req})
        resp = self.server.initialize()
        self.log.append({"direction": "<-", "method": "initialize/result", "payload": resp})
        self.server_info = resp["result"]["serverInfo"]

        """Step 2: list tools."""
        req2 = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        self.log.append({"direction": "->", "method": "tools/list", "payload": req2})
        resp2 = self.server.list_tools()
        self.log.append({"direction": "<-", "method": "tools/list/result", "payload": resp2})
        self.available_tools = resp2["result"]["tools"]

        """Step 3: list resources."""
        req3 = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
        self.log.append({"direction": "->", "method": "resources/list", "payload": req3})
        resp3 = self.server.list_resources()
        self.log.append({"direction": "<-", "method": "resources/list/result", "payload": resp3})
        self.available_resources = resp3["result"]["resources"]

    def call_tool(self, name: str, arguments: dict) -> str:
        req = {"jsonrpc": "2.0", "id": len(self.log) + 1, "method": "tools/call",
               "params": {"name": name, "arguments": arguments}}
        self.log.append({"direction": "->", "method": "tools/call", "payload": req})
        resp = self.server.call_tool(name, arguments)
        self.log.append({"direction": "<-", "method": "tools/call/result", "payload": resp})
        return resp["result"]["content"][0]["text"]


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

tab_protocol, tab_agent, tab_concepts = st.tabs([
    "📋 Tab A -- Protocol Flow",
    "🔧 Tab B -- LLM Agent + MCP",
    "📝 Tab C -- MCP Concepts",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB A -- Protocol Flow (step-by-step message display)
# ════════════════════════════════════════════════════════════════════════════

with tab_protocol:
    st.subheader("Tab A -- MCP Protocol Flow")
    st.markdown("""
    This tab shows the **actual JSON-RPC messages** exchanged between the MCP client (agent)
    and the MCP server (NexaBank policy server) during:
    1. **Initialization handshake** -- client and server agree on protocol version
    2. **Tool discovery** -- client asks "what tools do you have?"
    3. **Tool call** -- client asks the server to execute a specific tool
    """)

    proto_log = []
    server_proto = NexaBankMCPServer()
    mcp_client_proto = MCPClient(server_proto, proto_log)

    st.markdown("### Step 1+2: Initialization + Tool Discovery (happens automatically on connect)")
    for msg in proto_log:
        direction = msg["direction"]
        icon = "📤" if direction == "->" else "📥"
        color = "#E8F4FD" if direction == "->" else "#FEF9E7"
        border = "#2E86C1" if direction == "->" else "#D4AC0D"
        label = "MCP CLIENT -> MCP SERVER" if direction == "->" else "MCP SERVER -> MCP CLIENT"
        st.markdown(
            f'<div style="background:{color};border-left:4px solid {border};'
            f'padding:8px 12px;margin:4px 0;border-radius:4px;">'
            f'<strong>{icon} {label}</strong>  <code>{msg["method"]}</code>'
            f'</div>',
            unsafe_allow_html=True,
        )
        with st.expander(f"View JSON: {msg['method']}"):
            st.code(json.dumps(msg["payload"], indent=2), language="json")

    st.markdown("---")
    st.markdown("### Step 3: Tool Call (triggered when agent needs a tool)")

    col1, col2 = st.columns(2)
    with col1:
        tool_name = st.selectbox(
            "Tool to call:",
            [t["name"] for t in mcp_client_proto.available_tools],
        )
    with col2:
        tool_schema = next(t for t in mcp_client_proto.available_tools if t["name"] == tool_name)
        prop_name = list(tool_schema["inputSchema"]["properties"].keys())[0]
        prop_enum = tool_schema["inputSchema"]["properties"][prop_name].get("enum", [])
        if prop_enum:
            arg_val = st.selectbox(f"{prop_name}:", prop_enum)
        else:
            arg_val = st.text_input(f"{prop_name}:", value="NexaSaver")

    if st.button("▶  Send tools/call message", type="primary", key="mcp_call"):
        call_log = []
        call_result = mcp_client_proto.call_tool(tool_name, {prop_name: arg_val})
        # Show the last 2 messages (call + result)
        for msg in proto_log[-2:]:
            direction = msg["direction"]
            icon = "📤" if direction == "->" else "📥"
            color = "#E8F4FD" if direction == "->" else "#FEF9E7"
            border = "#2E86C1" if direction == "->" else "#D4AC0D"
            label = "MCP CLIENT -> MCP SERVER" if direction == "->" else "MCP SERVER -> MCP CLIENT"
            with st.container(border=True):
                st.markdown(f"**{icon} {label}** `{msg['method']}`")
                st.code(json.dumps(msg["payload"], indent=2), language="json")
        st.success(f"Tool result: {call_result}")


# ════════════════════════════════════════════════════════════════════════════
# TAB B -- LLM Agent using MCP-backed tools
# ════════════════════════════════════════════════════════════════════════════

with tab_agent:
    st.subheader("Tab B -- Real LLM Agent + MCP Server")
    st.markdown("""
    The LLM agent acts as an MCP client.
    It discovers tools from the NexaBank MCP server at startup,
    then uses them to answer customer questions.
    The agent code is **identical to Phase 1c** -- only the tool source changes.
    """)

    TASKS_MCP = {
        "What savings rate do you offer?":         "What savings rate does NexaBank offer and what are the conditions?",
        "How much for an international transfer?": "I need to send money to Australia. What are the fees and how long does it take?",
        "Refund policy":                           "What is NexaBank's refund policy? I want a refund on a purchase from last month.",
        "Fraud report procedure":                  "I think my card has been used fraudulently. What should I do?",
        "Mortgage rates":                          "What mortgage rates does NexaBank currently offer?",
    }

    if "sel_mcp_b" not in st.session_state:
        st.session_state.sel_mcp_b = list(TASKS_MCP.keys())[0]

    col1, col2 = st.columns([2, 1])
    with col2:
        for label in TASKS_MCP:
            if st.button(label, key=f"mcp_{label}"):
                st.session_state.sel_mcp_b = label
                st.rerun()
    with col1:
        question = st.text_area("Customer question:", value=TASKS_MCP[st.session_state.sel_mcp_b], height=80)

    if st.button("▶  Run Agent + MCP", type="primary", key="run_mcp_b"):
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()
        agent_log = []
        server_b = NexaBankMCPServer()
        mcp_b = MCPClient(server_b, agent_log)

        # Convert MCP tools to SDK-callable functions
        def get_account_rates(account_type: str) -> str:
            """Get NexaBank interest rates. account_type: NexaSaver, NexaFlex_ISA, NexaCurrent, mortgage"""
            return mcp_b.call_tool("get_account_rates", {"account_type": account_type})

        def get_fee_schedule(service: str) -> str:
            """Get NexaBank fees. service: international_transfer, overdraft, refund, mortgage_application"""
            return mcp_b.call_tool("get_fee_schedule", {"service": service})

        def get_policy(topic: str) -> str:
            """Get NexaBank policy. topic: refund, fraud, complaints, aml, account_closure"""
            return mcp_b.call_tool("get_policy", {"topic": topic})

        config = types.GenerateContentConfig(
            tools=[get_account_rates, get_fee_schedule, get_policy],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            system_instruction=(
                "You are NexaBank's customer advisor. "
                "ALWAYS use tools to get accurate policy information. "
                "Never answer from training data alone."
            ),
        )
        convo = client.chats.create(model=MODEL, config=config)

        with st.spinner("Agent processing..."):
            response = _call(convo.send_message, question)

        tool_calls_made = []
        MAX = 4
        for _ in range(MAX):
            if not response.function_calls:
                break
            fc = response.function_calls[0]
            args = dict(fc.args)
            with st.spinner(f"Agent calls MCP tool: {fc.name}({args})..."):
                result = {"get_account_rates": get_account_rates,
                          "get_fee_schedule": get_fee_schedule,
                          "get_policy": get_policy}[fc.name](**args)
            tool_calls_made.append({"tool": fc.name, "args": args, "result": result})
            response = _call(
                convo.send_message,
                types.Part.from_function_response(name=fc.name, response={"result": result}),
            )

        # Display
        if tool_calls_made:
            with st.container(border=True):
                st.markdown("#### MCP Tool Calls Made")
                for tc in tool_calls_made:
                    col_t, col_r = st.columns([1, 2])
                    with col_t:
                        st.markdown(f"**Tool:** `{tc['tool']}`")
                        st.markdown(f"**Args:** `{tc['args']}`")
                    with col_r:
                        st.info(tc["result"])

        with st.container(border=True):
            st.markdown("#### ? Final Answer (grounded via MCP)")
            st.success(response.text)

        with st.expander("🔬 MCP Protocol Log -- all JSON-RPC messages this session"):
            st.caption(f"{len(agent_log)} messages exchanged between agent (client) and NexaBank server")
            for i, msg in enumerate(agent_log):
                direction = msg["direction"]
                label = "CLIENT -> SERVER" if direction == "->" else "SERVER -> CLIENT"
                with st.expander(f"[{i+1}] {label}  {msg['method']}"):
                    st.code(json.dumps(msg["payload"], indent=2), language="json")


# ════════════════════════════════════════════════════════════════════════════
# TAB C -- Key MCP Concepts
# ════════════════════════════════════════════════════════════════════════════

with tab_concepts:
    st.subheader("Tab C -- MCP Key Concepts and Architecture")

    st.markdown("### The two halves of MCP")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### MCP Server (Tool Provider)")
            st.markdown("""
Implements the **server side** of the protocol.
Exposes:
- **Tools** (`tools/list`, `tools/call`) -- callable actions
- **Resources** (`resources/list`, `resources/read`) -- readable data
- **Prompts** (`prompts/list`, `prompts/get`) -- reusable prompt templates

Real examples:
- NexaBank policy server (this demo)
- GitHub MCP server
- Filesystem MCP server
- Google Drive MCP server
""")
    with col2:
        with st.container(border=True):
            st.markdown("#### MCP Client (Agent)")
            st.markdown("""
Implements the **client side** of the protocol.
Does:
1. **Connect** to one or more MCP servers
2. **Discover** what tools/resources they expose
3. **Expose** discovered tools to the LLM as callable functions
4. **Route** LLM tool calls through the MCP protocol

The same agent can connect to MULTIPLE MCP servers simultaneously,
giving it access to tools from all of them.
""")

    st.markdown("### MCP message flow")
    st.code("""
Client                          Server
  |                               |
  |-- initialize() ------------->|   # Announce protocol version + capabilities
  |<-- serverInfo, capabilities --|   # Server announces what it supports
  |                               |
  |-- tools/list() ------------->|   # "What tools do you have?"
  |<-- [{name, description, schema}] # Server returns tool catalogue
  |                               |
  |  [LLM decides to call a tool] |
  |                               |
  |-- tools/call(name, args) --->|   # "Call this tool with these args"
  |<-- {content: [{type, text}]} -|   # Server returns result
  |                               |
  |  [LLM uses result to respond] |
""", language="text")

    st.markdown("### Why MCP matters for production")
    st.markdown("""
| Scenario | Without MCP | With MCP |
|---|---|---|
| New tool available | Redeploy all agents | Deploy new MCP server, agents auto-discover |
| Tool updated | Change + redeploy agent | Change MCP server, agents get new schema |
| Audit tool calls | Custom logging per agent | Standard protocol log at MCP layer |
| Multiple agents, same tools | Duplicate tool code | One MCP server serves all agents |
| Third-party tools | Custom integration per tool | Any MCP-compatible tool works |
| Cross-language | Agent + tools must be same language | Server in any language, client in any language |
""")

st.markdown("---")
st.markdown("### What's next -> Phase 6c: A2A Protocol")
st.markdown(
    "MCP standardises agent-to-tool connections. "
    "**A2A (Google, Apr 2025)** standardises agent-to-**agent** connections -- "
    "when the other side isn't a tool server but a full autonomous agent with its own reasoning."
)
