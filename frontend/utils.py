# import pandas as pd
# import streamlit as st
# import requests
# from collections import defaultdict

# API_BASE_URL = "http://localhost:8000"

# # Load datasets locally
# @st.cache_data
# def load_data():
#     try:
#         df_geodat_plz = pd.read_csv('../datasets/geodata_berlin_plz.csv', sep=';')
#         df_lstat = pd.read_excel('../datasets/Ladesaeulenregister_SEP.xlsx', header=10)
#         df_residents = pd.read_csv('../datasets/plz_einwohner.csv')
        
#         df_lstat['Breitengrad'] = pd.to_numeric(df_lstat['Breitengrad'].astype(str).str.replace(',', '.'), errors='coerce')
#         df_lstat['Längengrad'] = pd.to_numeric(df_lstat['Längengrad'].astype(str).str.replace(',', '.'), errors='coerce')
        
#         return df_geodat_plz, df_lstat, df_residents
#     except Exception as e:
#         st.error(f"Error loading data: {e}")
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# # Initialize session state
# def initialize_session_state():
#     default_states = {
#         "postal_code": "",
#         "map": None,
#         "filtered_stations": pd.DataFrame(),
#         "locations": [],
#         "user_feedback": defaultdict(list),
#         "total_ratings": defaultdict(list),
#         "ratings": {},
#         "user_info": None,
#         "users": [],
#         "df_geodat_plz": pd.DataFrame(),
#         "df_lstat": pd.DataFrame(),
#         "df_residents": pd.DataFrame()
#     }
#     for key, value in default_states.items():
#         if key not in st.session_state:
#             st.session_state[key] = value


import pandas as pd
import streamlit as st
import requests
from collections import defaultdict
from typing import Tuple

API_BASE_URL = "http://localhost:8000"

class DataLoader:
    """Handles data loading and preprocessing."""
    def __init__(self, geodata_path: str, ladesaeulen_path: str, residents_path: str):
        self.geodata_path = geodata_path
        self.ladesaeulen_path = ladesaeulen_path
        self.residents_path = residents_path

    #@st.cache_data
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Loads and preprocesses data from local files."""
        try:
            df_geodat_plz = pd.read_csv(self.geodata_path, sep=';')
            df_lstat = pd.read_excel(self.ladesaeulen_path, header=10)
            df_residents = pd.read_csv(self.residents_path)
            
            # Preprocess data
            df_lstat['Breitengrad'] = pd.to_numeric(
                df_lstat['Breitengrad'].astype(str).str.replace(',', '.'), errors='coerce'
            )
            df_lstat['Längengrad'] = pd.to_numeric(
                df_lstat['Längengrad'].astype(str).str.replace(',', '.'), errors='coerce'
            )
            
            return df_geodat_plz, df_lstat, df_residents
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


class SessionStateManager:
    """Manages Streamlit's session state initialization."""
    @staticmethod
    def initialize_state():
        """Initializes the default session state values."""
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

class ApiClient:
    """Handles API requests to the backend."""
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def get(self, endpoint: str, params: dict = None):
        """Sends a GET request to the specified endpoint."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API request failed: {e}")
            return None

    def post(self, endpoint: str, data: dict):
        """Sends a POST request to the specified endpoint."""
        try:
            response = requests.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API request failed: {e}")
            return None
