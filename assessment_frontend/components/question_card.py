import streamlit as st

def display_question(question_data, q_index):

    st.subheader(
        f"Question {q_index + 1}"
    )

    st.write(
        question_data["question"]
    )

    selected_answer = st.radio(

        "Choose your answer",

        question_data["options"],

        index=None,

        key=f"question_{q_index}"

    )

    return selected_answer