import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Student Performance Dashboard", page_icon="🎓", layout="wide")

st.title("🎓 Student Performance Analysis")
st.caption("Explore academic results, attendance, study habits and subject-wise performance.")

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_csv("student_performance.csv")
    return data

st.sidebar.header("Dashboard filters")
uploaded_file = st.sidebar.file_uploader("Upload your own CSV (optional)", type=["csv"])

try:
    df = load_data(uploaded_file)
except FileNotFoundError:
    st.error("student_performance.csv was not found. Keep it in the same folder as app.py.")
    st.stop()
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

required_columns = [
    "Student_ID", "Gender", "Study_Hours", "Attendance", "Sleep_Hours",
    "Math_Score", "Science_Score", "English_Score", "Computer_Score"
]
missing = [col for col in required_columns if col not in df.columns]
if missing:
    st.error("The CSV is missing required columns: " + ", ".join(missing))
    st.stop()

# Clean and calculate derived columns so uploaded files can use the same dashboard.
numeric_cols = ["Study_Hours", "Attendance", "Sleep_Hours",
                "Math_Score", "Science_Score", "English_Score", "Computer_Score"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=numeric_cols + ["Gender", "Student_ID"]).copy()
subject_cols = ["Math_Score", "Science_Score", "English_Score", "Computer_Score"]
df["Total_Marks"] = df[subject_cols].sum(axis=1)
df["Average_Marks"] = df[subject_cols].mean(axis=1)
df["Performance"] = pd.cut(
    df["Average_Marks"], bins=[-0.01, 39.99, 59.99, 79.99, 100],
    labels=["Needs Improvement", "Average", "Good", "Excellent"]
).astype(str)
df["Result"] = np.where((df[subject_cols] >= 35).all(axis=1), "Pass", "Fail")

gender_options = ["All"] + sorted(df["Gender"].astype(str).unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", gender_options)
min_attendance = st.sidebar.slider("Minimum attendance (%)", 0, 100, 0)
max_study = float(max(8, np.ceil(df["Study_Hours"].max())))
study_range = st.sidebar.slider("Study hours per day", 0.0, max_study, (0.0, max_study), step=0.5)

filtered = df.copy()
if selected_gender != "All":
    filtered = filtered[filtered["Gender"].astype(str) == selected_gender]
filtered = filtered[
    (filtered["Attendance"] >= min_attendance) &
    (filtered["Study_Hours"].between(study_range[0], study_range[1]))
]

if filtered.empty:
    st.warning("No students match these filters. Adjust the filters in the sidebar.")
    st.stop()

# KPI cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students analysed", f"{len(filtered):,}")
c2.metric("Average marks", f"{filtered['Average_Marks'].mean():.1f}/100")
c3.metric("Pass rate", f"{(filtered['Result'].eq('Pass').mean() * 100):.1f}%")
c4.metric("Average attendance", f"{filtered['Attendance'].mean():.1f}%")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Average marks by subject")
    subject_means = filtered[subject_cols].mean().rename({
        "Math_Score": "Math", "Science_Score": "Science",
        "English_Score": "English", "Computer_Score": "Computer"
    })
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(x=subject_means.index, y=subject_means.values, ax=ax)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average marks")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15)
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Performance category distribution")
    counts = filtered["Performance"].value_counts().reindex(
        ["Needs Improvement", "Average", "Good", "Excellent"], fill_value=0
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_ylabel("")
    st.pyplot(fig)
    plt.close(fig)

left, right = st.columns(2)
with left:
    st.subheader("Study hours vs average marks")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.regplot(data=filtered, x="Study_Hours", y="Average_Marks",
                scatter_kws={"alpha": 0.45}, line_kws={"color": "red"}, ax=ax)
    ax.set_xlabel("Study hours per day")
    ax.set_ylabel("Average marks")
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Attendance vs average marks")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=filtered, x="Attendance", y="Average_Marks",
                    hue="Result", alpha=0.7, ax=ax)
    ax.set_xlabel("Attendance (%)")
    ax.set_ylabel("Average marks")
    st.pyplot(fig)
    plt.close(fig)

st.divider()
st.subheader("Correlation between numeric variables")
corr_cols = ["Study_Hours", "Attendance", "Sleep_Hours"] + subject_cols + ["Average_Marks"]
fig, ax = plt.subplots(figsize=(11, 6))
sns.heatmap(filtered[corr_cols].corr(numeric_only=True), annot=True, fmt=".2f",
            cmap="coolwarm", center=0, ax=ax)
st.pyplot(fig)
plt.close(fig)

st.subheader("Student records")
show_only = st.checkbox("Show students who need improvement only")
table = filtered.copy()
if show_only:
    table = table[table["Performance"] == "Needs Improvement"]
st.dataframe(
    table[["Student_ID", "Gender", "Study_Hours", "Attendance"] + subject_cols +
          ["Average_Marks", "Performance", "Result"]].sort_values("Average_Marks"),
    use_container_width=True,
    hide_index=True
)

st.subheader("Key observations")
best_subject = filtered[subject_cols].mean().idxmax().replace("_Score", "")
lowest_subject = filtered[subject_cols].mean().idxmin().replace("_Score", "")
study_corr = filtered["Study_Hours"].corr(filtered["Average_Marks"])
attendance_corr = filtered["Attendance"].corr(filtered["Average_Marks"])
st.write(f"- **Highest average subject:** {best_subject}.")
st.write(f"- **Lowest average subject:** {lowest_subject}.")
st.write(f"- **Study hours and marks correlation:** {study_corr:.2f}.")
st.write(f"- **Attendance and marks correlation:** {attendance_corr:.2f}.")
st.caption("Correlation describes association, not proof that one factor causes another. "
           "Pass means scoring at least 35 in every listed subject.")
