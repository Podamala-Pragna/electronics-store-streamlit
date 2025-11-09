import streamlit as st
from pathlib import Path
from services.auth import current_user, logout

def navbar():
    # Logo fallback
    if Path("assets/logo.png").exists():
        logo_html = "<img src='assets/logo.png' height='36'>"
    else:
        logo_html = "<div style='height:36px;width:36px;background:#e5e7eb;border-radius:8px'></div>"

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div style="display:flex;gap:12px;align-items:center">
            {logo_html}
            <h3 style="margin:0;">ElectroX</h3>
          </div>
        </div>
        <hr/>
        """,
        unsafe_allow_html=True
    )

    user = current_user()
    cols = st.columns([4,2,2,2,2,2,2])

    # Always visible
    cols[0].page_link("app.py", label="Home", icon="🏠")

    if user:
        cols[1].page_link("pages/_1_inventory.py", label="Inventory", icon="🛍️")
        cols[2].page_link("pages/_2_cart.py", label="Cart", icon="🛒")
        cols[3].page_link("pages/_3_orders.py", label="Orders", icon="📦")
        cols[4].page_link("pages/_4_repairs.py", label="Repairs", icon="🛠️")
        cols[5].page_link("pages/_5_sell_device.py", label="Sell Device", icon="📱")
        cols[6].page_link("pages/_0_login_register.py", label="Account", icon="👤")
    else:
        # Show just Account while logged out
        cols[6].page_link("pages/_0_login_register.py", label="Account", icon="👤")
