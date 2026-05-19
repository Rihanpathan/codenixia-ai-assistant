"""
pages/lead_form.py
------------------
Get in Touch page — called via show() from app.py.

Fields:   Full Name*, Email*, Phone, Interested In (dropdown), Message
On submit: validate → score → save to DB → send both emails → success banner
"""

import streamlit as st

from modules.database import save_lead
from modules.lead_scoring import compute_score, classify_lead
from modules.email_service import send_lead_notification, send_lead_confirmation


def show() -> None:
    """Render the Get in Touch / Lead Capture page."""

    # ── Form Card Styling Overrides ────────────────────────────────────────────
    st.markdown(
        """
        <style>
        /* Styles Streamlit Form as a premium card */
        div[data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
            border-radius: 12px !important;
            padding: 30px !important;
            margin-bottom: 25px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Hero Section ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 30px; border-radius: 12px; margin-bottom: 25px; color: white;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: white; border: none; font-family: sans-serif;">📋 Join the Codenixia Platform</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px; color: #E0E7FF; font-weight: 500; font-family: sans-serif; line-height: 1.5;">
                Submit your profile details below to register for the AI/ML course, apply for our practical internship, or schedule a custom business automation audit.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Process Indicator Cards ────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 25px;">
            <div style="flex: 1; background-color: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 13px; font-weight: 700; color: #4F46E5;">1. Fill Form 📝</span>
            </div>
            <div style="color: #9CA3AF; font-weight: bold; font-size: 16px;">➔</div>
            <div style="flex: 1; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: #4B5563;">2. AI Scores Lead 🤖</span>
            </div>
            <div style="color: #9CA3AF; font-weight: bold; font-size: 16px;">➔</div>
            <div style="flex: 1; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: #4B5563;">3. Confirmation 📨</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Form ──────────────────────────────────────────────────────────────────
    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name  = st.text_input("Full Name *",     placeholder="Jane Doe")
            email = st.text_input("Email Address *", placeholder="jane@example.com")
            phone = st.text_input("Phone Number",    placeholder="+91 98765 43210")

        with col2:
            interest = st.selectbox(
                "Interested In *",
                ["Select…", "AI/ML Course", "Internship Program", "Consultation", "Other"],
            )
            message = st.text_area(
                "Message (optional)",
                placeholder="Tell us a bit about what you're looking for…",
                height=138,
            )

        submitted = st.form_submit_button("Send Message 🚀", use_container_width=True)

    # ── Validation & processing ────────────────────────────────────────────────
    if submitted:
        errors = []
        if not name.strip():
            errors.append("Full Name is required.")
        if not email.strip():
            errors.append("Email Address is required.")
        if interest == "Select…":
            errors.append("Please select an area of interest.")

        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        else:
            lead_data = {
                "name":     name.strip(),
                "email":    email.strip(),
                "phone":    phone.strip(),
                "interest": interest,
                "message":  message.strip(),
            }

            # Score & classify
            score             = compute_score(lead_data)
            category          = classify_lead(score)
            lead_data["score"]    = score
            lead_data["category"] = category

            # Persist to SQLite
            saved = save_lead(lead_data)

            # Outbound emails (non-blocking — failures are logged, not raised)
            send_lead_notification(lead_data)
            send_lead_confirmation(lead_email=email.strip(), lead_name=name.strip())

            # Trigger Balloon Celebration!
            st.balloons()

            # Success card
            st.markdown(
                f"""
                <div style="background-color: #DEF7EC; border-left: 5px solid #0E9F6E; border-radius: 8px; padding: 20px; margin-bottom: 20px; color: #03543F;">
                    <h3 style="margin: 0 0 5px 0; color: #03543F; font-size: 18px; font-weight: 700;">🎉 Application Submitted Successfully!</h3>
                    <p style="margin: 0; font-size: 14px; color: #046C4E; font-weight: 500;">
                        Thanks, <b>{name.split()[0]}</b>! Our AI has scored your entry, logged it to our sqlite database, and successfully dispatched confirmation emails!
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Badge mapping
            badge_style = ""
            if "Hot" in category:
                badge_style = "background-color: #FDF2F2; color: #E02424; border: 1px solid #F87171;"
            elif "Warm" in category:
                badge_style = "background-color: #FEF9C3; color: #D97706; border: 1px solid #FBBF24;"
            else:
                badge_style = "background-color: #E0F2FE; color: #0284C7; border: 1px solid #38BDF8;"

            # Lead Badges
            st.markdown(
                f"""
                <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 25px;">
                    <div style="background-color: #EEF2FF; border: 1px solid #C7D2FE; padding: 12px 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 10px; font-weight: 700; color: #4F46E5; letter-spacing: 0.5px; text-transform: uppercase;">Lead Score</div>
                        <div style="font-size: 20px; font-weight: 800; color: #1F2937;">{score} <span style="font-size: 12px; color: #6B7280; font-weight: 500;">/ 100</span></div>
                    </div>
                    <div style="{badge_style} padding: 12px 20px; border-radius: 8px; text-align: center; flex-grow: 1;">
                        <div style="font-size: 10px; font-weight: 700; opacity: 0.8; letter-spacing: 0.5px; text-transform: uppercase;">Lead Temperature</div>
                        <div style="font-size: 18px; font-weight: 800;">{category}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not saved:
                st.warning("⚠️ Your message was received but could not be saved to the database.")
