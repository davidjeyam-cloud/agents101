"""
Agentic AI Cookbook — main entry point.
Defines sidebar navigation grouped by phase.
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Agentic AI Cookbook",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation({
    "Phase 0 — Start Here": [
        st.Page("pages/00a_Home.py",              title="Home"),
        st.Page("pages/00c_Agent_Anatomy.py",     title="Agent Anatomy"),
        st.Page("pages/00b_Learning_Insights.py", title="Learning Insights"),
        st.Page("pages/00_Hello_Gemini.py",       title="Hello Gemini"),
        st.Page("pages/0q_Quiz_Hub.py",           title="📝 Quiz Hub"),
    ],
    "Phase 1 — Augmented LLM": [
        st.Page("pages/01_Phase1_Augmented_LLM.py", title="Augmented LLM"),
    ],
    "Phase 2 — Workflow Patterns": [
        st.Page("pages/02a_Prompt_Chaining.py",       title="2a — Prompt Chaining"),
        st.Page("pages/02b_Routing.py",               title="2b — Routing"),
        st.Page("pages/02c_Parallelization.py",       title="2c — Parallelization"),
        st.Page("pages/02d_Orchestrator_Workers.py",  title="2d — Orchestrator-Workers"),
        st.Page("pages/02e_Evaluator_Optimizer.py",   title="2e — Evaluator-Optimizer"),
    ],
    "Phase 3 — Core Agent Patterns": [
        st.Page("pages/03_Agents.py",          title="3a — ReAct Agent"),
        st.Page("pages/03f_Reflection.py",     title="3b — Reflection Agent (was 3f)"),
        st.Page("pages/03f2_Planning.py",      title="3c — Planning Agent"),
        st.Page("pages/03g2_CodeExec.py",      title="3d — Code Execution Tool"),
        st.Page("pages/03p_PatternCompare.py", title="3e — Pattern Decision Guide"),
    ],
    "Phase 4 — Trust & Safety": [
        st.Page("pages/03b_Guardrails.py",   title="4a — Guardrails (was 3b)"),
        st.Page("pages/03c_HITL.py",         title="4b — Human-in-the-Loop (was 3c)"),
        st.Page("pages/03e_LLM_Judge.py",    title="4c — LLM-as-Judge (was 3e)"),
        st.Page("pages/03m_Evals.py",        title="4d — Evaluation Framework"),
    ],
    "Phase 5 — Knowledge & Memory": [
        st.Page("pages/03d_RAG_Agent.py",    title="5a — RAG Agent (was 3d)"),
        st.Page("pages/03i_LongMemory.py",   title="5b — Long-term Memory"),
    ],
    "Phase 6 — Multi-Agent & Protocols": [
        st.Page("pages/03g_MultiAgent.py",   title="6a — Multi-Agent"),
        st.Page("pages/03j_MCP.py",          title="6b — MCP Protocol"),
        st.Page("pages/03k_A2A.py",          title="6c — A2A Protocol"),
        st.Page("pages/03l_AgentComms.py",   title="6d — Agent Communications"),
    ],
    "Phase 7 — Production Operations": [
        st.Page("pages/03h_Observability.py", title="7a — Observability"),
        st.Page("pages/03n_CostLatency.py",   title="7b — Cost & Latency"),
        st.Page("pages/03o_ErrorAnalysis.py", title="7c — Error Analysis"),
    ],
    "Phase 8 — Agents in Practice": [
        st.Page("pages/04a_Customer_Support.py",  title="8a — Customer Support Agent"),
        st.Page("pages/04a1_Elite_Agent.py",      title="8a.1 — Elite Multi-Agent System"),
        st.Page("pages/04b_Coding_Agent.py",      title="8b — Coding Agent 🔜"),
    ],
    "Phase 9 — Best Practices": [
        st.Page("pages/05_Best_Practices.py", title="9 — Best Practices"),
    ],
    "Phase 10 — Frameworks": [
        st.Page("pages/06a_LangGraph_Workflows.py", title="10a — LangGraph Workflows 🔜"),
        st.Page("pages/06b_LangGraph_Agents.py",    title="10b — LangGraph Agents 🔜"),
        st.Page("pages/06c_LangSmith.py",           title="10c — LangSmith 🔜"),
        st.Page("pages/06d_LangChain.py",           title="10d — LangChain 🔜"),
        st.Page("pages/06e_GoogleADK.py",           title="10e — Google ADK 🔜"),
        st.Page("pages/06f_Framework_Compare.py",   title="10f — Framework Compare 🔜"),
    ],
    "Phase 11 — Managed Platforms": [
        st.Page("pages/07a_VertexAI.py",    title="11a — Vertex AI 🔜"),
        st.Page("pages/07b_Azure.py",       title="11b — Azure AI 🔜"),
        st.Page("pages/07c_Bedrock.py",     title="11c — AWS Bedrock 🔜"),
        st.Page("pages/07d_OpenAI.py",      title="11d — OpenAI Assistants 🔜"),
        st.Page("pages/07e_Platforms.py",   title="11e — Platform Compare 🔜"),
    ],
})

pg.run()
