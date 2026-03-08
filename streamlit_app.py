import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api"
USER_ID = 1  # test user ID
MAX_SESSIONS = 20  # last N sessions to fetch

st.set_page_config(page_title="Chat with LLaMA", layout="wide")
st.title("Chat with LLaMA")

# ------------------------------
# Session state
# ------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions_list" not in st.session_state:
    st.session_state.sessions_list = []

# ------------------------------
# 1️⃣ Fetch last N sessions for the user
# ------------------------------
try:
    response = requests.get(f"{API_URL}/sessions/user/{USER_ID}")
    response.raise_for_status()
    sessions = response.json()
    # take last MAX_SESSIONS
    sessions = sorted(sessions, key=lambda x: x["id"], reverse=True)[:MAX_SESSIONS]
    st.session_state.sessions_list = sessions
except requests.RequestException as e:
    st.error(f"Failed to fetch sessions: {e}")
    sessions = []

# ------------------------------
# 2️⃣ Sidebar: select session or create new
# ------------------------------
st.sidebar.title("Your Sessions")

# List previous sessions
if st.session_state.sessions_list:
    session_options = {
        f"{s['title']} (ID: {s['id']})": s["id"]
        for s in st.session_state.sessions_list
    }
    selected = st.sidebar.selectbox("Select a session", list(session_options.keys()))
    selected_id = session_options[selected]
    if st.session_state.session_id != selected_id:
        st.session_state.session_id = selected_id
        # Fetch messages for this session
        try:
            resp = requests.get(f"{API_URL}/messages/session/{selected_id}")
            resp.raise_for_status()
            messages = resp.json()
            # store in session state
            st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        except requests.RequestException as e:
            st.error(f"Failed to load messages: {e}")

# Button to start a new session
if st.sidebar.button("Start New Session"):
    payload = {"title": "New Chat", "user_id": USER_ID}
    try:
        resp = requests.post(f"{API_URL}/sessions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        st.session_state.session_id = data["id"]
        st.session_state.messages = []
        st.success(f"New session created! ID: {data['id']}")
        st.experimental_rerun()  # reload sidebar to include new session
    except requests.RequestException as e:
        st.error(f"Failed to create session: {e}")

# ------------------------------
# 3️⃣ Display chat messages
# ------------------------------
st.subheader("Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------------
# 4️⃣ Send a new message
# ------------------------------
if st.session_state.session_id:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Send to FastAPI
        try:
            resp = requests.post(f"{API_URL}/chat/message", json={
                "session_id": st.session_state.session_id,
                "message": user_input
            })
            resp.raise_for_status()
            assistant_msg = resp.json()["content"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
            with st.chat_message("assistant"):
                st.markdown(assistant_msg)
        except requests.RequestException as e:
            st.error(f"Failed to get response from server: {e}")