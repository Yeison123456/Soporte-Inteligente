from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "mysql+aiomysql://root:@localhost:3306/tickets_db"

# Motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

# Sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
