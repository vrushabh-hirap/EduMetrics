"""
pages/pg_performance.py
-----------------------
EduMetrics — Page 2: Performance Analysis
Renders Subject-wise Avg Marks table, Grade Distribution table,
and Top 10 Students Leaderboard table with refined UI styling and subtle color accents.
All data comes from st.session_state (populated by app.py).
"""

import pandas as pd
import streamlit as st
from utils.analytics import (
    grade_distribution,
    subject_averages,
    top_students,
)
from utils.icons import icon_academic_cap, icon_clipboard, icon_trophy


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Cohort Breakdown</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Performance Analysis</h1>", unsafe_allow_html=True)
    st.caption(f"Showing **{len(filtered_df)}** student(s) after applying filters.")

    st.divider()

    # ── Summary Tables (Side-by-Side Cards) ──────────────────────────────────
    pa_col1, pa_col2 = st.columns(2)

    with pa_col1:
        st.markdown(
            f'<div class="table-card-header">'
            f'{icon_clipboard(18)} Subject-wise Average Marks'
            f'</div>',
            unsafe_allow_html=True,
        )
        subj_avg_df = subject_averages(filtered_df)
        if not subj_avg_df.empty:
            # Format Average Marks nicely
            display_subj = subj_avg_df.copy()
            display_subj["Average Marks"] = display_subj["Average_Marks"].apply(lambda v: f"{v:.2f}")
            display_subj = display_subj[["Subject", "Average Marks"]]
            st.dataframe(display_subj, use_container_width=True, hide_index=True)
        else:
            st.info("No subject data available for current filters.")

    with pa_col2:
        st.markdown(
            f'<div class="table-card-header">'
            f'{icon_clipboard(18)} Grade Distribution'
            f'</div>',
            unsafe_allow_html=True,
        )
        grade_dist_df = grade_distribution(filtered_df)
        if not grade_dist_df.empty:
            st.dataframe(grade_dist_df, use_container_width=True, hide_index=True)
        else:
            st.info("No grade distribution data available for current filters.")

    st.divider()

    # ── Leaderboard: Top 10 Students ─────────────────────────────────────────
    st.markdown(
        f'<div class="table-card-header" style="font-size: 20px;">'
        f'{icon_trophy(20, color="#d97706")} Top 10 Performing Students'
        f'</div>',
        unsafe_allow_html=True,
    )
    top_df = top_students(filtered_df, n=10)
    if not top_df.empty:
        # Add rank column #1, #2, #3...
        top_df_display = top_df.copy()
        top_df_display.insert(0, "Rank", [f"#{i+1}" for i in range(len(top_df_display))])
        st.dataframe(top_df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No top student data available for current filters.")

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f'<p class="stCaption" style="display: flex; align-items: center; gap: 6px;">'
        f'{icon_academic_cap(16)} <span><strong>EduMetrics</strong> — Student Performance Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit &amp; Plotly</span>'
        f'</p>',
        unsafe_allow_html=True,
    )


render()
