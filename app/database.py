from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.base import Base  # Use absolute import
from app.models import user_model, product_model  # Use absolute import

DATABASE_URL = "mysql+asyncmy://root:root@localhost:3306/security_journey"

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for AsyncSession
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error in create_tables: {e}")

async def get_db():
    async with SessionLocal() as db:  # Use async with to manage session lifecycle
        yield db