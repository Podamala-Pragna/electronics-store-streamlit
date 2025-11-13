# pages/_4_repairs.py
import streamlit as st
from components.navbar import navbar
from services.auth import require_login, is_staff
from services import store

st.set_page_config(page_title="Repairs • ElectroX", layout="wide")
navbar()
user = require_login()
st.title("Repairs")

if is_staff(user):
    st.info("You’re staff. Use the Staff Dashboard to manage all repair tickets.")
    st.page_link("pages/_6_staff_dashboard.py", label="Open Staff Dashboard →", icon="🧰")

st.subheader("Create a repair ticket")

col1, col2 = st.columns(2)
with col1:
    device_type = st.selectbox("Device type", ["Phone","Laptop","Tablet","Accessory","Other"], key="rp_devtype")
    device = st.text_input("Device model (e.g., iPhone 12, Dell XPS 13)", key="rp_device")
    issue = st.text_area("Describe the issue", key="rp_issue")
with col2:
    preferred_time = st.text_input("Preferred visit time (e.g., 2025-11-12 17:30 or 'Saturday evening')", key="rp_pref")
    photo = st.file_uploader("Upload a device photo (optional)", type=["jpg","jpeg","png"], key="rp_img")

if st.button("Submit", key="rp_submit"):
    img_path = store.save_upload(photo) if photo else ""
    if not device:
        st.error("Please enter your device model.")
    else:
        ticket = store.create_repair(
            email=user["email"],
            device_type=device_type,
            device=device,
            issue=issue,
            preferred_time=preferred_time,
            image_path=img_path
        )
        st.success(f"Ticket created: {ticket}. Our staff will confirm a schedule or propose a new time.")
        st.rerun()

st.subheader("Your repair tickets")
df = store.list_repairs(email=user["email"], all_for_staff=False)
if df.empty:
    st.info("No tickets yet.")
else:
    st.dataframe(
        df[["ticket","device_type","device","status","preferred_time","scheduled_time","contacted","created_at"]]
          .reset_index(drop=True),
        use_container_width=True
    )
