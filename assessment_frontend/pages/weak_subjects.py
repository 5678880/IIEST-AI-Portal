from datetime import date

import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import ask_ai_tutor
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(
    page_title="Revise Weak Subjects",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") not in ["student", "teacher"]:
    st.error("Student Or Teacher Access Only")
    st.stop()


show_sidebar()

st.title("Revise / Practice Weak Subjects")
st.caption("Choose the subjects you need help with and get a daily revision system.")

if "weak_subject_plan" not in st.session_state:
    st.session_state.weak_subject_plan = {}

selected_subjects = st.multiselect(
    "Select weak subjects",
    BTECH_CSE_SUBJECTS,
    default=list(st.session_state.weak_subject_plan.keys())
)

col1, col2, col3 = st.columns(3)

with col1:
    reminder_time = st.time_input("Daily reminder time")

with col2:
    session_length = st.slider("Study block minutes", 15, 90, 35)

with col3:
    break_length = st.slider("Break minutes", 5, 20, 10)

notes = st.text_area(
    "What feels difficult?",
    placeholder="Example: I forget OS scheduling algorithms and DBMS normalization.",
    height=120
)

if st.button("Generate Weak Subject Plan", type="primary"):
    if not selected_subjects:
        st.warning("Select at least one subject.")
    else:
        prompt = (
            "Create a daily revision and practice plan for these weak subjects: "
            + ", ".join(selected_subjects)
            + f". Study block: {session_length} minutes. Break: {break_length} minutes. "
            + f"Student notes: {notes}"
        )

        with st.spinner("Creating revision plan..."):
            result = ask_ai_tutor(
                prompt,
                "B.Tech CSE",
                "medium",
                st.session_state.token,
                task="improvement"
            )

        for subject in selected_subjects:
            st.session_state.weak_subject_plan[subject] = {
                "reminder": str(reminder_time),
                "study_block": session_length,
                "break": break_length,
                "created": str(date.today())
            }

        st.success("Daily weak-subject plan created.")
        st.write(result.get("answer", "No plan generated."))

st.divider()

st.subheader("Daily Revision Board")

if not st.session_state.weak_subject_plan:
    st.info("No weak subjects selected yet.")
else:
    for subject, plan in st.session_state.weak_subject_plan.items():
        with st.container(border=True):
            st.subheader(subject)
            st.write(f"Reminder: {plan['reminder']}")
            st.write(f"Focus block: {plan['study_block']} minutes")
            st.write(f"Break: {plan['break']} minutes")
            st.progress(0.35, text="Today: revise notes, solve 5 questions, review mistakes.")

st.components.v1.html(
    """
    <script>
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }
    </script>
    """,
    height=0
)
