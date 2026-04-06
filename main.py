from fastapi import FastAPI
from app.routes import user, message, session, chat, product
from app.core.database import Base, engine
from fastapi_mcp import FastApiMCP

app = FastAPI(title="Chatbot API")
mcp = FastApiMCP(app, include_operations=["get_products", "create_products", "update_products","delete_products"])
mcp.mount_http()

Base.metadata.create_all(bind= engine) # to create Db tabel

@app.get("/")
def root():
    return {"message": "Chatbot API running"}

app.include_router(user.router)
app.include_router(session.router)
app.include_router(message.router)
app.include_router(chat.router)
app.include_router(product.router)