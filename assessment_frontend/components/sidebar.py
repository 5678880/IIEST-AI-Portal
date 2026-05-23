import streamlit as st

from components.theme import apply_theme


def show_sidebar():
    apply_theme()

    st.sidebar.title("IIEST AI Portal")
    st.sidebar.caption("Student-Teacher Intelligence")

    st.sidebar.divider()

    if "user" in st.session_state:
        role = st.session_state.user["role"]

        if role == "teacher":
            st.sidebar.subheader("Teacher Command Center")
            st.sidebar.page_link("pages/teacher_portal.py", label="Teacher Portal")
            st.sidebar.page_link("pages/exam_builder.py", label="Exam Builder")
            st.sidebar.page_link("pages/class_tests.py", label="Class Tests")
            st.sidebar.page_link("pages/teacher_attendance.py", label="Attendance Intelligence")
            st.sidebar.page_link("pages/teacher_grading.py", label="AI Grading Center")
            st.sidebar.page_link("pages/teacher_analytics.py", label="Analytics Dashboard")

            st.sidebar.divider()
            st.sidebar.subheader("Student Portal Preview")
            st.sidebar.page_link("pages/live_exam.py", label="Live Exam")
            st.sidebar.page_link("pages/student_dashboard.py", label="Student Dashboard")
            st.sidebar.page_link("pages/student_ai_assistant.py", label="AI Study Assistant")
            st.sidebar.page_link("pages/student_papers.py", label="Papers")
            st.sidebar.page_link("pages/weak_subjects.py", label="Revise Weak Subjects")
            st.sidebar.page_link("pages/learning_resources.py", label="Learning Resources")

        elif role == "student":
            st.sidebar.subheader("Student Menu")
            st.sidebar.page_link("pages/live_exam.py", label="Live Exam")
            st.sidebar.page_link("pages/student_dashboard.py", label="My Dashboard")
            st.sidebar.page_link("pages/student_ai_assistant.py", label="AI Study Assistant")
            st.sidebar.page_link("pages/student_papers.py", label="Papers")
            st.sidebar.page_link("pages/weak_subjects.py", label="Revise Weak Subjects")
            st.sidebar.page_link("pages/learning_resources.py", label="Learning Resources")

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div style="background: rgba(37,99,235,0.16); border: 1px solid rgba(147,197,253,0.24);
                    padding: 14px; border-radius: 16px; font-size: 13px; color: #dbeafe;">
            AI highlights teacher workload, learning risk, grading gaps, attendance patterns,
            and student revision needs.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.divider()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.caption("FastAPI • Streamlit • Ollama • Llama3")
