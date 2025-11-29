from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
import uuid
import random


from app.services.gmail.send import send_correo
from app.schemas.schemas import TicketIn, TicketOut
from app.models.models import Ticket, TicketHistory, User, Role
from app.schemas.ticketStatusHistory import EstadoHistorialIn
from app.database import get_db

from app.services import phishing as phishing_svc
from app.services import anonymizer as sensibilidad_svc
from app.services import mantenimiento as mant_svc
from app.services import churn as churn_svc
from app.services import vectorizer as vectorizer_svc
from app.core.preprocess import clean_text, text_signals
from app.services.rules import rule_engine

router = APIRouter()
vec = vectorizer_svc.load_vectorizer()

@router.post("/tickets", response_model=TicketOut)
async def process_ticket(ticket: TicketIn, db: AsyncSession = Depends(get_db)):


    ticket_id = ticket.ID_Ticket or str(uuid.uuid4())
    raw_text = ticket.Descripcion_Caso
    clean = clean_text(raw_text)
    signals = text_signals(clean)

    # -------------------------------------------------------------
    # 1) RESOLVER ID DEL CLIENTE USANDO CORREO
    # -------------------------------------------------------------
    q_cliente = await db.execute(
        select(User).join(Role).where(
            Role.nombre == "cliente",
            User.correo == ticket.correo_cliente
        )
    )
    cliente = q_cliente.scalars().first()


    if not cliente:
        raise HTTPException(
            status_code=400,
            detail="El correo del cliente no existe o no tiene rol 'cliente'."
        )

    id_cliente = cliente.id

    # -------------------------------------------------------------
    # 2) ASIGNAR ACCOUNT MANAGER RANDOM
    # -------------------------------------------------------------
    q_managers = await db.execute(
        select(User).join(Role).where(Role.nombre == "account_manager")
    )
    managers = q_managers.scalars().all()

    if not managers:
        raise HTTPException(
            status_code=400,
            detail="No existen usuarios con rol 'account_manager'."
        )

    manager_random = random.choice(managers)
    id_account_manager = manager_random.id

    # -------------------------------------------------------------
    # 3) CREAR TICKET EN BD Y GUARDAR ESTADO INICIAL “Nuevo”
    # -------------------------------------------------------------
    nuevo_ticket = Ticket(
        id=ticket_id,
        cliente_id=id_cliente,
        account_manager_id=id_account_manager,
        titulo=ticket.titulo,
        descripcion=raw_text,
        fecha_creacion=datetime.now(timezone.utc),
        recomendacion_agente= None,
        tipo_mantenimiento="",
        riego_churn=0,
        estado_actual="Nuevo",
    )

    db.add(nuevo_ticket)
    await db.commit()

    # HISTORIAL - estado “Nuevo”
    historial = TicketHistory(
        ticket_id=ticket_id,
        estado="Nuevo",
        comentario="Ticket creado",
        fecha_cambio=datetime.now(timezone.utc)
    )
    db.add(historial)
    await db.commit()

    # enviar aviso por correo
    enviar_correo( cliente.correo, ticket_id, historial.estado, historial.comentario)


    # -------------------------------------------------------------
    # 4) PHISHING
    # -------------------------------------------------------------
    is_phish, ph_reasons = phishing_svc.detect_phishing(clean)
    if is_phish:

        # Guardar cambio de estado a “Aislado”
        nuevo_estado = TicketHistory(
            ticket_id=ticket_id,
            estado="Aislado",
            comentario="Ticket aislado por phishing",
            fecha_cambio=datetime.now(timezone.utc)
        )
        db.add(nuevo_estado)

        # Actualizar estado actual
        nuevo_ticket.estado_actual = "Aislado"
        nuevo_ticket.recomendacion_agente =  {"level": "CRITICO", "message": "Phishing detectado"}
        await db.commit()

        # enviar aviso por correo
        enviar_correo( cliente.correo, ticket_id, nuevo_estado.estado, nuevo_estado.comentario)

        return {
            "ID_Ticket": ticket_id,
            "Cliente": cliente,
            "Account_Manager": manager_random,
            "Tipo_Mantenimiento": "None",
            "Riesgo_Churn_Real": 0,            
            "Descripcion_Caso": clean,
            "Titulo": nuevo_ticket.titulo,
            "Estado_Actual": nuevo_ticket.estado_actual,
            "Recomendacion": {"level": "CRITICO", "message": "Phishing detectado"},
            "Fecha_Creacion": nuevo_ticket.fecha_creacion,
            "Estados_Historial": await obtener_historial(ticket_id, db)
        }

    # -------------------------------------------------------------
    # 5) Sensibilidad (PII)
    # -------------------------------------------------------------
    clean = sensibilidad_svc.anonimizar_texto(clean)

    # -------------------------------------------------------------
    # 6) Clasificación mantenimiento
    # -------------------------------------------------------------
    classification, mant_reasons = mant_svc.classify_mantenimiento(clean)



    # -------------------------------------------------------------
    # 7) Churn
    # -------------------------------------------------------------
    churn_payload = {
        "Descripcion_Caso": clean,
        "Antiguedad_Contrato": cliente.antiguedad_contrato,
        "Volumen_Tickets_Ult_Mes": await get_volumen_tickets_ultimo_mes(db, cliente.id),
        "Segmento_Cliente": cliente.segmento
    }
    churn_result = churn_svc.predict_churn_score(churn_payload)

    

    # -------------------------------------------------------------
    # 8) Sentiment
    # -------------------------------------------------------------
    if signals["negative_count"] > signals["positive_count"]:
        sentiment_val = -1.0
    elif signals["positive_count"] > signals["negative_count"]:
        sentiment_val = 1.0
    else:
        sentiment_val = 0.0


    historial_abierto = TicketHistory(
        ticket_id=ticket_id,
        estado="Abierto",
        comentario="Ticket abierto para procesamiento", 
        fecha_cambio=datetime.now(timezone.utc)
    )
    db.add(historial_abierto)
    await db.commit()

    # -------------------------------------------------------------
    # 9) Actualizar estado actual
    # -------------------------------------------------------------
    nuevo_ticket.estado_actual = "Abierto"
    nuevo_ticket.recomendacion_agente =  rule_engine(churn_result["score"], sentiment_val)
    nuevo_ticket.tipo_mantenimiento = classification["class"]
    nuevo_ticket.riego_churn = churn_result["score"]
    await db.commit()

    # enviar aviso por correo
    enviar_correo( cliente.correo, ticket_id, historial_abierto.estado, historial_abierto.comentario)


    # -------------------------------------------------------------
    # 10) Respuesta final
    # -------------------------------------------------------------
    result = {
        "ID_Ticket": ticket_id,
        "Cliente": cliente,
        "Account_Manager": manager_random,
        "Tipo_Mantenimiento": classification["class"],
        "Riesgo_Churn_Real": churn_result["score"],
        "Recomendacion": rule_engine(churn_result["score"], sentiment_val),
        "Descripcion_Caso": clean,
        "Titulo": nuevo_ticket.titulo,
        "Estado_Actual": nuevo_ticket.estado_actual,
        "Fecha_Creacion": nuevo_ticket.fecha_creacion,
        "Estados_Historial": await obtener_historial(ticket_id, db)
    }

    return result

