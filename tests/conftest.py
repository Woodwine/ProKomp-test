import pytest

from src.config import DB_NAME
from src.db.database import AsyncIOMotorClient, MONGO_URL


@pytest.fixture(scope="session")
def test_q_params():
    """
    Fixture representing test query params.
    """
    return {
        "rows_params": {"city": "Moscow"},
        "sort": [("age", -1)],
        "limit": 1,
    }


@pytest.fixture(scope='session')
def test_doc():
    """
    Fixture representing test document.
    """
    return {
        "doc_name": "test_info",
        "columns": ["name", "surname", "age", "city"],
        "rows": [
            {"name": "Anna", "surname": "Ivanova", "age": 32, "city": "Moscow"},
            {"name": "Alexey", "surname": "Petrov", "age": 28, "city": "Tula"},
            {"name": "Inna", "surname": "Sidorova", "age": 42, "city": "Rostov"},
            {"name": "Maxim", "surname": "Novicov", "age": 40, "city": "Moscow"},
        ]
    }


@pytest.fixture
async def test_db():
    """
    Fixture representing database
    """
    client = AsyncIOMotorClient(MONGO_URL)
    return client


@pytest.fixture(autouse=True, scope='session')
def run_before_and_after_tests(test_doc):
    """
    Fixture for deletion test artefacts from database.
    """
    client = AsyncIOMotorClient(MONGO_URL)
    yield
    db = client[DB_NAME]
    db['documents'].delete_one({"doc_name": test_doc["doc_name"]})
    db[test_doc["doc_name"]].drop()
