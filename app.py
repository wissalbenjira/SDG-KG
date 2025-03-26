import streamlit as st
from config.config_handler import load_config
from scenario import visualize_sdgraph, import_database, define_use_case, compute_indicator
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import json

st.set_page_config(page_title="SDGraph Tool", layout="wide")
st.sidebar.title("Navigation")
st.logo("data/logo2.png", size="large")

page = st.sidebar.radio("Go to:", [
    "Configuration",
    "Visualize the SDGraph",
    "Import a Database",
    "Define a Use Case",
    "Compute an Indicator"
])

config = load_config()

if page == "Configuration":
    with open("sdg_initt_reformatted.json", "r", encoding="utf-8") as f:
        elements = json.load(f)

    # 🎛️ Extraire types de nœuds
    all_types = sorted(set(n["data"]["label"] for n in elements["nodes"]))
    selected_types = st.multiselect("Filter node types", all_types, default=all_types[:3])

    # 🔍 Filtrage dynamique
    filtered_nodes = [n for n in elements["nodes"] if n["data"]["label"] in selected_types]
    visible_ids = {n["data"]["id"] for n in filtered_nodes}
    filtered_edges = [
        e for e in elements["edges"]
        if e["data"]["source"] in visible_ids and e["data"]["target"] in visible_ids
    ]

    filtered_elements = {"nodes": filtered_nodes, "edges": filtered_edges}

    # 🎨 Styles des nœuds
    node_styles = [
        NodeStyle(label='Goal', color='#f16667', caption='name', icon="wallet"),
        NodeStyle(label='Target', color='#f79767', caption='name', icon="flag"),
        NodeStyle(label='Indicator', color='#ffc454', caption='name', icon="monitor"),
        NodeStyle(label='Concept', color='#8dcc93', caption='id'),
        NodeStyle(label='Attribute', color='#4c8eda', caption='id'),
        NodeStyle(label='Column', color='#a5abb6', caption='id'),
        NodeStyle(label='Database', color='#c990c0', caption='id'),
    ]

    # 🎨 Styles des arêtes
    edge_styles = [
        EdgeStyle("HAS_TARGET", caption="label", directed=True),
        EdgeStyle("HAS_INDICATOR", caption="label", directed=True),
        EdgeStyle("HAS_CONCEPT", caption="label", directed=True),
        EdgeStyle("HAS_INSTANCE", caption="label", directed=True),
        EdgeStyle("HAS_COLUMN", caption="label", directed=True),
        EdgeStyle("IS_MAPPED_TO", caption="label", directed=True),
        EdgeStyle("HAS_ATTRIBUTE", caption="label", directed=True)
    ]

    # ⚙️ Layout plus léger
    layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

    # 🚀 Affichage
    st.markdown("### 📊 SDGraph Preview")
    st_link_analysis(filtered_elements, layout, node_styles, edge_styles, height=800)

    # 🔧 Configuration de base
    from config.config_handler import show_configuration
    show_configuration(config)

elif page == "Visualize the SDGraph":
    visualize_sdgraph.run(config)

elif page == "Import a Database":
    import_database.run(config)

elif page == "Define a Use Case":
    define_use_case.run()

elif page == "Compute an Indicator":
    compute_indicator.run()
