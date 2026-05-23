import json

from app.models import Question


QUESTIONS_PER_TYPE_PER_SUBJECT = 500


SUBJECT_CATALOG = {
    "Engineering Mathematics": ("MA101", ["Linear Algebra", "Calculus", "Differential Equations", "Probability", "Transforms", "Numerical Methods"]),
    "Discrete Mathematics": ("CS201", ["Logic", "Sets", "Relations", "Functions", "Graphs", "Combinatorics"]),
    "Engineering Physics": ("PH101", ["Semiconductors", "Optics", "Quantum Mechanics", "Lasers", "Waves", "Modern Physics"]),
    "Engineering Chemistry": ("CH101", ["Thermodynamics", "Electrochemistry", "Polymers", "Corrosion", "Water Treatment", "Chemical Bonding"]),
    "Basic Electrical Engineering": ("EE101", ["DC Circuits", "AC Circuits", "Transformers", "Machines", "Power Factor", "Network Theorems"]),
    "Basic Electronics Engineering": ("EC101", ["Diodes", "Transistors", "Amplifiers", "Logic Gates", "Op-Amps", "Rectifiers"]),
    "Programming in C": ("CS101", ["Pointers", "Arrays", "Functions", "Structures", "File Handling", "Recursion"]),
    "Object Oriented Programming": ("CS102", ["Classes and Objects", "Inheritance", "Polymorphism", "Encapsulation", "Exception Handling", "Interfaces"]),
    "Data Structures": ("CS202", ["Arrays", "Stacks", "Queues", "Linked Lists", "Trees", "Graphs", "Hashing", "Heaps"]),
    "Design and Analysis of Algorithms": ("CS301", ["Time Complexity", "Sorting", "Searching", "Dynamic Programming", "Greedy Algorithms", "Graph Algorithms", "Divide and Conquer"]),
    "Computer Organization and Architecture": ("CS203", ["Instruction Cycle", "Pipelining", "Cache Memory", "Addressing Modes", "ALU", "I/O Organization"]),
    "Operating Systems": ("CS302", ["Process Scheduling", "Deadlock", "Memory Management", "Paging", "File Systems", "Synchronization", "Semaphores"]),
    "Database Management Systems": ("CS303", ["ER Model", "Normalization", "SQL Joins", "Transactions", "Indexing", "Relational Algebra", "Concurrency Control"]),
    "Computer Networks": ("CS401", ["OSI Model", "TCP UDP", "IP Addressing", "Routing", "HTTP DNS", "Network Security", "Congestion Control"]),
    "Theory of Computation": ("CS402", ["Finite Automata", "Regular Expressions", "Context Free Grammar", "Pushdown Automata", "Turing Machine", "Decidability"]),
    "Compiler Design": ("CS501", ["Lexical Analysis", "Parsing", "Syntax Directed Translation", "Intermediate Code", "Code Optimization", "Symbol Table"]),
    "Software Engineering": ("CS304", ["SDLC", "Requirement Analysis", "UML", "Testing", "Software Metrics", "Agile"]),
    "Web Technologies": ("CS204", ["HTML CSS", "JavaScript", "REST APIs", "HTTP", "Authentication", "Frontend Backend"]),
    "Artificial Intelligence": ("CS403", ["Search Algorithms", "Knowledge Representation", "Inference", "Planning", "Expert Systems", "Heuristics"]),
    "Machine Learning": ("CS502", ["Supervised Learning", "Regression", "Classification", "Clustering", "Model Evaluation", "Overfitting"]),
    "Deep Learning": ("CS601", ["Neural Networks", "Backpropagation", "CNN", "RNN", "Optimization", "Regularization"]),
    "Data Science": ("CS701", ["Data Cleaning", "EDA", "Statistics", "Visualization", "Feature Engineering", "Model Selection"]),
    "Cloud Computing": ("CS503", ["Virtualization", "IaaS", "PaaS", "SaaS", "Containers", "Load Balancing"]),
    "Cyber Security": ("CS404", ["CIA Triad", "Malware", "Authentication", "Firewalls", "Risk Assessment", "Security Policies"]),
    "Cryptography and Network Security": ("CS702", ["Symmetric Key", "Public Key", "Hashing", "Digital Signature", "RSA", "Key Exchange"]),
    "Internet of Things": ("CS602", ["Sensors", "Actuators", "MQTT", "Edge Computing", "IoT Architecture", "Security"]),
    "Mobile Application Development": ("CS603", ["Activities", "Layouts", "Intents", "SQLite", "APIs", "Lifecycle"]),
    "Distributed Systems": ("CS504", ["Clocks", "Consistency", "Replication", "Consensus", "RPC", "Fault Tolerance"]),
    "Big Data Analytics": ("CS604", ["Hadoop", "MapReduce", "Spark", "NoSQL", "Stream Processing", "Data Warehousing"]),
    "Human Computer Interaction": ("CS703", ["Usability", "User Research", "Prototyping", "Accessibility", "Evaluation", "Interaction Design"]),
    "Professional Ethics": ("HS801", ["Engineering Ethics", "Privacy", "IPR", "Professional Responsibility", "Cyber Law", "Sustainability"]),
    "Environmental Studies": ("EV101", ["Ecosystems", "Pollution", "Biodiversity", "Climate Change", "Waste Management", "Sustainable Development"])
}


