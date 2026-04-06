# streamlit_app/pages/products.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001/api/products"

if "token" not in st.session_state:
    st.error("Please login first")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.set_page_config(page_title="Products", layout="wide")
st.title("Products")

# ------------------------------
# Load products
# ------------------------------
resp = requests.get(API_URL)
products = resp.json() if resp.status_code == 200 else []

# ------------------------------
# Display products
# ------------------------------
st.subheader("Current Menu")
if products:
    for p in products:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        col1.write(f"**{p['name']}**")
        col2.write(f"${p['price']:.2f}")
        if col3.button("Edit", key=f"edit_{p['id']}"):
            st.session_state[f"editing_{p['id']}"] = True
        if col4.button("Delete", key=f"del_{p['id']}"):
            requests.delete(f"{API_URL}/{p['id']}")
            st.rerun()

        if st.session_state.get(f"editing_{p['id']}"):
            with st.form(key=f"form_{p['id']}"):
                new_name = st.text_input("Name", value=p["name"])
                new_price = st.number_input("Price", value=p["price"], min_value=0.0, step=0.5)
                if st.form_submit_button("Save"):
                    requests.put(f"{API_URL}/{p['id']}", json={"name": new_name, "price": new_price})
                    st.session_state[f"editing_{p['id']}"] = False
                    st.rerun()
else:
    st.info("No products yet.")

# ------------------------------
# Add new product
# ------------------------------
st.subheader("Add Product")
with st.form("add_product"):
    name = st.text_input("Name")
    price = st.number_input("Price", min_value=0.0, step=0.5)
    if st.form_submit_button("Add"):
        requests.post(API_URL, json={"name": name, "price": price})
        st.rerun()