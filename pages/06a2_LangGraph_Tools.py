"""
Phase 10b3 — LangGraph: Tools & Security
Layer 5 of the architecture diagram: @tool decorator, ToolNode, Guard Agent,
MCP adapters, HITL Command(resume), structured output, audit trails.
Cross-refs: Phase 1c (tools), Phase 3a (ReAct), Phase 4b (HITL), Phase 6c (MCP).
"""
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="10b3 — LangGraph Tools & Security", page_icon="🔧", layout="wide")

from utils.diagrams import diagram_langgraph_tools_security
from utils.llm import MODEL, _client

st.title("🔧 10b3 — LangGraph: Tools & Security")
st.caption(
    "Layer 5 of the architecture: @tool decorator, ToolNode, Guard Agent, MCP adapters, "
    "HITL Command(resume), structured output. "
    "Cross-refs → Phase 1c (tools) · Phase 3a (ReAct) · Phase 4b (HITL) · Phase 6c (MCP)."
)

st.image(diagram_langgraph_tools_security(), use_container_width=True,
         caption="Layer 5 — Tools & Security: tool call flow (left) + guard/HITL/audit (right)")

st.markdown("""
<div style='background:#FEF6E4;border-left:5px solid #B05C10;padding:16px 22px;
border-radius:6px;margin-bottom:18px'>
<span style='font-size:1.05rem;font-weight:700;color:#B05C10'>
🔗 Connecting to what you already know (Phase 1c · Phase 3a · Phase 4b · Phase 6c)</span><br><br>
<span style='color:#1C2833'>
In Phase 1c you manually parsed <code>response.function_calls</code> and dispatched tools yourself.
In Phase 3a (ReAct) you ran the Think→Act→Observe loop by hand.
In Phase 4b (HITL) you interrupted the loop for human approval using a flag in the loop.<br><br>
LangGraph's <strong>ToolNode</strong> handles Phase 1c dispatch automatically.
<strong>create_react_agent</strong> is Phase 3a as a compiled graph.
<strong>interrupt_before + Command(resume=...)</strong> is Phase 4b as a first-class graph primitive — pausing
mid-graph, waiting for a human signal, then resuming exactly where it stopped.
</span>
</div>
""", unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Layer 5 — Tools & Security"):
    st.markdown("""
LangGraph's tool layer has **four distinct upgrade paths** over raw SDK tool use:

| Capability | Phase 1c Raw SDK | LangGraph Tool Layer |
|---|---|---|
| Tool definition | `types.FunctionDeclaration` | `@tool` decorator (auto-generates schema) |
| Dispatch | Manual: parse `response.function_calls`, call fn | `ToolNode` handles all dispatch |
| Error handling | Try/except in your loop | `ToolNode` catches + returns errors as messages |
| HITL pause | Flag + break in while loop | `interrupt_before=["tools"]` — graph pauses |
| HITL resume | Re-enter loop with human input | `graph.invoke(Command(resume=...))` |
| MCP tools | Manual HTTP/JSON-RPC calls | `langchain_mcp_adapters` wraps as `@tool` |
| Guard Agent | Custom pre-tool LLM call | `guard_node` as graph node before ToolNode |
| Audit trail | Print statements | LangSmith auto-traces all tool calls |

**The Guard Agent pattern** (Layer 5 security):
A `guard_node` runs **before** ToolNode. It checks:
1. Is this tool call within the agent's scope?
2. Would this action cause irreversible harm?
3. Does it require human approval?
If any check fails, the guard routes to a `reject_node` instead of proceeding.
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — @tool + ToolNode + Guard Agent + HITL"):
    st.code('''
# ── 1. @tool decorator — auto-generates JSON schema ──────────────────────────
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Returns temperature and conditions."""
    # LangChain reads the docstring as the tool description
    # It reads the type hints to generate the JSON schema
    import requests
    r = requests.get(f"https://wttr.in/{city}?format=3")
    return r.text if r.ok else f"Weather unavailable for {city}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. REQUIRES human approval before executing."""
    # High-risk tool — should go through HITL
    return f"Email sent to {to}: {subject}"

tools = [get_weather, send_email]

# ── 2. ToolNode — automatic dispatch (replaces Phase 1c manual loop) ──────────
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)   # give it the tools list
# ToolNode reads tool_calls from the last AIMessage and executes them
# Returns ToolMessages that the LLM can read in the next turn

# ── 3. Guard Agent — security node before tools ───────────────────────────────
from typing import Literal
from langgraph.graph import StateGraph, MessagesState, START, END

def guard_node(state: MessagesState) -> dict:
    """Check if the intended tool call is safe to execute."""
    last_msg = state["messages"][-1]
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return {"messages": []}

    for tc in last_msg.tool_calls:
        if tc["name"] == "send_email":
            # High-risk action — flag for HITL
            state["requires_approval"] = True
    return {}

def route_after_guard(state) -> Literal["tools", "hitl", END]:
    last_msg = state["messages"][-1]
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return END
    if state.get("requires_approval"):
        return "hitl"              # pause for human
    return "tools"                 # safe to proceed

# ── 4. HITL with interrupt_before ─────────────────────────────────────────────
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

def hitl_node(state: MessagesState):
    """Pause and wait for human approval."""
    last_msg = state["messages"][-1]
    tool_name = last_msg.tool_calls[0]["name"] if last_msg.tool_calls else "unknown"
    # interrupt() pauses the graph — returns control to the caller
    human_decision = interrupt(f"Approve tool call '{tool_name}'? (yes/no)")
    if human_decision.lower() != "yes":
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content="Action rejected by human reviewer.")]}
    return {}  # proceed to tools

# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("agent",  lambda s: {"messages": [llm_with_tools.invoke(s["messages"])]})
builder.add_node("guard",  guard_node)
builder.add_node("hitl",   hitl_node)
builder.add_node("tools",  tool_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", "guard")
builder.add_conditional_edges("guard", route_after_guard)
builder.add_edge("hitl", "tools")
builder.add_edge("tools", "agent")   # back to agent after tool result

mem = MemorySaver()
graph = builder.compile(checkpointer=mem)

# ── 5. Resume after HITL pause ────────────────────────────────────────────────
cfg = {"configurable": {"thread_id": "user-1"}}

# First invoke: graph pauses at hitl_node
result = graph.invoke({"messages": [("user", "Send an email to alice@example.com")]}, cfg)
# result is an Interrupt — not a final answer

# Human approves in UI, then:
final = graph.invoke(Command(resume="yes"), cfg)  # graph resumes from hitl_node
''', language="python")
    st.markdown("""
**Why `Command(resume=...)` beats a flag:** In Phase 4b, you tracked approval state in `st.session_state`
and re-entered the while loop manually. `Command(resume=...)` is cleaner — it loads the exact checkpoint
where the graph paused and injects the human's response as if it were returned from `interrupt()`.
The graph code reads it as a normal function return. No re-running already-completed nodes.

**Guard Agent vs Guardrails (Phase 4a):** Phase 4a Guardrails check the *input message* (is the user
asking something harmful?). The Guard Agent checks the *tool call* (is the action about to be taken safe?).
Both are needed in production — they guard different layers.
""")

st.markdown("---")
st.markdown("### Interactive Demos")

tab_tool, tab_guard, tab_mcp = st.tabs([
    "@tool — decorator vs raw SDK",
    "Guard Agent + HITL flow",
    "MCP + Structured Output",
])

# ── TAB: @tool comparison ─────────────────────────────────────────────────────
with tab_tool:
    st.markdown("**@tool decorator — what it generates vs Phase 1c manual FunctionDeclaration**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Phase 1c: Manual FunctionDeclaration")
        st.code('''
from google.genai import types

# You write this schema by hand
weather_fn = types.FunctionDeclaration(
    name="get_weather",
    description="Get current weather for a city.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING,
                description="The city name"
            )
        },
        required=["city"]
    )
)
tool_config = types.Tool(function_declarations=[weather_fn])
''', language="python")

    with col2:
        st.markdown("#### LangGraph: @tool generates the schema")
        st.code('''
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city.
    Returns temperature and conditions."""
    # Docstring → description
    # Type hint (city: str) → schema
    # Return type → output schema
    ...

# View the auto-generated schema:
print(get_weather.name)         # "get_weather"
print(get_weather.description)  # from docstring
print(get_weather.args_schema)  # Pydantic model from hints
''', language="python")

    if st.button("Show auto-generated tool schema", key="show_schema"):
        st.json({
            "name": "get_weather",
            "description": "Get current weather for a city. Returns temperature and conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"}
                },
                "required": ["city"]
            }
        })
        st.caption("@tool reads the type hints and docstring — zero boilerplate")

    st.markdown("---")
    st.markdown("**ToolNode dispatch — live comparison**")

    if st.button("Run weather tool via ToolNode pattern", key="run_toolnode"):
        try:
            client = _client()
            import utils.tools as t
            # Simulate what ToolNode does: execute the tool call, return ToolMessage
            city = "London"
            result = t.get_weather(city)
            st.success(f"ToolNode executed `get_weather(city='{city}')`")
            st.code(f"ToolMessage: {result}", language="text")

            with st.expander("🔬 Execution Trace — ToolNode internal flow"):
                st.code(
                    "1. Agent returns AIMessage with tool_calls=[{name:'get_weather', args:{city:'London'}}]\n"
                    "2. ToolNode reads tool_calls from last message\n"
                    "3. ToolNode looks up 'get_weather' in its tools list\n"
                    "4. ToolNode calls get_weather(city='London')\n"
                    f"5. ToolNode wraps result in ToolMessage(content='{result[:80]}...')\n"
                    "6. ToolMessage appended to state['messages']\n"
                    "7. Graph routes back to agent node — agent reads ToolMessage and responds",
                    language="text"
                )
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB: Guard Agent + HITL ───────────────────────────────────────────────────
with tab_guard:
    st.markdown("**Guard Agent — pre-tool security check simulation**")
    st.markdown("""
