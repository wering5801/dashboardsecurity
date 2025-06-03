import streamlit as st

def show_definitions_checkbox():
    """
    Provides a consistent checkbox for showing/hiding chart definitions across dashboards.
    Returns the checkbox state (True/False)
    """
    show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
    return show_definitions

def definition_card(title, definition, use_case):
    """
    Creates a consistent definition card to be used across dashboards
    """
    html = f"""
    <div class="definition-card">
        <h4>{title}</h4>
        <p><strong>Definition:</strong> {definition}</p>
        <p><strong>Use Case:</strong> {use_case}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def definition_card_css():
    """
    Returns CSS styling for definition cards
    """
    return """
    <style>
    .definition-card {
        padding: 15px;
        background-color: #f1f7fd;
        border-left: 4px solid #3498db;
        border-radius: 3px;
        margin-bottom: 15px;
        font-family: sans-serif;
    }
    .definition-card h4 {
        color: #2c3e50;
        margin-top: 0;
        margin-bottom: 10px;
        font-family: sans-serif;
    }
    .definition-card p {
        color: #34495e;
        margin-bottom: 5px;
        font-family: sans-serif;
    }
    </style>
    """