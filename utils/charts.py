"""
utils/charts.py
---------------
All Plotly chart builders for EduMetrics (Light Mode Design System).
Each function accepts a DataFrame (and optional styling params) and returns a
plotly.graph_objects.Figure so app.py can call st.plotly_chart(fig).
No Streamlit imports here — keeps chart logic fully testable in isolation.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Consistent EduMetrics colour palette (optimized for Light Canvas)
DEPT_COLOR_MAP = {
    "Cs": "#4f46e5",    # Indigo
    "It": "#0891b2",    # Cyan
    "Ece": "#d97706",   # Amber
    "Mech": "#059669",  # Emerald
}

GRADE_COLOR_MAP = {
    "A+": "#16a34a",    # Green
    "A": "#65a30d",     # Lime
    "B": "#2563eb",     # Blue
    "C": "#d97706",     # Amber
    "D": "#ea580c",     # Orange
    "F": "#dc2626",     # Red
}

_PLOTLY_TEMPLATE = "plotly_white"
_FONT_FAMILY = "Arial, Helvetica, sans-serif"


def _style_fig(fig: go.Figure) -> go.Figure:
    """Helper to apply consistent EduMetrics light-mode styling to all Plotly figures."""
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",   # transparent — inherits white page bg
        plot_bgcolor="#ffffff",           # solid white so chart area is always light
        font=dict(family=_FONT_FAMILY, color="#09090b", size=12),
        title_font=dict(family=_FONT_FAMILY, size=15, color="#09090b"),
        margin=dict(l=20, r=20, t=48, b=20),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#e4e4e7",
            font=dict(family=_FONT_FAMILY, color="#09090b", size=13),
        ),
    )
    fig.update_xaxes(
        gridcolor="#e4e4e7",
        zerolinecolor="#d4d4d8",
        linecolor="#e4e4e7",
        tickfont=dict(family=_FONT_FAMILY, color="#52525b", size=12),
        title_font=dict(family=_FONT_FAMILY, color="#09090b", size=13),
    )
    fig.update_yaxes(
        gridcolor="#e4e4e7",
        zerolinecolor="#d4d4d8",
        linecolor="#e4e4e7",
        tickfont=dict(family=_FONT_FAMILY, color="#52525b", size=12),
        title_font=dict(family=_FONT_FAMILY, color="#09090b", size=13),
    )
    return fig


def subject_avg_bar(subject_avg_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing the class-wide average for each subject.
    Input: DataFrame with columns ['Subject', 'Average_Marks'].
    """
    if subject_avg_df.empty or "Average_Marks" not in subject_avg_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Subject-wise Average Marks",
            annotations=[{
                "text": "No subject data available for current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    fig = px.bar(
        subject_avg_df,
        x="Average_Marks",
        y="Subject",
        orientation="h",
        text="Average_Marks",
        color="Average_Marks",
        color_continuous_scale=["#93c5fd", "#2563eb", "#1e3a8a"],
        title="Subject-wise Average Marks",
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
    fig.update_layout(
        xaxis_range=[0, 105],
        xaxis_title="Average Marks",
        yaxis_title="Subject",
        coloraxis_showscale=False,
    )
    return _style_fig(fig)


def attendance_vs_marks_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot of Attendance (x-axis) vs Avg_Marks (y-axis).
    Points are coloured by Department to reveal departmental patterns.
    Requires 'Avg_Marks' column — call analytics.compute_grades() first.
    """
    if df.empty or "Attendance" not in df.columns or "Avg_Marks" not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Attendance vs Average Marks",
            annotations=[{
                "text": "No attendance / marks data available for current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    color_col = "Department" if "Department" in df.columns else None
    hover_cols = [c for c in ["Name", "Student_ID", "Semester"] if c in df.columns]

    fig = px.scatter(
        df,
        x="Attendance",
        y="Avg_Marks",
        color=color_col,
        color_discrete_map=DEPT_COLOR_MAP if color_col else None,
        hover_data=hover_cols if hover_cols else None,
        title="Attendance vs Average Marks",
        labels={"Attendance": "Attendance (%)", "Avg_Marks": "Average Marks"},
        opacity=0.9,
    )
    # Add reference lines to mark common thresholds
    fig.add_vline(
        x=75, line_dash="dash", line_color="#ef4444",
        annotation_text="75% Attendance Threshold",
        annotation_position="top right",
        annotation_font=dict(family=_FONT_FAMILY, color="#dc2626", size=11),
    )
    fig.add_hline(
        y=40, line_dash="dash", line_color="#f97316",
        annotation_text="40 Marks Pass Cutoff",
        annotation_position="bottom right",
        annotation_font=dict(family=_FONT_FAMILY, color="#ea580c", size=11),
    )
    return _style_fig(fig)


def grade_distribution_pie(grade_dist_df: pd.DataFrame) -> go.Figure:
    """
    Pie chart showing the proportion of students in each letter grade bucket.
    Input: DataFrame with columns ['Grade', 'Count'].
    """
    if grade_dist_df.empty or "Grade" not in grade_dist_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Grade Distribution",
            annotations=[{
                "text": "No grade distribution data available for current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    fig = px.pie(
        grade_dist_df,
        names="Grade",
        values="Count",
        color="Grade",
        color_discrete_map=GRADE_COLOR_MAP,
        title="Grade Distribution",
        hole=0.4,  # Donut style
    )
    fig.update_traces(
        textinfo="label+percent",
        pull=[0.02] * len(grade_dist_df),
        marker=dict(line=dict(color="#ffffff", width=2)),
    )
    return _style_fig(fig)


def semester_performance_bar(semester_avg_df: pd.DataFrame) -> go.Figure:
    """
    Bar chart showing average marks per semester.
    Input: DataFrame with columns ['Semester', 'Average_Marks'].
    """
    if semester_avg_df.empty or "Average_Marks" not in semester_avg_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Semester-wise Average Performance",
            annotations=[{
                "text": "No semester data available for current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    fig = px.bar(
        semester_avg_df,
        x="Semester",
        y="Average_Marks",
        text="Average_Marks",
        color="Average_Marks",
        color_continuous_scale=["#99f6e4", "#0d9488", "#115e59"],
        title="Semester-wise Average Performance",
        labels={"Average_Marks": "Average Marks", "Semester": "Semester"},
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
    fig.update_layout(
        yaxis_range=[0, 105],
        coloraxis_showscale=False,
    )
    return _style_fig(fig)


def top_students_bar(top_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart ranking the top students by average marks.
    Input: DataFrame with columns ['Name', 'Avg_Marks'] (and optionally 'Department').
    """
    if top_df.empty or "Avg_Marks" not in top_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Top Performing Students",
            annotations=[{
                "text": "No top student data available for current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    top_df = top_df.sort_values("Avg_Marks", ascending=True)
    color_col = "Department" if "Department" in top_df.columns else None

    fig = px.bar(
        top_df,
        x="Avg_Marks",
        y="Name",
        orientation="h",
        color=color_col,
        color_discrete_map=DEPT_COLOR_MAP if color_col else None,
        text="Avg_Marks",
        title="Top Performing Students",
        labels={"Avg_Marks": "Average Marks", "Name": "Student"},
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
    fig.update_layout(
        xaxis_range=[0, 110],
    )
    return _style_fig(fig)


def at_risk_bar(at_risk_df: pd.DataFrame) -> go.Figure:
    """
    Bar chart visualising how far below the marks threshold at-risk students are.
    Useful for quickly spotting the most critical cases.
    """
    if at_risk_df.empty or "Avg_Marks" not in at_risk_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="At-Risk Students — Average Marks",
            annotations=[{
                "text": "No at-risk students found with current filters",
                "showarrow": False,
                "font": dict(family=_FONT_FAMILY, size=14, color="#71717a")
            }],
        )
        return _style_fig(fig)

    df_sorted = at_risk_df.sort_values("Avg_Marks", ascending=True)

    fig = px.bar(
        df_sorted,
        x="Avg_Marks",
        y="Name",
        orientation="h",
        color="Avg_Marks",
        color_continuous_scale=["#ef4444", "#f87171", "#fca5a5"],
        text="Avg_Marks",
        title="At-Risk Students — Average Marks",
        labels={"Avg_Marks": "Average Marks", "Name": "Student"},
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
    fig.update_layout(
        xaxis_range=[0, 105],
        coloraxis_showscale=False,
    )
    return _style_fig(fig)
