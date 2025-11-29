from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import TicketHistory
from app.schemas.ticketStatusHistory import EstadoHistorialIn, EstadoHistorialOut
from app.database import get_db

router = APIRouter(prefix="/historyTicket", tags=["HistoryTicket"])

@router.post("/", response_model=EstadoHistorialOut)
async def crear_rol(data: EstadoHistorialIn, db: AsyncSession = Depends(get_db)):
    ticketHistory = TicketHistory(ticket_id=data.ticket_id, estado=data.estado, comentario=data.comentario, fecha_cambio=data.fecha_cambio)
    db.add(ticketHistory)
    await db.commit()
    await db.refresh(ticketHistory)
    return ticketHistory

@router.get("/", response_model=list[EstadoHistorialOut])
async def listar_historyTicket(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketHistory))
    return result.scalars().all()
