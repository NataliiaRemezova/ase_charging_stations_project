import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import shape
import folium
from collections import defaultdict
from folium.plugins import HeatMap
from core import methods as m1
from core import HelperTools as ht
from config import pdict



# Load data
df_geodat_plz = pd.read_csv('datasets/geodata_berlin_plz.csv', sep=';')  # Geospatial data
df_lstat = pd.read_excel('datasets/Ladesaeulenregister_SEP.xlsx', header=10)
df_residents = pd.read_csv('datasets/plz_einwohner.csv')  # Residents data



# Data preprocessing
def preprocess_data():
    # Rename columns if needed to maintain consistency
    if 'Latitude' not in df_geodat_plz.columns:
        df_geodat_plz.rename(columns={'Breitengrad': 'Latitude', 'Längengrad': 'Longitude'}, inplace=True)
    return df_geodat_plz, df_lstat

df_geodat_plz, df_lstat = preprocess_data()

# Set page config
st.set_page_config(page_title="ChargeHub Berlin 🌩", layout="wide")

# Initialize session state
if "locations" not in st.session_state:
    st.session_state.locations = []

if "postal_code" not in st.session_state:
    st.session_state.postal_code = "10117"

if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = defaultdict(list)

if "total_ratings" not in st.session_state:
    st.session_state.total_ratings = defaultdict(list)

# Sidebar navigation
st.sidebar.title("Ansicht wählen")
aview = st.sidebar.radio(
    "", ["Home", "Heatmaps", "Bezirke", "Postleitzahlen", "Details", "Charging Station Management", "My Account", "Registration"]
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

    postal_code = st.text_input("Postleitzahl eingeben", st.session_state.postal_code)
    if st.button("Suchen"):
        st.session_state.postal_code = postal_code
        st.session_state.locations = [
            (52.5206, 13.4098, "Normallader"),
            (52.5155, 13.3777, "Schnelllader"),
            (52.5246, 13.4285, "Normallader"),
        ]

    if st.session_state.locations:
        latitudes = [loc[0] for loc in st.session_state.locations]
        longitudes = [loc[1] for loc in st.session_state.locations]
        center_lat = sum(latitudes) / len(latitudes)
        center_lon = sum(longitudes) / len(longitudes)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

        for lat, lon, label in st.session_state.locations:
            folium.Marker(
                location=[lat, lon], 
                popup=folium.Popup(label, parse_html=True), 
                tooltip=label
            ).add_to(m)

        st_folium(m, width=800, height=500)

        st.markdown("**Gefundene Ladestationen: 54**")
        st.markdown("- **Normallader (≤ 22 kW):** 44")
        st.markdown("- **Schnelllader (22-43 kW):** 10")
        st.markdown("- **Alle Ladestationen anzeigen:** [hier klicken](#)")
    else:
        st.write("Keine Ergebnisse verfügbar. Bitte suchen Sie erneut.")

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

elif aview == "Bezirke":
    st.subheader("Ladestationen nach Bezirken")
    st.write("Kartenansicht nach Bezirken")

elif aview == "Charging Station Management":
    st.subheader("Charging Station Management")

    st.write("### Storing Data About Charging Station")
    station = st.text_input("Enter station name:")
    rating = st.slider("Rate the station (1-5):", 1, 5, 3)
    if st.button("Submit Rating"):
        st.session_state.total_ratings[station].append(rating)
        st.success(f"Rating for {station} submitted!")

    st.write("### Display Ratings")
    for station, ratings in st.session_state.total_ratings.items():
        avg_rating = sum(ratings) / len(ratings)
        st.write(f"{station}: Average Rating = {avg_rating:.2f} ({len(ratings)} ratings)")

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