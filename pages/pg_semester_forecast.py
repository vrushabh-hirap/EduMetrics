"""
pages/pg_semester_forecast.py
------------------------------
EduMetrics — Page: Semester Forecast (Trend Projection)
Fits a Linear Regression trend line on a student's historical semester averages
(Semester 1, 2, 3...) to project their next semester performance.

Includes:
  1. Pre-check guard: checks if current dataset contains students with 2+ semester records.
     - If NO: renders a clear explanatory message card and stops cleanly.
     - If YES: enables student selector dropdown for qualifying students.
  2. Plotly trend line chart (historical solid line + dashed forecast extension).
  3. Forecast summary metric card with trend direction & slope.
  4. Plain-language caveat card highlighting trend projection limitations.
  5. Historical semester scores breakdown table.

All data comes from st.session_state (populated by app.py).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.icons import (
    icon_academic_cap,
    icon_alert,
    icon_chart_bar,
    icon_clipboard,
    icon_folder,
    icon_info,
    icon_sparkles,
    icon_trending_down,
    icon_trophy,
)
import importlib
import utils.ml_models

importlib.reload(utils.ml_models)

from utils.ml_models import forecast_next_semester, get_multi_semester_students

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


def _build_forecast_chart(hist_df: pd.DataFrame, fc_dict: dict) -> go.Figure:
    """
    Build a Plotly line chart showing historical semester averages (solid blue)
    extended to the forecasted next semester (dashed amber).
    """
    fig = go.Figure()

    # Historical data points
    x_hist = hist_df["Semester"].tolist()
    y_hist = hist_df["Avg_Marks"].tolist()

    # Forecast point
    next_sem_name = fc_dict["next_sem_name"]
    next_sem_val = fc_dict["forecasted_marks"]

    # Trace 1: Historical trend line
    fig.add_trace(
        go.Scatter(
            x=x_hist,
            y=y_hist,
            mode="lines+markers",
            name="Historical Marks",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=10, color="#1d4ed8", symbol="circle"),
            hovertemplate="%{x}: <b>%{y:.1f}</b> marks<extra></extra>",
        )
    )

    # Trace 2: Forecast extension (dashed line connecting last historical point to forecast point)
    x_fc = [x_hist[-1], next_sem_name]
    y_fc = [y_hist[-1], next_sem_val]

    fig.add_trace(
        go.Scatter(
            x=x_fc,
            y=y_fc,
            mode="lines+markers",
            name="Forecasted Trend",
            line=dict(color="#d97706", width=3, dash="dash"),
            marker=dict(size=12, color="#d97706", symbol="star"),
            hovertemplate="%{x}: <b>%{y:.1f}</b> (Forecasted)<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"Semester Performance Trend & Next Semester Projection ({fc_dict['student_name']})",
        xaxis_title="Semester",
        yaxis_title="Average Marks",
        yaxis=dict(range=[0, 105]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family=_FONT, color="#09090b"),
        ),
    )

    return _style_fig(fig)


def render() -> None:
    if "filtered_df" not in st.session_state:
        st.info("Loading data…")
        st.stop()

    cleaned_df = st.session_state.get("cleaned_df", st.session_state.filtered_df)
    filtered_df = st.session_state.filtered_df

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(
        '<span class="eyebrow-mono">Machine Learning · Time-Series Trajectory</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<h1>Semester Forecast</h1>", unsafe_allow_html=True)
    st.caption(
        "Trend projection for student academic performance across consecutive semesters."
    )

    st.divider()

    # ── PRE-CHECK: Check if dataset contains multi-semester student records ──
    eligible_students = get_multi_semester_students(cleaned_df)

    if eligible_students.empty:
        # RENDER EXPLANATORY MESSAGE CARD (Feature Not Applicable)
        st.markdown(
            f'''
            <div style="
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
            ">
                <div style="display: flex; align-items: flex-start; gap: 14px;">
                    <div style="
                        width: 42px; height: 42px; border-radius: 10px;
                        background: #dbeafe; display: flex; align-items: center;
                        justify-content: center; flex-shrink: 0;
                    ">
                        {icon_info(24, color="#1d4ed8")}
                    </div>
                    <div>
                        <div style="font-size: 17px; font-weight: 700; color: #1e40af; margin-bottom: 6px;">
                            Semester Forecasting Not Applicable for Current Dataset
                        </div>
                        <div style="font-size: 14px; color: #1e3a8a; line-height: 1.6;">
                            Semester forecasting requires <strong>multiple records per student across different semesters</strong>
                            (i.e. the same Student ID appearing in Semester 1, Semester 2, etc.).
                            <br><br>
                            The currently loaded dataset contains <strong>one record per student</strong> ({len(filtered_df)} unique students).
                            To use this feature, upload a CSV dataset containing repeated Student_IDs across multiple semesters.
                        </div>
                    </div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        # Show Sample Format Guide
        st.markdown(
            f'''
            <div class="table-card-container">
                <div class="table-card-header">
                    {icon_folder(18, color="#2563eb")} Expected Multi-Semester CSV Format Example
                </div>
                <div style="font-size: 13px; color: #52525b; margin-bottom: 12px;">
                    Below is an example structure of how a multi-semester dataset should look:
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px;">
                        <thead>
                            <tr style="background: #f4f4f5; border-bottom: 1px solid #e4e4e7;">
                                <th style="padding: 8px 12px; text-align: left;">Student_ID</th>
                                <th style="padding: 8px 12px; text-align: left;">Name</th>
                                <th style="padding: 8px 12px; text-align: left;">Department</th>
                                <th style="padding: 8px 12px; text-align: left;">Semester</th>
                                <th style="padding: 8px 12px; text-align: right;">Maths</th>
                                <th style="padding: 8px 12px; text-align: right;">Programming</th>
                                <th style="padding: 8px 12px; text-align: right;">Attendance</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #e4e4e7;">
                                <td style="padding: 8px 12px; font-weight: 600;">S001</td>
                                <td style="padding: 8px 12px;">Aarav Shah</td>
                                <td style="padding: 8px 12px;">CS</td>
                                <td style="padding: 8px 12px; color: #2563eb; font-weight: 600;">Semester 1</td>
                                <td style="padding: 8px 12px; text-align: right;">70</td>
                                <td style="padding: 8px 12px; text-align: right;">75</td>
                                <td style="padding: 8px 12px; text-align: right;">85%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e4e4e7;">
                                <td style="padding: 8px 12px; font-weight: 600;">S001</td>
                                <td style="padding: 8px 12px;">Aarav Shah</td>
                                <td style="padding: 8px 12px;">CS</td>
                                <td style="padding: 8px 12px; color: #2563eb; font-weight: 600;">Semester 2</td>
                                <td style="padding: 8px 12px; text-align: right;">75</td>
                                <td style="padding: 8px 12px; text-align: right;">80</td>
                                <td style="padding: 8px 12px; text-align: right;">88%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e4e4e7;">
                                <td style="padding: 8px 12px; font-weight: 600;">S001</td>
                                <td style="padding: 8px 12px;">Aarav Shah</td>
                                <td style="padding: 8px 12px;">CS</td>
                                <td style="padding: 8px 12px; color: #2563eb; font-weight: 600;">Semester 3</td>
                                <td style="padding: 8px 12px; text-align: right;">82</td>
                                <td style="padding: 8px 12px; text-align: right;">85</td>
                                <td style="padding: 8px 12px; text-align: right;">90%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            ''',
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

    # ── IF MULTI-SEMESTER DATA IS SUPPORTED: Render Forecasting UI ────────────
    st.caption(
        f"Found **{len(eligible_students)}** student(s) with 2+ semester records "
        f"out of {filtered_df['Student_ID'].nunique()} total students in filter."
    )

    # Student Selector Dropdown
    student_options = [
        f"{row['Student_ID']} - {row['Name']} ({row['Department']}) [{row['Semester_Count']} Sems]"
        for _, row in eligible_students.iterrows()
    ]
    selected_option = st.selectbox(
        "Select Student for Semester Forecasting",
        options=student_options,
        index=0,
        key="forecast_student_select",
    )

    selected_sid = selected_option.split(" - ")[0].strip()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Run forecast
    hist_df, fc_dict, error_msg = forecast_next_semester(filtered_df, selected_sid)

    if error_msg:
        st.warning(error_msg)
        return

    # ── Section 1: Forecast KPI & Trend Summary ──────────────────────────────
    col_fc1, col_fc2 = st.columns([2, 3])

    with col_fc1:
        slope_val = fc_dict["slope"]
        slope_str = f"+{slope_val:.1f}" if slope_val > 0 else f"{slope_val:.1f}"
        trend_color = "#16a34a" if slope_val >= 0 else "#dc2626"
        trend_label = "Improving Trend" if slope_val > 0 else ("Declining Trend" if slope_val < 0 else "Stable Trend")

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
                    PROJECTED {fc_dict["next_sem_name"].upper()} MARKS
                </span>
                <div style="font-size: 46px; font-weight: 700; color: #ffffff; margin: 8px 0; line-height: 1;">
                    {fc_dict["forecasted_marks"]:.1f} <span style="font-size: 20px; font-weight: 400; color: #a1a1aa;">/ 100</span>
                </div>
                <div style="display: flex; gap: 8px; align-items: center; margin-top: 4px;">
                    <span style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); color: {trend_color}; font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 9999px;">
                        {trend_label} ({slope_str} pts/sem)
                    </span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    with col_fc2:
        # Plain-language caveat card
        st.markdown(
            f'''
            <div style="
                background: #fffbeb;
                border: 1px solid #fcd34d;
                border-radius: 12px;
                padding: 20px 24px;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {icon_alert(20, color="#d97706")}
                    <span style="font-size: 15px; font-weight: 700; color: #92400e;">Trend Projection Caveat</span>
                </div>
                <div style="font-size: 13.5px; color: #78350f; line-height: 1.55;">
                    {fc_dict["caveat"]}
                    <br><br>
                    <strong>Framing Note:</strong> Linear trend projection extrapolates previous trajectory into the upcoming semester. It serves as an <em>illustrative indicator</em>, not a guaranteed prediction.
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Section 2: Trend Chart ────────────────────────────────────────────────
    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_chart_bar(18, color="#2563eb")} Historical Trajectory & Forecasted Next Semester'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(_build_forecast_chart(hist_df, fc_dict), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section 3: Historical Breakdown Table ─────────────────────────────────
    st.markdown('<div class="table-card-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-card-header">'
        f'{icon_clipboard(18, color="#2563eb")} Semester History Breakdown — {fc_dict["student_name"]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    rows_html = ""
    for _, r in hist_df.iterrows():
        rows_html += (
            f"<tr>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; font-weight:600;'>{r['Semester']}</td>"
            f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #e4e4e7; color:#09090b; text-align:right;'>{r['Avg_Marks']:.1f}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:center;'><span style='background:#f4f4f5; color:#52525b; border:1px solid #e4e4e7; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:600;'>Historical</span></td>"
            f"</tr>"
        )

    # Add forecast row
    rows_html += (
        f"<tr style='background:#fffbeb;'>"
        f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #fcd34d; color:#92400e; font-weight:700;'>{fc_dict['next_sem_name']} (Forecast)</td>"
        f"<td style='padding:10px 14px; font-size:14px; border-bottom:1px solid #fcd34d; color:#92400e; font-weight:700; text-align:right;'>{fc_dict['forecasted_marks']:.1f}</td>"
        f"<td style='padding:10px 14px; border-bottom:1px solid #fcd34d; text-align:center;'><span style='background:#fef3c7; color:#d97706; border:1px solid #fcd34d; padding:2px 10px; border-radius:9999px; font-size:12px; font-weight:700;'>Projected</span></td>"
        f"</tr>"
    )

    table_html = (
        f"<div style='overflow-x:auto;'>"
        f"<table style='width:100%; border-collapse:collapse; font-family:Arial,sans-serif;'>"
        f"<thead><tr>"
        f"<th style='background:#f4f4f5; color:#09090b; font-size:12px; font-weight:700; text-transform:uppercase; padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:left;'>Semester</th>"
        f"<th style='background:#f4f4f5; color:#09090b; font-size:12px; font-weight:700; text-transform:uppercase; padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:right;'>Average Marks</th>"
        f"<th style='background:#f4f4f5; color:#09090b; font-size:12px; font-weight:700; text-transform:uppercase; padding:10px 14px; border-bottom:1px solid #e4e4e7; text-align:center;'>Record Type</th>"
        f"</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)
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
