"""
utils/ml_models.py
------------------
Machine-learning helpers for EduMetrics:
  1. train_risk_model() — RandomForestClassifier for At-Risk Prediction
  2. train_marks_regressor() — RandomForestRegressor for Final Marks Prediction
  3. get_multi_semester_students() & forecast_next_semester() — Trend forecasting
  4. segment_students() — KMeans Clustering for Student Segmentation

All functions are pure computation (no Streamlit calls) and accept/return
plain Pandas DataFrames so they remain independently testable.
"""

from __future__ import annotations

import re
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error, silhouette_score
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

# Minimum dataset requirements before we attempt training.
MIN_ROWS_FOR_TRAINING = 15

# Subject columns the analytics module recognises — detection is dynamic.
_KNOWN_SUBJECT_COLUMNS = ["Maths", "Programming", "Database", "AI_ML"]


def _detect_subject_columns(df: pd.DataFrame) -> list[str]:
    """Return recognised subject columns that actually exist in df."""
    return [c for c in _KNOWN_SUBJECT_COLUMNS if c in df.columns]


def _build_at_risk_label(
    df: pd.DataFrame,
    marks_threshold: float,
    attendance_threshold: float,
) -> pd.Series:
    """
    Reuse the SAME rule-based logic as flag_at_risk() to produce a binary
    Series (1 = at-risk, 0 = not at-risk).
    """
    subject_cols = _detect_subject_columns(df)
    avg = df[subject_cols].mean(axis=1) if subject_cols else pd.Series(0.0, index=df.index)
    low_marks = avg < marks_threshold
    low_att = (
        df["Attendance"] < attendance_threshold
        if "Attendance" in df.columns
        else pd.Series(False, index=df.index)
    )
    return (low_marks | low_att).astype(int)


# ─────────────────────────────────────────────────────────────────────────────
# 1. AT-RISK PREDICTION (CLASSIFICATION)
# ─────────────────────────────────────────────────────────────────────────────
def train_risk_model(
    df: pd.DataFrame,
    marks_threshold: float,
    attendance_threshold: float,
) -> tuple:
    """
    Train a RandomForestClassifier to predict at-risk probability.

    Returns: (model, feature_importance_df, predictions_df, error_message)
    """
    if df is None or df.empty or len(df) < MIN_ROWS_FOR_TRAINING:
        n = len(df) if df is not None else 0
        return None, None, None, (
            f"Not enough data to train a reliable model — need at least "
            f"{MIN_ROWS_FOR_TRAINING} students in the current filter "
            f"(currently {n})."
        )

    subject_cols = _detect_subject_columns(df)
    feature_cols = []
    if "Attendance" in df.columns:
        feature_cols.append("Attendance")
    if "Internal_Marks" in df.columns:
        feature_cols.append("Internal_Marks")
    feature_cols.extend(subject_cols)

    if not feature_cols:
        return None, None, None, "No usable feature columns found in the dataset."

    X = df[feature_cols].copy().fillna(df[feature_cols].median(numeric_only=True))
    y = _build_at_risk_label(df, marks_threshold, attendance_threshold)

    unique_classes = y.unique()
    if len(unique_classes) < 2:
        class_desc = "all at-risk" if unique_classes[0] == 1 else "none at-risk"
        return None, None, None, (
            "Not enough data variety to train a reliable model — "
            f"all {len(df)} students in the current filter are {class_desc}. "
            "Need both at-risk and not-at-risk students present."
        )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        oob_score=True,
        n_jobs=-1,
    )
    model.fit(X, y)
    oob_accuracy = float(model.oob_score_)

    try:
        n_folds = min(3, int(y.value_counts().min()))
        cv_scores = cross_val_score(
            RandomForestClassifier(
                n_estimators=100, random_state=42,
                class_weight="balanced", n_jobs=-1,
            ),
            X, y,
            cv=n_folds,
            scoring="balanced_accuracy",
        )
        cv_accuracy = float(np.mean(cv_scores))
    except Exception:
        cv_accuracy = None

    fi_df = (
        pd.DataFrame({"Feature": feature_cols, "Importance": model.feature_importances_})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )
    fi_df.attrs["oob_accuracy"] = oob_accuracy
    fi_df.attrs["cv_accuracy"] = cv_accuracy
    fi_df.attrs["n_estimators"] = model.n_estimators
    fi_df.attrs["n_features"] = len(feature_cols)
    fi_df.attrs["n_students"] = len(df)
    fi_df.attrs["n_at_risk_label"] = int(y.sum())

    proba = model.predict_proba(X)
    at_risk_idx = list(model.classes_).index(1)
    risk_pct = proba[:, at_risk_idx] * 100.0

    def _risk_level(p: float) -> str:
        if p >= 70:
            return "High"
        if p >= 30:
            return "Medium"
        return "Low"

    pred_df = df.copy()
    pred_df["Risk_Probability"] = risk_pct.round(1)
    pred_df["Risk_Level"] = pred_df["Risk_Probability"].apply(_risk_level)

    display_cols = [
        c for c in
        ["Student_ID", "Name", "Department", "Semester", "Risk_Probability", "Risk_Level"]
        if c in pred_df.columns
    ]
    predictions_df = (
        pred_df[display_cols]
        .sort_values("Risk_Probability", ascending=False)
        .reset_index(drop=True)
    )

    return model, fi_df, predictions_df, None


