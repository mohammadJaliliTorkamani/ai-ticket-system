from typing import Optional

from bson import ObjectId

from app.db.mongodb import db
from app.models.ticket import Ticket
from app.models.user import User
from app.utils.vector_utils import cosine_similarity


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


async def get_user_by_email_by_id(user_id: str) -> Optional[User]:
    data = await db.users.find_one({"_id": ObjectId(user_id)})
    if data:
        return User(**data)
    return None

async def get_ticket_by_id(ticket_id: str) -> Optional[Ticket]:
    data = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
    if data:
        return Ticket(**data)
    return None

async def get_similar_tickets(ticket_id: str, user_id: str, top_k: int = 3):
    tickets = []
    source_ticket = await get_ticket_by_id(ticket_id)

    if not source_ticket:
        return []

    if str(source_ticket.user_id) != str(user_id):
        return []

    if not source_ticket.embedding:
        return []

    similarities = []

    cursor = db.tickets.find({
        "user_id": ObjectId(user_id),
        "embedding": {"$exists": True, "$ne": None}
    })

    async for ticket_data in cursor:
        ticket = Ticket(**ticket_data)

        # Skip source ticket
        if str(ticket.id) == ticket_id:
            continue

        # Safety check
        if not ticket.embedding:
            continue

        score = cosine_similarity(
            source_ticket.embedding,
            ticket.embedding
        )

        similarities.append((ticket, score))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return [ticket for ticket, _ in similarities[:top_k]]