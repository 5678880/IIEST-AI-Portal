from app.models import User

# -----------------------------------
# CREATE USER
# -----------------------------------

def create_user(

    db,

    user_data
):

    user = User(

        name=user_data.get(
            "name"
        ),

        email=user_data.get(
            "email"
        ),

        password=user_data.get(
            "password"
        ),

        role=user_data.get(
            "role"
        )
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user

# -----------------------------------
# FETCH USER
# -----------------------------------

def get_user_by_email(

    db,

    email
):

    user = db.query(
        User
    ).filter(

        User.email == email
    ).first()

    return user
