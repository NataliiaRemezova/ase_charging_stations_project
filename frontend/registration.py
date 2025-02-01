import streamlit as st
import requests
from utils import API_BASE_URL


def display_registration():
    """
    Displays the registration and login page for ChargeHub Berlin.

    This function:
    - Provides a login interface where users can enter their email and password.
    - Provides a sign-up interface for new users to create an account.
    - Stores authenticated user information (token, username, email, user ID) in Streamlit session state.
    - Allows users to log out.
    - Fetches the user's profile after successful login.

    Features:
    - **Login Functionality**: Users can log in using their email and password.
    - **User Registration**: New users can create an account with a username, email, and password.
    - **Session Management**: Stores authentication token and user details in session state.
    - **Logout Option**: Users can log out and clear session data.
    """
    st.title("Welcome to ChargeHub Berlin 🌩")

    if "user_info" not in st.session_state:
        st.session_state.user_info = None

    def login(email, password):
        """
        Handles user login by sending authentication credentials to the API.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Updates:
            st.session_state.user_info: Stores user authentication details upon successful login.
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/token",
                data={"username": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    st.session_state.user_info = {
                        "token": token,
                        "username": email
                    }
                    st.success("Logged in successfully!")

                    headers = {"Authorization": f"Bearer {token}"}
                    profile_response = requests.get(
                        f"{API_BASE_URL}/auth/users/me", headers=headers
                    )
                    if profile_response.status_code == 200:
                        user_data = profile_response.json()
                        st.session_state.user_info["username"] = user_data.get("username")
                        st.session_state.user_info["email"] = user_data.get("email")
                        st.session_state.user_info["user_id"] = user_data.get("id")  # Save user_id
                        print("User info")
                        print(st.session_state.user_info["user_id"])
                        print("Get user id")
                        print(user_data.get("id"))
                        st.success(f"Welcome, {user_data.get('username')}!")
                    else:
                        st.error("Failed to fetch user profile after login.")
                else:
                    st.error("Login failed: Token not received.")
            else:
                st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")


    def register(username, email, password):
        """
        Handles new user registration.

        Args:
            username (str): The desired username.
            email (str): The user's email.
            password (str): The user's password.
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                st.success("Account created successfully! Please log in.")
            else:
                st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    # Display UI
    if st.session_state.user_info:
        """
        If a user is logged in, display their profile and provide a logout button.
        """
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info.get('email', 'Not available')}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()
    else:
        """
        If no user is logged in, display login and registration tabs.
        """
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
