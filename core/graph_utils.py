import streamlit as st
from streamlit_agraph import Node, Edge
from neo4j import GraphDatabase
import json
from core.functions import LABEL_COLORS  

def get_neo4j_session(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver.session(database="neo4j")

def add_to_graph(session, db_name, csv_path, geojson_path, encoding, separator, concept, column_mapping, return_subgraph=False):
    """ Inserts the database and column nodes into Neo4j and optionally returns the subgraph. """
    try:
        # Check if database already exists
        result = session.run(
            "MATCH (db:Database {id: $db_name}) RETURN db LIMIT 1",
            {"db_name": db_name}
        ).single()

        if result:
            st.warning(f"Database '{db_name}' already exists in the graph.")
            return ([], []) if return_subgraph else None

        # Create Database node
        session.run("""
            MERGE (db:Database {id: $db_name})
            SET db.geojson_filepath = $geojson_path,
                db.csv_filepath = $csv_path,
                db.csv_encoding = $encoding,
                db.csv_separator = $separator
        """, {
            "db_name": db_name,
            "geojson_path": geojson_path or "",
            "csv_path": csv_path or "",
            "encoding": encoding,
            "separator": separator
        })

        # Link Database to Concept
        session.run("""
            MATCH (c:Concept {id: $concept}), (db:Database {id: $db_name})
            MERGE (c)-[:HAS_INSTANCE]->(db)
        """, {"concept": concept, "db_name": db_name})

        # Create Column nodes and relationships
        for column, attribute in column_mapping.items():
            if attribute != "Drop":
                session.run("""
                    MERGE (col:Column {id: $column})
                    MERGE (db:Database {id: $db_name})
                    MERGE (attr:Attribute {id: $attribute})
                    MERGE (attr)<-[:IS_MAPPED_TO]-(col)
                    MERGE (db)-[:HAS_COLUMN]->(col)
                """, {
                    "column": column,
                    "db_name": db_name,
                    "attribute": attribute
                })

        st.success(f"Database '{db_name}' and its columns have been added to the graph!")

        if return_subgraph:
            # --- Query for subgraph related to the newly added database ---
            query = """
            MATCH (g:Goal)-->(t:Target)-->(i:Indicator {id: "11.2.1"})-[:HAS_CONCEPT]->(c:Concept)
                  -[:HAS_INSTANCE]->(db:Database {id: $db_name})-[:HAS_COLUMN]->(col:Column)
                  -[:IS_MAPPED_TO]->(attr:Attribute)
            RETURN g, t, i, db, c, col, attr
            """
            result = session.run(query, {"db_name": db_name})

            filtered_nodes = {}
            filtered_edges = []

            for record in result:
                g, t, i, db, c, col, attr = record["g"], record["t"], record["i"], record["db"], record["c"], record["col"], record["attr"]
                for node_obj in [g, t, i, db, c, col, attr]:
                    node_id = node_obj["id"]
                    node_label = node_obj.get("label", node_id)
                    if node_id not in filtered_nodes:
                        filtered_nodes[node_id] = Node(
                            id=node_id,
                            label=node_label,
                            color=LABEL_COLORS.get(list(node_obj.labels)[0], "#888"),
                            size=16,
                            font={"size": 12, "vadjust": -30}
                        )

                filtered_edges.extend([
                    Edge(source=g["id"], target=t["id"], label="HAS_TARGET"),
                    Edge(source=t["id"], target=i["id"], label="HAS_INDICATOR"),
                    Edge(source=i["id"], target=c["id"], label="HAS_CONCEPT"),
                    Edge(source=c["id"], target=db["id"], label="HAS_INSTANCE"),
                    Edge(source=db["id"], target=col["id"], label="HAS_COLUMN"),
                    Edge(source=col["id"], target=attr["id"], label="IS_MAPPED_TO"),
                    Edge(source=c["id"], target=attr["id"], label="HAS_ATTRIBUTE")
                ])

            return list(filtered_nodes.values()), filtered_edges

    except Exception as e:
        st.error(f"Error while adding to graph: {e}")
        return ([], []) if return_subgraph else None


def fetch_nodes(session):
    nodes = {}
    for label, color in LABEL_COLORS.items():
        query = f"MATCH (n:{label}) RETURN n"
        result = session.run(query)
        for record in result:
            node_data = record["n"]
            node_id = str(node_data["id"])
            node_label = node_data.get("name", node_id)
            description = node_data.get("description", "No description available.")
            title = f"{label}[id:{node_id}]\n{description}"
            image_url = node_data.get("image", None)

            if image_url:
                nodes[node_id] = Node(
                    id=node_id, label="", title=title,
                    shape="image", image=image_url, size=80
                )
            else:
                nodes[node_id] = Node(
                    id=node_id, label=node_label, title=title,
                    color=color, size=16, font={"size": 12, "vadjust": -30}
                )
    return nodes

def fetch_edges(session):
    query = "MATCH p=()-[r]->() RETURN p"
    result = session.run(query)
    edges = []
    for record in result:
        for rel in record["p"].relationships:
            edges.append(Edge(
                source=str(rel.start_node["id"]),
                target=str(rel.end_node["id"]),
                label=rel.type,
                font={"size": 6}
            ))
    return edges

def load_sdg_data(session, file_path="sdg_initt.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for node in data["nodes"]:
            properties = {k: v for k, v in node.items() if k not in ["id", "type"]}
            query = f"""
                MERGE (n:{node['type']} {{id: $id}})
                SET n += $properties
            """
            session.run(query, id=node["id"], properties=properties)

        for edge in data["edges"]:
            query = """
                MATCH (a {id: $source}), (b {id: $target})
                MERGE (a)-[:{label}]->(b)
            """.replace("{label}", edge["label"])
            session.run(query, source=edge["source"], target=edge["target"])

        st.success("SDG data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading SDG data: {e}")
