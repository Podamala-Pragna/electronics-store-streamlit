import streamlit as st
import bcrypt
from db import query_df, execute_sql

def _hash_pw(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def _check_pw(pw: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed)

def current_user():
    return st.session_state.get("user")

def logout():
    for k in ["user"]:
        if k in st.session_state:
            del st.session_state[k]

def register(email: str, password: str, role: str = "customer"):
    # Ensure users table exists
    execute_sql("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARBINARY(100) NOT NULL,
        role ENUM('customer','staff','admin') NOT NULL DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    pwd_hash = _hash_pw(password)
    execute_sql(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        (email, pwd_hash, role)
    )
    return True

def login(email: str, password: str):
    df = query_df("SELECT id, email, password_hash, role FROM users WHERE email=%s", (email,))
    if df.empty:
        return False
    row = df.iloc[0]
    if _check_pw(password, row["password_hash"]):
        st.session_state["user"] = {
            "id": int(row["id"]),
            "email": row["email"],
            "role": row["role"]
        }
        return True
    return False
