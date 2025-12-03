from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

try:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=settings.OPENAI_API_KEY
    )
    print("Successfully initialized Embedding model.")
except Exception as e:
    print(f"Error initializing the embedding model: {e}")
    embeddings = None