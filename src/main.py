from fastapi import FastAPI

from src.dataworkers.routers import router as router_documents
from src.db.database import connect_to_mongo, close_mongo_connection
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title='ProK test'
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup():
    """
    Creates a connection to the database.
    """
    await connect_to_mongo()


@app.on_event('shutdown')
async def on_shutdown():
    """
    Closes the database connection.
    """
    close_mongo_connection()


app.include_router(router_documents)
