from sqlalchemy import Column, Integer, String
from app.base import Base

class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40), unique=True, index=True)
    price = Column(Integer, unique=False, index=True)