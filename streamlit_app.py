import streamlit as st
import requests
from fastapi import FastAPI

# Set up the Streamlit app title and description
st.title("Berlin Heatmap Charging Stations")
st.write("Getting the nearest charging station according to the user by PLZ")

# Define the FastAPI backend URL
backend_url = "http://127.0.0.1:8000"

# TODO: create server runner and database connection
app = FastAPI()

@app.get("/api/healthcheck")
async def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Healthcheck endpoint
if st.sidebar.button("Check Backend Health"):
    health_response = requests.get(f"{backend_url}/api/healthcheck")
    if health_response.status_code == 200:
        st.sidebar.success("Backend is healthy!")
    else:
        st.sidebar.error("Backend health check failed.")
