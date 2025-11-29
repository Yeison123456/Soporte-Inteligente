from fastapi import FastAPI
from app.database import engine, Base
from app.api import tickets, users, roles  # tus endpoints

app = FastAPI(title="Support AI Backend")

# Incluir routers
app.include_router(tickets.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")

# Startup event para inicializar tablas
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas inicializadas correctamente")
