"""
pages/pg_charts.py
------------------
EduMetrics — Page 3: Visual Exploration (Interactive Charts)
Displays all 5 interactive Plotly charts directly on the page in a rich multi-column grid:
1. Subject-wise Average Marks (Bar Chart)
2. Grade Distribution (Donut Chart)
3. Attendance vs Average Marks (Scatter Plot)
4. Semester Performance (Bar Chart)
5. Top 10 Students Ranking (Horizontal Bar Chart)

All data comes from st.session_state (populated by app.py).
"""

import streamlit as st
from utils.analytics import (
    grade_distribution,
    semester_averages,
    subject_averages,
    top_students,
)
from utils.charts import (
    attendance_vs_marks_scatter,
    grade_distribution_pie,
    semester_performance_bar,
    subject_avg_bar,
    top_students_bar,
)
from utils.icons import icon_academic_cap, icon_trending_down


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Visual Exploration</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Visual Exploration &amp; Charts</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle-text">Interactive graphical insights into student marks, '
        "attendance patterns, and grade distributions</p>",
        unsafe_allow_html=True,
    )
    st.caption(f"Showing **{len(filtered_df)}** student(s) after applying filters.")

    st.divider()

    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">'
        f'{icon_trending_down(22)}'
        f'<span style="font-size: 22px; font-weight: 600; color: #09090b;">Interactive Visualizations</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── ROW 1: Subject Averages + Grade Distribution ────────────────────────
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        st.markdown(
            '<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 16px; margin-bottom: 20px;">',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            subject_avg_bar(subject_averages(filtered_df)),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with r1_col2:
        st.markdown(
            '<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 16px; margin-bottom: 20px;">',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            grade_distribution_pie(grade_distribution(filtered_df)),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ROW 2: Attendance vs Marks + Semester Performance ───────────────────
    r2_col1, r2_col2 = st.columns(2)

    with r2_col1:
        st.markdown(
            '<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 16px; margin-bottom: 20px;">',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            attendance_vs_marks_scatter(filtered_df),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with r2_col2:
        st.markdown(
            '<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 16px; margin-bottom: 20px;">',
            unsafe_allow_html=True,
        )
        sem_avg_df = semester_averages(filtered_df)
        if sem_avg_df.empty:
            st.info("No semester data available for the current filters.")
        else:
            st.plotly_chart(
                semester_performance_bar(sem_avg_df),
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ROW 3: Top Students Bar Chart (Full Width) ──────────────────────────
    st.markdown(
        '<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 16px; margin-bottom: 20px;">',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        top_students_bar(top_students(filtered_df, n=10)),
        use_container_width=True,
    )
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
