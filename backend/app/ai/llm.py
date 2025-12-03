from langchain.chat_models import init_chat_model
from app.core.config import settings

try:
    chat_model = init_chat_model(
        "gpt-4.1", api_key=settings.OPENAI_API_KEY
    )
    print("Successfully initialized the LLM model.")
except Exception as e:
    print(f"Error initializing the LLM model: {e}")
    chat_model = None