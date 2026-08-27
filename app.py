"""
app.py
------
EduMetrics — Multi-Page Entry Point
Handles: page config, CSS injection, sidebar (upload / filters / thresholds),
data loading, filtering, session_state population, and st.navigation.

All page content lives in pages/pg_*.py.
Run with:  streamlit run app.py
"""

import io
import importlib
import pathlib

import pandas as pd
import streamlit as st

import utils.icons
import utils.data_cleaning
importlib.reload(utils.icons)
importlib.reload(utils.data_cleaning)

from utils.ai_widget import render_ai_chatbot
from utils.analytics import compute_grades
from utils.data_cleaning import clean_data, load_and_validate
from utils.icons import (
    icon_academic_cap,
    icon_alert,
    icon_chart_bar,
    icon_check,
    icon_download,
    icon_edumetrics_logo,
    icon_folder,
    icon_info,
    icon_sparkles,
    icon_trending_down,
    icon_user,
    icon_users,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduMetrics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS & JS — Arial Font, Protection (No Text Selection/Right Click), No Scrollbars
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" rel="stylesheet">
    <style>
        /* ═══════════════════════════════════════════════════════════════════
           EDUMETRICS — Light Mode Design System & Protection Rules
        ═══════════════════════════════════════════════════════════════════ */

        /* ── 1. DISABLE TEXT SELECTION GLOBALLY ── */
        html, body, .stApp, div, p, span, h1, h2, h3, h4, h5, h6, label, table, th, td {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }

        /* Re-enable text selection for input fields & textareas so user typing works */
        input, textarea, [data-baseweb="input"] input, [data-baseweb="select"] input {
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
            user-select: text !important;
        }

        /* ── 2. HIDE ALL SCROLLBARS GLOBALLY ── */
        ::-webkit-scrollbar {
            display: none !important;
            width: 0px !important;
            height: 0px !important;
            background: transparent !important;
        }
        * {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }

        /* ── 3. GLOBAL FONT FAMILY OVERRIDE (Arial, Helvetica, sans-serif) ── */
        :root {
            color-scheme: light !important;
            --background-color: #ffffff !important;
            --secondary-background-color: #f4f4f5 !important;
            --text-color: #09090b !important;
            --primary-color: #09090b !important;
        }

        html, body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .main,
        .block-container,
        [data-testid="stSidebar"] {
            font-family: Arial, Helvetica, sans-serif !important;
            color-scheme: light !important;
            background-color: #ffffff !important;
            color: #09090b !important;
            -webkit-font-smoothing: antialiased;
        }

        /* Explicit Arial font-family override for text elements (EXCLUDING Material icons) */
        h1, h2, h3, h4, h5, h6, p, label, button, input, select, textarea,
        .stMarkdown, .stCaption, .eyebrow-mono, .profile-card,
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
        [data-baseweb="tab"], [data-baseweb="tag"] {
            font-family: Arial, Helvetica, sans-serif !important;
        }

        /* ── CUSTOM SPINNER & LOADING FEEDBACK BANNER ── */
        div[data-testid="stSpinner"] {
            background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%) !important;
            border: 1px solid #bfdbfe !important;
            border-radius: 12px !important;
            padding: 14px 20px !important;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.12) !important;
            color: #1d4ed8 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin: 8px 0 16px 0 !important;
        }

        div[data-testid="stSpinner"] > div {
            border-top-color: #2563eb !important;
        }

        /* FIX: Preserve Material Symbols font for Streamlit expanders & icons */
        .material-symbols-outlined,
        [data-testid="stExpanderToggleIcon"],
        [data-testid="stExpander"] summary span,
        span.material-symbols-outlined {
            font-family: 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            line-height: 1 !important;
            text-transform: none !important;
            letter-spacing: normal !important;
            word-wrap: normal !important;
            white-space: nowrap !important;
            direction: ltr !important;
        }

        /* ── 4. NATIVE HEADER & SIDEBAR TOGGLE ── */
        header[data-testid="stHeader"],
        [data-testid="stHeader"] {
            background-color: transparent !important;
            box-shadow: none !important;
            border: none !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
        }

        /* Hide default Streamlit top decoration strip */
        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* Ensure sidebar toggle button icons remain dark and visible */
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stCollapsedControl"] button,
        [data-testid="stCollapsedControl"] svg,
        button[aria-label="Expand sidebar"],
        button[aria-label="Collapse sidebar"] {
            color: #09090b !important;
            fill: #09090b !important;
        }

        [data-testid="stAppViewContainer"] > section.main,
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stMain"],
        .stApp .main {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        div.block-container,
        .block-container,
        [data-testid="stMain"] .block-container {
            padding-top: 0.75rem !important; /* ~12px top breathing room, no huge gap */
            padding-bottom: 2rem !important;
            max-width: 1440px !important;
        }

        [data-testid="stVerticalBlock"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           6. SIDEBAR — PERMANENT EXPANDED & TOP BRAND CARD HIERARCHY
        ══════════════════════════════════════════════════════════════════ */

        /* 6A. Sidebar container — fixed 300px, always visible */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
            background-color: #fafafa !important;
            border-right: 1px solid #e4e4e7 !important;
            font-family: Arial, Helvetica, sans-serif !important;
            transform: translate3d(0, 0, 0) !important;
            visibility: visible !important;
        }

        /* 6B. Hide ALL collapse/expand toggle buttons */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarHeader"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarHeader"] button,
        button[data-testid="stExpandSidebarButton"] {
            display: none !important;
        }

        /* 6C. stSidebarContent — flex column */
        [data-testid="stSidebarContent"] {
            display: flex !important;
            flex-direction: column !important;
            padding: 16px 14px !important;
            gap: 8px !important;
        }

        /* Unwrap intermediate Streamlit layout blocks only (NOT element containers or custom cards) */
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"] > div,
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"],
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlockBorderWrapper"] {
            display: contents !important;
        }

        /* 6D. Top-to-bottom flex order:
           1. EduMetrics Brand Card (TOP OF SIDEBAR)
           2. Main Navigation links
           3. Dataset Engine card
           4. File uploader
           5. Sample dataset badge
           6. Footer status line
        */
        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.edu-sidebar-brand-card),
        .edu-sidebar-brand-card {
            order: -100 !important;
            margin-bottom: 10px !important;
            display: block !important;
            width: 100% !important;
        }

        .edu-sidebar-brand-card-text {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: flex-start !important;
        }

        .edu-sidebar-brand-card-text div,
        .edu-sidebar-brand-card-text span {
            display: block !important;
        }

        [data-testid="stSidebarNav"] {
            order: 0 !important;
        }

        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.edu-sidebar-dataset-card),
        .edu-sidebar-dataset-card {
            order: 10 !important;
            margin-top: 14px !important;
            display: block !important;
            width: 100% !important;
        }

        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has([data-testid="stFileUploader"]),
        [data-testid="stFileUploader"] {
            order: 20 !important;
            margin-top: 6px !important;
            display: block !important;
            width: 100% !important;
        }

        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.edu-sidebar-sample-badge),
        .edu-sidebar-sample-badge {
            order: 30 !important;
            margin-top: 6px !important;
            display: flex !important;
            width: 100% !important;
        }

        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.edu-sidebar-footer),
        .edu-sidebar-footer {
            order: 40 !important;
            margin-top: 16px !important;
            display: flex !important;
            width: 100% !important;
        }

        /* 6E. "MAIN NAVIGATION" eyebrow label */
        [data-testid="stSidebarNav"]::before {
            content: "MAIN NAVIGATION";
            display: block !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.1px !important;
            color: #71717a !important;
            margin-bottom: 6px !important;
            padding-left: 4px !important;
        }

        /* 6F. Nav list */
        [data-testid="stSidebarNav"] ul {
            list-style: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 3px !important;
        }

        [data-testid="stSidebarNav"] li {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 6G. Nav link pills */
        [data-testid="stSidebarNav"] a {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            padding: 9px 12px !important;
            border-radius: 8px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #3f3f46 !important;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            text-decoration: none !important;
            box-shadow: none !important;
            transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #eff6ff !important;
            color: #2563eb !important;
            border-color: #dbeafe !important;
            transform: translateX(4px) !important;
        }

        /* Active nav item — Royal Blue primary gradient pill */
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] [aria-selected="true"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-color: #1d4ed8 !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28) !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] *,
        [data-testid="stSidebarNav"] a[aria-current="page"] span,
        [data-testid="stSidebarNav"] a[aria-current="page"] svg {
            color: #ffffff !important;
            fill: #ffffff !important;
        }

        /* 6H. File uploader styling */
        [data-testid="stFileUploader"] section {
            background-color: #ffffff !important;
            border: 1px dashed #d4d4d8 !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        [data-testid="stFileUploader"] section:hover {
            border-color: #2563eb !important;
            background-color: #eff6ff40 !important;
        }

        /* ── 8. KPI METRIC CARDS ── */
        [data-testid="metric-container"] {
            background-color: #ffffff !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 10px !important;
            padding: 16px 18px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] > div,
        [data-testid="stMetricLabel"] label,
        [data-testid="stMetricLabel"] p {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 12px !important;
            line-height: 16px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            color: #52525b !important;
            font-weight: 600 !important; /* Semibold label */
            white-space: normal !important;
            overflow: visible !important;
            word-break: break-word !important;
        }

        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] > div {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 30px !important;
            line-height: 38px !important;
            font-weight: 700 !important; /* Bold */
            color: #09090b !important;
        }

        /* ── 9. AT-RISK STATUS METRIC CARDS ── */
        .at-risk-total [data-testid="metric-container"] { border-left: 4px solid #ef4444 !important; }
        .at-risk-marks [data-testid="metric-container"] { border-left: 4px solid #f97316 !important; }
        .at-risk-attendance [data-testid="metric-container"] { border-left: 4px solid #eab308 !important; }
        .at-risk-both [data-testid="metric-container"] { border-left: 4px solid #dc2626 !important; }

        /* ── 10. DATAFRAMES & TABLES ── */
        [data-testid="stDataFrame"],
        [data-testid="stTable"],
        div[data-testid="stDataFrameContainer"],
        .stDataFrame, .stTable {
            font-family: Arial, Helvetica, sans-serif !important;
            color: #09090b !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 8px !important;
        }

        [data-testid="stTable"] th,
        .stTable th {
            background-color: #f4f4f5 !important;
            color: #09090b !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important; /* Semibold table header */
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            padding: 10px 14px !important;
            border-bottom: 1px solid #e4e4e7 !important;
        }
        [data-testid="stTable"] td,
        .stTable td {
            color: #09090b !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 14px !important;
            font-weight: 400 !important; /* Normal weight cell content */
            padding: 10px 14px !important;
            border-bottom: 1px solid #e4e4e7 !important;
        }

        /* ── 11. BUTTONS ── */
        .stButton > button,
        .stDownloadButton > button,
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {
            border-radius: 9999px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 14px !important;
            line-height: 20px !important;
            font-weight: 500 !important;
            padding: 8px 24px !important;
            background-color: #ffffff !important;
            border: 1px solid #d4d4d8 !important;
            color: #09090b !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            background-color: #09090b !important;
            color: #ffffff !important;
            border-color: #09090b !important;
        }

        /* ── 12. TABS ── */
        button[data-baseweb="tab"] {
            font-family: Arial, Helvetica, sans-serif !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            color: #71717a !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #09090b !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #09090b !important;
        }

        /* ── 13. MULTISELECT & INPUTS ── */
        [data-baseweb="tag"] {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            background-color: #f4f4f5 !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 9999px !important;
            color: #09090b !important;
        }
        [data-baseweb="select"] input,
        [data-baseweb="input"] input {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 15px !important;
        }
        [data-testid="stSlider"] label,
        [data-testid="stSlider"] [data-testid="stWidgetLabel"] p {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }
        [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }
        /* Hide duplicate tick labels in Streamlit slider */
        [data-testid="stSliderTickBar"] {
            display: none !important;
        }

        /* ── 14. PROFILE CARD & HIGHLIGHT CARDS ── */
        .profile-card {
            background-color: #ffffff !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 10px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            font-family: Arial, Helvetica, sans-serif !important;
        }
        .highlight-name {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            color: #09090b !important;
        }

        /* Styled Performer Cards */
        .performer-card {
            background-color: #ffffff !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 10px !important;
            padding: 16px 20px !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 4px !important;
        }
        .performer-card.top { border-left: 4px solid #16a34a !important; }
        .performer-card.lowest { border-left: 4px solid #ea580c !important; }

        /* ── 15. MULTISELECT OVERLAP FIX ── */
        [data-baseweb="select"] > div:first-child {
            padding-right: 44px !important;
        }

        /* ── 16. SUBTLE ACCENT CARD PANELS ── */
        .table-card-container {
            background-color: #ffffff !important;
            border: 1px solid #e4e4e7 !important;
            border-radius: 10px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
            margin-bottom: 20px !important;
        }
        .table-card-header {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #09090b !important;
            margin-bottom: 12px !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
    </style>

    <!-- JavaScript to Disable Right-Click Context Menu -->
    <script>
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
        }, false);
    </script>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_CSV_PATH = pathlib.Path(__file__).parent / "data" / "sample_students.csv"


@st.cache_data(show_spinner="Loading and cleaning data…")
def load_sample() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load and clean the bundled sample dataset. Cached so reruns are instant."""
    raw = pd.read_csv(SAMPLE_CSV_PATH)
    validated = load_and_validate(raw)
    cleaned, report = clean_data(validated)
    return raw, cleaned, report


@st.cache_data(show_spinner="Cleaning uploaded data…")
def load_uploaded(file_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load and clean a user-uploaded CSV. Cached by file content hash."""
    raw = pd.read_csv(io.BytesIO(file_bytes))
    validated = load_and_validate(raw)
    cleaned, report = clean_data(validated)
    return raw, cleaned, report


# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION SETUP
# ─────────────────────────────────────────────────────────────────────────────
pg = st.navigation(
    [
        st.Page("pages/pg_overview.py",          title="Overview",            icon=":material/grid_view:", default=True),
        st.Page("pages/pg_performance.py",       title="Performance Analysis", icon=":material/analytics:"),
        st.Page("pages/pg_charts.py",            title="Visual Exploration",   icon=":material/insights:"),
        st.Page("pages/pg_at_risk.py",           title="At-Risk Students",    icon=":material/warning:"),
        st.Page("pages/pg_risk_prediction.py",   title="Risk Prediction",      icon=":material/model_training:"),
        st.Page("pages/pg_marks_prediction.py",  title="Marks Prediction",     icon=":material/auto_graph:"),
        st.Page("pages/pg_student_segments.py",  title="Student Segments",     icon=":material/pie_chart:"),
        st.Page("pages/pg_semester_forecast.py", title="Semester Forecast",    icon=":material/timeline:"),
        st.Page("pages/pg_student_lookup.py",    title="Student Lookup",       icon=":material/person_search:"),
        st.Page("pages/pg_reports.py",          title="Reports",              icon=":material/assessment:"),
    ]
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Branding + Dataset upload
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # 1. Premium Light Primary-Colored Brand Header Card
    st.markdown(
        f'''
        <div class="edu-sidebar-brand-card" style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 16px;
            color: #0f172a;
            box-shadow: 0 2px 10px rgba(37, 99, 235, 0.06);
            margin-bottom: 8px;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="
                        width: 42px; height: 42px; border-radius: 10px;
                        background: #eff6ff;
                        border: 1px solid #dbeafe;
                        display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.12);
                        flex-shrink: 0;
                    ">
                        {icon_edumetrics_logo(34, color="#2563eb")}
                    </div>
                    <div class="edu-sidebar-brand-card-text" style="display: flex; flex-direction: column; justify-content: center; min-width: 0;">
                        <span style="font-size: 17px; font-weight: 800; color: #1e293b; line-height: 20px; letter-spacing: -0.4px; display: block; white-space: nowrap;">EduMetrics</span>
                        <span style="font-size: 11px; color: #64748b; font-weight: 600; line-height: 14px; margin-top: 2px; display: block; white-space: nowrap;">Academic Analytics Suite</span>
                    </div>
                </div>
                <span class="edu-sidebar-brand-badge" style="
                    font-size: 10px; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.6px; background: #eff6ff;
                    color: #2563eb; border: 1px solid #bfdbfe;
                    padding: 3px 7px; border-radius: 6px;
                ">v2.5</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # 2. Dataset Section Card & Upload Container
    st.markdown(
        f'''
        <div class="edu-sidebar-dataset-card" style="
            background: #ffffff;
            border: 1px solid #e4e4e7;
            border-radius: 10px;
            padding: 12px 14px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        ">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.1px; color: #71717a; display: flex; align-items: center; justify-content: space-between;">
                <span style="display: flex; align-items: center; gap: 6px;">
                    {icon_folder(15, color="#71717a")} DATASET ENGINE
                </span>
                <span style="display: flex; align-items: center; gap: 4px; color: #16a34a; font-size: 11px; font-weight: 600; text-transform: none; letter-spacing: normal;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #16a34a; display: inline-block;"></span> Active
                </span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload student CSV file(s)",
        type=["csv"],
        accept_multiple_files=True,
        key="uploader_csv",
        help=(
            "Upload 1 or multiple classroom/division CSV files. Must contain: "
            "Student_ID, Name, Department, Semester, Maths, Programming, Database, "
            "AI_ML, Attendance, Internal_Marks, Final_Marks"
        ),
    )

    if "cleaned_df" in st.session_state and st.session_state.cleaned_df is not None and not st.session_state.cleaned_df.empty:
        if st.button("🗑️ Reset / Clear Dataset", use_container_width=True, key="btn_reset_dataset"):
            st.session_state.cleaned_df = pd.DataFrame()
            st.session_state.raw_df = pd.DataFrame()
            st.session_state.quality_report = {}
            st.session_state.filtered_df = pd.DataFrame()
            st.rerun()

    st.markdown(
        '''
        <div class="edu-sidebar-footer" style="
            border-top: 1px solid #e2e8f0;
            padding-top: 14px;
            margin-top: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 11px;
            color: #64748b;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                <span style="font-weight: 700; color: #334155; font-size: 11px; letter-spacing: -0.1px;">EduMetrics Suite</span>
                <span style="display: inline-flex; align-items: center; gap: 5px; color: #16a34a; font-weight: 600; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 12px; font-size: 10px;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #16a34a; display: inline-block;"></span> Ready
                </span>
            </div>
            <div style="font-size: 10px; color: #94a3b8; font-weight: 500; display: flex; align-items: center; gap: 4px;">
                <span>All Systems Operational</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA & MULTI-FILE INGESTION
# ─────────────────────────────────────────────────────────────────────────────
raw_df: pd.DataFrame | None = None
cleaned_df: pd.DataFrame | None = None
quality_report: dict | None = None
load_error: str | None = None

from utils.data_cleaning import load_sample, load_uploaded, process_multiple_files

try:
    if uploaded_files and len(uploaded_files) > 0:
        if len(uploaded_files) == 1:
            f = uploaded_files[0]
            raw_df, cleaned_df, quality_report = load_uploaded(f.getvalue())
            cleaned_df["Source_File"] = f.name
            raw_df["Source_File"] = f.name
        else:
            raw_df, cleaned_df, quality_report = process_multiple_files(uploaded_files)
        st.session_state.cleaned_df = cleaned_df
        st.session_state.raw_df = raw_df
        st.session_state.quality_report = quality_report
    else:
        if "cleaned_df" in st.session_state and st.session_state.cleaned_df is not None and not st.session_state.cleaned_df.empty:
            cleaned_df = st.session_state.cleaned_df
            raw_df = st.session_state.get("raw_df", cleaned_df)
            quality_report = st.session_state.get("quality_report", {})
except ValueError as exc:
    load_error = str(exc)
except Exception as exc:
    load_error = f"Unexpected error loading data: {exc}"

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT AREA — MANDATORY UPLOAD LANDING SCREEN vs DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if load_error:
    st.error(f"❌ **Data Ingestion Error**: {load_error}")
    st.session_state.filtered_df = pd.DataFrame()
    st.stop()

if cleaned_df is None or cleaned_df.empty:
    st.session_state.filtered_df = pd.DataFrame()
    st.session_state.cleaned_df = pd.DataFrame()

    # RENDER MANDATORY UPLOAD LANDING INSTRUCTIONS SCREEN
    landing_html = f'''<div style="background: #ffffff; border: 1px solid #e4e4e7; border-radius: 16px; padding: 40px 36px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin: 30px auto; max-width: 880px;">
<div style="width: 68px; height: 68px; border-radius: 18px; background: #eff6ff; border: 1px solid #dbeafe; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; box-shadow: 0 8px 24px rgba(37, 99, 235, 0.15);">
{icon_edumetrics_logo(48, color="#2563eb")}
</div>
<span class="eyebrow-mono" style="color: #2563eb;">EduMetrics Suite v2.5</span>
<h1 style="font-size: 30px; font-weight: 700; color: #09090b; margin: 8px 0 12px 0;">Upload Student CSV Datasets to Begin</h1>
<p style="font-size: 15px; color: #52525b; max-width: 650px; margin: 0 auto 28px auto; line-height: 1.6;">
Welcome to EduMetrics! Please follow the simple steps below to upload your classroom or division CSV datasets using the sidebar on the left.
</p>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; text-align: left; margin-bottom: 28px;">
<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 16px;">
<div style="background: #eff6ff; color: #2563eb; width: 28px; height: 28px; border-radius: 50%; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">1</div>
<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Open Left Sidebar</div>
<div style="font-size: 12px; color: #64748b; line-height: 1.5;">Locate the <strong>DATASET ENGINE</strong> section in the sidebar on the left side of your screen.</div>
</div>

<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 16px;">
<div style="background: #eff6ff; color: #2563eb; width: 28px; height: 28px; border-radius: 50%; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">2</div>
<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Select CSV File(s)</div>
<div style="font-size: 12px; color: #64748b; line-height: 1.5;">Click <strong>Browse files</strong> or drag &amp; drop 1 or multiple division CSV files at once.</div>
</div>

<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 16px;">
<div style="background: #eff6ff; color: #2563eb; width: 28px; height: 28px; border-radius: 50%; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">3</div>
<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Explore Analytics</div>
<div style="font-size: 12px; color: #64748b; line-height: 1.5;">EduMetrics automatically cleans, validates, and aggregates records into real-time ML dashboards.</div>
</div>
</div>

<div style="background: #f4f4f5; border: 1px dashed #d4d4d8; border-radius: 12px; padding: 16px 20px; text-align: left;">
<div style="font-size: 13px; font-weight: 700; color: #09090b; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
{icon_info(16, color="#2563eb")} Required CSV Header Format:
</div>
<code style="font-size: 12px; color: #2563eb; background: #ffffff; padding: 8px 12px; border-radius: 6px; border: 1px solid #e4e4e7; display: block; overflow-x: auto;">
Student_ID, Name, Department, Semester, Maths, Programming, Database, AI_ML, Attendance, Internal_Marks, Final_Marks
</code>
</div>
</div>'''
    st.markdown(landing_html, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTERS PANEL & SESSION STATE POPULATION (AFTER DATA UPLOAD)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("Filter Controls & Thresholds", expanded=True):
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        dept_options = sorted(cleaned_df["Department"].dropna().unique().tolist()) if (cleaned_df is not None and "Department" in cleaned_df.columns) else []
        selected_depts = st.multiselect(
            "Department",
            options=dept_options,
            default=dept_options,
            key="filter_dept",
        )

    with f_col2:
        sem_options = sorted(cleaned_df["Semester"].dropna().unique().tolist()) if (cleaned_df is not None and "Semester" in cleaned_df.columns) else []
        selected_sems = st.multiselect(
            "Semester",
            options=sem_options,
            default=sem_options,
            key="filter_sem",
        )

    with f_col3:
        source_options = sorted(cleaned_df["Source_File"].dropna().unique().tolist()) if "Source_File" in cleaned_df.columns else ["Uploaded Dataset"]
        selected_sources = st.multiselect(
            "Source File / Division",
            options=source_options,
            default=source_options,
            key="filter_source_files",
            help="Select one or multiple uploaded classroom/division CSV files to view.",
        )

    with f_col4:
        subj_options = ["All Subjects", "Maths", "Programming", "Database", "AI_ML"]
        selected_subject = st.selectbox(
            "Highlight Subject",
            options=subj_options,
            index=0,
            key="filter_subj",
        )

    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    with f_c1:
        att_range = st.slider(
            "Attendance range (%)",
            min_value=0.0, max_value=100.0,
            value=(0.0, 100.0), step=1.0,
            key="filter_att",
        )

    with f_c2:
        marks_range = st.slider(
            "Average marks range",
            min_value=0.0, max_value=100.0,
            value=(0.0, 100.0), step=1.0,
            key="filter_marks",
        )

    with f_c3:
        marks_threshold = st.slider(
            "Marks threshold (< flagged)",
            min_value=0, max_value=100, value=40, step=1,
            help="Students whose average subject marks fall below this value are flagged.",
            key="threshold_marks",
        )

    with f_c4:
        attendance_threshold = st.slider(
            "Attendance threshold (< flagged)",
            min_value=0, max_value=100, value=75, step=1,
            help="Students whose attendance (%) falls below this value are flagged.",
            key="threshold_attendance",
        )

# ── APPLY FILTERS ──────────────────────────────────────────────────────────
graded_df = compute_grades(cleaned_df)

source_mask = graded_df["Source_File"].isin(selected_sources) if ("Source_File" in graded_df.columns and selected_sources) else True

mask = (
    graded_df["Department"].isin(selected_depts)
    & graded_df["Semester"].isin(selected_sems)
    & source_mask
    & (graded_df["Attendance"] >= att_range[0])
    & (graded_df["Attendance"] <= att_range[1])
    & (graded_df["Avg_Marks"] >= marks_range[0])
    & (graded_df["Avg_Marks"] <= marks_range[1])
)
filtered_df = graded_df[mask].reset_index(drop=True)

# ── Persist all shared data in session_state ──────────────────────────
st.session_state.filtered_df = filtered_df
st.session_state.cleaned_df = cleaned_df
st.session_state.raw_df = raw_df
st.session_state.quality_report = quality_report
st.session_state.marks_threshold = marks_threshold
st.session_state.attendance_threshold = attendance_threshold
st.session_state.selected_subject = selected_subject
st.session_state.load_error = None

# Warn globally if filters yield empty result — visible on any page
if filtered_df.empty:
    st.warning(
        "No students match the current filters. Please adjust the filter controls above.",
    )

# ─────────────────────────────────────────────────────────────────────────────
# RUN ACTIVE PAGE & AI CHATBOT
# ─────────────────────────────────────────────────────────────────────────────
render_ai_chatbot()

with st.spinner("Updating EduMetrics analytics & machine learning models..."):
    pg.run()
