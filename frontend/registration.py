import streamlit as st
import requests
from utils import API_BASE_URL

def display_registration():
    st.title("Welcome to ChargeHub Berlin 🌩")

    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    def sign_up(username, email, password):
        response = requests.post(f"{API_BASE_URL}/signup", json={
            "username": username,
            "email": email,
            "password": password
        })
        return response

    def log_in(email, password):
        response = requests.post(f"{API_BASE_URL}/login", json={
            "email": email,
            "password": password
        })
        return response

    if st.session_state.user_info:
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info['email']}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
    else:
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.subheader("Log In")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Log In"):
                log_in(email, password)

        with tab2:
            st.subheader("Sign Up")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                sign_up(username, email, password)
