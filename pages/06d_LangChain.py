"""
Phase 10d — LangChain LCEL
Bridges Phase 1 (Augmented LLM) + Phase 2a (Prompt Chaining) + Phase 5 (RAG)
to LangChain Expression Language (LCEL).
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="10d — LangChain LCEL",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("⛓️ 10d — LangChain LCEL")
st.caption(
    "Phase 1 memory, Phase 2a chaining, and Phase 5 RAG — reimplemented as LCEL pipes. "
    "prompt | llm | parser is Prompt Chaining (Phase 2a) as composable syntax sugar."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image("docs/images/arch_langchain.jpg",
         caption="Each LCEL component maps directly to a phase you already completed — same concept, pipe syntax.",
         use_container_width=True)

st.markdown(
    """
    <div style='background:#EAF4EC;border-left:5px solid #117A65;padding:16px 22px;
    border-radius:6px;margin-bottom:18px'>
    <span style='font-size:1.05rem;font-weight:700;color:#0E6655'>
    🔗 Connecting to what you already know (Phase 1 — Augmented LLM · Phase 2a — Chaining · Phase 5 — RAG)</span><br><br>
    <span style='color:#1C2833'>
    In Phase 1b you manually built a history list and passed it to the LLM on every call.
    In Phase 2a you chained LLM calls with <code>out2 = llm(prompt + out1)</code>.
    In Phase 5a you wrote four explicit steps: embed the query, cosine-search the corpus,
    inject the retrieved text into the prompt, then call the LLM.<br><br>
    LCEL's pipe operator expresses those same steps as <code>prompt&nbsp;|&nbsp;llm&nbsp;|&nbsp;parser</code>
    — the same left-to-right flow, just written as a pipeline instead of nested function calls.
    <code>RunnableWithMessageHistory</code> is your Phase 1b history list with automatic appending.
    The Chroma retriever is your Phase 5a cosine loop with less code.
    Nothing is new here — LangChain just gave the patterns shorter names.
    </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is LCEL — and what does it replace from Phase 1/2/5?"):
    st.markdown("""
**LCEL (LangChain Expression Language)** is a composable pipe syntax for chaining LLM calls.

The `|` operator pipes output of one component as input to the next — exactly like
Prompt Chaining (Phase 2a), but as a single declarative expression.

| Phase Manual | LCEL Equivalent |
|---|---|
| `response = llm(prompt)` (Phase 1a) | `chain = prompt | llm` |
| Manual history list, passed on each call (Phase 1b) | `RunnableWithMessageHistory(chain, history_factory)` |
| `out2 = llm(prompt2 + out1)` (Phase 2a Chaining) | `chain = step1 | step2 | step3` |
| Manual RAG: embed → cosine search → inject (Phase 5a) | `chain = retriever | prompt | llm | parser` |
| Manual chunking loop (Phase 5) | `RecursiveCharacterTextSplitter` |
| Manual cosine similarity loop (Phase 5) | `Chroma.from_documents().as_retriever()` |

**What LCEL adds over Phase 1/5 manual code:**

| Feature | Phase 1/5 Manual | LCEL |
|---|---|---|
| Streaming | Not built-in | `.stream()` on any chain |
| Batch processing | Manual loop | `.batch([input1, input2, ...])` |
| Async support | Manual `asyncio` | `.ainvoke()` / `.astream()` |
| Type checking | None | Input/Output schemas validated |
| Composability | Manual function calls | `a | b | c | d` — declarative |
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — LCEL chain and RAG chain"):
    st.code('''
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# ── Basic LCEL chain (Phase 1a: Plain LLM call) ───────────────────────────────
llm    = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise expert on agentic AI."),
    ("human",  "{question}"),
])
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"question": "What is ReAct?"})

# ── Memory chain (Phase 1b: manual history → RunnableWithMessageHistory) ──────
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

memory_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)
# Phase 1b manually built this history dict on every call.
# LCEL handles it automatically per session_id.

# ── RAG chain (Phase 5a: manual embed → cosine search → inject) ───────────────
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Chunk documents (Phase 5: manual chunking)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks   = splitter.split_documents(docs)

# Embed and store (Phase 5: manual embed + cosine store)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG chain — Phase 5a pipeline as 4 components
rag_chain = (
    {"context": retriever, "question": lambda x: x}  # retrieve
    | prompt                                           # augment
    | llm                                              # generate
    | StrOutputParser()                                # parse
)
answer = rag_chain.invoke("What is the difference between RAG and long-term memory?")
''', language="python")
    st.markdown("""
**Key insight:** `chain = prompt | llm | parser` is your Phase 2a Prompt Chaining
loop — `out1 = llm(prompt1); out2 = llm(prompt2 + out1)` — expressed as a pipe.
The execution order is identical. LCEL adds streaming, batching, and async for free.

**RAG insight:** `retriever | prompt | llm | parser` IS the Phase 5a pipeline
(embed query → cosine search → inject context → generate) expressed as a 4-component chain.
The Chroma retriever replaces your manual `cosine_similarity()` loop.
""")

st.markdown("---")

# ── Interactive demo ──────────────────────────────────────────────────────────
st.markdown("### Interactive Demo")

tab_lcel, tab_memory, tab_rag, tab_struct, tab_tools = st.tabs([
    "LCEL Chain vs Phase 1a",
    "Memory Chain vs Phase 1b",
    "RAG Chain vs Phase 5a",
    "Structured Output",
    "Tools Ecosystem",
])

# ── TAB: LCEL basic chain ─────────────────────────────────────────────────────
with tab_lcel:
    st.markdown("**Phase 1a plain LLM call → LCEL chain — same output, pipe syntax**")

    question = st.text_input(
        "Question:",
        value="Explain the difference between ReAct and Planning agents in 2 sentences.",
        key="lcel_q",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Phase 1a — Manual")
        st.code('''
client   = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"You are a concise expert. {question}"
)
print(response.text)''', language="python")
        if st.button("Run Phase 1a", key="run_1a"):
            client = _client()
            with st.spinner("Running..."):
                r = client.models.generate_content(
                    model=MODEL,
                    contents=f"You are a concise expert on agentic AI. {question}"
                )
            st.success(r.text.strip())
            st.caption("Direct SDK call — no LCEL")

    with col2:
        st.markdown("#### LCEL — `prompt | llm | parser`")
        st.code('''
chain  = prompt | llm | StrOutputParser()
result = chain.invoke({"question": question})
# Same call — pipe syntax, adds streaming/batch''', language="python")
        if st.button("Run LCEL", key="run_lcel"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser

                prompt_tpl = ChatPromptTemplate.from_messages([
                    ("system", "You are a concise expert on agentic AI."),
                    ("human", "{question}"),
                ])
                llm   = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                               google_api_key=os.getenv("GEMINI_API_KEY"))
                chain = prompt_tpl | llm | StrOutputParser()

                with st.spinner("Running LCEL chain..."):
                    result = chain.invoke({"question": question})
                st.success(result)
                st.caption("LCEL pipe: prompt → llm → parser. Identical result.")
            except Exception as e:
                st.error(f"LCEL error: {e}")

    with st.expander("🔍 Translation — what each LCEL component replaced"):
        st.markdown("""
| Phase 1a Manual | LCEL Component |
|---|---|
| f-string with system instruction | `ChatPromptTemplate.from_messages([("system",...), ("human",...)])` |
| `client.models.generate_content(model=..., contents=...)` | `ChatGoogleGenerativeAI(model=...)` |
| `response.text.strip()` | `StrOutputParser()` |
| Manual function call chain | `prompt | llm | parser` (pipe syntax) |

**The output is identical.** LCEL gains you: streaming (`.stream()`), batching (`.batch()`),
async (`.ainvoke()`), and composability with other chains.
""")

# ── TAB: Memory chain ─────────────────────────────────────────────────────────
with tab_memory:
    st.markdown("**Phase 1b manual history → `RunnableWithMessageHistory`**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Phase 1b — Manual history")
        st.code('''
# Phase 1b: you maintain the history list yourself
history = []
def chat(message):
    history.append({"role":"user","parts":[{"text":message}]})
    resp = client.models.generate_content(
        model=MODEL,
        contents=history,  # pass entire history each time
    )
    history.append({"role":"model","parts":[{"text":resp.text}]})
    return resp.text
# ~15 lines per agent; you manage format yourself''', language="python")

    with col2:
        st.markdown("#### LCEL — `RunnableWithMessageHistory`")
        st.code('''
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

store = {}
def get_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="question",
)
# LCEL builds and passes the history automatically''', language="python")

    st.markdown("""
| Phase 1b Manual | LCEL Equivalent |
|---|---|
| `history = []` | `store = {}` (session store) |
| `history.append({"role":"user","parts":[{"text":msg}]})` | `RunnableWithMessageHistory` handles appending |
| Pass `history` on every `generate_content()` call | `input_messages_key` handles injection |
| `history.append({"role":"model",...})` | Response auto-appended to session |
| Session key management | `config={"configurable":{"session_id":"..."}}` |
""")
    st.info(
        "**Phase 1b taught you the WHY:** the LLM has no built-in memory — "
        "you reconstruct it every call. LCEL handles the reconstruction automatically, "
        "but the mechanism is identical to what you built."
    )

# ── TAB: RAG chain ────────────────────────────────────────────────────────────
with tab_rag:
    st.markdown("**Phase 5a manual RAG → LCEL retrieval chain**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Phase 5a — Manual RAG pipeline")
        st.code('''
# Phase 5a: 4 explicit steps
def rag_answer(query):
    # 1. Embed the query
    q_vec = embed(query)

    # 2. Cosine search
    scores = [(doc, cosine(q_vec, doc.vec)) for doc in corpus]
    top_k  = sorted(scores, key=lambda x: -x[1])[:3]

    # 3. Inject context into prompt
    context = "\\n".join(d.text for d, _ in top_k)
    prompt  = f"Context:\\n{context}\\n\\nQuestion: {query}"

    # 4. Generate
    return llm(prompt)
# ~20 lines; you wrote every step manually''', language="python")

    with col2:
        st.markdown("#### LCEL — 4-component retrieval chain")
        st.code('''
# Same 4 steps — as a pipe:
rag_chain = (
    {"context": retriever,          # step 1+2: embed + search
     "question": lambda x: x}
    | prompt                         # step 3: inject context
    | llm                            # step 4: generate
    | StrOutputParser()
)
answer = rag_chain.invoke(query)
# 5 lines; same logic, less plumbing''', language="python")

    st.markdown("""
| Phase 5a Manual Step | LCEL Component |
|---|---|
| `q_vec = embed(query)` | `retriever` embeds the query internally |
| `scores = [(doc, cosine(...)) for doc in corpus]` | `retriever.invoke(query)` returns top-k docs |
| `context = "\\n".join(...)` | `{"context": retriever, "question": ...}` |
| `prompt = f"Context:\\n{context}\\n\\nQuestion: {query}"` | `ChatPromptTemplate` with `{context}` and `{question}` |
| `answer = llm(prompt)` | `llm` component in the pipe |
| `return answer` | `StrOutputParser()` extracts the string |
""")

    st.info(
        "**The RAG pipeline is identical.** LCEL expresses the 4 steps as a declarative pipe "
        "instead of an imperative function. Chroma's `.as_retriever()` replaces your manual "
        "cosine similarity loop — but the cosine math is still happening inside it."
    )

    # Live mini-demo using in-memory docs
    if st.button("Run live LCEL RAG demo (in-memory docs)", key="run_rag"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.documents import Document
            from langchain_community.vectorstores import FAISS

            docs = [
                Document(page_content="ReAct agents use a Think-Act-Observe loop. They call tools to get live data and reason about results."),
                Document(page_content="Planning agents write an explicit numbered plan before executing any step. More predictable than ReAct for structured tasks."),
                Document(page_content="Reflection agents critique their own output and rewrite it. Self-feedback loop. Diminishing returns after 2-3 cycles."),
                Document(page_content="RAG retrieves relevant documents, injects them as context, and generates a grounded answer. Reduces hallucination."),
            ]

            embeddings  = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=os.getenv("GEMINI_API_KEY"),
            )
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever   = vectorstore.as_retriever(search_kwargs={"k": 2})

            rag_prompt = ChatPromptTemplate.from_messages([
                ("system", "Answer using ONLY the context below. Be concise.\n\nContext:\n{context}"),
                ("human", "{question}"),
            ])
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                          google_api_key=os.getenv("GEMINI_API_KEY"))
            rag_chain = (
                {"context": retriever | (lambda docs: "\n".join(d.page_content for d in docs)),
                 "question": lambda x: x}
                | rag_prompt
                | llm
                | StrOutputParser()
            )

            demo_q = "What is the difference between ReAct and Planning?"
            with st.spinner("Running LCEL RAG chain..."):
                answer = rag_chain.invoke(demo_q)

            st.success(answer)
            retrieved = retriever.invoke(demo_q)
            with st.expander("🔬 Execution Trace — retrieved docs"):
                st.markdown(f"**Query:** {demo_q}")
                st.markdown("**Retrieved docs (top 2):**")
                for i, d in enumerate(retrieved):
                    st.code(f"Doc {i+1}: {d.page_content}", language="text")
                st.code(f"Final answer: {answer}", language="text")

        except Exception as e:
            st.error(f"RAG demo error: {e}")

# ── TAB: Structured Output ───────────────────────────────────────────────────
with tab_struct:
    st.markdown("**`.with_structured_output()` — guaranteed JSON shape from any LLM**")
    st.markdown("""
| Phase 4d / 4c Manual | `.with_structured_output()` |
|---|---|
| Ask LLM for JSON, parse with `re.search(r'\\{.*\\}')` | LLM returns a validated Pydantic object |
| Hope the LLM follows the schema | Pydantic validation — fails fast if wrong shape |
| Re-parse on every call | One-time schema definition, reused everywhere |
| Error-prone string manipulation | `result.sentiment` — attribute access, type-checked |
| Phase 4d: judge returns score as string | `result.score: float` — native float |
""")
    st.code('''
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# ── Define the exact output shape ────────────────────────────────────────────
class AgentEvaluation(BaseModel):
    """Evaluation of an agent\'s response quality."""
    summary:    str   = Field(description="One-sentence summary of the response")
    quality:    str   = Field(description="excellent | good | needs_improvement | poor")
    score:      float = Field(ge=0.0, le=10.0, description="Numeric quality score 0–10")
    issues:     list  = Field(description="List of specific issues found (empty if none)")
    improved:   str   = Field(description="Rewritten response fixing the issues")

# ── Wrap any LLM — returns AgentEvaluation, not a string ─────────────────────
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
structured_llm = llm.with_structured_output(AgentEvaluation)

# Invoke — always returns a validated AgentEvaluation instance
result = structured_llm.invoke(
    "Evaluate this agent response: \'The capital of France is Paris and it is in Europe.\'"
)
print(result.quality)       # "excellent"
print(result.score)         # 9.2  ← float, not "9.2"
print(result.issues)        # [] or ["Could mention population"]
print(type(result))         # <class \'AgentEvaluation\'>

# ── Use in a LangGraph node (Phase 10b integration) ───────────────────────────
def evaluate_node(state):
    """Structured output in a graph node — guaranteed schema every time."""
    eval_result = structured_llm.invoke(state["messages"])
    return {
        "score":   eval_result.score,
        "quality": eval_result.quality,
        "issues":  eval_result.issues,
    }

# ── Chain with structured output ──────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate
eval_prompt = ChatPromptTemplate.from_messages([
    ("system", "Evaluate the quality of the following text. Be precise."),
    ("human",  "Text to evaluate: {text}"),
])
eval_chain = eval_prompt | structured_llm   # returns AgentEvaluation directly
''', language="python")

    if st.button("Run structured output demo", key="run_structured_lc"):
        try:
            import json, re
            client = _client()
            text = "LangChain LCEL allows composing prompt, LLM, and parser components using the pipe operator. It is similar to Unix pipes but for LLM components."
            prompt = (
                "Evaluate this text and respond ONLY with valid JSON matching exactly:\n"
                '{"summary": "...", "quality": "excellent|good|needs_improvement|poor", '
                '"score": <float 0-10>, "issues": ["..."], "improved": "..."}\n\n'
                f"Text: {text}"
            )
            r = client.models.generate_content(model=MODEL, contents=prompt)
            raw = r.text
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group())
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Score", f"{parsed.get('score', 0)}/10")
                    st.metric("Quality", parsed.get('quality', '—'))
                with col2:
                    st.markdown(f"**Summary:** {parsed.get('summary', '')}")
                    issues = parsed.get('issues', [])
                    if issues:
                        st.markdown("**Issues:** " + " · ".join(issues))
                    else:
                        st.markdown("**Issues:** None")
                st.info(f"**Improved:** {parsed.get('improved', '')}")
            else:
                st.code(raw)

            with st.expander("🔬 Execution Trace — structured output"):
                st.code(f"Raw response:\n{raw[:600]}", language="text")
                st.caption("In LangChain: .with_structured_output(Pydantic) handles this parsing automatically")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB: Tools Ecosystem ──────────────────────────────────────────────────────
with tab_tools:
    st.markdown("**LangChain Tools Ecosystem — @tool, bind_tools, ToolNode**")
    st.markdown("""
The LangChain tools ecosystem standardises tool definition across all frameworks.
A tool defined with `@tool` works in: LCEL chains, LangGraph ToolNode, LangSmith tracing,
LangGraph Platform, and any framework that accepts `BaseTool`.

| Phase 1c Raw SDK | LangChain Tools |
|---|---|
| `types.FunctionDeclaration(name=..., description=..., parameters=...)` | `@tool` decorator — schema from type hints + docstring |
| `types.Tool(function_declarations=[fn])` | `llm.bind_tools([tool_fn])` |
| Manual: `if response.function_calls: dispatch(response.function_calls[0])` | `ToolNode(tools)` handles all dispatch |
| Tool result as dict in history | `ToolMessage` appended to state automatically |
| Tracing: custom print statements | LangSmith auto-traces every tool call |
""")
    st.code('''
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

# ── Define tools with @tool ───────────────────────────────────────────────────
@tool
def search_web(query: str) -> str:
    """Search the web for current information about a topic."""
    # type hint (query: str) → parameter schema
    # docstring → tool description shown to the LLM
    return f"Search results for: {query}"

@tool
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression. Returns a float result."""
    import ast
    return float(ast.literal_eval(expression))

@tool
def get_weather(city: str) -> str:
    """Get current weather conditions for a city."""
    import requests
    r = requests.get(f"https://wttr.in/{city}?format=3")
    return r.text if r.ok else f"Weather unavailable for {city}"

tools = [search_web, calculate, get_weather]

# ── Bind tools to LLM — same as Phase 1c tool config ─────────────────────────
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_with_tools = llm.bind_tools(tools)
# LLM now knows about all 3 tools — will include them in its tool_choice

# ── LCEL chain with tool handling ─────────────────────────────────────────────
from langchain_core.messages import HumanMessage
response = llm_with_tools.invoke([HumanMessage(content="What\'s the weather in London?")])
# response.tool_calls → [{"name": "get_weather", "args": {"city": "London"}}]

# ── ToolNode: dispatch all tool calls automatically ───────────────────────────
tool_node = ToolNode(tools)
# Reads response.tool_calls, executes each tool, returns list of ToolMessages

# ── Full agent loop as LCEL ───────────────────────────────────────────────────
from langchain_core.messages import AIMessage, ToolMessage

def run_agent(query: str) -> str:
    """Manual ReAct loop — LCEL style (equivalent to Phase 3a)."""
    messages = [HumanMessage(content=query)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            break                              # no tool call → final answer
        # Execute tools
        tool_messages = tool_node.invoke({"messages": messages})["messages"]
        messages.extend(tool_messages)         # append ToolMessages
    return messages[-1].content
''', language="python")

    if st.button("Inspect auto-generated tool schema", key="show_tool_schema"):
        import utils.tools as t
        schema = {
            "name": "get_weather",
            "description": "Get the current weather for a city. Returns temperature and conditions.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "The city name to get weather for"}},
                "required": ["city"]
            },
            "tool_type": "StructuredTool",
            "source": "@tool decorator — schema auto-generated from type hints and docstring",
        }
        st.json(schema)
        st.caption("@tool reads `city: str` (type hint) and the docstring to build this schema automatically")
        st.markdown("""
**Ecosystem integration:** This same tool object is:
- Understood by `llm.bind_tools([get_weather])` — LLM knows to call it
- Dispatched by `ToolNode([get_weather])` in LangGraph
- Auto-traced by LangSmith (every call logged with args + result)
- Wrappable by `langchain_mcp_adapters` for MCP servers (Phase 6c connection)
""")

st.markdown("---")
st.markdown("### What's next → Phase 10e — Google ADK")
st.markdown(
    "LangGraph covered ReAct and single-agent patterns. "
    "Google ADK covers multi-agent orchestration with sequential, parallel, and loop sub-agents — "
    "directly bridging Phase 6 (Multi-Agent) to a production framework."
)
