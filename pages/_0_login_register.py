import streamlit as st
from components.navbar import navbar
from services.auth import current_user, register, login, logout, update_role
from services.auth import require_login, is_staff

st.set_page_config(page_title="Account • ElectroX", layout="wide")
navbar()
st.title("Account")

user = current_user()
if user:
    st.success(f"Signed in as {user['email']} ({user['role']})")
    with st.expander("Change role (demo)"):
        new_role = st.selectbox("Role", ["customer","staff","admin"], index=["customer","staff","admin"].index(user["role"]))
        if st.button("Update role"):
            if update_role(user["email"], new_role):
                st.session_state["user"]["role"] = new_role
                st.success("Role updated")
    if st.button("Log out"):
        logout(); st.rerun()
else:
    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login:
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Sign in"):
            if login(email, pw):
                st.success("Welcome!")
                st.rerun()
            else:
                st.error("Invalid email or password")
    with tab_register:
        email_r = st.text_input("Email ", key="reg_email")
        pw_r = st.text_input("Password ", type="password", key="reg_pw")
        pw2_r = st.text_input("Confirm Password ", type="password", key="reg_pw2")
        role_r = st.selectbox("Role ", ["customer","staff"], key="reg_role")
        if st.button("Create account"):
            if pw_r != pw2_r:
                st.error("Passwords do not match")
            else:
                ok = register(email_r, pw_r, role_r)
                if ok:
                    st.success("Account created. Please sign in.")
                else:
                    st.error("Registration failed (email may already exist)")
