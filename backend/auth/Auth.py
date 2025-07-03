from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException
import os
from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str):
    jwt_secret = os.getenv("TOKEN")
    if not jwt_secret:
        raise HTTPException(status_code=500, detail="JWT secret not configured")
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
