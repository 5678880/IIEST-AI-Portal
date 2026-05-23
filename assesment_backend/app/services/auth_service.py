from app.security import (
    hash_password,
    verify_password,
    create_access_token
)

# -----------------------------------
# MOCK DATABASE USERS
# -----------------------------------

mock_users = {

    "student@test.com": {

        "name": "Student",

        "email": "student@test.com",

        "hashed_password": hash_password("1234"),

        "role": "student"
    },

    "teacher@test.com": {

        "name": "Teacher",

        "email": "teacher@test.com",

        "hashed_password": hash_password("1234"),

        "role": "teacher"
    }
}

# -----------------------------------
# AUTHENTICATE USER
# -----------------------------------

def authenticate_user(

    email,

    password
):

    user = mock_users.get(email)

    # -----------------------------------
    # USER NOT FOUND
    # -----------------------------------

    if not user:

        return {

            "success": False,

            "message": "User not found"
        }

    # -----------------------------------
    # VERIFY PASSWORD
    # -----------------------------------

    if not verify_password(

        password,

        user["hashed_password"]
    ):

        return {

            "success": False,

            "message": "Invalid password"
        }

    # -----------------------------------
    # CREATE TOKEN
    # -----------------------------------

    token = create_access_token({

        "sub": user["email"],

        "role": user["role"]
    })

    return {

        "success": True,

        "message": "Login Successful",

        "access_token": token,

        "token_type": "bearer",

        "user": {

            "name": user["name"],

            "email": user["email"],

            "role": user["role"]
        }
    }