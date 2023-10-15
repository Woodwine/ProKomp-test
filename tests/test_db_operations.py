import pytest
from src.db.db_methods import add_document, retrieve_documents, retrieve_one_document, get_filtered_document, \
    delete_document

name = "test_info"
fail_name = 'fail_test_info'


@pytest.mark.asyncio
async def test_add_document(test_db, test_doc):
    created_doc = await add_document(test_db, test_doc)
    assert created_doc.get('doc_name') == "test_info"
    assert created_doc.get('columns') == ["name", "surname", "age", "city"]


@pytest.mark.asyncio
async def test_fail_add_document(test_db, test_doc):
    result = await add_document(test_db, test_doc)
    assert result == "Документ с таким названием уже существует"


@pytest.mark.asyncio
async def test_retrieve_documents(test_db):
    docs = await retrieve_documents(test_db)
    assert len(docs) == 1
    assert docs[0].get("doc_name") == "test_info"


@pytest.mark.asyncio
@pytest.mark.parametrize("doc_name", [name])
async def test_retrieve_one_document(test_db, doc_name):
    doc = await retrieve_one_document(test_db, doc_name)
    assert doc.get("doc_name") == "test_info"
    assert doc.get('columns') == ["name", "surname", "age", "city"]


@pytest.mark.asyncio
@pytest.mark.parametrize("doc_name", [fail_name])
async def test_fail_retrieve_document(test_db, doc_name):
    result = await retrieve_one_document(test_db, doc_name)
    assert result is None


@pytest.mark.asyncio
async def test_get_filtered_document(test_db, test_q_params):
    all_docs = await get_filtered_document(test_db, name, test_q_params)
    doc = all_docs[0]
    assert len(all_docs) == 1
    assert doc.get("age") == 40
    assert doc.get("name") == "Maxim"


@pytest.mark.asyncio
@pytest.mark.parametrize("doc_name", [name])
async def test_delete_document(test_db, doc_name):
    result = await delete_document(test_db, doc_name)
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize("doc_name", [fail_name])
async def test_fail_delete_document(test_db, doc_name):
    result = await delete_document(test_db, doc_name)
    assert result is False

