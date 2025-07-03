import os
import logging
import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from jose import JWTError, jwt
import bcrypt
from dotenv import load_dotenv
from chat.askgemini import ask_gemini

from Schema.Schema import User, Userlog  # Your pydantic schemas
from auth.Auth import verify_token, oauth2_scheme  # Your auth helpers

# Optional: If ask_gemini can be async, import here
# from chat.askgemini import ask_gemini  
# If not async, you can keep it sync but then chat_endpoint is sync

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Config from environment
MONGODB_URL = os.getenv("MONGOURL")
MONGODB_NAME = os.getenv("MONGO_DB_NAME")
JWT_SECRET = os.getenv("TOKEN")

# MongoDB client and collections
client = MongoClient(MONGODB_URL)
db = client[MONGODB_NAME]
Model = db["users"]
ModelHistory = db["history"]

app = FastAPI()

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for chat messages
class ChatRequest(BaseModel):
    message: str

# ====================
# Routes
# ====================

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/register")
async def register(user: User):
    try:
        existing_user = Model.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        Model.insert_one({
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
        })
        return {"message": "User registered successfully"}
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/login")
async def login(user: Userlog):
    try:
        existing_user = Model.find_one({"email": user.email})
        if not existing_user:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        stored_password = existing_user["password"]
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")

        if not bcrypt.checkpw(user.password.encode("utf-8"), stored_password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        if not JWT_SECRET:
            raise HTTPException(status_code=500, detail="JWT secret not configured")

        token = jwt.encode(
            {"id": str(existing_user["_id"]), "email": existing_user["email"]},
            JWT_SECRET,
            algorithm="HS256",
        )
        return {"message": "Login successful", "token": token}
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat")
async def chat_endpoint(
    data: ChatRequest,
    token: str = Depends(oauth2_scheme),
):
    user = verify_token(token)
    try:
        # Await the async ask_gemini function to get the string response
        reply = await ask_gemini(data.message)  # <-- await here!

        # Save chat history with actual reply string
        ModelHistory.insert_one({
            "userId": user["id"],
            "message": data.message,
            "response": reply,
            "timestamp": datetime.utcnow(),
        })

        return {"response": reply}
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/history")
async def get_history(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    try:
        history = list(
            ModelHistory.find(
                {"userId": user["id"]},
                {"_id": 0, "message": 1, "response": 1, "timestamp": 1},
            ).sort("timestamp", 1)
        )
        return {"history": history}
    except Exception:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Unable to fetch history")
