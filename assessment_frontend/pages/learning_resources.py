from urllib.parse import quote_plus

import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import ask_ai_tutor
from services.study_catalog import BTECH_CSE_SUBJECTS, RESOURCE_SOURCES


st.set_page_config(
    page_title="Learning Resources",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") not in ["student", "teacher"]:
    st.error("Student Or Teacher Access Only")
    st.stop()


show_sidebar()

st.title("Learning Resources")
st.caption("Enter any syllabus topic and get learning links, notes directions, PDFs, and deeper references.")

subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS)
topic = st.text_input("Topic or syllabus unit", placeholder="Example: deadlock in operating systems")
level = st.selectbox("Depth", ["Beginner", "Exam revision", "Deep understanding"])

if st.button("Find Resources", type="primary"):
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        query = quote_plus(f"{subject} {topic} {level}")

        st.subheader("Instant Learning Links")
        for label, base_url in RESOURCE_SOURCES:
            st.link_button(label, base_url + query, use_container_width=True)

        st.divider()
        st.subheader("AI Study Map")
        with st.spinner("Creating resource roadmap..."):
            result = ask_ai_tutor(
                f"Create a study map for {topic} in {subject}. Include what to watch, what to read, what to practice, and what to revise.",
                subject,
                "medium",
                st.session_state.token,
                task="improvement"
            )
        st.write(result.get("answer", "No study map generated."))
