import streamlit as st
from components.navbar import navbar
from services.auth import require_login
from services import store
from services.auth import require_login

st.set_page_config(page_title="Repairs • ElectroX", layout="wide")
navbar()
user = require_login()  # 🔒
st.title("Repairs")

with st.expander("Create Ticket"):
    device = st.text_input("Device (e.g., iPhone 13)")
    issue = st.text_area("Issue description")
    if st.button("Submit Ticket"):
        t = store.create_repair(user["email"], device, issue)
        st.success(f"Ticket created: {t}")

st.subheader("My Tickets")
df = store.list_repairs(user["email"])
if df.empty:
    st.info("No tickets yet.")
else:
    st.dataframe(df, use_container_width=True)
