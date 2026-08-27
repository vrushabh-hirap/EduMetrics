"""
utils/ai_widget.py
------------------
EduMetrics Floating AI Chatbot Widget.
Renders an animated SVG circular button (80px x 80px) at bottom: 36px, right: 36px with continuous animation.
When clicked, opens a spacious, modern popover chat window for context-aware Q&A powered by Groq.
Suggested question chips only display when chat history is empty.
"""

import base64
import importlib
import streamlit as st
import utils.ai_chatbot as ai_chatbot
from utils.avatar_data import RAW_CHATBOT_SVG
from utils.icons import icon_academic_cap



def render_ai_chatbot() -> None:
    """Render the single fixed floating circular animated SVG AI Assistant popover button and chat dialog."""
    if "filtered_df" not in st.session_state or st.session_state.filtered_df is None:
        return

    filtered_df = st.session_state.filtered_df
    marks_thresh = st.session_state.get("marks_threshold", 40)
    att_thresh = st.session_state.get("attendance_threshold", 75)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Inject CSS for floating SVG button & enlarged popover chat window
    st.markdown(
        f"""
        <style>
            /* 1. Live Animated SVG Container (Fixed at Bottom: 32px; Right: 32px) */
            .edu-animated-bot-fab {{
                position: fixed !important;
                bottom: 32px !important;
                right: 32px !important;
                width: 76px !important;
                height: 76px !important;
                border-radius: 50% !important;
                z-index: 999998 !important;
                pointer-events: none !important;
                filter: drop-shadow(0 6px 20px rgba(0, 0, 0, 0.22)) !important;
                transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            }}

            /* Zero out layout height in document flow below filter section */
            div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *)),
            div[data-testid="stElementContainer"]:has(button[aria-label*="EduMetrics"]),
            div[data-testid="stElementContainer"]:has(button[title*="EduMetrics"]) {{
                height: 0 !important;
                min-height: 0 !important;
                max-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: visible !important;
                border: none !important;
            }}

            /* 2. Position ONLY the Single AI Chatbot Popover Container at Bottom-Right Corner */
            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *),
            div[data-testid="stPopover"]:has(button[aria-label*="EduMetrics"]),
            div[data-testid="stPopover"]:has(button[title*="EduMetrics"]) {{
                position: fixed !important;
                bottom: 32px !important;
                right: 32px !important;
                width: 76px !important;
                height: 76px !important;
                z-index: 999999 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            /* Transparent Overlay Popover Button Sitting Directly over the SVG Icon */
            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *) > button,
            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *) button,
            div[data-testid="stPopover"]:has(button[aria-label*="EduMetrics"]) button,
            div[data-testid="stPopover"]:has(button[title*="EduMetrics"]) button {{
                position: fixed !important;
                bottom: 32px !important;
                right: 32px !important;
                width: 76px !important;
                height: 76px !important;
                border-radius: 50% !important;
                opacity: 0.0001 !important;
                background: transparent !important;
                border: none !important;
                outline: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                cursor: pointer !important;
                z-index: 999999 !important;
                pointer-events: auto !important;
            }}

            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *) button *,
            div[data-testid="stPopover"]:has(button[aria-label*="EduMetrics"]) button *,
            div[data-testid="stPopover"]:has(button[title*="EduMetrics"]) button * {{
                opacity: 0.0001 !important;
                pointer-events: none !important;
            }}

            /* Hover zoom on the animated SVG when button is hovered */
            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *):hover ~ .edu-animated-bot-fab,
            div[data-testid="stPopover"]:not(div[data-testid="stColumn"] *):hover + .edu-animated-bot-fab,
            div[data-testid="stPopover"]:has(button[aria-label*="EduMetrics"]):hover ~ .edu-animated-bot-fab,
            div[data-testid="stPopover"]:has(button[aria-label*="EduMetrics"]):hover + .edu-animated-bot-fab {{
                transform: scale(1.1) !important;
            }}

            /* Position Opened Chat Window Container Fixed at Bottom-Right Corner (above SVG icon) */
            div[data-testid="stPopoverBody"]:has(.edu-chatbot-header-card),
            div[data-baseweb="popover"]:has(.edu-chatbot-header-card) {{
                position: fixed !important;
                bottom: 116px !important;
                right: 32px !important;
                top: auto !important;
                left: auto !important;
                transform: none !important;
                width: 500px !important;
                max-width: 92vw !important;
                max-height: 75vh !important;
                border-radius: 16px !important;
                border: 1px solid #e4e4e7 !important;
                box-shadow: 0 20px 48px rgba(0, 0, 0, 0.22) !important;
                padding: 18px !important;
                background-color: #ffffff !important;
                z-index: 9999999 !important;
                opacity: 1 !important;
                overflow-y: auto !important;
            }}

            /* Ensure text inside chatbot popover body remains visible & wraps cleanly */
            div[data-testid="stPopoverBody"]:has(.edu-chatbot-header-card) * {{
                opacity: 1 !important;
                visibility: visible !important;
            }}

            /* Enable smooth thin scrollbars specifically inside the AI chatbot popover window */
            div[data-testid="stPopoverBody"]:has(.edu-chatbot-header-card) ::-webkit-scrollbar {{
                display: block !important;
                width: 6px !important;
                height: 6px !important;
                background: #f4f4f5 !important;
            }}
            div[data-testid="stPopoverBody"]:has(.edu-chatbot-header-card) ::-webkit-scrollbar-thumb {{
                background: #a1a1aa !important;
                border-radius: 9999px !important;
            }}
        </style>
        <div class="edu-animated-bot-fab">
            {RAW_CHATBOT_SVG}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render st.popover as the single clickable popover overlay
    with st.popover("", help="Click to open EduMetrics AI Assistant", key="ai_chatbot_popover_widget"):
        # Header Card
        st.markdown(
            f'''
            <div class="edu-chatbot-header-card" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f4f4f5; padding-bottom: 12px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; background: #36c5fe15; display: flex; align-items: center; justify-content: center;">
                        {RAW_CHATBOT_SVG}
                    </div>
                    <div>
                        <div style="font-size: 17px; font-weight: 700; color: #09090b; line-height: 22px;">EduMetrics AI</div>
                        <div style="font-size: 12px; color: #16a34a; font-weight: 600; display: flex; align-items: center; gap: 4px;">
                            <span style="display: inline-block; width: 7px; height: 7px; background-color: #16a34a; border-radius: 50%;"></span> Online &amp; Ready
                        </div>
                    </div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        # Suggested Questions — SHOW ONLY FOR FIRST TIME (when chat history is empty)
        if not st.session_state.chat_history:
            st.markdown(
                '<p style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #71717a; margin-bottom: 8px;">'
                'Suggested Questions'
                '</p>',
                unsafe_allow_html=True,
            )

            chip1, chip2 = st.columns(2)
            with chip1:
                if st.button("🏆 Top Performer", key="ai_chip1", use_container_width=True):
                    st.session_state.pending_query = "Who is the top performer and what are their scores?"

            with chip2:
                if st.button("🚨 At-Risk List", key="ai_chip2", use_container_width=True):
                    st.session_state.pending_query = "How many students are at risk and why?"

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Enlarged Chat History Scrollable Container (400px height)
        chat_box = st.container(height=400)
        with chat_box:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div style="text-align: center; padding: 40px 10px; color: #71717a;">'
                    '<p style="font-size: 24px; margin-bottom: 8px;">👋</p>'
                    '<p style="font-size: 14px; font-weight: 600; color: #09090b; margin-bottom: 4px;">How can I help you today?</p>'
                    '<p style="font-size: 13px; color: #71717a;">Ask any question about student performance, department averages, or at-risk lists.</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input Prompt Field
        query_input = st.chat_input("Ask EduMetrics AI...", key="ai_chat_input")
        query_to_run = query_input or st.session_state.pop("pending_query", None)

        if query_to_run:
            st.session_state.chat_history.append({"role": "user", "content": query_to_run})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(query_to_run)
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing student dataset..."):
                        importlib.reload(ai_chatbot)
                        ans = ai_chatbot.ask_groq_chatbot(
                            user_query=query_to_run,
                            filtered_df=filtered_df,
                            marks_threshold=marks_thresh,
                            attendance_threshold=att_thresh,
                            chat_history=st.session_state.chat_history,
                        )
                        st.markdown(ans)
                        st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()
