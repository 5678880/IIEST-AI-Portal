import os

import requests

# ===================================
# BASE URL
# ===================================

BASE_URL = os.environ.get(

    "API_BASE_URL",

    "http://127.0.0.1:8001"
)

# ===================================
# LOGIN USER
# ===================================

def login_user(

    email,

    password
):

    try:

        response = requests.post(

            f"{BASE_URL}/login",

            data={

                "username": email,

                "password": password
            }
        )

        return response.json()

    except Exception as e:

        return {

            "success": False,

            "message": str(e)
        }

# ===================================
# REGISTER USER
# ===================================

def register_user(data):

    try:

        response = requests.post(

            f"{BASE_URL}/register",

            json=data
        )

        return response.json()

    except Exception as e:

        return {

            "error": str(e)
        }

# ===================================
# GENERATE AI QUESTIONS
# ===================================

def generate_ai_questions(

    topic,

    difficulty,

    num_questions,

    exam_id,

    token
):

    try:

        response = requests.post(

            f"{BASE_URL}/generate_questions",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json={

                "topic": topic,

                "difficulty": difficulty,

                "num_questions": num_questions,

                "exam_id": exam_id
            }
        )

        # -----------------------------------
        # SAFE RESPONSE
        # -----------------------------------

        if response.status_code != 200:

            return {

                "generated_questions": []
            }

        if not response.text:

            return {

                "generated_questions": []
            }

        return response.json()

    except Exception as e:

        print(e)

        return {

            "generated_questions": []
        }

# ===================================
# FETCH QUESTIONS
# ===================================

