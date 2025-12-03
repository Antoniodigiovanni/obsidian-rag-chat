from typing import List
from bson import ObjectId
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo.collection import Collection

from app.db.vectorstore import vector_store
from app.schemas.models import DocumentResponse, DocumentInput

def _serialize_doc(doc_data: dict) -> DocumentResponse:
    """Converts a MongoDB document to a Pydantic response model."""
    return DocumentResponse(
        id=str(doc_data["_id"]),
        content=doc_data.get("text", "") or doc_data.get("page_content", ""),
        metadata=doc_data.get("metadata", {})
    )

def index_document(payload: DocumentInput) -> List[str]:
    """Splits text, creates documents, and adds them to the vector store."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(texts=[payload.content], metadatas=[payload.metadata])
    ids = vector_store.add_documents(docs)
    return ids

def list_documents_from_db(collection: Collection, limit: int) -> List[DocumentResponse]:
    """Lists raw documents directly from the MongoDB collection."""
    cursor = collection.find({}).limit(limit)
    return [_serialize_doc(doc) for doc in cursor]

def delete_document_from_db(collection: Collection, doc_id: str) -> int:
    """Deletes a document by its ID and returns the count of deleted items."""
    result = collection.delete_one({"_id": ObjectId(doc_id)})
    return result.deleted_count

def reset_db_collection(collection: Collection) -> int:
    """Deletes all documents in the collection."""
    result = collection.delete_many({})
    return result.deleted_count