import pandas as pd
import streamlit as st
from utils import DataLoader, SessionStateManager  # Import utility classes
import folium
from streamlit_folium import st_folium

def display_details(*args, **kwargs):
    """
    Displays detailed statistics and filters for charging stations in Berlin.
    """
    st.subheader("Charging Station Details")

    # Ensure session state variables are initialized
    SessionStateManager.initialize_state()

    # Load data using DataLoader if not already loaded in session state
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

    # Filter the data for Berlin only
    berlin_df = df_lstat[df_lstat['Ort'] == 'Berlin']

    # User input to filter stations by charging type or service status
    charging_types = berlin_df['Art der Ladeeinrichung'].unique()
    selected_type = st.selectbox("Select Charging Type", options=charging_types)

    # Filter data based on selected charging type
    filtered_df = berlin_df[berlin_df['Art der Ladeeinrichung'] == selected_type]

    # Calculate statistics dynamically from filtered_df
    total_stations = filtered_df.shape[0]
    available_stations = filtered_df[filtered_df['Art der Ladeeinrichung'] != "Out of Service"].shape[0]
    out_of_service_stations = total_stations - available_stations
    total_points = filtered_df['Anzahl Ladepunkte'].sum()

    # Recent achievements
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

    # Additional filters for ZIP Codes within Berlin
    berlin_zip_codes = berlin_df['Postleitzahl'].unique()
    selected_zip = st.selectbox("Select a ZIP Code (Berlin)", options=berlin_zip_codes)

    filtered_by_zip = berlin_df[berlin_df['Postleitzahl'] == selected_zip]
    st.write(f"Total Stations in ZIP Code {selected_zip}: {filtered_by_zip.shape[0]}")

    # Displaying detailed table with street and number info
    if st.checkbox("Show Detailed Data"):
        st.write(filtered_by_zip[[
            'Postleitzahl', 'Straße', 'Hausnummer', 
            'Breitengrad', 'Längengrad', 
            'Art der Ladeeinrichung', 'Anzahl Ladepunkte'
        ]])
