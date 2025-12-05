import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Obsidian Vault RAG"

    MONGO_URI: str = os.getenv("MONGO_URI")
    DB_NAME: str = "obsidian_rag"
    CHUNKS_COLLECTION_NAME: str = "chunks"
    DOCUMENTS_COLLECTION_NAME: str = "documents"
    INDEX_NAME: str = "vector_index"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()
