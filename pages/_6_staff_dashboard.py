import streamlit as st
from components.navbar import navbar
from services.auth import require_role
from services import store
from services.auth import require_role

st.set_page_config(page_title="Staff • ElectroX", layout="wide")
navbar()
user = require_role(["staff","admin"])  # 🔒 staff/admin only
st.title("Staff Dashboard")

tab1, tab2, tab3 = st.tabs(["Sell Requests","Products","Orders"])

# Sell Requests
with tab1:
    st.subheader("Sell Requests")
    status = st.selectbox("Filter", ["All","Pending","Converted","Rejected"])
    df = store.list_sell_requests(None if status=="All" else status)
    st.dataframe(df, use_container_width=True)
    st.markdown("### Actions")
    req_id = st.text_input("Request ID")
    act = st.selectbox("Action", ["Approve → Convert to Product","Reject"])
    price = st.number_input("List Price (₹)", min_value=0, step=500, value=5000)
    stock = st.number_input("Stock", min_value=1, step=1, value=1)
    if st.button("Apply"):
        if act.startswith("Approve"):
            pid = store.convert_sell_request_to_product(req_id, price, stock, created_by=user["email"])
            st.success(f"Converted to product #{pid}" if pid else "Invalid request id")
        else:
            ok = store.update_sell_request(req_id, "Rejected")
            st.success("Rejected" if ok else "Invalid request id")

# Products
with tab2:
    st.subheader("Products")
    dfp = store.list_products()
    st.dataframe(dfp, use_container_width=True)
    pid = st.number_input("Product ID to update", min_value=1, step=1)
    new_price = st.number_input("New price (₹)", min_value=0, step=500)
    new_stock = st.number_input("New stock", min_value=0, step=1)
    if st.button("Update Product"):
        ok = store.update_product(int(pid), price=float(new_price), stock=int(new_stock))
        st.success("Updated" if ok else "Product not found")

# Orders
with tab3:
    st.subheader("Orders")
    o = store.list_orders()
    st.dataframe(o, use_container_width=True)
    oid = st.text_input("Order ID")
    new_status = st.selectbox("Set status", ["Paid","Pending","Shipped","Delivered","Cancelled"])
    if st.button("Update Status"):
        ok = store.update_order_status(oid, new_status)
        st.success("Updated" if ok else "Order not found")
