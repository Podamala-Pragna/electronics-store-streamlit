import streamlit as st
from components.navbar import navbar
from services.auth import require_login
from services import store
from services.auth import require_login

st.set_page_config(page_title="Sell Your Device • ElectroX", layout="wide")
navbar()
user = require_login()  # 🔒
st.title("Sell your device")

with st.form("sell_form"):
    device = st.text_input("Device (model)")
    brand = st.text_input("Brand")
    condition = st.selectbox("Condition", ["Excellent","Very Good","Good","Fair"])
    price = st.number_input("Expected price (₹)", min_value=0, step=500)
    desc = st.text_area("Notes")
    img = st.file_uploader("Upload photo", type=["jpg","jpeg","png"])
    submitted = st.form_submit_button("Submit Request")

if submitted:
    img_path = store.save_upload(img) if img else ""
    req_id = store.create_sell_request(user["email"], device, brand, condition, price, desc, img_path)
    st.success(f"Request submitted: {req_id}")

st.subheader("My Sell Requests")
df = store.list_sell_requests()
mine = df[df["email"] == user["email"]]
if mine.empty:
    st.info("No requests yet.")
else:
    st.dataframe(mine, use_container_width=True)
