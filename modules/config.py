"""
config.py
---------
Loads environment variables and exposes app-wide settings.
"""

import os
from dotenv import load_dotenv

try:
    import streamlit as st
    for key, val in st.secrets.items():
        os.environ.setdefault(key, str(val))
except Exception:
    pass

# Load env variables immediately upon module import to prevent timing/ordering issues
load_dotenv()


def load_config() -> None:
    """Load .env variables into the environment (call once at startup)."""
    load_dotenv()


# ── Convenience accessors ────────────────────────────────────────────────────

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PATH") or "sqlite:///leads.db"
EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER: str = os.getenv("EMAIL_USER") or os.getenv("GMAIL_EMAIL") or os.getenv("ADMIN_EMAIL") or ""
EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD") or ""
APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "change-me")
DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "admin")

# ── Structured Company Knowledge Base (Ground Truth FAQ Context) ──────────────
CODENIXIA_KNOWLEDGE_BASE = """
CODENIXIA COMPANY OVERVIEW:
Codenixia is a premium educational platform and AI automation agency helping students, developers, and businesses learn and implement state-of-the-art AI, Machine Learning, and LLM automation systems.

OUR MAIN OFFERINGS:
1. 🎓 AI/ML Course:
   - What: A comprehensive 12-week program covering Python, Machine Learning fundamentals, deep learning, NLP, and model evaluation.
   - For whom: Absolute beginners, intermediate developers, and students wanting a solid foothold in AI.
   - Cost: Affordable, merit-based scholarships available.
   
2. 💼 AI / LLM / Automation Internship Program:
   - What: A 4 to 12-week practical hands-on internship.
   - Work area: Building Generative AI chatbots, Prompt engineering, Fine-Tuning LLMs, SQLite/Google Sheets database syncing, and SMTP automation workflows.
   - Perks: Official internship completion certificate, letter of recommendation, and live project deployment portfolios.
   - Selection process: 2-round assessment (Round 1 is a practical business automation project, followed by a technical interaction).

3. 🔍 Business Consultation:
   - What: Custom software audits, business flow automation, and LLM-powered integrations for startups and enterprises.

DASHBOARD & OFFICE DETAILS:
- Location: Mumbai, Maharashtra, India (Hybrid & Remote options).
- Founders/Advisors: Lead automation developers and industry machine learning researchers.
- How to Apply: Interested candidates and students must navigate to the '📋 Get in Touch' tab in our app and submit their details.

FREQUENTLY ASKED QUESTIONS (FAQ):
- Q: What is the internship selection timeline?
  A: Task release is 18th May 2026, 6:00 PM. The submission deadline is 20th May 2026, 6:00 PM.
- Q: Is prior AI knowledge needed for the internship?
  A: Basic Python programming is required. We evaluate execution ability, curiosity, and project completeness over complex pre-existing expertise.
- Q: Is the internship online or offline?
  A: It is fully online/remote, with hybrid meetups for students based in Mumbai.
- Q: How can I apply for a custom automation consultation?
  A: Please use the '📋 Get in Touch' form or email us at support@codenixia.com.
"""
