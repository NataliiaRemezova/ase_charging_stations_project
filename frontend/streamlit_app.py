import streamlit as st
from utils import load_data, initialize_session_state
from home import display_home
from heatmaps import display_heatmaps
from postal_code import display_postal_code
from details import display_details
from account import display_account
from registration import display_registration


initialize_session_state()
df_geodat_plz, df_lstat, df_residents = load_data()

aview = st.sidebar.radio("", ["Home", "Heatmaps", "Postal Code Search", "Details", "My Account", "Registration"])

if aview == "Home":
    display_home()
elif aview == "Heatmaps":
    display_heatmaps(df_lstat, df_geodat_plz, df_residents)
elif aview == "Postal Code Search":
    display_postal_code(df_lstat)
elif aview == "Details":
    display_details(df_lstat)
elif aview == "My Account":
    display_account()
elif aview == "Registration":
    display_registration()
