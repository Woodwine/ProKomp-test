from typing import List, Optional
from beanie import Document
from pydantic import Field, BaseModel


class DocumentInfo(Document):
    """
    Represents one document in documents collection.
    """
    doc_name: str = Field(max_length=500)
    columns: List[str]

    class Settings:
        name = 'documents'


class QueryParams(BaseModel):
    """
    Represents query params object.
    """
    rows_params: Optional[dict] = None
    sort: Optional[dict] = None
    limit: Optional[int] = 50
