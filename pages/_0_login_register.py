# pages/_0_login_register.py
import streamlit as st
from components.navbar import navbar
from services.auth import current_user, register, login, logout, update_role

st.set_page_config(page_title="Account • ElectroX", layout="wide")
navbar()
st.title("Account")

# small helper to redirect safely across Streamlit versions
def _goto(path: str):
    try:
        # Streamlit >= 1.25
        st.switch_page(path)
    except Exception:
        # Fallback: store target and rerun; navbar or app.py can read and route
        st.session_state["__goto__"] = path
        st.rerun()

user = current_user()
if user:
    st.success(f"Signed in as {user['email']} ({user['role']})")

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Go to Inventory", key="acct_to_inventory"):
            _goto("pages/_1_inventory.py")
    with colB:
        if st.button("Go to Cart", key="acct_to_cart"):
            _goto("pages/_2_cart.py")
    with colC:
        if user["role"] == "staff" and st.button("Go to Staff Dashboard", key="acct_to_staff"):
            _goto("pages/_6_staff_dashboard.py")

    with st.expander("Change role (demo)"):
        new_role = st.selectbox(
            "Role",
            ["customer","staff"],
            index=["customer","staff"].index(user["role"]),
            key="role_change_select"
        )
        if st.button("Update role", key="role_change_btn"):
            if update_role(user["email"], new_role):
                st.session_state["user"]["role"] = new_role
                st.success("Role updated")

    if st.button("Log out", key="logout_btn"):
        logout(); st.rerun()

else:
    tab_login, tab_register = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------
    with tab_login:
        st.subheader("Login to your account")
        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Password", type="password", key="login_pw")
        role_pick = st.selectbox("Role", ["customer","staff"], key="login_role")
        if st.button("Sign in", key="login_btn"):
            ok = login(email, pw, expected_role=role_pick)
            if ok:
                # redirect based on role
                target = "pages/_6_staff_dashboard.py" if role_pick == "staff" else "pages/_1_inventory.py"
                _goto(target)
            else:
                st.error("Invalid email/password or role mismatch.\n"
                         "Please select the correct role you registered with.")

    # ---------------- REGISTER ----------------
    with tab_register:
        st.subheader("Create a new account")
        email_r = st.text_input("Email ", key="reg_email")
        pw_r = st.text_input("Password ", type="password", key="reg_pw")
        pw2_r = st.text_input("Confirm Password ", type="password", key="reg_pw2")
        role_r = st.selectbox("Role ", ["customer","staff"], key="reg_role")
        if st.button("Create account", key="reg_btn"):
            if pw_r != pw2_r:
                st.error("Passwords do not match")
            else:
                ok = register(email_r, pw_r, role_r)
                if ok:
                    st.success("Account created. Please sign in.")
                else:
                    st.error("Registration failed (email may already exist)")
