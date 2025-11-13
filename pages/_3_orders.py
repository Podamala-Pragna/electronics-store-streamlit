# pages/_3_orders.py
import streamlit as st
from components.navbar import navbar
from services.auth import require_login, is_staff
from services import store

st.set_page_config(page_title="Orders • ElectroX", layout="wide")
navbar()
user = require_login()

st.title("Orders")

if is_staff(user):
    st.caption("Staff view — see all orders, approve or decline.")
    colf1, colf2, colf3 = st.columns([3,2,2])
    email_filter = colf1.text_input("Filter by customer email (optional)", key="ord_f_email")
    status_filter = colf2.selectbox("Status", ["All", "Pending Approval", "Approved", "Declined"], key="ord_f_status")
    refresh = colf3.button("Refresh", key="ord_f_refresh")

    df = store.list_orders(email=email_filter or None, for_customer=False)
    if status_filter != "All":
        df = df[df["status"] == status_filter]

    if df.empty:
        st.info("No orders found.")
    else:
        for _, row in df.iterrows():
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3,2,2,2,3])
                c1.markdown(f"**{row['order_id']}**")
                c2.markdown(f"₹ {int(row['total']):,}")
                c3.markdown(f"{row['email']}")
                c4.markdown(f"**{row['status']}**")
                a1, a2 = c5.columns(2)
                if a1.button("Approve", key=f"ap_{row['order_id']}") and row["status"] != "Approved":
                    if store.approve_order(row["order_id"]):
                        st.success(f"Approved {row['order_id']}")
                        st.rerun()
                if a2.button("Decline", key=f"dc_{row['order_id']}") and row["status"] != "Declined":
                    if store.decline_order(row["order_id"]):
                        st.warning(f"Declined {row['order_id']}")
                        st.rerun()

        st.markdown("#### All orders")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
else:
    st.caption("Customer view — you can see only your **Approved** orders.")
    df = store.list_orders(email=user["email"], for_customer=True)
    if df.empty:
        st.info("No approved orders yet. Once staff approves, your orders will appear here.")
    else:
        st.dataframe(
            df[["order_id","total","payment_method","status","created_at"]].reset_index(drop=True),
            use_container_width=True
        )
