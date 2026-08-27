"""
utils/ai_chatbot.py
-------------------
EduMetrics AI Chatbot Service (Powered by Google Gemini API).
Constructs rich, compact dataset context (including full student roster details)
and handles Gemini API communication with round-robin key load balancing,
detailed error logging, and automatic failover.
"""

import json
import logging
import ssl
import urllib.error
import urllib.request
import pandas as pd

import os

# Configure Logger for EduMetrics AI
logger = logging.getLogger("EduMetricsAI")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def get_gemini_api_keys() -> list:
    """Fetch Gemini API keys from environment variables or Streamlit secrets safely."""
    keys_env = os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY") or ""
    if not keys_env:
        try:
            import streamlit as st
            if "GEMINI_API_KEYS" in st.secrets:
                keys_env = st.secrets["GEMINI_API_KEYS"]
            elif "GEMINI_API_KEY" in st.secrets:
                keys_env = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    if isinstance(keys_env, list):
        return [k for k in keys_env if k]
    if isinstance(keys_env, str) and keys_env.strip():
        return [k.strip() for k in keys_env.split(",") if k.strip()]
    return ["YOUR_GEMINI_API_KEY_HERE"]


GEMINI_API_KEYS = get_gemini_api_keys()

# Keep alias for backwards compatibility
GROQ_API_KEYS = GEMINI_API_KEYS
GROQ_API_KEY = GEMINI_API_KEYS[0]

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
DEFAULT_MODEL = "gemini-3.6-flash"

_key_index = 0


def get_rotated_api_keys() -> list:
    """Return API keys ordered starting from the current round-robin index for load balancing & failover."""
    global _key_index
    start_idx = _key_index % len(GEMINI_API_KEYS)
    _key_index += 1
    return [GEMINI_API_KEYS[(start_idx + i) % len(GEMINI_API_KEYS)] for i in range(len(GEMINI_API_KEYS))]


