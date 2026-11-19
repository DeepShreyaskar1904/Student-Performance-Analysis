# Student Performance Analysis Dashboard

A beginner-friendly Data Science project using a synthetic dataset and Streamlit.

## Files
- `student_performance.csv`: 500 synthetic student records.
- `app.py`: Streamlit dashboard.
- `requirements.txt`: Python dependencies.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

## Dataset notes
The dataset is synthetic and generated for learning. It is not real student data.
The dashboard calculates total marks and average marks from four subjects.
A student passes if they score at least 35 in every subject.

## Data Science workflow
1. Load data with Pandas.
2. Inspect shape, columns, types and summary statistics.
3. Check missing values and clean invalid rows.
4. Create derived columns (total, average, performance, result).
5. Filter and group records.
6. Explore distributions and subject averages.
7. Use scatter plots and correlation to study associations.
8. Communicate findings in the dashboard.

## Statistical concepts
- Mean: average value.
- Median: middle value.
- Standard deviation: spread of values.
- Percentages: pass rate and category distribution.
- Correlation: strength and direction of a linear association.

No machine-learning model is used in this project.
