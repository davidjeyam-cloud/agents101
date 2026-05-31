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

from utils.diagrams import diagram_langchain
from utils.llm import MODEL, _client

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("⛓️ 10d — LangChain LCEL")
st.caption(
    "Phase 1 memory, Phase 2a chaining, and Phase 5 RAG — reimplemented as LCEL pipes. "
    "prompt | llm | parser is Prompt Chaining (Phase 2a) as composable syntax sugar."
)

# ── Diagram ───────────────────────────────────────────────────────────────────
st.image(diagram_langchain(),
         caption="LangChain LCEL maps each component back to a pattern you built in Phases 1, 2, and 5",
         use_column_width=True)

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

tab_lcel, tab_memory, tab_rag = st.tabs([
    "LCEL Chain vs Phase 1a",
    "Memory Chain vs Phase 1b",
    "RAG Chain vs Phase 5a",
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
| Manual function call chain | `prompt \| llm \| parser` |

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

st.markdown("---")
st.markdown("### What's next → Phase 10e — Google ADK")
st.markdown(
    "LangGraph covered ReAct and single-agent patterns. "
    "Google ADK covers multi-agent orchestration with sequential, parallel, and loop sub-agents — "
    "directly bridging Phase 6 (Multi-Agent) to a production framework."
)
