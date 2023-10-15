from typing import List, Any, Optional

from src.dataworkers.models import QueryParams, DocumentInfo
from src.db.database import AsyncIOMotorClient
from src.config import DB_NAME


async def add_document(connection: AsyncIOMotorClient, doc: dict) -> DocumentInfo | str:
    """
    Adds a new document to collection 'documents' and creates a new database collection corresponding to the file
    """
    db = connection[DB_NAME]
    doc_name = doc['doc_name']
    collection_list = await db.list_collection_names()

    if doc_name in collection_list:
        return "Документ с таким названием уже существует"

    document_collection = db.get_collection('documents')
    item = await document_collection.insert_one({"doc_name": doc_name, "columns": doc["columns"]})
    created_doc = await document_collection.find_one({'_id': item.inserted_id})
    new_collection = db[doc_name]
    await new_collection.insert_many(doc["rows"])
    return created_doc


async def retrieve_documents(connection: AsyncIOMotorClient) -> List[DocumentInfo]:
    """
    Retrieves a list of documents from the collection 'documents'
    """
    db = connection[DB_NAME]
    document_collection = db.get_collection('documents')
    docs = await document_collection.find().to_list(length=None)
    return docs


async def retrieve_one_document(connection: AsyncIOMotorClient, doc_name: str) -> DocumentInfo | None:
    """
    Retrieves one document from the collection 'documents'
    """
    db = connection[DB_NAME]
    document_collection = db.get_collection('documents')
    doc = await document_collection.find_one({"doc_name": doc_name})

    if doc:
        return doc
    return None


async def get_filtered_document(connection: AsyncIOMotorClient, doc_name: str,
                                params: Optional[QueryParams]) -> Any:
    """
    Retrieves the filtered collection
    """
    db = connection[DB_NAME]
    collection_list = await db.list_collection_names()

    if doc_name not in collection_list:
        return None

    collection = db[doc_name]
    if params:
        rows_params = params.get('rows_params')
        limit = params.get("limit")
        sort = params.get('sort')
        cursor = collection.find(rows_params)
        if sort:
            cursor.sort(sort)
        if limit:
            cursor.limit(limit)
    else:
        cursor = collection.find()
    return await cursor.to_list(length=None)


async def delete_document(connection: AsyncIOMotorClient, doc_name: str) -> bool:
    """
    Deletes the collection from database and the corresponding document from the collection 'documents'
    """
    db = connection[DB_NAME]
    collection_list = await db.list_collection_names()
    document_collection = db.get_collection('documents')
    if doc_name in collection_list:
        collection = db[doc_name]
        collection.drop()
        await document_collection.delete_one({"doc_name": doc_name})
        return True
    return False
