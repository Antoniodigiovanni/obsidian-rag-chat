from bson import ObjectId
from app.schemas.models import DocumentResponse

def serialize_doc(doc):
    return DocumentResponse(
        id=str(doc["_id"]),
        content=doc.get("text", "") or doc.get("page_content", ""),
        metadata=doc.get("metadata", {})
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
