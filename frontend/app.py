import streamlit as st
import requests
import os

# App Config
st.set_page_config(page_title="ObsiChat", page_icon="🧠")
st.title("🧠 ObsiChat")
st.caption("A RAG-powered chatbot that lets you chat with your Obsidian's Second Brain, powered by a FastAPI backend.")

# Backend Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{BACKEND_URL}/"
QUERY_ENDPOINT = f"{BACKEND_URL}/query"

# API Health Check
try:
    response = requests.get(HEALTH_ENDPOINT)
    if response.status_code != 200 or response.json().get("status") != "active":
        st.error("Backend is not running or not healthy. Please start the FastAPI server.")
        st.stop()
except requests.exceptions.ConnectionError:
    st.error(f"Could not connect to the backend at {BACKEND_URL}. Please ensure it's running.")
    st.stop()

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from the backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(QUERY_ENDPOINT, json={"question": prompt})
                response.raise_for_status()

                response_data = response.json()
                full_response = response_data.get("answer", "Sorry, I didn't get a valid answer.")

                st.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except requests.exceptions.RequestException as e:
                error_message = f"Failed to get a response from the backend: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})