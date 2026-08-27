"""
pages/pg_risk_prediction.py
---------------------------
EduMetrics — Page: Risk Prediction (ML)
Trains a RandomForest on the current filtered dataset and displays:
  1. Model Overview  — OOB / CV accuracy + explanatory note
  2. Feature Importance — ranked horizontal bar chart
  3. Student Risk Probabilities — sortable colour-coded table
  4. Automatic retraining whenever filtered_df or thresholds change.

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
)
import importlib
import utils.ml_models

importlib.reload(utils.ml_models)

from utils.ml_models import train_risk_model

# ── Plotly styling constants (mirrors charts.py) ─────────────────────────────
_PLOTLY_TEMPLATE = "plotly_white"
_FONT = "Arial, Helvetica, sans-serif"


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


# ── Risk-level badge HTML helper ─────────────────────────────────────────────
_LEVEL_STYLES = {
    "High":   ("background:#fef2f2; color:#dc2626; border:1px solid #fca5a5;"),
    "Medium": ("background:#fffbeb; color:#d97706; border:1px solid #fcd34d;"),
    "Low":    ("background:#f0fdf4; color:#16a34a; border:1px solid #86efac;"),
}

def _badge(level: str) -> str:
    style = _LEVEL_STYLES.get(level, "background:#f4f4f5; color:#52525b; border:1px solid #e4e4e7;")
    return (
        f'<span style="display:inline-block; padding:2px 10px; border-radius:9999px; '
        f'font-size:12px; font-weight:600; {style}">{level}</span>'
    )


def _feature_importance_chart(fi_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart ranked by importance (highest at top)."""
    df_plot = fi_df.sort_values("Importance", ascending=True)  # ascending=True → highest at top in h-bar
    fig = px.bar(
        df_plot,
        x="Importance",
        y="Feature",
        orientation="h",
        text="Importance",
        color="Importance",
        color_continuous_scale=["#bfdbfe", "#2563eb", "#1e3a8a"],
        title="Feature Importance — Drivers of At-Risk Prediction",
        labels={"Importance": "Importance Score", "Feature": "Feature"},
    )
    fig.update_traces(
        textposition="outside",
        texttemplate="%{text:.3f}",
    )
    fig.update_layout(
        xaxis_range=[0, min(1.0, fi_df["Importance"].max() * 1.25)],
        coloraxis_showscale=False,
    )
    return _style_fig(fig)


def _render_predictions_table(pred_df: pd.DataFrame) -> None:
    """
    Render the student risk probabilities as a styled HTML table with
    colour-coded Risk_Level badges — matching the app's existing table style.
    """
    rows_html = ""
    for _, row in pred_df.iterrows():
        sid   = row.get("Student_ID", "—")
        name  = row.get("Name", "—")
        dept  = row.get("Department", "—")
        sem   = row.get("Semester", "—")
        prob  = f"{row['Risk_Probability']:.1f}%"
        level = row.get("Risk_Level", "—")
        badge_html = _badge(level) if level in _LEVEL_STYLES else level

        rows_html += (
            f"<tr>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sid}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:500;'>{name}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{dept}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sem}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:600; text-align:right;'>{prob}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:center;'>{badge_html}</td>"
            f"</tr>"
        )

    headers = ["Student ID", "Name", "Department", "Semester", "Risk Probability", "Risk Level"]
    align_map = {"Risk Probability": "right", "Risk Level": "center"}
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