MCQ_STEMS = [
    "In a GATE-style question on {topic}, which statement is most accurate?",
    "For {subject}, identify the correct interpretation of {topic}.",
    "Which option best matches the university-level use of {topic}?",
    "A student is solving a problem involving {topic}. Which idea should be applied first?",
    "Which statement about {topic} is correct for competitive exam preparation?"
]


SHORT_STEMS = [
    "Write a short note on {topic} in {subject}.",
    "Define {topic} and state one important use in {subject}.",
    "Mention the key steps or properties of {topic}.",
    "Explain why {topic} is important in university examinations.",
    "Differentiate the main idea of {topic} from a closely related concept."
]


LONG_STEMS = [
    "Explain {topic} in detail with working, advantages, limitations, and an example.",
    "Discuss {topic} as asked in a university-level descriptive answer.",
    "Describe the complete mechanism of {topic} and show how it is applied.",
    "Write a detailed answer on {topic}, including diagram or algorithm where applicable.",
    "Analyze {topic} with theory, steps, example, and common mistakes."
]


def difficulty_for(index):
    return ["easy", "medium", "hard"][index % 3]


def build_mcq(subject, code, topic, index):
    stem = MCQ_STEMS[index % len(MCQ_STEMS)].format(
        subject=subject,
        topic=topic
    )
    scenario = index // len(MCQ_STEMS) + 1
    correct_options = [
        f"Identify the rule behind {topic}, apply it to the given constraints, and verify the result.",
        f"Use the formal definition of {topic} and check whether each condition in the problem is satisfied.",
        f"Break the {topic} problem into assumptions, method, and final inference before choosing an answer.",
        f"Apply {topic} to the specific data or scenario instead of relying only on memorized wording."
    ]
    wrong_option_sets = [
        [
            f"Ignore constraints because {topic} questions always have a fixed answer.",
            f"Choose the longest option because GATE questions in {subject} reward length.",
            f"Treat {topic} as unrelated theory with no effect on problem solving."
        ],
        [
            f"Use trial-and-error only; definitions of {topic} are unnecessary.",
            f"Assume every case of {topic} has identical input and output.",
            f"Skip the condition checking step because only the final keyword matters."
        ],
        [
            f"Memorize one sentence and apply it to every {topic} problem.",
            f"Select the option that mentions {subject}, even if the reasoning is wrong.",
            f"Ignore edge cases because GATE-style questions never test them."
        ],
        [
            f"Convert every {topic} question into a general aptitude question.",
            f"Answer from memory without reading the values or scenario.",
            f"Assume diagrams, formulas, or tables are decorative and not part of the solution."
        ]
    ]
    correct = correct_options[index % len(correct_options)]
    distractors = wrong_option_sets[index % len(wrong_option_sets)]
    options = [correct] + distractors

    return {
        "subject": subject,
        "subject_code": code,
        "topic": topic,
        "question_type": "mcq",
        "difficulty": difficulty_for(index),
        "marks": 1,
        "question": f"{code}-GATE-MCQ-{index + 1:03d}: {stem} Case variant {scenario}.",
        "options": options,
        "correct_answer": correct,
        "keywords": f"{topic}, {subject}, GATE, concept, application",
        "solution_steps": "Read the constraints; identify the concept; eliminate distractors; select the option that matches the rule.",
        "explanation": f"This GATE-style item checks conceptual application of {topic} in {subject}.",
        "source": "GATE-style IIEST CSE Seed Bank",
        "university_pattern": "GATE MCQ",
        "repeated_concept": "Yes"
    }


