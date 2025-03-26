import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import folium
from streamlit_folium import st_folium

@st.cache_data
def load_data():
    population_df = pd.read_csv("data/Population (2017-2021, INSEE).csv", dtype={'CODE_IRIS': str, 'CODE_COMMUNE': str})
    population_gdf = gpd.read_file("data/Population (2017-2021, INSEE).geojson")
    transport_df = pd.read_csv("data/PublicTransportStop (2014-2024, OpenStreetMap).csv", dtype={'osm_id': str})
    transport_gdf = gpd.read_file("data/PublicTransportStop (2014-2024, OpenStreetMap).geojson")
    distances_df = pd.read_csv("data/distances_2017_2021.csv", dtype={'population_id': str, 'transport_id': str})
    return population_df, population_gdf, transport_df, transport_gdf, distances_df

def run():
    st.title("Compute an Indicator")
    st.subheader("Indicator 11.2.1")

    population_df, population_gdf, transport_df, transport_gdf, distances_df = load_data()

    st.header("1. Configure Filters")
    spatial_level = st.radio("Select Spatial Level", ["COMMUNE", "IRIS"])
    years = sorted(population_df['ANNEE_DONNEES'].unique())
    selected_years = st.multiselect("Select Years", years, default=years)

    transport_classes = sorted(transport_df['fclass'].unique())
    selected_transport_classes = st.multiselect("Select Transport Classes", transport_classes, default=transport_classes)

    modes_of_transport = sorted(population_df['MODE_TRANS'].unique())
    selected_modes_of_transport = st.multiselect("Select Modes of Transport", modes_of_transport, default=modes_of_transport)

    population_df = population_df[
        population_df['ANNEE_DONNEES'].isin(selected_years) &
        population_df['MODE_TRANS'].isin(selected_modes_of_transport)
    ]
    transport_df = transport_df[
        transport_df['fclass'].isin(selected_transport_classes) &
        transport_df['year'].isin(selected_years)
    ]

    if spatial_level == "COMMUNE":
        population_df = population_df.drop("CODE_IRIS", axis=1).groupby(["CODE_COMMUNE", "ANNEE_DONNEES", "MODE_TRANS"]).sum("VALEUR").reset_index()
        merge_key = "CODE_COMMUNE"
    else:
        population_df = population_df.drop("CODE_COMMUNE", axis=1)
        merge_key = "CODE_IRIS"

    population_gdf = population_gdf.merge(population_df, left_on='id', right_on=merge_key)
    transport_gdf = transport_gdf.merge(transport_df, left_on='id', right_on='osm_id')

    min_distances = distances_df.groupby('population_id')['distance'].min().reset_index()
    min_distances = min_distances.merge(distances_df, on=['population_id', 'distance'])
    min_distances = min_distances[min_distances['transport_id'].isin(transport_gdf['id'])]
    min_distances = min_distances[min_distances['population_id'].isin(population_gdf['id'])]

    transport_gdf = transport_gdf[transport_gdf['id'].isin(min_distances['transport_id'])]
    population_gdf = population_gdf.merge(min_distances, left_on='id', right_on='population_id').to_crs("EPSG:4326")

    st.header("2. Select Cities and Threshold")
    city_options = np.unique([f'{x["name"]} ({x["id"]})' for _, x in population_gdf.iterrows()])
    selected_cities = st.multiselect("Select Cities", city_options)
    threshold = st.slider("Select Distance Threshold (meters)", 1, 1000, 100)

    selected_city_ids = [x.split('(')[-1].strip(')') for x in selected_cities]
    filtered_population_gdf = population_gdf[population_gdf['id'].isin(selected_city_ids)]

    st.header("3. Indicator Result")
    if not filtered_population_gdf.empty:
        filtered_population_gdf['under_threshold'] = filtered_population_gdf['distance'] <= threshold
        proportion_under_threshold = filtered_population_gdf.groupby('ANNEE_DONNEES')['under_threshold'].mean()

        st.metric("Mean Indicator Value", round(proportion_under_threshold.mean(), 3))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(proportion_under_threshold.index, proportion_under_threshold.values, marker='o', linestyle='-', color='steelblue')
        ax.set_title("Proportion of Population with Access to Public Transport", fontsize=14)
        ax.set_xlabel("Year")
        ax.set_ylabel("Proportion")

        if 2024 in range(min(proportion_under_threshold.index), max(proportion_under_threshold.index) + 1):
            ax.axvline(x=2024, color='red', linestyle='--', label='Paris Olympics 2024')
            ax.legend()

        last_year = proportion_under_threshold.index[-1]
        last_val = proportion_under_threshold.values[-1]
        ax.annotate(f"{last_val:.2f}", xy=(last_year, last_val), xytext=(last_year, last_val + 0.02),
                    ha='center', fontsize=10, arrowprops=dict(arrowstyle="->", color='black'))

        st.pyplot(fig)
    else:
        st.info("Please select at least one city to compute the indicator.")

    st.header("4. Population & Distance Maps")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Population Distribution**")
        m1 = folium.Map(
            location=[population_gdf.geometry.centroid.y.mean(), population_gdf.geometry.centroid.x.mean()],
            zoom_start=11,
            tiles="CartoDB positron"
        )
        folium.Choropleth(
            geo_data=population_gdf,
            data=population_gdf,
            columns=["id", "VALEUR"],
            key_on="feature.properties.id",
            fill_color="YlGnBu",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Population"
        ).add_to(m1)
        st_folium(m1, width=450, height=500)

    with col2:
        st.markdown("**Distance to Nearest Public Transport Stop**")
        m2 = folium.Map(
            location=[population_gdf.geometry.centroid.y.mean(), population_gdf.geometry.centroid.x.mean()],
            zoom_start=11,
            tiles="CartoDB positron"
        )
        folium.Choropleth(
            geo_data=population_gdf,
            data=population_gdf,
            columns=["id", "distance"],
            key_on="feature.properties.id",
            fill_color="OrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Distance (m)"
        ).add_to(m2)
        st_folium(m2, width=450, height=500)
