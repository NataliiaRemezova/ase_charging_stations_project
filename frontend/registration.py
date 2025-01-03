import streamlit as st
import requests
from utils import API_BASE_URL
import datetime
#from pymongo import MongoClient
#from bcrypt import hashpw, gensalt, checkpw

# MongoDB connection
#client = MongoClient("mongodb://localhost:27017")  
#db = client['chargehub']  
#users_collection = db['users'] 

def display_registration():
    st.title("Welcome to ChargeHub Berlin 🌩")

    if 'user_info' not in st.session_state:
        st.session_state.user_info = []

    def sign_up(username, email, password):
        # Commenting out database interaction
        # if users_collection.find_one({"email": email}):
        #     st.warning('Email already exists!')
        # else:
        # Hash the password before storing it (simulated)
        user = {
            "username": username,
            "email": email,
            "password": password,  # Store password directly (for simplicity in this mock version)
            "date_joined": str(datetime.datetime.now())
        }
        # Simulate storing user in session state instead of database
        st.session_state.users.append(user)
        st.success('Account created successfully!')
        st.balloons()

    def log_in(email, password):
        # Simulate login by checking the user data in session state
        user = next((u for u in st.session_state.users if u['email'] == email), None)
        if user and user['password'] == password:
            st.session_state.user_info = {"username": user['username'], "email": user['email']}
            st.success('Logged in successfully!')
        else:
            st.warning('Invalid email or password')

    if st.session_state.user_info:
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info['email']}")

        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()  # Reload the page after logout
    else:
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.subheader("Log In")
            email = st.text_input("Email", key="login_email")  # Add a unique key
            password = st.text_input("Password", type="password", key="login_password")  # Add a unique key
            if st.button("Log In"):
                log_in(email, password)

        with tab2:
            st.subheader("Sign Up")
            username = st.text_input("Username", key="signup_username")  # Add a unique key
            email = st.text_input("Email", key="signup_email")  # Add a unique key
            password = st.text_input("Password", type="password", key="signup_password")  # Add a unique key
            if st.button("Sign Up"):
                sign_up(username, email, password)