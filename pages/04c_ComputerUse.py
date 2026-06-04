"""
Phase 8c — Computer Use Agents
Agents that control real software via screenshots and click/type actions.
Claude Computer Use API + browser automation (Playwright-style).
Demo: conceptual simulation — shows the action loop without a live browser.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Phase 8c — Computer Use",
    page_icon="🖥️",
    layout="wide",
)

from utils.styles import phase_header, ACCENT_COMPLETE
from utils.llm import MODEL, _client, _call
from utils.trace import render_trace
from google.genai import types

st.markdown(phase_header(
    "Phase 8c &nbsp;·&nbsp; Agents in Practice &nbsp;·&nbsp; Computer Control",
    "🖥️ Computer Use Agents",
    "Agents that perceive and control real software — not just text. "
    "The agent sees a screenshot, decides what to click or type, and acts.",
    accent=ACCENT_COMPLETE,
), unsafe_allow_html=True)

# ── Concept ───────────────────────────────────────────────────────────────────
with st.expander("📖 What is a Computer Use agent — and why is it different from everything before?"):
    st.markdown("""
Every agent in Phases 1–8b works through **text APIs**:
the agent calls a function, gets a JSON response, reasons, calls another function.

Computer Use agents work through **visual perception and UI actions**:
the agent sees a screenshot, decides what to click or type, acts on the live screen,
then sees the new screenshot. The interface is any software — a browser, a desktop app,
a legacy system with no API.

**The action loop:**

```
Screenshot ──► LLM reasons ──► Action (click / type / scroll / keypress)
    ↑                                         │
    └─────────────────────────────────────────┘
              (repeat until task complete)
```

**Why this is genuinely agentic:**

| | API-calling agent (Phase 3a) | Computer Use agent |
|---|---|---|
| **Interface** | Function calls → JSON | Screenshots → UI actions |
| **Requires API** | Yes — tool must have an API | No — works on any GUI |
| **What it controls** | Structured data | Pixels, buttons, input fields |
| **Latency per step** | Milliseconds | Seconds (render + screenshot) |
| **Where it shines** | Modern services with APIs | Legacy systems, no-API tools, complex workflows |

**Real-world use cases:**

| Use case | Why Computer Use wins |
|---|---|
| **Legacy banking system** | No API exists — agent navigates the old UI |
| **Multi-step form filling** | 15 fields across 3 pages — agent reads, types, submits |
| **Cross-app workflow** | Copy data from email → paste into spreadsheet → file in CRM |
| **QA testing** | Agent tests the UI the way a human would |
| **Research** | Agent searches multiple websites, reads, compiles findings |

**The two primary implementations:**

| System | By | How | Status |
|---|---|---|---|
| **Claude Computer Use** | Anthropic | Screenshot → action via Claude API `computer_use` tool | Available (API beta) |
| **Browser automation agents** | Open-source | Playwright/Selenium + LLM decision layer | Available |

**Claude Computer Use — how the API works:**

```python
# The agent receives a screenshot as a base64 image
# and returns an action structured as:
{
  "type": "computer_use",
  "action": "left_click",
  "coordinate": [450, 320],   # pixel coordinates
}
# OR
{
  "type": "computer_use",
  "action": "type",
  "text": "johndoe@example.com",
}
```

The loop: take screenshot → send to Claude with task → get action → execute action →
take new screenshot → send again. Repeat until Claude says `"stop"`.

**Why this demo is a simulation:**

