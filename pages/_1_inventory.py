import streamlit as st
from components.navbar import navbar
from components.cards import product_card
from services.auth import require_login, is_staff
from services import store

st.set_page_config(page_title="Inventory • ElectroX", layout="wide")
navbar()
user = require_login()  # 🔒 must be logged in
st.title("Inventory")

# -------------------- FILTERS --------------------
with st.expander("Filters", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    q = f1.text_input("Search", key="filter_search")
    brand = f2.text_input("Brand", key="filter_brand")
    category = f3.selectbox("Category", ["All","Phone","Laptop","Tablet","Accessory","Other"], key="filter_cat")
    condition = f4.selectbox("Condition", ["All","Excellent","Very Good","Good","Fair"], key="filter_cond")
    apply = f5.button("Apply", key="filter_apply")

filters = {"q": q, "brand": brand, "category": category, "condition": condition}
active_filters = apply or any([q, brand, category != "All", condition != "All"])
df = store.list_products(filters if active_filters else None)

# -------------------- ADD PRODUCT (staff only) --------------------
if is_staff(user):
    with st.expander("Add Product", expanded=False):
        name = st.text_input("Name", key="add_name")
        brand_in = st.text_input("Brand", key="add_brand")
        category_in = st.selectbox("Category", ["Phone","Laptop","Tablet","Accessory","Other"], key="add_cat")
        condition_in = st.selectbox("Condition", ["Excellent","Very Good","Good","Fair"], key="add_cond")
        price = st.number_input("Price (₹)", min_value=0, step=500, key="add_price")
        stock = st.number_input("Stock", min_value=0, step=1, key="add_stock")
        warranty = st.number_input("Warranty (months)", min_value=0, max_value=24, value=3, key="add_warranty")
        desc = st.text_area("Description", key="add_desc")
        img = st.file_uploader("Upload image", type=["jpg","jpeg","png"], key="add_img")
        if st.button("Save", key="add_save"):
            img_path = store.save_upload(img) if img else ""
            pid = store.add_product({
                "name": name,
                "brand": brand_in,
                "category": category_in,
                "condition": condition_in,
                "price": price,
                "stock": stock,
                "warranty_months": warranty,
                "desc": desc,
                "image_path": img_path,
                "created_by": user["email"],
            })
            st.success(f"Product #{pid} added")
            st.rerun()

# -------------------- PRODUCTS LIST --------------------
if df.empty:
    st.info("No products yet.")
else:
    for _, row in df.iterrows():
        product_card(row.to_dict())
