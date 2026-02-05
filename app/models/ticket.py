from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from datetime import datetime
from app.models.user import PyObjectId


class Ticket(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    title: str
    description: str
    category: Optional[str] = None
    summary: Optional[str] = None
    suggested_reply: Optional[str] = None
    status: str = "open"  # open, pending, closed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
        schema_extra = {
            "example": {
                "user_id": "64b9c2f6c2a1b2a1f0a1a1a1",
                "title": "Cannot login",
                "description": "I forgot my password and can't login",
                "status": "open"
            }
        }
