import re

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


CONCEPT_ANSWERS = {
    "maths": {
        "answer": "Maths, or mathematics, is the study of numbers, quantities, shapes, patterns, measurements, and logical reasoning. It helps us calculate, compare, prove ideas, solve problems, and describe the real world using rules and formulas.",
        "steps": [
            "Arithmetic studies numbers and basic operations like addition, subtraction, multiplication, and division.",
            "Algebra uses symbols and equations to represent unknown values.",
            "Geometry studies shapes, sizes, angles, and space.",
            "Calculus studies change, motion, rates, and accumulation."
        ],
        "example": "When you calculate marks percentage, measure distance, write code logic, or analyze data, you are using mathematics.",
        "practice": "Name one place where you use maths in daily life."
    },
    "mathematics": {
        "answer": "Mathematics is the study of numbers, quantities, shapes, patterns, measurements, and logical reasoning. It helps us calculate, compare, prove ideas, solve problems, and describe the real world using rules and formulas.",
        "steps": [
            "Arithmetic studies numbers and basic operations like addition, subtraction, multiplication, and division.",
            "Algebra uses symbols and equations to represent unknown values.",
            "Geometry studies shapes, sizes, angles, and space.",
            "Calculus studies change, motion, rates, and accumulation."
        ],
        "example": "When you calculate marks percentage, measure distance, write code logic, or analyze data, you are using mathematics.",
        "practice": "Name one place where you use mathematics in daily life."
    },
    "transistor": {
        "answer": "A transistor is a small semiconductor device that can switch electronic signals on and off or amplify them. It is one of the basic building blocks of computers, radios, phones, and almost all modern electronic circuits.",
        "steps": [
            "It has three terminals, usually called emitter, base, and collector in a BJT, or source, gate, and drain in a FET.",
            "A small input signal controls a larger current flowing through the device.",
            "When used as a switch, it acts like an electronic on/off gate.",
            "When used as an amplifier, it makes a weak signal stronger."
        ],
        "example": "In a computer chip, millions or billions of tiny transistors switch on and off to represent 0s and 1s.",
        "practice": "Why are transistors useful in digital computers?"
    },
    "photosynthesis": {
        "answer": "Photosynthesis is the process by which green plants use sunlight, carbon dioxide, and water to make glucose food and release oxygen.",
        "steps": [
            "Chlorophyll in leaves absorbs sunlight.",
            "The plant takes in carbon dioxide from the air.",
            "Roots absorb water from the soil.",
            "Light energy converts carbon dioxide and water into glucose and oxygen."
        ],
        "example": "A leaf uses sunlight during the day to make food for the plant.",
        "practice": "What are the two main raw materials needed for photosynthesis?"
    },
    "machine learning": {
        "answer": "Machine learning is a type of artificial intelligence where computers learn patterns from data and use those patterns to make predictions or decisions.",
        "steps": [
            "The model is given training data.",
            "It finds patterns in that data.",
            "It is tested on new data.",
            "It improves when the data and feedback are better."
        ],
        "example": "A spam filter learns from many emails and predicts whether a new email is spam.",
        "practice": "Why does the quality of training data matter?"
    }
}


def normalize_text(text):
    return re.sub(
        r"\s+",
        " ",
        text.strip().lower()
    )


def find_known_concept(question):
    normalized = normalize_text(question)

    for concept in CONCEPT_ANSWERS:
        if concept in normalized:
            return concept

    return None


def build_tutor_prompt(question, subject, difficulty, task):
    task_instructions = {
        "answer": "Give the exact answer first, then a short explanation, steps, example, and practice question.",
        "teach": "Teach the topic like a live tutor. Explain clearly, build from basics, use examples, identify mistakes, and end with a practice question.",
        "summarize": "Summarize the student's text into clear revision notes with key points and a one-line takeaway.",
        "weak_topics": "Identify likely topics the student needs to improve, explain why, and rank them by priority.",
        "improvement": "Create a practical improvement plan with daily actions, practice tasks, and checkpoints."
    }

    return f"""
You are an expert AI study tutor for school students.

Task:
{task_instructions.get(task, task_instructions["answer"])}

Subject:
{subject}

Difficulty:
{difficulty}

Student input:
{question}

Rules:
- Start with a direct answer.
- Be accurate and specific.
- Use simple student-friendly language.
- Keep it useful, not too long.
- If the student asks for a definition, give the definition immediately.
- If it is a problem, solve it step by step.
- End with one quick practice question.
- If SOURCE MODE says uploaded material only, do not use outside knowledge.
"""


