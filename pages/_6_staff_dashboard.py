# pages/_6_staff_dashboard.py
import streamlit as st
from components.navbar import navbar
from services.auth import require_role, current_user
from services import store

st.set_page_config(page_title="Staff Dashboard • ElectroX", layout="wide")
navbar()
user = require_role(["staff"])

st.title("Staff Dashboard")

# ---------------- ORDERS ----------------
st.header("Orders")
colf1, colf2, colf3 = st.columns([3,2,2])
email_filter = colf1.text_input("Filter by customer email (optional)", key="s_ord_email")
status_filter = colf2.selectbox("Status", ["All", "Pending Approval", "Approved", "Declined"], key="s_ord_status")
refresh_orders = colf3.button("Refresh", key="s_ord_refresh")

odf = store.list_orders(email=email_filter or None, for_customer=False)
if status_filter != "All":
    odf = odf[odf["status"] == status_filter]

if odf.empty:
    st.info("No orders.")
else:
    for _, row in odf.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3,2,2,2,3])
            c1.markdown(f"**{row['order_id']}**")
            c2.markdown(f"₹ {int(row['total']):,}")
            c3.markdown(f"{row['email']}")
            c4.markdown(f"**{row['status']}**")
            a1, a2 = c5.columns(2)
            if a1.button("Approve", key=f"s_ap_{row['order_id']}") and row["status"] != "Approved":
                if store.approve_order(row["order_id"]):
                    st.success(f"Approved {row['order_id']}")
                    st.rerun()
            if a2.button("Decline", key=f"s_dc_{row['order_id']}") and row["status"] != "Declined":
                if store.decline_order(row["order_id"]):
                    st.warning(f"Declined {row['order_id']}")
                    st.rerun()

    st.markdown("#### All orders")
    st.dataframe(odf.reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ---------------- REPAIRS ----------------
st.header("Repairs")

fc1, fc2, fc3 = st.columns([3,2,2])
email_f = fc1.text_input("Filter by customer email (optional)", key="s_rp_email")
status_f = fc2.selectbox("Status", ["All","In Progress","Scheduled","Completed","Declined"], key="s_rp_status")
refresh = fc3.button("Refresh", key="s_rp_refresh")

rdf = store.list_repairs(all_for_staff=True)
if email_f:
    rdf = rdf[rdf["email"].str.contains(email_f, case=False, na=False)]
if status_f != "All":
    rdf = rdf[rdf["status"] == status_f]

if rdf.empty:
    st.info("No repair tickets.")
else:
    for _, r in rdf.iterrows():
        with st.container():
            st.markdown("---")
            top = st.columns([3,2,2,2,3])
            top[0].markdown(f"**{r['ticket']}** — {r['device_type']} • {r['device']}")
            top[1].markdown(f"**Status:** {r['status']}")
            top[2].markdown(f"**Customer:** {r['email']}")
            top[3].markdown(f"**Preferred:** {r['preferred_time'] or '—'}")
            if r.get("image_path"):
                top[4].image(r["image_path"], width="stretch")
            else:
                top[4].write("No image")

            st.caption(f"Issue: {r['issue'] or '—'}")

            c1, c2, c3, c4, c5 = st.columns([2,2,3,3,3])

            # Status quick buttons
            if c1.button("Approve", key=f"rp_ok_{r['ticket']}") and r["status"] != "Scheduled":
                store.update_repair_status(r["ticket"], "Scheduled")
                st.success(f"{r['ticket']} approved (use Schedule to set time).")
                st.rerun()
            if c1.button("Complete", key=f"rp_done_{r['ticket']}") and r["status"] != "Completed":
                store.update_repair_status(r["ticket"], "Completed")
                st.success(f"{r['ticket']} marked Completed.")
                st.rerun()
            if c1.button("Decline", key=f"rp_dec_{r['ticket']}") and r["status"] != "Declined":
                store.update_repair_status(r["ticket"], "Declined")
                st.warning(f"{r['ticket']} declined.")
                st.rerun()

            # Schedule / Reschedule
            new_time = c2.text_input("Set schedule (time string)", value=r["scheduled_time"], key=f"rp_sch_{r['ticket']}")
            notes = c3.text_input("Staff notes (optional)", key=f"rp_note_{r['ticket']}")
            if c2.button("Save schedule", key=f"rp_sch_btn_{r['ticket']}"):
                store.schedule_repair_time(r["ticket"], new_time, staff_notes=notes)
                st.success("Schedule updated.")
                st.rerun()

            # Contacted + Assign
            contacted_val = bool(r["contacted"])
            contacted = c4.toggle("Customer contacted", value=contacted_val, key=f"rp_contact_{r['ticket']}")
            if contacted != contacted_val:
                store.set_repair_contacted(r["ticket"], contacted)
                st.info("Contact status updated.")
                st.rerun()

            assign_label = r["assigned_to"] or "(unassigned)"
            if c5.button(f"Assign to me ({assign_label})", key=f"rp_assign_{r['ticket']}"):
                store.assign_repair(r["ticket"], user["email"])
                st.success(f"Assigned {r['ticket']} to {user['email']}")
                st.rerun()

    st.markdown("#### All repair tickets")
    st.dataframe(
        rdf[["ticket","email","device_type","device","status","preferred_time","scheduled_time","contacted","assigned_to","created_at"]]
           .reset_index(drop=True),
        use_container_width=True
    )
