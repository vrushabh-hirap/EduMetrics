"""
utils/analytics.py
------------------
Pure-computation functions for EduMetrics.
All functions accept a cleaned Pandas DataFrame and return either a scalar,
a dict of KPIs, or a new DataFrame — they contain no Streamlit calls.
"""

import pandas as pd
import numpy as np

# Assumption: "average marks" for a student = mean of these four subject scores.
# The computed average is also used to derive letter grades and rankings.
SUBJECT_COLUMNS = ["Maths", "Programming", "Database", "AI_ML"]

# Grade boundaries (inclusive upper bound)
GRADE_BOUNDARIES = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0,  "F"),
]

# Pass threshold: student is considered "passed" if avg subject marks >= 40
PASS_THRESHOLD = 40


def _avg_marks_series(df: pd.DataFrame) -> pd.Series:
    """
    Internal helper: compute the per-student average across subject columns
    that actually exist in the DataFrame (graceful if a column is absent).
    """
    available = [c for c in SUBJECT_COLUMNS if c in df.columns]
    if not available:
        return pd.Series(0.0, index=df.index)
    return df[available].mean(axis=1)


def compute_grades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add an 'Avg_Marks' and 'Grade' column to the DataFrame.
    'Grade' is a letter grade derived from 'Avg_Marks' using GRADE_BOUNDARIES.
    Returns a copy so the original is never mutated.
    """
    df = df.copy()
    df["Avg_Marks"] = _avg_marks_series(df).round(2)

    def _letter_grade(score: float) -> str:
        for threshold, grade in GRADE_BOUNDARIES:
            if score >= threshold:
                return grade
        return "F"

    df["Grade"] = df["Avg_Marks"].apply(_letter_grade)
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute the six dashboard KPI cards from a (potentially filtered) DataFrame.
    Returns a dict so app.py can unpack and display each value independently.
    """
    if df.empty:
        return {
            "avg_marks": 0.0,
            "avg_attendance": 0.0,
            "pass_pct": 0.0,
            "student_count": 0,
            "top_performer": "—",
            "lowest_performer": "—",
        }

    avg_series = _avg_marks_series(df)
    pass_count = (avg_series >= PASS_THRESHOLD).sum()

    # Find the student name at the max/min avg_marks index
    top_idx = avg_series.idxmax()
    low_idx = avg_series.idxmin()

    return {
        "avg_marks": round(float(avg_series.mean()), 2),
        "avg_attendance": round(float(df["Attendance"].mean()), 2) if "Attendance" in df.columns else 0.0,
        "pass_pct": round(float(pass_count / len(df) * 100), 1),
        "student_count": len(df),
        "top_performer": df.loc[top_idx, "Name"] if "Name" in df.columns else "—",
        "lowest_performer": df.loc[low_idx, "Name"] if "Name" in df.columns else "—",
    }


def subject_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with columns ['Subject', 'Average_Marks'] giving the
    class-wide mean for each subject.  Only includes subjects present in df.
    """
    available = [c for c in SUBJECT_COLUMNS if c in df.columns]
    avgs = {subj: round(float(df[subj].mean()), 2) for subj in available}
    return pd.DataFrame(list(avgs.items()), columns=["Subject", "Average_Marks"])


def semester_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with columns ['Semester', 'Average_Marks'] giving the
    mean avg-marks per semester, sorted by semester value.
    """
    if "Semester" not in df.columns:
        return pd.DataFrame(columns=["Semester", "Average_Marks"])
    temp = df.copy()
    temp["Avg_Marks"] = _avg_marks_series(temp)
    result = (
        temp.groupby("Semester")["Avg_Marks"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"Avg_Marks": "Average_Marks"})
    )
    # Sort semesters numerically if possible, otherwise alphabetically
    try:
        result["_sort_key"] = result["Semester"].str.extract(r"(\d+)").astype(float)
        result = result.sort_values("_sort_key").drop(columns=["_sort_key"])
    except Exception:
        result = result.sort_values("Semester")
    return result.reset_index(drop=True)


def top_students(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Return the top-n students ranked by their average subject marks.
    Includes Name, Department, Semester, Avg_Marks, and Grade columns.
    """
    temp = df.copy()
    temp["Avg_Marks"] = _avg_marks_series(temp).round(2)
    temp = temp.sort_values("Avg_Marks", ascending=False).head(n)

    # Build a tidy output frame with only the columns we want to display
    cols = [c for c in ["Student_ID", "Name", "Department", "Semester", "Avg_Marks"] if c in temp.columns]
    return temp[cols].reset_index(drop=True)


def grade_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with columns ['Grade', 'Count'] for the pie chart.
    """
    temp = compute_grades(df)
    dist = temp["Grade"].value_counts().reset_index()
    dist.columns = ["Grade", "Count"]
    # Sort by natural grade order
    grade_order = ["A+", "A", "B", "C", "D", "F"]
    dist["_order"] = dist["Grade"].apply(lambda g: grade_order.index(g) if g in grade_order else 99)
    return dist.sort_values("_order").drop(columns=["_order"]).reset_index(drop=True)


def student_profile(df: pd.DataFrame, student_id: str) -> dict:
    """
    Return a dict with the full academic profile for a single student,
    identified by Student_ID. Returns an empty dict if not found.
    """
    row = df[df["Student_ID"].astype(str) == str(student_id)]
    if row.empty:
        return {}
    row = row.iloc[0]
    profile = row.to_dict()
    # Compute avg marks and grade on the fly for the profile view
    available_subjects = [c for c in SUBJECT_COLUMNS if c in df.columns]
    if available_subjects:
        profile["Avg_Marks"] = round(float(row[available_subjects].mean()), 2)
        for threshold, grade in GRADE_BOUNDARIES:
            if profile["Avg_Marks"] >= threshold:
                profile["Grade"] = grade
                break
    return profile
