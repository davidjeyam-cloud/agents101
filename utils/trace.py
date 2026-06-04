"""
render_trace() — standardised Execution Trace expander.
Ensures every LLM page has a consistent title, tab numbering, and structure.

Usage (single tab):
    render_trace(("LLM Call", fn))

Usage (multi-tab):
    render_trace(
        ("LLM Call",        fn_call),
        ("Raw Output",      fn_raw),
        ("Decision Logic",  fn_logic),
    )

Each fn is a zero-argument callable that renders its tab content.
Inner functions with closures work naturally:

    def _tab_call():
        st.code(system_prompt)
        st.code(user_msg)

    def _tab_raw():
        st.code(raw_response)

    render_trace(("LLM Call", _tab_call), ("Raw Output", _tab_raw))
"""

import streamlit as st

_NUMS = "①②③④⑤"
TRACE_TITLE = "🔬 Execution Trace — exact prompts and raw responses"


def render_trace(*sections: tuple) -> None:
    """
    Render a standardised Execution Trace expander.

    sections: one or more (label, render_fn) tuples
    Single section: content rendered without a tab bar.
    Multiple sections: each gets a numbered tab ①②③...
    """
    with st.expander(TRACE_TITLE):
        if not sections:
            return
        if len(sections) == 1:
            sections[0][1]()
        else:
            tab_labels = [f"{_NUMS[i]} {lbl}" for i, (lbl, _) in enumerate(sections)]
            tabs = st.tabs(tab_labels)
            for tab, (_, fn) in zip(tabs, sections):
                with tab:
                    fn()
