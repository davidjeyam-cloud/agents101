"""
Phase 10b2 — LangGraph: Memory & Persistence
Layer 4 of the architecture diagram: Checkpointer, Memory Store, Vector Store, Conv. Memory.
Cross-refs: Phase 1b (manual history), Phase 5a (RAG), Phase 5b (long-term memory).
"""
import os, json
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="10b2 — LangGraph Memory", page_icon="🧠", layout="wide")

from utils.llm import MODEL, _client

st.title("🧠 10b2 — LangGraph: Memory & Persistence")
st.caption(
    "Layer 4 of the architecture: Checkpointer hierarchy, Memory Store, Conv. Memory, Vector Store. "
    "Cross-refs → Phase 1b (manual history) · Phase 5a (RAG) · Phase 5b (long-term memory)."
)

st.image("docs/images/arch_langgraph_memory.jpg", use_container_width=True,
         caption="Checkpointer hierarchy, Memory Store vs Conversation Memory vs Vector Store, and thread_id scoping")

st.markdown("""
<div style='background:#EAF4EC;border-left:5px solid #6C3483;padding:16px 22px;
border-radius:6px;margin-bottom:18px'>
<span style='font-size:1.05rem;font-weight:700;color:#6C3483'>
🔗 Connecting to what you already know (Phase 1b · Phase 5a · Phase 5b)</span><br><br>
<span style='color:#1C2833'>
In Phase 1b you manually maintained a <code>history</code> list and passed it on every call.
In Phase 5a you built a vector store with cosine search from scratch.
In Phase 5b you used ChromaDB for long-term memory.<br><br>
LangGraph's <strong>Checkpointer</strong> is your Phase 1b history list — but automatic, thread-scoped, and
swappable from in-memory to SQLite to Redis to Postgres by changing one import.
The <strong>Memory Store</strong> is your Phase 5b long-term store — but with a standard API across backends.
Nothing is new. The infrastructure is just more production-ready.
</span>
</div>
""", unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Layer 4 — Memory & Context"):
    st.markdown("""
LangGraph has **five distinct memory mechanisms** — each solves a different problem:

| Mechanism | Scope | What it stores | Phase equivalent |
|---|---|---|---|
| **Checkpointer** | Per thread (session) | Full graph state after every node | Phase 1b manual history |
| **Memory Store** | Cross-session (user) | Facts, preferences, user profile | Phase 5b ChromaDB |
| **Conv. Memory** | Within a run | Message buffer or compressed summary | Phase 1b history variants |
| **Vector Store (RAG)** | External knowledge | Embedded documents, cosine retrieval | Phase 5a RAG Agent |
| **Knowledge Graph** | Structured relationships | Entity/relation graphs, Neo4j | Not in course (advanced) |

**The Checkpointer hierarchy** (swap by changing one import):
```python
from langgraph.checkpoint.memory import MemorySaver      # dev / testing
from langgraph.checkpoint.sqlite import SqliteSaver       # local prod, zero infra
from langgraph.checkpoint.redis import RedisSaver         # distributed, requires Redis
from langgraph.checkpoint.postgres import PostgresSaver   # enterprise, requires Postgres
```
""")

# ── Core Code Pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — Checkpointer + Memory Store"):
    st.code('''
# ── Checkpointer: swap-in persistence ────────────────────────────────────────
from langgraph.checkpoint.memory import MemorySaver      # dev
from langgraph.checkpoint.sqlite import SqliteSaver       # prod — zero infra needed

# SqliteSaver: same API as MemorySaver, backed by a .db file
with SqliteSaver.from_conn_string("checkpoints.db") as cp:
    agent = create_react_agent(llm, tools, checkpointer=cp)

    # Thread ID scopes state per user/conversation
    config_user_a = {"configurable": {"thread_id": "user-alice-session-1"}}
    config_user_b = {"configurable": {"thread_id": "user-bob-session-1"}}

    # Each thread maintains independent state
    agent.invoke({"messages": [("user", "My name is Alice")]}, config_user_a)
    agent.invoke({"messages": [("user", "My name is Bob")]},   config_user_b)

    # State persists across invocations — agent remembers
    result = agent.invoke({"messages": [("user", "What is my name?")]}, config_user_a)
    # → "Your name is Alice"  (loaded from checkpoint)

# ── Memory Store: cross-session facts ─────────────────────────────────────────
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("user", "alice"), "profile", {"name": "Alice", "pref": "concise answers"})

# In a node: access the store via injected parameter
def agent_node(state, *, store: InMemoryStore):
    profile = store.get(("user", "alice"), "profile")
    user_pref = profile.value.get("pref", "")
    # Use preference to personalise the response
    ...

# ── ConversationBufferMemory vs ConversationSummaryMemory ────────────────────
# Buffer: keeps all messages (Phase 1b equivalent)
from langchain.memory import ConversationBufferMemory
buffer_mem = ConversationBufferMemory(return_messages=True)

# Summary: compresses old messages into a summary (saves tokens on long chats)
from langchain.memory import ConversationSummaryMemory
summary_mem = ConversationSummaryMemory(llm=llm, return_messages=True)
# After N turns: summary_mem auto-summarises earlier turns → shorter context window
''', language="python")
    st.markdown("""
**Why Thread ID matters:** Every call with the same `thread_id` loads the same checkpoint state —
the agent continues the conversation. Different `thread_id` = fresh state. This is how one
deployed agent serves thousands of users concurrently with complete isolation.

**SqliteSaver** is the sweet spot for local/single-server deployments: zero infrastructure,
same API as `MemorySaver`, persists across process restarts. Use it by default when building.
""")

st.markdown("---")
st.markdown("### Interactive Demos")

tab_cp, tab_store, tab_conv = st.tabs([
    "Checkpointer — thread persistence",
    "Memory Store — cross-session facts",
    "Conv. Memory — buffer vs summary",
])

# ── TAB: Checkpointer ─────────────────────────────────────────────────────────
with tab_cp:
    st.markdown("**Live demo — same thread_id picks up where it left off (MemorySaver)**")
    st.markdown("""
| Phase 1b Manual | LangGraph Checkpointer |
|---|---|
| `history = []` — you create | Checkpointer creates per thread |
| `history.append(user_msg)` | Automatic on every node |
| `history.append(model_msg)` | Automatic after every LLM call |
| Pass `history` on every call | `config={"configurable":{"thread_id":"..."}}` |
| Lost on process restart | SqliteSaver persists to disk |
""")
    col1, col2 = st.columns(2)
    if "cp_agent" not in st.session_state:
        st.session_state.cp_agent = None
        st.session_state.cp_history = []

    with col1:
        st.markdown("#### Turn 1 — tell the agent your name")
        name_in = st.text_input("Your name:", value="Alice", key="cp_name")
        if st.button("Send turn 1", key="cp_t1"):
            try:
                from langgraph.prebuilt import create_react_agent
                from langgraph.checkpoint.memory import MemorySaver
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm_cp = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                                google_api_key=os.getenv("GEMINI_API_KEY"))
                mem = MemorySaver()
                agent = create_react_agent(llm_cp, tools=[], checkpointer=mem)
                st.session_state.cp_agent = agent
                st.session_state.cp_mem   = mem
                cfg = {"configurable": {"thread_id": "demo-thread-1"}}
                r = agent.invoke({"messages": [("user", f"My name is {name_in}. Acknowledge this.")]}, cfg)
                reply = r["messages"][-1].content
                st.success(reply)
                st.session_state.cp_history.append(("user", f"My name is {name_in}."))
                st.session_state.cp_history.append(("agent", reply))
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.markdown("#### Turn 2 — ask agent to recall your name")
        if st.button("Ask: what is my name?", key="cp_t2"):
            if st.session_state.cp_agent:
                try:
                    cfg = {"configurable": {"thread_id": "demo-thread-1"}}
                    r = st.session_state.cp_agent.invoke(
                        {"messages": [("user", "What is my name?")]}, cfg
                    )
                    reply = r["messages"][-1].content
                    st.success(reply)
                    st.caption("Agent remembered from turn 1 — state loaded from MemorySaver checkpoint")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Run Turn 1 first.")

    if st.session_state.cp_history:
        with st.expander("🔬 Execution Trace — conversation state"):
            for role, msg in st.session_state.cp_history:
                st.code(f"[{role}] {msg[:200]}", language="text")
            st.caption("MemorySaver holds this state — same thread_id = same conversation")

