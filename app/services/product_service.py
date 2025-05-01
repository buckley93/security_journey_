from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import product_schema
from app.models import product_model

class ProductServices:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_products(self) -> list[product_schema.ProductCreate]:
        try:
            query = select(product_model.Products)
            result = await self.session.execute(query)
            products = result.scalars().all() 
            return [product_schema.ProductCreate.from_orm(product) for product in products]
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def get_product_by_id(self, product_id: int) -> product_schema.ProductCreate:
        try:
            if not product_id:
                return None
            query = select(product_model.Products).where(product_model.Products.id == product_id)
            result = await self.session.execute(query)
            product = result.scalars().first() 
            print(product.price)
            return product_schema.ProductCreate.from_orm(product) if product else None
        except Exception as e:
            print(f"Error fetching products: {e}")
            return None