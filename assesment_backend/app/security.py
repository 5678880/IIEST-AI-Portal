from datetime import datetime
from datetime import timedelta

from jose import jwt
from jose import JWTError

from passlib.context import CryptContext

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

# -----------------------------------
# SECRET CONFIG
# -----------------------------------

SECRET_KEY = "SUPER_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# -----------------------------------
# TOKEN URL
# -----------------------------------

oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl="login"
)

# -----------------------------------
# PASSWORD HASHING
# -----------------------------------

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)

# -----------------------------------
# HASH PASSWORD
# -----------------------------------

def hash_password(password):

    return pwd_context.hash(password)

# -----------------------------------
# VERIFY PASSWORD
# -----------------------------------

def verify_password(

    plain_password,

    hashed_password
):

    return pwd_context.verify(

        plain_password,

        hashed_password
    )

# -----------------------------------
# CREATE ACCESS TOKEN
# -----------------------------------

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(

        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({

        "exp": expire
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt

# -----------------------------------
# VERIFY TOKEN
# -----------------------------------

def verify_token(

    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        role = payload.get("role")

        # -----------------------------------
        # INVALID TOKEN
        # -----------------------------------

        if email is None:

            raise HTTPException(

                status_code=401,

                detail="Invalid Token"
            )

        return {

            "email": email,

            "role": role
        }

    except JWTError:

        raise HTTPException(

            status_code=401,

            detail="Token Verification Failed"
        )