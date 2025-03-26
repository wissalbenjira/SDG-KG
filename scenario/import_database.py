import streamlit as st
import pandas as pd
from core.graph_utils import get_neo4j_session, add_to_graph
from core.functions import Mapp_columns_with_openai
from streamlit_agraph import agraph, Config

def run(config):
    st.title("Load Data - Import a Database")

    # --- Full reset requested ---
    if "reset_import" not in st.session_state:
        st.session_state.reset_import = False

    if st.session_state.reset_import:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- Input: Name of database with key ---
    db_name = st.text_input("Name of the database:", key="db_name")

    try:
        session = get_neo4j_session(
            config["neo4j"]["URI"],
            config["neo4j"]["Username"],
            config["neo4j"]["Password"]
        )

        concepts = session.run("MATCH (c:Concept) RETURN c.id").values()
        concepts = [c[0] for c in concepts] if concepts else []

        if concepts:
            selected_concept = st.selectbox("Select a Concept:", concepts, key="concept_select")

            attributes = session.run(
                "MATCH (c:Concept {id: $concept})-[:HAS_ATTRIBUTE]->(a:Attribute) RETURN a.id",
                {"concept": selected_concept}
            ).values()
            attributes = [a[0] for a in attributes] if attributes else []

            geojson_file = st.file_uploader("Upload GeoJSON File", type=["geojson"], key="geojson_file")
            csv_file = st.file_uploader("Upload CSV File", type=["csv"], key="csv_file")

            geojson_path = f"data/{geojson_file.name}" if geojson_file else None
            csv_path = f"data/{csv_file.name}" if csv_file else None

            if db_name and st.session_state.get("prev_db_name") != db_name:
                st.session_state.column_mapping = {}

            if csv_file and st.session_state.get("prev_csv_name") != csv_file.name:
                st.session_state.column_mapping = {}

            st.session_state.prev_db_name = db_name
            st.session_state.prev_csv_name = csv_file.name if csv_file else None

            if csv_file:
                encoding = st.selectbox("Select file encoding:", ["utf-8", "latin-1"], key="encoding")
                separator = st.text_input("Enter CSV separator:", value=",", key="separator")

                try:
                    df = pd.read_csv(csv_file, encoding=encoding, sep=separator)
                    st.write("Preview of the uploaded CSV file:")
                    st.dataframe(df.head())

                    if not attributes:
                        st.warning("No attributes found for the selected concept.")
                    else:
                        st.subheader("Column Mapping")
                        options = ["Drop"] + attributes

                        if "column_mapping" not in st.session_state:
                            st.session_state.column_mapping = {col: "Drop" for col in df.columns}

                        if st.button("Mapp columns using OpenAI"):
                            mapping = Mapp_columns_with_openai(df, attributes, config)
                            if "error" in mapping:
                                st.error(mapping["error"])
                            else:
                                st.session_state.column_mapping = mapping
                                st.success("Mapping updated successfully!")

                        for col in df.columns:
                            st.session_state.column_mapping[col] = st.selectbox(
                                f"Mapp column: {col}",
                                options,
                                index=options.index(st.session_state.column_mapping.get(col, "Drop")),
                                key=f"select_{col}"
                            )

                        if st.button("Add to the graph and show subgraph"):
                            if not db_name:
                                st.error("Please provide a database name.")
                            else:
                                nodes, edges = add_to_graph(
                                    session, db_name, csv_path, geojson_path, encoding, separator,
                                    selected_concept, st.session_state.column_mapping,
                                    return_subgraph=True
                                )

                                st.markdown("### ✅ Subgraph Visualization")
                                config_graph = Config(
                                    height=600,
                                    width=1000,
                                    nodeHighlightBehavior=True,
                                    highlightColor="#F7A7A6",
                                    directed=True,
                                    collapsible=True
                                )
                                agraph(nodes=nodes, edges=edges, config=config_graph)

                                # ✅ Flag pour afficher le bouton reset
                                st.session_state.import_done = True

                except Exception as e:
                    st.error(f"Error loading CSV file: {e}")

        else:
            st.warning("No concepts found in the database.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

    # --- Show reset button only after import ---
    if st.session_state.get("import_done", False):
        st.markdown("---")
        if st.button("Start a New Import"):
            st.session_state.reset_import = True
            st.rerun()