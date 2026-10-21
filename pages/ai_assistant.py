"""
NexHR - Tab 07: AI Assistant (Groq)
A strictly scoped chat interface. The assistant can only analyze data
already in NexHR via a fixed set of read-only functions -- see
services/ai_service.py for the enforced boundaries.
"""
import streamlit as st

from services import ai_service
from assets.theme import page_header

SUGGESTED_QUESTIONS = [
    "What is our current monthly payroll?",
    "Who are the top 3 performers right now?",
    "How much are we spending on canteen perks?",
    "Give me a status summary of all projects.",
    "Which department has the highest salary cost?",
]


def render():
    page_header("AI Assistant", "Ask questions about authorized workforce data")

    st.caption("Powered by Groq. Strictly limited to analyzing this company's HR data — "
               "it cannot modify records, hire/fire anyone, send messages, or access anything outside this dataset.")

    if not ai_service.is_configured():
        st.warning("No GROQ_API_KEY found in your `.env` file. Add one to enable the assistant "
                   "— a free key is available at https://console.groq.com/keys")

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    st.markdown("**Try asking:**")
    qcols = st.columns(len(SUGGESTED_QUESTIONS))
    for col, question in zip(qcols, SUGGESTED_QUESTIONS):
        if col.button(question, width='stretch'):
            st.session_state["pending_question"] = question

    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about employees, salary, performance, projects, or hiring...")
    pending = st.session_state.pop("pending_question", None)
    question = user_input or pending

    if question:
        st.session_state.ai_chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing company data..."):
                history_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.ai_chat_history[:-1][-6:]  # short rolling context
                ]
                answer = ai_service.ask_assistant(question, chat_history=history_for_api)
                st.markdown(answer)
        st.session_state.ai_chat_history.append({"role": "assistant", "content": answer})

    if st.session_state.ai_chat_history:
        if st.button("Clear conversation"):
            st.session_state.ai_chat_history = []
            st.rerun()
