from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from src.db.db_methods import add_document, retrieve_documents, delete_document, \
    get_filtered_document, retrieve_one_document
from src.dataworkers.models import QueryParams
from src.dataworkers.services import convert_csv_to_dict, query_params
from src.db.database import AsyncIOMotorClient, get_database

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/documents',
    tags=['Documents']
)


@router.post('/', response_description='New document added into the database', response_class=HTMLResponse,
             name="add_doc")
async def add_new_document(request: Request, file: UploadFile = File(...),
                           db: AsyncIOMotorClient = Depends(get_database)):
    """
    Adds a new collection with data from the file to the database.
    """
    if not file.filename.endswith('.csv'):
        docs = await retrieve_documents(db)
        return templates.TemplateResponse("home.html",
                                          context={"request": request, "docs": docs,
                                                   "message": "Выберите файл в формате csv"})

    data_dict = await convert_csv_to_dict(file)
    doc = await add_document(db, data_dict)

    if doc and type(doc) != str:
        redirect_url = request.url_for('one_doc', **{"doc_name": doc.get("doc_name")})
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    docs = await retrieve_documents(db)

    if doc and type(doc) == str:
        return templates.TemplateResponse("home.html", context={"request": request, "docs": docs, "message": doc})

    return templates.TemplateResponse("home.html",
                                      context={"request": request, "docs": docs,
                                               "message": "Ошибка в загрузке документа"})


@router.get('/', response_description='Documents retrieved', response_class=HTMLResponse, name="docs_info")
async def get_documents_info(request: Request, db: AsyncIOMotorClient = Depends(get_database)):
    """
    Represents all collections from the database.
    """
    docs = await retrieve_documents(db)

    if docs:
        return templates.TemplateResponse("home.html", context={"request": request, "docs": docs})

    return templates.TemplateResponse("home.html",
                                      context={"request": request, "message": "Нет загруженных документов"})


@router.get('/{doc_name}', response_description='Document data retrieved', response_class=HTMLResponse, name="one_doc")
async def get_data_from_document(request: Request, doc_name: str, query: QueryParams = Depends(query_params),
                                 db: AsyncIOMotorClient = Depends(get_database)):
    """
    Represents all the information from one collection and filters it.
    """
    doc = await get_filtered_document(db, doc_name, query)
    doc_info = await retrieve_one_document(db, doc_name)

    if doc_info:
        return templates.TemplateResponse("one_document.html",
                                          context={"request": request, "doc_info": doc_info, "doc": doc,
                                                   "limit": query.get('limit')})
    else:
        redirect_url = request.url_for('docs_info')
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/{doc_name}', response_description='Document deleted', name="delete_doc")
async def delete_one_document(request: Request, doc_name: str, db: AsyncIOMotorClient = Depends(get_database)):
    """
    Deletes one collection from the database.
    """
    await delete_document(db, doc_name)
    redirect_url = request.url_for('docs_info')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
