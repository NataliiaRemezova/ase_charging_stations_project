import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import shape
from collections import defaultdict
from core import methods as m1
from core import HelperTools as ht
from config import pdict



# Load data
df_geodat_plz = pd.read_csv('datasets/geodata_berlin_plz.csv', sep=';')  # Geospatial data
df_lstat = pd.read_excel('datasets/Ladesaeulenregister_SEP.xlsx', header=10)
df_residents = pd.read_csv('datasets/plz_einwohner.csv')  # Residents data

# Clean the latitude and longitude columns to remove commas and convert to numeric
df_lstat['Breitengrad'] = pd.to_numeric(df_lstat['Breitengrad'].str.replace(',', '.'), errors='coerce')
df_lstat['Längengrad'] = pd.to_numeric(df_lstat['Längengrad'].str.replace(',', '.'), errors='coerce')

# Initialize session state if not already done
if "postal_code" not in st.session_state:
    st.session_state.postal_code = ""
if "map" not in st.session_state:
    st.session_state.map = None  # Initialize an empty map state
if "filtered_stations" not in st.session_state:
    st.session_state.filtered_stations = pd.DataFrame()  # Initialize empty DataFrame
if "locations" not in st.session_state:
    st.session_state.locations = []
if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = defaultdict(list)
if "total_ratings" not in st.session_state:
    st.session_state.total_ratings = defaultdict(list)
if "ratings" not in st.session_state:
    st.session_state.ratings = {}

# Data preprocessing
def preprocess_data():
    # Rename columns if needed to maintain consistency
    if 'Latitude' not in df_geodat_plz.columns:
        df_geodat_plz.rename(columns={'Breitengrad': 'Latitude', 'Längengrad': 'Longitude'}, inplace=True)
    return df_geodat_plz, df_lstat

df_geodat_plz, df_lstat = preprocess_data()


# Function to display star ratings after marker click
def display_star_rating(station_name):
    """ Displays a star-based rating system for a station. """
    rating = st.radio("Rate the station:", options=[1, 2, 3, 4, 5], format_func=lambda x: "⭐" * x)
    if st.button(f"Submit Rating for {station_name}"):
        if station_name in st.session_state.ratings:
            st.session_state.ratings[station_name].append(rating)
        else:
            st.session_state.ratings[station_name] = [rating]
        st.success(f"Rating {rating} stars submitted for {station_name}!")


# Set page config
st.set_page_config(page_title="ChargeHub Berlin 🌩", layout="wide")

# Sidebar navigation
st.sidebar.title("Ansicht wählen")
aview = st.sidebar.radio(
    "", ["Home", "Heatmaps", "Postleitzahlen", "Details", "My Account", "Registration"]
)

# Main header
st.title("ChargeHub Berlin 🌩")

if aview == "Home":
    st.subheader("Willkommen bei ChargeHub Berlin 🌩")
    st.markdown(""" 
    ### Features:
    - **Search for charging stations by zip code (PLZ).**
    - **Visualize charging station density and population using heatmaps.**
    - **Explore detailed statistics for each zip code.**

    ### Key Metrics:
    """)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Charging Stations", value="1500+")
    with col2:
        st.metric(label="PLZ Covered", value="96")
    with col3:
        st.metric(label="Residents Served", value="3M+")

    st.markdown("---")
    
    st.markdown("### Interactive Map")
    st.write("Explore charging station locations in Berlin.")
    home_map = folium.Map(location=[52.5206, 13.4098], zoom_start=12)
    folium.Marker([52.5206, 13.4098], tooltip="Central Station", popup="Main Berlin Station").add_to(home_map)
    st_folium(home_map, width=800, height=400)

elif aview == "Heatmaps":
    st.subheader("Electric Charging Station Heatmaps")
    function_selection = st.radio(
        "Select Visualization Type",
        (
            "Heatmap: Electric Charging Stations and Residents",
            "Heatmap: Electric Charging Stations by KW and Residents"
        )
    )

    # Preprocess data
    gdf_lstat = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

    if function_selection == "Heatmap: Electric Charging Stations and Residents":
        st.write("Heatmap showing Electric Charging Stations and Residents")
        m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)
    else:
        st.write("Heatmap showing Electric Charging Stations by KW and Residents")
        m1.make_streamlit_electric_Charging_resid_by_kw(gdf_lstat3, gdf_residents2)


