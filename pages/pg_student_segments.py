"""
pages/pg_student_segments.py
-----------------------------
EduMetrics — Page: Student Segments (K-Means Clustering)
Unsupervised grouping of students based on Attendance and Average Marks.

Includes:
  1. Interactive Cluster Count Slider (2–6 clusters, default 4).
  2. Overview & Silhouette Score metric card with plain-language quality note.
  3. Plotly 2D Scatter Plot (Attendance vs Avg Marks, points colored by Cluster_Label).
  4. Cluster Segment Summaries (student count, mean attendance, mean marks, description).
  5. Detailed Student Segment Assignment Table.

All data comes from st.session_state (populated by app.py).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.icons import (
    icon_academic_cap,
    icon_alert,
    icon_chart_bar,
    icon_clipboard,
    icon_info,
    icon_sparkles,
    icon_trending_down,
    icon_trophy,
)

import importlib
import utils.ml_models

importlib.reload(utils.ml_models)

from utils.ml_models import segment_students

# ── Plotly styling constants (mirrors charts.py) ─────────────────────────────
_PLOTLY_TEMPLATE = "plotly_white"
_FONT = "Arial, Helvetica, sans-serif"

# Vibrant light-canvas cluster colors
CLUSTER_COLORS = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#9333ea", "#0891b2"]


def _style_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family=_FONT, color="#09090b", size=12),
        title_font=dict(family=_FONT, size=15, color="#09090b"),
        margin=dict(l=20, r=20, t=48, b=20),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#e4e4e7",
            font=dict(family=_FONT, color="#09090b", size=13),
        ),
    )
    fig.update_xaxes(
        gridcolor="#e4e4e7", zerolinecolor="#d4d4d8", linecolor="#e4e4e7",
        tickfont=dict(family=_FONT, color="#52525b", size=12),
        title_font=dict(family=_FONT, color="#09090b", size=13),
    )
    fig.update_yaxes(
        gridcolor="#e4e4e7", zerolinecolor="#d4d4d8", linecolor="#e4e4e7",
        tickfont=dict(family=_FONT, color="#52525b", size=12),
        title_font=dict(family=_FONT, color="#09090b", size=13),
    )
    return fig


def _build_cluster_scatter(clustered_df: pd.DataFrame, summary_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of Attendance vs Average Marks colored by Cluster_Label."""
    unique_labels = summary_df["Cluster_Label"].tolist()
    color_map = {label: CLUSTER_COLORS[idx % len(CLUSTER_COLORS)] for idx, label in enumerate(unique_labels)}

    hover_cols = [c for c in ["Name", "Student_ID", "Department", "Semester"] if c in clustered_df.columns]

    fig = px.scatter(
        clustered_df,
        x="Attendance",
        y="Avg_Marks",
        color="Cluster_Label",
        color_discrete_map=color_map,
        hover_data=hover_cols,
        title="Student Segments — Attendance vs Average Marks",
        labels={"Attendance": "Attendance (%)", "Avg_Marks": "Average Marks", "Cluster_Label": "Segment"},
        opacity=0.88,
    )

    fig.update_traces(marker=dict(size=9, line=dict(width=1, color="#ffffff")))

    # Add centroid markers for each cluster
    for idx, row in summary_df.iterrows():
        c_name = row["Cluster_Label"]
        c_att = row["Mean_Attendance"]
        c_marks = row["Mean_Avg_Marks"]
        c_color = color_map.get(c_name, "#09090b")

        fig.add_trace(
            go.Scatter(
                x=[c_att],
                y=[c_marks],
                mode="markers+text",
                name=f"Centroid: {c_name}",
                text=[f"  <b>Centroid: {c_name}</b>"],
                textposition="top right",
                textfont=dict(family=_FONT, size=11, color=c_color),
                marker=dict(size=15, color=c_color, symbol="diamond", line=dict(width=2, color="#ffffff")),
                showlegend=False,
                hovertemplate=f"Centroid ({c_name})<br>Att: {c_att}%<br>Marks: {c_marks}<extra></extra>",
            )
        )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family=_FONT, color="#09090b", size=12),
        ),
        xaxis=dict(range=[0, 105]),
        yaxis=dict(range=[0, 105]),
    )

    return _style_fig(fig)


