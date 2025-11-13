# components/navbar.py
import streamlit as st
from pathlib import Path
from services.auth import current_user

def navbar():
    user = current_user()
    logo_path = Path("assets/logo.png")

    if logo_path.exists():
        logo_html = "<img src='assets/logo.png' class='logo-img' style='border-radius:8px;margin-right:8px;'>"
    else:
        logo_html = "<div class='logo-img' style='width:42px;background:#2563eb;border-radius:8px;'></div>"

    st.markdown(f"""
    <div class="navglass">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:12px;">
          {logo_html}
          <h2 style="margin:0;font-weight:700;color:#0f172a;">ElectroX</h2>
        </div>
        <div style="font-size:.95rem;color:#475569;">
          {("Signed in as <b>"+user['email']+"</b> ("+user['role']+")") if user else "You’re not signed in"}
        </div>
      </div>
      <hr/>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns([4,2,2,2,2,2,2])
    cols[0].page_link("app.py", label="Home", icon="🏠")
    if user:
        cols[1].page_link("pages/_1_inventory.py", label="Inventory", icon="🛍️")
        cols[2].page_link("pages/_2_cart.py", label="Cart", icon="🛒")
        cols[3].page_link("pages/_3_orders.py", label="Orders", icon="📦")
        cols[4].page_link("pages/_4_repairs.py", label="Repairs", icon="🛠️")
        cols[5].page_link("pages/_5_sell_device.py", label="Sell Device", icon="📱")
        if user["role"] == "staff":
            cols[6].page_link("pages/_6_staff_dashboard.py", label="Staff", icon="🧰")
        else:
            cols[6].page_link("pages/_0_login_register.py", label="Account", icon="👤")
    else:
        cols[6].page_link("pages/_0_login_register.py", label="Account", icon="👤")
