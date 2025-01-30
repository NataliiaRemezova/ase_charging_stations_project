import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
from .timer_utils import timer

# ------------------------------------------------------------------------------
# Data Processing Functions

def sort_by_plz_add_geometry(df, geo_df, config):
    """Sorts a DataFrame by postal code (PLZ) and adds geometry data."""
    df_sorted = df.copy().sort_values(by='PLZ').reset_index(drop=True)
    merged_df = df_sorted.merge(geo_df, on=config["geocode"], how='left').dropna(subset=['geometry'])
    merged_df['geometry'] = gpd.GeoSeries.from_wkt(merged_df['geometry'])
    return gpd.GeoDataFrame(merged_df, geometry='geometry')

@timer
def preprocess_lstat(df, geo_df, config):
    """Preprocesses the dataframe from Ladesaeulenregister_SEP.xlsx."""
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    
    if 'Nennleistung Ladeeinrichtung [kW]' not in df.columns:
        st.warning("Column 'Nennleistung Ladeeinrichtung [kW]' not found.")
        return None
    
    df = df[['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    df.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)
    
    df['Breitengrad'] = df['Breitengrad'].astype(str).str.replace(',', '.').astype(float, errors='ignore')
    df['Längengrad'] = df['Längengrad'].astype(str).str.replace(',', '.').astype(float, errors='ignore')
    
    df = df[(df["Bundesland"] == 'Berlin') & (df["PLZ"].between(10115, 14200))]
    df['KW'] = pd.to_numeric(df['KW'], errors='coerce').dropna()
    
    return sort_by_plz_add_geometry(df, geo_df, config)

@timer
def count_plz_occurrences(df):
    """Counts occurrences of loading stations per PLZ and retains KW information."""
    return df.groupby(['PLZ', 'KW']).agg(Number=('PLZ', 'count'), geometry=('geometry', 'first')).reset_index()

@timer
def preprocess_resid(df, geo_df, config):
    """Preprocesses the dataframe from plz_einwohner.csv."""
    df = df[['plz', 'einwohner', 'lat', 'lon']].rename(columns={"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"})
    df['Breitengrad'] = df['Breitengrad'].astype(str).str.replace(',', '.')
    df['Längengrad'] = df['Längengrad'].astype(str).str.replace(',', '.')
    df = df[df["PLZ"].between(10000, 14200)]
    return sort_by_plz_add_geometry(df, geo_df, config)

# ------------------------------------------------------------------------------
# Streamlit Application

def create_streamlit_map(df1, df2, by_kw=False):
    """Creates a Streamlit map visualization for electric charging stations and residents."""
    st.title('Heatmaps: Electric Charging Stations and Residents')
    layer_selection = st.radio("Select Layer", ("Residents", "Charging Stations" if not by_kw else "Charging Stations by KW"))
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        if 'Einwohner' in df2.columns:
            color_map = LinearColormap(['yellow', 'red'], vmin=df2['Einwohner'].min(), vmax=df2['Einwohner'].max())
            for _, row in df2.iterrows():
                folium.GeoJson(row['geometry'],
                               style_function=lambda x, color=color_map(row['Einwohner']): {
                                   'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
                               },
                               tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}").add_to(m)
        else:
            st.warning("Residents data is not available.")
    else:
        if by_kw:
            for kw in df1['KW'].unique():
                kw_data = df1[df1['KW'] == kw]
                if not kw_data.empty:
                    feature_group = folium.FeatureGroup(name=f'KW {kw}')
                    color_map = LinearColormap(['yellow', 'red'], vmin=kw_data['Number'].min(), vmax=kw_data['Number'].max())
                    for _, row in kw_data.iterrows():
                        folium.GeoJson(row['geometry'],
                                       style_function=lambda x, color=color_map(row['Number']): {
                                           'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
                                       },
                                       tooltip=f"PLZ: {row['PLZ']}, KW: {kw}, Number: {row['Number']}").add_to(feature_group)
                    feature_group.add_to(m)
        else:
            color_map = LinearColormap(['yellow', 'red'], vmin=df1['Number'].min(), vmax=df1['Number'].max())
            for _, row in df1.iterrows():
                folium.GeoJson(row['geometry'],
                               style_function=lambda x, color=color_map(row['Number']): {
                                   'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
                               },
                               tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}").add_to(m)

    folium.LayerControl().add_to(m)
    color_map.add_to(m)
    folium_static(m, width=800, height=600)
