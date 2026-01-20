import sys
import io

# Force UTF-8 encoding for stdout/stderr on Windows to handle emoji characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import streamlit as st
from streamlit_echarts import st_echarts
import numpy as np
import pandas as pd

# This must be the first Streamlit command
st.set_page_config(
    page_title="Security Operations Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
from theme_utils import setup_theme
from auth import require_authentication

# Configure theme settings
theme = setup_theme()

# ==============================================
# AUTHENTICATION - REQUIRED FOR ALL PAGES
# ==============================================
# This will show login page if not authenticated
# and stop execution until user logs in
if not require_authentication():
    st.stop()

# Default ECharts options
def get_default_echarts_options(title, x_label, y_label):
    return {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "toolbox": {
            "feature": {
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {}
            }
        },
        "xAxis": {
            "type": "category",
            "name": x_label,
            "nameLocation": "middle",
            "nameGap": 30
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "nameLocation": "middle",
            "nameGap": 50
        },
        "grid": {
            "left": "10%",
            "right": "10%",
            "bottom": "15%",
            "containLabel": True
        },
        "dataZoom": [
            {"type": "inside"},
            {"type": "slider"}
        ],
        "theme": "dark" if theme == "dark" else "light"
    }

# Import dashboard modules
from host_analysis import host_analysis_dashboard
#from detection_analysis import detection_analysis_dashboard
#from severity_analysis import severity_analysis_dashboard
from time_based_analysis import time_based_analysis_dashboard
from vulnerability_dashboard import vulnerability_dashboard
from three_month_trend_analysis import three_month_trend_analysis_dashboard
from detection_summary import detection_summary_dashboard
from falcon_generator import falcon_generator_dashboard
from drag_drop_dashboard_builder import drag_drop_dashboard_function
from pivot_table_builder import pivot_table_builder_dashboard
from main_dashboard_report import main_dashboard_report
from dashboard_pdf_export import falcon_dashboard_pdf_layout
# Detection Status Dashboard removed - functionality merged into Ticket Lifecycle
# from detection_status_dashboard import detection_status_dashboard

# Configure sidebar
st.sidebar.title("Security Dashboard")

# Dashboard selection
dashboard = st.sidebar.selectbox(
    "Select Dashboard",
    [
        "🛡️ Main Dashboard Report",
        "📄 PDF Export Dashboard (Single-Page)",
        "Falcon Data Generator",
        "Pivot Table Builder (Excel-Style)",
        # "📊 Detection Status Analysis",  # Merged into Ticket Lifecycle
        # Hidden for now - not in use at this moment
        # "Host Analysis",
        # "Detection and Severity Analysis Analysis",
        # "Time-based Analysis",
        # "Vulnerability Analysis",
        # "Three-Month Trend Analysis",
        # "Custom Drag & Drop Dashboard Builder"
     ],
    key="dashboard_selector"
)

# Call the selected dashboard function
if dashboard == "🛡️ Main Dashboard Report":
    main_dashboard_report()
elif dashboard == "📄 PDF Export Dashboard (Single-Page)":
    falcon_dashboard_pdf_layout()
elif dashboard == "Host Analysis":
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
elif dashboard == "Three-Month Trend Analysis":
    three_month_trend_analysis_dashboard()
elif dashboard == "Falcon Data Generator":
    falcon_generator_dashboard()
elif dashboard == "Pivot Table Builder (Excel-Style)":
    pivot_table_builder_dashboard()
# elif dashboard == "📊 Detection Status Analysis":
#     detection_status_dashboard()  # Merged into Ticket Lifecycle
elif dashboard == "Custom Drag & Drop Dashboard Builder":
    drag_drop_dashboard_function()
