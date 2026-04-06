from fastmcp import FastMCP
from app.core.database import SessionLocal
from app.services import product as product_service
from app.schemas.product import ProductCreate, ProductUpdate
import logging

mcp = FastMCP("product-manager")

logging.basicConfig(filename="mcp_debug.log", level=logging.INFO)

@mcp.tool()
def list_products() -> list[dict]:
    db = SessionLocal()
    products = product_service.get_all_products(db)
    db.close()
    return [{"id": p.id, "name": p.name, "price": p.price} for p in products]


@mcp.tool()
def add_product(name: str, price: float) -> dict:
    db = SessionLocal()
    data = ProductCreate(name=name, price=price)
    p = product_service.create_product(db, data)
    db.close()
    return {"id": p.id, "name": p.name, "price": p.price}


@mcp.tool()
def update_product(product_id: int, name: str = None, price: float = None) -> dict:
    db = SessionLocal()
    data = ProductUpdate(name=name, price=price)
    p = product_service.update_product(db, product_id, data)
    db.close()
    return {"id": p.id, "name": p.name, "price": p.price}


@mcp.tool()
def delete_product(product_id: int) -> dict:
    db = SessionLocal()
    result = product_service.delete_product(db, product_id)
    db.close()
    return result


if __name__ == "__main__":
    mcp.run(transport="http")