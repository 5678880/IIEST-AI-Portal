import streamlit as st

from components.sidebar import show_sidebar
from components.theme import ai_feature_grid, apply_theme, hero
from services.api_client import login_user, register_user


st.set_page_config(
    page_title="IIEST Student-Teacher AI Portal",
    page_icon="AI",
    layout="wide"
)

apply_theme()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if st.session_state.logged_in:
    show_sidebar()

    hero(
        "IIEST Student-Teacher AI Portal",
        f"Welcome {st.session_state.user['name']}. Use the sidebar pages to move between teacher intelligence, student learning, exams, grading, and analytics."
    )

    ai_feature_grid(
        [
            {
                "title": "AI for teachers",
                "body": "Question generation, grading support, attendance risk detection, class-test planning, and student intervention suggestions."
            },
            {
                "title": "AI for students",
                "body": "BerriBot voice tutor, custom exams, weak-subject revision, papers, learning resources, and personalized feedback."
            },
            {
                "title": "AI for collaboration",
                "body": "Teachers can inspect the student portal, understand learner experience, and assign better support from the same workspace."
            }
        ]
    )

    st.info(f"Logged in as {st.session_state.user['role']}. Open a page from the sidebar.")
    st.stop()


hero(
    "IIEST Student-Teacher AI Portal",
    "A modern academic intelligence system for teachers and students: exams, grading, attendance, resources, BerriBot tutoring, and AI-assisted intervention planning."
)

ai_feature_grid(
    [
        {
            "title": "Teacher intelligence",
            "body": "AI helps teachers create tests, grade faster, detect weak students, and plan attendance-based interventions."
        },
        {
            "title": "Student learning",
            "body": "Students get voice tutoring, custom exams, weak-topic practice, papers, resources, and revision reminders."
        },
        {
            "title": "Reliable assessment",
            "body": "Mixed-format exams support MCQ, short, long, numerical, and coding-style answers."
        }
    ]
)

login_tab, signup_tab = st.tabs(
    [
        "Login",
        "Sign Up"
    ]
)

with login_tab:
    st.subheader("Login To Your Account")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", type="primary"):
        with st.spinner("Authenticating..."):
            result = login_user(login_email, login_password)

        if result.get("success"):
            st.session_state.logged_in = True
            st.session_state.token = result.get("access_token")
            st.session_state.user = result.get("user")
            st.success("Login successful")
            st.rerun()
        else:
            st.error(result.get("message", "Invalid Credentials"))

with signup_tab:
    st.subheader("Create New Account")
    signup_name = st.text_input("Full Name")
    signup_email = st.text_input("Signup Email")
    signup_password = st.text_input("Signup Password", type="password")
    signup_role = st.selectbox("Select Role", ["teacher", "student"])

    if st.button("Create Account"):
        signup_data = {
            "name": signup_name,
            "email": signup_email,
            "password": signup_password,
            "role": signup_role
        }

        with st.spinner("Creating Account..."):
            result = register_user(signup_data)

        if "user_id" in result:
            st.success("Account created successfully")
            st.info("You can now login using your credentials.")
        else:
            st.error(result.get("error", "Signup Failed"))

st.divider()
st.caption("AI Assessment Platform • FastAPI • Streamlit • Ollama • Llama3")
