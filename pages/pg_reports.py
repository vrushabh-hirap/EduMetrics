"""
pages/pg_reports.py
-------------------
EduMetrics — Page 5: Reports
Download Filtered Dataset (CSV) and Download Summary Report (CSV).
All data comes from st.session_state (populated by app.py).
"""

import pandas as pd
import streamlit as st
from utils.analytics import compute_kpis
from utils.icons import (
    icon_academic_cap,
    icon_chart_bar,
    icon_download,
)
from utils.risk_detection import flag_at_risk, risk_summary


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 CSV bytes for st.download_button."""
    return df.to_csv(index=False).encode("utf-8")


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df
    marks_threshold = st.session_state.marks_threshold
    attendance_threshold = st.session_state.attendance_threshold

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Export Engine</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Download Reports</h1>", unsafe_allow_html=True)
    st.caption(
        f"Exporting **{len(filtered_df)}** student(s) matching the current filters."
    )

    st.divider()

    # ── Compute data for export ───────────────────────────────────────────────
    kpis = compute_kpis(filtered_df)
    at_risk_df = flag_at_risk(filtered_df, marks_threshold, attendance_threshold)

    # ── Download buttons ─────────────────────────────────────────────────────
    dl_c1, dl_c2 = st.columns(2)

    with dl_c1:
        st.markdown(
            f'<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">'
            f'{icon_download(18)}'
            f'<span style="font-weight: 600; font-size: 16px; color: #09090b;">Filtered Dataset</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "All students matching the current filter controls with computed "
            "grades and average marks."
        )
        st.download_button(
            label="Download Filtered Dataset (CSV)",
            data=df_to_csv_bytes(filtered_df),
            file_name="edumetrics_filtered_students.csv",
            mime="text/csv",
            help="Downloads all students matching the current filter controls.",
        )

    with dl_c2:
        st.markdown(
            f'<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">'
            f'{icon_chart_bar(18)}'
            f'<span style="font-weight: 600; font-size: 16px; color: #09090b;">Summary Report</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "KPI summary table plus the at-risk student list — "
            "useful for department-level reporting."
        )

        kpi_rows = pd.DataFrame([
            {"Metric": k.replace("_", " ").title(), "Value": str(v)}
            for k, v in kpis.items()
        ])
        separator = pd.DataFrame([{"Metric": "--- AT-RISK STUDENTS ---", "Value": ""}])
        at_risk_export = (
            at_risk_df.rename(
                columns={"Student_ID": "Metric", "Risk_Reason": "Value"}
            )
            if not at_risk_df.empty
            else pd.DataFrame([{"Metric": "None", "Value": "No at-risk students"}])
        )
        summary_csv = pd.concat(
            [kpi_rows, separator, at_risk_export], ignore_index=True
        )

        st.download_button(
            label="Download Summary Report (CSV)",
            data=df_to_csv_bytes(summary_csv),
            file_name="edumetrics_summary_report.csv",
            mime="text/csv",
            help="Downloads KPI summary + at-risk student list.",
        )

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f'<p class="stCaption" style="display: flex; align-items: center; gap: 6px;">'
        f'{icon_academic_cap(16)} <span><strong>EduMetrics</strong> — Student Performance Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit &amp; Plotly</span>'
        f'</p>',
        unsafe_allow_html=True,
    )


render()
