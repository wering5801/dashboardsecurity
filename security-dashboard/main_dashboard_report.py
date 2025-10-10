import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as reportlab_colors
import tempfile
import os

# Import the pivot table creation functions
from pivot_table_builder import create_pivot_table, create_pivot_chart, create_detection_key_metrics_cards

# Global color schemes
SEVERITY_COLORS = {
    'Critical': '#DC143C',  # Crimson Red
    'High': '#ED7D31',      # Orange
    'Medium': '#5B9BD5',    # Blue
    'Low': '#70AD47'        # Green
}

MONTHLY_COLORS = {
    'month_1': '#70AD47',   # Green (oldest)
    'month_2': '#5B9BD5',   # Blue (middle)
    'month_3': '#FFC000'    # Gold (latest)
}


def show_welcome_screen():
    """Display simple message - header already shown from main function"""

    st.info("💡 **No data loaded yet**")
    st.markdown("### 📋 Getting Started")
    st.markdown("""
    To view your comprehensive security analysis:

    1. **Navigate to "Falcon Data Generator"** in the sidebar
    2. **Upload your CrowdStrike CSV files** (up to 3 months)
    3. **Click "Process All Months"** to analyze your data
    4. **Return here** to view the complete dashboard
    """)

    st.success("✅ System ready for data processing")


