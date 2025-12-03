import os

# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = "vault"
# COLLECTION_NAME = "obsidian_vault"
# INDEX_NAME = "vector_index"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Obsidian Vault RAG"
    API_V1_STR: str = "/api/v1"

    MONGO_URI: str = os.getenv("MONGO_URI")
    DB_NAME: str = "vault"
    COLLECTION_NAME: str = "obsidian_vault"
    INDEX_NAME: str = "vector_index"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()
