from langchain_mongodb import MongoDBAtlasVectorSearch
from app.core.config import settings
from app.db.mongodb import collection
from app.ai.embeddings import embeddings

try:
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=settings.INDEX_NAME
    )
    print("Successfully initialized MongoDB Atlas Vector Search.")
except Exception as e:
    print(f"Error initializing vector store: {e}")
    vector_store = None