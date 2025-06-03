import streamlit as st

# This must be the first Streamlit command
st.set_page_config(
    page_title="Security Operations Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from theme_utils import setup_theme, toggle_theme
#from copy_utils import add_copy_button_to_figure, copy_all_button

# Apply the current theme
plt_style = setup_theme()
plt.style.use(plt_style)

# Import dashboard modules
from host_analysis import host_analysis_dashboard
#from detection_analysis import detection_analysis_dashboard 
#from severity_analysis import severity_analysis_dashboard
from time_based_analysis import time_based_analysis_dashboard
from vulnerability_dashboard import vulnerability_dashboard
from three_month_trend import three_month_trend_dashboard
from detection_summary import detection_summary_dashboard

# Configure sidebar
st.sidebar.title("Security Dashboard")

# Theme toggle button
st.sidebar.button("Toggle Dark/Light Mode", on_click=toggle_theme, key="theme_toggle")

# Dashboard selection
dashboard = st.sidebar.selectbox(
    "Select Dashboard",
    ["Host Analysis", #"Detection Analysis", 
     #"Severity Analysis", 
     "Detection and Severity Analysis Analysis", "Time-based Analysis",
     "Vulnerability Analysis", "3-Month Trend Analysis"
     ],
    key="dashboard_selector"
)

# Call the selected dashboard function
if dashboard == "Host Analysis":
    host_analysis_dashboard()
elif dashboard == "Detection and Severity Analysis Analysis":
    detection_summary_dashboard()
#elif dashboard == "Detection Analysis":
    #detection_analysis_dashboard()
#elif dashboard == "Severity Analysis":
    #severity_analysis_dashboard()
elif dashboard == "Time-based Analysis":
    time_based_analysis_dashboard()
elif dashboard == "Vulnerability Analysis":
    vulnerability_dashboard()
elif dashboard == "3-Month Trend Analysis":
    three_month_trend_dashboard()
