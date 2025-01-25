import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from backend.core import methods as m1
print(sys.path)

from backend.config import pdict

def display_heatmaps(df_lstat, df_geodat_plz, df_residents):
    st.subheader("Electric Charging Station Heatmaps")
    function_selection = st.radio(
        "Select Visualization Type",
        [
            "Heatmap: Electric Charging Stations and Residents",
            "Heatmap: Electric Charging Stations by Power (KW) and Residents"
        ]
    )

    gdf_lstat = m1.preprocess_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
    gdf_residents2 = m1.preprocess_resid(df_residents, df_geodat_plz, pdict)

    if function_selection == "Heatmap: Electric Charging Stations and Residents":
        m1.create_streamlit_map(gdf_lstat3, gdf_residents2)
    else:
        m1.create_streamlit_map(gdf_lstat3, gdf_residents2, True)
