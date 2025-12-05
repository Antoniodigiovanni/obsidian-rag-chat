from pymongo.errors import CollectionInvalid, OperationFailure
from app.core.config import settings
from app.db.mongodb import client

def init_db():
    """
    Initialize the database:
    - Create collection if it doesn't exist.
    - Create vector search index if it doesn't exist.
    """
    try:
        db = client[settings.DB_NAME]
        
        # 1. Create Collections
        existing_collections = db.list_collection_names()

        if settings.CHUNKS_COLLECTION_NAME in existing_collections:
            print(f"Collection '{settings.CHUNKS_COLLECTION_NAME}' already exists.")
        else:
            try:
                db.create_collection(settings.CHUNKS_COLLECTION_NAME)
                print(f"Collection '{settings.CHUNKS_COLLECTION_NAME}' created successfully.")
            except CollectionInvalid as e:
                print(f"Error creating collection: {e}")
                return

        if settings.DOCUMENTS_COLLECTION_NAME in existing_collections:
            print(f"Collection '{settings.DOCUMENTS_COLLECTION_NAME}' already exists.")
        else:
            try:
                db.create_collection(settings.DOCUMENTS_COLLECTION_NAME)
                print(f"Collection '{settings.DOCUMENTS_COLLECTION_NAME}' created successfully.")
            except CollectionInvalid as e:
                print(f"Error creating collection: {e}")
                return

        collection = db[settings.CHUNKS_COLLECTION_NAME]

        # 2. Create Vector Search Index
        # Field name for embeddings. 
        embedding_field = "embedding" 
        
        index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": embedding_field,
                    "numDimensions": 3072, # text-embedding-3-large
                    "similarity": "cosine"
                }
            ]
        }

        print(f"Checking for index '{settings.INDEX_NAME}'...")
        
        try:
            # list_search_indexes returns a cursor
            existing_indexes = list(collection.list_search_indexes(settings.INDEX_NAME))
            if existing_indexes:
                print(f"Index '{settings.INDEX_NAME}' already exists.")
            else:
                print(f"Creating index '{settings.INDEX_NAME}'...")
                model = {
                    "definition": index_definition,
                    "name": settings.INDEX_NAME,
                    "type": "vectorSearch"
                }
                collection.create_search_index(model=model)
                print(f"Index '{settings.INDEX_NAME}' creation initiated.")
                
        except OperationFailure as e:
            print(f"Operation failed when checking/creating index: {e}")
        except Exception as e:
            print(f"Error managing search index: {e}")

    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