# ── TAB: Memory Store ─────────────────────────────────────────────────────────
with tab_store:
    st.markdown("**Memory Store — persist user facts across sessions (cross-session memory)**")
    st.markdown("""
| Phase 5b Manual | LangGraph Memory Store |
|---|---|
| `chroma_client.upsert(id, embedding, metadata)` | `store.put(namespace, key, value)` |
| `chroma_client.query(embedding, n_results=5)` | `store.get(namespace, key)` |
| Custom embedding + cosine search | Built-in semantic search (InMemoryStore) |
| Per-collection namespace | Tuple namespace: `("user", user_id)` |

**Key difference from Checkpointer:**
- Checkpointer = session memory (one conversation thread)
- Memory Store = user memory (facts that persist across ALL sessions for that user)
""")
    st.code('''
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Save a user fact (cross-session)
store.put(("user", "alice"), "profile", {
    "name": "Alice",
    "preferences": "concise answers, no jargon",
    "expertise": "senior software engineer"
})
store.put(("user", "alice"), "last_topic", {"topic": "LangGraph memory"})

# Retrieve in a node — inject via parameter
def personalised_agent(state, *, store: InMemoryStore):
    profile = store.get(("user", "alice"), "profile")
    if profile:
        pref = profile.value.get("preferences", "")
        sys_msg = f"User preference: {pref}"
    # Search across all stored facts
    results = store.search(("user", "alice"), query="preferences")
    ...
''', language="python")

    st.info("**Phase 5b connection:** The Memory Store is the same concept as your ChromaDB long-term "
            "memory — but with a cleaner API and first-class LangGraph integration. "
            "For production, swap `InMemoryStore` for `AsyncPostgresStore` or `RedisStore`.")

