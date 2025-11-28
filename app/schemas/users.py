from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    nombre: str
    correo: EmailStr
    antiguedad_contrato: int | None = None
    segmento: str | None = None
    hashed_password: str
    rol_id: int

class UserCreate(UserBase):
    hashed_password: str

class UserOut(UserBase):
    id: int

    model_config = {
        "from_attributes": True 
    }

class UserLogin(BaseModel):
    correo: str
    password: str
