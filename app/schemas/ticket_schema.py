from pydantic import BaseModel, Field
from typing import Optional

class TicketCreate(BaseModel):
    title: str
    description: str

class TicketOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    category: Optional[str]
    summary: Optional[str]
    suggested_reply: Optional[str]
    status: str
