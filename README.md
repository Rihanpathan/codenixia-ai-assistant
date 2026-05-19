# 🤖 Codenixia AI-Powered Business Automation Assistant

Welcome to the **Codenixia AI-Powered Business Automation Assistant** repository! This application is built as a complete, production-grade assessment project for the **Codenixia AI / LLM / Automation Internship Program (Round 1)**.

The system is designed to act as an automated front-desk assistant, lead management, and analytics dashboard for the Codenixia platform, demonstrating **AI/LLM integration**, **multi-layered automation workflows**, **offline SQLite database logging**, and **interactive analytics dashboard engineering**.

---

## 🚀 Live Demo & Deployment
*   **GitHub Repository:** https://github.com/Rihanpathan/codenixia-ai-assistant
*   **Live Hosted App:** https://rihanpathan-codenixia-ai-assistant-app-mjvpun.streamlit.app
*   **5-7 Min Demo Video:** 

---

## 📊 System Architecture Diagram

![System Architecture Diagram](architecture.png)

Below is the conceptual architecture showing how data, AI, databases, and SMTP email services interact seamlessly:

```
                  ┌────────────────────────────────────────┐
                  │           USER INTERACTION             │
                  │  (Streamlit Unified Frontend Web App)  │
                  └───────────┬────────────────┬───────────┘
                              │                │
              [Form Submission]                [Chat Message Input]
                              │                │
                              ▼                ▼
                  ┌───────────────┐        ┌──────────────────┐
                  │Lead Validation│        │Gemini 1.5-Flash  │
                  └───────┬───────┘        │AI Chatbot Engine │
                          │                └────────┬─────────┘
                   [Quality Score]                  │
                          │                         ▼
                          ▼                ┌──────────────────┐
                  ┌───────────────┐        │ SQLite DB Sync   │
                  │ SQLite DB Log │        │ (chat_history)   │
                  │    (leads)    │        └──────────────────┘
                  └───────┬───────┘
                          │
         ┌────────────────┴───────────────┐
         │  AUTOMATION WORKFLOW TRIGGERS  │
         └────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌──────────────┐        ┌─────────────┐
│  SMTP Email  │        │ SMTP Email  │        ┌──────────────────┐
│ Confirmation │        │ Notification│        │ Admin Dashboard  │
│  (to User)   │        │  (to Admin) │ ◄────► │ password-secured │
└──────────────┘        └─────────────┘        │  metrics & logs  │
                                               └──────────────────┘
```

---

## ⚡ Mandatory Modules & Coverage (100% Satisfied)

This project satisfies and exceeds every single mandatory and stack parameter required in the assessment:

### 1. 💬 AI Assistant / Chatbot (100% Covered)
*   **Implementation:** Developed inside [`views/chatbot.py`](views/chatbot.py) and [`modules/gemini_chat.py`](modules/gemini_chat.py).
*   **Capabilities:** Integrates the state-of-the-art **Google Gemini 1.5-Flash** API. Includes a tailored system instruction instructing the AI to behave as a helpful Codenixia course advisor.
*   **Memory:** Manages stateful conversation histories (`st.session_state.messages`) ensuring multi-turn context preservation.
*   **Analytics:** Automatically logs every Q&A pair with timestamps to database.

### 2. 📝 Lead Capture System (100% Covered)
*   **Implementation:** Located in [`views/lead_form.py`](views/lead_form.py).
*   **Capabilities:** Captures Name, Email, Phone, Course/Interest selection, and Message details.
*   **Lead Scoring Logic:** Instantly evaluates leads from `0–100` inside [`modules/lead_scoring.py`](modules/lead_scoring.py) based on profile parameters (domain validity, phone presence, message depth, and interest alignment) classifying them instantly as `Hot 🔥`, `Warm 🌤️`, or `Cold ❄️`.

### 3. 💾 Data Storage (100% Covered)
*   **Implementation:** Handled via context-managed thread-safe SQLite connection in [`modules/database.py`](modules/database.py).
*   **Tables:** 
    *   `leads` (Stores details, category, quality scores, and timestamps).
    *   `chat_history` (Stores user questions and assistant answers for statistics).
*   **Resiliency:** Dynamic schema migrations verify columns and tables on startup to prevent system crashes.

### 4. ⚙️ Automation Workflows (100% Covered - Multi-layered!)
*   **Workflow 1 (Form Submission ➡️ Email Automation):** When a lead is captured, it immediately executes two non-blocking TLS SMTP emails inside [`modules/email_service.py`](modules/email_service.py):
    1.  **User Confirmation:** Welcoming them to Codenixia with dynamic name rendering.
    2.  **Admin Notification:** Alerting the administrative email of a new candidate with full details and quality scores.
*   **Workflow 2 (Lead Capture ➡️ Live SQLite Logging):** Commits lead details immediately.
*   **Workflow 3 (Chatbot ➡️ Live Analytics Logging):** Deduplicates chat questions to log the top 5 most frequently asked questions.

### 5. 📊 Admin Dashboard / View (100% Covered)
*   **Implementation:** Securely password-gated dashboard inside [`views/dashboard.py`](views/dashboard.py).
*   **Capabilities:**
    *   **4 KPI Metric Tiles:** Total Leads, Hot, Warm, and Cold lead distribution.
    *   **Instant Filtering:** Interactive text-search to filter leads by name, email, interest, or scores.
    *   **Data Export:** Live **Export as CSV** button.
    *   **Chat Statistics:** Rendered top-5 most asked chatbot questions sorted by frequency.
    *   **Report Generation:** A **Send Daily Report** button that compiles today's leads metrics, builds a responsive HTML summary, and emails it to the Admin.

---

## 🛠️ Technology Stack Breakdown
*   **Frontend Framework:** Python Streamlit
*   **AI Engine:** Google Gemini Generative AI SDK (`google-generativeai`)
*   **Database:** SQLite (`sqlite3` with thread-safe Connection Wrapper)
*   **Data Engine:** Pandas
*   **Email Automation:** Gmail SMTP (Secure TLS protocol)
*   **Environment Config:** `python-dotenv`

---

## 💻 Local Installation & Setup

Get the server running on your computer in just 3 steps:

### 1. Clone the Repository & Install Dependencies
```bash
git clone https://github.com/your-profile/codenixia-ai-assistant.git
cd codenixia-ai-assistant
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a file named `.env` in the root directory and paste your configuration:
```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Admin Settings
DASHBOARD_PASSWORD=admin

# Email SMTP Settings (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_google_app_password_here
```
> ⚠️ **SMTP note:** Gmail requires creating a secure 16-character **App Password** under Google Account settings ➡️ Security to send automated emails.

### 3. Launch the Server
```bash
streamlit run app.py
```
This automatically initiates database tables and opens the frontend at:
👉 **`http://localhost:8501`**

---

## ☁️ Streamlit Cloud Deployment Guide
1. Push this complete project structure to your private/public **GitHub** repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and link your GitHub.
3. Deploy a new application selecting your repository and specifying `app.py` as the entrypoint.
4. Paste the content of your local `.env` into the **Advanced Settings ➡️ Secrets** section.
5. Launch! Streamlit handles live deployments and auto-updates on every push to your main branch!
