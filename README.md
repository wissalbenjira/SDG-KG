# SDG-KG

**SDG-KG** is a spatio-temporal knowledge graph framework designed to compute Sustainable Development Goals (SDG) indicators from heterogeneous and open data sources. It enables users to import data, map it to SDG concepts, define use cases, and compute development indicators interactively.

## Technologies

- Python
- [Streamlit](https://streamlit.io/) for the user interface
- [Neo4j](https://neo4j.com/docs/) for graph modeling
- [pandas](https://pandas.pydata.org/) for data manipulation
- [st-link-analysis](https://pypi.org/project/st-link-analysis/) for interactive graph visualization

## Getting Started

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
```

### Run the App

```bash
py -m streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## 📂 Project Structure

```
SDG-KG/
│
├── app.py                        
├── data/                         
├── scenario/   
|── core/
|── scenario                
├── requirements.txt              
└── README.md
```

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 🙋 Author

Developed by [Wissal Benjira](https://github.com/wissalbenjira)  
---
