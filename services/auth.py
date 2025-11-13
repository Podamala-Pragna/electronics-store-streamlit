# services/auth.py
import streamlit as st
import bcrypt
from . import store

# ---------------------------
# Session helpers
# ---------------------------
def current_user():
    return st.session_state.get("user")

def _set_user(email: str):
    role = store.get_role(email)
    st.session_state["user"] = {"email": email, "role": role}

def logout():
    st.session_state.pop("user", None)

# ---------------------------
# Password-based auth
# ---------------------------
def register(email: str, password: str, role: str = "customer") -> bool:
    if not email or not password:
        return False
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    ok = store.create_user(email, pw_hash, role)
    return ok

def login(email: str, password: str, expected_role: str | None = None) -> bool:
    """
    If expected_role is given, enforce it must match the stored role.
    """
    if not email or not password:
        return False
    u = store.get_user(email)
    if not u:
        return False
    stored = (u.get("password_hash") or "").encode("utf-8")
    if not stored:
        return False
    if not bcrypt.checkpw(password.encode("utf-8"), stored):
        return False

    actual_role = u.get("role", "customer")
    if expected_role and expected_role != actual_role:
        return False

    _set_user(email)
    return True

def update_role(email: str, role: str) -> bool:
    ok = store.set_role(email, role)
    if ok and current_user() and current_user()["email"] == email:
        _set_user(email)
    return ok

# ---------------------------
# Guards
# ---------------------------
def require_login():
    """Stop the page if user isn't logged in. Returns the user dict if logged in."""
    user = current_user()
    if not user:
        st.warning("Please sign in to access this page.")
        st.page_link("pages/_0_login_register.py", label="Go to Login/Register →", icon="🔐")
        st.stop()
    return user

def require_role(roles: list[str]):
    """Stop the page if user's role not in allowed roles. Returns the user dict if allowed."""
    user = require_login()
    if user["role"] not in roles:
        st.error("You do not have permission to access this page.")
        st.page_link("app.py", label="Back to Home →", icon="🏠")
        st.stop()
    return user

def is_staff(user) -> bool:
    return bool(user and user.get("role") == "staff")
