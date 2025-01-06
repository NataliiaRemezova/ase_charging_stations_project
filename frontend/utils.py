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
        "user_info": None,
        "users": [],  # Simulate a simple mock list of users in session state for testing
        "df_geodat_plz": pd.DataFrame(),
        "df_lstat": pd.DataFrame(),
        "df_residents": pd.DataFrame()
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Fetch Data from FastAPI
@st.cache_data
def fetch_data_from_api():
    try:
        response = requests.get(f"{API_BASE_URL}/data")
        response.raise_for_status()
        data = response.json()
        
        # Handle potential empty or malformed data
        df_geodat_plz = pd.DataFrame(data.get("geodat_plz", []))
        df_lstat = pd.DataFrame(data.get("lstat", []))
        df_residents = pd.DataFrame(data.get("residents", []))
        
        # Ensure correct column names
        if "Postleitzahl" not in df_lstat.columns and "PLZ" in df_lstat.columns:
            df_lstat.rename(columns={"PLZ": "Postleitzahl"}, inplace=True)
        if "Postleitzahl" not in df_residents.columns and "PLZ" in df_residents.columns:
            df_residents.rename(columns={"PLZ": "Postleitzahl"}, inplace=True)
        
        return df_geodat_plz, df_lstat, df_residents
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
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
