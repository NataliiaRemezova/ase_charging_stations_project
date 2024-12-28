import os
import pandas as pd
import geopandas as gpd
import streamlit as st
from core import methods as m1
from core import HelperTools as ht
from config import pdict

@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""
    # Load data
    df_geodat_plz = pd.read_csv('datasets/geodata_berlin_plz.csv', sep=';')
    df_lstat = pd.read_excel('datasets/Ladesaeulenregister_SEP.xlsx', header=10)
    df_residents = pd.read_csv('datasets/plz_einwohner.csv')

    # Data Quality Checks
    quality_issues_lstat = ht.check_data_quality(df_lstat, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]'],
                                                 {'Postleitzahl': int, 'Bundesland': str, 'Breitengrad': float, 'Längengrad': float, 'Nennleistung Ladeeinrichtung [kW]': float},
                                                 {'Postleitzahl': (10000, 14200), 'Nennleistung Ladeeinrichtung [kW]': (0, 1000)})
    if quality_issues_lstat:
        print("Data Quality Issues for Charging Stations:", quality_issues_lstat)

    quality_issues_residents = ht.check_data_quality(df_residents, ['plz', 'einwohner', 'lat', 'lon'],
                                                     {'plz': int, 'einwohner': int, 'lat': float, 'lon': float},
                                                     {'plz': (10000, 14200), 'einwohner': (0, 50000)})
    if quality_issues_residents:
        print("Data Quality Issues for Residents Data:", quality_issues_residents)

    # Preprocess data
    gdf_lstat = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

    # Streamlit app logic
    st.title('Berlin Electric Charging Station Heatmaps')
    function_selection = st.radio(
        "Select Visualization Type",
        (
            "Heatmap: Electric Charging Stations and Residents",
            "Heatmap: Electric Charging Stations by KW and Residents"
        )
    )

    if function_selection == "Heatmap: Electric Charging Stations and Residents":
        m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)
    else:
        m1.make_streamlit_electric_Charging_resid_by_kw(gdf_lstat3, gdf_residents2)


if __name__ == "__main__":
    main()