def main_dashboard_report():
    """
    Main Dashboard Falcon Report - Enhanced UI/UX
    Consolidated single-view dashboard with professional design
    """
    # Note: st.set_page_config() is called in app.py, not here
    # to avoid StreamlitSetPageConfigMustBeFirstCommandError

    # ============================
    # CUSTOM CSS FOR ENHANCED UI/UX
    # ============================
    st.markdown("""
        <style>
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 95%;
        }

        /* Header styling */
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            text-align: center;
        }
        .dashboard-header h1 {
            color: white;
            margin: 0;
            font-size: 3em;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .dashboard-header p {
            color: #f0f0f0;
            margin: 0.8rem 0 0 0;
            font-size: 1.4em;
            font-weight: 300;
        }
        .dashboard-subtitle {
            color: #cbd5e0;
            font-size: 0.95em;
            margin-top: 0.5rem;
        }

        /* Section container */
        .section-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
            border-left: 5px solid #667eea;
        }

        /* Section header */
        .section-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        .section-icon {
            font-size: 2.5em;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.1));
        }
        .section-title {
            font-size: 2em;
            font-weight: 700;
            color: #2d3748;
            margin: 0;
        }

        /* Analysis card */
        .analysis-card {
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .analysis-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        }
        .analysis-title {
            font-size: 1.4em;
            font-weight: 600;
            color: #4a5568;
            margin: 0 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #cbd5e0;
        }

        /* Info banner */
        .info-banner {
            background: linear-gradient(90deg, #ebf4ff 0%, #ffffff 100%);
            border-left: 4px solid #4299e1;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }

        /* Statistics row */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #f7fafc 0%, #ffffff 100%);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
        }
        .stat-label {
            font-size: 0.9em;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* Footer */
        .dashboard-footer {
            text-align: center;
            color: #a0aec0;
            font-size: 0.9em;
            padding: 2rem 0;
            border-top: 2px solid #e2e8f0;
            margin-top: 3rem;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f7fafc;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # DASHBOARD HEADER
    # ============================
    st.markdown("""
        <div class="dashboard-header">
            <h1>🛡️ Falcon Security Dashboard</h1>
            <p>Comprehensive Multi-Month Security Analysis Report</p>
            <div class="dashboard-subtitle">developed by Izami Ariff © 2025</div>
        </div>
    """, unsafe_allow_html=True)

    # Check if analysis results are available
    if 'host_analysis_results' not in st.session_state and \
       'detection_analysis_results' not in st.session_state and \
       'time_analysis_results' not in st.session_state:
        # Show welcome screen
        show_welcome_screen()
        return

    # ============================
    # SIDEBAR CONTROLS
    # ============================
    with st.sidebar:
        st.markdown("### 🎯 Dashboard Controls")
        st.markdown("---")

        # Display settings
        st.markdown("#### ⚙️ Display Settings")
        chart_height = st.slider("Chart Height (px)", 300, 800, 500, 50)

        layout_density = st.selectbox(
            "Layout Density",
            ["Compact", "Standard", "Spacious"],
            index=1
        )

        st.markdown("---")

        # Sections to display
        st.markdown("#### 📋 Report Sections")
        show_summary = st.checkbox("📊 Executive Summary", value=True)
        show_host_analysis = st.checkbox("🖥️ Host Analysis", value=True)
        show_detection_analysis = st.checkbox("🔍 Detection & Severity", value=True)
        show_time_analysis = st.checkbox("⏰ Time-Based Analysis", value=True)

        st.markdown("---")

        # Additional options
        st.markdown("#### 🔧 Additional Options")
        show_data_tables = st.checkbox("Show Data Tables", value=False)
        show_insights = st.checkbox("Show Key Insights", value=True)

        st.markdown("---")
        st.caption("💡 All visualizations use pre-configured settings from the Pivot Table Builder")

    # Store settings
    st.session_state.update({
        'chart_height': chart_height,
        'layout_density': layout_density,
        'show_data_tables': show_data_tables,
        'show_insights': show_insights
    })

    # ============================
    # EXECUTIVE SUMMARY
    # ============================
    if show_summary:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><div class="section-icon">📊</div><h2 class="section-title">Executive Summary</h2></div>', unsafe_allow_html=True)

        # Calculate summary statistics
        summary_stats = calculate_summary_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Total Detections</div>
                    <div class="stat-value">{summary_stats.get('total_detections', 0):,}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Unique Hosts</div>
                    <div class="stat-value">{summary_stats.get('unique_hosts', 0):,}</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Critical Alerts</div>
                    <div class="stat-value">{summary_stats.get('critical_detections', 0):,}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Months Analyzed</div>
                    <div class="stat-value">{summary_stats.get('months_analyzed', 0)}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ============================
    # HOST ANALYSIS SECTION
    # ============================
    if show_host_analysis and 'host_analysis_results' in st.session_state:
        render_host_analysis_section(chart_height, show_data_tables, show_insights)

    # ============================
    # DETECTION & SEVERITY SECTION
    # ============================
    if show_detection_analysis and 'detection_analysis_results' in st.session_state:
        render_detection_analysis_section(chart_height, show_data_tables, show_insights)

    # ============================
    # TIME-BASED ANALYSIS SECTION
    # ============================
    if show_time_analysis and 'time_analysis_results' in st.session_state:
        render_time_analysis_section(chart_height, show_data_tables, show_insights)

    # ============================
    # FOOTER
    # ============================
    st.markdown("""
        <div class="dashboard-footer">
            <p>🛡️ Falcon Security Dashboard | Multi-Month Analysis Report</p>
            <p style="font-size: 0.85em; margin-top: 0.5rem;">Generated on """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """</p>
        </div>
    """, unsafe_allow_html=True)



def calculate_summary_statistics():
    """Calculate executive summary statistics"""
    stats = {
        'total_detections': 0,
        'unique_hosts': 0,
        'critical_detections': 0,
        'months_analyzed': 0
    }

    # Get data from session state
    if 'detection_analysis_results' in st.session_state:
        detection_data = st.session_state['detection_analysis_results']

        if 'critical_high_overview' in detection_data:
            df = detection_data['critical_high_overview']
            if 'Month' in df.columns:
                stats['months_analyzed'] = len(df['Month'].unique())

            # Calculate total detections
            total_det = df[df['KEY METRICS'] == 'Total Detections']
            if not total_det.empty and 'Count' in total_det.columns:
                stats['total_detections'] = int(total_det['Count'].sum())

            # Calculate unique devices
            unique_dev = df[df['KEY METRICS'] == 'Unique Devices']
            if not unique_dev.empty and 'Count' in unique_dev.columns:
                stats['unique_hosts'] = int(unique_dev['Count'].sum())

            # Calculate critical detections
            critical_det = df[df['KEY METRICS'] == 'Critical Detections']
            if not critical_det.empty and 'Count' in critical_det.columns:
                stats['critical_detections'] = int(critical_det['Count'].sum())

    return stats


def render_host_analysis_section(chart_height, show_data_tables, show_insights):
    """Render Host Analysis section with enhanced UI"""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><div class="section-icon">🖥️</div><h2 class="section-title">Host Analysis</h2></div>', unsafe_allow_html=True)

    host_results = st.session_state['host_analysis_results']

    # A1. Overview - Key Metrics
    if 'overview_key_metrics' in host_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">A1. Overview - Key Metrics</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            host_results['overview_key_metrics'],
            analysis_key='overview_key_metrics',
            config={
                'rows': ['Month'],
                'columns': ['KEY METRICS'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Month',
                'use_monthly_colors': True,
                'chart_sort_direction': 'descending'
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # A2. Top Hosts
    if 'overview_top_hosts' in host_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">A2. Top Hosts with Most Detections</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            host_results['overview_top_hosts'],
            analysis_key='overview_top_hosts',
            config={
                'rows': ['TOP HOSTS WITH MOST DETECTIONS'],
                'columns': ['Month'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Value (Detection Count)',
                'use_monthly_colors': True,
                'chart_sort_direction': 'descending',
                'top_n': {
                    'enabled': True,
                    'field': 'TOP HOSTS WITH MOST DETECTIONS',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Count',
                    'per_month': False
                }
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # A3. User Analysis
    if 'user_analysis' in host_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">A3. User Analysis</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            host_results['user_analysis'],
            analysis_key='user_analysis',
            config={
                'rows': ['Username'],
                'columns': ['Month'],
                'values': ['Count of Detection'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Value (Detection Count)',
                'use_monthly_colors': True,
                'chart_sort_direction': 'descending',
                'top_n': {
                    'enabled': True,
                    'field': 'Username',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Count of Detection',
                    'per_month': False
                }
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # A4. Sensor Analysis
    if 'sensor_analysis' in host_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">A4. Sensor Analysis</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            host_results['sensor_analysis'],
            analysis_key='sensor_analysis',
            config={
                'rows': ['Sensor Version', 'Month', 'Status'],
                'columns': [],
                'values': ['Host Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Month',
                'chart_sort_direction': 'descending'
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_detection_analysis_section(chart_height, show_data_tables, show_insights):
    """Render Detection & Severity Analysis section"""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><div class="section-icon">🔍</div><h2 class="section-title">Detection & Severity Analysis</h2></div>', unsafe_allow_html=True)

    detection_results = st.session_state['detection_analysis_results']

    # B1. Critical and High Detection Overview
    if 'critical_high_overview' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B1. Critical and High Detection Overview</h3>', unsafe_allow_html=True)
        create_detection_key_metrics_cards(detection_results['critical_high_overview'])
        st.markdown('</div>', unsafe_allow_html=True)

    # B2. Detection Count by Severity
    if 'severity_trend' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B2. Detection Count by Severity</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            detection_results['severity_trend'],
            analysis_key='severity_trend',
            config={
                'rows': ['Month'],
                'columns': ['SeverityName'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Month',
                'use_severity_colors': True
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # B3. Geographic Analysis
    if 'country_analysis' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B3. Detection Count Across Country</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            detection_results['country_analysis'],
            analysis_key='country_analysis',
            config={
                'rows': ['Country'],
                'columns': ['Month'],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Detection Count',
                'chart_sort_direction': 'descending',
                'use_monthly_colors': True
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # B4. Files with Most Detections
    if 'file_analysis' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B4. Files with Most Detections</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            detection_results['file_analysis'],
            analysis_key='file_analysis',
            config={
                'rows': ['File Name'],
                'columns': ['Month'],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Horizontal Bar',
                'sort_by_field': 'Detection Count',
                'chart_sort_direction': 'descending',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'File Name',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Detection Count',
                    'per_month': False
                }
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # B5. Tactics by Severity
    if 'tactics_by_severity' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B5. Tactics by Severity</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            detection_results['tactics_by_severity'],
            analysis_key='tactics_by_severity',
            config={
                'rows': ['Month', 'SeverityName'],
                'columns': ['Tactic'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Tactic',
                'use_severity_colors': True,
                'use_monthly_colors': False
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # B6. Technique by Severity
    if 'technique_by_severity' in detection_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">B6. Technique by Severity</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            detection_results['technique_by_severity'],
            analysis_key='technique_by_severity',
            config={
                'rows': ['Month', 'SeverityName'],
                'columns': ['Technique'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Technique',
                'use_severity_colors': True,
                'use_monthly_colors': False,
                'top_n': {
                    'enabled': True,
                    'field': 'Technique',
                    'n': 10,
                    'type': 'top',
                    'by_field': 'Count',
                    'per_month': False
                }
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_time_analysis_section(chart_height, show_data_tables, show_insights):
    """Render Time-Based Analysis section"""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><div class="section-icon">⏰</div><h2 class="section-title">Time-Based Analysis</h2></div>', unsafe_allow_html=True)

    time_results = st.session_state['time_analysis_results']

    # C1. Daily Trends
    if 'daily_trends' in time_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">C1. Daily Trends</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            time_results['daily_trends'],
            analysis_key='daily_trends',
            config={
                'rows': ['Date', 'Month'],
                'columns': [],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Value (Detection Count)',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'Date',
                    'n': 3,
                    'type': 'top',
                    'by_field': 'Detection Count',
                    'per_month': True
                }
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # C2. Hourly Analysis
    if 'hourly_analysis' in time_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">C2. Hourly Analysis</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            time_results['hourly_analysis'],
            analysis_key='hourly_analysis',
            config={
                'rows': ['Hour'],
                'columns': [],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Line Chart',
                'sort_by_field': 'Hour',
                'chart_sort_direction': 'descending'
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # C3. Day of Week
    if 'day_of_week' in time_results:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="analysis-title">C3. Day of Week</h3>', unsafe_allow_html=True)
        display_analysis_chart(
            time_results['day_of_week'],
            analysis_key='day_of_week',
            config={
                'rows': ['Day', 'Type'],
                'columns': [],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Day',
                'use_monthly_colors': True
            },
            height=chart_height,
            show_table=show_data_tables
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_analysis_chart(df, analysis_key, config, height, show_table=False):
    """Display a single analysis chart with optional data table"""
    if df is None or df.empty:
        st.warning(f"No data available for {analysis_key}")
        return

    # Apply filters
    filtered_df = apply_filters(df.copy(), config)

    # Create pivot table
    pivot_table = create_pivot_table(filtered_df, config, analysis_key)

    if pivot_table is not None and not pivot_table.empty:
        # Create chart
        chart = create_pivot_chart(pivot_table, config['chart_type'], height, config, analysis_key)

        if chart:
            st.plotly_chart(chart, use_container_width=True)

        # Show data table if requested
        if show_table:
            with st.expander("📊 View Data Table", expanded=False):
                st.dataframe(pivot_table, use_container_width=True)


def apply_filters(df, config):
    """Apply filters like Top N to the dataframe"""
    top_n_config = config.get('top_n')
    if top_n_config and top_n_config.get('enabled'):
        try:
            filter_field = top_n_config['field']
            n_value = top_n_config['n']
            filter_type = top_n_config['type']
            by_field = top_n_config['by_field']
            per_month = top_n_config.get('per_month', False)

            if filter_field in df.columns and by_field in df.columns:
                if per_month and 'Month' in df.columns:
                    all_top_items = []
                    months = df['Month'].unique()

                    for month in months:
                        month_df = df[df['Month'] == month]
                        totals = month_df.groupby(filter_field)[by_field].sum().reset_index()
                        totals = totals.rename(columns={by_field: '_total'})

                        if filter_type == 'top':
                            top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                        else:
                            top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()

                        for item in top_items:
                            all_top_items.append((month, item))

                    df = df[df.apply(lambda row: (row['Month'], row[filter_field]) in all_top_items, axis=1)]
                else:
                    totals = df.groupby(filter_field)[by_field].sum().reset_index()
                    totals = totals.rename(columns={by_field: '_total'})

                    if filter_type == 'top':
                        top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                    else:
                        top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()

                    df = df[df[filter_field].isin(top_items)]
        except Exception as e:
            st.warning(f"Could not apply Top N filter: {str(e)}")

    return df


def generate_comprehensive_pdf_report(show_host, show_detection, show_time, chart_height):
    """Generate a comprehensive PDF report with all analyses"""
    buffer = io.BytesIO()

    try:
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        story = []
        styles = getSampleStyleSheet()

        # Title page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=reportlab_colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=1
        )

        story.append(Paragraph("🛡️ Falcon Security Dashboard", title_style))
        story.append(Paragraph("Comprehensive Multi-Month Analysis Report", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))

        metadata_text = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Type:</b> Consolidated Security Analysis<br/>
        <b>Developed by:</b> Izami Ariff © 2025
        """
        story.append(Paragraph(metadata_text, styles['Normal']))
        story.append(PageBreak())

        # Add placeholder for charts
        if show_host:
            story.append(Paragraph("HOST ANALYSIS", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Host analysis visualizations will be included here...", styles['Normal']))
            story.append(PageBreak())

        if show_detection:
            story.append(Paragraph("DETECTION & SEVERITY ANALYSIS", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Detection analysis visualizations will be included here...", styles['Normal']))
            story.append(PageBreak())

        if show_time:
            story.append(Paragraph("TIME-BASED ANALYSIS", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Time-based analysis visualizations will be included here...", styles['Normal']))

        doc.build(story)
        buffer.seek(0)

        return buffer.getvalue()

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


if __name__ == "__main__":
    main_dashboard_report()
