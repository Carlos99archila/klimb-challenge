import jwt
import os
from datetime import datetime, timedelta, timezone

#SECRET_KEY = str(os.environ.get("SECRET_KEY")) #coin variable de entorno en la nube
SECRET_KEY = str(os.environ.get("SECRET_KEY", "klimb-challenge-key")) #para usar en local 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
