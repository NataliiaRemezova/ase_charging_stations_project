import streamlit as st
import folium
from streamlit_folium import st_folium
from utils import load_data  # Import your utility functions

def calculate_metrics(df_lstat, df_residents):
    # Filter data for Berlin
    berlin_stations = df_lstat[df_lstat['Bundesland'] == 'Berlin']
    # Total number of charging stations
    total_charging_stations = berlin_stations['Anzahl Ladepunkte'].sum()
    # Total unique postal codes
    total_postal_codes = berlin_stations['Postleitzahl'].nunique()
    # Residents served (from residents dataset)
    berlin_residents = df_residents[df_residents['plz'].isin(berlin_stations['Postleitzahl'])]
    total_residents_served = berlin_residents['einwohner'].sum()
    
    return total_charging_stations, total_postal_codes, total_residents_served


def display_home():
    st.subheader("Welcome to ChargeHub Berlin 🌩")
    st.markdown("""
    ### Features:
    - **Search for charging stations by postal code (ZIP).**
    - **Visualize charging station density and population using heatmaps.**
    - **Explore detailed statistics for each postal code.**
    """)
    # Load data from utilities
    df_geodat_plz, df_lstat, df_residents = load_data()
    
    # Calculate metrics for Berlin
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
    folium.Marker([52.5206, 13.4098], tooltip="Central Station", popup="Main Berlin Station").add_to(home_map)
    st_folium(home_map, width=800, height=400)
