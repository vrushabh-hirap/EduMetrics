"""
utils/data_cleaning.py
----------------------
Handles all data ingestion, validation, and cleaning for EduMetrics.
Keeps app.py clean by centralising every pre-processing step here.
"""

import pandas as pd
import numpy as np

# Columns that MUST be present for the app to function correctly
REQUIRED_COLUMNS = [
    "Student_ID", "Name", "Department", "Semester",
    "Maths", "Programming", "Database", "AI_ML",
    "Attendance", "Internal_Marks", "Final_Marks",
]

# Subject mark columns (used in numeric validation and grade computation)
SUBJECT_COLUMNS = ["Maths", "Programming", "Database", "AI_ML"]

# All numeric columns (marks must stay within 0–100)
NUMERIC_COLUMNS = SUBJECT_COLUMNS + ["Attendance", "Internal_Marks", "Final_Marks"]


def load_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check that the uploaded / loaded DataFrame contains all required columns.
    Raises a ValueError with a human-readable message if any are missing so
    the caller (app.py) can surface a friendly st.error instead of a traceback.
    """
    if df.empty:
        raise ValueError("The uploaded file is empty. Please provide a non-empty CSV.")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"The dataset is missing required column(s): {', '.join(missing)}. "
            "Please check your file and re-upload."
        )
    return df


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Full cleaning pipeline. Returns (cleaned_df, quality_report_dict).

    Steps performed (in order):
      1. Strip leading/trailing whitespace from string columns.
      2. Normalise text casing for Department and Semester (title-case).
      3. Coerce numeric columns to numeric type; non-parseable values → NaN.
      4. Clamp mark/attendance values to the valid 0–100 range.
      5. Drop rows where Student_ID or Name is null (identity columns).
      6. Impute remaining numeric NaNs with the column median.
      7. Remove exact duplicate rows (keep first occurrence).
    """
    original_count = len(df)
    report = {
        "original_rows": original_count,
        "duplicates_removed": 0,
        "nulls_imputed": {},       # {column: count_of_imputed_values}
        "out_of_range_clamped": {},  # {column: count_of_clamped_values}
        "identity_rows_dropped": 0,
    }

    df = df.copy()

    # --- Step 1 & 2: Strip whitespace and normalise text casing ---
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    for col in ["Department", "Semester"]:
        if col in df.columns:
            # Replace placeholder "nan" strings (artefact of .astype(str) above)
            df[col] = df[col].replace("nan", np.nan)
            df[col] = df[col].str.title()

    # --- Step 3: Coerce numeric columns ---
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            original_non_null = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # Count values that could not be parsed (became NaN after coercion)
            new_nulls = original_non_null - df[col].notna().sum()
            if new_nulls > 0:
                # Track separately; they will be imputed in step 6
                report["nulls_imputed"].setdefault(col, 0)
                report["nulls_imputed"][col] += int(new_nulls)

    # --- Step 4: Clamp values to [0, 100] ---
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            # Count values outside the valid range before clamping
            out_of_range = ((df[col] < 0) | (df[col] > 100)).sum()
            if out_of_range > 0:
                report["out_of_range_clamped"][col] = int(out_of_range)
            df[col] = df[col].clip(lower=0, upper=100)

    # --- Step 5: Drop rows with null identity columns ---
    identity_mask = df["Student_ID"].isna() | (df["Student_ID"] == "nan") | \
                    df["Name"].isna() | (df["Name"] == "nan")
    dropped = int(identity_mask.sum())
    report["identity_rows_dropped"] = dropped
    df = df[~identity_mask].reset_index(drop=True)

    # --- Step 6: Impute remaining numeric NaNs with column median ---
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            null_count = int(df[col].isna().sum())
            if null_count > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                # Accumulate (some may have been added above in step 3)
                report["nulls_imputed"][col] = report["nulls_imputed"].get(col, 0) + null_count

    # --- Step 7: Remove duplicate rows ---
    before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    report["duplicates_removed"] = before_dedup - len(df)

    report["cleaned_rows"] = len(df)
    return df, report


