from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

def render_graph(nodes, edges, title="Graph Visualization", layout="cose"):
    import streamlit as st

    # Construire les éléments pour st-link-analysis
    elements = {
        "nodes": [],
        "edges": []
    }

    for node in nodes:
        node_type = node.title.split("[")[0] if "title" in node.to_dict() else "Node"
        elements["nodes"].append({
            "data": {
                "id": node.id,
                "label": node_type,
                "name": node.label
            }
        })

    for edge in edges:
        elements["edges"].append({
            "data": {
                "id": f"{edge.source}->{edge.target}",
                "label": edge.label,
                "source": edge.source,
                "target": edge.target
            }
        })

    # Styles
    node_styles = [
        NodeStyle("Goal", "#f16667", "name", "Goal"),
        NodeStyle("Target", "#f79767", "name", "Target"),
        NodeStyle("Indicator", "#ffc454", "name", "Indicator"),
        NodeStyle("Concept", "#8dcc93", "name", "Concept"),
        NodeStyle("Attribute", "#4c8eda", "name", "Attribute"),
        NodeStyle("Column", "#a5abb6", "name", "Column"),
        NodeStyle("Database", "#c990c0", "name", "Database"),
        NodeStyle("Node", "#cccccc", "name", "Node")
    ]

    edge_styles = [
        EdgeStyle("HAS_TARGET", caption="label", directed=True),
        EdgeStyle("HAS_INDICATOR", caption="label", directed=True),
        EdgeStyle("HAS_CONCEPT", caption="label", directed=True),
        EdgeStyle("HAS_INSTANCE", caption="label", directed=True),
        EdgeStyle("HAS_COLUMN", caption="label", directed=True),
        EdgeStyle("IS_MAPPED_TO", caption="label", directed=True),
        EdgeStyle("HAS_ATTRIBUTE", caption="label", directed=True),
    ]

    st.markdown(f"### ✅ {title}")
    st_link_analysis(elements, layout=layout, node_style=node_styles, edge_style=edge_styles)
