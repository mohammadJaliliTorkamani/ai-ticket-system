from typing import Optional

from pydantic import BaseModel


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