def format_known_answer(concept, subject, difficulty):
    data = CONCEPT_ANSWERS[concept]
    steps = "\n".join(
        f"{index}. {step}"
        for index, step in enumerate(data["steps"], start=1)
    )

    return f"""
Direct answer:
{data["answer"]}

How to understand it:
{steps}

Example:
{data["example"]}

Quick check:
{data["practice"]}
"""


def fallback_tutor_answer(question, subject, difficulty, task):
    known_concept = find_known_concept(question)

    if task == "answer" and known_concept:
        return format_known_answer(
            known_concept,
            subject,
            difficulty
        )

    definition_match = re.search(
        r"\bwhat\s+is\s+([a-zA-Z0-9 _\\-]+)",
        question,
        flags=re.IGNORECASE
    )

    if task in ["answer", "teach"] and definition_match:
        topic = definition_match.group(1).strip(" ?.").title()
        return f"""
Direct answer:
{topic} is the main concept being asked about. In study terms, understand it by learning its definition, purpose, how it works, and one real example.

How to learn it:
1. Write the definition in one simple sentence.
2. Identify where it is used.
3. Break it into smaller parts or steps.
4. Solve or explain one example.
5. Check whether your answer directly answers the question.

Example:
If the topic is from computer science, connect it to how a program, system, data, or network behaves. If it is from science or mathematics, connect it to the rule, formula, or process involved.

Quick check:
Write one sentence explaining {topic} in your own words.
"""

    if task == "teach":
        return f"""
Direct teaching answer:
Here is how to study this topic: {question[:220]}

Lesson:
1. Start with the definition and purpose.
2. Break the topic into 3-5 smaller parts.
3. Learn one solved example.
4. Try one question without looking at the answer.
5. Revise the mistake immediately.

Common mistake:
Students often memorize the wording without understanding where the idea is used.

Practice:
Explain the topic aloud in one minute, then write one exam-style question from it.
"""

    if task == "summarize":
        return f"""
Summary:
{question}

Key points:
1. Focus on the main idea first.
2. Pick out important terms, formulas, names, or steps.
3. Turn the content into short revision bullets.

One-line takeaway:
The most important idea is the central concept asked in the question.
"""

    if task == "weak_topics":
        return f"""
Topics that need improvement:
1. Core concept clarity - the question suggests you may need a stronger definition or base idea.
2. Step-by-step explanation - practice explaining how the answer is reached.
3. Examples and application - connect the concept to one real example.

Priority:
Start with the definition, then solve two examples, then explain the topic aloud in your own words.
"""

    if task == "improvement":
        return f"""
Improvement plan:
Day 1: Learn the definition and write it in your own words.
Day 2: Study two solved examples.
Day 3: Try five practice questions without checking answers first.
Day 4: Review your mistakes and write the correct method.
Day 5: Teach the topic aloud in one minute.

Practice task:
Create one easy, one medium, and one hard question from this topic and solve them.
"""

    return f"""
Direct answer:
I need the local AI model to give a fully exact answer for this question. Based on the text, the topic is {subject}, and the question is: {question}

Best next step:
Ask the question with the exact chapter, formula, or options if it is from an exam. I can then solve it more precisely.

Quick practice:
Write the main keyword from your question and one thing you already know about it.
"""


def generate_tutor_answer(
    question,
    subject="General",
    difficulty="medium",
    task="answer"
):
    known_concept = find_known_concept(question)

    if task == "answer" and known_concept:
        return {
            "answer": format_known_answer(
                known_concept,
                subject,
                difficulty
            ),
            "source": "instant_concept_bank",
            "task": task
        }

    prompt = build_tutor_prompt(
        question,
        subject,
        difficulty,
        task
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=45
        )
        response.raise_for_status()

        answer = response.json().get(
            "response",
            ""
        ).strip()

        if answer:
            return {
                "answer": answer,
                "source": "ollama",
                "task": task
            }

    except Exception:
        pass

    return {
        "answer": fallback_tutor_answer(
            question,
            subject,
            difficulty,
            task
        ),
        "source": "fallback",
        "task": task
    }
