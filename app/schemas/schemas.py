from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.schemas.users import UserOut

class EstadoHistorialOut(BaseModel):
    estado: str
    fecha: datetime

class TicketIn(BaseModel):
    ID_Ticket: Optional[str] = None
    titulo: str
    Descripcion_Caso: str
    correo_cliente: str


class TicketOut(BaseModel):
    ID_Ticket: str
    Cliente: UserOut
    Account_Manager: UserOut
    Tipo_Mantenimiento: str
    Riesgo_Churn_Real: float
    Recomendacion: dict
    Descripcion_Caso: str
    Titulo: str
    Estado_Actual: str
    Fecha_Creacion: datetime
    Estados_Historial: list[EstadoHistorialOut] 

