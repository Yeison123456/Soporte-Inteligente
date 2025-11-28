from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Role
from app.schemas.roles import RoleCreate, RoleOut
from app.database import get_db

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleOut)
async def crear_rol(data: RoleCreate, db: AsyncSession = Depends(get_db)):
    rol = Role(nombre=data.nombre, descripcion=data.descripcion)
    db.add(rol)
    await db.commit()
    await db.refresh(rol)
    return rol

@router.get("/", response_model=list[RoleOut])
async def listar_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role))
    return result.scalars().all()
