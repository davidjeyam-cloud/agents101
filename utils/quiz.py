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
            "Anthropic's definition of an Agent: LLM + Tools + Control Flow that directs itself using its own outputs",
            "Difference between deterministic Workflow (fixed steps) and dynamic Agent (LLM decides next step)",
            "Agent components: Perception (input), Memory (context/vector store), Action (tools/output)",
            "Why frameworks (LangChain, LangGraph) are learned LAST — API-first builds deeper understanding and debugging skill",
            "google-genai SDK is the correct import; google-generativeai is deprecated and must never be used",
            "Model rule: ALWAYS use gemini-2.5-flash or above; NEVER use 1.5-flash, 2.0-flash, or any sub-2.5 model",
            "GEMINI_API_KEY stored in .env file — never committed to git",
            "Streamlit multi-page app uses st.navigation() with grouped phase sections in the sidebar",
        ],
        "snippets": [
            "from google import genai  # correct; NOT: import google.generativeai",
            "client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))",
            "response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)",
        ],
    },
    "1": {
        "title": "Phase 1 — Augmented LLM",
        "icon": "🧠",
        "status": "complete",
        "concepts": [
            "Plain LLM: single stateless generate_content call — no memory between turns",
            "Memory augmentation: full conversation history passed as list of role/parts dicts on EVERY call",
            "History format: parts MUST be a list of dicts [{'text': '...'}], NOT a plain string — SDK validation error otherwise",
            "AutomaticFunctionCallingConfig(disable=True): REQUIRED to see function_calls in response",
            "Without disable=True: tools execute silently inside the SDK, response.function_calls is None — the bug is invisible",
            "Mini Agent: developer-controlled Think→Act→Observe loop — every step is explicit and inspectable",
            "Progression of agency: Plain LLM → +Memory → +Tools → Mini Agent (full loop)",
            "What makes something an Agent: it uses its OWN outputs to direct its NEXT action (self-direction)",
        ],
        "snippets": [
            "automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)",
            "history = [{'role': 'user', 'parts': [{'text': msg}]}]  # parts = list of dicts",
            "if response.function_calls:  # manually detect tools, execute, send result back",
        ],
    },
    "2": {
        "title": "Phase 2 — Workflow Patterns",
        "icon": "🔀",
        "status": "complete",
        "concepts": [
            "Prompt Chaining: output of step N injected into step N+1 — sequential, deterministic pipeline",
            "Routing: classify intent first, then route to the right specialized handler (traffic cop pattern)",
            "Parallelization variants: parallel sections (speed, independent subtasks) vs voting (accuracy via consensus)",
            "Orchestrator-Workers: orchestrator LLM decomposes task dynamically, assigns pieces to worker LLMs",
            "Evaluator-Optimizer: generator produces draft, evaluator scores it, loop continues until threshold met",
            "Key distinction — Workflow vs Agent: workflow = fixed predetermined flow; agent = LLM decides each step",
            "Orchestrator does NOT execute tasks itself — it only plans and delegates to workers",
            "When to choose each: chaining=fixed sequence, routing=specialization, parallel=independence, orchestrator=unknown complexity",
        ],
        "snippets": [
            "# Chaining: out1 = llm(step1_prompt); out2 = llm(step2_prompt + out1)",
            "# Routing: route = classify(input); response = HANDLERS[route](input)",
            "# Parallel: futures = [executor.submit(llm, p) for p in prompts]",
            "# Eval loop: while score < threshold: draft = generate(prompt); score = evaluate(draft)",
        ],
    },
    "3": {
        "title": "Phase 3 — Core Agent Patterns",
        "icon": "🤖",
        "status": "complete",
        "concepts": [
            "ReAct = Reason + Act: Think→Act→Observe loop, continues until LLM decides task is complete (no function_calls)",
            "Observe step is critical: tool result fed back to LLM as new context for the next reasoning step",
            "Reflection: LLM critiques its OWN previous output and self-rewrites — same model, self-feedback loop",
            "Reflection vs LLM-as-Judge: Reflection = self-critique (one model prompts itself); Judge = independent evaluator (separate neutral perspective)",
            "Planning Agent: explicit structured JSON plan created BEFORE any execution begins — Plan→Execute→Synthesize",
            "Planning vs ReAct: Planning commits upfront (predictable, auditable); ReAct decides dynamically (flexible, adaptive)",
            "Code Execution: Python exec() in sandboxed namespace, contextlib.redirect_stdout captures print output",
            "Max iterations guard (while i < MAX_ITER) prevents infinite loops in ALL agentic patterns",
        ],
        "snippets": [
            "while iteration < MAX_ITER:  # always guard agentic loops",
            "if not response.function_calls: break  # LLM decided no more tools needed — task done",
            "plan = json.loads(llm(plan_prompt))  # get structured JSON plan BEFORE executing any step",
            "buf = io.StringIO()\nwith contextlib.redirect_stdout(buf):\n    exec(code, sandbox)\noutput = buf.getvalue()",
        ],
    },
    "4": {
        "title": "Phase 4 — Trust & Safety",
        "icon": "🛡️",
        "status": "complete",
        "concepts": [
            "Guardrails: input guardrail (validate/sanitize BEFORE LLM call) + output guardrail (validate AFTER LLM responds)",
            "PII detection via regex: card numbers, passport numbers, sort codes, PIN phrases — never log or forward",
            "Prompt injection: attacker embeds instructions in user input to override system prompt behaviour",
            "Injection check: ask LLM 'INJECTION or SAFE?' — check exact match on 'INJECTION', NOT 'YES' in reply.upper()",
            "Why 'YES in response' fails: a helpful LLM often starts responses with 'Yes, I can help...' — false positive blocks legitimate users",
            "HITL checkpoints: agent pauses before irreversible actions (payments, cancellations) for human approval/rejection/modification",
            "LLM-as-Judge: completely independent evaluator with explicit rubric, scores 1-10, returns structured PASS/REVIEW/FAIL verdict",
            "Python 3.14+: inline (?i) flag mid-pattern causes PatternError — must use re.compile(pattern, re.IGNORECASE) instead",
        ],
        "snippets": [
            "reply = check.text.strip().upper()\nif reply == 'INJECTION' or reply.startswith('INJECTION'):\n    return blocked_response",
            "_PII_RE = re.compile(r'...card...|...pin...', re.IGNORECASE)  # flag, NOT (?i) inline",
            "score = judge(question=q, rubric=rubric, answer=a)\nverdict = 'PASS' if score >= 7 else 'REVIEW' if score >= 4 else 'FAIL'",
        ],
    },
    "5": {
        "title": "Phase 5 — Knowledge & Memory",
        "icon": "📚",
        "status": "complete",
        "concepts": [
            "RAG pipeline: Retrieve (cosine search) → Augment (inject docs into prompt) → Generate (grounded LLM answer)",
            "Embedding model: MUST use gemini-embedding-001 which produces 3072-dimensional vectors",
            "text-embedding-004 is DEPRECATED — returns HTTP 404 error; never use it",
            "Cosine similarity formula: dot(a,b)/(norm(a)*norm(b)) — 1.0=identical direction, 0=orthogonal/unrelated",
            "Silent np.zeros(3072) fallback is dangerous: masks embedding failures, all cosine scores become 0, retrieval silently returns wrong results",
            "Long-term Memory pattern: remember(text, metadata) stores embeddings persistently; recall(query, top_k) retrieves by similarity",
            "RAG vs Long-term Memory: RAG queries a static read-only document corpus; LTM is a dynamic write-read store that grows with conversation",
            "Top-k retrieval with threshold: return the k most similar docs, but only above a minimum relevance cutoff score",
        ],
        "snippets": [
            "result = client.models.embed_content(\n    model='gemini-embedding-001', contents=text,\n    config=types.EmbedContentConfig(task_type='RETRIEVAL_DOCUMENT'))",
            "emb = np.array(result.embeddings[0].values)  # shape (3072,) — NOT (768,)",
            "sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))  # cosine similarity",
        ],
    },
    "6": {
        "title": "Phase 6 — Multi-Agent & Protocols",
        "icon": "🤝",
        "status": "complete",
        "concepts": [
            "Multi-Agent: root orchestrator delegates to specialist sub-agents; sub-agents ARE tools from root's perspective",
            "Parallel multi-agent: ThreadPoolExecutor runs multiple sub-agents simultaneously; no blocking between specialists",
            "MCP = Model Context Protocol (Anthropic, Nov 2024): standard protocol for agent-to-resource connections (tools, data sources)",
            "MCP protocol flow: initialize → list_tools (server returns schemas) → call_tool (JSON-RPC 2.0 format)",
            "A2A = Agent-to-Agent Protocol (Google, Apr 2025): standard for agent-to-agent task delegation",
            "A2A Agent Card: JSON discovery document at /.well-known/agent.json describing agent capabilities",
            "A2A task lifecycle: submitted → working → completed (or failed) with structured JSON messages at each step",
            "MCP vs A2A are COMPLEMENTARY: MCP = agent connects to tools/resources; A2A = agent delegates to another agent",
        ],
        "snippets": [
            "# MCP: server.list_tools() → [{name, description, inputSchema}]\n# client calls: server.call_tool(name, arguments)",
            "# A2A: card = get('/.well-known/agent.json').json()\n# task = submit_task(card, input_text)",
            "with ThreadPoolExecutor() as ex:\n    futures = {name: ex.submit(agent_fn, task) for name, agent_fn in agents.items()}",
        ],
    },
    "7": {
        "title": "Phase 7 — Production Operations",
        "icon": "🔭",
        "status": "complete",
        "concepts": [
            "Observability: trace every LLM call with span metadata — timestamp, latency_ms, input_tokens, output_tokens, estimated cost",
            "TraceCollector wraps _call() to record spans automatically without changing any business logic code",
            "Token counting: client.models.count_tokens() gives EXACT count BEFORE sending — enables budget enforcement",
            "Prompt caching: repeated system prompt prefix cached by API — 60-80% cost savings on repeated calls with same context",
            "Model routing: Flash-Lite for fast classification/routing, Flash for standard generation, Pro for complex multi-step reasoning",
            "5 error taxonomy: Hallucination, Tool Loop, Context Overflow, Prompt Injection, Logic Error — each needs a different fix",
            "Tool Loop detection: count calls per tool; if same tool called 3+ times with same arguments → break with explicit error",
            "LLM-as-Judge auto-diagnoses errors by comparing broken agent response vs fixed response against a rubric",
        ],
        "snippets": [
            "token_count = client.models.count_tokens(model=MODEL, contents=prompt).total_tokens",
            "model = 'gemini-2.5-flash-lite' if complexity == 'simple' else 'gemini-2.5-flash'",
            "if tool_call_counts[tool_name] > MAX_TOOL_CALLS:\n    raise RuntimeError(f'Tool loop: {tool_name} called too many times')",
        ],
    },
    "8": {
        "title": "Phase 8 — Agents in Practice",
        "icon": "🎧",
        "status": "complete",
        "concepts": [
            "Customer Support pipeline: Guardrails → Memory → RAG → ReAct → LLM-Judge → HITL → Observability — all patterns combined",
            "Elite Multi-Agent System: all 13 agentic patterns active simultaneously with MCP servers + A2A specialist routing",
            "MCP Policy Server grounds ALL specialist answers: specialists MUST call search_policies FIRST before any response",
            "Specialist routing: banking/fraud/international/complaints — route by detected intent, not simple keyword matching",
            "Refund queries MUST route to banking specialist (has get_fees + search_policies tools), NOT to complaints specialist",
            "Production injection guard: check reply.startswith('INJECTION'), never 'YES' in text — prevents false positives on legitimate queries",
            "Each specialist has its own tailored tool map matching their domain responsibilities",
            "Grounding principle: never answer from model training memory alone when a policy/data MCP server is available",
        ],
        "snippets": [
            "reply = check.text.strip().upper()\nif reply == 'INJECTION' or reply.startswith('INJECTION'):\n    return {'pass': False, 'reason': 'Injection detected'}",
            "# System prompt rule: 'ALWAYS call search_policies FIRST for ANY question about NexaBank'",
            "SPECIALIST_TOOL_MAP = {\n    'banking': [search_policies, get_rates, get_fees],\n    'international': [get_country_info, get_public_holidays, search_policies],\n}",
        ],
    },
}

# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are an expert Agentic AI examiner with deep production experience building LLM-powered systems.
Your job is to test whether learners truly UNDERSTAND the patterns — not whether they can recite definitions.

Phase under examination: {phase_title}

Core concepts in scope:
{concepts}

Code patterns to draw from for snippet-based questions:
{snippets}

━━━ EXAMINER PHILOSOPHY ━━━

NEVER write surface-level recall questions. Examples of what to AVOID:
  ✗  "What does ReAct stand for?"
  ✗  "Which SDK should you use with Gemini?"
  ✗  "What is the MCP protocol?"

ALWAYS write questions that require reasoning, trade-off analysis, or failure-mode thinking. Examples of the standard to AIM FOR:
  ✓  "Your ReAct agent calls get_account_balance() 12 times before timing out. The tool returns valid data each time. What is the most likely architectural cause, and which fix addresses the root issue?"
  ✓  "A team argues that a Prompt Chain can replace a ReAct agent for their use case. Under what specific condition are they correct — and what is the single constraint that breaks that assumption?"
  ✓  "You remove AutomaticFunctionCallingConfig(disable=True) from your agent. The agent still returns answers. Why does this appear to work, and what critical capability have you silently lost?"

The wrong options must represent genuine misconceptions that a surface-level learner would pick — not obviously absurd answers.

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
{{"q":"full question text","opts":["first choice","second choice","third choice","fourth choice"],"ans":0,"type":"scenario","explain":"2-3 sentence explanation citing the specific rule, trade-off, or failure mechanism — not just 'because it is correct'"}}

Hard format rules:
1. opts must contain exactly 4 strings
2. CRITICAL: opts must be PLAIN TEXT — no letter prefixes like "A.", "B)", "(C)" — the UI labels them automatically
3. ans is 0-indexed (0=first option, 1=second, 2=third, 3=fourth)
4. explain must reference the exact concept, rule, or failure mode — no vague justifications
5. Do not repeat the same concept across multiple questions
6. Questions must be self-contained — include enough context that the learner does not need to look anything up
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
