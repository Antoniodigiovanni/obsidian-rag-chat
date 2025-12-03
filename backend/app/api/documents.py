from fastapi import APIRouter, HTTPException
from typing import List
from app.db.vectorstore import vector_store
from app.db.mongodb import collection
from app.schemas.models import DocumentInput, DocumentResponse
from app.utils.serializers import serialize_doc
from bson import ObjectId
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/index")
def index_document(payload: DocumentInput):
    """
    Splits text into chunks, embeds them, and saves to MongoDB.
    """
    try:
        # 1. Text Splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.create_documents(
            texts=[payload.content], 
            metadatas=[payload.metadata]
        )

        # 2. Add to Vector Store
        # MongoDBAtlasVectorSearch handles embedding generation automatically here
        ids = vector_store.add_documents(docs)
        
        return {"message": f"Successfully indexed {len(ids)} chunks.", "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[DocumentResponse])
def list_documents(limit: int = 10):
    """
    Reads the vector database. Lists raw documents from the collection.
    """
    try:
        # Using PyMongo directly for efficient reading without embedding logic
        cursor = collection.find({}).limit(limit)
        results = [serialize_doc(doc) for doc in cursor]
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    """
    Deletes a specific document chunk by its MongoDB _id.
    """
    try:
        result = collection.delete_one({"_id": ObjectId(doc_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset")
def reset_database():
    """
    Resets the Vector DB by deleting all documents in the collection.
    WARNING: This is irreversible.
    """
    try:
        result = collection.delete_many({})
        return {"message": f"Database reset. Deleted {result.deleted_count} documents."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))