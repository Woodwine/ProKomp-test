from motor.motor_asyncio import AsyncIOMotorClient

from src.config import DB_PORT, DB_HOST

MONGO_URL = f'mongodb://{DB_HOST}:{DB_PORT}'


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database():
    return db.client


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(MONGO_URL, uuidRepresentation="standard")


def close_mongo_connection():
    db.client.close()
