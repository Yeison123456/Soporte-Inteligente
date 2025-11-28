from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User
from app.schemas.users import UserCreate, UserOut, UserLogin
from app.database import get_db
from passlib.hash import bcrypt

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.post("/", response_model=UserOut)
async def crear_usuario(data: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = bcrypt.hash(data.password)
    user = User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hashed_pw,
        antiguedad_contrato=0,
        Segmento=data.Segmento,
        role_id=data.role_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/", response_model=list[UserOut])
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.correo == data.correo)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # verificar rol Account Manager
    if user.rol_id != 2:  # o el ID que uses para Account Manager
        raise HTTPException(status_code=403, detail="Acceso denegado: solo Account Managers")

    return {
        "message": "Inicio de sesión exitoso",
        "user_id": user.id,
        "nombre": user.nombre,
        "rol": user.rol_id
    }
