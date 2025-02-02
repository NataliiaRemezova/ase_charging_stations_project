import streamlit as st
from postal_code import fetch_station_ratings, submit_rating, change_availability_status, update_station_rating, delete_station_rating, fetch_stations_by_postal_code
import folium
from streamlit_folium import st_folium
import time
from streamlit_star_rating import st_star_rating

# Display Charging Station Map and Details
def display_postal_code(df_lstat):
    """
    Streamlit UI for searching and displaying charging stations by postal code.

    This function:
    - Allows users to search for charging stations using a ZIP code.
    - Displays an interactive map of charging stations.
    - Allows users to click on a station marker to view details.
    - Enables users to rate, update ratings, delete ratings, and change station availability.

    Features:
    - **Search Charging Stations**: Users enter a postal code to fetch stations.
    - **Interactive Map**: Clickable markers allow users to select a station.
    - **User Ratings & Comments**: Users can submit, update, and delete ratings.
    - **Change Availability**: Users can toggle the station's availability.
    """
    if "view" not in st.session_state:
        st.session_state.view = "search"
        
    if st.session_state.view == "search":
        st.subheader("🔍 Search for Charging Stations by Zip Code")
        
        # Enter Postal Code
        postal_code = st.text_input("Enter zip code", st.session_state.get("postal_code", ""))

        if st.button("Search or Update"):
            st.session_state.postal_code = postal_code
            stations = fetch_stations_by_postal_code(postal_code)
            st.session_state.selected_station = None

            if "selected_station" not in st.session_state:
                st.session_state.selected_station = None
            
            update_map(stations)

        # Display Map
        if st.session_state.get("map"):
            output = st_folium(st.session_state.map, width=800, height=500)

            # Marker Click Interaction
            if output and output.get("last_object_clicked"):
                lat_lng = output["last_object_clicked"]

                # Find the selected station based on click coordinates
                selected_station = next(
                    (station for station in st.session_state.filtered_stations
                    if tuple(map(float, station['location'].split(", "))) == (lat_lng['lat'], lat_lng['lng'])),
                    None
                )

                if selected_station:
                    st.session_state.selected_station = selected_station
                    location_name = selected_station.get('name', 'Unknown Location')

                    st.success(f"You selected: {location_name}")
                    if st.button("Show Details"):
                        st.session_state.view = "details"
                        st.rerun()

                else:
                    st.warning("Could not identify the selected station.")

        # Display Station Summary
        if "filtered_stations" in st.session_state:
            stations = st.session_state.filtered_stations
            st.markdown(f"**Total Charging Stations Found:** {len(stations)}")

            st.markdown("### Station Details")
            for station in stations:
                st.write(f"- **{station['name']}** (Status: {'Available' if station['availability_status'] else 'Not Available'})")
    
    # Display Details and Rating
    elif st.session_state.get("view") == "details" and st.session_state.selected_station:
        """
        Displays detailed information about a selected charging station.
        - Shows the station's location and availability.
        - Allows users to submit, update, or delete ratings.
        - Provides an option to change station availability.
        """
        station = st.session_state.selected_station
        st.subheader(f"🚗 {station['name']}")
        st.write(f"**Location:** {station['location']}")
        st.write(f"**Availability:** {'Available' if station['availability_status'] else 'Not Available'}")
        
        st.markdown(f"### **User Reviews for {station['location']}**")
        ratings = fetch_station_ratings(station['id'])
        if ratings:
            for r in ratings:
                if isinstance(r['comment'], list):
                    submitted_comment = r['comment'][0]
                else:
                    submitted_comment = r['comment']
                if isinstance(r['rating_value'], list):
                    rating_value = r['rating_value'][0]
                else:
                    rating_value = r['rating_value']
                st.write(f" {r['username']}: ⭐ {rating_value} - {submitted_comment}")
                if st.session_state.user_info is not None:
                    if r['user_id'] == st.session_state.user_info.get("user_id"):
                        if st.button("delete"):
                            delete_station_rating(r['id'])
                            st.rerun()
                
        else:
            st.write("No reviews available for this station.")

        rating = st_star_rating(label="Rate this station (1-5 stars):", maxValue=5, defaultValue=3,
                                key=f"star_rating_{station['id']}")
        comment = st.text_area("Leave a comment about this station")
        show_submit = True
        show_update = False
        if st.session_state.user_info is not None:
            if ratings:
                for r in ratings:
                    if r['user_id'] == st.session_state.user_info.get("user_id"):
                        show_submit = False
                        show_update = True
        else:
            show_submit = False
            show_update = False
        
        if show_submit:
            if st.button("Submit Rating"):
                if 'user_info' in st.session_state and st.session_state.user_info:
                    token = st.session_state.user_info.get("token")
                    user_id = st.session_state.user_info.get("user_id")
                    submit_rating(station['id'], rating, comment, token, user_id)
                    st.rerun()
                else:
                    st.error("You must be logged in to rate a station.")
        
        if show_update:
            if st.button("Update comment"):
                if 'user_info' in st.session_state and st.session_state.user_info:
                    token = st.session_state.user_info.get("token")
                    user_id = st.session_state.user_info.get("user_id")
                    update_station_rating(r['id'], rating, comment)
                    st.rerun()
                else:
                    st.error("You must be logged in to rate a station.")
            
        if st.button("Change Availability"):
            if 'user_info' in st.session_state and st.session_state.user_info:
                token = st.session_state.user_info.get("token")
                user_id = st.session_state.user_info.get("user_id")
                change_availability_status(station['id'], token, user_id)
                stations = fetch_stations_by_postal_code(st.session_state.postal_code)
                time.sleep(0.5)
                update_map(stations)
            else:
                st.error("You must be logged in to change availability.")

        if st.button("Back"):
            st.session_state.view = "search"
            st.session_state.selected_station = None
            st.rerun()


def update_map(stations):
    """
    Updates the interactive map with charging station locations.

    Args:
        stations (list): A list of charging station dictionaries.
    """
    if stations:
        try:
            # Parse the location string of the first station
            center_lat, center_lon = map(float, stations[0]['location'].split(", "))
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)

            for station in stations:
                # Parse the location field
                lat, lon = map(float, station['location'].split(", "))
                name = station.get('name', 'Unknown Name')
                status = 'Available' if station['availability_status'] else 'Not Available'

                folium.Marker(
                    location=[lat, lon],
                    tooltip=f"Name: {name}",
                    popup=f"<b>{name}</b><br>Status: {status}<br>Lat: {lat}, Lon: {lon}",
                    icon=folium.Icon(color='green' if station['availability_status'] else 'red')
                ).add_to(map_obj)
            
            st.session_state.filtered_stations = stations
            st.session_state.map = map_obj
        except (KeyError, TypeError, ValueError) as e:
            st.error(f"Error processing station data: {e}")
    else:
        st.warning("No charging stations found for the given postal code.")