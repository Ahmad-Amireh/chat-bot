# app/services/product.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return p

def create_product(db: Session, data: ProductCreate):
    p = Product(name=data.name, price=data.price)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def update_product(db: Session, product_id: int, data: ProductUpdate):
    p = get_product_by_id(db, product_id)
    if data.name is not None:
        p.name = data.name
    if data.price is not None:
        p.price = data.price
    db.commit()
    db.refresh(p)
    return p

def delete_product(db: Session, product_id: int):
    p = get_product_by_id(db, product_id)
    db.delete(p)
    db.commit()
    return {"deleted": product_id}