def quality_report_text(report: dict) -> str:
    """
    Convert the quality report dict into a human-readable markdown string
    that can be rendered inside a Streamlit expander.
    """
    lines = [
        f"- **Original rows:** {report['original_rows']}",
        f"- **Rows after cleaning:** {report['cleaned_rows']}",
        f"- **Duplicate rows removed:** {report['duplicates_removed']}",
        f"- **Identity rows dropped (null ID/Name):** {report['identity_rows_dropped']}",
    ]

    if report["nulls_imputed"]:
        lines.append("- **Missing values imputed (median strategy):**")
        for col, cnt in report["nulls_imputed"].items():
            lines.append(f"  - {col}: {cnt} value(s)")
    else:
        lines.append("- **Missing values imputed:** None")

    if report["out_of_range_clamped"]:
        lines.append("- **Out-of-range values clamped to [0, 100]:**")
        for col, cnt in report["out_of_range_clamped"].items():
            lines.append(f"  - {col}: {cnt} value(s)")
    else:
        lines.append("- **Out-of-range values clamped:** None")

    return "\n".join(lines)


import io


def load_sample(filepath: str = "data/sample_students.csv") -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load sample CSV dataset from disk and run validation and cleaning."""
    raw = pd.read_csv(filepath)
    val = load_and_validate(raw)
    cleaned, report = clean_data(val)
    from utils.analytics import compute_grades
    cleaned = compute_grades(cleaned)
    return raw, cleaned, report


def load_uploaded(file_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Parse uploaded CSV bytes and run validation and cleaning."""
    raw = pd.read_csv(io.BytesIO(file_bytes))
    val = load_and_validate(raw)
    cleaned, report = clean_data(val)
    from utils.analytics import compute_grades
    cleaned = compute_grades(cleaned)
    return raw, cleaned, report



def process_multiple_files(files: list) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Process and combine multiple uploaded CSV files into a unified dataset.
    Attaches a 'Source_File' column to track origin (e.g., Division_A.csv).
    
    Returns: (combined_raw_df, combined_cleaned_df, combined_quality_report)
    """
    if not files:
        raise ValueError("No files provided.")

    raw_dfs = []
    cleaned_dfs = []
    
    total_original = 0
    total_cleaned = 0
    total_dedup = 0
    total_dropped = 0
    nulls_acc = {}
    clamped_acc = {}
    file_names = []

    for idx, f in enumerate(files):
        # Determine filename
        if hasattr(f, "name"):
            filename = f.name
            content = f.getvalue()
        elif isinstance(f, tuple) and len(f) == 2:
            filename, content = f
        else:
            filename = f"File_{idx+1}.csv"
            content = f

        clean_filename = filename.rsplit(".", 1)[0].replace("_", " ").title() if "." in filename else filename
        file_names.append(filename)

        # Parse raw CSV bytes
        try:
            if isinstance(content, bytes):
                raw = pd.read_csv(io.BytesIO(content))
            else:
                raw = pd.read_csv(content)
        except Exception as exc:
            raise ValueError(f"Error parsing '{filename}': {exc}")

        # Validate required columns
        validated = load_and_validate(raw)
        validated["Source_File"] = filename
        raw["Source_File"] = filename
        raw_dfs.append(raw)

        # Clean individual dataset
        cleaned, rpt = clean_data(validated)
        cleaned["Source_File"] = filename
        cleaned_dfs.append(cleaned)

        # Aggregate report stats
        total_original += rpt.get("original_rows", 0)
        total_cleaned += rpt.get("cleaned_rows", 0)
        total_dedup += rpt.get("duplicates_removed", 0)
        total_dropped += rpt.get("identity_rows_dropped", 0)

        for col, cnt in rpt.get("nulls_imputed", {}).items():
            nulls_acc[col] = nulls_acc.get(col, 0) + cnt
        for col, cnt in rpt.get("out_of_range_clamped", {}).items():
            clamped_acc[col] = clamped_acc.get(col, 0) + cnt

    # Combine into unified DataFrames
    combined_raw = pd.concat(raw_dfs, ignore_index=True)
    combined_cleaned = pd.concat(cleaned_dfs, ignore_index=True)

    # Re-enrich grade & avg marks for combined dataset
    from utils.analytics import compute_grades
    combined_cleaned = compute_grades(combined_cleaned)

    combined_report = {
        "files_count": len(files),
        "file_names": file_names,
        "original_rows": total_original,
        "cleaned_rows": len(combined_cleaned),
        "duplicates_removed": total_dedup,
        "identity_rows_dropped": total_dropped,
        "nulls_imputed": nulls_acc,
        "out_of_range_clamped": clamped_acc,
    }

    return combined_raw, combined_cleaned, combined_report
