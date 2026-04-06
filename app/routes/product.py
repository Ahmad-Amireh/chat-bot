# app/routes/product.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product import get_all_products, create_product, update_product, delete_product

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("", response_model=List[ProductResponse], operation_id="get_products")
def list_products(db: Annotated[Session, Depends(get_db)]):
    return get_all_products(db)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, operation_id="create_products")
def add_product(data: ProductCreate, db: Annotated[Session, Depends(get_db)]):
    return create_product(db, data)

@router.put("/{product_id}", response_model=ProductResponse, operation_id="update_products")
def edit_product(product_id: int, data: ProductUpdate, db: Annotated[Session, Depends(get_db)]):
    return update_product(db, product_id, data)

@router.delete("/{product_id}", operation_id="delete_products")
def remove_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    return delete_product(db, product_id)