from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db

from app.security import create_access_token

from app.services.user_service import (
    create_user,
    get_user_by_email
)

router = APIRouter()

# -----------------------------------
# REGISTER USER
# -----------------------------------

@router.post("/register")

def register(

    data: dict,

    db: Session = Depends(get_db)
):

    existing_user = get_user_by_email(

        db,

        data.get("email")
    )

    if existing_user:

        return {

            "error":

            "User already exists"
        }

    user = create_user(

        db,

        data
    )

    return {

        "message":

        "User Registered Successfully",

        "user_id": user.id
    }

# -----------------------------------
# LOGIN
# -----------------------------------

@router.post("/login")

def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)
):

    user = get_user_by_email(

        db,

        form_data.username
    )

    if not user:

        return {

            "success": False,

            "message": "User not found"
        }

    if user.password != form_data.password:

        return {

            "success": False,

            "message": "Invalid password"
        }

    access_token = create_access_token(

        {

            "sub": user.email,

            "role": user.role
        }
    )

    return {

        "success": True,

        "access_token": access_token,

        "user": {

            "name": user.name,

            "email": user.email,

            "role": user.role
        }
    }