"""
pages/pg_at_risk.py
-------------------
EduMetrics — Page 4: At-Risk Students
Renders threshold summary, 4 color-accented status metric cards,
the risk score bar chart (top), and the flagged student table (stacked below).
All data comes from st.session_state (populated by app.py).
"""

import streamlit as st
from utils.charts import at_risk_bar
from utils.icons import (
    icon_academic_cap,
    icon_clipboard,
    icon_trending_down,
)
from utils.risk_detection import flag_at_risk, risk_summary


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df
    marks_threshold = st.session_state.marks_threshold
    attendance_threshold = st.session_state.attendance_threshold

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Early Warning System</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>At-Risk Student Analysis</h1>", unsafe_allow_html=True)
    st.caption(
        f"Thresholds: Avg Marks < **{marks_threshold}** | "
        f"Attendance < **{attendance_threshold}%**  "
        "(adjustable via filter controls above)"
    )
    st.caption(f"Showing **{len(filtered_df)}** student(s) after applying filters.")

    st.divider()

    # ── Compute at-risk data ──────────────────────────────────────────────────
    at_risk_df = flag_at_risk(filtered_df, marks_threshold, attendance_threshold)
    summary = risk_summary(at_risk_df)

    # ── Status metric cards (Color-Accented KPI Row) ──────────────────────────
    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown('<div class="at-risk-total">', unsafe_allow_html=True)
        st.metric("Total At-Risk", summary["total"])
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="at-risk-marks">', unsafe_allow_html=True)
        st.metric("Low Marks Only", summary["low_marks_only"])
        st.markdown("</div>", unsafe_allow_html=True)

    with r3:
        st.markdown('<div class="at-risk-attendance">', unsafe_allow_html=True)
        st.metric("Low Attendance Only", summary["low_attendance_only"])
        st.markdown("</div>", unsafe_allow_html=True)

    with r4:
        st.markdown('<div class="at-risk-both">', unsafe_allow_html=True)
        st.metric("Both Issues", summary["both"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Stacked Vertical Cards (Chart Top, Table Below) ──────────────────────
    if at_risk_df.empty:
        st.markdown(
            f'<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 20px; text-align: center; color: #166534; font-weight: 600;">'
            f'No at-risk students found with the current thresholds and filters.'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Card 1 (TOP): Risk Score Distribution Chart
        st.markdown(
            f'<div class="table-card-container">'
            f'<div class="table-card-header">'
            f'{icon_trending_down(18, color="#dc2626")} Risk Score Distribution'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(at_risk_bar(at_risk_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Card 2 (BELOW): Full-width Flagged Students List Table
        st.markdown(
            f'<div class="table-card-container">'
            f'<div class="table-card-header">'
            f'{icon_clipboard(18, color="#dc2626")} Flagged Students List ({len(at_risk_df)})'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(at_risk_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f'<p class="stCaption" style="display: flex; align-items: center; gap: 6px;">'
        f'{icon_academic_cap(16)} <span><strong>EduMetrics</strong> — Student Performance Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit &amp; Plotly</span>'
        f'</p>',
        unsafe_allow_html=True,
    )


render()
