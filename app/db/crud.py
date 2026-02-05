from app.db.mongodb import db
from app.models.user import User
from app.models.ticket import Ticket
from bson import ObjectId
from typing import Optional

# --- USERS ---
async def create_user(user: User):
    result = await db.users.insert_one(user.dict(by_alias=True))
    user.id = result.inserted_id
    return user

async def get_user_by_email(email: str) -> Optional[User]:
    data = await db.users.find_one({"email": email})
    if data:
        return User(**data)
    return None

# --- TICKETS ---
async def create_ticket(ticket: Ticket):
    result = await db.tickets.insert_one(ticket.dict(by_alias=True))
    ticket.id = result.inserted_id
    return ticket

async def get_tickets_by_user(user_id: str):
    tickets = []
    cursor = db.tickets.find({"user_id": ObjectId(user_id)})
    async for ticket in cursor:
        tickets.append(Ticket(**ticket))
    return tickets
