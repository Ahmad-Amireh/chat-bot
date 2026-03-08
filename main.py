from fastapi import FastAPI
from app.routes import user, message, session, chat
from app.core.database import Base, engine

app = FastAPI(title="Chatbot API")

Base.metadata.create_all(bind= engine) # to create Db tabel

@app.get("/")
def root():
    return {"message": "Chatbot API running"}

app.include_router(user.router)
app.include_router(session.router)
app.include_router(message.router)
app.include_router(chat.router)