# 🎓 EduMetrics — Academic Performance Analytics & Machine Learning Suite

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit_learn-1.4%2B-F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Developer](https://img.shields.io/badge/Developed%20By-Vrushabh%20Hirap-2563eb.svg?style=for-the-badge)](https://vrushabhhirap.vercel.app)

**EduMetrics** is an enterprise-grade academic performance intelligence platform built with Python, Streamlit, Scikit-Learn, and Plotly. It transforms raw student academic records (marks, attendance, internal assessments) into actionable administrative insights, predictive risk flags, ML-driven performance forecasts, and unsupervised behavioral segmentations.

---

## 🌟 Key Features & Modules

### 📁 1. Multi-CSV Dataset & Division Aggregation Engine
- **Multi-File Ingestion**: Drag & drop 10s or 100s of classroom CSV files at once (`Division_A.csv`, `Division_B.csv`, `Classroom_1.csv`...).
- **Automatic Origin Tracking**: Attaches a `Source_File` column to every student record, enabling seamless switching between single classroom analysis and college-wide aggregation.
- **Data Hygiene Pipeline**: Automated whitespace stripping, casing normalization, numeric type coercion, median missing value imputation, and out-of-range clamping (`[0, 100]`).

### 📊 2. Executive Overview & Filter Controls
- **KPI Metrics**: Real-time computation of total student count, class average marks, overall attendance, pass percentage, top performer, and lowest performer.
- **Multi-Dimensional Filters**: Filter dataset dynamically by Department, Semester, Source File/Division, Attendance Range, Average Marks Range, and Custom Risk Thresholds.

### 🔮 3. Machine Learning Suite

| ML Model | Algorithm / Technique | Purpose & Output |
| :--- | :--- | :--- |
| **At-Risk Risk Classifier** | `RandomForestClassifier(n_estimators=100, class_weight='balanced')` | Predicts student risk probability ($0-100\%$) based on subject marks and attendance patterns. Displays Feature Importance charts & Risk Level badges (`HIGH`, `MEDIUM`, `LOW`). |
| **Marks Regressor & Simulator** | `RandomForestRegressor(n_estimators=100)` | Predicts `Final_Marks` (strictly excluding target leakage). Includes $R^2$ cross-validation scoring, MAE, RMSE, Residual analysis, and an **Interactive What-If Scenario Simulator**. |
| **Student Segmentation** | `KMeans(n_clusters=K)` + `StandardScaler` | Groups students into $K$ behavioral clusters based on Attendance & Average Marks. Auto-labels clusters into tiers (`High Performers`, `At-Risk Low Attendance`, etc.) with Silhouette Scores and 2D Scatter Centroids. |
| **Semester Forecasting** | `LinearRegression` Time-Series Trajectory | Projects next semester average marks for multi-semester students based on historical trend slopes. |

### 🤖 4. Floating AI Chatbot Assistant (Powered by Google Gemini API)
- **Context-Aware Analytics Q&A**: Embedded floating AI widget that reads current dataset context, student rosters, subject averages, and risk summaries to answer natural language queries.
- **Failover & Key Rotation**: Implements round-robin API key rotation and automatic failover handling.

### 📤 5. Reports & Data Exporter
- Export filtered student subsets and complete executive summary reports to standard `.csv` files.

---

## 📂 Repository Architecture & Project Structure

```text
EduMetrics/
├── app.py                      # Main entry point & multi-page router with global CSS & filter panel
├── requirements.txt            # Python dependencies (Streamlit, Scikit-Learn, Pandas, Plotly, etc.)
├── README.md                   # Complete GitHub project documentation
├── project_details.md          # Project specification reference
├── .streamlit/
│   └── config.toml             # Custom light mode Streamlit theme configuration (#2563eb Royal Blue)
├── data/
│   ├── sample_students.csv                 # 200-student single semester sample dataset
│   └── sample_multi_semester_students.csv  # Multi-semester sample dataset for forecasting
├── pages/
│   ├── pg_overview.py          # Executive Overview, KPIs, Data Quality Report & Footer Credits
│   ├── pg_performance.py       # Subject performance analytics & department breakdowns
│   ├── pg_charts.py            # Visual Data Exploration (Scatter, Histogram, Box plot, Heatmaps)
│   ├── pg_at_risk.py           # Rule-based At-Risk student threshold table & summary
│   ├── pg_risk_prediction.py   # ML Risk Classifier & Feature Importance chart
│   ├── pg_marks_prediction.py  # ML Final Marks Regressor & What-If Scenario Simulator
│   ├── pg_student_segments.py  # ML KMeans Clustering & Cluster Profile Cards
│   ├── pg_semester_forecast.py # ML Time-Series Semester Performance Forecasting
│   ├── pg_student_lookup.py    # Individual Student Deep-Dive Search & Profile Cards
│   └── pg_reports.py          # CSV Report Exporter
└── utils/
    ├── analytics.py            # KPI calculation & grade computation logic
    ├── data_cleaning.py        # Ingestion, multi-CSV merger, validation & data cleaning
    ├── ml_models.py            # Machine Learning engine (Classification, Regression, Clustering, Forecasting)
    ├── risk_detection.py       # Threshold rule-based risk flagging logic
    ├── charts.py               # Plotly chart styling & figure generators
    ├── ai_chatbot.py           # Google Gemini API integration & prompt builder
    ├── ai_widget.py            # Floating CSS/HTML AI Assistant popover container
    ├── avatar_data.py          # SVG Chatbot assets
    └── icons.py                # Reusable SVG line icon library (Cap, Charts, Logo, etc.)
```

---

## 📋 Required CSV Data Schema

EduMetrics dynamically detects subject columns and requires the following header format:

| Column Name | Type | Description | Valid Range / Format |
| :--- | :--- | :--- | :--- |
| **`Student_ID`** | String | Unique identifier for each student | e.g. `S001`, `1001` |
| **`Name`** | String | Student full name | e.g. `Aarav Shah` |
| **`Department`** | String | Academic department | e.g. `CS`, `IT`, `ECE`, `Mech` |
| **`Semester`** | String | Current academic semester | e.g. `Semester 1`, `Semester 2` |
| **`Maths`** | Numeric | Subject mark | `0` to `100` |
| **`Programming`** | Numeric | Subject mark | `0` to `100` |
| **`Database`** | Numeric | Subject mark | `0` to `100` |
| **`AI_ML`** | Numeric | Subject mark | `0` to `100` |
| **`Attendance`** | Numeric | Student attendance percentage | `0` to `100` |
| **`Internal_Marks`** | Numeric | Continuous evaluation marks | `0` to `100` |
| **`Final_Marks`** | Numeric | Semester end exam marks | `0` to `100` |

---

## 🚀 Getting Started & Local Setup

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/vrushabhhirap/EduMetrics.git
cd EduMetrics
```

### 3. Create a Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Launch Application
```bash
streamlit run app.py
```

The application will open automatically in your browser at **`http://localhost:8502`**.

---

## 🛠️ Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Data Visualization**: [Plotly Express & Graph Objects](https://plotly.com/python/)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) (`RandomForestClassifier`, `RandomForestRegressor`, `KMeans`, `StandardScaler`, `cross_val_score`)
- **AI Intelligence**: Google Gemini API (`gemini-3.6-flash`)

---

## 🔒 Privacy & Data Security

EduMetrics operates under a **Strict Local-First Privacy Architecture**:
- All CSV datasets uploaded to EduMetrics are processed strictly **in-memory** within your browser session.
- Student names, marks, attendance, and identity records are **never saved to external databases or third-party servers**.
- Session memory is automatically cleared when the application tab is closed.

---

## 📜 License & Credits

Distributed under the **MIT License**. See `LICENSE` for more information.

### 👤 Developed By
**Vrushabh Hirap**  
🌐 **Portfolio Website**: [https://vrushabhhirap.vercel.app](https://vrushabhhirap.vercel.app)
