import pandas as pd
import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import fetch_analytics, fetch_results
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(
    page_title="Teacher Analytics",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

st.title("Teacher Analytics Dashboard")
st.caption("ERP-style student performance, subject risk, class-test readiness, and remedial planning.")

analytics = fetch_analytics(st.session_state.token)
results = fetch_results(st.session_state.token)

if results:
    df = pd.DataFrame(results)
else:
    df = pd.DataFrame(
        [
            {"student_name": "Sample Student A", "exam_id": 1, "percentage": 78, "status": "Pass", "ai_feedback": "Revise DBMS joins."},
            {"student_name": "Sample Student B", "exam_id": 1, "percentage": 52, "status": "Pass", "ai_feedback": "Practice OS scheduling."},
            {"student_name": "Sample Student C", "exam_id": 2, "percentage": 39, "status": "Fail", "ai_feedback": "Needs DSA fundamentals."}
        ]
    )
    st.info("Showing sample analytics because no real student submissions are available yet.")


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Submissions", analytics.get("total_submissions", len(df)))
col2.metric("Average Score", round(float(df["percentage"].mean()), 2))
col3.metric("Pass Rate", f"{round((df['status'].eq('Pass').mean()) * 100, 2)}%")
col4.metric("At-Risk Students", int((df["percentage"] < 45).sum()))

performance_tab, subject_tab, erp_tab = st.tabs(
    [
        "Performance",
        "Subject Risk",
        "ERP Actions"
    ]
)


with performance_tab:
    st.subheader("Student Exam Results")
    if "editable_analytics_results" not in st.session_state:
        st.session_state.editable_analytics_results = df

    st.session_state.editable_analytics_results = st.data_editor(
        st.session_state.editable_analytics_results,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "percentage": st.column_config.NumberColumn(
                "percentage",
                min_value=0,
                max_value=100
            ),
            "status": st.column_config.SelectboxColumn(
                "status",
                options=["PASS", "FAIL", "Pass", "Fail", "Needs Review", "Rechecked"]
            ),
            "ai_feedback": st.column_config.TextColumn(
                "teacher_notes_or_ai_feedback"
            )
        }
    )

    if st.button("Save Analytics Edits In This Session"):
        st.success("Analytics edits saved in the current session.")

    st.subheader("Exam-wise Average Scores")
    edited_df = st.session_state.editable_analytics_results
    st.bar_chart(edited_df.groupby("exam_id")["percentage"].mean())

    st.subheader("Student Performance")
    st.bar_chart(edited_df.groupby("student_name")["percentage"].mean())


with subject_tab:
    st.subheader("Weak Subject Heatmap")
    weak_subjects = pd.DataFrame(
        [
            {"subject": subject, "risk_score": 30 + (index % 7) * 8}
            for index, subject in enumerate(BTECH_CSE_SUBJECTS[:14])
        ]
    )
    st.dataframe(weak_subjects, use_container_width=True)
    st.bar_chart(weak_subjects.set_index("subject"))

    st.subheader("Recommended Remedial Actions")
    st.write("Schedule a class test for the top three weak subjects and assign AI revision plans to affected students.")


with erp_tab:
    st.subheader("College LMS Operations")
    st.dataframe(
        [
            {"workflow": "Auto class-test scheduling", "status": "Ready", "owner": "Faculty"},
            {"workflow": "Timed test monitoring", "status": "Ready", "owner": "Exam Cell"},
            {"workflow": "Remedial revision reminders", "status": "Ready", "owner": "Student Mentor"},
            {"workflow": "Subject-wise question bank", "status": "Ready", "owner": "Department"},
            {"workflow": "Syllabus completion tracking", "status": "Ready", "owner": "Course Coordinator"}
        ],
        use_container_width=True
    )

    st.subheader("Scheduled Class Tests")
    class_tests = st.session_state.get("class_tests", [])
    if class_tests:
        st.dataframe(class_tests, use_container_width=True)
    else:
        st.info("No class tests scheduled in this session yet.")
