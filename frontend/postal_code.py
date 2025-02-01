import streamlit as st
import requests


# ------------------------------
# 🚀 Fetch Charging Stations by Postal Code
# ------------------------------
def fetch_stations_by_postal_code(postal_code):
    try:
        response = requests.get(f"http://localhost:8000/stations/search/{postal_code}")
        if response.status_code == 200:
            stations = response.json().get("stations", [])
            return stations
        else:
            st.error(f"Failed to fetch charging stations: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []

# ------------------------------
# 🚀 Submit Charging Station Rating
# ------------------------------
def submit_rating(station_id, rating_value, comment, token, user_id):
    """
    Submit a rating for a charging station via backend API.
    """
    if not token:
        st.error("You must be logged in to rate a station.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "rating_value": rating_value,
        "comment": comment
    }
    url = f"http://localhost:8000/stations/{station_id}/rate?user_id={user_id}"  # Add user_id to query

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            st.success("Rating submitted successfully!")
        else:
            st.error(f"Failed to submit rating: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        
def change_availability_status(station_id, token, user_id):
    """
    Change a availability for a charging station via backend API.
    """
    if not token:
        st.error("You must be logged in to rate a station.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    url = f"http://localhost:8000/stations/{station_id}/availability?user_id={user_id}"  # Add user_id to query

    try:
        response = requests.post(
            url,
            headers=headers
        )

        if response.status_code == 200:
            st.success("Availability changed successfully!")
        else:
            st.error(f"Failed to change availability: {response.json().get('detail', 'Unknown error')}")
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
# 🚀 Delete Rating for a Charging Station
# ------------------------------
def delete_station_rating(rating_id):
    """
    Delete rating for a specific charging station.
    """
    try:
        token = st.session_state.user_info.get("token")
        if not token:
            st.error("You must be logged in to delete rating.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        user_id = st.session_state.user_info.get("user_id")
        url = f"http://localhost:8000/ratings/{rating_id}?user_id={user_id}"
        response = requests.delete(
            url,
            headers=headers
        )

        if response.status_code == 200:
            st.success("Rating deleted successfully!")
        else:
            st.error(f"Failed to delete rating: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")


# ------------------------------
# 🚀 Update Rating for a Charging Station
# ------------------------------
def update_station_rating(rating_id, rating_value, comment):
    """
    Update rating for a specific charging station.
    """
    try:
        token = st.session_state.user_info.get("token")
        if not token:
            st.error("You must be logged in to delete rating.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        user_id = st.session_state.user_info.get("user_id")
        payload={
            "rating_value": rating_value,
            "comment": comment
        }
        url = f"http://localhost:8000/ratings/{rating_id}?user_id={user_id}"
        response = requests.put(
            url,
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            st.success("Rating deleted successfully!")
        else:
            st.error(f"Failed to delete rating: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")


