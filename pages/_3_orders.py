import streamlit as st
from components.navbar import navbar
from services.auth import require_login
from services import store
from services.auth import require_login

st.set_page_config(page_title="Orders • ElectroX", layout="wide")
navbar()
user = require_login()  # 🔒
st.title("My Orders")

df = store.list_orders(user["email"])
if df.empty:
    st.info("No orders found.")
else:
    st.dataframe(df, use_container_width=True)
