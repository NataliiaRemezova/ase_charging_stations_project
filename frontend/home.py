import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import DataLoader, SessionStateManager  

def calculate_metrics(df_lstat, df_residents):
    """
    Calculate metrics for charging stations and residents served in Berlin.
    """
    
    berlin_stations = df_lstat[df_lstat['Bundesland'] == 'Berlin']
    total_charging_stations = berlin_stations['Anzahl Ladepunkte'].sum()
    total_postal_codes = berlin_stations['Postleitzahl'].nunique()
    berlin_residents = df_residents[df_residents['plz'].isin(berlin_stations['Postleitzahl'])]
    total_residents_served = berlin_residents['einwohner'].sum()
    
    return total_charging_stations, total_postal_codes, total_residents_served


def display_home():
    """
    Displays the Home page with key metrics and an interactive map.

    This function:
    - Introduces the ChargeHub Berlin application with key features.
    - Loads and caches dataset information into Streamlit's session state.
    - Computes key statistics related to charging stations and population coverage.
    - Displays an interactive **map of Berlin** with markers.

    Features:
    - **Search for charging stations by postal code (ZIP).**
    - **Visualize charging station density and population using heatmaps.**
    - **Explore detailed statistics for each postal code.**
    - **View an interactive map with markers.**

    Metrics Displayed:
    - **Total Charging Stations**: The number of available stations in Berlin.
    - **Postal Codes Covered**: The number of Berlin ZIP codes with charging stations.
    - **Residents Served**: The total number of Berlin residents covered by charging stations.
    """
    st.subheader("Welcome to ChargeHub Berlin 🌩")
    st.markdown("""
    ### Features:
    - **Search for charging stations by postal code (ZIP).**
    - **Visualize charging station density and population using heatmaps.**
    - **Explore detailed statistics for each postal code.**
    """)
    
    SessionStateManager.initialize_state()
    
    if 'df_geodat_plz' not in st.session_state or st.session_state.df_geodat_plz.empty:
        data_loader = DataLoader(
            geodata_path='../datasets/geodata_berlin_plz.csv',
            ladesaeulen_path='../datasets/Ladesaeulenregister_SEP.xlsx',
            residents_path='../datasets/plz_einwohner.csv'
        )
        df_geodat_plz, df_lstat, df_residents = data_loader.load_data()
        st.session_state.df_geodat_plz = df_geodat_plz
        st.session_state.df_lstat = df_lstat
        st.session_state.df_residents = df_residents
    else:
        df_geodat_plz = st.session_state.df_geodat_plz
        df_lstat = st.session_state.df_lstat
        df_residents = st.session_state.df_residents

    total_stations, total_postal_codes, residents_served = calculate_metrics(df_lstat, df_residents)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Charging Stations", value=f"{total_stations}")
    with col2:
        st.metric(label="Postal Codes Covered", value=f"{total_postal_codes}")
    with col3:
        st.metric(label="Residents Served", value=f"{residents_served:,}")
    
    st.markdown("### Interactive Map")
    home_map = folium.Map(location=[52.5206, 13.4098], zoom_start=12)
    folium.Marker(
        [52.5206, 13.4098], tooltip="Central Station", popup="Main Berlin Station"
    ).add_to(home_map)
    st_folium(home_map, width=800, height=400)

