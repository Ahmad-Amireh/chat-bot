import streamlit as st
import requests

API_URL = "http://localhost:8000/api/users/login"

st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):

    response = requests.post(
        API_URL,
        json={
            "email": email,
            "password": password
        }
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        st.session_state["token"] = token
        st.success("Login successful!")
        st.switch_page("pages/chat.py")
    else:
        st.error("Invalid email or password")