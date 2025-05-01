from pydantic import BaseModel

class ProductCreate(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        from_attributes = True