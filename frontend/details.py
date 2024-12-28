import streamlit as st
import pandas as pd

def display_details():
    st.subheader("Charging Station Details")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Available Charging Stations")
        st.bar_chart(pd.DataFrame({"Stations": [10, 15, 20]}, index=["Occupied", "Available", "Out of Service"]))

    with col2:
        st.markdown("### Total Points")
        st.metric("Points", "1,234")
        st.markdown("**Recent Achievements**")
        st.write("- Power User")
        st.write("- Earned +150 Points")
