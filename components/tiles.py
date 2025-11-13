# components/tiles.py
import streamlit as st

def _tile(title: str, subtitle: str, page: str, seed: str):
    with st.container():
        st.markdown('<div class="card tile" style="overflow:hidden">', unsafe_allow_html=True)
        st.image(f"https://picsum.photos/seed/{seed}/1024/640", width="stretch")
        st.markdown(f"**{title}**")
        st.caption(subtitle)
        st.page_link(page, label=f"🎁  Browse {title} →")
        st.markdown("</div>", unsafe_allow_html=True)

def category_tiles():
    col1, col2, col3, col4 = st.columns(4)
    with col1: _tile("Phone", "Shop phone", "pages/_1_inventory.py", "phone")
    with col2: _tile("Laptop", "Shop laptop", "pages/_1_inventory.py", "laptop")
    with col3: _tile("Tablet", "Shop tablet", "pages/_1_inventory.py", "tablet")
    with col4: _tile("Accessory", "Shop accessory", "pages/_1_inventory.py", "accessory")
