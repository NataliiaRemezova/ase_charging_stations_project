import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_star_rating import st_star_rating
import requests


# ------------------------------
# 🚀 Fetch Charging Stations by Postal Code
# ------------------------------
def fetch_stations_by_postal_code(postal_code):
    """
    Fetch charging stations from the backend API based on postal code.
    """
    try:
        response = requests.get(f"http://localhost:8000/stations/search/{postal_code}")
        if response.status_code == 200:
            return response.json().get("stations", [])
        else:
            st.error(f"Failed to fetch charging stations: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []


# ------------------------------
# 🚀 Submit Charging Station Rating
# ------------------------------
def submit_rating(station_id, rating_value, comment, token):
    """
    Submit a rating for a charging station via backend API.
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"http://localhost:8000/stations/{station_id}/rate",
            headers=headers,
            json={"rating_value": rating_value, "comment": comment}
        )
        if response.status_code == 200:
            st.success("Rating submitted successfully!")
        else:
            st.error(f"Failed to submit rating: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")


# ------------------------------
# 🚀 Fetch Ratings for a Charging Station
# ------------------------------
def fetch_station_ratings(station_id):
    """
    Fetch existing ratings for a specific charging station.
    """
    try:
        response = requests.get(f"http://localhost:8000/stations/{station_id}/ratings")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch ratings: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []


# ------------------------------
# 🚀 Display Charging Station Map and Details
# ------------------------------
def display_postal_code(df_lstat):
    """
    Streamlit UI for searching and displaying charging stations by postal code.
    """
    st.subheader("🔍 Search for Charging Stations by Zip Code")
    
    # 📍 Enter Postal Code
    postal_code = st.text_input("Enter zip code", st.session_state.get("postal_code", ""))

    if st.button("Search"):
        st.session_state.postal_code = postal_code
        stations = fetch_stations_by_postal_code(postal_code)
        
        if stations:
            # 📍 Create a Folium map centered on the first station
            center_lat = float(stations[0]['location']['lat'])
            center_lon = float(stations[0]['location']['lon'])
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)

            for station in stations:
                color = 'green' if station['availability_status'] else 'red'
                folium.Marker(
                    location=[station['location']['lat'], station['location']['lon']],
                    tooltip=station['id'],
                    popup=f"Status: {'Available' if station['availability_status'] else 'Not Available'}"
                ).add_to(map_obj)
            
            st.session_state.filtered_stations = stations
            st.session_state.map = map_obj
        else:
            st.warning("No charging stations found for the given postal code.")

    # 🗺️ Display Map
    if st.session_state.get("map"):
        output = st_folium(st.session_state.map, width=800, height=500)

        # 📍 Marker Click Interaction
        if output and output.get("last_object_clicked"):
            lat_lng = output["last_object_clicked"]
            selected_station = next(
                (station for station in st.session_state.filtered_stations
                 if float(station['location']['lat']) == lat_lng['lat']
                 and float(station['location']['lon']) == lat_lng['lng']),
                None
            )

            if selected_station:
                station_id = selected_station['id']
                location_name = selected_station.get('id', 'Unknown Location')

                st.success(f"You selected: {location_name}")
                st.markdown(f"### **Rate this Station**")

                # ⭐ Rating Widget
                rating = st_star_rating(
                    label="Rate this station (1-5 stars):",
                    maxValue=5,
                    defaultValue=3,
                    key=f"star_rating_{station_id}"
                )
                comment = st.text_area("Leave a comment about this station")

                if st.button("Submit Rating"):
                    if 'user_info' in st.session_state and st.session_state.user_info:
                        token = st.session_state.user_info.get("token")
                        submit_rating(station_id, rating, comment, token)
                    else:
                        st.error("You must be logged in to rate a station.")

                # 📊 Display Ratings
                st.markdown(f"### **User Reviews for {location_name}**")
                ratings = fetch_station_ratings(station_id)
                if ratings:
                    for r in ratings:
                        st.write(f"⭐ {r['rating_value']} - {r['comment']}")
                else:
                    st.write("No reviews available for this station.")
            else:
                st.warning("Could not identify the selected station.")

    # 📊 Display Station Summary
    if "filtered_stations" in st.session_state and not st.session_state.filtered_stations.empty:
        stations = st.session_state.filtered_stations
        st.markdown(f"**Total Charging Stations Found:** {len(stations)}")
        standard_chargers = len([s for _, s in stations.iterrows() if s['Nennleistung Ladeeinrichtung [kW]'] <= 22])
        fast_chargers = len([s for _, s in stations.iterrows() if 22 < s['Nennleistung Ladeeinrichtung [kW]'] <= 43])

        st.markdown(f"- **Standard Chargers (≤ 22 kW):** {standard_chargers}")
        st.markdown(f"- **Fast Chargers (22-43 kW):** {fast_chargers}")

        if st.button("View All Stations"):
            st.write(stations)

