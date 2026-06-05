"""
Phase 8d — Multimodal Agents
Agents that perceive images alongside text — vision RAG, document parsing,
chart reading, screenshot analysis. Uses Gemini's native multimodal input.
"""
import os, io, base64, json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils.llm import MODEL, _call
from utils.styles import phase_header, ACCENT_COMPLETE
from utils.trace import render_trace

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Phase 8d — Multimodal Agents", page_icon="👁️", layout="wide")

if not api_key:
    st.error("GEMINI_API_KEY not found."); st.stop()

client = genai.Client(api_key=api_key)

st.markdown(phase_header(
    "Phase 8d &nbsp;·&nbsp; Agents in Practice &nbsp;·&nbsp; Vision + Text",
    "👁️ Multimodal Agents",
    "Agents that see as well as read — image input, visual RAG, document parsing, "
    "and chart analysis using Gemini's native multimodal capability.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is a Multimodal Agent — and what can it perceive?"):
    st.markdown("""
Every agent in Phases 1–8c worked with **text in, text out**.
A multimodal agent adds **image perception** — it can reason about what it sees, not just what it reads.

**What Gemini 2.5 Flash accepts as input:**

| Modality | Input type | Example agent task |
|---|---|---|
| **Text** | String | Conversation, instructions, structured data |
| **Image** | JPEG / PNG / WebP / HEIC | Read a document photo, analyse a chart, describe a screenshot |
| **PDF** | PDF bytes | Parse a multi-page policy document with diagrams |
| **Audio** | MP3 / WAV | Transcribe and analyse a customer call recording |
| **Video** | MP4 / MOV | Analyse surveillance footage, summarise a tutorial video |

This course focuses on **image input** — the most common agentic use case and fully supported in the current stack.

**Three patterns where multimodal changes what's possible:**

| Pattern | Text-only limitation | Multimodal solution |
|---|---|---|
| **Document agents** | PDFs with embedded charts, tables, or diagrams return garbled text | Send the page as an image — agent reads layout, tables, and text together |
| **Visual RAG** | Retrieval over image-heavy knowledge bases fails with text embeddings | Embed image descriptions, retrieve by semantic similarity, answer from image |
| **Screenshot analysis** | Computer Use (Phase 8c) sends coordinates blindly | Agent describes what it sees before acting — reads error messages, button labels, form states |

**Key API difference — sending an image:**

```python
# Text only (every previous phase):
response = client.models.generate_content(model=MODEL, contents="What is X?")

# Multimodal (this phase):
response = client.models.generate_content(
    model=MODEL,
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        types.Part.from_text("What does this chart show?"),
    ]
)
```

The model receives both simultaneously — it reads the image and the question together,
producing an answer grounded in what it actually sees.
""")

with st.expander("📐 Core Code Pattern — Multimodal Agent"):
    st.code('''
from google.genai import types

# ── PATTERN 1: Answer a question about an image ───────────────────────────────
def ask_about_image(image_bytes: bytes, mime_type: str, question: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(question),
        ],
    )
    return response.text

# ── PATTERN 2: Extract structured data from a document image ─────────────────
def extract_from_document(image_bytes: bytes) -> dict:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(
                "Extract all data from this document. "
                "Return valid JSON: {title, date, key_figures, summary}"
            ),
        ],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text)

# ── PATTERN 3: Multimodal tool — agent calls when it needs to see something ───
def analyse_screenshot(image_bytes: bytes) -> str:
    """Analyse a screenshot and describe what actions are available."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            types.Part.from_text(
                "Describe: 1) What page/screen is this? "
                "2) What interactive elements are visible? "
                "3) What is the current state?"
            ),
        ],
    )
    return response.text
''', language="python")
    st.markdown("""
**What changed vs text-only agents:**
- `contents` is now a **list** instead of a string — it can hold any mix of `Part` objects
- `Part.from_bytes()` sends raw image bytes with the MIME type
- The model processes image and text **simultaneously** — not sequentially
- Every tool and pattern from previous phases works unchanged — you just add image Parts

**Why this is more powerful than OCR + text:**
An OCR pipeline extracts text from images but loses layout, colour, and spatial relationships.
Gemini reads the image directly — it understands that a red cell in a table means "warning",
that a downward arrow in a chart means "declining", that a checked box means "complete".
""")

st.markdown("---")

# ── Demo ──────────────────────────────────────────────────────────────────────
st.markdown("## Live Demo — Three multimodal agent patterns")

tab_qa, tab_extract, tab_compare = st.tabs([
    "👁️ Tab A — Image Q&A",
    "📄 Tab B — Document Extraction",
    "🔍 Tab C — Chart Analysis",
])

# ── TAB A: Image Q&A ──────────────────────────────────────────────────────────
with tab_qa:
    st.markdown("### Upload any image — ask the agent questions about it")
    st.caption("The agent sees the image and answers in context. No text extraction, no OCR — direct visual perception.")

    uploaded = st.file_uploader("Upload an image (JPEG, PNG, WebP):", type=["jpg","jpeg","png","webp"], key="mm_upload")

    PRESET_QUESTIONS = [
        "What does this image show? Describe in detail.",
        "What text or numbers are visible in this image?",
        "What is the main subject and what is happening?",
        "Are there any charts, tables, or structured data? If so, extract the key values.",
        "What actions or next steps does this image suggest?",
    ]

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("**Quick questions:**")
        for q in PRESET_QUESTIONS:
            if st.button(q[:45] + "…" if len(q) > 45 else q, key=f"qa_{q[:20]}"):
                st.session_state.mm_q = q
                st.rerun()
    with col1:
        question = st.text_area(
            "Your question about the image:",
            value=st.session_state.get("mm_q", PRESET_QUESTIONS[0]),
            height=80,
            key="mm_question",
        )

    if st.button("▶  Ask Agent", type="primary", key="run_mm_qa"):
        if not uploaded:
            st.warning("Please upload an image first.")
            st.stop()
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        image_bytes = uploaded.read()
        mime_type = uploaded.type or "image/jpeg"

        system = (
            "You are a visual analysis agent. You receive an image and a question. "
            "Answer accurately based on what you actually see in the image. "
            "If something is not visible or unclear, say so — do not guess."
        )

        col_img, col_ans = st.columns([1, 1])
        with col_img:
            st.markdown("**Image sent to agent:**")
            st.image(image_bytes, use_container_width=True)
        with col_ans:
            st.markdown("**Agent's answer:**")
            with st.spinner("Agent analysing image..."):
                resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        types.Part.from_text(question),
                    ],
                    config=types.GenerateContentConfig(system_instruction=system),
                )
            answer = resp.text.strip()
            st.success(answer)

        st.toast("✅ Visual Q&A complete", icon="👁️")

        def _tab_call():
            st.markdown("**System prompt:**")
            st.code(system, language="text")
            st.markdown("**Contents sent (list of Parts):**")
            st.code(
                f"[\n"
                f"  Part.from_bytes(data=<{len(image_bytes):,} bytes>, mime_type='{mime_type}'),\n"
                f"  Part.from_text('{question[:80]}{'...' if len(question)>80 else ''}')\n"
                f"]",
                language="python",
            )
        def _tab_raw():
            st.code(answer, language="text")

        render_trace(("Multimodal Call", _tab_call), ("Raw Answer", _tab_raw))

