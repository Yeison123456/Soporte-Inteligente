import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine, Base
from app.models.models import Role, User
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__ident="2b",  # fuerza uso moderno y compatible
)

def hash_password(password: str):
    return pwd_context.hash(password)


async def init_db():
    print("📌 Creando tablas...")

    # Crear tablas usando un engine sync dentro del async engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Crear session async
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as db:

        # ----------------- ROLES -----------------
        roles_existentes = (await db.execute(select(Role))).scalars().all()

        if not roles_existentes:
            print("📌 Insertando roles...")

            roles_data = [
                Role(nombre="cliente", descripcion="Rol para clientes"),
                Role(nombre="account_manager", descripcion="Rol para account managers"),
            ]

            db.add_all(roles_data)
            await db.commit()

        # Obtener roles actualizados
        roles = {
            r.nombre: r
            for r in (await db.execute(select(Role))).scalars().all()
        }

        # ---------------- USUARIOS ----------------
        users_existentes = (await db.execute(select(User))).scalars().all()

        if not users_existentes:
            print("📌 Insertando usuarios...")

            cliente = User(
                nombre="Cliente Prueba",
                correo="jeisonrodriguezrodriguez227@gmail.com",
                hashed_password=hash_password("cliente123"),
                antiguedad_contrato=3,
                segmento="A",
                rol_id=roles["cliente"].id
            )

            manager1 = User(
                nombre="Manager Uno",
                correo="manager1@empresa.com",
                hashed_password=hash_password("manager1"),
                rol_id=roles["account_manager"].id
            )

            manager2 = User(
                nombre="Manager Dos",
                correo="manager2@empresa.com",
                hashed_password=hash_password("manager2"),
                rol_id=roles["account_manager"].id
            )

            db.add_all([cliente, manager1, manager2])
            await db.commit()

    print("🚀 Base de datos inicializada correctamente.")


if __name__ == "__main__":
    asyncio.run(init_db())
