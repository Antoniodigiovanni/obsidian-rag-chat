from fastapi import APIRouter, HTTPException
from app.schemas.models import QueryInput
from app.services.rag_service import get_rag_agent 

router = APIRouter(prefix="/query", tags=["query"])

@router.post("")
def query_rag_system(payload: QueryInput):
    """
    Performs a RAG query using the agent with tool access.
    
    Args:
        payload: Contains the user's question
        
    Returns:
        The agent's response
    """
    try:
        # Get the agent
        agent = get_rag_agent()
        
        # Invoke the agent with the user's question
        response = agent.invoke({"messages": [{"role": "user", "content": payload.question}]})
        
        # Extract the final answer from agent response
        # The exact structure depends on your LangGraph setup
        answer = response["messages"][-1].content if response.get("messages") else str(response)
        
        return {
            "question": payload.question,
            "answer": answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")