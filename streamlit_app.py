import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api"
USER_ID = 1

st.set_page_config(page_title="Chat with LLaMA", layout="wide")
st.title("Chat with LLaMA")

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create session if not exists
if st.session_state.session_id is None:
    if st.button("Start New Session"):
        response = requests.post(f"{API_URL}/sessions", json={"title": "New Chat", "user_id": USER_ID})
        if response.status_code == 201:
            data = response.json()
            st.session_state.session_id = data["id"]
            st.session_state.messages = []
            st.success(f"Session created! ID: {st.session_state.session_id}")
        else:
            st.error("Failed to create session.")

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Send message
if st.session_state.session_id:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Append user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Send to FastAPI
        response = requests.post(f"{API_URL}/chat/message", json={
            "session_id": st.session_state.session_id,
            "message": user_input
        })

        if response.status_code == 200:
            assistant_msg = response.json()["content"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
            with st.chat_message("assistant"):
                st.markdown(assistant_msg)
        else:
            st.error("Failed to get response from server.")