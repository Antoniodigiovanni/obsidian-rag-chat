from pymongo import MongoClient
from app.core.config import settings

# Singleton
try:
    client = MongoClient(settings.MONGO_URI)
    # Ping to verify connection
    client.admin.command('ping')
    db = client[settings.DB_NAME]
    collection = db[settings.COLLECTION_NAME]
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise  # fail fast

