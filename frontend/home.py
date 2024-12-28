import streamlit as st
import folium
from streamlit_folium import st_folium

def display_home():
    st.subheader("Welcome to ChargeHub Berlin 🌩")
    st.markdown("""
    ### Features:
    - **Search for charging stations by postal code (ZIP).**
    - **Visualize charging station density and population using heatmaps.**
    - **Explore detailed statistics for each postal code.**
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Charging Stations", value="1500+")
    with col2:
        st.metric(label="Postal Codes Covered", value="96")
    with col3:
        st.metric(label="Residents Served", value="3M+")

    st.markdown("### Interactive Map")
    home_map = folium.Map(location=[52.5206, 13.4098], zoom_start=12)
    folium.Marker([52.5206, 13.4098], tooltip="Central Station", popup="Main Berlin Station").add_to(home_map)
    st_folium(home_map, width=800, height=400)