# ── TAB: Conv. Memory comparison ──────────────────────────────────────────────
with tab_conv:
    st.markdown("**ConversationBufferMemory vs ConversationSummaryMemory — when to use each**")
    st.markdown("""
| Feature | ConversationBufferMemory | ConversationSummaryMemory |
|---|---|---|
| What it stores | Full message history (every turn) | Compressed summary of earlier turns |
| Token usage | Grows linearly with conversation length | Stays roughly constant after compression |
| Information loss | None — exact history | Some — summary may lose detail |
| Best for | Short conversations (< ~20 turns) | Long-running sessions, support tickets |
| Phase equivalent | Phase 1b manual history list | Phase 1b + LLM-based compression |
| LangGraph equivalent | `add_messages` reducer | Custom summarise node in graph |
""")
    st.code('''
# ── Buffer: every message, exact ─────────────────────────────────────────────
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

store = {}
def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{history}"),    # ← buffer or summary injected here
    ("human", "{question}"),
])
chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(chain, get_history,
    input_messages_key="question", history_messages_key="history")

# ── LangGraph equivalent: summarise node ────────────────────────────────────
def summarise_if_long(state):
    """Compress history when message count exceeds threshold."""
    if len(state["messages"]) < 10:
        return {}                       # nothing to do
    old_msgs  = state["messages"][:-2]  # keep last 2 turns intact
    summary_r = llm.invoke(
        f"Summarise this conversation history in 3 sentences:\\n" +
        "\\n".join(m.content[:200] for m in old_msgs)
    )
    from langchain_core.messages import SystemMessage
    new_msgs = [SystemMessage(content=f"Conversation summary: {summary_r.content}"),
                *state["messages"][-2:]]
    return {"messages": new_msgs}      # replace history with summary + last 2 turns
''', language="python")

    if st.button("Run buffer vs summary comparison", key="run_conv_mem"):
        try:
            client = _client()
            conversation = [
                ("user",  "Hi! My name is Alice and I work in fintech."),
                ("model", "Hello Alice! Nice to meet you. How can I help with fintech today?"),
                ("user",  "I'm building an AI agent for fraud detection."),
                ("model", "Great project! Fraud detection agents typically use anomaly detection combined with rule engines."),
                ("user",  "Yes, exactly. What memory strategy should I use for long conversations?"),
            ]
            # Simulate buffer — all messages
            buffer_tokens = sum(len(r) + len(c) for r, c in conversation) * 4  # rough token estimate
            # Simulate summary — compressed
            summary_prompt = "Summarise in 2 sentences: " + " | ".join(f"{r}: {c}" for r, c in conversation[:4])
            summary_r = client.models.generate_content(model=MODEL, contents=summary_prompt)
            summary_tokens = len(summary_r.text) * 4

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Buffer Memory**")
                st.markdown(f"Tokens in context: **~{buffer_tokens}**")
                st.markdown("Contains: all 5 turns verbatim")
                for role, msg in conversation:
                    st.code(f"[{role}] {msg}", language="text")
            with col2:
                st.markdown("**Summary Memory (after compression)**")
                st.markdown(f"Tokens in context: **~{summary_tokens}** ({summary_tokens*100//buffer_tokens}% of buffer)")
                st.success(f"Summary:\n{summary_r.text}")
                st.caption("+ last 2 turns kept verbatim")

            with st.expander("🔬 Execution Trace"):
                st.code(f"Buffer: {buffer_tokens} est. tokens\n"
                        f"Summary: {summary_tokens} est. tokens\n"
                        f"Saving: ~{buffer_tokens - summary_tokens} tokens per turn", language="text")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("### What's next → Phase 10b3 — LangGraph Tools & Security")
st.markdown("Layer 5: the @tool decorator, ToolNode dispatch, MCP adapters, Guard Agent, HITL Command(resume).")
