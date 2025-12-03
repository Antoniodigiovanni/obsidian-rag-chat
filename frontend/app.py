import streamlit as st
import requests
import os
import time

# App Config
st.set_page_config(page_title="ObsiChat", page_icon="🧠")
st.title("🧠 ObsiChat")
st.caption("A RAG-powered chatbot that lets you chat with your Obsidian's Second Brain, powered by a FastAPI backend.")

# Backend Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{BACKEND_URL}/"
QUERY_ENDPOINT = f"{BACKEND_URL}/query"

# Health Check + Wake up the backend if it goes to sleep (free tier...)
with st.spinner("Waking up backend server... this may take up to 2 minutes on Render ⏳"):
    max_retries = 30   # retry for ~30–60 seconds depending on sleep interval
    sleep_seconds = 2

    backend_ready = False
    for _ in range(max_retries):
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "active":
                backend_ready = True
                break
        except requests.exceptions.ConnectionError:
            pass  # backend is still asleep

        time.sleep(sleep_seconds)

if not backend_ready:
    st.error(f"Backend at {BACKEND_URL} is not responding. It may still be waking up, try refreshing the page!")
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