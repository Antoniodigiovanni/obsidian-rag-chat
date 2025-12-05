from typing import List
from bson import ObjectId
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from pymongo.collection import Collection
import uuid
from datetime import datetime, timezone

from app.db.vectorstore import vector_store
from app.schemas.models import DocumentResponse, DocumentInput

import os
import shutil
import tempfile
import zipfile
import hashlib
from typing import List, Union
from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import ObsidianLoader
from langchain_core.documents import Document

from app.db.mongodb import documents_collection
from app.db.vectorstore import vector_store
from app.schemas.models import DocumentResponse, DocumentInput

def _serialize_doc(doc_data: dict) -> DocumentResponse:
    """Converts a MongoDB document to a Pydantic response model."""
    return DocumentResponse(
        id=str(doc_data["_id"]),
        title=doc_data.get("title", "Untitled"),
        content=doc_data.get("full_content") or doc_data.get("text") or doc_data.get("page_content", ""),
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

async def process_and_index_files(files: List[UploadFile]):
    """
    Processes uploaded files (Markdown or Zip).
    Extracts metadata, checks for duplicates, and indexes new documents.
    """
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            if file.filename.endswith(".zip"):
                # Handle Zip (Obsidian Vault)
                extract_dir = os.path.join(temp_dir, "vault")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                loader = ObsidianLoader(extract_dir)
                documents = loader.load()
            else:
                # Handle Single Markdown File
                # ObsidianLoader expects a directory, so we point it to the temp_dir
                # But we need to make sure it only loads this file or we treat it as a vault of 1 file
                # Actually, ObsidianLoader scans the directory. 
                # If we just have one file in temp_dir, it should work.
                # However, if we have multiple uploaded files, we might want to isolate them.
                # For simplicity, let's process one by one in isolated subdirs if needed, 
                # but here we are in a loop.
                # Let's create a specific subdir for this file to be safe.
                single_file_dir = os.path.join(temp_dir, f"single_{uuid.uuid4()}")
                os.makedirs(single_file_dir)
                shutil.move(file_path, os.path.join(single_file_dir, file.filename))
                
                loader = ObsidianLoader(single_file_dir)
                documents = loader.load()

            # Process loaded documents
            for doc in documents:
                result = _index_single_document(doc)
                results.append(result)
                
    return results

def _index_single_document(doc: Document):
    try:
        # 2. Add title to metadata
        source = doc.metadata.get("source", "")
        title = os.path.basename(source)
        if title.endswith(".md"):
            title = title[:-3]
        doc.metadata["title"] = title

        # 1. GENERATE HASH
        content_hash = hashlib.sha256(doc.page_content.encode('utf-8')).hexdigest()

        # 4. CHECK FOR DUPLICATES
        existing_doc = documents_collection.find_one({"content_hash": content_hash})
        
        if existing_doc:
            # 5. Check path metadata if hash is not there? 
            # User said: "If the hash is not there, understand if the path metadata is the same, or maybe check this before the hash"
            # If hash IS there, it's a duplicate content.
            # We can check if it's the SAME file (path) or just same content.
            # For now, if content is same, we skip.
            return {
                "message": "Document already exists. Skipped.",
                "doc_id": str(existing_doc["_id"]),
                "status": "skipped",
                "file": title
            }

        # 6. If new, store with uuid and chunk
        doc_id = str(uuid.uuid4())
        
        parent_doc = {
            "_id": doc_id,
            "content_hash": content_hash,
            "title": title,
            "full_content": doc.page_content,
            "created_at": datetime.now(timezone.utc),
            "metadata": doc.metadata
        }
        
        # Insert into MongoDB
        documents_collection.insert_one(parent_doc)

        # Chunk and Embed
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # We can also use MarkdownHeaderTextSplitter if we want better structure
        
        chunks = text_splitter.split_documents([doc])
        
        # Add parent ID to chunks metadata
        for chunk in chunks:
            chunk.metadata["parent_id"] = doc_id
            chunk.metadata["content_hash"] = content_hash
        
        # 7. Store embedding's chunk in vector store
        vector_store.add_documents(chunks)
        
        return {
            "message": "Indexed successfully", 
            "doc_id": doc_id,
            "status": "indexed",
            "file": title
        }

    except Exception as e:
        print(f"Error processing document {doc.metadata.get('source', 'unknown')}: {e}")
        return {
            "message": f"Error: {str(e)}",
            "status": "error",
            "file": doc.metadata.get("title", "unknown")
        }