def fetch_questions():

    try:

        response = requests.get(

            f"{BASE_URL}/questions"
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        return response.json()

    except Exception as e:

        print(e)

        return []

# ===================================
# CREATE EXAM
# ===================================

def create_exam(

    exam_data,

    token
):

    try:

        response = requests.post(

            f"{BASE_URL}/create_exam",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json=exam_data
        )

        if response.status_code != 200:

            return {}

        if not response.text:

            return {}

        return response.json()

    except Exception as e:

        print(e)

        return {}

# ===================================
# FETCH EXAMS
# ===================================

def fetch_exams():

    try:

        response = requests.get(

            f"{BASE_URL}/exams"
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        return response.json()

    except Exception as e:

        print(e)

        return []

# ===================================
# ADD QUESTIONS TO EXAM
# ===================================

def add_questions_to_exam(

    exam_id,

    question_ids,

    token
):

    try:

        response = requests.post(

            f"{BASE_URL}/add_questions_to_exam",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json={

                "exam_id": exam_id,

                "question_ids": question_ids
            }
        )

        if response.status_code != 200:

            return {}

        if not response.text:

            return {}

        return response.json()

    except Exception as e:

        print(e)

        return {}

# ===================================
# START EXAM
# ===================================

def start_exam(

    exam_id,

    token
):

    try:

        response = requests.get(

            f"{BASE_URL}/start_exam/{exam_id}",

            headers={

                "Authorization":

                f"Bearer {token}"
            }
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        return response.json()

    except Exception as e:

        print(e)

        return []

# ===================================
# SUBMIT EXAM
# ===================================

def submit_exam(

    exam_id,

    answers,

    token
):

    try:

        response = requests.post(

            f"{BASE_URL}/submit_exam",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json={

                "exam_id": exam_id,

                "answers": answers
            }
        )

        if response.status_code != 200:

            return {}

        if not response.text:

            return {}

        return response.json()

    except Exception as e:

        print(e)

        return {}

# ===================================
# CREATE CUSTOM EXAM
# ===================================

def create_custom_exam(exam_config, token):

    try:

        response = requests.post(

            f"{BASE_URL}/custom_exam",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json=exam_config
        )

        if response.status_code != 200:

            return {}

        if not response.text:

            return {}

        return response.json()

    except Exception as e:

        print(e)

        return {}

# ===================================
# SEED QUESTION BANK
# ===================================

def seed_question_bank(token):

    try:

        response = requests.post(

            f"{BASE_URL}/seed_question_bank",

            headers={

                "Authorization":

                f"Bearer {token}"
            }
        )

        if response.status_code != 200:

            return {}

        return response.json()

    except Exception as e:

        print(e)

        return {}

# ===================================
# FETCH ANALYTICS
# ===================================

def fetch_analytics(token):

    try:

        response = requests.get(

            f"{BASE_URL}/analytics",

            headers={

                "Authorization":

                f"Bearer {token}"
            }
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        return response.json()

    except Exception as e:

        print(e)

        return []

# ===================================
# FETCH RESULTS
# ===================================

def fetch_results(token):

    try:

        response = requests.get(

            f"{BASE_URL}/results",

            headers={

                "Authorization":

                f"Bearer {token}"
            }
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        return response.json()

    except Exception as e:

        print(e)

        return []

# ===================================
# FETCH MY RESULTS
# ===================================

def fetch_my_results(token):

    try:

        response = requests.get(

            f"{BASE_URL}/my_results",

            headers={

                "Authorization":

                f"Bearer {token}"
            }
        )

        if response.status_code != 200:

            return []

        if not response.text:

            return []

        try:

            return response.json()

        except:

            return []

    except Exception as e:

        print(e)

        return []

# ===================================
# AI TUTOR
# ===================================

def ask_ai_tutor(question, subject, difficulty, token, task="answer"):

    try:

        response = requests.post(

            f"{BASE_URL}/ai_tutor",

            headers={

                "Authorization":

                f"Bearer {token}"
            },

            json={

                "question": question,

                "subject": subject,

                "difficulty": difficulty,

                "task": task
            }
        )

        if response.status_code != 200:

            return {

                "answer": "I could not reach the tutor right now.",

                "source": "error"
            }

        if not response.text:

            return {

                "answer": "The tutor did not return an answer.",

                "source": "empty"
            }

        return response.json()

    except Exception as e:

        return {

            "answer": str(e),

            "source": "exception"
        }


# ===================================
# SUBJECT ENROLLMENTS
# ===================================

def fetch_subject_catalog():
    try:
        response = requests.get(f"{BASE_URL}/subject_catalog")

        if response.status_code != 200 or not response.text:
            return []

        return response.json()

    except Exception:
        return []


def add_teacher_subject(data, token):
    try:
        response = requests.post(
            f"{BASE_URL}/teacher_subjects",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        if response.status_code not in [200, 201] or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def fetch_teacher_subjects(token):
    try:
        response = requests.get(
            f"{BASE_URL}/teacher_subjects",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200 or not response.text:
            return []

        return response.json()

    except Exception:
        return []


def fetch_teacher_subject_students(token):
    try:
        response = requests.get(
            f"{BASE_URL}/teacher_subject_students",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200 or not response.text:
            return []

        return response.json()

    except Exception:
        return []


def add_student_subject(data, token):
    try:
        response = requests.post(
            f"{BASE_URL}/student_subjects",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        if response.status_code not in [200, 201] or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def fetch_student_subjects(token):
    try:
        response = requests.get(
            f"{BASE_URL}/student_subjects",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200 or not response.text:
            return []

        return response.json()

    except Exception:
        return []


def populate_exam_from_bank(data, token):
    try:
        response = requests.post(
            f"{BASE_URL}/populate_exam_from_bank",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        if response.status_code != 200 or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def preview_question_sets(data, token):
    try:
        response = requests.post(
            f"{BASE_URL}/preview_question_sets",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        if response.status_code != 200 or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def create_exam_sets(data, token):
    try:
        response = requests.post(
            f"{BASE_URL}/create_exam_sets",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )

        if response.status_code != 200 or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def save_exam_set_assignments(assignments, token):
    try:
        response = requests.post(
            f"{BASE_URL}/exam_set_assignments",
            headers={"Authorization": f"Bearer {token}"},
            json={"assignments": assignments}
        )

        if response.status_code != 200 or not response.text:
            return {}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def fetch_exam_set_assignments(token):
    try:
        response = requests.get(
            f"{BASE_URL}/exam_set_assignments",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200 or not response.text:
            return []

        return response.json()

    except Exception:
        return []
