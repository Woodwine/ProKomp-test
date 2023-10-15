from urllib.parse import parse_qs, urlsplit
import pandas
from fastapi import File, Depends
from starlette.requests import Request
import re

from src.db.db_methods import retrieve_one_document
from src.db.database import AsyncIOMotorClient, get_database


async def convert_csv_to_dict(file: File(...)) -> dict:
    """
    Converts csv-file to the dict.
    """
    data_dict = {}
    file_name = file.filename
    doc_name = file_name.split('.')[0]
    data = pandas.read_csv(file.file, index_col=0)
    data.columns = data.columns.str.replace(f"{doc_name}.", '')
    headers = data.columns.to_list()
    rows = data.to_dict("records")
    data_dict["doc_name"] = doc_name
    data_dict["columns"] = headers
    data_dict["rows"] = rows
    return data_dict


def convert_value(value: str) -> float | str:
    """
    Converts a string to a floating point number, if possible.
    """
    try:
        new_val = float(value)
        return new_val
    except ValueError:
        return value


def get_query_params(params: dict, columns: list) -> tuple:
    """
    Converts query params to the dict.
    """
    rows_params = {}
    for key, value in params.items():
        if key in columns:
            new_value = convert_value(value[0])
            if isinstance(new_value, str):
                new_value = re.compile(f'{new_value}', re.IGNORECASE)
                rows_params[key] = new_value
            rows_params[key] = new_value
    sort = params.get('sort')
    sort_params = [(i[1:], -1) if i[0] == '-' else (i, 1) for i in sort] if sort else []
    limit = int(params['limit'][0]) if 'limit' in params else 100

    return rows_params, sort_params, limit


async def query_params(doc_name: str, request: Request, db: AsyncIOMotorClient = Depends(get_database)) -> dict:
    """
    Parses query params.
    """
    doc = await retrieve_one_document(db, doc_name)
    columns = doc['columns']
    url = str(request.url)
    query = urlsplit(url).query
    q_params = parse_qs(query)

    full_params = {}
    rows_params, sort_params, limit = get_query_params(q_params, columns)
    full_params["rows_params"] = rows_params
    full_params['sort'] = sort_params
    full_params["limit"] = limit

    return full_params
