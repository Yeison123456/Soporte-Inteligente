from pydantic import BaseModel

class RoleBase(BaseModel):
    nombre: str
    descripcion: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    id: int

    model_config = {
        "from_attributes": True
    }