# ─────────────────────────────────────────────────────────────────────────────
# 2. FINAL MARKS PREDICTION (REGRESSION)
# ─────────────────────────────────────────────────────────────────────────────
def train_marks_regressor(df: pd.DataFrame) -> tuple:
    """
    Train a RandomForestRegressor to predict Final_Marks for every student.

    Returns: (model, r2_score_val, feature_importance_df, predictions_df, error_message)
    """
    if df is None or df.empty or len(df) < MIN_ROWS_FOR_TRAINING:
        n = len(df) if df is not None else 0
        return None, None, None, None, (
            f"Not enough data to train a reliable regression model — need at least "
            f"{MIN_ROWS_FOR_TRAINING} students in the current filter "
            f"(currently {n})."
        )

    if "Final_Marks" not in df.columns:
        return None, None, None, None, "Final_Marks column is missing from the dataset."

    subject_cols = _detect_subject_columns(df)
    feature_cols = []
    if "Internal_Marks" in df.columns:
        feature_cols.append("Internal_Marks")
    if "Attendance" in df.columns:
        feature_cols.append("Attendance")
    for col in subject_cols:
        if col != "Final_Marks" and col not in feature_cols:
            feature_cols.append(col)

    if not feature_cols:
        return None, None, None, None, "No usable predictor feature columns found in dataset."

    X = df[feature_cols].copy().fillna(df[feature_cols].median(numeric_only=True))
    y = df["Final_Marks"].copy().fillna(df["Final_Marks"].median())

    if y.nunique() <= 1:
        return None, None, None, None, (
            "Cannot train regression model — all students in the current filter "
            "have identical Final_Marks values."
        )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    n_samples = len(df)
    cv_folds = 5 if n_samples >= 30 else max(3, min(5, n_samples // 5))
    try:
        cv_r2 = cross_val_score(
            RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            X, y,
            cv=cv_folds,
            scoring="r2",
        )
        r2_val = float(np.mean(cv_r2))
    except Exception:
        r2_val = float(r2_score(y, model.predict(X)))

    y_pred_all = model.predict(X)
    mae_val = float(mean_absolute_error(y, y_pred_all))
    rmse_val = float(root_mean_squared_error(y, y_pred_all))

    fi_df = (
        pd.DataFrame({"Feature": feature_cols, "Importance": model.feature_importances_})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )
    fi_df.attrs["r2_score"] = r2_val
    fi_df.attrs["mae"] = mae_val
    fi_df.attrs["rmse"] = rmse_val
    fi_df.attrs["n_features"] = len(feature_cols)
    fi_df.attrs["n_students"] = len(df)
    fi_df.attrs["cv_folds"] = cv_folds
    fi_df.attrs["feature_cols"] = feature_cols

    pred_df = df.copy()
    pred_df["Actual_Final_Marks"] = pred_df["Final_Marks"].round(1)
    pred_df["Predicted_Final_Marks"] = y_pred_all.round(1)
    pred_df["Residual"] = (pred_df["Actual_Final_Marks"] - pred_df["Predicted_Final_Marks"]).round(1)

    display_cols = [
        c for c in
        ["Student_ID", "Name", "Department", "Semester",
         "Actual_Final_Marks", "Predicted_Final_Marks", "Residual"]
        if c in pred_df.columns
    ]
    predictions_df = (
        pred_df[display_cols]
        .sort_values("Student_ID")
        .reset_index(drop=True)
    )

    return model, r2_val, fi_df, predictions_df, None


# ─────────────────────────────────────────────────────────────────────────────
# 3. SEMESTER PERFORMANCE FORECASTING (TREND PROJECTION)
# ─────────────────────────────────────────────────────────────────────────────
def get_multi_semester_students(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify students in df who have 2 or more distinct numeric semester records.
    Checks Student_ID first, and falls back to Name if Student_ID is unique per row.
    Returns a DataFrame with Student_ID, Name, Department, and Semester_Count.
    """
    if df is None or df.empty or "Semester" not in df.columns:
        return pd.DataFrame(columns=["Student_ID", "Name", "Department", "Semester_Count"])

    temp = df.copy()

    def _parse_sem_num(sem_val) -> int:
        sem_str = str(sem_val)
        match = re.search(r"\d+", sem_str)
        if match:
            return int(match.group(0))
        return 1

    temp["Sem_Num"] = temp["Semester"].apply(_parse_sem_num)

    # Step 1: Check by Student_ID
    if "Student_ID" in temp.columns:
        temp["Student_ID_str"] = temp["Student_ID"].astype(str)
        counts_id = (
            temp.groupby("Student_ID_str")["Sem_Num"]
            .nunique()
            .reset_index(name="Semester_Count")
        )
        eligible_ids = counts_id[counts_id["Semester_Count"] >= 2]

        if not eligible_ids.empty:
            cols = [c for c in ["Student_ID", "Name", "Department"] if c in temp.columns]
            details = temp[temp["Student_ID_str"].isin(eligible_ids["Student_ID_str"])][cols].drop_duplicates("Student_ID")
            result = pd.merge(
                details,
                eligible_ids.rename(columns={"Student_ID_str": "Student_ID"}),
                on="Student_ID",
            ).sort_values("Student_ID")
            return result.reset_index(drop=True)

    # Step 2: Fallback to Name if Student_ID is unique per row
    if "Name" in temp.columns:
        temp["Name_str"] = temp["Name"].astype(str)
        counts_name = (
            temp.groupby("Name_str")["Sem_Num"]
            .nunique()
            .reset_index(name="Semester_Count")
        )
        eligible_names = counts_name[counts_name["Semester_Count"] >= 2]

        if not eligible_names.empty:
            cols = [c for c in ["Student_ID", "Name", "Department"] if c in temp.columns]
            details = temp[temp["Name_str"].isin(eligible_names["Name_str"])][cols].drop_duplicates("Name")
            result = pd.merge(
                details,
                eligible_names.rename(columns={"Name_str": "Name"}),
                on="Name",
            ).sort_values("Name")
            return result.reset_index(drop=True)

    return pd.DataFrame(columns=["Student_ID", "Name", "Department", "Semester_Count"])


def forecast_next_semester(df: pd.DataFrame, student_identifier: str) -> tuple:
    """
    Fit a LinearRegression on a student's historical semester averages to project
    their next semester average marks. Can match by Student_ID or Name.

    Returns: (historical_df, forecast_dict, error_msg)
    """
    if df is None or df.empty:
        return None, None, "No data available."

    student_str = str(student_identifier).strip()

    # Match by Student_ID first, fallback to Name
    student_rows = df[df["Student_ID"].astype(str) == student_str].copy()
    if student_rows.empty and "Name" in df.columns:
        student_rows = df[df["Name"].astype(str) == student_str].copy()

    if student_rows.empty:
        return None, None, f"No records found for Student identifier '{student_str}'."

    if "Avg_Marks" not in student_rows.columns:
        subj_cols = _detect_subject_columns(student_rows)
        if subj_cols:
            student_rows["Avg_Marks"] = student_rows[subj_cols].mean(axis=1)
        else:
            student_rows["Avg_Marks"] = 0.0

    def _parse_sem_num(sem_val) -> int:
        sem_str = str(sem_val)
        match = re.search(r"\d+", sem_str)
        if match:
            return int(match.group(0))
        return 1

    student_rows["Sem_Num"] = student_rows["Semester"].apply(_parse_sem_num)

    sem_history = (
        student_rows.groupby("Sem_Num")
        .agg({"Semester": "first", "Avg_Marks": "mean"})
        .reset_index()
        .sort_values("Sem_Num")
        .reset_index(drop=True)
    )

    n_points = len(sem_history)
    if n_points < 2:
        return None, None, (
            f"Student {student_str} only has {n_points} semester record. "
            "At least 2 historical semesters are required to project a trend line."
        )

    X = sem_history[["Sem_Num"]].values
    y = sem_history["Avg_Marks"].values

    model = LinearRegression()
    model.fit(X, y)

    last_sem_num = int(X[-1][0])
    next_sem_num = last_sem_num + 1
    raw_pred = float(model.predict([[next_sem_num]])[0])
    forecasted_marks = float(np.clip(raw_pred, 0.0, 100.0))

    slope = float(model.coef_[0])

    if n_points == 2:
        caveat = (
            "Note: Forecast is based on only 2 semester data points. "
            "Linear trends with minimal history are illustrative and less reliable."
        )
    elif n_points == 3:
        caveat = (
            "Note: Forecast is based on 3 semesters of data. "
            "Trend projections refine as more semester data becomes available."
        )
    else:
        caveat = (
            f"Note: Forecast is based on {n_points} historical semesters. "
            "Illustrative trend line projection based on linear regression."
        )

    forecast_dict = {
        "student_id": str(student_rows["Student_ID"].iloc[0]) if "Student_ID" in student_rows.columns else student_str,
        "student_name": student_rows["Name"].iloc[0] if "Name" in student_rows.columns else student_str,
        "n_history": n_points,
        "last_sem_num": last_sem_num,
        "next_sem_num": next_sem_num,
        "next_sem_name": f"Semester {next_sem_num}",
        "forecasted_marks": round(forecasted_marks, 1),
        "slope": round(slope, 2),
        "caveat": caveat,
    }

    return sem_history, forecast_dict, None


# ─────────────────────────────────────────────────────────────────────────────
# 4. UNSUPERVISED STUDENT SEGMENTATION (K-MEANS CLUSTERING)
# ─────────────────────────────────────────────────────────────────────────────
def segment_students(df: pd.DataFrame, n_clusters: int = 4) -> tuple:
    """
    Perform unsupervised KMeans clustering on students based on Attendance
    and Average Marks. Auto-labels clusters dynamically based on centroid positions.

    Returns: (clustered_df, cluster_summary_df, silhouette_val, error_msg)
    """
    if df is None or df.empty or len(df) < 8:
        n = len(df) if df is not None else 0
        return None, None, None, (
            f"Not enough student data to cluster meaningfully — need at least 8 "
            f"students in the current filter (currently {n})."
        )

    temp_df = df.copy()

    if "Avg_Marks" not in temp_df.columns:
        subj_cols = _detect_subject_columns(temp_df)
        if subj_cols:
            temp_df["Avg_Marks"] = temp_df[subj_cols].mean(axis=1).round(2)
        else:
            return None, None, None, "No subject mark columns found for clustering."

    if "Attendance" not in temp_df.columns:
        return None, None, None, "Attendance column is missing from dataset."

    n_students = len(temp_df)
    target_k = max(2, min(n_clusters, n_students // 4))

    X_raw = temp_df[["Attendance", "Avg_Marks"]].copy().fillna(temp_df[["Attendance", "Avg_Marks"]].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    kmeans = KMeans(n_clusters=target_k, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(X_scaled)
    temp_df["Cluster_ID"] = cluster_ids

    try:
        if n_students > target_k and target_k >= 2:
            sil_val = float(silhouette_score(X_scaled, cluster_ids))
        else:
            sil_val = 0.0
    except Exception:
        sil_val = 0.0

    overall_med_att = float(X_raw["Attendance"].median())
    overall_med_marks = float(X_raw["Avg_Marks"].median())

    cluster_stats = []
    for cid in range(target_k):
        c_mask = (temp_df["Cluster_ID"] == cid)
        c_rows = temp_df[c_mask]
        c_count = len(c_rows)
        c_mean_att = float(c_rows["Attendance"].mean()) if c_count > 0 else 0.0
        c_mean_marks = float(c_rows["Avg_Marks"].mean()) if c_count > 0 else 0.0

        cluster_stats.append({
            "Cluster_ID": cid,
            "Count": c_count,
            "Mean_Attendance": round(c_mean_att, 1),
            "Mean_Avg_Marks": round(c_mean_marks, 1),
        })

    cluster_stats.sort(key=lambda s: (s["Mean_Avg_Marks"], s["Mean_Attendance"]), reverse=True)

    quadrant_counts = {}
    for stat in cluster_stats:
        att = stat["Mean_Attendance"]
        marks = stat["Mean_Avg_Marks"]

        high_marks = (marks >= overall_med_marks)
        high_att = (att >= overall_med_att)

        if high_marks and high_att:
            base_label = "High Performers"
            base_desc = "Strong academic performance paired with high class attendance."
        elif high_marks and not high_att:
            base_label = "Capable but Inconsistent"
            base_desc = "High academic potential despite lower attendance records."
        elif not high_marks and high_att:
            base_label = "Struggling Despite Effort"
            base_desc = "Good attendance records but struggling with subject marks; needs academic tutoring."
        else:
            base_label = "At-Risk / Attendance Strugglers"
            base_desc = "Low academic scores combined with low attendance; requires immediate intervention."

        quadrant_counts[base_label] = quadrant_counts.get(base_label, 0) + 1
        cnt = quadrant_counts[base_label]

        if cnt == 1:
            label = base_label
        elif cnt == 2:
            label = f"{base_label} (Moderate)"
        else:
            label = f"{base_label} (Group {cnt})"

        stat["Cluster_Label"] = label
        stat["Description"] = base_desc

    label_map = {s["Cluster_ID"]: s["Cluster_Label"] for s in cluster_stats}
    temp_df["Cluster_Label"] = temp_df["Cluster_ID"].map(label_map)

    summary_df = pd.DataFrame(cluster_stats)[[
        "Cluster_ID", "Cluster_Label", "Count",
        "Mean_Attendance", "Mean_Avg_Marks", "Description"
    ]].reset_index(drop=True)

    summary_df.attrs["silhouette_score"] = round(sil_val, 3)
    summary_df.attrs["n_clusters_used"] = target_k
    summary_df.attrs["n_students"] = n_students

    display_cols = [
        c for c in
        ["Student_ID", "Name", "Department", "Semester", "Attendance", "Avg_Marks", "Cluster_Label"]
        if c in temp_df.columns
    ]
    clustered_df = temp_df[display_cols].sort_values("Student_ID").reset_index(drop=True)

    return clustered_df, summary_df, sil_val, None
