import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_star_rating import st_star_rating

def display_postal_code(df_lstat):
    st.subheader("Search for charging stations by zip code")
    # Input for postal code
    postal_code = st.text_input("Enter zip code", st.session_state.get("postal_code", ""))

    if st.button("Search"):
        st.session_state.postal_code = postal_code
        # Filter stations by postal code
        filtered_stations = df_lstat[df_lstat['Postleitzahl'].astype(str) == postal_code]
        st.session_state.filtered_stations = filtered_stations.dropna(subset=['Breitengrad', 'Längengrad'])

        # Create the map if there are filtered stations
        if not st.session_state.filtered_stations.empty:
            center_lat = st.session_state.filtered_stations['Breitengrad'].mean()
            center_lon = st.session_state.filtered_stations['Längengrad'].mean()
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)

            # Add markers to the map
            for _, row in st.session_state.filtered_stations.iterrows():
                folium.Marker(
                    location=[row['Breitengrad'], row['Längengrad']],
                    tooltip=row.get('Anzeigename (Karte)', 'Unknown'),
                    popup=row.get('Anzeigename (Karte)', 'Unknown')
                ).add_to(map_obj)
            st.session_state.map = map_obj

    # Display the map if it exists
    if st.session_state.get("map"):
        output = st_folium(st.session_state.map, width=800, height=500)

        # Check if a marker is clicked
        if output and output.get("last_object_clicked"):
            lat_lng = output["last_object_clicked"]

            # Find the station name based on coordinates
            selected_station = st.session_state.filtered_stations[
                (st.session_state.filtered_stations['Breitengrad'] == lat_lng['lat']) &
                (st.session_state.filtered_stations['Längengrad'] == lat_lng['lng'])
            ]

            if not selected_station.empty:
                location_name = selected_station.iloc[0]['Anzeigename (Karte)']
            else:
                location_name = "Unknown Location"

            # Display the station name
            st.success(f"You selected: {location_name}")

            ## Display ratings (placeholder until backend/database is implemented)
            st.markdown(f"**Rating for {location_name}:**")
            # st.write("Rating: ##")  # Placeholder for backend rating

            # Rating widget (temporary for testing)
            rating = st_star_rating(
                label=f"Rate {location_name}",
                maxValue=5,
                defaultValue=3,
                key=f"star_rating_{location_name}"
            )
            st.write(f"Your rating for {location_name}: {rating} stars")

        else:
            st.info("Click on a marker to select a charging station.")

    # Display summary of stations
    if "filtered_stations" in st.session_state and not st.session_state.filtered_stations.empty:
        filtered_stations = st.session_state.filtered_stations
        st.markdown(f"**Charging stations found:** {len(filtered_stations)}")
        st.markdown(f"- **Standard charger (≤ 22 kW):** {filtered_stations[filtered_stations['Nennleistung Ladeeinrichtung [kW]'] <= 22].shape[0]}")
        st.markdown(f"- **Fast charger  (22-43 kW):** {filtered_stations[(filtered_stations['Nennleistung Ladeeinrichtung [kW]'] > 22) & (filtered_stations['Nennleistung Ladeeinrichtung [kW]'] <= 43)].shape[0]}")
        st.markdown(f"- **View all charging stations:** [hier klicken](#)")
