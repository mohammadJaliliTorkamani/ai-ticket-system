from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.db.crud import create_ticket, get_tickets_by_user
from app.models.ticket import Ticket
from app.schemas.ticket_schema import TicketCreate, TicketOut
from app.tasks.ticket_tasks import analyze_ticket

router = APIRouter(tags=["Tickets"])


# --- Create Ticket ---
@router.post("/tickets", response_model=TicketOut)
async def create_new_ticket(ticket: TicketCreate, current_user=Depends(get_current_user)):
    ticket_obj = Ticket(user_id=current_user.id, title=ticket.title, description=ticket.description)
    created_ticket = await create_ticket(ticket_obj)

    # Trigger Celery task to analyze ticket asynchronously
    analyze_ticket.delay(str(created_ticket.id), ticket.title, ticket.description)

    return TicketOut(**created_ticket.dict())


# --- List Tickets ---
@router.get("/tickets", response_model=list[TicketOut])
async def list_my_tickets(current_user=Depends(get_current_user)):
    tickets = await get_tickets_by_user(str(current_user.id))
    return [TicketOut(**t.dict()) for t in tickets]
