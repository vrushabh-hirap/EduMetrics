"""
pages/pg_overview.py
--------------------
EduMetrics — Page 1: Overview
Displays KPI summary cards + Data Quality Report expander.
All data comes from st.session_state (populated by app.py on every run).
"""

import streamlit as st
from utils.analytics import compute_kpis
from utils.icons import (
    icon_academic_cap,
    icon_check,
    icon_chart_bar,
    icon_trophy,
    icon_edumetrics_logo,
    icon_search,
    icon_user,
    icon_users,
    icon_download,
    icon_alert,
    icon_target,
    icon_sparkles,
    icon_bot,
    icon_shield_check,
    icon_scale,
    icon_file_text,
    icon_external_link,
)


def render() -> None:
    # ── Guard: ensure session_state is populated ──────────────────────────────
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df
    raw_df = st.session_state.raw_df
    cleaned_df = st.session_state.cleaned_df
    quality_report = st.session_state.quality_report

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Institutional Intelligence</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Student Performance Analytics</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle-text">Interactive analytics dashboard for student '
        "academic performance &amp; risk detection</p>",
        unsafe_allow_html=True,
    )
    st.caption(f"Showing **{len(filtered_df)}** student(s) after applying filters.")

    st.divider()

    # ── KPI Metrics ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Executive Summary</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 8px; margin-top: 10px; margin-bottom: 14px;">'
        f'{icon_chart_bar(22)}'
        f'<span style="font-size: 22px; font-weight: 600; color: #09090b;">Key Performance Indicators</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    kpis = compute_kpis(filtered_df)

    # Row 1: 4 Numerical KPIs (Balanced 4-Column Layout)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Students", kpis["student_count"])
    k2.metric("Avg Marks", f"{kpis['avg_marks']:.1f}")
    k3.metric("Avg Attendance", f"{kpis['avg_attendance']:.1f}%")
    k4.metric("Pass Rate", f"{kpis['pass_pct']:.1f}%")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Row 2: 2 Highlight Performers (50/50 Split - Ample space so full student names NEVER get truncated)
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            f"""
            <div class="performer-card top">
                <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #16a34a; display: flex; align-items: center; gap: 6px;">
                    {icon_trophy(14, color='#16a34a')} Top Performer
                </span>
                <span class="highlight-name" style="margin-top: 2px;">{kpis['top_performer']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            f"""
            <div class="performer-card lowest">
                <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #ea580c; display: flex; align-items: center; gap: 6px;">
                    Lowest Performer
                </span>
                <span class="highlight-name" style="margin-top: 2px;">{kpis['lowest_performer']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Data Quality Report ──────────────────────────────────────────────────
    with st.expander("Data Quality Report", expanded=True):
        # Structured Mini Stat Cards
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Raw Rows", len(raw_df))
        q2.metric("Cleaned Rows", len(cleaned_df))
        q3.metric("Duplicates Dropped", quality_report.get("duplicates_removed", 0))
        q4.metric("Identity Nulls Dropped", quality_report.get("identity_rows_dropped", 0))

        st.markdown("<hr style='border: none; border-top: 1px solid #f4f4f5; margin: 16px 0;'>", unsafe_allow_html=True)

        # Imputation & Clamping details with clean status badges
        imputed_dict = quality_report.get("nulls_imputed", {})
        clamped_dict = quality_report.get("out_of_range_clamped", {})

        imputed_str = ", ".join([f"{k}: {v}" for k, v in imputed_dict.items()]) if imputed_dict else "None"
        clamped_str = ", ".join([f"{k}: {v}" for k, v in clamped_dict.items()]) if clamped_dict else "None"

        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(
                f'<div style="font-size: 14px; color: #3f3f46; display: flex; align-items: center; gap: 6px;">'
                f'{icon_check(16, color="#16a34a")} <strong>Missing Values Imputed (Median):</strong> {imputed_str}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c_info2:
            st.markdown(
                f'<div style="font-size: 14px; color: #3f3f46; display: flex; align-items: center; gap: 6px;">'
                f'{icon_check(16, color="#16a34a")} <strong>Values Clamped [0, 100]:</strong> {clamped_str}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.checkbox("Preview cleaned dataset (first 20 rows)", key="overview_preview_cleaned"):
            st.dataframe(cleaned_df.head(20), use_container_width=True)

    # ── Institutional Website Footer (Rebuilt From Scratch) ───────────────────
    st.divider()
    
    footer_html = f'''
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 32px 36px 24px 36px; margin-top: 24px; margin-bottom: 70px; font-family: Arial, Helvetica, sans-serif; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);">
<div style="display: grid; grid-template-columns: 2.2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 24px; align-items: start;">
<div>
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
<div style="width: 36px; height: 36px; border-radius: 8px; background: #eff6ff; border: 1px solid #dbeafe; display: flex; align-items: center; justify-content: center;">
{icon_edumetrics_logo(26, color="#2563eb")}
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-size: 19px; font-weight: 800; color: #0f172a; letter-spacing: -0.4px;">EduMetrics</span>
<span style="background: #eff6ff; color: #2563eb; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px; border: 1px solid #dbeafe;">v2.5</span>
</div>
</div>
<p style="font-size: 13px; color: #64748b; line-height: 1.6; margin: 0; max-width: 290px;">
Academic performance analytics and machine learning intelligence suite for educational institutions.
</p>
</div>
<div>
<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.1px; color: #64748b; margin-bottom: 12px;">
Navigation
</div>
<div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #334155; font-weight: 500;">
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_chart_bar(14, color="#64748b")} Overview</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_chart_bar(14, color="#64748b")} Performance</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_search(14, color="#64748b")} Visual Exploration</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_user(14, color="#64748b")} Student Lookup</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_download(14, color="#64748b")} Reports Export</span>
</div>
</div>
<div>
<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.1px; color: #64748b; margin-bottom: 12px;">
ML Suite
</div>
<div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #334155; font-weight: 500;">
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_alert(14, color="#64748b")} Risk Classifier</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_target(14, color="#64748b")} Marks Regressor</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_users(14, color="#64748b")} Student Clustering</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_sparkles(14, color="#64748b")} Semester Forecast</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_bot(14, color="#64748b")} AI Assistant</span>
</div>
</div>
<div>
<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.1px; color: #64748b; margin-bottom: 12px;">
Institutional Legal
</div>
<div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #334155; font-weight: 500;">
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_shield_check(14, color="#64748b")} Privacy Policy</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_scale(14, color="#64748b")} Terms &amp; Conditions</span>
<span style="display: inline-flex; align-items: center; gap: 8px;">{icon_file_text(14, color="#64748b")} MIT Open License</span>
</div>
</div>
</div>
<div style="border-top: 1px solid #e2e8f0; margin-bottom: 18px;"></div>
<div style="display: flex; align-items: center; justify-content: space-between; font-size: 13px; color: #64748b; font-weight: 400;">
<div>
Copyright © 2026 EduMetrics. All Rights Reserved.
</div>
<div>
Developed by <a href="https://vrushabhhirap.vercel.app" target="_blank" style="color: #2563eb; font-weight: 700; text-decoration: none;">Vrushabh Hirap</a>
</div>
</div>
</div>
'''
    st.markdown(footer_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Clean Legal Popovers Layout with Chatbot Clearance
    pop_col, _ = st.columns([5, 1])
    with pop_col:
        p1, p2, p3 = st.columns(3)
        with p1:
            with st.popover("Privacy Policy", use_container_width=True):
                st.markdown(
                    "### Privacy Policy\n"
                    "**1. Local Data Processing**: All CSV datasets uploaded to EduMetrics are processed strictly in-memory within your active browser session.\n\n"
                    "**2. Zero External Storage**: Student names, marks, attendance, and identity records are never saved to external databases or shared with third-party servers.\n\n"
                    "**3. Data Hygiene**: Session memory is automatically flushed when the session ends or browser tab is closed."
                )
        with p2:
            with st.popover("Terms & Conditions", use_container_width=True):
                st.markdown(
                    "### Terms & Conditions\n"
                    "**1. Educational Purpose**: EduMetrics is designed for academic evaluation, department performance analytics, and educational research.\n\n"
                    "**2. Risk Indicators**: At-Risk prediction probabilities and regression estimates are decision-support metrics and should be combined with qualitative instructor evaluations.\n\n"
                    "**3. Open License**: Usage is free for educational institutions and faculty members."
                )
        with p3:
            with st.popover("MIT License", use_container_width=True):
                st.markdown(
                    "### MIT License\n"
                    "```text\n"
                    "Copyright (c) 2026 Vrushabh Hirap\n\n"
                    "Permission is hereby granted, free of charge, to any person obtaining a copy "
                    "of this software and associated documentation files (the \"Software\"), to deal "
                    "in the Software without restriction, including without limitation the rights "
                    "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
                    "copies of the Software.\n"
                    "```"
                )


render()
