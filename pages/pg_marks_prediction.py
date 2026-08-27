"""
pages/pg_marks_prediction.py
----------------------------
EduMetrics — Page: Marks Prediction (ML Regression)
Trains a RandomForestRegressor on the current filtered dataset to predict Final_Marks.
Includes:
  1. Model Performance Overview — R² score, MAE, RMSE + plain-English interpretation
  2. Predicted vs Actual Marks — Scatter plot with y=x reference line
  3. Feature Importance — Horizontal bar chart of input drivers
  4. What-If Simulator — Live interactive prediction sliders for student mark scenarios
  5. Student Predictions & Residuals — Detailed sortable table

All data comes from st.session_state (populated by app.py).
"""

import numpy as np
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

from utils.ml_models import train_marks_regressor

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


def _actual_vs_predicted_chart(pred_df: pd.DataFrame) -> go.Figure:
    """Scatter plot comparing Actual Final Marks vs Predicted Final Marks with y=x line."""
    fig = px.scatter(
        pred_df,
        x="Actual_Final_Marks",
        y="Predicted_Final_Marks",
        color="Department" if "Department" in pred_df.columns else None,
        hover_data=[c for c in ["Name", "Student_ID", "Residual"] if c in pred_df.columns],
        title="Predicted vs Actual Final Marks",
        labels={
            "Actual_Final_Marks": "Actual Final Marks",
            "Predicted_Final_Marks": "Predicted Final Marks",
        },
        opacity=0.85,
    )

    # Reference diagonal line y = x representing 100% perfect predictions
    min_val = min(pred_df["Actual_Final_Marks"].min(), pred_df["Predicted_Final_Marks"].min())
    max_val = max(pred_df["Actual_Final_Marks"].max(), pred_df["Predicted_Final_Marks"].max())
    padding = 2

    fig.add_shape(
        type="line",
        x0=min_val - padding,
        y0=min_val - padding,
        x1=max_val + padding,
        y1=max_val + padding,
        line=dict(color="#ef4444", width=2, dash="dash"),
    )

    fig.add_annotation(
        x=max_val,
        y=max_val,
        text="Ideal Line (y = x)",
        showarrow=False,
        font=dict(family=_FONT, color="#dc2626", size=11),
        yshift=14,
    )

    return _style_fig(fig)