# ── TAB B: Document Extraction ────────────────────────────────────────────────
with tab_extract:
    st.markdown("### Upload a document image — agent extracts structured data")
    st.caption("Works on invoices, reports, forms, scanned documents, screenshots of data tables.")

    doc_upload = st.file_uploader("Upload a document image:", type=["jpg","jpeg","png","webp","pdf"], key="mm_doc")

    EXTRACT_PROMPTS = {
        "General document": "Extract all key information from this document. Return JSON: {title, date, key_points, numbers_mentioned, summary}",
        "Invoice / receipt": "Extract all financial data. Return JSON: {vendor, date, line_items: [{description, amount}], total, currency}",
        "Report / chart page": "Extract all data shown. Return JSON: {title, period, metrics: [{name, value, unit}], key_insight}",
        "Form / table": "Extract all fields and values. Return JSON: {form_title, fields: [{label, value}]}",
    }

    extract_type = st.selectbox("Document type:", list(EXTRACT_PROMPTS.keys()), key="mm_dtype")
    extract_prompt = EXTRACT_PROMPTS[extract_type]

    if st.button("▶  Extract Data", type="primary", key="run_mm_extract"):
        if not doc_upload:
            st.warning("Please upload a document image first.")
            st.stop()

        doc_bytes = doc_upload.read()
        doc_mime = doc_upload.type or "image/jpeg"

        col_doc, col_out = st.columns([1, 1])
        with col_doc:
            st.markdown("**Document sent to agent:**")
            if doc_mime != "application/pdf":
                st.image(doc_bytes, use_container_width=True)
            else:
                st.info("PDF uploaded.")

        with col_out:
            st.markdown("**Extracted structured data:**")
            with st.spinner("Agent extracting data from document..."):
                resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=[
                        types.Part.from_bytes(data=doc_bytes, mime_type=doc_mime),
                        types.Part.from_text(extract_prompt),
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
            try:
                extracted = json.loads(resp.text)
                st.json(extracted)
            except json.JSONDecodeError:
                st.code(resp.text, language="text")

        st.toast("✅ Document extraction complete", icon="📄")

# ── TAB C: Chart Analysis ─────────────────────────────────────────────────────
with tab_compare:
    st.markdown("### Chart / Graph Analysis — agent reads data from visual charts")
    st.caption(
        "Upload a chart image (bar chart, line graph, pie chart). "
        "The agent reads the values, identifies trends, and answers questions."
    )

    chart_upload = st.file_uploader("Upload a chart image:", type=["jpg","jpeg","png","webp"], key="mm_chart")

    CHART_QUESTIONS = [
        "What type of chart is this? What does it show?",
        "What are the exact values for each data point or category?",
        "What is the highest and lowest value? What does this tell us?",
        "What trend is visible? Is it increasing, decreasing, or stable?",
        "Summarise the key insight from this chart in one sentence.",
    ]

    chart_q = st.selectbox("What to analyse:", CHART_QUESTIONS, key="mm_chartq")
    custom_chart_q = st.text_input("Or type a custom question:", key="mm_chart_custom")
    final_chart_q = custom_chart_q if custom_chart_q.strip() else chart_q

    if st.button("▶  Analyse Chart", type="primary", key="run_mm_chart"):
        if not chart_upload:
            st.warning("Please upload a chart image first.")
            st.stop()

        chart_bytes = chart_upload.read()
        chart_mime = chart_upload.type or "image/jpeg"

        system_chart = (
            "You are a data analyst agent. You receive a chart or graph image. "
            "Read the values, axes, labels, and legend accurately. "
            "Be precise with numbers — do not estimate when values are clearly labelled."
        )

        col_c, col_a = st.columns([1, 1])
        with col_c:
            st.markdown("**Chart sent to agent:**")
            st.image(chart_bytes, use_container_width=True)
        with col_a:
            st.markdown("**Agent's analysis:**")
            with st.spinner("Agent reading chart..."):
                resp = _call(
                    client.models.generate_content,
                    model=MODEL,
                    contents=[
                        types.Part.from_bytes(data=chart_bytes, mime_type=chart_mime),
                        types.Part.from_text(final_chart_q),
                    ],
                    config=types.GenerateContentConfig(system_instruction=system_chart),
                )
            chart_answer = resp.text.strip()
            st.info(chart_answer)

        st.toast("✅ Chart analysis complete", icon="🔍")

        def _tab_chart_call():
            st.markdown("**System prompt:**")
            st.code(system_chart, language="text")
            st.markdown("**Question asked:**")
            st.code(final_chart_q, language="text")
        def _tab_chart_raw():
            st.code(chart_answer, language="text")

        render_trace(("Chart Call", _tab_chart_call), ("Raw Answer", _tab_chart_raw))

st.markdown("---")
with st.expander("🔍 What just happened — Multimodal pipeline"):
    st.markdown("""
| Step | Input | What ran | Output |
|---|---|---|---|
| **Build contents list** | Image bytes + question text | Assemble `[Part.from_bytes(), Part.from_text()]` | Multimodal content list |
| **Send to model** | Content list | `generate_content(model, contents=[...])` | Model response |
| **Model perception** | Image pixels + question tokens | Gemini vision encoder + language model jointly | Grounded text answer |

**The key difference from text-only agents:**
The model does not process image and text separately and combine them.
It processes both **simultaneously** — the visual tokens and text tokens attend to each other
in the same transformer forward pass. This is why it can answer "what does the red bar represent?"
— it connects the colour (visual) to the label (text in the chart) in one step.

**Production considerations:**
- **Image size:** Gemini resizes large images internally — no need to pre-resize, but smaller images process faster
- **Cost:** Image tokens are counted separately — a 1024×1024 image ≈ 258 tokens at standard rates
- **Privacy:** Images are sent to the API — ensure compliance before sending PII-containing documents
- **Caching:** Use `st.cache_resource` for knowledge-base images embedded at startup (same as text RAG)
""")

st.markdown("---")
st.markdown("### What's next → Phase 8e — Enterprise Event-Driven Patterns")
st.markdown(
    "Now that agents can perceive multiple modalities, Phase 8e shows how they integrate "
    "into enterprise systems — triggered by events from Kafka, responding asynchronously, "
    "and fitting into existing microservice architectures."
)
