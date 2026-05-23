import requests
import json
import re

# -----------------------------------
# OLLAMA URL
# -----------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"

# -----------------------------------
# EXTRACT JSON
# -----------------------------------

def extract_json(text):

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    match = re.search(

        r"\[.*\]",

        text,

        re.DOTALL
    )

    if match:

        return match.group(0)

    return None

# -----------------------------------
# GENERATE SINGLE QUESTION
# -----------------------------------

def generate_single_question(

    topic,

    difficulty
):

    prompt = f"""

Generate EXACTLY ONE multiple choice question.

Topic:
{topic}

Difficulty:
{difficulty}

Return ONLY JSON.

FORMAT:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer": "Correct Option"
  }}
]

"""

    response = requests.post(

        OLLAMA_URL,

        json={

            "model": "llama3",

            "prompt": prompt,

            "stream": False
        }
    )

    result = response.json()

    raw_response = result.get(
        "response",
        ""
    )

    json_text = extract_json(
        raw_response
    )

    if not json_text:

        raise Exception(
            "JSON extraction failed"
        )

    questions = json.loads(
        json_text
    )

    return questions[0]

# -----------------------------------
# GENERATE QUESTIONS
# -----------------------------------

def generate_questions(

    topic,

    difficulty,

    num_questions
):

    generated_questions = []

    # -----------------------------------
    # LOOP EXACT QUESTION COUNT
    # -----------------------------------

    for index in range(num_questions):

        try:

            question = generate_single_question(

                topic,

                difficulty
            )

            question["difficulty"] = difficulty

            question["topic"] = topic

            generated_questions.append(
                question
            )

        except Exception as e:

            print("\nQUESTION GENERATION ERROR:\n")
            print(str(e))

            # -----------------------------------
            # FALLBACK QUESTION
            # -----------------------------------

            generated_questions.append(

                {

                    "question":

                    f"{index + 1}. Which option best explains {topic}?",

                    "options": [

                        f"{topic} is an important concept that helps solve real academic or technical problems.",

                        f"{topic} is only a random term and has no practical use.",

                        f"{topic} is always used only for memorizing definitions.",

                        f"{topic} is unrelated to the subject being studied."
                    ],

                    "correct_answer":

                    f"{topic} is an important concept that helps solve real academic or technical problems.",

                    "difficulty":

                    difficulty,

                    "topic":

                    topic
                }
            )

    return generated_questions
