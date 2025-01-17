import streamlit as st
import requests
from utils import API_BASE_URL


def display_registration():
    st.title("Welcome to ChargeHub Berlin 🌩")

    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    def login(email, password):
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/token",
                data={"username": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    # Store token and user info in session state
                    st.session_state.user_info = {
                        "token": token,
                        "username": email
                    }
                    st.success("Logged in successfully!")

                    # Fetch user profile to confirm
                    headers = {"Authorization": f"Bearer {token}"}
                    profile_response = requests.get(
                        f"{API_BASE_URL}/auth/users/me", headers=headers
                    )
                    if profile_response.status_code == 200:
                        user_data = profile_response.json()
                        st.session_state.user_info["username"] = user_data.get("username")
                        st.session_state.user_info["email"] = user_data.get("email")
                        st.success(f"Welcome, {user_data.get('username')}!")
                    else:
                        st.error("Failed to fetch user profile after login.")
                else:
                    st.error("Token not received. Please try again.")
            else:
                st.error(f"Failed to log in: {response.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    def register(username, email, password):
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 200:
                st.success("Account created successfully! Please log in.")
            else:
                st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    if st.session_state.user_info:
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info.get('email', 'Not available')}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.subheader("Log In")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Log In"):
                login(email, password)

        with tab2:
            st.subheader("Sign Up")
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                register(username, email, password)
