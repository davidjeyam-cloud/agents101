"""
Phase 5a — RAG Agent (Retrieval-Augmented Generation)
Agent searches a knowledge base before answering — grounded in real documents.
Pattern: Retrieve (embed + cosine search) → Augment (inject context) → Generate (LLM)
"""

import streamlit as st
import os
import json
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.llm import _call, MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 5a — RAG Agent", page_icon="📚", layout="wide")
st.title("📚 Phase 5a — RAG Agent")
st.caption("Retrieval-Augmented Generation — agent searches a knowledge base before answering")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Diagram ────────────────────────────────────────────────────────────────────
from utils.diagrams import diagram_3d
st.image(diagram_3d(), use_container_width=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is RAG — and why does every production agent need it?"):
    st.markdown("""
    > *"Retrieval-Augmented Generation grounds the model's responses in specific,
    > up-to-date information from your own documents — not just training data."*

    **The three steps (R-A-G):**

    | Step | What happens | Tech used |
    |---|---|---|
    | **Retrieve** | Embed the query → cosine search → find top-K similar chunks | `gemini-embedding-001` (3072-dim) |
    | **Augment** | Inject retrieved chunks into the prompt as context | Prompt engineering |
    | **Generate** | LLM answers using the context — not just training data | `gemini-2.5-flash` |

    **Why agents need RAG:**
    - LLMs know general knowledge — not YOUR organisation's specific policies
    - Training data is static — RAG gives access to current documents
    - Without RAG: model may hallucinate specific figures, dates, or policies
    - With RAG: model cites the actual retrieved document

    **Basic RAG vs Agentic RAG:**

    | | Basic RAG (workflow) | Agentic RAG (this demo) |
    |---|---|---|
    | Who triggers retrieval? | Always — hardcoded | Agent decides — may skip if confident |
    | What query? | User's exact words | Agent may reformulate for better retrieval |
    | How many times? | Once | Agent may search multiple times with different queries |
    | Is it an agent? | ❌ Workflow | ✅ Agent |
    """)

with st.expander("📐 Core Code Pattern — RAG Agent"):
    st.code('''
# ── STEP 1: EMBED DOCUMENTS (once at startup) ────────────────────────────────
@st.cache_resource
def build_knowledge_base():
    for doc in DOCUMENTS:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=doc["content"],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        doc["embedding"] = result.embeddings[0].values
    return DOCUMENTS

# ── STEP 2: RETRIEVAL TOOL (agent calls this) ────────────────────────────────
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """Search NexaBank knowledge base. Returns top matching policy chunks."""
    # Embed the query
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    q_emb = np.array(result.embeddings[0].values)

    # Cosine similarity against all documents
    scores = [np.dot(q_emb, np.array(doc["embedding"])) /
              (np.linalg.norm(q_emb) * np.linalg.norm(doc["embedding"]))
              for doc in kb]

    top_indices = np.argsort(scores)[::-1][:top_k]
    chunks = [f"[{kb[i][\'title\']}] {kb[i][\'content\']}" for i in top_indices]
    return "\\n\\n".join(chunks)

# ── STEP 3: AGENTIC RAG LOOP ─────────────────────────────────────────────────
# Agent decides when to search, what to search for, and when it has enough
convo = client.chats.create(model=MODEL, config=GenerateContentConfig(
    tools=[search_knowledge_base],           # retrieval is a TOOL
    automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
    system_instruction="Always search the knowledge base before answering...",
))
response = convo.send_message(user_question)

# Handle tool calls (agent may search multiple times)
while response.function_calls:
    fc     = response.function_calls[0]
    result = search_knowledge_base(**dict(fc.args))
    response = convo.send_message(
        Part.from_function_response(name=fc.name, response={"result": result})
    )

grounded_answer = response.text   # answer cites retrieved content
''', language="python")
    st.markdown("""
**What makes this Agentic RAG (not basic RAG):**
- `search_knowledge_base` is a **tool** — the agent DECIDES whether to call it
- Agent may search with **reformulated queries** — not just the user's words
- Agent may search **multiple times** with different queries
- Agent chooses when it has **enough context** to answer

**Key component:** `gemini-embedding-001` converts text to a 3072-dimension vector.
Cosine similarity finds semantically similar chunks — not just keyword matches.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# NexaBank Knowledge Base
# ══════════════════════════════════════════════════════════════════════════════

DOCUMENTS = [
    {
        "id": "refund_policy",
        "title": "Refund & Dispute Policy",
        "content": (
            "NexaBank Refund Policy: Customers may request a full refund within 30 days of purchase "
            "for any NexaBank product or service. Refunds up to £500 are processed automatically within "
            "3-5 working days. Refunds above £500 require manager approval and take 5-10 working days. "
            "For disputed transactions, customers must report within 120 days. Refunds are credited "
            "to the original payment method. International refunds may take up to 15 working days "
            "due to currency conversion processing."
        ),
    },
    {
        "id": "account_types",
        "title": "Account Types & Features",
        "content": (
            "NexaBank offers three main account types: (1) NexaCurrent — everyday account with "
            "no monthly fee, contactless card, and 0.1% cashback on purchases. Overdraft available "
            "up to £2,000 subject to credit check. (2) NexaSaver — high-interest savings account "
            "paying 4.75% AER (variable), minimum balance £100, no penalty for withdrawal. "
            "(3) NexaFlex ISA — cash ISA paying 4.2% AER tax-free, annual allowance £20,000, "
            "transfers from other ISAs accepted. All accounts include online and mobile banking."
        ),
    },
    {
        "id": "international_payments",
        "title": "International Payments & SWIFT",
        "content": (
            "NexaBank international transfers: SWIFT payments available to 180+ countries. "
            "Fee structure: £5 for EU/EEA (SEPA), £15 for US/Canada/Australia, £25 for all other countries. "
            "Exchange rate: mid-market rate + 0.5% margin. Transfers typically complete in 1-3 business days "
            "for SEPA, 2-5 days for SWIFT. Maximum single transfer: £100,000 (higher limits require "
            "Enhanced Due Diligence). IBAN required for European transfers. Payments above £10,000 "
            "may be held for AML review (up to 2 business days)."
        ),
    },
    {
        "id": "fraud_security",
        "title": "Fraud Prevention & Security",
        "content": (
            "NexaBank fraud reporting: Report suspected fraud immediately via: (1) In-app — tap 'Report Fraud' "
            "in Security settings. (2) Phone — 0800 123 4567 (24/7, free). (3) Secure message in online banking. "
            "We will never ask for your PIN, full password, or to move money to a 'safe account'. "
            "Authorised Push Payment (APP) fraud: if tricked into sending money, report within 13 months "
            "for potential reimbursement under the PSR 2023 mandatory reimbursement scheme (up to £415,000). "
            "Account is frozen immediately on fraud report. Replacement card issued within 3-5 working days."
        ),
    },
    {
        "id": "overdraft_policy",
        "title": "Overdraft Terms & Charges",
        "content": (
            "NexaBank NexaCurrent overdraft: Arranged overdraft up to £2,000 available subject to credit check. "
            "Interest rate: 39.9% EAR (representative). £1 daily buffer — no charges for overdraft up to £1. "
            "No fees for arranged overdraft, only interest. Unarranged overdraft: £5 per day maximum "
            "(charged if balance is negative without arrangement). Overdraft review every 12 months. "
            "To apply or increase limit: use app or call 0800 123 4568. Overdraft can be refused or "
            "reduced if financial circumstances change."
        ),
    },
    {
        "id": "mortgage_products",
        "title": "Mortgage Products",
        "content": (
            "NexaBank mortgage range: Fixed-rate mortgages available at 2-year fix (4.89% APRC), "
            "5-year fix (4.65% APRC), and 10-year fix (4.99% APRC). Variable rate tracker: Bank of England "
            "base rate + 0.75%. Maximum LTV: 95% (first-time buyers), 90% (remortgage), 75% (buy-to-let). "
            "Minimum loan: £50,000. Maximum loan: £2,000,000 (subject to income assessment). "
            "Early repayment charge: 3% in year 1, 2% in year 2 (for 2-year fix). Mortgage holiday: "
            "up to 3 months allowed once per mortgage term. Application: online or with a mortgage advisor."
        ),
    },
    {
        "id": "account_closure",
        "title": "Account Closure Process",
        "content": (
            "NexaBank account closure: To close your account, you must: (1) Ensure balance is zero or "
            "transfer remaining funds. (2) Cancel all standing orders and direct debits. (3) Request closure "
            "via app, online banking, or branch. Closure is processed within 5 working days. "
            "Customers with accounts for 5+ years are offered a retention call with a specialist "
            "who can offer tailored rates or products. Final statement issued within 10 working days. "
            "Closure cannot be reversed after processing. Joint accounts require both account holders' consent."
        ),
    },
    {
        "id": "mobile_banking",
        "title": "Mobile Banking App",
        "content": (
            "NexaBank mobile app: Available on iOS 14+ and Android 9+. Features: real-time notifications, "
            "instant payments (Faster Payments up to £250,000), card freeze/unfreeze, spending analytics, "
            "budget categories, and biometric login. Mobile cheque deposit: up to £500 per cheque, "
            "£1,000 per day. App-exclusive: savings round-ups, cashback offers, and NexaRewards points. "
            "Security: 256-bit encryption, device fingerprinting, and automatic logout after 5 minutes "
            "of inactivity. App support: in-app chat 8am-10pm, or call 0800 123 4567."
        ),
    },
    {
        "id": "aml_kyc",
        "title": "AML / KYC Requirements",
        "content": (
            "NexaBank AML and KYC: All customers must complete identity verification (KYC) before account "
            "activation. Required documents: valid passport or driving licence + proof of address (utility "
            "bill or bank statement, not older than 3 months). Enhanced Due Diligence (EDD) triggered for: "
            "transactions above £10,000, PEPs (Politically Exposed Persons), high-risk countries, "
            "and unusual transaction patterns. Suspicious Activity Reports (SARs) filed with the NCA "
            "as required by the Proceeds of Crime Act 2002. Account may be suspended during AML review. "
            "Customers will NOT be told if a SAR has been filed (tipping off offence)."
        ),
    },
    {
        "id": "complaints",
        "title": "Complaints & Escalation Process",
        "content": (
            "NexaBank complaints procedure: Step 1 — Contact us: phone 0800 123 4567, secure message, "
            "or branch. We aim to resolve within 3 business days. Step 2 — If unresolved within 8 weeks, "
            "you may escalate to the Financial Ombudsman Service (FOS) free of charge. FOS contact: "
            "www.financial-ombudsman.org.uk or 0800 023 4567. Step 3 — Regulatory complaints: "
            "FCA can be contacted at www.fca.org.uk/consumers. Final Response Letter issued within "
            "8 weeks in all cases. Compensation for distress: up to £200 at NexaBank's discretion. "
            "FOS awards: up to £375,000 for financial losses."
        ),
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# Build knowledge base — embed documents once, cache
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Building knowledge base — embedding documents…")
def build_kb(_client):
    """Embed all documents and return KB. Cached across reruns."""
    kb = []
    for doc in DOCUMENTS:
        try:
            result = _client.models.embed_content(
                model="gemini-embedding-001",
                contents=doc["content"],
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            emb = np.array(result.embeddings[0].values)
        except Exception:
            emb = np.zeros(3072)
        kb.append({**doc, "embedding": emb})
    return kb

kb = build_kb(client)

# ── Retrieval function (exposed as agent tool) ─────────────────────────────────

def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """
    Search NexaBank's knowledge base for relevant policy or product information.

    Args:
        query: Natural language search query about NexaBank products or policies
        top_k: Number of most relevant documents to return (default 3)
    """
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        q_emb = np.array(result.embeddings[0].values)
    except Exception:
        return "Knowledge base search unavailable."

    scores = []
    for doc in kb:
        d_emb = doc["embedding"]
        norm  = np.linalg.norm(q_emb) * np.linalg.norm(d_emb)
        score = float(np.dot(q_emb, d_emb) / norm) if norm > 0 else 0.0
        scores.append((score, doc))

    top = sorted(scores, key=lambda x: x[0], reverse=True)[:int(top_k)]

    chunks = []
    for score, doc in top:
        chunks.append(
            f"[Source: {doc['title']} | Relevance: {score:.2f}]\n{doc['content']}"
        )
    return "\n\n---\n\n".join(chunks)


def get_document(doc_id: str) -> str:
    """
    Retrieve the full content of a specific NexaBank knowledge base document.

    Args:
        doc_id: Document ID (e.g. refund_policy, account_types, fraud_security)
    """
    for doc in kb:
        if doc["id"] == doc_id:
            return f"[{doc['title']}]\n{doc['content']}"
    return f"Document '{doc_id}' not found. Available IDs: {', '.join(d['id'] for d in kb)}"


def search_with_trace(query: str, top_k: int = 3) -> dict:
    """
    Same retrieval logic as search_knowledge_base, but returns full trace data
    for the Query Evolution display — vector snippet, all scores, top-K chunks.
    """
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        q_emb = np.array(result.embeddings[0].values)
    except Exception:
        return {}

    scored = []
    for doc in kb:
        d_emb = doc["embedding"]
        norm  = np.linalg.norm(q_emb) * np.linalg.norm(d_emb)
        score = float(np.dot(q_emb, d_emb) / norm) if norm > 0 else 0.0
        scored.append({
            "id":      doc["id"],
            "title":   doc["title"],
            "content": doc["content"],
            "score":   score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_ids = {s["id"] for s in scored[:top_k]}

    return {
        "query":          query,
        "vector_snippet": q_emb[:8].tolist(),
        "vector_dim":     len(q_emb),
        "all_scores":     scored,
        "top_k":          scored[:top_k],
        "top_ids":        top_ids,
    }


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"**Knowledge base:** {len(kb)} NexaBank policy documents embedded with `gemini-embedding-001` (3072-dim vectors)")

with st.expander("📄 View Knowledge Base documents"):
    for doc in DOCUMENTS:
        st.markdown(f"**{doc['title']}** `[{doc['id']}]`")
        st.caption(doc["content"][:120] + "…")

st.markdown("---")

EXAMPLES = {
    "Refund timeline":
        "I requested a £650 refund last week. How long will it take to arrive and what is the process?",
    "Best savings rate":
        "I have £5,000 to save. What's the best interest rate NexaBank offers and are there any restrictions?",
    "Report fraud":
        "Someone has made unauthorised purchases on my card. What should I do right now and will I get my money back?",
    "International transfer":
        "I need to send £8,000 to my family in Australia. What are the fees and how long will it take?",
    "Complaint process":
        "NexaBank hasn't resolved my issue in 6 weeks. What are my options and can I go to the ombudsman?",
    "❓ Outside KB (tests hallucination)":
        "What is NexaBank's current Bitcoin trading fee and which cryptocurrencies do you support?",
}

if "sel_3d" not in st.session_state:
    st.session_state.sel_3d = EXAMPLES["Refund timeline"]

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("**Example questions:**")
    for label, text in EXAMPLES.items():
        if st.button(label, key=f"ex3d_{label}"):
            st.session_state.sel_3d = text
            st.rerun()
with col1:
    question = st.text_area(
        "Customer question:",
        value=st.session_state.sel_3d,
        height=100,
    )

show_without = st.checkbox("Also show answer WITHOUT RAG (see the difference)", value=True)

st.markdown("---")

if st.button("▶  Run RAG Agent + Query X-Ray", type="primary", key="run_3d"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    # ══════════════════════════════════════════════════════════════════════════
    # WITHOUT RAG (baseline) — optional
    # ══════════════════════════════════════════════════════════════════════════

    if show_without:
        with st.container(border=True):
            st.markdown("#### ❌ Without RAG — LLM from training data only")
            st.caption("No knowledge base consulted. Model answers from general training.")
            with st.spinner("LLM answering without RAG…"):
                no_rag = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "You are a banking assistant. Answer the question as best you can. "
                            "If you don't know specific details, say so."
                        )
                    ),
                )
            st.warning(no_rag.text)
            st.caption("⚠️ Response may be vague, incorrect, or hallucinated — no domain knowledge injected.")

        st.markdown("<div style='text-align:center;font-size:1.5rem;margin:6px 0'>↕ compare with RAG below</div>",
                    unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # WITH RAG AGENT — run first, collect all traces, then display pipeline
    # ══════════════════════════════════════════════════════════════════════════

    SYSTEM = (
        "You are NexaBank's AI assistant. ALWAYS search the knowledge base "
        "before answering any question about NexaBank products, policies, rates, "
        "or procedures. Never answer from training data alone — use the retrieved "
        "content to give accurate, specific answers. If the knowledge base doesn't "
        "contain relevant information, say so honestly."
    )

    config = types.GenerateContentConfig(
        tools=[search_knowledge_base, get_document],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        system_instruction=SYSTEM,
    )
    convo = client.chats.create(model=MODEL, config=config)

    with st.spinner("Agent running — collecting retrieval trace…"):
        response = _call(convo.send_message, question)

    # ── Tool call loop — collect full trace ───────────────────────────────────
    retrieval_traces = []   # [{tool, args, raw_result, xray}]
    MAX = 4

    for _ in range(MAX):
        if not response.function_calls:
            break
        fc   = response.function_calls[0]
        args = dict(fc.args)

        raw_result = (search_knowledge_base(**args) if fc.name == "search_knowledge_base"
                      else get_document(**args))

        xray = None
        if fc.name == "search_knowledge_base":
            with st.spinner('Building X-Ray trace for search query...'):
                xray = search_with_trace(
                    query=args.get("query", ""),
                    top_k=int(args.get("top_k", 3)),
                )

        retrieval_traces.append({
            "tool":       fc.name,
            "args":       args,
            "raw_result": raw_result,
            "xray":       xray,
        })

        response = _call(
            convo.send_message,
            types.Part.from_function_response(
                name=fc.name, response={"result": raw_result}
            ),
        )

    final_answer = response.text

    # ══════════════════════════════════════════════════════════════════════════
    # DISPLAY: Query Evolution Pipeline
    # ══════════════════════════════════════════════════════════════════════════

    st.markdown("---")
    st.markdown("## 🔬 Query Evolution Pipeline — how your question became an answer")
    st.caption(
        "Every transformation shown: raw question → 3072-dim vector → cosine scores → "
        "retrieved chunks → augmented prompt → grounded response"
    )

    if not retrieval_traces:
        st.info("Agent answered without searching the knowledge base.")
    else:
        for search_num, trace in enumerate(retrieval_traces, 1):
            xray = trace["xray"]
            if not xray:
                continue

            if len(retrieval_traces) > 1:
                st.markdown(f"### Search call {search_num} of {len(retrieval_traces)}")

            # ── ① EMBED ──────────────────────────────────────────────────────
            with st.container(border=True):
                st.markdown("#### ① EMBED — natural language → numeric vector")
                st.caption(
                    "gemini-embedding-001 converts every word's meaning into numbers. "
                    "Semantically similar phrases get similar vectors — that's what enables fuzzy matching."
                )
                col_q, col_v = st.columns([1, 1])
                with col_q:
                    st.markdown("**Agent's search query (input):**")
                    st.info(f'"{xray["query"]}"')
                    if xray["query"] != question:
                        st.caption(
                            "⚡ Agent reformulated the query — different from what you typed. "
                            "This is Agentic RAG in action."
                        )
                    else:
                        st.caption("Agent used your original question as-is.")
                with col_v:
                    st.markdown(f"**Output: {xray['vector_dim']}-dimensional vector (first 8 values):**")
                    snippet = ", ".join(f"{v:+.4f}" for v in xray["vector_snippet"])
                    st.code(f"[{snippet}, ...]", language="text")
                    st.caption(
                        f"3072 numbers encode the full semantic meaning. "
                        "Each document in the KB was pre-embedded the same way at startup."
                    )

            st.markdown(
                "<div style='text-align:center;font-size:1.2rem;margin:4px 0'>↓ compare query vector against all document vectors</div>",
                unsafe_allow_html=True,
            )

            # ── ② COSINE SIMILARITY ──────────────────────────────────────────
            with st.container(border=True):
                st.markdown(f"#### ② COSINE SIMILARITY — query vs all {len(xray['all_scores'])} documents")
                st.caption(
                    "Formula: `cos(θ) = (query · doc) / (|query| × |doc|)`. "
                    "Result is 0–1: 1.0 = identical meaning, 0.0 = unrelated. "
                    "Pure Python/NumPy — no external search engine."
                )
                st.code(
                    "score = np.dot(q_emb, d_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(d_emb))",
                    language="python",
                )
                st.markdown("")

                for doc_s in xray["all_scores"]:
                    is_retrieved = doc_s["id"] in xray["top_ids"]
                    score        = doc_s["score"]
                    score_clamped = max(0.0, min(1.0, score))

                    col_icon, col_title, col_score, col_bar = st.columns([0.05, 0.45, 0.1, 0.4])
                    with col_icon:
                        st.markdown("🟢" if is_retrieved else "⚪")
                    with col_title:
                        label = f"**{doc_s['title']}**" if is_retrieved else doc_s["title"]
                        suffix = "  ← **retrieved**" if is_retrieved else ""
                        st.markdown(label + suffix)
                    with col_score:
                        st.markdown(f"`{score:.3f}`")
                    with col_bar:
                        st.progress(score_clamped)

                # ── Documents narrowed summary ────────────────────────────────
                max_score = xray["all_scores"][0]["score"] if xray["all_scores"] else 0.0
                RELEVANCE_THRESHOLD = 0.50
                retrieved_docs  = [d for d in xray["all_scores"] if d["id"] in xray["top_ids"]]
                excluded_docs   = [d for d in xray["all_scores"] if d["id"] not in xray["top_ids"]]

                st.markdown("---")
                st.markdown("**📋 Narrowing decision — which documents were selected:**")

                if max_score < RELEVANCE_THRESHOLD:
                    st.error(
                        f"**No relevant policy found in the knowledge base.**\n\n"
                        f"Best match was **{xray['all_scores'][0]['title']}** "
                        f"with a similarity score of **{max_score:.3f}** — "
                        f"below the meaningful threshold of {RELEVANCE_THRESHOLD}.\n\n"
                        "The LLM will acknowledge it has no specific NexaBank policy on this topic "
                        "and should not hallucinate an answer."
                    )
                    st.caption(
                        "Tip: try the 'Outside KB' example question (Bitcoin) to see this path clearly."
                    )
                else:
                    col_sel, col_excl = st.columns(2)
                    with col_sel:
                        st.markdown(f"**✅ RETRIEVED — {len(retrieved_docs)} doc(s) injected into prompt:**")
                        for d in retrieved_docs:
                            st.markdown(f"- **{d['title']}** `{d['score']:.3f}`")
                    with col_excl:
                        st.markdown(f"**⬜ NOT RETRIEVED — {len(excluded_docs)} doc(s) excluded (lower score):**")
                        for d in excluded_docs:
                            st.markdown(f"- {d['title']} `{d['score']:.3f}`")

            st.markdown(
                "<div style='text-align:center;font-size:1.2rem;margin:4px 0'>↓ top-K chunks passed to the LLM</div>",
                unsafe_allow_html=True,
            )

            # ── ③ RETRIEVED CHUNKS ───────────────────────────────────────────
            with st.container(border=True):
                if max_score < RELEVANCE_THRESHOLD:
                    st.markdown(f"#### ③ RETRIEVED CHUNKS — top {len(xray['top_k'])} documents (low relevance)")
                    st.warning(
                        "These are the closest matches found, but none crossed the relevance threshold. "
                        "They are still passed to the LLM, which should recognise they don't answer the question."
                    )
                else:
                    st.markdown(f"#### ③ RETRIEVED CHUNKS — top {len(xray['top_k'])} documents")
                st.caption(
                    "These are the exact text passages pulled from the knowledge base. "
                    "They become the context window the LLM reads when generating its answer."
                )
                for j, chunk in enumerate(xray["top_k"], 1):
                    with st.expander(
                        f"Chunk {j} — {chunk['title']}  (similarity: {chunk['score']:.3f})",
                        expanded=(j == 1),
                    ):
                        st.markdown(f"**Source doc ID:** `{chunk['id']}`")
                        st.markdown(chunk["content"])

            st.markdown(
                "<div style='text-align:center;font-size:1.2rem;margin:4px 0'>↓ inject chunks into prompt</div>",
                unsafe_allow_html=True,
            )

            # ── ④ AUGMENTED PROMPT ───────────────────────────────────────────
            with st.container(border=True):
                st.markdown("#### ④ AUGMENTED PROMPT — what the LLM actually receives")
                st.caption(
                    "The retrieved chunks are injected into the conversation as a tool result. "
                    "The LLM now has the user's question AND the relevant policy text in its context window."
                )

                col_before, col_after = st.columns(2)
                with col_before:
                    st.markdown("**Before augmentation — raw question only:**")
                    st.warning(f'"{xray["query"]}"')
                    st.caption("~10–20 tokens. LLM has no NexaBank-specific knowledge.")
                with col_after:
                    total_chars = sum(len(c["content"]) for c in xray["top_k"])
                    st.markdown(f"**After augmentation — question + {len(xray['top_k'])} chunks:**")
                    st.success(
                        f'"{xray["query"]}"\n\n'
                        f'+ [{xray["top_k"][0]["title"]}] {xray["top_k"][0]["content"][:80]}…\n'
                        f'+ [{xray["top_k"][1]["title"]}] {xray["top_k"][1]["content"][:60]}…'
                        if len(xray["top_k"]) > 1 else
                        f'"{xray["query"]}"\n\n'
                        f'+ [{xray["top_k"][0]["title"]}] {xray["top_k"][0]["content"][:120]}…'
                    )
                    st.caption(f"~{total_chars // 4} extra tokens of domain knowledge injected.")

                # Full augmented prompt in expander
                full_context = "\n\n---\n\n".join(
                    f"[Source: {c['title']} | Relevance: {c['score']:.3f}]\n{c['content']}"
                    for c in xray["top_k"]
                )
                full_prompt = (
                    f"SYSTEM:\n{SYSTEM}\n\n"
                    f"USER QUESTION:\n{xray['query']}\n\n"
                    f"RETRIEVED CONTEXT (injected via tool result):\n{full_context}"
                )
                with st.expander("📄 Full augmented prompt — exactly what the LLM receives"):
                    st.code(full_prompt, language="text")

    st.markdown(
        "<div style='text-align:center;font-size:1.5rem;margin:6px 0'>↓ LLM generates grounded answer</div>",
        unsafe_allow_html=True,
    )

    # ── ⑤ GROUNDED RESPONSE ──────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("#### ⑤ GROUNDED RESPONSE — answer citing retrieved content")
        st.caption(
            "The LLM reads the injected context and generates a response. "
            "Specific figures, timelines, and policies come from the retrieved documents — not hallucination."
        )
        st.success(final_answer)

    # ── Summary ───────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 What just happened — RAG breakdown with real values"):
        # Build real-value summary from collected traces
        search_xrays = [t["xray"] for t in retrieval_traces if t["xray"]]
        if search_xrays:
            last_xray   = search_xrays[-1]
            top_doc     = last_xray["top_k"][0] if last_xray["top_k"] else None
            all_queries = [x["query"] for x in search_xrays]
            total_chars = sum(len(c["content"]) for x in search_xrays for c in x["top_k"])
            found_relevant = last_xray["all_scores"][0]["score"] >= 0.50 if last_xray["all_scores"] else False

            retrieved_titles = ", ".join(
                f'"{c["title"]}" ({c["score"]:.3f})'
                for c in last_xray["top_k"]
            )
            excluded_titles = ", ".join(
                d["title"]
                for d in last_xray["all_scores"]
                if d["id"] not in last_xray["top_ids"]
            )
            query_display = all_queries[0] if len(all_queries) == 1 else " → ".join(f'"{q}"' for q in all_queries)

            st.markdown(f"""
| Step | What ran | Actual output this run |
|---|---|---|
| **① Embed** | `gemini-embedding-001` → {last_xray['vector_dim']}-dim vector | First 3 values: `{last_xray['vector_snippet'][0]:+.4f}`, `{last_xray['vector_snippet'][1]:+.4f}`, `{last_xray['vector_snippet'][2]:+.4f}` |
| **② Cosine search** | Scored all {len(last_xray['all_scores'])} KB docs | Query used: *"{all_queries[0][:70]}{'...' if len(all_queries[0])>70 else ''}"* |
| **Top match** | Highest scoring document | **{top_doc['title'] if top_doc else 'none'}** — score `{top_doc['score']:.3f}` {"✅ relevant" if found_relevant else "❌ below threshold"} |
| **③ Retrieved** | {len(last_xray['top_k'])} doc(s) selected | {retrieved_titles} |
| **Excluded** | {len(last_xray['all_scores']) - len(last_xray['top_k'])} doc(s) not used | {excluded_titles[:120]}{'...' if len(excluded_titles) > 120 else ''} |
| **④ Augment** | Context injected into prompt | ~{total_chars // 4} tokens of policy text added |
| **⑤ Generate** | `gemini-2.5-flash` answered | {"Grounded answer using retrieved docs" if found_relevant else "Agent acknowledged no specific policy found"} |
| **Agent searches** | {len(retrieval_traces)} call(s) total | {query_display[:100]} |
""")
        else:
            st.markdown(f"""
| Step | What ran | How |
|---|---|---|
| **Agent** | No knowledge base search made | Agent answered from conversation context directly |
| **Generate** | `gemini-2.5-flash` answered | No RAG augmentation applied this run |
""")

        st.markdown("""
**Without RAG:** LLM guesses NexaBank-specific rates, fees, and timelines from training data.
**With RAG:** LLM answers using the actual policy document — specific and accurate.

**Why Agentic RAG > Basic RAG:**
- *Whether* to search — agent decides (may skip if confident from context)
- *What* to search — agent may reformulate query for better retrieval
- *How many times* — agent may search again with different terms

**Production stack:** Replace in-memory cosine search with:
- **Vertex AI Search** (Google) — fully managed RAG
- **ChromaDB** — open-source vector store
- **Pinecone / Weaviate** — managed vector databases
- **AlloyDB / BigQuery** — with vector search extensions
""")

    st.markdown("---")
    st.markdown("### What's next → Phase 4c: LLM-as-Judge")
    st.markdown(
        "A separate LLM evaluates the RAG agent's response for accuracy, completeness, "
        "and grounding — acting as an independent quality gate before the user sees it."
    )
