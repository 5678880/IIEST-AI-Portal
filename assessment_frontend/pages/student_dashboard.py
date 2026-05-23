import streamlit as st
import pandas as pd

from components.auth import require_login
from services.api_client import (
    add_student_subject,
    fetch_student_subjects,
    fetch_subject_catalog,
    fetch_my_results
)

from components.sidebar import (
    show_sidebar
)

# ===================================
# PAGE CONFIG
# ===================================

st.set_page_config(

    page_title="Student Dashboard",

    layout="wide"
)

# ===================================
# LOGIN CHECK
# ===================================

require_login()

# ===================================
# ROLE CHECK
# ===================================

user = st.session_state.get(
    "user",
    {}
)

if user.get("role") not in ["student", "teacher"]:

    st.error(
        "Student Or Teacher Access Only"
    )

    st.stop()

# ===================================
# SIDEBAR
# ===================================

show_sidebar()

# ===================================
# TITLE
# ===================================

st.title(
    "Student Performance Dashboard"
)

st.markdown("""

Track your exam performance, analyze
your strengths and weaknesses, and
receive AI-generated study suggestions.

""")

st.divider()

st.subheader(
    "My Subject Enrollments"
)

subject_catalog = fetch_subject_catalog()
student_subjects = fetch_student_subjects(
    st.session_state.token
)

if subject_catalog:
    catalog_lookup = {
        item["subject"]: item
        for item in subject_catalog
    }

    with st.form("student_subject_enrollment_form"):
        name_col, roll_col = st.columns(2)
        with name_col:
            enrollment_name = st.text_input(
                "Student full name",
                value=user.get("name", "")
            )
        with roll_col:
            roll_no = st.text_input(
                "Roll number",
                placeholder="Example: CSE/23/045"
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            selected_subject = st.selectbox(
                "Subject",
                list(catalog_lookup.keys())
            )

        selected_catalog = catalog_lookup[selected_subject]

        with col2:
            semester = st.selectbox(
                "Semester",
                sorted(
                    {
                        item["semester"]
                        for item in subject_catalog
                    }
                ),
                index=sorted(
                    {
                        item["semester"]
                        for item in subject_catalog
                    }
                ).index(selected_catalog["semester"])
            )

        with col3:
            section = st.text_input(
                "Class / Section",
                value="CSE-A"
            )

        with col4:
            academic_year = st.text_input(
                "Academic Year",
                value="2026"
            )

        submitted = st.form_submit_button(
            "Enroll In Subject",
            type="primary"
        )

        if submitted:
            result = add_student_subject(
                {
                    "student_name": enrollment_name,
                    "roll_no": roll_no,
                    "subject": selected_subject,
                    "subject_code": selected_catalog["subject_code"],
                    "semester": semester,
                    "section": section,
                    "academic_year": academic_year
                },
                st.session_state.token
            )

            if result.get("error"):
                st.error(result["error"])
            else:
                st.success(
                    f"Enrolled in {selected_subject} ({selected_catalog['subject_code']})."
                )
                st.rerun()

if student_subjects:
    st.dataframe(
        pd.DataFrame(student_subjects),
        use_container_width=True
    )
else:
    st.info(
        "Enroll in your current semester subjects here. Teachers will then see you in their subject rosters."
    )

st.divider()

# ===================================
# FETCH RESULTS
# ===================================

results = fetch_my_results(

    st.session_state.token
)

# ===================================
# EMPTY RESULTS
# ===================================

if not results:

    st.info(
        "No exam results available yet."
    )

    st.stop()

# ===================================
# DATAFRAME
# ===================================

df = pd.DataFrame(results)

# ===================================
# METRICS
# ===================================

average_percentage = round(

    df["percentage"].mean(),

    2
)

highest_score = round(

    df["percentage"].max(),

    2
)

lowest_score = round(

    df["percentage"].min(),

    2
)

total_exams = len(df)

# ===================================
# METRIC CARDS
# ===================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Exams",
        total_exams
    )

with col2:

    st.metric(
        "Average Score",
        f"{average_percentage}%"
    )

with col3:

    st.metric(
        "Highest Score",
        f"{highest_score}%"
    )

with col4:

    st.metric(
        "Lowest Score",
        f"{lowest_score}%"
    )

# ===================================
# PERFORMANCE TREND
# ===================================

st.divider()

st.subheader(
    "Performance Trend"
)

chart_data = df[
    "percentage"
]

st.line_chart(
    chart_data
)

# ===================================
# RESULTS TABLE
# ===================================

st.divider()

st.subheader(
    "Exam Results"
)

st.dataframe(

    df,

    use_container_width=True
)

# ===================================
# AI FEEDBACK
# ===================================

st.divider()

st.subheader(
    "AI Performance Suggestions"
)

feedbacks = df["ai_feedback"].dropna()

if len(feedbacks) == 0:

    st.info(
        "No AI suggestions available yet."
    )

else:

    for feedback in feedbacks:

        st.success(
            feedback
        )
