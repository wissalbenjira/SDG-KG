import streamlit as st
from core.graph_utils import get_neo4j_session, fetch_nodes, fetch_edges, load_sdg_data
from core.functions import LABEL_COLORS
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

def run(config):
    st.title("Visualize the SDGraph")

    try:
        session = get_neo4j_session(
            config["neo4j"]["URI"],
            config["neo4j"]["Username"],
            config["neo4j"]["Password"]
        )

        if st.button("Reinitialize the Graph"):
            try:
                session.run("MATCH (n) DETACH DELETE n")
                st.success("Graph cleared. Reloading SDG data...")
                load_sdg_data(session)
            except Exception as e:
                st.error(f"Error reinitializing graph: {e}")

        all_nodes = fetch_nodes(session)
        all_edges = fetch_edges(session)

        all_node_types = list(LABEL_COLORS.keys())
        selected_types = st.multiselect("Filter by node type:", all_node_types, default=["Goal", "Target", "Indicator"])

        # Filtrer les noeuds par type
        filtered_nodes = {
            node_id: node for node_id, node in all_nodes.items()
            if node.to_dict()["title"].split("[")[0] in selected_types
        }

        visible_ids = set(filtered_nodes.keys())

        # Garder les edges connectés à des noeuds visibles
        filtered_edges = [
            edge for edge in all_edges
            if edge.source in visible_ids and edge.target in visible_ids
        ]

        # Convertir en format st-link-analysis
        elements = {
            "nodes": [
                {
                    "data": {
                        "id": node.id,
                        "label": node.title.split("[")[0],
                        "name": node.label
                    }
                }
                for node in filtered_nodes.values()
            ],
            "edges": [
                {
                    "data": {
                        "id": f"e{i}",
                        "label": edge.label,
                        "source": edge.source,
                        "target": edge.target
                    }
                }
                for i, edge in enumerate(filtered_edges, 1)
            ]
        }

        # Styles des nœuds
        node_styles = [
            NodeStyle(label='Goal', color='#f16667', caption='name', icon="wallet"),
            NodeStyle(label='Target', color='#f79767', caption='name', icon="flag"),
            NodeStyle(label='Indicator', color='#ffc454', caption='name', icon="monitor"),
            NodeStyle(label='Concept', color='#8dcc93', caption='id'),
            NodeStyle(label='Attribute', color='#4c8eda', caption='id'),
            NodeStyle(label='Column', color='#a5abb6', caption='id'),
            NodeStyle(label='Database', color='#c990c0', caption='id'),
        ]

        # Styles des arêtes
        edge_styles = [
            EdgeStyle("HAS_TARGET", caption="label", directed=True),
            EdgeStyle("HAS_INDICATOR", caption="label", directed=True),
            EdgeStyle("HAS_CONCEPT", caption="label", directed=True),
            EdgeStyle("HAS_INSTANCE", caption="label", directed=True),
            EdgeStyle("HAS_COLUMN", caption="label", directed=True),
            EdgeStyle("IS_MAPPED_TO", caption="label", directed=True),
            EdgeStyle("HAS_ATTRIBUTE", caption="label", directed=True),
        ]

        layout = {
            "name": "concentric",
            "animate": "end",
            "nodeDimensionsIncludeLabels": False
        }

        # Affichage
        st.markdown("### 📊 SDGraph from Neo4j")
        st_link_analysis(elements, layout, node_styles, edge_styles, height=800)

    except Exception as e:
        st.error(f"An error occurred: {e}")
