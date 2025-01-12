# import streamlit as st
# from utils import load_data, initialize_session_state
# from home import display_home
# from heatmaps import display_heatmaps
# from postal_code import display_postal_code
# from details import display_details
# from account import display_account
# from registration import display_registration

# # Initialize session state variables
# initialize_session_state()

# # Load data directly (not through FastAPI)
# if 'df_geodat_plz' not in st.session_state or st.session_state.df_geodat_plz.empty:
#     df_geodat_plz, df_lstat, df_residents = load_data()
#     st.session_state.df_geodat_plz = df_geodat_plz
#     st.session_state.df_lstat = df_lstat
#     st.session_state.df_residents = df_residents

# # Sidebar Navigation
# aview = st.sidebar.radio(
#     "Navigation", 
#     ["Home", "Heatmaps", "Postal Code Search", "Details", "My Account", "Registration"]
# )

# # Navigation Logic
# if aview == "Home":
#     display_home()
# elif aview == "Heatmaps":
#     display_heatmaps(
#         st.session_state.df_lstat, 
#         st.session_state.df_geodat_plz, 
#         st.session_state.df_residents
#     )
# elif aview == "Postal Code Search":
#     display_postal_code(st.session_state.df_lstat)
# elif aview == "Details":
#     display_details(st.session_state.df_lstat)
# elif aview == "My Account":
#     display_account()
# elif aview == "Registration":
#     display_registration()


import os
import sys
import warnings
import streamlit as st
from utils import DataLoader, SessionStateManager
from home import display_home
from heatmaps import display_heatmaps
from postal_code import display_postal_code
from details import display_details
from account import display_account
from registration import display_registration

warnings.filterwarnings('ignore', category=UserWarning)

# Print current working directory for debugging
print("Current Working Directory:", os.getcwd())

# Set project root dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.environ['PROJECT_ROOT'] = PROJECT_ROOT
print("Project Root:", PROJECT_ROOT)

# Set datasets folder path
datasets_path = os.path.join(PROJECT_ROOT, 'datasets')

# Verify file existence in datasets folder
geodata_path = os.path.join(datasets_path, 'geodata_berlin_plz.csv')
ladesaeulen_path = os.path.join(datasets_path, 'Ladesaeulenregister_SEP.xlsx')
residents_path = os.path.join(datasets_path, 'plz_einwohner.csv')



# Initialize session state using the SessionStateManager
SessionStateManager.initialize_state()

# Append datasets path to system path for easier access
sys.path.append(datasets_path)

# Load data using the DataLoader class if not already loaded in session state
if 'df_geodat_plz' not in st.session_state or st.session_state.df_geodat_plz.empty:
    try:
        # Initialize DataLoader with absolute paths
        data_loader = DataLoader(
            geodata_path=geodata_path,
            ladesaeulen_path=ladesaeulen_path,
            residents_path=residents_path
        )

        # Load data
        df_geodat_plz, df_lstat, df_residents = data_loader.load_data()

        # Save data in session state
        st.session_state.df_geodat_plz = df_geodat_plz
        st.session_state.df_lstat = df_lstat
        st.session_state.df_residents = df_residents

        st.write("Data loaded successfully!")

    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.write("Data already loaded in session state.")

# Sidebar Navigation with unique keys
aview = st.sidebar.radio(
    "Navigation", 
    ["Home", "Heatmaps", "Postal Code Search", "Details", "My Account", "Registration"],
    key="sidebar_navigation"
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
