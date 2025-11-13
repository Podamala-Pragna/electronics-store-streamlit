# components/footer.py
import streamlit as st

def footer():
    st.markdown("""
    <div class="footer">
      <div style="display:flex;gap:24px;flex-wrap:wrap;">
        <div style="min-width:220px">
          <strong>ElectroX</strong><br>
          <span class="muted">Certified pre-owned electronics.</span><br><br>
          <div class="muted">support@electrox.store</div>
        </div>
        <div style="min-width:160px">
          <strong>Shop</strong><br>
          <a class="btn-link" href="?page=pages/_1_inventory.py">Inventory</a><br>
          <a class="btn-link" href="?page=pages/_5_sell_device.py">Sell your device</a><br>
          <a class="btn-link" href="?page=pages/_3_orders.py">Orders</a>
        </div>
        <div style="min-width:160px">
          <strong>Support</strong><br>
          <a class="btn-link" href="?page=pages/_4_repairs.py">Repairs</a><br>
          <span class="muted">Warranty & Returns</span><br>
          <span class="muted">FAQ</span>
        </div>
      </div>
      <div style="margin-top:16px" class="muted">© 2025 ElectroX</div>
    </div>
    """, unsafe_allow_html=True)
