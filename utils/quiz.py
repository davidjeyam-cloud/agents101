"""
Quiz system: seed concepts per phase + Gemini-powered MCQ generation.
generate_questions() calls Gemini with JSON mode to produce fresh questions each run.
"""
import json
import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

load_dotenv()

MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Seed bank — concept strings per completed phase.
# Gemini generates 12 fresh MCQ variants from these every quiz session.
# ---------------------------------------------------------------------------
PHASE_SEEDS: dict[str, dict] = {
    "0": {
        "title": "Phase 0 — Foundations",
        "icon": "🏗️",
        "status": "complete",
        "concepts": [
            "Anthropic's definition of an Agent: an LLM that uses Tools and Control Flow to direct its OWN next actions based on its OWN outputs",
            "Workflow vs Agent: a Workflow has a fixed, predetermined sequence of steps; an Agent's path is decided dynamically by the LLM at each step",
            "Agent components: Perception (inputs from environment), Memory (in-context + persistent), Action (tool calls + final output)",
            "Why learning frameworks (LangChain, LangGraph, ADK) LAST matters: framework abstractions hide the underlying mechanics; devs who build raw first can debug frameworks; the reverse is much harder",
            "The LLM is the reasoning engine — it can be swapped (GPT-4, Claude, Gemini, Llama) without changing the agent architecture",
            "API keys and secrets must never be committed to source control — always use environment variables or a secrets manager",
            "Agentic AI expands LLM capability along two axes: memory (what it knows) and actions (what it can do)",
            "The minimum viable agent: an LLM that receives a task, decides to call a tool, observes the result, and decides what to do next",
        ],
        "snippets": [
            "# Workflow: fixed steps — step1() → step2(result1) → step3(result2)",
            "# Agent: LLM decides — while not done: action = llm(history); result = execute(action); history += result",
            "# Agent self-direction: next_action = llm(task + all_previous_results)  # owns its own loop",
        ],
    },
    "1": {
        "title": "Phase 1 — Augmented LLM",
        "icon": "🧠",
        "status": "complete",
        "concepts": [
            "Plain LLM: single stateless call — no memory, no tools, no awareness of prior turns",
            "Memory augmentation: full conversation history (role + content pairs) passed on EVERY call — the LLM has no built-in memory; you reconstruct it each time",
            "Tool use requires manual orchestration: after the LLM requests a tool call, you execute it and send the result back in the next message",
            "Automatic tool execution is a hidden risk: when the SDK executes tools silently, you lose visibility — you cannot log, audit, or inspect what ran",
            "Mini Agent loop: developer controls Think → Act (tool call) → Observe (tool result) → repeat — every step is explicit and inspectable",
            "Progression of agency: Plain LLM (stateless) → +Memory (stateful) → +Tools (actions) → Mini Agent (self-directed loop)",
            "What makes something an Agent: the LLM uses its OWN output from one step as the input driving its NEXT step — it self-directs",
            "The difference between giving an LLM tools vs building an agent: tools alone don't make an agent; the agent loop (self-direction) does",
        ],
        "snippets": [
            "# Memory: always pass full history — LLM has no state of its own\nhistory.append({'role': 'user', 'content': msg}); response = llm(history)",
            "# Manual tool loop — visibility by design:\nif response.tool_calls:\n    result = execute_tool(response.tool_calls[0])\n    history.append({'role': 'tool', 'content': result})",
            "# Agent loop guard:\nwhile iteration < MAX_ITER:\n    response = llm(history)\n    if not response.tool_calls: break  # LLM decided it's done",
        ],
    },
    "2": {
        "title": "Phase 2 — Workflow Patterns",
        "icon": "🔀",
        "status": "complete",
        "concepts": [
            "Prompt Chaining: output of step N is injected as input to step N+1 — deterministic, sequential, lowest cost, error propagates silently",
            "Routing: classify input first, then dispatch to a specialised handler — 2 LLM calls total; misclassification is the primary failure mode",
            "Parallelization: fan-out to N independent workers simultaneously; two variants — parallel sections (speed) and voting (accuracy via consensus)",
            "Orchestrator-Workers: orchestrator LLM decomposes task dynamically and assigns subtasks to specialist workers; orchestrator does NOT execute — it only delegates",
            "Evaluator-Optimizer: generator produces output, evaluator scores it, loop repeats until score meets threshold — generator and evaluator can collude if same model",
            "Workflow vs Agent distinction: in all 5 workflow patterns, the developer defines WHEN each LLM call happens; in agents the LLM decides",
            "When Prompt Chaining beats ReAct: when every step is predictable, chaining is cheaper, faster, and more auditable than an open-ended agent loop",
            "Parallelization's aggregation problem: when N workers return contradictory answers, you need an explicit tiebreaker rule before voting works",
        ],
        "snippets": [
            "# Chaining: out1 = llm(step1_prompt); out2 = llm(step2_prompt + out1)",
            "# Routing: route = classify(input); response = HANDLERS[route](input)",
            "# Eval-Optimizer loop:\nwhile score < threshold and i < MAX_ITER:\n    draft = generate(prompt); score = evaluate(draft); i += 1",
        ],
    },
    "3": {
        "title": "Phase 3 — Core Agent Patterns",
        "icon": "🤖",
        "status": "complete",
        "concepts": [
            "ReAct (Reason + Act): Think → Act (tool) → Observe (result) → repeat; the LLM decides when it has enough to answer and stops calling tools",
            "ReAct's key weakness: no upfront plan means the agent can take inefficient or circular paths on complex multi-step tasks",
            "Reflection: LLM critiques its OWN previous output and self-rewrites — same model, self-feedback loop; diminishing returns after 2-3 cycles",
            "Reflection vs LLM-as-Judge: Reflection is self-critique (one model); Judge is an independent evaluator (separate neutral perspective with no stake in the original output)",
            "Planning Agent (Plan-and-Execute): explicit structured plan committed BEFORE any tool is called; each step executed with full plan context",
            "Planning vs ReAct trade-off: Planning is auditable and efficient for predictable tasks; ReAct is flexible but expensive for open-ended tasks",
            "Code Execution as a tool: the agent writes code, a sandboxed interpreter runs it, the stdout/result is fed back — enables deterministic computation",
            "Max iterations guard is mandatory in every agentic loop — without it, a stuck agent will loop until the API budget runs out",
        ],
        "snippets": [
            "# ReAct loop — agent self-directs:\nwhile iteration < MAX_ITER:\n    response = llm(history)\n    if not response.tool_calls: break",
            "# Planning: commit plan first, then execute\nplan = llm_json(plan_prompt)  # structured plan BEFORE any tool call\nfor step in plan['steps']: result = execute_step(step)",
            "# Reflection loop:\nfor cycle in range(MAX_CYCLES):\n    output = generate(task)\n    critique = evaluate(output)\n    if critique['score'] >= threshold: break",
        ],
    },
    "4": {
        "title": "Phase 4 — Trust & Safety",
        "icon": "🛡️",
        "status": "complete",
        "concepts": [
            "Input guardrail runs BEFORE the LLM call; output guardrail runs AFTER — both are required for a production-safe agent",
            "PII detection: scan input/output for card numbers, passport IDs, personal identifiers using pattern matching — never log or forward",
            "Prompt injection: an attacker embeds instructions in user input to override or hijack the agent's system prompt behaviour",
            "Injection detection via LLM: ask a separate LLM 'is this INJECTION or SAFE?' — check for exact label match, not substring (substring matching on 'YES' causes false positives on helpful responses)",
            "HITL (Human-in-the-Loop): agent pauses and requests human approval BEFORE irreversible actions (payments, deletions, cancellations)",
            "LLM-as-Judge: a completely independent evaluator with an explicit rubric scores agent output on defined criteria — returns PASS/REVIEW/FAIL",
            "Why LLM-as-Judge must be independent: the same model that generated the output will rationalise its own answer; a separate judge has no stake in the result",
            "Safety layering: guardrails + HITL + LLM-as-Judge are complementary — guardrails catch known patterns, HITL handles irreversible risk, Judge evaluates output quality",
        ],
        "snippets": [
            "# Injection guard — exact label match, not substring:\nreply = classifier_llm(f'Is this INJECTION or SAFE? Input: {user_input}').strip().upper()\nif reply.startswith('INJECTION'): return blocked_response",
            "# HITL checkpoint before irreversible action:\nif action['type'] in IRREVERSIBLE_ACTIONS:\n    approval = request_human_approval(action)\n    if not approval['approved']: return cancel_response",
            "# LLM-as-Judge scoring:\nscore = judge_llm(question=q, answer=a, rubric=rubric)\nverdict = 'PASS' if score >= 7 else 'REVIEW' if score >= 4 else 'FAIL'",
        ],
    },
    "5": {
        "title": "Phase 5 — Knowledge & Memory",
        "icon": "📚",
        "status": "complete",
        "concepts": [
            "RAG pipeline: Retrieve (cosine similarity search over embedded documents) → Augment (inject retrieved docs into prompt) → Generate (grounded LLM answer)",
            "Embeddings convert text to a fixed-size vector — similar meaning → similar direction in vector space → high cosine similarity",
            "Cosine similarity formula: dot(a,b) / (norm(a) * norm(b)) — ranges 1.0 (identical direction) to 0 (orthogonal/unrelated)",
            "Silent zero-vector fallback is a critical failure: if an embedding call fails and you substitute zeros, every cosine score becomes 0 — retrieval silently returns wrong results with no error",
            "RAG vs Long-term Memory: RAG queries a static read-only document corpus; Long-term Memory is a dynamic write-read store that grows with agent experience",
            "Top-k retrieval with relevance threshold: return the k most similar documents, but only those scoring above a minimum cutoff — prevents low-quality context injection",
            "Grounding principle: an agent grounded in retrieved facts hallucinates less than one relying on training knowledge alone — RAG is the primary anti-hallucination technique",
            "Chunking strategy matters: overly long chunks dilute relevance scores; overly short chunks lose context — chunk size is a tunable parameter",
        ],
        "snippets": [
            "# Embed and store:\nvector = embed(text)  # any embedding model: OpenAI, Gemini, Cohere, etc.\nvector_store.add(id=doc_id, vector=vector, metadata=doc)",
            "# Retrieve by cosine similarity:\nquery_vec = embed(query)\nscores = [(doc, cosine(query_vec, doc.vector)) for doc in vector_store]\ntop_k = sorted(scores, key=lambda x: -x[1])[:k]",
            "# Augment prompt with retrieved context:\ncontext = '\\n'.join(doc.text for doc, score in top_k if score > THRESHOLD)\nfinal_prompt = f'Context:\\n{context}\\n\\nQuestion: {query}'",
        ],
    },
    "6": {
        "title": "Phase 6 — Multi-Agent & Protocols",
        "icon": "🤝",
        "status": "complete",
        "concepts": [
            "Multi-Agent architecture: a root orchestrator delegates to specialist sub-agents; from the orchestrator's perspective, each sub-agent is just a callable tool",
            "Parallel multi-agent: independent specialist agents run concurrently — no blocking between them; results aggregated after all complete",
            "MCP (Model Context Protocol, Anthropic 2024): standard protocol for agent-to-RESOURCE connections — tools, databases, APIs; solves the N×M integration problem",
            "MCP flow: agent initialises connection → lists available tools (server returns schemas) → calls tool by name with arguments → receives structured result",
            "A2A (Agent-to-Agent Protocol, Google 2025): standard for agent-to-AGENT task delegation — one agent submits a task to another agent as a peer",
            "A2A Agent Card: a JSON discovery document at a well-known URL describing an agent's capabilities, skills, and authentication requirements",
            "MCP vs A2A are complementary, not competing: MCP = agent connects to tools/data; A2A = agent delegates to another agent — a production system uses both",
            "Trust boundary in multi-agent systems: a sub-agent must validate inputs from an orchestrator just as it would from a human — orchestrators can be compromised",
        ],
        "snippets": [
            "# Sub-agent as tool — orchestrator's view:\ndef research_agent(query: str) -> str: ...  # specialist wrapped as callable\norchestrator_tools = [research_agent, write_agent, review_agent]",
            "# MCP: agent discovers tools at runtime — not hardcoded\ntools = mcp_client.list_tools()  # [{name, description, inputSchema}]\nresult = mcp_client.call_tool(name='search_docs', arguments={'query': q})",
            "# Parallel sub-agents:\nwith ThreadPoolExecutor() as ex:\n    futures = {name: ex.submit(agent_fn, task) for name, agent_fn in specialists.items()}\n    results = {name: f.result() for name, f in futures.items()}",
        ],
    },
    "7": {
        "title": "Phase 7 — Production Operations",
        "icon": "🔭",
        "status": "complete",
        "concepts": [
            "Observability: every LLM call should emit a structured trace span — timestamp, latency, input tokens, output tokens, estimated cost, tool calls made",
            "Wrapping LLM calls in a tracer decorator adds observability without changing business logic — separation of concerns",
            "Token counting BEFORE sending enables hard budget enforcement; counting after is too late to prevent overruns",
            "Prompt caching: if the system prompt is repeated across calls, the API can cache the prefix — typical savings 60-80% on cached tokens",
            "Model routing by complexity: route simple classification/routing tasks to a cheaper fast model; reserve the powerful model for complex multi-step reasoning",
            "Five production error types: Hallucination, Tool Loop, Context Overflow, Prompt Injection, Logic Error — each has a different root cause and different fix",
            "Tool loop detection: if the same tool is called with the same arguments N times without progress, the agent is stuck — break with an explicit error, do not let it exhaust the budget",
            "LLM-as-Judge for automated error diagnosis: compare broken vs fixed agent responses against a rubric to identify which error category applies",
        ],
        "snippets": [
            "# Observability decorator — wraps any LLM call:\n@trace_span\ndef call_llm(prompt): return llm(prompt)  # span captures latency + tokens automatically",
            "# Model routing by task complexity:\nmodel = cheap_fast_model if task_type in SIMPLE_TASKS else powerful_model",
            "# Tool loop guard:\nif tool_call_counts[tool_name] >= MAX_TOOL_CALLS:\n    raise RuntimeError(f'Tool loop detected: {tool_name} called {MAX_TOOL_CALLS}+ times')",
        ],
    },
    "8": {
        "title": "Phase 8 — Agents in Practice",
        "icon": "🎧",
        "status": "complete",
        "concepts": [
            "Production agent pipeline composes multiple patterns: Guardrails → Memory → RAG → ReAct → LLM-Judge → HITL → Observability — each layer has a distinct responsibility",
            "Specialist routing by intent (not keyword): a classifier LLM determines which specialist agent handles the request — keyword matching is brittle for natural language",
            "Grounding mandate: in a domain-specific agent, every answer must be grounded in retrieved policy/data — the LLM must call the knowledge source FIRST, not answer from training memory",
            "Each specialist agent has its own system prompt, its own tool set, and its own trust boundary — not one generic agent doing everything",
            "Injection guard in production: check for exact label ('INJECTION') not substring — 'YES' substring matching produces false positives on legitimate user responses",
            "HITL position in pipeline: placed AFTER the agent computes an action plan but BEFORE irreversible execution — this is the only position that is both informed and preventative",
            "Observability in production: every span should include which specialist handled the request, how many tool calls were made, and the LLM-Judge verdict",
            "Failure gracefully: when a specialist fails, the pipeline should return a safe fallback response — never surface raw exception text to the end user",
        ],
        "snippets": [
            "# Specialist routing — intent-based, not keyword:\nspecialist = intent_classifier(user_input)  # returns 'billing' | 'technical' | 'general'\nresponse = SPECIALISTS[specialist].run(user_input, context)",
            "# Grounding system prompt rule:\n# 'Before answering ANY question, call search_knowledge_base() first.\n#  Never answer from training memory alone when a knowledge tool is available.'",
            "# Pipeline composition:\nif not input_guardrail(user_input)['safe']: return safe_error_response\ncontext = memory.recall(user_input) + rag.retrieve(user_input)\nresponse = specialist_agent(user_input, context)\nif not output_guardrail(response)['safe']: return safe_error_response",
        ],
    },
}

# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are an expert Agentic AI examiner with deep production experience building LLM-powered systems.
Your job is to test whether learners truly UNDERSTAND the patterns — not whether they can recite definitions.

This course teaches LLM-agnostic agentic AI architecture. The patterns, principles, and trade-offs
apply to ANY LLM (GPT-4, Claude, Gemini, Llama, Mistral — it does not matter which).

Phase under examination: {phase_title}

Core concepts in scope:
{concepts}

Code patterns to draw from for snippet-based questions:
{snippets}

━━━ BANNED TOPICS — NEVER ask about these ━━━

  ✗  Any specific LLM product name (Gemini, GPT-4, Claude, Flash, Pro, Llama, etc.)
  ✗  Any specific SDK or library (google-genai, openai, anthropic, LangChain, LangGraph, etc.)
  ✗  API key names (GEMINI_API_KEY, OPENAI_API_KEY, etc.) or environment variable specifics
  ✗  Model version numbers (2.5-flash, gpt-4o, claude-3, etc.) or model tiers by brand name
  ✗  Specific embedding model names or their exact vector dimensions
  ✗  Deprecated library migrations (google-generativeai → google-genai, etc.)
  ✗  UI framework specifics (st.session_state keys, Streamlit widget names)
  ✗  Any question that only an engineer using one specific vendor's API could answer

