import streamlit as st
import requests
import os
import time


# App Config
st.set_page_config(page_title="ObsiChat", page_icon="🧠")
st.title("🧠 ObsiChat")
st.caption("A RAG-powered chatbot that lets you chat with your Obsidian's Second Brain, powered by a FastAPI backend.")

# Custom CSS for larger tabs
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Backend Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{BACKEND_URL}/"
QUERY_ENDPOINT = f"{BACKEND_URL}/query"
DOCUMENTS_ENDPOINT = f"{BACKEND_URL}/documents/list"
UPLOAD_ENDPOINT = f"{BACKEND_URL}/documents/upload"
RESET_ENDPOINT = f"{BACKEND_URL}/documents/reset"


# Health Check + Wake up the backend if it goes to sleep (free tier...)
with st.spinner("Waking up backend server... this may take up to 2 minutes. Using free tier services has its own limitations 😊"):
    max_retries = 30 
    sleep_seconds = 2

    backend_ready = False
    for _ in range(max_retries):
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "active":
                backend_ready = True
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            pass
        

        time.sleep(sleep_seconds)

if not backend_ready:
    st.error(f"Backend at {BACKEND_URL} is not responding. It may still be waking up, try refreshing the page!")
    st.stop()

tab_chat, tab_docs = st.tabs(["💬 Chat", "📚 Documents"])

with tab_chat:
    chat_container = st.container(height=500) 

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message inside the container
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        # Get response from the backend
        with chat_container.chat_message("assistant"):
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

with tab_docs:
    with st.expander("➕ Add New Document"):
        st.write("Upload text or markdown files to the database.")
        
        # Use a key in session state to reset the uploader
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0

        uploaded_files = st.file_uploader(
            "Choose files", 
            type=["zip", "md"], 
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
        if uploaded_files and st.button("Process Documents"):
            with st.status("Uploading...", expanded=True) as status:
                success_count = 0
                for file in uploaded_files:
                    try:
                        # Backend expects 'files' as the key for List[UploadFile]
                        files_payload = [("files", (file.name, file, file.type))]
                        response = requests.post(UPLOAD_ENDPOINT, files=files_payload)
                        response.raise_for_status()
                        st.write(f"✅ {file.name} uploaded.")
                        success_count += 1
                    except Exception as e:
                        st.error(f"❌ Error with {file.name}: {e}")
                
                if success_count == len(uploaded_files):
                    status.update(label="All files uploaded successfully!", state="complete", expanded=False)
                else:
                    status.update(label="Upload finished with some errors.", state="error", expanded=True)

                # Increment key to reset uploader on next run
                st.session_state.uploader_key += 1
                time.sleep(1) # Give user a moment to see the status
                st.rerun()

    st.divider()

    # --- SECTION 2: READER ---
    col_header, col_refresh, col_reset = st.columns([3, 1, 1])
    col_header.subheader("📚 Knowledge Base")
    
    # Add a manual refresh button in case the backend updates externally
    if col_refresh.button("🔄 Refresh"):
        st.rerun()

    # Reset Database Button
    if col_reset.button("🗑️ Reset DB", type="primary"):
        try:
            res = requests.delete(RESET_ENDPOINT)
            res.raise_for_status()
            st.toast("Database reset successfully!", icon="🗑️")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to reset database: {e}")

    # Fetch documents
    documents = []
    try:
        # Only show spinner if we don't have docs in state yet (optional optimization)
        with st.spinner("Fetching notes..."):
            res = requests.get(DOCUMENTS_ENDPOINT)
            res.raise_for_status()
            documents = res.json() # Expecting list of dicts: [{'id': 1, 'title': 'abc', 'content': '...'}]
    except Exception as e:
        st.error(f"Could not load documents. Check connection to backend.")
    
    if not documents:
        st.info("No documents found. Upload one above!")
    
    else:
        # Create a dictionary for easy lookup: { "Title": {doc_object} }
        # This handles the selection logic cleaner than a loop
        doc_map = {doc.get("title", f"Untitled {i}"): doc for i, doc in enumerate(documents)}
        
        # 1. Selection UI
        selected_title = st.selectbox("Select a note to read:", options=list(doc_map.keys()))

        # 2. Display UI
        if selected_title:
            selected_doc = doc_map[selected_title]
            
            # Use a scrollable container for the content so it fits nicely
            read_container = st.container(height=500, border=True)
            
            with read_container:
                st.markdown(f"## {selected_doc.get('title')}")
                st.caption(f"ID: {selected_doc.get('id', 'N/A')}")
                st.divider()
                st.markdown(selected_doc.get("content", "_(No content)_"))