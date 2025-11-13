# app.py
import streamlit as st
from pathlib import Path
from components.navbar import navbar
from components.theme import inject_theme
from components.tiles import category_tiles
from components.footer import footer
from services.auth import current_user
from services import store

st.set_page_config(page_title="ElectroX", layout="wide", page_icon="⚡")
inject_theme()

# init cart once
if "cart" not in st.session_state:
    st.session_state["cart"] = {}

# handle deferred navigation
goto = st.session_state.pop("__goto__", None)
if goto:
    try: st.switch_page(goto)
    except Exception: pass

navbar()
user = current_user()

# --- HERO
left, right = st.columns([2,3], vertical_alignment="center")
with left:
    st.markdown("<h1 style='font-size:3rem;line-height:1.05'>Buy smart. Save more.</h1>", unsafe_allow_html=True)
    st.write("Certified pre-owned phones, laptops & tablets with warranty and easy returns.")
    if user:
        st.page_link("pages/_1_inventory.py", label="Browse Inventory →", icon="🛍️")
    else:
        st.page_link("pages/_0_login_register.py", label="Login to start shopping →", icon="🔐")

with right:
    banner = Path("assets/banner.jpg")
    st.image(str(banner) if banner.exists() else "https://picsum.photos/1200/400", width="stretch")

# --- TRUST STRIP
st.markdown("### Why ElectroX?")
a, b, c = st.columns(3)
a.markdown('<div class="card"><b>14-point Quality Check</b><br><span class="muted">Every device inspected and certified.</span></div>', unsafe_allow_html=True)
b.markdown('<div class="card"><b>Up to 6-Month Warranty</b><br><span class="muted">Peace of mind included.</span></div>', unsafe_allow_html=True)
c.markdown('<div class="card"><b>Easy Returns</b><br><span class="muted">Hassle-free replacements.</span></div>', unsafe_allow_html=True)

# --- CATEGORIES
st.markdown("### Shop by category")
category_tiles()  # uses dynamic categories internally

# --- FEATURED PRODUCTS (purely from data; no placeholders)
st.markdown("### Featured devices")
cards = st.columns(3)
df = store.list_featured()  # staff controls this by checking "Featured"
shown = 0

def _product_card_simple(slot, name, price, img=None, caption=""):
    with slot:
        st.markdown('<div class="card tile">', unsafe_allow_html=True)
        st.image(img or f"https://picsum.photos/seed/{name.replace(' ','')}/640/420", width="stretch")
        st.markdown(f"<b>{name}</b><br><span class='muted'>{caption}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin:.5rem 0 0'><span class='chip'>₹{int(price):,}</span></div>", unsafe_allow_html=True)
        st.page_link("pages/_1_inventory.py", label="View details →", icon="🔎")
        st.markdown('</div>', unsafe_allow_html=True)

if df is not None and not df.empty:
    for idx, (_, row) in enumerate(df.iterrows()):
        _product_card_simple(
            cards[idx % 3],
            row["name"],
            row["price"],
            row.get("image_path") or None,
            f'{row["brand"]} • {row["condition"]}'
        )
        shown += 1
else:
    st.info("No featured devices yet. Staff can mark items as **Featured** from the Inventory page.")

footer()