Running a live browser inside a Streamlit app requires a VM environment (Docker + VNC).
The demo below simulates the Computer Use action loop using text descriptions of UI states —
the same reasoning the agent performs, but without a real browser.
In production you would replace the simulated UI with actual `playwright` screenshot calls.
""")

with st.expander("📐 Core Code Pattern — Computer Use with Playwright"):
    st.code('''
import anthropic
import base64
from playwright.sync_api import sync_playwright

client = anthropic.Anthropic()

def screenshot_to_base64(page) -> str:
    png_bytes = page.screenshot()
    return base64.standard_b64encode(png_bytes).decode("utf-8")

def run_computer_use_agent(task: str, url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page    = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url)

        messages = []
        for _ in range(20):                             # max 20 actions
            screenshot_b64 = screenshot_to_base64(page)

            # ── Ask Claude what to do next ──────────────────────────────────
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text",  "text": f"Task: {task}"},
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/png",
                        "data": screenshot_b64,
                    }},
                ],
            })
            response = client.beta.messages.create(
                model    = "claude-opus-4-8-20260101",
                max_tokens = 4096,
                tools    = [{"type": "computer_20241022",
                             "name": "computer",
                             "display_width_px":  1280,
                             "display_height_px": 900}],
                messages = messages,
                betas    = ["computer-use-2024-10-22"],
            )

            # ── Execute the action Claude decided ───────────────────────────
            done = True
            for block in response.content:
                if block.type == "tool_use" and block.name == "computer":
                    action = block.input
                    done   = False

                    if action["action"] == "left_click":
                        page.mouse.click(*action["coordinate"])
                    elif action["action"] == "type":
                        page.keyboard.type(action["text"])
                    elif action["action"] == "scroll":
                        page.mouse.wheel(0, action.get("direction", 3) * 100)
                    elif action["action"] == "key":
                        page.keyboard.press(action["key"])
                    elif action["action"] == "screenshot":
                        pass   # just take a new screenshot next loop

            if done:           # Claude stopped using the tool — task complete
                break

        browser.close()
        return response.content[-1].text   # Claude's final text summary
''', language="python")
    st.markdown("""
**Key points:**
- The `computer_20241022` tool is Anthropic's Computer Use beta tool — Claude receives screenshots and outputs pixel-level actions
- The loop runs until Claude stops requesting the tool (decides task is done)
- `playwright` handles actual browser control — Claude handles the reasoning
- Replace `playwright` with `pyautogui` to control desktop apps instead of browsers

