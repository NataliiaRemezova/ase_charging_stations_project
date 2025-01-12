# import streamlit as st
# import requests
# from utils import API_BASE_URL


# def display_registration():
#     st.title("Welcome to ChargeHub Berlin 🌩")

#     if 'user_info' not in st.session_state:
#         st.session_state.user_info = None

#     def login(email, password):
#         try:
#             response = requests.post(
#                 f"{API_BASE_URL}/auth/token",
#                 data={"username": email, "password": password}
#             )
#             if response.status_code == 200:
#                 data = response.json()
#                 token = data.get("access_token")
#                 if token:
#                     # Store token and user info in session state
#                     st.session_state.user_info = {
#                         "token": token,
#                         "username": email
#                     }
#                     st.success("Logged in successfully!")

#                     # Fetch user profile to confirm
#                     headers = {"Authorization": f"Bearer {token}"}
#                     profile_response = requests.get(
#                         f"{API_BASE_URL}/auth/users/me", headers=headers
#                     )
#                     if profile_response.status_code == 200:
#                         user_data = profile_response.json()
#                         st.session_state.user_info["username"] = user_data.get("username")
#                         st.session_state.user_info["email"] = user_data.get("email")
#                         st.success(f"Welcome, {user_data.get('username')}!")
#                     else:
#                         st.error("Failed to fetch user profile after login.")
#                 else:
#                     st.error("Token not received. Please try again.")
#             else:
#                 st.error(f"Failed to log in: {response.json().get('detail')}")
#         except requests.exceptions.RequestException as e:
#             st.error(f"Request failed: {e}")

#     def register(username, email, password):
#         try:
#             response = requests.post(
#                 f"{API_BASE_URL}/auth/register",
#                 json={"username": username, "email": email, "password": password}
#             )
#             if response.status_code == 200:
#                 st.success("Account created successfully! Please log in.")
#             else:
#                 st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             st.error(f"Request failed: {e}")

#     if st.session_state.user_info:
#         st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
#         st.text(f"Email: {st.session_state.user_info.get('email', 'Not available')}")

#         if st.button("Log Out"):
#             st.session_state.user_info = None
#             st.success("Logged out successfully!")
#             st.rerun()
#     else:
#         tab1, tab2 = st.tabs(["Log In", "Sign Up"])

#         with tab1:
#             st.subheader("Log In")
#             email = st.text_input("Email", key="login_email")
#             password = st.text_input("Password", type="password", key="login_password")
#             if st.button("Log In"):
#                 login(email, password)

#         with tab2:
#             st.subheader("Sign Up")
#             username = st.text_input("Username", key="signup_username")
#             email = st.text_input("Email", key="signup_email")
#             password = st.text_input("Password", type="password", key="signup_password")
#             if st.button("Sign Up"):
#                 register(username, email, password)


import streamlit as st
import requests
from utils import DataLoader, SessionStateManager, ApiClient
import os

def display_registration():
    st.title("Welcome to ChargeHub Berlin 🌩")

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.environ['PROJECT_ROOT'] = PROJECT_ROOT
    print("Project Root:", PROJECT_ROOT)

    # Set datasets folder path
    datasets_path = os.path.join(PROJECT_ROOT, 'datasets')
    # Initialize session state
    SessionStateManager.initialize_state()

    # Load data into session state
    data_loader = DataLoader(
        geodata_path = os.path.join(datasets_path, 'geodata_berlin_plz.csv'),
        ladesaeulen_path = os.path.join(datasets_path, 'Ladesaeulenregister_SEP.xlsx'),
        residents_path = os.path.join(datasets_path, 'plz_einwohner.csv')
    )
    df_geodat_plz, df_lstat, df_residents = data_loader.load_data()
    st.session_state["df_geodat_plz"] = df_geodat_plz
    st.session_state["df_lstat"] = df_lstat
    st.session_state["df_residents"] = df_residents

    # Initialize API client
    api_client = ApiClient()

    if "user_info" not in st.session_state:
        st.session_state.user_info = None

    def login(email, password):
        """Handles user login."""
        try:
            response = api_client.post(
                "auth/token",
                data={"username": email, "password": password}
            )
            if response:
                token = response.get("access_token")
                if token:
                    st.session_state.user_info = {"token": token, "username": email}
                    st.success("Logged in successfully!")

                    # Fetch user profile
                    headers = {"Authorization": f"Bearer {token}"}
                    user_data = api_client.get("auth/users/me", headers=headers)
                    if user_data:
                        st.session_state.user_info["username"] = user_data.get("username")
                        st.session_state.user_info["email"] = user_data.get("email")
                        st.success(f"Welcome, {user_data.get('username')}!")
                    else:
                        st.error("Failed to fetch user profile after login.")
                else:
                    st.error("Token not received. Please try again.")
            else:
                st.error("Login failed.")
        except Exception as e:
            st.error(f"Error during login: {e}")

    def register(username, email, password):
        """Handles user registration."""
        try:
            response = api_client.post(
                "auth/register",
                json={"username": username, "email": email, "password": password}
            )
            if response:
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Registration failed.")
        except Exception as e:
            st.error(f"Error during registration: {e}")

    # Display login or registration options
    if st.session_state.user_info:
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info.get('email', 'Not available')}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.experimental_rerun()
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
