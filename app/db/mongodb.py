import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = "ai_ticket_db"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
