"""
Phase 5b -- Long-term Memory
Vector store (in-memory) using gemini-embedding-001 + cosine similarity.
Memories persist across conversation turns in session_state.
Two tabs:
  A. Memory Bank   -- manually store, browse, recall memories with similarity scores
  B. Agent Memory  -- NexaBank advisor that remembers customers across turns
"""

import streamlit as st
import os
import json
import numpy as np
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 5b -- Long-term Memory", page_icon="🧠", layout="wide")
st.title("🧠 Phase 5b -- Long-term Memory")
st.caption("Vector store that persists across sessions -- agent remembers customers, preferences, past issues")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

from utils.diagrams import diagram_long_memory
st.image(diagram_long_memory(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is Long-term Memory -- and how does it differ from context-window memory?"):
    st.markdown("""
    **Two types of memory in agentic systems:**

    | Feature | Context Window (Phase 1 — tab 1b) | Vector Store (Phase 5b) |
    |---|---|---|
    | **Scope** | Single session only | Persists across sessions |
    | **Size** | Limited by context window (~1M tokens max) | Unlimited (disk/DB) |
    | **Retrieval** | All history replayed every call | Only relevant memories retrieved |
    | **Cost** | Every token costs on every call | Only retrieved tokens cost |
    | **Search** | No semantic search | Cosine similarity (fuzzy matching) |
    | **Update** | Grows as conversation progresses | Explicit `remember()` calls |
    | **Phase** | Phase 1 (Memory tab) | 5b |

    **The three steps (same as RAG in Phase 5a, but the content is memories, not documents):**

    | Step | What happens |
    |---|---|
    | **Store** | Embed the memory text with `gemini-embedding-001` → store vector + metadata |
    | **Recall** | Embed the query → cosine similarity against all stored memories → return top-K |
    | **Inject** | Retrieved memories injected into the agent's system prompt before each response |

    **Types of things to remember:**
    - Customer preferences ("prefers email, not phone")
    - Past issues ("had fraud case June 2026, resolved")
    - Account facts ("holds NexaSaver + ISA")
    - Interaction summaries ("complained about fees twice")
    - Important dates ("mortgage review due Nov 2026")

    **How it connects to Phase 5a RAG:**
    RAG retrieves from a **static knowledge base** (documents).
    Long-term memory retrieves from a **dynamic, growing store** (past interactions).
    Same technical pattern (embed → cosine → inject) -- different content.
    """)

with st.expander("📐 Core Code Pattern -- Long-term Memory"):
    st.code('''
import numpy as np
from google import genai
from google.genai import types

EMBED_MODEL = "gemini-embedding-001"

class VectorMemoryStore:
    """In-memory vector store for agent memories."""

    def __init__(self):
        self.memories = []  # [{text, embedding, metadata, created_at}]

    def remember(self, text: str, metadata: dict = None) -> str:
        """Embed and store a memory."""
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        self.memories.append({
            "text":       text,
            "embedding":  np.array(result.embeddings[0].values),
            "metadata":   metadata or {},
            "created_at": datetime.now().isoformat(),
        })
        return f"Remembered: {text[:60]}..."

    def recall(self, query: str, top_k: int = 3) -> list:
        """Find most similar memories to the query."""
        if not self.memories:
            return []
        q_result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        q_emb = np.array(q_result.embeddings[0].values)

        scored = []
        for mem in self.memories:
            norm = np.linalg.norm(q_emb) * np.linalg.norm(mem["embedding"])
            score = float(np.dot(q_emb, mem["embedding"]) / norm) if norm > 0 else 0.0
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

# ── Usage in agent ────────────────────────────────────────────────────────────
store = VectorMemoryStore()

# Before responding: recall relevant memories
relevant = store.recall(user_message, top_k=3)
memory_context = "\\n".join(f"- {m['text']}" for _, m in relevant)

response = llm(
    system=f"""You are NexaBank\'s customer advisor.
Customer memory context:
{memory_context}
Use this context to personalise your response.""",
    user=user_message
)

# After responding: store what was learned
store.remember(f"Customer asked about {topic} -- {summary}", metadata={"type": "interaction"})
''', language="python")
    st.markdown("""
**Key insight:** The agent doesn't call `remember()` and `recall()` autonomously --
your pipeline calls them. This is deliberate: memory management is explicit, not hidden.
An agent that auto-stores everything may accumulate noise; selective storage is better.

**Connecting to Phase 5a RAG:**
Both use `gemini-embedding-001` + cosine similarity.
RAG: static documents → knowledge base.
Memory: dynamic interactions → episodic memory.
The retrieval code is identical.

**Production:** Use ChromaDB (local) or Vertex AI Matching Engine (cloud) instead of
this in-memory list. The interface (`remember` / `recall`) stays the same.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# MEMORY STORE (session-scoped)
# ══════════════════════════════════════════════════════════════════════════════

EMBED_MODEL = "gemini-embedding-001"


def embed(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return np.array(result.embeddings[0].values)


def remember(text: str, metadata: dict = None) -> dict:
    emb = embed(text, "RETRIEVAL_DOCUMENT")
    entry = {
        "id":         len(st.session_state.memory_store),
        "text":       text,
        "embedding":  emb,
        "metadata":   metadata or {},
        "created_at": datetime.now().strftime("%H:%M:%S"),
    }
    st.session_state.memory_store.append(entry)
    return entry


def recall(query: str, top_k: int = 3, threshold: float = 0.4) -> list:
    if not st.session_state.memory_store:
        return []
    q_emb = embed(query, "RETRIEVAL_QUERY")
    scored = []
    for mem in st.session_state.memory_store:
        d = mem["embedding"]
        norm = np.linalg.norm(q_emb) * np.linalg.norm(d)
        score = float(np.dot(q_emb, d) / norm) if norm > 0 else 0.0
        scored.append((score, mem))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(s, m) for s, m in scored[:top_k] if s >= threshold]


# Initialise session memory store once
if "memory_store" not in st.session_state:
    st.session_state.memory_store = []
if "mem_agent_history" not in st.session_state:
    st.session_state.mem_agent_history = []


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_a, tab_b = st.tabs([
    "📋 Tab A -- Memory Bank",
    "🔧 Tab B -- Agent with Memory",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB A -- Memory Bank
# ════════════════════════════════════════════════════════════════════════════

with tab_a:
    st.subheader("Tab A -- Memory Bank Operations")
    st.markdown("""
    Manually store facts, then recall them by natural-language query.
    Watch the **similarity scores** to understand which memories are semantically closest.
    """)

    st.markdown(f"**Memory store:** {len(st.session_state.memory_store)} memories stored")

    col1, col2 = st.columns([1, 1])

    # ── Store ──────────────────────────────────────────────────────────────
    with col1:
        st.markdown("#### Store a memory")

        PRESET_MEMORIES = [
            ("Customer preference", "John Smith prefers to be contacted by email not phone, and uses the NexaBank mobile app daily"),
            ("Past fraud case", "John Smith had an unauthorised transaction of GBP 420 in March 2026, resolved within 5 days, full refund issued"),
            ("Account holding", "John Smith holds a NexaSaver account (GBP 8,200 balance) and a NexaFlex ISA (GBP 12,000 balance)"),
            ("Complaint history", "John Smith complained twice about overdraft charges in 2025 -- both escalated to manager, both resolved with partial refund"),
            ("Mortgage note", "John Smith is planning to buy a house in 2027, mortgage pre-assessment done: max loan GBP 210,000"),
            ("Life event", "John Smith mentioned his daughter starts university in September 2026 -- may need to review savings and payments"),
            ("Risk note", "John Smith called about a suspicious email claiming to be NexaBank -- confirmed phishing, educated on security"),
        ]

        if "mem_preset_idx" not in st.session_state:
            st.session_state.mem_preset_idx = 0

        st.markdown("**Preset memories to add:**")
        for i, (label, _) in enumerate(PRESET_MEMORIES):
            if st.button(f"+ {label}", key=f"mem_preset_{i}"):
                st.session_state.mem_preset_idx = i
                st.rerun()

        mem_text = st.text_area(
            "Memory text:",
            value=PRESET_MEMORIES[st.session_state.mem_preset_idx][1],
            height=80,
        )
        mem_type = st.selectbox(
            "Type:",
            ["preference", "past_issue", "account_fact", "complaint", "life_event", "risk_note"],
        )

        if st.button("💾 Store Memory", type="primary", key="store_mem"):
            with st.spinner("Embedding and storing..."):
                entry = remember(mem_text, {"type": mem_type})
            st.success(f"Stored memory #{entry['id']} ({len(entry['embedding'])} dims)")

        if st.button("Clear all memories", key="clear_mem"):
            st.session_state.memory_store = []
            st.rerun()

    # ── Recall ──────────────────────────────────────────────────────────────
    with col2:
        st.markdown("#### Recall by query")

        RECALL_QUERIES = {
            "How to reach this customer?": "contact preference communication channel",
            "Any security issues?": "fraud suspicious phishing security",
            "What accounts does this customer have?": "account balance savings ISA holdings",
            "Has this customer complained before?": "complaint escalation issue problem",
            "Future financial plans?": "mortgage house university savings goal",
        }

        if "recall_q" not in st.session_state:
            st.session_state.recall_q = list(RECALL_QUERIES.keys())[0]

        for label in RECALL_QUERIES:
            if st.button(label, key=f"rq_{label}"):
                st.session_state.recall_q = label
                st.rerun()

        recall_query = st.text_input("Query:", value=st.session_state.recall_q)
        top_k = st.slider("Top K:", 1, 5, 3, key="mem_topk")
        threshold = st.slider("Min similarity:", 0.0, 1.0, 0.4, 0.05, key="mem_thresh")

        if st.button("🔍 Recall", type="primary", key="do_recall"):
            if not st.session_state.memory_store:
                st.warning("No memories stored yet. Add some in the left panel first.")
            else:
                with st.spinner("Embedding query and searching..."):
                    results = recall(recall_query, top_k=top_k, threshold=threshold)

                if not results:
                    st.error("No memories above the similarity threshold.")
                else:
                    st.markdown(f"**Found {len(results)} relevant memories:**")
                    for rank, (score, mem) in enumerate(results, 1):
                        bar_val = min(max(score, 0.0), 1.0)
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"**#{rank}** `[{mem['metadata'].get('type','')}]` {mem['text']}")
                                st.caption(f"Stored at {mem['created_at']}")
                            with c2:
                                st.metric("Similarity", f"{score:.3f}")
                                st.progress(bar_val)

    # ── All memories ─────────────────────────────────────────────────────────
    if st.session_state.memory_store:
        with st.expander(f"🗃️ All stored memories ({len(st.session_state.memory_store)} total)"):
            for mem in st.session_state.memory_store:
                st.markdown(
                    f"`#{mem['id']}` `[{mem['metadata'].get('type','')}]` "
                    f"**{mem['text'][:80]}...**  _{mem['created_at']}_"
                )
                st.caption(f"Vector: [{', '.join(f'{v:.4f}' for v in mem['embedding'][:5])}, ...] ({len(mem['embedding'])} dims)")


# ════════════════════════════════════════════════════════════════════════════
# TAB B -- Agent with Memory
# ════════════════════════════════════════════════════════════════════════════

with tab_b:
    st.subheader("Tab B -- NexaBank Agent with Customer Memory")
    st.markdown("""
    A NexaBank advisor that:
    1. **Recalls** relevant memories before every response
    2. **Stores** a summary of each interaction after responding
    3. Becomes more personalised with every turn

    Switch between **no-memory mode** and **memory mode** to see the difference.
    """)

    col_cfg, col_chat = st.columns([1, 2])

    with col_cfg:
        st.markdown("**Configuration:**")
        use_memory = st.toggle("Enable long-term memory", value=True)
        mem_topk_b = st.slider("Memories to recall per turn:", 1, 5, 3, key="mem_topk_b")
        auto_store = st.toggle("Auto-store interaction summaries", value=True)

        st.markdown("**Quick-add customer background:**")
        BACKGROUND = [
            "John Smith has NexaSaver (GBP 8,200) and ISA (GBP 12,000)",
            "John prefers email contact and uses the mobile app daily",
            "John had a fraud case in March 2026, resolved with full refund",
            "John is planning to buy a house in 2027, max mortgage GBP 210,000",
            "John complained about overdraft fees twice in 2025",
        ]
        for bg in BACKGROUND:
            if st.button(f"Store: {bg[:45]}...", key=f"bg_{bg[:20]}"):
                with st.spinner("Storing..."):
                    remember(bg, {"type": "background", "customer": "John Smith"})
                st.success("Stored.")

        st.markdown("---")
        st.metric("Memories in store", len(st.session_state.memory_store))

        if st.button("Clear chat history", key="clear_chat_b"):
            st.session_state.mem_agent_history = []
            st.rerun()

    with col_chat:
        st.markdown("**Conversation:**")

        # Display conversation history
        for turn in st.session_state.mem_agent_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])
                if turn.get("memories_used"):
                    with st.expander("🧠 Memories recalled for this response"):
                        for score, text in turn["memories_used"]:
                            st.caption(f"Score {score:.3f}: {text}")

        # User input
        user_msg = st.chat_input("Ask NexaBank advisor...")

        if user_msg:
            st.session_state.mem_agent_history.append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)

            # ── Recall phase ──────────────────────────────────────────────
            memories_used = []
            memory_context = ""
            if use_memory and st.session_state.memory_store:
                with st.spinner("Recalling relevant memories..."):
                    recalled = recall(user_msg, top_k=mem_topk_b, threshold=0.35)
                memories_used = [(s, m["text"]) for s, m in recalled]
                if recalled:
                    memory_context = "\n\nCustomer memory:\n" + "\n".join(
                        f"- [{m['metadata'].get('type','')}] {m['text']}"
                        for _, m in recalled
                    )

            # ── Generate response ──────────────────────────────────────────
            system = (
                "You are NexaBank's personalised customer advisor. "
                "Be warm, specific, and reference what you know about the customer. "
                "Keep responses under 120 words."
                + memory_context
            )
            history_for_llm = [
                {"role": "model" if t["role"] == "assistant" else t["role"],
                 "parts": [{"text": t["content"]}]}
                for t in st.session_state.mem_agent_history[:-1]
            ]

            with st.spinner("Generating response..."):
                resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=[*history_for_llm,
                               {"role": "user", "parts": [{"text": user_msg}]}],
                    config=types.GenerateContentConfig(system_instruction=system),
                )
            agent_reply = resp.text.strip()

            with st.chat_message("assistant"):
                st.markdown(agent_reply)
                if memories_used:
                    with st.expander(f"🧠 {len(memories_used)} memories recalled"):
                        for score, text in memories_used:
                            st.caption(f"Score {score:.3f}: {text}")
                elif use_memory:
                    st.caption("No relevant memories retrieved for this query.")

            # ── Store summary ──────────────────────────────────────────────
            if auto_store and use_memory:
                summary = f"Customer asked: {user_msg[:60]} -- Advisor: {agent_reply[:60]}"
                with st.spinner("Storing interaction summary..."):
                    remember(summary, {"type": "interaction", "turn": len(st.session_state.mem_agent_history)})

            st.session_state.mem_agent_history.append({
                "role":         "assistant",
                "content":      agent_reply,
                "memories_used": memories_used,
            })
            st.rerun()

    # ── Trace ─────────────────────────────────────────────────────────────
    if st.session_state.mem_agent_history:
        with st.expander("🔬 Execution Trace -- memory lifecycle per turn"):
            st.markdown("""
| Step | What happens | Code |
|---|---|---|
| **Recall** | Query embedded → cosine search → top-K memories | `recall(user_msg, top_k=3)` |
| **Inject** | Retrieved memories added to system prompt | `system += memory_context` |
| **Generate** | LLM sees question + memory context | `generate_content(...)` |
| **Store** | Interaction summary embedded + stored | `remember(summary, metadata)` |
""")
            st.markdown(f"**Turns in conversation:** {len([t for t in st.session_state.mem_agent_history if t['role']=='user'])}")
            st.markdown(f"**Total memories:** {len(st.session_state.memory_store)}")

st.markdown("---")
st.markdown("### What's next -> Phase 6a: Multi-Agent")
st.markdown(
    "Phase 5 (Knowledge & Memory) is complete. Phase 6 introduces agent collaboration. "
    "**6a Multi-Agent:** a root orchestrator routes queries to specialist sub-agents -- "
    "each a full agent with its own tools, system prompt, and reasoning loop. "
    "Andrew Ng Pattern 4."
)
