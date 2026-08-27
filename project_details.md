# EduMetrics — Student Performance Analytics Dashboard

## Technology Stack
- Python
- Streamlit
- Pandas
- NumPy
- Plotly / Matplotlib

## Objective
Build an interactive web application that analyzes student academic data and converts raw marks, attendance, and subject information into useful visual insights.

---

## Main Features

### 1. CSV Dataset Upload
- Users can upload their own student dataset (`.csv`).
- Provide a sample/demo dataset option if no file is uploaded, so the app is usable out of the box.

### 2. Data Cleaning
- Handle missing values (impute or drop, with a visible strategy).
- Remove duplicate records.
- Fix inconsistent data (e.g., inconsistent casing in Department/Semester, stray whitespace, invalid marks outside 0–100 range).
- Show a short "data quality report" summarizing what was cleaned.

### 3. Performance Overview (KPI Metrics)
Display at a glance:
- Average marks
- Average attendance
- Pass percentage
- Number of students
- Highest performer
- Lowest performer

### 4. Interactive Filters (Sidebar)
Allow filtering students by:
- Department
- Semester
- Subject
- Attendance range (slider)
- Marks range (slider)

All downstream KPIs, charts, and tables should react to the active filters.

### 5. Visual Analytics
- Subject-wise average marks (bar chart)
- Attendance vs marks (scatter plot, to explore correlation)
- Grade distribution (histogram/pie chart based on computed grades)
- Semester-wise performance (bar/line chart)
- Top-performing students (ranked table/bar chart)

### 6. At-Risk Student Detection
- Flag students with low marks and/or poor attendance based on configurable thresholds (e.g., marks < 40, attendance < 75%).
- Display a dedicated table/section listing at-risk students with the reason(s) they were flagged.

### 7. Student Details View
- Let the user select an individual student (by ID or Name).
- Show a full academic profile: all subject marks, attendance, internal/final marks, computed grade, and risk status.

### 8. Download Reports
- Export the currently filtered dataset as CSV.
- Optionally export a summary analysis (KPIs + at-risk list) as CSV.

---

## Suggested Dataset Columns
| Column | Description |
|---|---|
| Student_ID | Unique identifier |
| Name | Student name |
| Department | Department/branch |
| Semester | Current semester |
| Maths | Subject marks |
| Programming | Subject marks |
| Database | Subject marks |
| AI_ML | Subject marks |
| Attendance | Attendance percentage |
| Internal_Marks | Internal assessment marks |
| Final_Marks | Final exam marks |

---

## Application Structure

```
app.py
│
├── Dataset Upload
├── Data Cleaning
├── Sidebar Filters
├── KPI Metrics
├── Performance Analysis
├── Interactive Charts
├── At-Risk Student Analysis
└── Download Reports
```

Recommended implementation approach:
- Keep `app.py` as the entry point/orchestrator.
- Split logic into modules for maintainability, e.g.:
  - `utils/data_cleaning.py`
  - `utils/analytics.py`
  - `utils/charts.py`
  - `utils/risk_detection.py`
- Use `st.cache_data` for expensive data operations (loading/cleaning) to keep the app responsive.
- Use `st.session_state` where needed to persist filter state and uploaded data across reruns.

---

## Intermediate-Level Concepts Demonstrated
1. Streamlit UI development
2. Pandas data manipulation
3. Data preprocessing
4. Statistical analysis
5. Interactive data visualization
6. Filtering and user inputs
7. Conditional logic
8. CSV file handling
9. Basic academic risk analysis
10. Dashboard design and deployment

## Why This Is Intermediate-Level
It goes beyond a simple Streamlit calculator or static visualization because it combines file handling + preprocessing + analytics + interactive filtering + multiple visualizations + automated insights + downloadable results into one cohesive application.

---

## Possible Future Improvements
- Add ML-based prediction of student performance.
- Predict whether a student is at risk of failing (classification model).
- Add login/authentication for teachers and students.
- Store data using SQLite/PostgreSQL instead of in-memory CSV handling.
- Generate automated PDF performance reports.
- Deploy the application using Streamlit Community Cloud.

---

## Acceptance Criteria (for the build)
- [ ] App runs with `streamlit run app.py` without errors on a fresh environment.
- [ ] Uploading a CSV with the suggested columns works end-to-end.
- [ ] A sample dataset is bundled so the app works without any upload.
- [ ] All filters correctly narrow down KPIs, charts, and tables.
- [ ] At-risk thresholds are configurable via the sidebar (not hardcoded only).
- [ ] Charts are interactive (Plotly preferred) and readable on both light/dark Streamlit themes.
- [ ] Download buttons produce valid, correctly filtered CSV files.
- [ ] Code is modular, commented, and free of unhandled exceptions on malformed input (e.g., missing columns, empty file).