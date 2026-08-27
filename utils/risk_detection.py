"""
utils/risk_detection.py
-----------------------
At-risk student detection logic for EduMetrics.
Thresholds are passed in as parameters (not hardcoded) so the sidebar sliders
in app.py can adjust them at runtime without touching this module.
"""

import pandas as pd
from utils.analytics import SUBJECT_COLUMNS, GRADE_BOUNDARIES


def flag_at_risk(
    df: pd.DataFrame,
    marks_threshold: float,
    attendance_threshold: float,
) -> pd.DataFrame:
    """
    Identify students who fall below either the marks or attendance threshold.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned (and ideally filtered) student DataFrame.
    marks_threshold : float
        Students whose average subject marks < this value are flagged.
    attendance_threshold : float
        Students whose Attendance (%) < this value are flagged.

    Returns
    -------
    pd.DataFrame
        Subset of df for at-risk students, with an additional 'Risk_Reason'
        column describing which threshold(s) they breached.
    """
    if df.empty:
        return df.copy()

    temp = df.copy()

    # Compute per-student average marks across available subject columns
    available = [c for c in SUBJECT_COLUMNS if c in temp.columns]
    if available:
        temp["Avg_Marks"] = temp[available].mean(axis=1).round(2)
    else:
        temp["Avg_Marks"] = 0.0

    # Boolean masks for each risk condition
    low_marks = temp["Avg_Marks"] < marks_threshold
    low_attendance = (temp["Attendance"] < attendance_threshold) if "Attendance" in temp.columns else pd.Series(False, index=temp.index)

    # Build human-readable reason strings
    def _reason(row_low_marks: bool, row_low_att: bool) -> str:
        reasons = []
        if row_low_marks:
            reasons.append(f"Avg marks < {marks_threshold}")
        if row_low_att:
            reasons.append(f"Attendance < {attendance_threshold}%")
        return " | ".join(reasons)

    at_risk_mask = low_marks | low_attendance
    temp["Risk_Reason"] = temp.apply(
        lambda r: _reason(low_marks[r.name], low_attendance[r.name]), axis=1
    )

    # Keep only flagged rows; filter out "no reason" rows just in case
    result = temp[at_risk_mask & (temp["Risk_Reason"] != "")].copy()

    # Bring the most relevant columns to the front for the display table
    display_cols = ["Student_ID", "Name", "Department", "Semester",
                    "Avg_Marks", "Attendance", "Grade", "Risk_Reason"]
    # Only include columns that actually exist in result
    display_cols = [c for c in display_cols if c in result.columns]
    # Add Grade if not yet present (compute on the fly)
    if "Grade" not in result.columns and "Avg_Marks" in result.columns:
        def _grade(score: float) -> str:
            for threshold, grade in GRADE_BOUNDARIES:
                if score >= threshold:
                    return grade
            return "F"
        result["Grade"] = result["Avg_Marks"].apply(_grade)
        display_cols = ["Student_ID", "Name", "Department", "Semester",
                        "Avg_Marks", "Attendance", "Grade", "Risk_Reason"]
        display_cols = [c for c in display_cols if c in result.columns]

    return result[display_cols].reset_index(drop=True)


def risk_summary(at_risk_df: pd.DataFrame) -> dict:
    """
    Generate a quick summary dict for the at-risk section header.
    """
    if at_risk_df.empty:
        return {"total": 0, "low_marks_only": 0, "low_attendance_only": 0, "both": 0}

    both = at_risk_df["Risk_Reason"].str.contains("|", regex=False, na=False) & \
           at_risk_df["Risk_Reason"].str.contains("marks", na=False) & \
           at_risk_df["Risk_Reason"].str.contains("Attendance", na=False)

    low_marks_only = at_risk_df["Risk_Reason"].str.contains("marks", na=False) & ~both
    low_att_only = at_risk_df["Risk_Reason"].str.contains("Attendance", na=False) & ~both

    return {
        "total": len(at_risk_df),
        "low_marks_only": int(low_marks_only.sum()),
        "low_attendance_only": int(low_att_only.sum()),
        "both": int(both.sum()),
    }