def _render_summary_cards(summary_df: pd.DataFrame) -> None:
    """Render cluster summary cards in a clean grid."""
    cols = st.columns(min(len(summary_df), 4))

    for idx, row in summary_df.iterrows():
        col = cols[idx % len(cols)]
        c_label = row["Cluster_Label"]
        c_count = row["Count"]
        c_att = row["Mean_Attendance"]
        c_marks = row["Mean_Avg_Marks"]
        c_desc = row["Description"]
        c_color = CLUSTER_COLORS[idx % len(CLUSTER_COLORS)]

        with col:
            st.markdown(
                f'''
                <div style="
                    background: #ffffff;
                    border: 1px solid #e4e4e7;
                    border-left: 4px solid {c_color};
                    border-radius: 10px;
                    padding: 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
                    margin-bottom: 14px;
                    height: 100%;
                ">
                    <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: {c_color}; display: block; margin-bottom: 4px;">
                        SEGMENT {idx + 1}
                    </span>
                    <div style="font-size: 16px; font-weight: 700; color: #09090b; margin-bottom: 6px;">
                        {c_label}
                    </div>
                    <div style="font-size: 13px; color: #52525b; margin-bottom: 10px; display: flex; gap: 12px; font-weight: 600;">
                        <span>👥 {c_count} Students</span>
                        <span>📊 {c_marks:.1f} Avg</span>
                        <span>📅 {c_att:.1f}% Att</span>
                    </div>
                    <div style="font-size: 12.5px; color: #71717a; line-height: 1.45; border-top: 1px solid #f4f4f5; padding-top: 8px;">
                        {c_desc}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )


def _render_students_table(clustered_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    """Render student segments table with styled cluster badges."""
    unique_labels = summary_df["Cluster_Label"].tolist()
    color_map = {label: CLUSTER_COLORS[idx % len(CLUSTER_COLORS)] for idx, label in enumerate(unique_labels)}

    rows_html = ""
    for _, row in clustered_df.iterrows():
        sid = row.get("Student_ID", "—")
        name = row.get("Name", "—")
        dept = row.get("Department", "—")
        sem = row.get("Semester", "—")
        att = f"{row['Attendance']:.1f}%" if "Attendance" in row else "—"
        marks = f"{row['Avg_Marks']:.1f}" if "Avg_Marks" in row else "—"
        label = row.get("Cluster_Label", "—")
        c_color = color_map.get(label, "#52525b")

        badge_html = f'<span style="background:{c_color}15; color:{c_color}; border:1px solid {c_color}40; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:600;">{label}</span>'

        rows_html += (
            f"<tr>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sid}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:500;'>{name}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{dept}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sem}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; text-align:right;'>{att}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:600; text-align:right;'>{marks}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:center;'>{badge_html}</td>"
            f"</tr>"
        )

    headers = ["Student ID", "Name", "Department", "Semester", "Attendance", "Average Marks", "Assigned Segment"]
    align_map = {"Attendance": "right", "Average Marks": "right", "Assigned Segment": "center"}

    header_html = "".join(
        f"<th style='background:#f4f4f5; color:#09090b; font-family:Arial,sans-serif; "
        f"font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.7px; "
        f"padding:10px 14px; border-bottom:1px solid #e4e4e7; white-space:nowrap; "
        f"text-align:{align_map.get(h, 'left')};'>{h}</th>"
        for h in headers
    )

    table_html = (
        f"<div style='overflow-x:auto;'>"
        f"<table style='width:100%; border-collapse:collapse; font-family:Arial,sans-serif;'>"
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df = st.session_state.filtered_df

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Unsupervised Machine Learning · Pattern Recognition</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Student Segments</h1>", unsafe_allow_html=True)
    st.caption(
        f"Grouping **{len(filtered_df)}** student(s) into behavioral clusters using K-Means "
        "on standardized Attendance & Average Marks."
    )

    st.divider()

    # ── Controls: Cluster Count Slider ───────────────────────────────────────
    col_cnt1, col_cnt2 = st.columns([2, 3])
    with col_cnt1:
        n_clusters = st.slider(
            "Number of Clusters (k)",
            min_value=2,
            max_value=6,
            value=4,
            step=1,
            key="segment_k_slider",
            help="Adjust how many distinct behavioral clusters to group students into.",
        )

    # Run clustering (live reactivity — no caching)
    clustered_df, summary_df, sil_val, error_msg = segment_students(filtered_df, n_clusters=n_clusters)

    if error_msg:
        st.markdown(
            f'<div style="background:#fffbeb; border:1px solid #fcd34d; border-radius:10px; '
            f'padding:20px 24px; display:flex; align-items:flex-start; gap:12px;">'
            f'{icon_alert(22, color="#d97706")}'
            f'<div><div style="font-size:15px; font-weight:600; color:#92400e; margin-bottom:4px;">Clustering Skipped</div>'
            f'<div style="font-size:14px; color:#78350f;">{error_msg}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            f'<p class="stCaption" style="display:flex; align-items:center; gap:6px;">'
            f'{icon_academic_cap(16)} <span><strong>EduMetrics</strong> — Student Performance Analytics Dashboard&nbsp;|&nbsp;Built with Streamlit &amp; Plotly</span>'
            f'</p>',
            unsafe_allow_html=True,
        )
        return

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1 — Overview & Silhouette Score
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_sparkles(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Clustering Overview</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    n_used = summary_df.attrs.get("n_clusters_used", n_clusters)
    n_stu = summary_df.attrs.get("n_students", len(filtered_df))

    # Determine silhouette quality note
    if sil_val >= 0.5:
        sil_note = "Strong Cluster Separation (Distinct Groups)"
        sil_bg, sil_fg, sil_border = "#f0fdf4", "#16a34a", "#86efac"
    elif sil_val >= 0.25:
        sil_note = "Moderate Cluster Separation"
        sil_bg, sil_fg, sil_border = "#eff6ff", "#2563eb", "#bfdbfe"
    else:
        sil_note = "Overlapping Segments (Ambiguous Groups)"
        sil_bg, sil_fg, sil_border = "#fffbeb", "#d97706", "#fcd34d"

    m1, m2, m3 = st.columns(3)
    m1.metric("Students Clustered", n_stu)
    m2.metric("Clusters Formed (k)", n_used)
    m3.metric("Silhouette Score", f"{sil_val:.3f}")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Explanatory card
    st.markdown(
        f'<div style="background:#f4f4f5; border:1px solid #e4e4e7; border-radius:10px; '
        f'padding:16px 20px; display:flex; align-items:flex-start; gap:12px; margin-bottom:14px;">'
        f'{icon_info(20, color="#52525b")}'
        f'<div style="font-size:14px; color:#3f3f46; line-height:1.55;">'
        f'<strong>How Student Segmentation Works:</strong> K-Means unsupervised clustering groups students based on '
        f'natural patterns in <strong>Attendance</strong> and <strong>Average Marks</strong> (standardized via StandardScaler). '
        f'Cluster labels are generated programmatically by comparing segment centroids against overall dataset medians. '
        f'<span style="background:{sil_bg}; color:{sil_fg}; border:1px solid {sil_border}; padding:2px 8px; border-radius:6px; font-weight:600; font-size:12px; margin-left:6px;">'
        f'{sil_note}'
        f'</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2 — Plotly Cluster Scatter Plot
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_chart_bar(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Cluster Visualization</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_chart_bar(18, color="#2563eb")} 2D Student Clusters (Attendance vs Average Marks)'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(_build_cluster_scatter(clustered_df, summary_df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3 — Segment Summaries
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_trophy(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Segment Profiles & Behavioral Summaries</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    _render_summary_cards(summary_df)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4 — Detailed Student Segment Table
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_clipboard(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Student Segment Roster</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_clipboard(18, color="#2563eb")} All {len(clustered_df)} Students with Assigned Cluster Segment'
        f'</div>',
        unsafe_allow_html=True,
    )
    _render_students_table(clustered_df, summary_df)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f'<p class="stCaption" style="display:flex; align-items:center; gap:6px;">'
        f'{icon_academic_cap(16)} <span><strong>EduMetrics</strong> — Student Performance Analytics Dashboard&nbsp;|&nbsp;Built with Streamlit &amp; Plotly</span>'
        f'</p>',
        unsafe_allow_html=True,
    )


render()
