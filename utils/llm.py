"""
Gemini LLM wrapper — single place to configure the model.
All pages import from here so swapping models means editing one line.
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception
)

load_dotenv()

MODEL = "gemini-2.5-flash"


def _is_retryable(exc: BaseException) -> bool:
    """Retry on 503 / UNAVAILABLE — transient Google capacity spikes."""
    msg = str(exc)
    return "503" in msg or "UNAVAILABLE" in msg


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=api_key)


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=3, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call(fn, *args, **kwargs):
    """Retry wrapper — silently retries up to 4× on 503, with 3–20s backoff."""
    return fn(*args, **kwargs)


def chat(prompt: str, history: list[dict] | None = None, system: str | None = None) -> str:
    """
    Simple single-turn or multi-turn chat.

    Args:
        prompt:  The user's message.
        history: Prior turns — each dict has keys 'role' ('user'/'model') and 'parts' (str).
        system:  Optional system instruction.

    Returns:
        The model's reply as a plain string.
    """
    client = _client()

    if history:
        config = types.GenerateContentConfig(system_instruction=system) if system else None
        convo = client.chats.create(model=MODEL, history=history, config=config)
        response = _call(convo.send_message, prompt)
    else:
        config = types.GenerateContentConfig(system_instruction=system) if system else None
        response = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=config,
        )

    return response.text


def chat_with_tools(
    prompt: str,
    tools: list,
    history: list[dict] | None = None,
    system: str | None = None,
) -> tuple[str, list]:
    """
    Chat with function-calling tools enabled (manual loop — automatic calling disabled).

    Args:
        prompt:  The user's message.
        tools:   List of Python callables — SDK auto-generates the schema.
        history: Prior conversation turns.
        system:  Optional system instruction.

    Returns:
        Tuple of (reply_text, updated_history).
    """
    client = _client()
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=system,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    convo = client.chats.create(model=MODEL, history=history or [], config=config)
    response = _call(convo.send_message, prompt)
    return response.text, convo.get_history()
