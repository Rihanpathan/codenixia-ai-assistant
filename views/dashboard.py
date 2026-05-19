"""
pages/dashboard.py
------------------
Admin Dashboard page — called via show() from app.py.

Password-protected via DASHBOARD_PASSWORD from modules/config.py.

Sections (authenticated only):
  • 4 KPI metric tiles  — Total / Hot / Warm / Cold leads
  • Searchable leads table with CSV export button
  • Top-5 most-asked chatbot questions table
"""

import streamlit as st
import pandas as pd

from modules.config import DASHBOARD_PASSWORD
from modules.database import get_all_leads, get_top_questions
from modules.email_service import send_daily_report


def show() -> None:
    """Render the Admin Dashboard page."""

    # ── Password gate ─────────────────────────────────────────────────────────
    if "dashboard_authenticated" not in st.session_state:
        st.session_state.dashboard_authenticated = False

    if not st.session_state.dashboard_authenticated:
        st.title("🔒 Admin Dashboard")
        st.markdown("This area is restricted. Enter the dashboard password to continue.")

        with st.form("login_form"):
            password_input = st.text_input(
                "Password",
                type="password",
                placeholder="Enter dashboard password…",
            )
            login_submitted = st.form_submit_button(
                "Unlock Dashboard 🔓", use_container_width=True
            )

        if login_submitted:
            if password_input == DASHBOARD_PASSWORD:
                st.session_state.dashboard_authenticated = True
                st.rerun()
            else:
                st.warning("⚠️ Incorrect password. Please try again.")

        st.stop()  # nothing below renders until authenticated

    # ── Authenticated view ────────────────────────────────────────────────────

    # Sidebar: logout button
    with st.sidebar:
        st.markdown("---")
        st.success("✅ Authenticated")
        if st.button("🔒 Log out", use_container_width=True):
            st.session_state.dashboard_authenticated = False
            st.rerun()

    st.title("📊 Admin Dashboard")
    st.caption("Live data from your SQLite database · Refresh the page to update.")

    # ── Fetch data ────────────────────────────────────────────────────────────
    df: pd.DataFrame = get_all_leads()
    total = len(df)

    # ── KPI tiles ─────────────────────────────────────────────────────────────
    if total > 0:
        raw_cats = df["category"].astype(str)
        hot  = raw_cats.str.startswith("Hot").sum()
        warm = raw_cats.str.startswith("Warm").sum()
        cold = raw_cats.str.startswith("Cold").sum()
    else:
        hot = warm = cold = 0

    # ── KPI tiles ─────────────────────────────────────────────────────────────
    if total > 0:
        raw_cats = df["category"].astype(str)
        hot  = raw_cats.str.startswith("Hot").sum()
        warm = raw_cats.str.startswith("Warm").sum()
        cold = raw_cats.str.startswith("Cold").sum()
    else:
        hot = warm = cold = 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div style="background-color: #EFF6FF; border-left: 5px solid #3B82F6; border-radius: 8px; padding: 15px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                <div style="font-size: 11px; font-weight: 700; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.5px;">📋 Total Leads</div>
                <div style="font-size: 26px; font-weight: 800; color: #1E3A8A; margin-top: 5px;">{total}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div style="background-color: #FDF2F2; border-left: 5px solid #EF4444; border-radius: 8px; padding: 15px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                <div style="font-size: 11px; font-weight: 700; color: #EF4444; text-transform: uppercase; letter-spacing: 0.5px;">🔥 Hot Leads</div>
                <div style="font-size: 26px; font-weight: 800; color: #9B1C1C; margin-top: 5px;">{hot}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div style="background-color: #FFFBEB; border-left: 5px solid #F59E0B; border-radius: 8px; padding: 15px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                <div style="font-size: 11px; font-weight: 700; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.5px;">🌤️ Warm Leads</div>
                <div style="font-size: 26px; font-weight: 800; color: #92400E; margin-top: 5px;">{warm}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div style="background-color: #F9FAFB; border-left: 5px solid #6B7280; border-radius: 8px; padding: 15px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px;">❄️ Cold Leads</div>
                <div style="font-size: 26px; font-weight: 800; color: #374151; margin-top: 5px;">{cold}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # ── Interest Distribution Bar Chart ───────────────────────────────────────
    if total > 0:
        st.subheader("📈 Lead Interest Distribution")
        interest_counts = df["interest"].value_counts()
        st.bar_chart(interest_counts, color="#4F46E5")

    st.divider()

    # ── Leads table ───────────────────────────────────────────────────────────
    st.subheader("📋 Captured Leads Database")

    if df.empty:
        st.info("No leads captured yet. Use **Get in Touch** to submit the first one.")
    else:
        st.markdown("##### 🔍 Search and Filter Leads")
        search = st.text_input(
            "search",
            placeholder="Type candidate name, email, interest, or category to filter...",
            label_visibility="collapsed",
        )

        display_df = df.copy()

        if search.strip():
            mask = display_df.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            display_df = display_df[mask]

        col_order = [
            c for c in
            ["id", "name", "email", "phone", "interest",
             "score", "category", "message", "timestamp"]
            if c in display_df.columns
        ]
        display_df = display_df[col_order]

        # Style Category cells
        def style_category(val):
            if "Hot" in str(val):
                return "color: #E02424; font-weight: bold; background-color: #FDF2F2;"
            elif "Warm" in str(val):
                return "color: #D97706; font-weight: bold; background-color: #FEF9C3;"
            elif "Cold" in str(val):
                return "color: #0284C7; font-weight: bold; background-color: #E0F2FE;"
            return ""

        try:
            styled_df = display_df.style.map(style_category, subset=["category"])
        except AttributeError:
            styled_df = display_df.style.applymap(style_category, subset=["category"])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id":        st.column_config.NumberColumn("ID", width="small"),
                "score":     st.column_config.ProgressColumn(
                                 "Score", min_value=0, max_value=100, format="%d"
                             ),
                "timestamp": st.column_config.DatetimeColumn(
                                 "Submitted", format="D MMM YYYY, HH:mm"
                             ),
            },
        )

        st.caption(f"Showing **{len(display_df)}** of **{total}** leads")

        btn1, btn2 = st.columns(2)
        with btn1:
            csv_bytes = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Export as CSV",
                data=csv_bytes,
                file_name="codenixia_leads.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with btn2:
            if st.button("📨 Send Daily Report", use_container_width=True):
                with st.spinner("Generating and sending report…"):
                    success = send_daily_report(df)
                if success:
                    st.success("✅ Daily lead summary report has been sent to the Admin email!")
                else:
                    st.error("⚠️ Failed to send daily report. Please verify your SMTP settings in .env.")

    st.divider()

    # ── Top-5 chatbot questions ───────────────────────────────────────────────
    st.subheader("💬 Top 5 Most-Asked Chatbot Questions")

    top_q: pd.DataFrame = get_top_questions(limit=5)

    if top_q.empty:
        st.info("No chat history yet. Start a conversation in **Chat Assistant**.")
    else:
        top_q.index = top_q.index + 1
        top_q.index.name = "Rank"

        st.dataframe(
            top_q,
            use_container_width=True,
            column_config={
                "question": st.column_config.TextColumn("Question",    width="large"),
                "count":    st.column_config.NumberColumn("Times Asked", width="small"),
            },
        )
