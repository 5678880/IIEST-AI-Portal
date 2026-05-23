from pydantic import BaseModel

# -----------------------------------
# LOGIN SCHEMA
# -----------------------------------

class LoginSchema(BaseModel):

    email: str

    password: str

# -----------------------------------
# USER RESPONSE SCHEMA
# -----------------------------------

class UserResponse(BaseModel):

    id: int

    name: str

    email: str

    role: str

# -----------------------------------
# QUESTION RESPONSE SCHEMA
# -----------------------------------

class QuestionSchema(BaseModel):

    id: int

    question: str

    option_a: str

    option_b: str

    option_c: str

    option_d: str

    correct_answer: str

    difficulty: str

    subject: str