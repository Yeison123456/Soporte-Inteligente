from pydantic import BaseModel
from datetime import datetime

class EstadoHistorialIn(BaseModel):
    estado: str
    comentario: str
    ticket_id: str

class EstadoHistorialOut(EstadoHistorialIn):
    id: int

    model_config = {
        "from_attributes": True
    }