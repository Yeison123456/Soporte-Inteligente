from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import tickets, users, roles  # tus endpoints

app = FastAPI(title="Support AI Backend")

# ============================================
# Configuración CORS - IMPORTANTE
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:5173",      # Alternativa localhost
        "http://localhost:3000",      # React dev server (por si cambias)
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],  # Permite todos los headers
)

# Para desarrollo, puedes usar esto (menos seguro):
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Permite TODOS los orígenes
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# ============================================
# Incluir routers
# ============================================
app.include_router(tickets.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")

# ============================================
# Startup event para inicializar tablas
# ============================================
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas inicializadas correctamente")
    print("🌐 CORS configurado para desarrollo")

# ============================================
# Health check endpoint (opcional pero útil)
# ============================================
@app.get("/")
async def root():
    return {
        "message": "Support AI Backend API",
        "status": "running",
        "docs":"/docs"
}