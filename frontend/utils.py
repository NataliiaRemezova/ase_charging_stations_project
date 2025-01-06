import pandas as pd
import streamlit as st
import requests
from collections import defaultdict

API_BASE_URL = "http://localhost:8000"

# Load datasets locally
@st.cache_data
def load_data():
    try:
        df_geodat_plz = pd.read_csv('../datasets/geodata_berlin_plz.csv', sep=';')
        df_lstat = pd.read_excel('../datasets/Ladesaeulenregister_SEP.xlsx', header=10)
        df_residents = pd.read_csv('../datasets/plz_einwohner.csv')
        
        df_lstat['Breitengrad'] = pd.to_numeric(df_lstat['Breitengrad'].astype(str).str.replace(',', '.'), errors='coerce')
        df_lstat['Längengrad'] = pd.to_numeric(df_lstat['Längengrad'].astype(str).str.replace(',', '.'), errors='coerce')
        
        return df_geodat_plz, df_lstat, df_residents
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Initialize session state
def initialize_session_state():
    default_states = {
        "postal_code": "",
        "map": None,
        "filtered_stations": pd.DataFrame(),
        "locations": [],
        "user_feedback": defaultdict(list),
        "total_ratings": defaultdict(list),
        "ratings": {},
        "user_info": None,
        "users": [],
        "df_geodat_plz": pd.DataFrame(),
        "df_lstat": pd.DataFrame(),
        "df_residents": pd.DataFrame()
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value
