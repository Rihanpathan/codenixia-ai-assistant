"""
pages/chatbot.py
----------------
Chat Assistant page — called via show() from app.py.

Features:
• Full conversation rendered with st.chat_message / st.chat_input
• Entire history stored in st.session_state → memory preserved across turns
• Every user ↔ assistant exchange saved to SQLite via modules/database.py
• Sidebar section: clear chat button + live top-5 questions
"""

import streamlit as st

from modules.gemini_chat import init_gemini, send_message
from modules.database import save_chat_exchange, get_top_questions


# ── Gemini: module-level initialization flag (avoids Streamlit module-level side-effects) ──
_gemini_initialized = False
_gemini_error = ""


def show() -> None:
    """Render the Chat Assistant page."""
    global _gemini_initialized, _gemini_error

    # ── Try to initialise Gemini ──────────────────────────────────────────────
    gemini_ready = True
    gemini_error = ""

    if not _gemini_initialized:
        try:
            init_gemini()
            _gemini_initialized = True
        except ValueError as exc:
            _gemini_error = str(exc)

    if _gemini_error:
        gemini_ready = False
        gemini_error = _gemini_error

    # ── Session state ─────────────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages: list[dict] = []

    # ── CSS Overrides for Premium Chat bubbles ─────────────────────────────────
    st.markdown(
        """
        <style>
        /* Custom styled chat messages for a professional app look */
        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]),
        div[data-testid="stChatMessage"]:has(span[data-testid="chatAvatarIcon-user"]),
        div[data-testid="stChatMessage"]:has(img[alt="user"]) {
            background-color: #EEF2FF !important;
            border: 1px solid #C7D2FE !important;
            border-radius: 14px !important;
            padding: 12px 16px !important;
            margin-bottom: 15px !important;
        }

        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]),
        div[data-testid="stChatMessage"]:has(span[data-testid="chatAvatarIcon-assistant"]),
        div[data-testid="stChatMessage"]:has(img[alt="assistant"]) {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
            border-radius: 14px !important;
            padding: 12px 16px !important;
            margin-bottom: 15px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar extras (within this page) ────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔥 Top 5 Questions")
        top_q = get_top_questions(limit=5)
        if top_q.empty:
            st.caption("No questions recorded yet.")
        else:
            for _, row in top_q.iterrows():
                st.markdown(f"- **{row['count']}×** {row['question']}")

    # ── Page header ───────────────────────────────────────────────────────────
    header_col, btn_col = st.columns([4, 1])
    with header_col:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                <span style="font-size: 32px;">🤖</span>
                <div>
                    <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #1F2937; line-height: 1.2;">Codenixia AI Assistant</h1>
                    <p style="margin: 0; font-size: 13px; color: #6B7280; font-weight: 500;">Grounded course details, timelines, & consultation advisor</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with btn_col:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # ── API key guard ─────────────────────────────────────────────────────────
    if not gemini_ready:
        st.error(f"🔑 {gemini_error}")
        st.info("Set **GEMINI_API_KEY** in your `.env` file and restart the app.")
        st.stop()

    # ── Render existing conversation ──────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Welcome bubble when history is empty ──────────────────────────────────
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                """
                👋 **Welcome to the Codenixia AI Assistant!**
                
                I'm your grounded course and business automation advisor. I can answer questions accurately using our official company knowledge base.
                
                **Here are 3 example questions you can ask me to get started:**
                1. 📝 *How can I join the Codenixia AI/LLM Internship Program?*
                2. 🎓 *What topics are covered in the 12-week AI/ML course?*
                3. ⏰ *What is the submission deadline for the Round 1 internship project?*
                
                *Simply type your question in the chat input bar below!*
                """
            )

    # ── Handle new user input ─────────────────────────────────────────────────
    if prompt := st.chat_input("Ask me anything…"):

        # 1. Show & store the user's message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Pass full prior history so Gemini has multi-turn context
        prior_history = st.session_state.messages[:-1]

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = send_message(prior_history, prompt)
            st.markdown(reply)

        # 3. Store the reply
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 4. Persist to SQLite
        save_chat_exchange(question=prompt, response=reply)
