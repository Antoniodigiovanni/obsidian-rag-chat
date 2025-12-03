# ObsiChat

## Description

This project is a chat application that leverages a Retrieval-Augmented Generation (RAG) agent to answer questions.
The knowledge base is a personal Obsidian Vault functioning as a so called "Second Brain" (mocked for this example). 

## Architecture

The application is split into two main parts:

### Frontend

The user interface is a simple web application built with **Streamlit**. It provides a chat interface for users to interact with the backend RAG agent.

### Backend

The backend is a Python service built with **FastAPI**. It exposes a REST API that serves the RAG agent. 

For efficient document retrieval, it connects to **MongoDB Atlas Vector Search** to find relevant information before generating a response.

## Getting Started

...