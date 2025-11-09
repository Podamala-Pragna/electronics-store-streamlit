import streamlit as st
from pathlib import Path
from components.navbar import navbar
from services.auth import current_user

st.set_page_config(page_title="ElectroX", layout="wide", page_icon="⚡")

# init cart once
if "cart" not in st.session_state:
    st.session_state["cart"] = {}

navbar()

user = current_user()

col1, col2 = st.columns([2, 3])
with col1:
    st.title("Buy smart. Save more.")
    st.write("Certified pre-owned phones, laptops & tablets with warranty and easy returns.")
    if user:
        st.page_link("pages/_1_inventory.py", label="Browse Inventory →", icon="🛍️")
    else:
        st.page_link("pages/_0_login_register.py", label="Login to start shopping →", icon="🔐")

with col2:
    banner = Path("assets/banner.jpg")
    if banner.exists():
        st.image(str(banner), width="stretch")
    else:
        st.image("https://picsum.photos/1200/400", width="stretch")
        st.info("Add your own hero image at **assets/banner.jpg** to replace this placeholder.")

st.markdown("### Why ElectroX?")
b1, b2, b3 = st.columns(3)
b1.markdown("**14-point Quality Check**")
b2.markdown("**Up to 6-Month Warranty**")
b3.markdown("**Easy Returns**")
