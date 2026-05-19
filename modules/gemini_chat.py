"""
gemini_chat.py
--------------
Wrapper around the Google Gemini API (google-generativeai SDK).

Public API
----------
    init_gemini()                          → None
    send_message(history, user_msg)        → str

History format (matches st.session_state list):
    [{"role": "user" | "assistant", "content": "<text>"}, …]
"""

import google.generativeai as genai

from modules.config import GEMINI_API_KEY, CODENIXIA_KNOWLEDGE_BASE

# ── Module-level model instance (initialised once) ────────────────────────────
_model: genai.GenerativeModel | None = None

# System prompt — ground truth knowledge and anti-hallucination constraints
_SYSTEM_PROMPT = f"""You are a helpful, professional, and knowledgeable AI assistant for Codenixia, an AI educational platform and software automation agency.
Your primary role is to answer questions about our courses, internship program, selection timelines, and custom business automation offerings using ONLY the ground-truth company facts below.

---
🔴 CODENIXIA OFFICIAL KNOWLEDGE BASE:
{CODENIXIA_KNOWLEDGE_BASE}
---

⚠️ STRICT ANTI-HALLUCINATION GUIDELINES:
1. Ground Truth constraint: Base your answers ONLY on the official knowledge base listed above. Never invent facts, prices, contact emails, specific office addresses, or custom perks that are not explicitly documented.
2. Handling Out-of-Scope / Missing Info: If the user asks about specific details (such as specialized syllabus topics, custom fees, or details not written above), politely say: "I don't have that specific detail on hand. However, I'd be glad to loop in one of our team members! Please navigate to the '📋 Get in Touch' tab to submit a quick enquiry so we can help you directly."
3. Course and Internship guidelines: When describing how to join our courses or internship program, direct them to navigate to the custom form in the '📋 Get in Touch' tab.
4. Professionalism: Keep your replies structured, clear, friendly, and concise. Feel free to use appropriate bullet points and emojis to enhance readability.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Initialisation
# ─────────────────────────────────────────────────────────────────────────────

def init_gemini() -> None:
    """
    Configure the Gemini client with the API key and warm up the model.
    Call this once at app startup (e.g. from app.py or inside a page).
    Subsequent calls are no-ops.
    """
    global _model
    if _model is not None:
        return  # already initialised

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file and restart the app."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=_SYSTEM_PROMPT,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Messaging
# ─────────────────────────────────────────────────────────────────────────────

def _to_gemini_history(history: list[dict]) -> list[dict]:
    """
    Convert our internal history format to the format Gemini's SDK expects.

    Internal:  {"role": "assistant", "content": "…"}
    Gemini:    {"role": "model",     "parts":   ["…"]}
    """
    converted = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        converted.append({"role": role, "parts": [msg["content"]]})
    return converted


def send_message(conversation_history: list[dict], user_message: str) -> str:
    """
    Send *user_message* to Gemini with the full conversation history as context.

    Args:
        conversation_history:
            All prior turns as a list of {"role": …, "content": …} dicts.
            Pass the current st.session_state["messages"] list **before**
            appending the new user message.
        user_message:
            The latest message typed by the user.

    Returns:
        The assistant's reply as a plain string.
        Returns an error string (never raises) so the UI can display it cleanly.
    """
    global _model
    if _model is None:
        init_gemini()

    try:
        gemini_history = _to_gemini_history(conversation_history)
        chat_session = _model.start_chat(history=gemini_history)
        response = chat_session.send_message(user_message)
        return response.text.strip()

    except Exception as exc:  # noqa: BLE001
        return f"⚠️ Gemini error: {exc}"
