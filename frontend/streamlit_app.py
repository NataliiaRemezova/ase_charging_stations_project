import streamlit as st
from utils import load_data, initialize_session_state
from home import display_home
from heatmaps import display_heatmaps
from postal_code import display_postal_code
from details import display_details
from account import display_account
from registration import display_registration

# Initialize session state variables
initialize_session_state()

# Load data directly (not through FastAPI)
if 'df_geodat_plz' not in st.session_state or st.session_state.df_geodat_plz.empty:
    df_geodat_plz, df_lstat, df_residents = load_data()
    st.session_state.df_geodat_plz = df_geodat_plz
    st.session_state.df_lstat = df_lstat
    st.session_state.df_residents = df_residents

# Sidebar Navigation
aview = st.sidebar.radio(
    "Navigation", 
    ["Home", "Heatmaps", "Postal Code Search", "Details", "My Account", "Registration"]
)

# Navigation Logic
if aview == "Home":
    display_home()
elif aview == "Heatmaps":
    display_heatmaps(
        st.session_state.df_lstat, 
        st.session_state.df_geodat_plz, 
        st.session_state.df_residents
    )
elif aview == "Postal Code Search":
    display_postal_code(st.session_state.df_lstat)
elif aview == "Details":
    display_details(st.session_state.df_lstat)
elif aview == "My Account":
    display_account()
elif aview == "Registration":
    display_registration()
