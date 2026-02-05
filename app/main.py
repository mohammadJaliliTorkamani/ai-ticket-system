from fastapi import FastAPI

from app.db.mongodb import db
from app.routes import auth_routes

app = FastAPI(title="Welcome to AI Ticket Backend!")
app.include_router(auth_routes.router)

@app.get("/health")
async def health_check():
    collections = await db.list_collection_names()
    return {
        "status": "OK",
        "collections": collections
    }