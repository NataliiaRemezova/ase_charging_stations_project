import streamlit as st
import requests
from utils import API_BASE_URL


def display_account():
    if 'user_info' in st.session_state and st.session_state.user_info:
        token = st.session_state.user_info.get("token")
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(f"{API_BASE_URL}/auth/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                st.subheader(f"Welcome, {user_data['username']}!")
                st.text(f"Email: {user_data['email']}")
                
                # Edit Profile
                st.markdown("### Edit Profile")
                new_username = st.text_input("Username", value=user_data['username'])
                new_email = st.text_input("Email", value=user_data['email'])
                if st.button("Save Profile"):
                    response = requests.put(
                        f"{API_BASE_URL}/auth/users/me",
                        headers=headers,
                        json={"username": new_username, "email": new_email}
                    )
                    if response.status_code == 200:
                        st.success("Profile updated successfully!")
                    else:
                        st.error("Failed to update profile.")

                # Change Password
                st.markdown("### Change Password")
                old_password = st.text_input("Old Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                if st.button("Change Password"):
                    if new_password == confirm_password:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/change-password",
                            headers=headers,
                            json={"old_password": old_password, "new_password": new_password}
                        )
                        if response.status_code == 200:
                            st.success("Password updated successfully!")
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Passwords do not match.")
            else:
                st.error("Failed to fetch user data. Please log in again.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()
    else:
        st.write("Please log in to view your account.")
        st.stop()
