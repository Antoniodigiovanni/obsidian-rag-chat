from fastapi import APIRouter
from app.db.mongodb import client

router = APIRouter(prefix="", tags=["health"])

@router.get("/")
def health_check():
    """General service health check"""
    return {"status": "active", "service": "RAG Backend"}

@router.get("/mongodb")
def mongodb_health():
    """Check MongoDB connection using the ping command"""
    try:
        client.admin.command("ping")
        return {"status": "ok", "message": "MongoDB connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"MongoDB connection failed: {str(e)}"}