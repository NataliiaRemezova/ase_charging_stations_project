import pandas as pd
import streamlit as st
import requests
from collections import defaultdict

API_BASE_URL = "http://localhost:8000/api"

# Load datasets
@st.cache_data
def load_data():
    df_geodat_plz = pd.read_csv('../datasets/geodata_berlin_plz.csv', sep=';')
    df_lstat = pd.read_excel('../datasets/Ladesaeulenregister_SEP.xlsx', header=10)
    df_residents = pd.read_csv('../datasets/plz_einwohner.csv')
    
    df_lstat['Breitengrad'] = pd.to_numeric(df_lstat['Breitengrad'].str.replace(',', '.'), errors='coerce')
    df_lstat['Längengrad'] = pd.to_numeric(df_lstat['Längengrad'].str.replace(',', '.'), errors='coerce')
    return df_geodat_plz, df_lstat, df_residents

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
        "user_info": None
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

# API helpers
def api_get(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def api_post(endpoint, payload):
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error posting data: {e}")
        return None
