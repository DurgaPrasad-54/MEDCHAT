import os
import logging
import traceback
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from jose import JWTError, jwt
import bcrypt
from dotenv import load_dotenv

from Schema.Schema import User, Userlog
from auth.Auth import verify_token, oauth2_scheme
from chat.askgemini import ask_gemini

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Config from environment
MONGODB_URL = os.getenv("MONGOURL")
MONGODB_NAME = os.getenv("MONGO_DB_NAME")
JWT_SECRET = os.getenv("TOKEN")

if not MONGODB_URL:
    raise EnvironmentError("MONGOURL not found in environment")
if not MONGODB_NAME:
    raise EnvironmentError("MONGO_DB_NAME not found in environment")
if not JWT_SECRET:
    raise EnvironmentError("TOKEN not found in environment")

try:
    client = MongoClient(MONGODB_URL)
    db = client[MONGODB_NAME]
    Model = db["users"]
    ModelHistory = db["history"]
    
    client.admin.command('ping')
    logging.info("MongoDB connection successful")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise

app = FastAPI(title="Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.post("/register")
async def register(user: User):
    try:
        existing_email = Model.find_one({"email": user.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        
        result = Model.insert_one(user_data)
        
        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {traceback.format_exc()}")
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

        token_data = {
            "id": str(existing_user["_id"]),
            "email": existing_user["email"],
            "username": existing_user["username"]
        }
        
        token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(existing_user["_id"]),
                "username": existing_user["username"],
                "email": existing_user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat")
async def chat_endpoint(
    data: ChatRequest,
    token: str = Depends(oauth2_scheme),
):
    user = verify_token(token)
    
    try:
        if not data.message or not data.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        reply = await ask_gemini(data.message.strip())

        history_data = {
            "userId": user["id"],
            "message": data.message.strip(),
            "response": reply,
            "timestamp": datetime.utcnow(),
        }
        
        ModelHistory.insert_one(history_data)

        return {
            "response": reply,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/history")
async def get_history(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    
    try:
        history = list(
            ModelHistory.find(
                {"userId": user["id"]},
                {"_id": 0, "message": 1, "response": 1, "timestamp": 1},
            ).sort("timestamp", -1).limit(100)  
        )
        
        return {
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logging.error(f"History fetch error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Unable to fetch history")
@app.delete("/clearhistory")
async def clear_history(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    
    try:
        result = ModelHistory.delete_many({"userId": user["id"]})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="No history found to delete")
        
        return {"message": "History cleared successfully", "deleted_count": result.deleted_count}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"History clear error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Unable to clear history")
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
