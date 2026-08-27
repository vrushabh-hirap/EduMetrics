"""
pages/pg_student_lookup.py
--------------------------
EduMetrics — Page 5: Student Lookup
Individual student profile view with name badge, profile columns,
and subject marks breakdown.
All data comes from st.session_state (populated by app.py).
"""

import pandas as pd
import streamlit as st
from utils.analytics import student_profile
from utils.icons import icon_academic_cap, icon_alert, icon_check, icon_search
from utils.risk_detection import flag_at_risk


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df
    marks_threshold = st.session_state.marks_threshold
    attendance_threshold = st.session_state.attendance_threshold

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Individual Profile Inspection</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Student Lookup</h1>", unsafe_allow_html=True)
    st.caption(f"Showing **{len(filtered_df)}** student(s) after applying filters.")

    st.divider()

    # ── Student selector ─────────────────────────────────────────────────────
    if filtered_df.empty:
        st.info("No students match the current filters. Please adjust the filter controls above.")
        return

    student_labels = filtered_df.apply(
        lambda r: f"{r['Student_ID']} — {r['Name']}", axis=1
    ).tolist()

    sel_col, _ = st.columns([1.2, 0.8])
    with sel_col:
        selected_label = st.selectbox(
            "Select a student",
            options=student_labels,
            key="student_select",
        )

    if not selected_label:
        return

    selected_id = selected_label.split(" — ")[0]
    profile = student_profile(filtered_df, selected_id)

    if not profile:
        st.warning("Student profile not found.")
        return

    # ── At-risk status for the selected student ───────────────────────────────
    student_row = filtered_df[
        filtered_df["Student_ID"].astype(str) == str(selected_id)
    ]
    student_at_risk = flag_at_risk(student_row, marks_threshold, attendance_threshold)
    is_at_risk = not student_at_risk.empty

    risk_icon = icon_alert(14, color="#dc2626") if is_at_risk else icon_check(14, color="#16a34a")
    risk_label = "AT-RISK" if is_at_risk else "On Track"
    risk_color = "#dc2626" if is_at_risk else "#16a34a"
    badge_bg = "#fef2f2" if is_at_risk else "#f0fdf4"

    # ── Profile card ─────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="profile-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #f4f4f5; padding-bottom: 12px;">
                <span class="highlight-name">{profile.get('Name', '—')}</span>
                <span style="font-family: Arial, Helvetica, sans-serif; font-size: 12px; font-weight: 700; color: {risk_color}; background-color: {badge_bg}; padding: 6px 14px; border: 1px solid {risk_color}; border-radius: 9999px; display: inline-flex; align-items: center; gap: 6px;">
                    {risk_icon} {risk_label}
                </span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    prof_c1, prof_c2, prof_c3 = st.columns(3)
    prof_c1.markdown(f"**Student ID:** {profile.get('Student_ID', '—')}")
    prof_c1.markdown(f"**Department:** {profile.get('Department', '—')}")
    prof_c1.markdown(f"**Semester:** {profile.get('Semester', '—')}")

    prof_c2.markdown(f"**Attendance:** {profile.get('Attendance', '—')}%")
    prof_c2.markdown(f"**Internal Marks:** {profile.get('Internal_Marks', '—')}")
    prof_c2.markdown(f"**Final Marks:** {profile.get('Final_Marks', '—')}")

    prof_c3.markdown(f"**Average Marks:** {profile.get('Avg_Marks', '—')}")
    prof_c3.markdown(f"**Grade:** {profile.get('Grade', '—')}")
    if is_at_risk:
        prof_c3.markdown(
            f"**Risk Reason:** {student_at_risk.iloc[0].get('Risk_Reason', '—')}"
        )

    # ── Subject marks breakdown ───────────────────────────────────────────────
    subject_cols_present = [
        c for c in ["Maths", "Programming", "Database", "AI_ML"] if c in profile
    ]
    if subject_cols_present:
        st.markdown("<br>**Subject Marks Breakdown:**", unsafe_allow_html=True)
        subj_df = pd.DataFrame(
            [{"Subject": s, "Marks": profile[s]} for s in subject_cols_present]
        )
        st.dataframe(subj_df, use_container_width=True, hide_index=True)

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
