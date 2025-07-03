from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import HTTPException
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str):
    jwt_secret = os.getenv("TOKEN")
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