If a concept is vendor-specific, generalise it: "the LLM SDK" not "google-genai",
"a fast cheap model" not "Flash-Lite", "an embedding model" not "gemini-embedding-001".

━━━ EXAMINER PHILOSOPHY ━━━

NEVER write surface-level recall questions. Examples of what to AVOID:
  ✗  "What does ReAct stand for?"
  ✗  "Which SDK should you import for Gemini?"
  ✗  "What is the MCP protocol?"
  ✗  "What vector dimension does gemini-embedding-001 return?"

ALWAYS write questions that require reasoning, trade-off analysis, or failure-mode thinking.
Aim for the standard of an Anthropic AI or AWS AI Practitioner certification:
  ✓  "Your ReAct agent calls get_account_balance() 12 times before timing out. The tool returns valid data each time. What is the most likely architectural cause, and which single fix addresses the root issue?"
  ✓  "A team argues that a Prompt Chain can replace a ReAct agent for their use case. Under what specific condition are they correct — and what is the single constraint that breaks that assumption?"
  ✓  "Your SDK is configured to execute tools automatically without exposing intermediate results. The agent still returns correct final answers. What production capability have you silently lost, and why does it matter?"
  ✓  "An agent's RAG retrieval returns contextually irrelevant documents for every query despite high embedding coverage. The embedding calls succeed. What is the most likely root cause?"
  ✓  "You need to build a system that answers questions about company policy documents that are updated weekly. Should you use RAG, Long-term Memory, or fine-tuning — and what is the deciding factor?"

