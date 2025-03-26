# SDG-KG

**SDG-KG** is a spatio-temporal knowledge graph framework designed to compute Sustainable Development Goals (SDG) indicators from heterogeneous and open data sources. It enables users to import data, map it to SDG concepts, define use cases, and compute development indicators interactively.

## 🌍 Features

- Ingest structured or semi-structured data from various sources (CSV, APIs, databases, etc.)
- Create metadata and semantic graphs aligned with the SDG framework (Goal, Target, Indicator, Concept)
- Define spatial, temporal, and disaggregation parameters for use cases
- Automatically generate and execute indicator computation workflows
- Interactive visualization of the SDG graph and indicator results

## 🛠️ Technologies

- Python
- [Streamlit](https://streamlit.io/) for the user interface
- [rdflib](https://rdflib.readthedocs.io/) for RDF and graph modeling
- [pandas](https://pandas.pydata.org/) for data manipulation
- [st-link-analysis](https://pypi.org/project/st-link-analysis/) for interactive graph visualization

## 🚀 Getting Started

### Prerequisites

Make sure you have **Python 3.8+** installed.

### Installation

```bash
# Clone the repository
git clone https://github.com/wissalbenjira/SDG-KG.git
cd SDG-KG

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
