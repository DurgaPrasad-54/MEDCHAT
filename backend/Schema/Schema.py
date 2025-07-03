from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    username: str
    email: str
    password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
class Userlog(BaseModel):
    email: str
    password: str

class History(BaseModel):
    user_id: str
    query: str
    response: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