The wrong options must represent genuine misconceptions a thoughtful but surface-level learner would pick.
They should be plausible — not obviously absurd.

━━━ QUESTION DISTRIBUTION ━━━

Generate exactly {n} questions with this type distribution:
  - 3 × "scenario"   : Real situation, which approach/pattern, and WHY — justify the choice
  - 3 × "tradeoff"   : X vs Y under a specific constraint or production requirement — which and why
  - 2 × "failure"    : A symptom is described — what is the root cause, or what will break if you do X
  - 2 × "rootcause"  : A broken snippet or misbehaving agent — identify the specific flaw and the correct fix
  - 2 × "design"     : Given a system requirement, design/justify an architectural decision

━━━ OUTPUT FORMAT ━━━

Return ONLY a valid JSON array. No markdown fences, no explanation, no commentary before or after.

Each element:
{{"q":"full question text","opts":["first choice","second choice","third choice","fourth choice"],"ans":0,"type":"scenario","explain":"2-3 sentence explanation citing the specific concept, trade-off, or failure mechanism — not just 'because it is correct'. The explanation must be useful to a learner who got it wrong."}}

Hard format rules:
1. opts must contain exactly 4 strings
2. CRITICAL: opts must be PLAIN TEXT — no letter prefixes like "A.", "B)", "(C)" — the UI labels them automatically
3. ans is 0-indexed (0=first option, 1=second, 2=third, 3=fourth)
4. explain must be genuinely educational — reference the exact mechanism, not just restate the answer
5. Do not repeat the same concept across multiple questions
6. Questions must be self-contained — include enough context that the learner does not need to look anything up
7. FINAL CHECK before returning: scan every question and option — if any banned topic appears, rewrite it
"""


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc)
    return "503" in msg or "UNAVAILABLE" in msg


def generate_questions(phase_key: str, num_questions: int = 12) -> list[dict]:
    """
    Generate MCQ questions for a phase using Gemini JSON mode.
    Returns list of dicts: {q, opts, ans, type, explain}.
    Raises on API error or malformed JSON.
    """
    phase = PHASE_SEEDS[phase_key]
    prompt = _PROMPT_TEMPLATE.format(
        phase_title=phase["title"],
        n=num_questions,
        concepts="\n".join(f"- {c}" for c in phase["concepts"]),
        snippets="\n".join(f"- {s}" for s in phase["snippets"]),
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(multiplier=1, min=3, max=20),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _call():
        return client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

    response = _call()
    questions = json.loads(response.text)

    if not isinstance(questions, list) or len(questions) == 0:
        raise ValueError(f"Gemini returned unexpected structure: {response.text[:200]}")

    # Normalise and validate each question
    validated = []
    for i, q in enumerate(questions[:num_questions]):
        if not all(k in q for k in ("q", "opts", "ans")):
            continue
        if not isinstance(q["opts"], list) or len(q["opts"]) != 4:
            continue
        if not isinstance(q["ans"], int) or not (0 <= q["ans"] <= 3):
            continue
        # Strip any "A.", "B)", "(C)", "A -", "A - " style prefixes Gemini sometimes adds
        clean_opts = [
            re.sub(r'^\s*[\(\[]?[A-Da-d]\s*[\.\)\]\:\-]\s*', '', opt).strip()
            for opt in q["opts"]
        ]
        validated.append({
            "q":       q["q"],
            "opts":    clean_opts,
            "ans":     q["ans"],
            "type":    q.get("type", "recall"),
            "explain": q.get("explain", ""),
        })

    if len(validated) < 8:
        raise ValueError(f"Too few valid questions generated ({len(validated)}). Try regenerating.")

    return validated
