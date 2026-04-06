# app/schemas/product.py
from pydantic import BaseModel, ConfigDict

class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)