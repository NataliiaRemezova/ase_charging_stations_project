import streamlit as st
import requests
from utils import API_BASE_URL

def display_account():
    # """
    # Display the authenticated user's account information and provide options to:
    # - View and edit profile information.
    # - Change password.
    # - Log out.

    # The function first checks if the user is logged in by verifying if `user_info` 
    # exists in the Streamlit session state. If authenticated, it fetches the user's 
    # details from the backend API and allows modifications.

    # Features:
    # - Displays the logged-in user's username and email.
    # - Allows username updates (email cannot be changed).
    # - Enables password changes with validation.
    # - Provides a logout option.

    # Raises:
    #     HTTPException (handled by API): If API requests fail due to authentication, 
    #     authorization, or server errors.
    # """
    if 'user_info' in st.session_state and st.session_state.user_info:
        token = st.session_state.user_info.get("token")
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(f"{API_BASE_URL}/auth/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                st.subheader(f"Welcome, {user_data['username']}!")
                st.text(f"Email: {user_data['email']}")
                
                st.markdown("### Edit Profile")
                new_username = st.text_input("Username", value=user_data['username'])
                if st.button("Save Profile"):
                    response = requests.put(
                        f"{API_BASE_URL}/auth/users/{user_data['id']}",
                        headers=headers,
                        json={"username": new_username}
                    )
                    if response.status_code == 200:
                        st.success("Profile updated successfully!")
                    else:
                        st.error(f"Failed to update profile: {response.json().get('detail', 'Unknown error')}")

                st.markdown("### Change Password")
                old_password = st.text_input("Old Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                if st.button("Change Password"):
                    if new_password == confirm_password:
                        response = requests.put(
                            f"{API_BASE_URL}/auth/users/{user_data['id']}",
                            headers=headers,
                            json={"old_password": old_password, "new_password": new_password}
                        )
                        if response.status_code == 200:
                            st.success("Password updated successfully!")
                        else:
                            st.error(f"Failed to update password: {response.json().get('detail', 'Unknown error')}")
                    else:
                        st.error("Passwords do not match.")
            else:
                st.error(f"Failed to fetch user data: {response.json().get('detail', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()
    else:
        st.write("Please log in to view your account.")
        st.stop()
