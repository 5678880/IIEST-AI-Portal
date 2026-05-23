import streamlit as st
import time

def show_timer(minutes=30):

    # Convert to seconds
    total_seconds = minutes * 60

    # Timer placeholder
    timer_placeholder = st.empty()

    while total_seconds >= 0:

        mins = total_seconds // 60

        secs = total_seconds % 60

        timer_placeholder.markdown(

            f"""
            ## ⏳ Time Remaining:
            ### {mins:02d}:{secs:02d}
            """
        )

        time.sleep(1)

        total_seconds -= 1