| Phase 4a Guardrails | Guard Agent (Phase 10b3) |
|---|---|
| Checks: user input (is the question safe?) | Checks: tool call (is the action safe?) |
| Runs at conversation entry | Runs between agent node and ToolNode |
| Blocks malicious prompts | Blocks dangerous tool invocations |
| Pattern: LLM judges input | Pattern: rule-based or LLM judges tool call |
| Output: allow/block message | Output: proceed/reject/escalate-to-HITL |
""")
    tool_to_call = st.selectbox(
        "Tool the agent wants to call:",
        ["get_weather", "get_stock_price", "send_email (high risk)", "delete_database (irreversible)"],
        key="guard_tool"
    )
    if st.button("Run guard check", key="run_guard"):
        try:
            client = _client()
            tool_name = tool_to_call.split(" ")[0]
            sys_p = (
                "You are a security Guard Agent. Given a tool call, classify it as:\n"
                "SAFE — low risk, no data mutation, reversible\n"
                "HITL — moderate risk, requires human approval before proceeding\n"
                "BLOCK — high risk, irreversible, or out of scope\n\n"
                "Respond with JSON: {\"verdict\": \"SAFE|HITL|BLOCK\", \"reason\": \"<one sentence>\"}"
            )
            user_p = f"Tool being called: {tool_name}"
            r = client.models.generate_content(model=MODEL, contents=f"{sys_p}\n\n{user_p}")
            import json, re
            raw = r.text
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            parsed = json.loads(m.group()) if m else {"verdict": "SAFE", "reason": raw[:100]}
            verdict = parsed.get("verdict", "SAFE")
            reason  = parsed.get("reason", "")

            color = {"SAFE": "🟢", "HITL": "🟡", "BLOCK": "🔴"}.get(verdict, "⚪")
            st.markdown(f"### Guard verdict: {color} **{verdict}**")
            st.info(reason)

            if verdict == "HITL":
                st.warning("Graph would PAUSE here — waiting for human approval")
                approved = st.radio("Approve?", ["Approve", "Reject"], key="hitl_radio", horizontal=True)
                if st.button("Submit decision", key="hitl_submit"):
                    if approved == "Approve":
                        st.success("Command(resume='yes') sent — graph resumes at ToolNode")
                    else:
                        st.error("Command(resume='no') sent — graph routes to reject_node")
            elif verdict == "BLOCK":
                st.error("Tool call blocked. Agent receives: 'This action is outside permitted scope.'")
            else:
                st.success(f"Proceeding to ToolNode — execute {tool_name}()")

            with st.expander("🔬 Execution Trace — guard node"):
                st.code(f"System: {sys_p[:200]}...\n\nUser: {user_p}\n\nRaw response: {raw[:300]}", language="text")
                st.code(f"Parsed: verdict={verdict}, reason={reason}\nRoute: {'tools' if verdict=='SAFE' else 'hitl' if verdict=='HITL' else 'reject'}", language="text")

        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB: MCP + Structured Output ─────────────────────────────────────────────
with tab_mcp:
    st.markdown("**MCP via langchain_mcp_adapters — Phase 6c MCP as a LangChain tool**")
    st.markdown("""
