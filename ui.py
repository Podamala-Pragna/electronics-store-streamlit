# ui.py — global CSS + topbar
import streamlit as st

def inject_css():
    st.markdown("""
    <style>
      :root {
        --brand:#2b67f6;
        --ink:#0f172a;
        --muted:#64748b;
        --card:#ffffff;
        --bg:#f6f8fc;
      }
      .stApp { background: var(--bg); }
      .hero h1 { font-size: 40px; margin:0; color:var(--ink) }
      .hero p  { color:var(--muted); margin-top:6px }
      .card {
        background:var(--card);
        border-radius:16px;
        padding:16px;
        box-shadow:0 4px 16px rgba(15,23,42,.08);
        height:100%;
      }
      .price { font-weight:700; }
      .btn {
        background:var(--brand); color:#fff; padding:10px 14px;
        border-radius:10px; text-decoration:none; display:inline-block;
      }
      .tag { background:#eef2ff; color:#3730a3; padding:2px 8px; border-radius:999px; font-size:12px }
    </style>
    """, unsafe_allow_html=True)

def topbar():
    left, right = st.columns([1,1])
    with left:
        st.markdown("<h3 style='margin:0'>⚡ ElectroStore</h3>", unsafe_allow_html=True)
    with right:
        user = st.session_state.get("user")
        if user:
            st.caption(f"Logged in as **{user['name']}** ({user['role']})")
