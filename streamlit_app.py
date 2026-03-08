import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:8000/api"  # your FastAPI URL
USER_ID = 1  # test user ID
MAX_SESSIONS = 20  # number of sessions to fetch

# Example list of products
PRODUCTS = ["shawarma", "pizza", "burger"]

# ------------------------------
# Function to replace product names with clickable links
# ------------------------------
def render_with_links(text: str) -> str:
    for product in PRODUCTS:
        pattern = re.compile(rf"\b{product}\b", re.IGNORECASE)
        text = pattern.sub(f"[{product}](http://127.0.0.1:8000/products/{product})", text)
    return text.replace("\n\n", "\n")  # normalize double line breaks

# ------------------------------
# Streamlit page config
# ------------------------------
st.set_page_config(page_title="Chat with LLaMA", layout="wide")
st.title("Chat with LLaMA")

# ------------------------------
# Session state initialization
# ------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions_list" not in st.session_state:
    st.session_state.sessions_list = []

# ------------------------------
# Fetch last N sessions for user
# ------------------------------
try:
    response = requests.get(f"{API_URL}/sessions/user/{USER_ID}")
    response.raise_for_status()
    sessions = response.json()
    # take last MAX_SESSIONS sorted by ID descending
    sessions = sorted(sessions, key=lambda x: x["id"], reverse=True)[:MAX_SESSIONS]
    st.session_state.sessions_list = sessions
except requests.RequestException as e:
    st.error(f"Failed to fetch sessions: {e}")
    sessions = []

# ------------------------------
# Sidebar: select session or start new
# ------------------------------
st.sidebar.title("Your Sessions")

# Numbered sessions for UI
if st.session_state.sessions_list:
    # Map display names like "Session 1", "Session 2" → session_id
    session_options = {f"Session {i+1}": s["id"] for i, s in enumerate(st.session_state.sessions_list)}
    
    # Selectbox with numbered sessions
    selected = st.sidebar.selectbox("Select a session", list(session_options.keys()))
    selected_id = session_options[selected]

    # Load messages if session changed
    if st.session_state.session_id != selected_id:
        st.session_state.session_id = selected_id
        try:
            resp = requests.get(f"{API_URL}/messages/session/{selected_id}")
            resp.raise_for_status()
            messages = resp.json()
            st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        except requests.RequestException as e:
            st.error(f"Failed to load messages: {e}")

# Button to start a new session
if st.sidebar.button("Start New Session"):
    payload = {"title": f"Session {len(st.session_state.sessions_list)+1}", "user_id": USER_ID}
    try:
        resp = requests.post(f"{API_URL}/sessions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        st.session_state.session_id = data["id"]
        st.session_state.messages = []
        st.success(f"New session created!")
        st.session_state.sessions_list.insert(0, data)  # prepend to list
    except requests.RequestException as e:
        st.error(f"Failed to create session: {e}")

# ------------------------------
# Display chat messages
# ------------------------------
st.subheader("Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            # Transform assistant message with links
            st.markdown(render_with_links(msg["content"]), unsafe_allow_html=False)
        else:
            st.markdown(msg["content"])

# ------------------------------
# Send a new message
# ------------------------------
if st.session_state.session_id:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # append user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # send to FastAPI
        try:
            resp = requests.post(f"{API_URL}/chat/message", json={
                "session_id": st.session_state.session_id,
                "message": user_input
            })
            resp.raise_for_status()
            assistant_msg = resp.json()["content"]

            # transform product names into links immediately
            assistant_msg_with_links = render_with_links(assistant_msg)

            # append assistant message
            st.session_state.messages.append({"role": "assistant", "content": assistant_msg_with_links})
            with st.chat_message("assistant"):
                st.markdown(assistant_msg_with_links)
        except requests.RequestException as e:
            st.error(f"Failed to get response from server: {e}")