| Phase 6c MCP (raw simulation) | LangGraph MCP integration |
|---|---|
| Simulated JSON-RPC protocol | Real `langchain_mcp_adapters` package |
| Manual tool dispatch | MCP tools appear as `@tool` in ToolNode |
| No LangSmith tracing | Full auto-trace in LangSmith |
| One server per demo | Multi-server: filesystem + Slack + GitHub |
""")
    st.code('''
# langchain_mcp_adapters wraps any MCP server as LangChain tools
# pip install langchain-mcp-adapters

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Connect to any MCP-compatible server
# (works with Claude Desktop MCP servers, local stdio servers, etc.)
async with MultiServerMCPClient({
    "filesystem": {
        "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
        "transport": "stdio",
    },
    "slack": {
        "url": "https://mcp.slack.com/sse",
        "transport": "sse",
        "headers": {"Authorization": f"Bearer {os.getenv('SLACK_TOKEN')}"}
    }
}) as mcp:
    tools = await mcp.get_tools()  # returns List[BaseTool] — same as @tool decorated fns

    agent = create_react_agent(llm, tools)
    result = await agent.ainvoke({
        "messages": [("user", "Read the README and post a summary to #dev-updates")]
    })
    # Agent decides: first call filesystem/read_file, then slack/post_message
    # Both MCP tools appear identical to @tool functions in ToolNode dispatch
''', language="python")

    st.markdown("---")
    st.markdown("**Structured Output — `.with_structured_output(Pydantic)` (Phase 10d upgrade)**")
    st.code('''
# Force any LangChain LLM to return a validated Pydantic object
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class AnalysisResult(BaseModel):
    summary: str     = Field(description="One-paragraph summary")
    sentiment: str   = Field(description="positive | negative | neutral")
    key_topics: list = Field(description="List of 3-5 main topics")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
structured_llm = llm.with_structured_output(AnalysisResult)

# Returns a validated AnalysisResult object — not a string
result = structured_llm.invoke("Analyse this text: LangGraph simplifies agentic workflows.")
print(result.sentiment)      # "positive"
print(result.confidence)     # 0.92
print(type(result))          # <class 'AnalysisResult'>

# In a graph node:
def analysis_node(state):
    result = structured_llm.invoke(state["messages"])
    return {"analysis": result.model_dump()}
''', language="python")

    if st.button("Run structured output demo", key="run_structured"):
        try:
            client = _client()
            import json, re
            text = "LangGraph provides a clean way to build production-grade AI agents with built-in persistence, interrupts, and streaming. It is opinionated but powerful."
            prompt = (
                f"Analyse this text and respond ONLY with a JSON object with these fields:\n"
                f"summary (string), sentiment (positive/negative/neutral), "
                f"key_topics (list of 3-5 strings), confidence (float 0-1)\n\n"
                f"Text: {text}"
            )
            r = client.models.generate_content(model=MODEL, contents=prompt)
            raw = r.text
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group())
                st.json(parsed)
                st.caption("Structured output — same shape every time, validated by Pydantic in LangChain")
            else:
                st.code(raw)

            with st.expander("🔬 Execution Trace — structured output"):
                st.code(f"Prompt: {prompt[:300]}\n\nRaw: {raw[:400]}", language="text")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("### What's next → Phase 10b4 — LangGraph Platform & Production")
st.markdown(
    "Studio UI, Deploy/Durable Execution, API Server patterns, `draw_mermaid_png()` on every graph, "
    "streaming token-by-token, production readiness checklist."
)
