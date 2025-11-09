import streamlit as st
from components.navbar import navbar
from services.auth import require_login
from services import store
from services.auth import require_login

st.set_page_config(page_title="Cart • ElectroX", layout="wide")
navbar()
user = require_login()  # 🔒
st.title("Your Cart")

cart = st.session_state.get("cart", {})
if not cart:
    st.info("Cart is empty.")
    st.stop()

dfp = store.list_products()
items = []
subtotal = 0.0
for pid, qty in cart.items():
    row = dfp[dfp["id"] == pid]
    if row.empty: continue
    price = float(row.iloc[0]["price"])
    name = row.iloc[0]["name"]
    line = price * qty
    items.append((pid, name, qty, price, line))
    subtotal += line

tax = round(subtotal * 0.18, 2)
shipping = 99.0 if subtotal > 0 else 0.0
total = round(subtotal + tax + shipping, 2)

st.subheader("Items")
for _, name, qty, price, line in items:
    st.write(f"**{name}** — Qty: {qty} • ₹{int(price):,} each • Line: ₹{int(line):,}")

st.subheader("Summary")
st.write(f"Subtotal: ₹{int(subtotal):,}")
st.write(f"Tax (18%): ₹{int(tax):,}")
st.write(f"Shipping: ₹{int(shipping):,}")
st.write(f"**Total: ₹{int(total):,}**")

st.subheader("Payment")
method = st.selectbox("Payment method", ["UPI","Card","COD"])
details = ""
if method == "UPI":
    upi = st.text_input("UPI ID (e.g., name@upi)")
    details = f"UPI:{upi}"
elif method == "Card":
    col1, col2 = st.columns(2)
    with col1: card = st.text_input("Card Number (####-####-####-####)")
    with col2: exp = st.text_input("Expiry (MM/YY)")
    cvv = st.text_input("CVV", type="password")
    details = f"CARD:{card}|EXP:{exp}"
else:
    st.info("Cash on Delivery selected. Payment will be collected at delivery.")
    details = "COD"

if st.button("Pay & Place Order"):
    try:
        oid = store.create_order(user["email"], cart, method, details)
        st.session_state["cart"] = {}
        st.success(f"Order placed: {oid}")
    except Exception as e:
        st.error(str(e))
