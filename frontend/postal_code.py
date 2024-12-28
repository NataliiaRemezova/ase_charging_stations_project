import streamlit as st
import folium
from streamlit_folium import st_folium

def display_postal_code(df_lstat):
    st.subheader("Ladestationen nach Postleitzahl suchen")
    postal_code = st.text_input("Postleitzahl eingeben", st.session_state.postal_code)

    if st.button("Suchen"):
        st.session_state.postal_code = postal_code
        filtered_stations = df_lstat[df_lstat['Postleitzahl'].astype(str) == postal_code]
        st.session_state.filtered_stations = filtered_stations.dropna(subset=['Breitengrad', 'Längengrad'])
        
        if not st.session_state.filtered_stations.empty:
            center_lat = st.session_state.filtered_stations['Breitengrad'].mean()
            center_lon = st.session_state.filtered_stations['Längengrad'].mean()
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)
            for _, row in st.session_state.filtered_stations.iterrows():
                folium.Marker(
                    location=[row['Breitengrad'], row['Längengrad']], 
                    tooltip=row.get('Anzeigename (Karte)', 'Unbekannt')
                ).add_to(map_obj)
            st.session_state.map = map_obj

    if st.session_state.map:
        st_folium(st.session_state.map, width=800, height=500)