def _create_ssl_context():
    """Create SSL context with fallback for macOS certificate bundle issues."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()


def _parse_http_error(http_err: urllib.error.HTTPError) -> str:
    """Extract detailed JSON error message from HTTP response body."""
    try:
        err_body = http_err.read().decode("utf-8", errors="ignore")
        if err_body:
            try:
                err_json = json.loads(err_body)
                if "error" in err_json:
                    err_obj = err_json["error"]
                    msg = err_obj.get("message", "")
                    code = err_obj.get("code", http_err.code)
                    status = err_obj.get("status", "")
                    return f"HTTP {code} ({status}): {msg}" if status else f"HTTP {code}: {msg}"
            except Exception:
                return f"HTTP {http_err.code}: {err_body[:300]}"
    except Exception:
        pass
    return f"HTTP Error {http_err.code}: {http_err.reason}"


def _send_gemini_request(api_key: str, payload: dict, timeout: int = 25) -> str:
    """Helper function to execute HTTP POST request to Google Gemini API with given key."""
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "INVALID_KEY"
    url = f"{GEMINI_API_URL}?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        },
    )

    try:
        ssl_ctx = _create_ssl_context()
        resp_obj = urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
    except urllib.error.HTTPError as http_err:
        detailed_err = _parse_http_error(http_err)
        logger.error(f"[Gemini API Request Failed with Key {masked_key}] -> {detailed_err}")
        raise RuntimeError(detailed_err) from http_err
    except Exception as exc:
        if "CERTIFICATE_VERIFY_FAILED" in str(exc) or "certificate verify failed" in str(exc):
            logger.warning(f"[SSL Verification Warning] Retrying with unverified SSL context for key {masked_key}")
            unverified_ctx = ssl._create_unverified_context()
            try:
                resp_obj = urllib.request.urlopen(req, timeout=timeout, context=unverified_ctx)
            except urllib.error.HTTPError as http_err2:
                detailed_err = _parse_http_error(http_err2)
                logger.error(f"[Gemini API Request Failed (Unverified SSL) with Key {masked_key}] -> {detailed_err}")
                raise RuntimeError(detailed_err) from http_err2
        else:
            logger.error(f"[Network/Connection Error with Key {masked_key}] -> {exc}")
            raise exc

    with resp_obj as resp:
        data = json.loads(resp.read().decode("utf-8"))
        try:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if "<think>" in answer and "</think>" in answer:
                answer = answer.split("</think>")[-1].strip()
            logger.info(f"[Gemini API Request Succeeded with Key {masked_key}]")
            return answer
        except (KeyError, IndexError) as parse_err:
            logger.error(f"[Gemini API Payload Parsing Error] Unexpected response format: {data}")
            raise RuntimeError(f"Unexpected API response format: {data}") from parse_err


def build_dataset_context(
    filtered_df: pd.DataFrame,
    marks_threshold: float,
    attendance_threshold: float,
    user_query: str = "",
) -> str:
    """Build a rich, compact JSON context string containing KPIs, summary statistics, and student records."""
    if filtered_df.empty:
        return "The dataset currently has 0 matching students with the active filters."

    from utils.analytics import compute_kpis, subject_averages, grade_distribution
    from utils.risk_detection import flag_at_risk

    kpis = compute_kpis(filtered_df)
    subj_avg = subject_averages(filtered_df).to_dict(orient="records")
    grade_dist = grade_distribution(filtered_df).to_dict(orient="records")
    at_risk_df = flag_at_risk(filtered_df, marks_threshold, attendance_threshold)

    # Department averages
    dept_summary = {}
    if "Department" in filtered_df.columns and "Avg_Marks" in filtered_df.columns:
        dept_summary = filtered_df.groupby("Department")["Avg_Marks"].mean().round(2).to_dict()

    # Compact student roster representation
    student_records = []
    subject_cols = [c for c in ["Maths", "Programming", "Database", "AI_ML"] if c in filtered_df.columns]

    for _, r in filtered_df.iterrows():
        rec = {
            "id": str(r.get("Student_ID", "")),
            "name": str(r.get("Name", "")),
            "dept": str(r.get("Department", "")),
            "sem": str(r.get("Semester", "")),
            "avg": round(float(r.get("Avg_Marks", 0)), 2),
            "grade": str(r.get("Grade", "")),
            "att": float(r.get("Attendance", 0)),
        }
        sub_scores = {s: float(r[s]) for s in subject_cols if pd.notna(r.get(s))}
        if sub_scores:
            rec["scores"] = sub_scores

        student_records.append(rec)

    # Limit total student records if dataset is massive to prevent payload overflow
    if len(student_records) > 60:
        query_lower = user_query.lower()
        matched = [s for s in student_records if s["name"].lower() in query_lower or s["id"].lower() in query_lower]
        others = [s for s in student_records if s not in matched]
        student_records = (matched + others)[:40]

    at_risk_summary = []
    if not at_risk_df.empty:
        for _, row in at_risk_df.head(15).iterrows():
            at_risk_summary.append({
                "id": row.get("Student_ID"),
                "name": row.get("Name"),
                "dept": row.get("Department"),
                "reason": row.get("Risk_Reason"),
            })

    context_dict = {
        "kpi_summary": {
            "total_students": kpis["student_count"],
            "class_avg_marks": kpis["avg_marks"],
            "class_avg_attendance": kpis["avg_attendance"],
            "pass_percentage": kpis["pass_pct"],
            "top_performer": kpis["top_performer"],
            "lowest_performer": kpis["lowest_performer"],
        },
        "department_averages": dept_summary,
        "subject_averages": subj_avg,
        "grade_distribution": grade_dist,
        "at_risk_summary": {
            "count": len(at_risk_df),
            "flagged_sample": at_risk_summary,
        },
        "all_students": student_records,
    }

    return json.dumps(context_dict, separators=(",", ":"))


def ask_groq_chatbot(
    user_query: str,
    filtered_df: pd.DataFrame,
    marks_threshold: float = 40,
    attendance_threshold: float = 75,
    chat_history: list = None,
) -> str:
    """
    Send query + dataset context to Google Gemini API using round-robin API key rotation
    and automatic failover if a key experiences rate limits (429) or errors.
    """
    dataset_context = build_dataset_context(filtered_df, marks_threshold, attendance_threshold, user_query)

    system_prompt = (
        "You are EduMetrics AI, an expert academic performance assistant.\n"
        "Answer user questions accurately using the currently filtered student dataset context below.\n\n"
        "RULES:\n"
        "1. Base answers strictly on the provided JSON dataset context (including student roster details).\n"
        "2. If asked about a student (e.g., 'Aditya Kumar'), look up their ID, department, semester, average score, grade, attendance, and subject scores in 'all_students'.\n"
        "3. Be concise, direct, professional, and helpful.\n"
        "4. Format responses cleanly using markdown bullet points.\n\n"
        f"DATASET CONTEXT (JSON):\n{dataset_context}"
    )

    contents = []
    if chat_history:
        for msg in chat_history[-4:]:  # Last 2 turns only
            role = "user" if msg.get("role") == "user" else "model"
            content = str(msg.get("content", ""))
            if len(content) > 300:
                content = content[:300] + "…"
            contents.append({"role": role, "parts": [{"text": content}]})

    contents.append({"role": "user", "parts": [{"text": user_query}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }

    keys_to_try = get_rotated_api_keys()
    collected_errors = []

    for key in keys_to_try:
        masked = f"{key[:8]}...{key[-4:]}"
        try:
            return _send_gemini_request(key, payload, timeout=25)
        except Exception as exc:
            collected_errors.append(f"Key ({masked}): {exc}")
            exc_str = str(exc)
            if "413" in exc_str or "Payload" in exc_str:
                return _ask_gemini_fallback(user_query, dataset_context, keys_to_try)
            # Try next key on error
            continue

    # If all keys failed, display detailed, human-friendly error details
    error_summary = " | ".join(collected_errors)
    logger.error(f"[AI Chatbot Error - All Keys Failed] {error_summary}")

    if any("429" in e or "Quota" in e or "ResourceExhausted" in e for e in collected_errors):
        return (
            "⚡ **Gemini API Rate Limit / Quota Exceeded** across all configured API keys.\n\n"
            f"**Error Details:** `{error_summary}`\n\n"
            "Please wait a few seconds and try again."
        )

    return f"❌ **AI Assistant Communication Error**:\n\n{error_summary}"


def _ask_gemini_fallback(user_query: str, dataset_context: str, keys_to_try: list = None) -> str:
    """Fallback handler with minimal payload if payload is too large, iterating through configured keys."""
    if not keys_to_try:
        keys_to_try = get_rotated_api_keys()

    payload = {
        "system_instruction": {
            "parts": [{"text": f"Answer concisely using this JSON dataset context:\n{dataset_context[:3000]}"}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_query}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }

    collected_errors = []
    for key in keys_to_try:
        masked = f"{key[:8]}...{key[-4:]}"
        try:
            return _send_gemini_request(key, payload, timeout=15)
        except Exception as e:
            collected_errors.append(f"Key ({masked}): {e}")
            continue

    err_msg = " | ".join(collected_errors)
    logger.error(f"[AI Chatbot Fallback Error] {err_msg}")
    return f"❌ **Could not retrieve answer**:\n\n{err_msg}"