# ── Main render ───────────────────────────────────────────────────────────────
def render() -> None:
    # Guard: session_state must be populated by app.py
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    filtered_df      = st.session_state.filtered_df
    marks_threshold  = st.session_state.marks_threshold
    att_threshold    = st.session_state.attendance_threshold

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Machine Learning · Predictive Analytics</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>At-Risk Prediction</h1>", unsafe_allow_html=True)
    st.caption(
        f"Thresholds: Avg Marks < **{marks_threshold}** | "
        f"Attendance < **{att_threshold}%**  "
        "(adjustable via filter controls above)"
    )
    st.caption(f"Training on **{len(filtered_df)}** student(s) in the current filter.")

    st.divider()

    # ── Train model (no caching — retrain on every filter/threshold change) ──
    model, fi_df, pred_df, error_msg = train_risk_model(
        filtered_df, marks_threshold, att_threshold
    )

    # ── Error / insufficient-data state ─────────────────────────────────────
    if error_msg:
        st.markdown(
            f'<div style="background:#fffbeb; border:1px solid #fcd34d; border-radius:10px; '
            f'padding:20px 24px; display:flex; align-items:flex-start; gap:12px;">'
            f'{icon_alert(22, color="#d97706")}'
            f'<div><div style="font-size:15px; font-weight:600; color:#92400e; margin-bottom:4px;">Model Training Skipped</div>'
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
    # SECTION 1 — Model Overview
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_sparkles(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Model Overview</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    oob_acc  = fi_df.attrs.get("oob_accuracy")
    cv_acc   = fi_df.attrs.get("cv_accuracy")
    n_feat   = fi_df.attrs.get("n_features", len(fi_df))
    n_stu    = fi_df.attrs.get("n_students", len(filtered_df))
    n_atrisk = fi_df.attrs.get("n_at_risk_label", 0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students Trained On", n_stu)
    m2.metric("Features Used", n_feat)
    m3.metric("OOB Accuracy", f"{oob_acc * 100:.1f}%" if oob_acc is not None else "—")
    m4.metric("CV Balanced Accuracy", f"{cv_acc * 100:.1f}%" if cv_acc is not None else "—")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Explanatory note card
    st.markdown(
        f'<div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; '
        f'padding:16px 20px; display:flex; align-items:flex-start; gap:12px; margin-bottom:8px;">'
        f'{icon_info(20, color="#2563eb")}'
        f'<div style="font-size:14px; color:#1e40af; line-height:1.55;">'
        f'<strong>How this model works:</strong> The Random Forest is trained using the <em>existing '
        f'rule-based at-risk flag</em> (marks &lt; {marks_threshold} or attendance &lt; {att_threshold}%) '
        f'as its training label. It <strong>learns which combinations of features best predict that label</strong>, '
        f'then outputs a <em>continuous probability</em> (0–100%) for every student — '
        f'giving a richer signal than a binary flag alone. '
        f'Changing the thresholds or filters automatically retrains the model. '
        f'OOB and CV accuracy scores are rough sanity metrics only; '
        f'the model is not a replacement for the rule-based system.'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Summary pill row
    at_risk_pct = round(n_atrisk / n_stu * 100, 1) if n_stu > 0 else 0
    st.markdown(
        f'<div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:8px; margin-bottom:4px;">'
        f'<span style="background:#f4f4f5; border:1px solid #e4e4e7; border-radius:9999px; '
        f'padding:4px 14px; font-size:13px; font-weight:600; color:#3f3f46;">'
        f'RandomForest · 100 trees · class_weight=balanced</span>'
        f'<span style="background:#f0fdf4; border:1px solid #86efac; border-radius:9999px; '
        f'padding:4px 14px; font-size:13px; font-weight:600; color:#16a34a;">'
        f'{n_stu - n_atrisk} not-at-risk label ({100 - at_risk_pct:.1f}%)</span>'
        f'<span style="background:#fef2f2; border:1px solid #fca5a5; border-radius:9999px; '
        f'padding:4px 14px; font-size:13px; font-weight:600; color:#dc2626;">'
        f'{n_atrisk} at-risk label ({at_risk_pct:.1f}%)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2 — Feature Importance
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_chart_bar(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Feature Importance</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="table-card-container">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_trending_down(18, color="#2563eb")} '
        f'Which factors most influence the risk prediction (ranked by importance score)'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(_feature_importance_chart(fi_df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3 — Student Risk Probabilities
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_clipboard(22, color="#2563eb")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Student Risk Probabilities</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Risk-level summary pills above the table
    high_n   = int((pred_df["Risk_Level"] == "High").sum())
    medium_n = int((pred_df["Risk_Level"] == "Medium").sum())
    low_n    = int((pred_df["Risk_Level"] == "Low").sum())

    st.markdown(
        f'<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">'
        f'<span style="background:#fef2f2; border:1px solid #fca5a5; border-radius:9999px; '
        f'padding:5px 16px; font-size:13px; font-weight:700; color:#dc2626;">'
        f'High Risk: {high_n}</span>'
        f'<span style="background:#fffbeb; border:1px solid #fcd34d; border-radius:9999px; '
        f'padding:5px 16px; font-size:13px; font-weight:700; color:#d97706;">'
        f'Medium Risk: {medium_n}</span>'
        f'<span style="background:#f0fdf4; border:1px solid #86efac; border-radius:9999px; '
        f'padding:5px 16px; font-size:13px; font-weight:700; color:#16a34a;">'
        f'Low Risk: {low_n}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_clipboard(18, color="#2563eb")} '
        f'All {len(pred_df)} Students — sorted by Risk Probability (highest first)'
        f'</div>',
        unsafe_allow_html=True,
    )
    _render_predictions_table(pred_df)
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
