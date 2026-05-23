import os

import streamlit as st


def require_login():
    if st.session_state.get("logged_in"):
        return

    if os.environ.get("SCREENSHOT_MODE") == "1":
        st.session_state.logged_in = True
        st.session_state.token = os.environ.get("SCREENSHOT_TOKEN", "")
        st.session_state.user = {
            "email": "teacher.preview@example.com",
            "name": "Teacher Preview",
            "role": "teacher"
        }
        return

    st.switch_page("app.py")
