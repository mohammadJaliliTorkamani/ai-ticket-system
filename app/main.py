from fastapi import FastAPI

from app.db.mongodb import db

app = FastAPI(title="Welcome to AI Ticket Backend!")

@app.get("/health")
async def health_check():
    collections = await db.list_collection_names()
    return {
        "status": "OK",
        "collections": collections
    }