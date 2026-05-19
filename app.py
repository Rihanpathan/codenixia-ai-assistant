"""
app.py
------
Single entry point for the Codenixia AI Assistant Streamlit app.

Navigation is handled here via a sidebar radio button.
Each page module exposes a show() function that renders its content.
"""

import importlib
import streamlit as st

from modules.config import load_config
from modules.database import init_db

# ── Must be the very first Streamlit call ─────────────────────────────────────
st.set_page_config(
    page_title="Codenixia AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS Overrides for Premium SaaS Aesthetics ──────────────────────────
st.markdown(
    """
    <style>
    /* Hide Streamlit default hamburger, footer, and deploy header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global page transition animation */
    

    /* Styled buttons with smooth lift & shadow hover effects */
    button[data-testid^="baseButton-"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button[data-testid^="baseButton-"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12) !important;
    }
    button[data-testid^="baseButton-"]:active {
        transform: translateY(1px) !important;
    }

    /* Premium card overlays for default Streamlit metrics */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid #F3F4F6 !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Bootstrap: load env vars and create DB tables ─────────────────────────────
load_config()
init_db()

# ── Dynamic Theme Management ──────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if st.session_state.theme == "dark":
    st.markdown(
        """
        <style>
        /* Force slate dark mode aesthetics globally */
        .stApp {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
        }
        /* Sidebar background & border */
        section[data-testid="stSidebar"] {
            background-color: #1E293B !important;
            border-right: 1px solid #334155 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        /* Text structures and headers */
        h1, h2, h3, h4, h5, h6, span, label, p, small, caption, li {
            color: #F8FAFC !important;
        }
        /* Metrics values overrides */
        div[data-testid="stMetricValue"] {
            color: #F8FAFC !important;
        }
        /* Metric Card overrides in Dark Mode */
        div[data-testid="metric-container"] {
            background-color: #1E293B !important;
            border-color: #334155 !important;
        }
        /* Forms, inputs, dropdown selectors */
        div[data-testid="stForm"] {
            background-color: #1E293B !important;
            border-color: #334155 !important;
        }
        input, textarea, select {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 1px solid #475569 !important;
        }
        div[role="listbox"] {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
        }
        /* Dataframes & Table panels styling */
        div[data-testid="stDataFrame"] {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
        }
        /* Notification banners override */
        div[data-testid="stNotification"] {
            background-color: #334155 !important;
            color: #F8FAFC !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── Page registry ─────────────────────────────────────────────────────────────
PAGES = {
    "💬 Chat Assistant":   "views.chatbot",
    "📋 Get in Touch":     "views.lead_form",
    "📊 Admin Dashboard":  "views.dashboard",
}

# ── Premium Custom-Styled Sidebar Navigation ──────────────────────────────────
with st.sidebar:
    # 1. Custom SVG & Gradient Logo
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 12px; padding: 15px 5px; margin-bottom: 5px;">
            <svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="border-radius: 8px;">
                <rect width="100" height="100" rx="24" fill="#4F46E5"/>
                <path d="M30 30H70V70H30V30Z" stroke="white" stroke-width="8" stroke-linejoin="round"/>
                <path d="M45 45L55 55M55 45L45 55" stroke="white" stroke-width="8" stroke-linecap="round"/>
            </svg>
            <span style="font-size: 22px; font-weight: 800; font-family: 'Outfit', 'Inter', sans-serif; background: linear-gradient(135deg, #4F46E5 0%, #818CF8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">Codenixia</span>
        </div>
        <div style="height: 1px; background-color: #E5E7EB; margin-bottom: 20px;"></div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Premium Navigation Radio Menu
    selection = st.radio(
        "Navigate to",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    # 3. Dynamic Theme Toggle Button
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    theme_emoji = "🌙" if st.session_state.theme == "light" else "☀️"
    theme_label = "Switch to Dark Mode" if st.session_state.theme == "light" else "Switch to Light Mode"
    if st.button(f"{theme_emoji} {theme_label}", use_container_width=True):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

    # 4. System Engine Info Box
    st.markdown(
        """
        <div style="margin-top: 40px; background-color: #EEF2FF; border-left: 4px solid #4F46E5; border-radius: 6px; padding: 12px;">
            <div style="font-size: 10px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: 0.8px;">SYSTEM ENGINE</div>
            <div style="font-size: 12px; font-weight: 600; color: #1F2937; margin-top: 3px; display: flex; align-items: center; gap: 4px;">
                ⚡ AI Powered by Gemini
            </div>
            <div style="font-size: 11px; color: #4B5563; margin-top: 3px;">Model 2.5-Flash is active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Premium Footer
    st.markdown(
        """
        <div style="margin-top: auto; padding-top: 30px; text-align: center;">
            <div style="height: 1px; background-color: #E5E7EB; margin-bottom: 12px;"></div>
            <div style="font-size: 11px; color: #9CA3AF; font-family: sans-serif; line-height: 1.4;">
                © 2026 Codenixia AI<br/>
                <span style="font-weight: 600; color: #6B7280;">Assistant v1.0.0</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Render the selected page ──────────────────────────────────────────────────
page_module = importlib.import_module(PAGES[selection])
page_module.show()