def _feature_importance_chart(fi_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing feature importances for Final Marks regression."""
    df_plot = fi_df.sort_values("Importance", ascending=True)
    fig = px.bar(
        df_plot,
        x="Importance",
        y="Feature",
        orientation="h",
        text="Importance",
        color="Importance",
        color_continuous_scale=["#cbd5e1", "#0284c7", "#0369a1"],
        title="Feature Importance — Influencers of Final Marks",
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
    """Render student predictions table with styled residual badges."""
    rows_html = ""
    align_map = {
        "Actual Final Marks": "right",
        "Predicted Final Marks": "right",
        "Residual": "right",
        "Status": "center",
    }

    for _, row in pred_df.iterrows():
        sid = row.get("Student_ID", "—")
        name = row.get("Name", "—")
        dept = row.get("Department", "—")
        sem = row.get("Semester", "—")
        actual = f"{row['Actual_Final_Marks']:.1f}"
        predicted = f"{row['Predicted_Final_Marks']:.1f}"
        res_val = float(row["Residual"])

        # Badge based on prediction residual
        if res_val >= 3.0:
            badge_html = '<span style="background:#f0fdf4; color:#16a34a; border:1px solid #86efac; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:600;">Outperformed (+%.1f)</span>' % res_val
        elif res_val <= -3.0:
            badge_html = '<span style="background:#fef2f2; color:#dc2626; border:1px solid #fca5a5; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:600;">Underperformed (%.1f)</span>' % res_val
        else:
            badge_html = '<span style="background:#f4f4f5; color:#52525b; border:1px solid #e4e4e7; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:600;">Accurate (%.1f)</span>' % res_val

        rows_html += (
            f"<tr>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sid}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:500;'>{name}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{dept}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b;'>{sem}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; text-align:right;'>{actual}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:600; text-align:right;'>{predicted}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; text-align:right;'>{res_val:+.1f}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:center;'>{badge_html}</td>"
            f"</tr>"
        )

    headers = [
        "Student ID", "Name", "Department", "Semester",
        "Actual Final Marks", "Predicted Final Marks", "Residual", "Status"
    ]
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

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Machine Learning · Regression Analytics</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Marks Prediction</h1>", unsafe_allow_html=True)
    st.caption(
        f"Predicting **Final Marks** based on Internal Marks, Attendance, and Subject Scores "
        f"for **{len(filtered_df)}** student(s) in the active filter."
    )

    st.divider()

    # ── Train regression model ───────────────────────────────────────────────
    model, r2_val, fi_df, pred_df, error_msg = train_marks_regressor(filtered_df)

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
    # SECTION 1 — Model Performance
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_sparkles(22, color="#0284c7")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Model Performance</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    mae_val = fi_df.attrs.get("mae", 0.0)
    rmse_val = fi_df.attrs.get("rmse", 0.0)
    n_stu = fi_df.attrs.get("n_students", len(filtered_df))
    n_feat = fi_df.attrs.get("n_features", len(fi_df))
    r2_pct = max(0.0, r2_val * 100)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("R² Variance Score", f"{r2_pct:.1f}%")
    m2.metric("Mean Absolute Error (MAE)", f"{mae_val:.2f}")
    m3.metric("Root Mean Sq. Error (RMSE)", f"{rmse_val:.2f}")
    m4.metric("Students Evaluated", n_stu)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Plain-English Interpretation Note Card
    st.markdown(
        f'<div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; '
        f'padding:16px 20px; display:flex; align-items:flex-start; gap:12px; margin-bottom:12px;">'
        f'{icon_info(20, color="#0284c7")}'
        f'<div style="font-size:14px; color:#0369a1; line-height:1.55;">'
        f'<strong>Model Interpretation:</strong> This Random Forest Regressor explains '
        f'<strong>~{r2_pct:.1f}%</strong> of the variation in student Final Marks based on '
        f'Internal Marks, Attendance, and subject scores. On average, predictions deviate by '
        f'only <strong>{mae_val:.1f} marks</strong> (MAE).'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2 & 3 — Visual Analytics (Predicted vs Actual & Feature Importance)
    # ═══════════════════════════════════════════════════════════════════════
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="table-card-header">'
            f'{icon_chart_bar(18, color="#0284c7")} Predicted vs Actual Final Marks'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_actual_vs_predicted_chart(pred_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="table-card-header">'
            f'{icon_trending_down(18, color="#0284c7")} Feature Importance (Predictors)'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_feature_importance_chart(fi_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4 — What-If Simulator
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_sparkles(22, color="#0284c7")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">What-If Scenario Simulator</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption("Adjust student inputs below to calculate predicted Final Marks in real time.")

    feature_cols = fi_df.attrs.get("feature_cols", [])

    sim_container = st.container()
    with sim_container:
        sim_col_inputs, sim_col_result = st.columns([3, 2])

        input_values = {}
        with sim_col_inputs:
            # Create two columns of sliders for clean grid layout
            sc1, sc2 = st.columns(2)
            for idx, feat in enumerate(feature_cols):
                target_col = sc1 if idx % 2 == 0 else sc2
                # Default slider value set to column median/mean
                default_val = float(filtered_df[feat].mean()) if feat in filtered_df.columns else 70.0
                min_val = 0.0
                max_val = 100.0

                with target_col:
                    input_values[feat] = st.slider(
                        f"{feat.replace('_', ' ')}",
                        min_value=min_val,
                        max_value=max_val,
                        value=round(default_val, 1),
                        step=1.0,
                        key=f"sim_slider_{feat}",
                    )

        with sim_col_result:
            # Compute live prediction using trained model
            input_row = pd.DataFrame([input_values])[feature_cols]
            pred_score = float(model.predict(input_row)[0])
            pred_score_clamped = min(100.0, max(0.0, pred_score))

            # Derive letter grade for context
            def _sim_grade(score: float) -> str:
                if score >= 90: return "A+"
                if score >= 80: return "A"
                if score >= 70: return "B"
                if score >= 60: return "C"
                if score >= 50: return "D"
                return "F"

            grade_letter = _sim_grade(pred_score_clamped)

            st.markdown(
                f'''
                <div style="
                    background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
                    border: 1px solid #27272a;
                    border-radius: 12px;
                    padding: 24px;
                    color: #ffffff;
                    text-align: center;
                    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                ">
                    <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.1px; color: #a1a1aa;">
                        PREDICTED FINAL MARKS
                    </span>
                    <div style="font-size: 48px; font-weight: 700; color: #ffffff; margin: 8px 0; line-height: 1;">
                        {pred_score_clamped:.1f} <span style="font-size: 20px; font-weight: 400; color: #a1a1aa;">/ 100</span>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center; margin-top: 4px;">
                        <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(96, 165, 250, 0.3); color: #60a5fa; font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 9999px;">
                            Grade {grade_letter}
                        </span>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5 — Student Predictions & Outliers Table
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">'
        f'{icon_clipboard(22, color="#0284c7")}'
        f'<span style="font-size:22px; font-weight:600; color:#09090b;">Student Predictions & Outlier Analysis</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_clipboard(18, color="#0284c7")} '
        f'All {len(pred_df)} Students — Actual vs Predicted Final Marks'
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