def build_short(subject, code, topic, index):
    stem = SHORT_STEMS[index % len(SHORT_STEMS)].format(
        subject=subject,
        topic=topic
    )

    return {
        "subject": subject,
        "subject_code": code,
        "topic": topic,
        "question_type": "short",
        "difficulty": difficulty_for(index + 1),
        "marks": 3,
        "question": f"{code}-SHORT-{index + 1:03d}: {stem}",
        "options": [],
        "correct_answer": f"A good short answer should define {topic}, mention its purpose, and connect it to {subject} with one precise example.",
        "keywords": f"{topic}, definition, purpose, example, {subject}",
        "solution_steps": "Define the term; write 2-3 key points; add one use or example.",
        "explanation": f"Short-answer marking checks definition, keyword coverage, and relevance to {subject}.",
        "source": "IIEST CSE Short Answer Seed Bank",
        "university_pattern": "Short Answer",
        "repeated_concept": "Yes"
    }


def build_long(subject, code, topic, index):
    stem = LONG_STEMS[index % len(LONG_STEMS)].format(
        subject=subject,
        topic=topic
    )

    return {
        "subject": subject,
        "subject_code": code,
        "topic": topic,
        "question_type": "long",
        "difficulty": difficulty_for(index + 2),
        "marks": 8,
        "question": f"{code}-LONG-{index + 1:03d}: {stem}",
        "options": [],
        "correct_answer": f"A complete long answer should introduce {topic}, explain the working or method, include a diagram/algorithm/example where relevant, discuss advantages and limitations, and conclude with exam-focused points.",
        "keywords": f"{topic}, working, method, diagram, example, advantages, limitations, conclusion",
        "solution_steps": "Introduction; theory; working/steps; example; advantages; limitations; conclusion.",
        "explanation": f"Long-answer marking checks structure, depth, examples, and conceptual correctness for {subject}.",
        "source": "IIEST CSE Long Answer Seed Bank",
        "university_pattern": "Long Descriptive",
        "repeated_concept": "Yes"
    }


def build_questions():
    questions = []

    for subject, (code, topics) in SUBJECT_CATALOG.items():
        builders = {
            "mcq": build_mcq,
            "short": build_short,
            "long": build_long
        }

        for question_type, builder in builders.items():
            for index in range(QUESTIONS_PER_TYPE_PER_SUBJECT):
                topic = topics[index % len(topics)]
                questions.append(
                    builder(subject, code, topic, index)
                )

    return questions


def add_question(db, item):
    options = item.get("options", [])

    while len(options) < 4:
        options.append("")

    db.add(
        Question(
            question=item["question"],
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_answer=item["correct_answer"],
            difficulty=item["difficulty"],
            subject=item["subject"],
            topic=item["topic"],
            question_type=item["question_type"],
            marks=item["marks"],
            keywords=item.get("keywords"),
            solution_steps=item.get("solution_steps"),
            explanation=item.get("explanation"),
            test_cases=item.get("test_cases"),
            source=item.get("source"),
            university_pattern=item.get("university_pattern"),
            repeated_concept=item.get("repeated_concept"),
            created_by="system_seed",
            exam_id=None
        )
    )


def seed_question_bank(db):
    target_count = len(SUBJECT_CATALOG) * 3 * QUESTIONS_PER_TYPE_PER_SUBJECT
    existing_seed_count = db.query(Question).filter(
        Question.created_by == "system_seed"
    ).count()

    if existing_seed_count >= target_count:
        return existing_seed_count

    db.query(Question).filter(
        Question.created_by == "system_seed"
    ).delete(synchronize_session=False)
    db.commit()

    for item in build_questions():
        add_question(db, item)

    coding_questions = [
        ("Data Structures", "CS202", "Stacks", "Write a program to implement push and pop operations on a stack."),
        ("Data Structures", "CS202", "Arrays", "Write a program to find the maximum element in an array."),
        ("Design and Analysis of Algorithms", "CS301", "Sorting", "Write a program to implement binary search on a sorted array."),
        ("Object Oriented Programming", "CS102", "Classes and Objects", "Write a class Student with name, roll number, and display method."),
        ("Database Management Systems", "CS303", "SQL Joins", "Write an SQL query to display students with their enrolled course names.")
    ]

    for subject, code, topic, question in coding_questions:
        add_question(
            db,
            {
                "subject": subject,
                "subject_code": code,
                "topic": topic,
                "question_type": "coding",
                "difficulty": "hard",
                "marks": 10,
                "question": question,
                "options": [],
                "correct_answer": "Code should be logically correct, handle sample input, and produce expected output.",
                "keywords": "input, output, logic, edge case",
                "solution_steps": "Understand input; choose data structure; implement logic; test output.",
                "explanation": "Coding answers are checked using keywords, logic notes, and sample test cases.",
                "test_cases": json.dumps([{"input": "sample input", "output": "expected output"}]),
                "source": "Coding Practice Bank",
                "university_pattern": "Lab/Coding",
                "repeated_concept": "Yes"
            }
        )

    db.commit()

    return db.query(Question).filter(
        Question.created_by == "system_seed"
    ).count()
