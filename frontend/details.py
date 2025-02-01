import pandas as pd
import streamlit as st
from utils import DataLoader, SessionStateManager  
import folium
from streamlit_folium import st_folium

def display_details(*args, **kwargs):
    """
    Displays detailed statistics and interactive filters for electric vehicle (EV) charging stations in Berlin.

    This function:
    - Loads and processes charging station data if not already present in session state.
    - Filters data for Berlin and allows users to select charging types and ZIP codes.
    - Dynamically calculates statistics such as total stations, availability, and total charging points.
    - Displays data using interactive charts and tables in Streamlit.

    Features:
    - **Charging Station Status**: Bar chart visualization of available vs. out-of-service stations.
    - **Total Charging Points**: Displays the total number of charging points.
    - **Recent Achievements**: Highlights recent improvements in Berlin's charging network.
    - **ZIP Code Filter**: Allows users to view stations in specific Berlin ZIP codes.
    - **Detailed Data Table**: Option to display raw data for selected ZIP codes.
    """
    st.subheader("Charging Station Details")

    
    SessionStateManager.initialize_state()

    
    if 'df_lstat' not in st.session_state or st.session_state.df_lstat.empty:
        data_loader = DataLoader(
            geodata_path='../datasets/geodata_berlin_plz.csv',
            ladesaeulen_path='../datasets/Ladesaeulenregister_SEP.xlsx',
            residents_path='../datasets/plz_einwohner.csv'
        )
        _, df_lstat, _ = data_loader.load_data()
        st.session_state.df_lstat = df_lstat
    else:
        df_lstat = st.session_state.df_lstat

    
    berlin_df = df_lstat[df_lstat['Ort'] == 'Berlin']

    
    charging_types = berlin_df['Art der Ladeeinrichung'].unique()
    selected_type = st.selectbox("Select Charging Type", options=charging_types)

    
    filtered_df = berlin_df[berlin_df['Art der Ladeeinrichung'] == selected_type]

    
    total_stations = filtered_df.shape[0]
    available_stations = filtered_df[filtered_df['Art der Ladeeinrichung'] != "Out of Service"].shape[0]
    out_of_service_stations = total_stations - available_stations
    total_points = filtered_df['Anzahl Ladepunkte'].sum()

    
    recent_achievements = [
        f"Expanded Network in Berlin",
        f"Added {available_stations} Available Stations of type {selected_type}",
        f"Total Points Surpassed {total_points}"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Charging Station Status")
        chart_data = pd.DataFrame({
            "Stations": [available_stations, out_of_service_stations]
        }, index=["Available", "Out of Service"])
        st.bar_chart(chart_data)

    with col2:
        st.markdown("### Total Charging Points")
        st.metric("Total Points", f"{int(total_points):,}")
        st.markdown("**Recent Achievements**")
        for achievement in recent_achievements:
            st.write(f"- {achievement}")

    
    berlin_zip_codes = berlin_df['Postleitzahl'].unique()
    selected_zip = st.selectbox("Select a ZIP Code (Berlin)", options=berlin_zip_codes)

    filtered_by_zip = berlin_df[berlin_df['Postleitzahl'] == selected_zip]
    st.write(f"Total Stations in ZIP Code {selected_zip}: {filtered_by_zip.shape[0]}")

    
    if st.checkbox("Show Detailed Data"):
        st.write(filtered_by_zip[[
            'Postleitzahl', 'Straße', 'Hausnummer', 
            'Breitengrad', 'Längengrad', 
            'Art der Ladeeinrichung', 'Anzahl Ladepunkte'
        ]])
