import streamlit as st

def product_card(row, cart_key_prefix="cart"):
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 3, 1])

        with c1:
            img = row.get("image_path", "")
            if isinstance(img, str) and img:
                st.image(img, width="stretch")
            else:
                st.image("https://picsum.photos/seed/product/300/200", width="stretch")

        with c2:
            st.subheader(row["name"])
            st.caption(f"{row['brand']} • {row['condition']} • {row.get('category','')}")
            st.write(row.get("desc", ""))
            st.caption(f"Warranty: {int(row.get('warranty_months', 3))} months")

        with c3:
            price = int(float(row["price"]))
            stock = int(row["stock"])
            st.metric("Price", f"₹{price:,}")
            st.caption(f"In stock: {stock}")

            qty = st.number_input(
                "Qty",
                min_value=1,
                max_value=max(1, stock),
                value=1,
                key=f"{cart_key_prefix}_qty_{int(row['id'])}"
            )
            if st.button("Add to cart", key=f"{cart_key_prefix}_btn_{int(row['id'])}"):
                cart = st.session_state.setdefault("cart", {})
                pid = int(row["id"])
                cart[pid] = cart.get(pid, 0) + int(qty)
                st.success("Added to cart")