@router.get("/tickets", response_model=list[TicketOut])
async def get_all_tickets(db: AsyncSession = Depends(get_db)):

    # Traer todos los tickets
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()

    response = []

    for t in tickets:

        response.append({
            "ID_Ticket": t.id,
            "Cliente": await obtener_usuario(t.cliente_id, db),
            "Account_Manager": await obtener_usuario(t.account_manager_id, db),
            "Tipo_Mantenimiento": t.tipo_mantenimiento,
            "Riesgo_Churn_Real": t.riego_churn,
            "Recomendacion": t.recomendacion_agente or {},
            "Descripcion_Caso": t.descripcion,
            "Titulo": t.titulo,
            "Estado_Actual": t.estado_actual,
            "Fecha_Creacion": t.fecha_creacion,
            "Estados_Historial": await obtener_historial( t.id, db)
        })

    return response

@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_all_tickets(ticket_id: str, db: AsyncSession = Depends(get_db)):

    # Obtener ticket
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalars().first()


    return {
        "ID_Ticket": ticket.id,
        "Cliente": await obtener_usuario(ticket.cliente_id, db),
        "Account_Manager": await obtener_usuario(ticket.account_manager_id, db),
        "Tipo_Mantenimiento": ticket.tipo_mantenimiento,
        "Riesgo_Churn_Real": ticket.riego_churn,
        "Recomendacion": ticket.recomendacion_agente or {},
        "Descripcion_Caso": ticket.descripcion,
        "Titulo": ticket.titulo,
        "Estado_Actual": ticket.estado_actual,
        "Fecha_Creacion": ticket.fecha_creacion,
        "Estados_Historial": await obtener_historial( ticket.id, db)
    }


@router.put("/tickets/{ticket_id}")
async def actualizar_estado_ticket(
    ticket_id: str,
    data: EstadoHistorialIn,
    db: AsyncSession = Depends(get_db)
):

    # Buscar ticket
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalars().first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Actualizar estado actual del ticket
    ticket.estado_actual = data.estado

    # Crear registro en historial
    historial_entry = TicketHistory(
        ticket_id=ticket_id,
        estado=data.estado,          # usamos el mismo estado
        comentario=data.comentario,
        fecha_cambio=datetime.now(timezone.utc)
    )

    db.add(historial_entry)
    db.add(ticket)

    await db.commit()
    await db.refresh(ticket)

    # enviar aviso por correo
    enviar_correo( ticket.cliente.correo, ticket.id, ticket.estado_actual, historial_entry.comentario)

    return {
        "message": "Estado actualizado correctamente",
        "ID_Ticket": ticket.id,
        "Nuevo_Estado": ticket.estado_actual,
        "Comentario": historial_entry.comentario
    }


# -------------------------------------------------------------
# FUNCIÓN PARA OBTENER HISTORIAL
# -------------------------------------------------------------
async def obtener_historial(ticket_id: str, db: AsyncSession):
    q = await db.execute(
        select(TicketHistory).where(TicketHistory.ticket_id == ticket_id).order_by(TicketHistory.fecha_cambio)
    )
    rows = q.scalars().all()

    return [{"estado": r.estado, "fecha": r.fecha_cambio} for r in rows]

async def obtener_usuario(usuario_id: str, db: AsyncSession):
    q = await db.execute(
        select(User).where(User.id == usuario_id)
    )
    rows = q.scalars().all()

    return rows[0]

async def get_volumen_tickets_ultimo_mes(db, user_id: int):
    hace_30_dias = datetime.now(timezone.utc) - timedelta(days=30)

    query = select(func.count()).select_from(Ticket).where(
        Ticket.cliente_id == user_id,
        Ticket.fecha_creacion >= hace_30_dias
    )

    result = await db.execute(query)
    total = result.scalar()

    return total or 0

def enviar_correo (to: str, ticker_id: str, estado_actual: str, comentario: str):
    # enviar aviso por correo
    return send_correo( 
            to=to,
            subject=f"Actualización de Ticket #{ticker_id}",
            mensaje=f"""
                    Hola, tu ticket ha cambiado de estado.

                    Nuevo estado: {estado_actual}
                    Comentario: {comentario}

                    Gracias por comunicarte con soporte. No responder este correo
                    """
            )