**Production considerations:**
- Run in a **sandboxed VM** — the agent has full control of the screen; you must isolate it
- Set a **maximum step limit** to prevent runaway loops
- Log every screenshot + action for audit and debugging
- Add a **human-in-the-loop** checkpoint (Phase 4b) for sensitive actions (form submissions, purchases)
""")

# ── Demo: Simulated Computer Use Loop ─────────────────────────────────────────
st.markdown("---")
st.markdown("## Live Demo — Simulated Computer Use reasoning loop")
st.caption(
    "This simulation shows the agent's reasoning at each step of a Computer Use task. "
    "The 'UI state' is described in text — in production it would be a real screenshot."
)

SCENARIOS = {
    "Fill a savings form": {
        "task": "Open a NexaBank savings account with £5,000 initial deposit, select NexaSaver product, and submit the form.",
        "ui_states": [
            "SCREEN: NexaBank homepage. Top nav: Home | Products | Login. Hero banner: 'Open an account today'.",
            "SCREEN: Products page. Three cards: NexaCurrent (0.1% cashback), NexaSaver (4.75% AER), NexaFlex ISA (4.2% AER). Each card has an 'Open Account' button.",
            "SCREEN: NexaSaver application form. Fields: Full name [empty], Email [empty], Initial deposit [empty], Date of birth [empty]. Submit button at bottom.",
            "SCREEN: NexaSaver form — partially filled. Full name [John Smith], Email [john@example.com], Initial deposit [£5,000], Date of birth [empty]. Submit button visible.",
            "SCREEN: Confirmation page. 'Application submitted! Your NexaSaver account will be active within 2 business days. Reference: NSA-2026-4471.'",
        ],
        "actions": [
            "left_click on 'Products' in top navigation",
            "left_click on 'Open Account' button on the NexaSaver card",
            "type 'John Smith' in Full name field, type 'john@example.com' in Email field, type '5000' in Initial deposit field",
            "type '15/03/1985' in Date of birth field, then left_click 'Submit'",
            "STOP — task complete. Confirmation received, reference NSA-2026-4471.",
        ],
    },
    "Research competitor rates": {
        "task": "Search for the best UK savings account rates above 4.5% AER and compile a comparison.",
        "ui_states": [
            "SCREEN: Browser — Google search page. Search bar empty.",
            "SCREEN: Google results for 'best UK savings rate above 4.5% AER 2026'. Top results from MoneySavingExpert, ThisIsMoney, Moneyfacts.",
            "SCREEN: MoneySavingExpert page showing savings rate comparison table. Columns: Bank, Account, AER, Min deposit.",
            "SCREEN: Table showing: Chase 5.1%, Atom Bank 4.9%, NatWest 4.8%, NexaBank NexaSaver 4.75%, Barclays 4.6%.",
            "SCREEN: Text document open. Compiled table typed: Chase 5.1%, Atom 4.9%, NatWest 4.8%, NexaBank 4.75%, Barclays 4.6%.",
        ],
        "actions": [
            "type 'best UK savings rate above 4.5% AER 2026' in search bar, press Enter",
            "left_click on MoneySavingExpert result",
            "scroll down to find savings comparison table",
            "read and record: Chase 5.1%, Atom 4.9%, NatWest 4.8%, NexaBank 4.75%, Barclays 4.6%",
            "STOP — task complete. Comparison compiled from MoneySavingExpert data.",
        ],
    },
}

selected_scenario = st.selectbox("Select scenario:", list(SCENARIOS.keys()), key="cu_scenario")
scenario = SCENARIOS[selected_scenario]

st.info(f"**Task:** {scenario['task']}")

if st.button("▶  Run Computer Use simulation", type="primary", key="run_cu"):

    client = _client()

    SYSTEM = (
        "You are a Computer Use agent. You receive a description of what is on screen and the current task. "
        "Decide exactly ONE action to take next: what to click, type, scroll, or whether to stop. "
        "Be concise — one action, one sentence reasoning. "
        "Reply in format: ACTION: <action description> | REASONING: <why>"
    )

    steps_trace = []
    st.markdown("### Action-by-action trace")

    for i, (ui_state, expected_action) in enumerate(
        zip(scenario["ui_states"], scenario["actions"])
    ):
        with st.container(border=True):
            col_screen, col_action = st.columns([1, 1])

            with col_screen:
                st.markdown(f"**Step {i+1} — Screen state:**")
                st.code(ui_state, language="text")

            with col_action:
                if "STOP" in expected_action:
                    st.markdown("**Agent decision:**")
                    st.success(f"STOP — task complete\n\n{expected_action.replace('STOP — ', '')}")
                    steps_trace.append({
                        "step": i + 1, "ui": ui_state, "action": expected_action, "raw": ""
                    })
                    break
                else:
                    prompt = (
                        f"Task: {scenario['task']}\n\n"
                        f"Current screen: {ui_state}\n\n"
                        f"What is your next action?"
                    )
                    with st.spinner(f"Agent deciding step {i+1}..."):
                        resp = _call(
                            client.models.generate_content,
                            model=MODEL,
                            contents=prompt,
                            config=types.GenerateContentConfig(system_instruction=SYSTEM),
                        )
                    agent_decision = resp.text.strip()
                    st.markdown("**Agent decision:**")
                    st.markdown(agent_decision)
                    steps_trace.append({
                        "step": i + 1, "ui": ui_state,
                        "action": expected_action, "raw": agent_decision
                    })

    st.toast("✅ Computer Use simulation complete", icon="🖥️")

    # ── Execution Trace ────────────────────────────────────────────────────────
    def _tab_loop():
        st.markdown("**The Computer Use reasoning loop:**")
        st.code(
            "for each step:\n"
            "  1. Take screenshot (here: read UI state description)\n"
            "  2. Send screenshot + task to LLM\n"
            "  3. LLM returns: action to take\n"
            "  4. Execute action (here: simulated)\n"
            "  5. Take new screenshot\n"
            "  6. Repeat until LLM says STOP",
            language="text",
        )
        st.markdown(f"**Total steps this run:** {len(steps_trace)}")

    def _tab_decisions():
        for s in steps_trace:
            st.markdown(f"**Step {s['step']}:**")
            if s["raw"]:
                st.code(s["raw"], language="text")
            else:
                st.success("STOP — task complete")
            st.markdown("---")

    render_trace(
        ("Loop structure",    _tab_loop),
        ("Agent decisions",   _tab_decisions),
    )

st.markdown("---")
st.markdown("### What's next → Phase 9 — Best Practices")
st.markdown(
    "You have now seen agents in production contexts: customer support, coding, and computer use. "
    "Phase 9 covers the best practices Anthropic recommends for tool design, "
    "prompt engineering, and when NOT to use agents."
)