elif aview == "Postleitzahlen":
    st.subheader("Ladestationen nach Postleitzahl suchen")

    # Input for postal code
    postal_code = st.text_input("Postleitzahl eingeben", st.session_state.postal_code)

    # When the "Suchen" button is clicked
    if st.button("Suchen"):
        st.session_state.postal_code = postal_code

        # Filter stations based on the postal code (make sure to use the correct column name 'Postleitzahl')
        filtered_stations = df_lstat[df_lstat['Postleitzahl'].astype(str) == st.session_state.postal_code]

        # Store filtered stations in session state
        st.session_state.filtered_stations = filtered_stations

        # Check if any stations match the postal code
        if not filtered_stations.empty:
            # Remove rows where latitude or longitude is NaN
            filtered_stations = filtered_stations.dropna(subset=['Breitengrad', 'Längengrad'])

            # Ensure there are valid coordinates after dropping NaN values
            if filtered_stations.empty:
                st.write("Keine gültigen Koordinaten für diese Postleitzahl gefunden.")
            else:
                latitudes = filtered_stations['Breitengrad']
                longitudes = filtered_stations['Längengrad']
                center_lat = latitudes.mean()
                center_lon = longitudes.mean()

                # Create the folium map centered around the average location of the filtered stations
                m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

                # Add markers for each station with a click event to rate the station
                for _, row in filtered_stations.iterrows():
                    station_name = row.get('Anzeigename (Karte)', 'Unbekannt')  # Default to 'Unbekannt' if empty
                    marker = folium.Marker(
                        location=[row['Breitengrad'], row['Längengrad']], 
                        popup=folium.Popup(f"<strong>{station_name}</strong><br>Click to rate this station!", parse_html=True),
                        tooltip=station_name
                    )

                    # Attach a click event to the marker to enable rating
                    marker.add_to(m)

                # Store the map in session state so it persists across reruns
                st.session_state.map = m

        else:
            # No stations found for this postal code
            st.write("Keine Ladestationen für diese Postleitzahl gefunden.")

    # If the map is already stored in session state, render it
    if st.session_state.map:
        # Display the map
        st_folium(st.session_state.map, width=800, height=500)

        # Show the number of found stations
        filtered_stations = st.session_state.filtered_stations
        st.markdown(f"**Gefundene Ladestationen:** {len(filtered_stations)}")
        st.markdown(f"- **Normallader (≤ 22 kW):** {filtered_stations[filtered_stations['Nennleistung Ladeeinrichtung [kW]'] <= 22].shape[0]}")
        st.markdown(f"- **Schnelllader (22-43 kW):** {filtered_stations[(filtered_stations['Nennleistung Ladeeinrichtung [kW]'] > 22) & (filtered_stations['Nennleistung Ladeeinrichtung [kW]'] <= 43)].shape[0]}")
        st.markdown(f"- **Alle Ladestationen anzeigen:** [hier klicken](#)")

        # Add a form to rate the station when clicked
        station_name = st.text_input("Geben Sie den Namen der Station ein, um zu bewerten:")
        if station_name:
            display_star_rating(station_name)

elif aview == "Details":
    st.subheader("Details der Ladestationen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Verfügbare Ladestationen")
        st.bar_chart(pd.DataFrame({"Ladestationen": [10, 15, 20]}, index=["Belegte", "Verfügbare", "Defekte"]))

    with col2:
        st.markdown("### Gesamtpunkte")
        st.metric("Punkte", "1,234")
        st.markdown("**Letzte Abzeichen**")
        st.write("- Power User")
        st.write("- +150 Punkte verdient")

elif aview == "My Account":
    st.subheader("My Account")

    username = st.text_input("Enter your name:")
    profile = st.text_area("Create your profile:")
    if st.button("Save Profile"):
        st.session_state.user_feedback[username].append(profile)
        st.success("Profile saved successfully!")

    st.write("### Display User Feedback")
    for user, feedbacks in st.session_state.user_feedback.items():
        st.write(f"**{user}:**")
        for fb in feedbacks:
            st.write(f"- {fb}")

elif aview == "Registration":

    # Streamlit app
    st.title('Welcome to ChargeHub Berlin 🌩')

    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    def sign_up(username, email, password):
        try:
            response = requests.post(f"{API_BASE_URL}/signup", json={
                "username": username,
                "email": email,
                "password": password
            })
            if response.status_code == 201:
                st.success("Account created successfully! Please log in.")
            else:
                st.error(response.json().get("detail", "Signup failed."))
        except Exception as e:
            st.error(f"Error connecting to the server: {e}")

    def log_in(email, password):
        try:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                st.session_state.user_info = response.json()
                st.success("Login successful!")
            else:
                st.error(response.json().get("detail", "Login failed."))
        except Exception as e:
            st.error(f"Error connecting to the server: {e}")

    def reset_password(email):
        try:
            response = requests.post(f"{API_BASE_URL}/reset-password", json={"email": email})
            if response.status_code == 200:
                st.success("Password reset link sent to your email.")
            else:
                st.error(response.json().get("detail", "Failed to send reset link."))
        except Exception as e:
            st.error(f"Error connecting to the server: {e}")

    def log_out():
        st.session_state.user_info = None
        st.success("You have been logged out.")

    if st.session_state.user_info:
        # Logged-in user view
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info['email']}")

        if st.button("Log Out"):
            log_out()

    else:
        # Signup/Login view
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.subheader("Log In")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Log In"):
                log_in(email, password)

            if st.button("Forgot Password?"):
                reset_password(email)

        with tab2:
            st.subheader("Sign Up")
            username = st.text_input("Username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")

            if st.button("Sign Up"):
                sign_up(username, email, password)

    # Example FastAPI Backend Endpoints:
    # POST /signup - Create a new user account
    # POST /login - Authenticate user and return user info
    # POST /reset-password - Send a password reset email