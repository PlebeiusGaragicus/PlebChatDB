import os

from motor.motor_asyncio import AsyncIOMotorClient



class Database:
    client: AsyncIOMotorClient = None
    db = None


db = Database()




async def connect_to_mongo():
    db.client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS", "mongodb://localhost:27017"))
    db.db = db.client.user_balance

async def close_mongo_connection():
    db.client.close()
