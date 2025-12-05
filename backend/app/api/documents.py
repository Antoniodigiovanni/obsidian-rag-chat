from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.db.vectorstore import vector_store
from app.db.mongodb import chunks_collection, documents_collection
from app.schemas.models import DocumentInput, DocumentResponse
from app.utils.serializers import serialize_doc
from bson import ObjectId
from app.services.document_service import process_and_index_files

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Uploads and processes files (Markdown or Zip).
    Extracts metadata, checks for duplicates, and indexes new documents.
    """
    try:
        results = await process_and_index_files(files)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[DocumentResponse])
def list_documents(limit: int = 10):
    """
    Reads the vector database. Lists raw documents from the collection.
    """
    try:
        # Reads documents using PyMongo directly
        cursor = documents_collection.find({}).limit(limit)
        results = [serialize_doc(doc) for doc in cursor]
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset")
def reset_database():
    """
    Resets the DB by deleting all documents in the collection.
    WARNING: This is irreversible.
    """
    try:
        result = documents_collection.delete_many({})
        # Also clear vector store if possible, or chunks collection
        chunks_collection.delete_many({})
        return {"message": f"Database reset. Deleted {result.deleted_count} documents."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    """
    Deletes a specific document by its MongoDB _id.
    """
    try:
        result = documents_collection.delete_one({"_id": ObjectId(doc_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))