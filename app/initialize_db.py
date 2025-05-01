import asyncio
from .database import create_tables  # Use relative import
from .models import user_model, product_model

async def main():
    await create_tables()

if __name__ == "__main__":
    asyncio.run(main())