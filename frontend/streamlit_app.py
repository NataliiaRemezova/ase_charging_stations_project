import os
import sys
import warnings
import streamlit as st
from utils import DataLoader, SessionStateManager
from home import display_home
from heatmaps import display_heatmaps
from ratings_availability import display_postal_code
from details import display_details
from account import display_account
from registration import display_registration

warnings.filterwarnings('ignore', category=UserWarning)

# Initialize session state variables
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False

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
if not st.session_state["data_loaded"]:
    """
        Loads dataset files if they haven't been loaded already.
        - Initializes DataLoader with dataset paths.
        - Loads geospatial, station, and resident data.
        - Saves the data in Streamlit's session state.
        """
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

        st.session_state["data_loaded"] = True
        st.write("✅ Data loaded successfully!")

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
else:
    st.write("ℹ️ Data already loaded in session state.")

# Sidebar Navigation with unique keys
navigation_options = ["Home", "Heatmaps", "Postal Code Search" ,"Details", "Registration"]
if st.session_state["user_info"]:
    navigation_options.append("My Account")

aview = st.sidebar.radio(
    "Navigation", 
    navigation_options,
    key="sidebar_navigation"
)

# Navigation Logic
try:
    """
    Handles navigation between different pages based on user selection.
    """
    if aview == "Home":
        display_home()
    elif aview == "Heatmaps":
        """
        Displays heatmaps of charging stations and residents if datasets are available.
        """
        if "df_lstat" in st.session_state and "df_geodat_plz" in st.session_state and "df_residents" in st.session_state:
            display_heatmaps(
                st.session_state.df_lstat, 
                st.session_state.df_geodat_plz, 
                st.session_state.df_residents
            )
        else:
            st.error("❌ Heatmap data is not available. Please check the dataset.")
    elif aview == "Postal Code Search":
        """
        Displays a search interface for finding charging stations by postal code.
        """
        if "df_lstat" in st.session_state:
            display_postal_code(st.session_state.df_lstat)
        else:
            st.error("❌ Postal code search data is not available.")
    elif aview == "Details":
        """
        Displays detailed statistics and filters for charging stations.
        """
        if "df_lstat" in st.session_state:
            display_details(st.session_state.df_lstat)
        else:
            st.error("❌ Details data is not available.")
    elif aview == "My Account":
        """
        Displays the user's account information and settings.
        """
        display_account()
    elif aview == "Registration":
        """
        Displays login and registration forms for user authentication.
        """
        display_registration()
    else:
        st.error("❌ Invalid navigation option selected.")
except Exception as e:
    st.error(f"❌ Error during navigation: {e}")
