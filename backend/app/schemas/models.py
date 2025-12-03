from pydantic import BaseModel, Field
from typing import List, Dict

class DocumentInput(BaseModel):
    content: str
    metadata: Dict = {}

class QueryInput(BaseModel):
    question: str

class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: dict


class QueryResponse(BaseModel):
    question: str
    answer: str
    