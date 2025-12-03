from langchain.tools import tool
from langchain.agents import create_agent
from langchain.tools import tool

from app.db.vectorstore import vector_store
from app.ai.llm import chat_model

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

def get_rag_agent():
    """Creates and returns the RAG agent."""
    tools = [retrieve_context]
    prompt = (
        "You have access to a tool that retrieves information from a Second Brain stored in an Obsidian Vault. "
        "Use the tool to help answer user queries."
    )
    return create_agent(chat_model, tools, system_prompt=prompt)
