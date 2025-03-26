import os, json
import openai
import streamlit as st
from neo4j import GraphDatabase

CONFIG_FILE = "config.json"

default_config = {
    "neo4j": {
        "URI": "bolt://localhost:7687",
        "Username": "neo4j",
        "Password": "password"
    },
    "openai": {
        "api_type": "",
        "api_key": "",
        "api_version": "",
        "api_base": "",
        "engine": ""
    }
}

def load_config():
    def validate_and_fill_config(config):
        validated_config = default_config.copy()
        if config:
            for section in default_config:
                validated_config[section].update(config.get(section, {}))
        return validated_config

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return validate_and_fill_config(config)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    st.success("Configuration saved successfully!")

def test_neo4j_connection(uri, username, password):
    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            driver.verify_connectivity()
        st.success("Successfully connected to Neo4j!")
    except Exception as e:
        st.error(f"Neo4j connection failed: {e}")

def test_openai_connection(api_type, api_key, api_version, api_base, engine):
    try:
        openai.api_type = api_type
        openai.api_key = api_key
        openai.api_version = api_version
        openai.api_base = api_base
        openai.ChatCompletion.create(
            engine=engine,
            messages=[{"role": "system", "content": "ping"}]
        )
        st.success("Successfully connected to OpenAI!")
    except Exception as e:
        st.error(f"OpenAI connection failed: {e}")

def show_configuration(config):
    st.title("Configuration")

    st.subheader("Neo4j Settings")
    config["neo4j"]["URI"] = st.text_input("URI", config["neo4j"]["URI"])
    config["neo4j"]["Username"] = st.text_input("Username", config["neo4j"]["Username"])
    config["neo4j"]["Password"] = st.text_input("Password", config["neo4j"]["Password"], type="password")

    if st.button("Test Neo4j Connection"):
        test_neo4j_connection(config["neo4j"]["URI"], config["neo4j"]["Username"], config["neo4j"]["Password"])

    st.subheader("OpenAI Settings")
    config["openai"]["api_type"] = st.text_input("API Type", config["openai"]["api_type"])
    config["openai"]["api_key"] = st.text_input("API Key", config["openai"]["api_key"], type="password")
    config["openai"]["api_version"] = st.text_input("API Version", config["openai"]["api_version"])
    config["openai"]["api_base"] = st.text_input("API Base", config["openai"]["api_base"])
    config["openai"]["engine"] = st.text_input("Engine", config["openai"]["engine"])

    if st.button("Ping OpenAI's ChatCompletion module"):
        test_openai_connection(
            config["openai"]["api_type"],
            config["openai"]["api_key"],
            config["openai"]["api_version"],
            config["openai"]["api_base"],
            config["openai"]["engine"]
        )

    if st.button("Save"):
        save_config(config)
