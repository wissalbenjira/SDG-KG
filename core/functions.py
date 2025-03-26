import json
import openai
import folium
import matplotlib.pyplot as plt
import streamlit as st

LABEL_COLORS = {
    "Goal": "#f16667",
    "Target": "#f79767",
    "Indicator": "#ffc454",
    "Concept": "#8dcc93",
    "Attribute": "#4c8eda",
    "Column": "#a5abb6",
    "Database": "#c990c0"
}

def Mapp_columns_with_openai(df, attributes, config):
    """Uses OpenAI to map DataFrame columns to attributes."""
    unique_values = {
        col: df[col].dropna().unique()[:10].tolist()
        for col in df.columns
    }

    prompt = f"""
    You are an AI assistant that maps CSV columns to a predefined list of attributes.
    The user has provided a DataFrame with the following columns and example unique values:

    {json.dumps(unique_values, indent=2)}

    The available attributes to map to are:
    {attributes}

    Return a JSON object mapping each column name to either one of the attributes or "Drop".
    """

    try:
        openai.api_type = config["openai"]["api_type"]
        openai.api_key = config["openai"]["api_key"]
        openai.api_version = config["openai"]["api_version"]
        openai.api_base = config["openai"]["api_base"]
        response = openai.ChatCompletion.create(
            engine=config["openai"]["engine"],
            temperature=0,
            messages=[{"role": "system", "content": "You are an expert data classifier."},
                      {"role": "user", "content": prompt}]
        )
        if "choices" in response and response["choices"]:
            return json.loads(response["choices"][0]["message"]["content"])
        else:
            return {"error": "Empty or invalid OpenAI response"}
    except Exception as e:
        return {"error": str(e)}

def plot_map(p, t, s, selected_year):
    m = folium.Map(location=[0, 0], zoom_start=2)

    def filter_by_year(gdf, time_col):
        if gdf is not None and time_col in gdf.columns:
            return gdf[gdf[time_col].dt.year == selected_year]
        return gdf

    p = filter_by_year(p, "ANNEE_DONNEES")
    t = filter_by_year(t, "year").head(100) if t is not None else None
    s = filter_by_year(s, "year").head(100) if s is not None else None

    def add_gdf_to_map(gdf, color):
        if gdf is not None:
            for _, row in gdf.iterrows():
                geom = row.geometry
                if geom.geom_type == "Point":
                    folium.Marker([geom.y, geom.x], icon=folium.Icon(color=color)).add_to(m)
                else:
                    folium.GeoJson(geom, style_function=lambda x: {"color": color}).add_to(m)

    add_gdf_to_map(p, "blue")
    add_gdf_to_map(t, "green")
    add_gdf_to_map(s, "red")

    return m

def plot_accessibility_graph(p):
    if "ANNEE_DONNEES" in p.columns and "VALEUR" in p.columns and "is_accessible" in p.columns:
        p["year"] = p["ANNEE_DONNEES"].dt.year
        grouped = p.groupby("year").agg(
            total_VALEUR=("VALEUR", "sum"),
            accessible_VALEUR=("VALEUR", lambda x: x[p["is_accessible"]].sum())
        )
        grouped["ratio"] = grouped["accessible_VALEUR"] / grouped["total_VALEUR"]

        fig, ax = plt.subplots()
        grouped["ratio"].plot(kind="line", marker="o", ax=ax)
        ax.set_ylabel("Accessibility Ratio")
        ax.set_title("Accessible VALEUR over Total VALEUR by Year")
        st.pyplot(fig)
