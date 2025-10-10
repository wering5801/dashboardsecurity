import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from theme_utils import setup_theme
import base64
import io
from datetime import datetime, timedelta
import re

# Global color configuration
CHART_COLORS = {
    'blue': '#3498db',
    'green': '#2ecc71',
    'orange': '#f39c12',
    'purple': '#9b59b6',
    'teal': '#1abc9c',
    'yellow': '#f1c40f',
    'gray': '#95a5a6',
    'red': '#e74c3c'  # Only used for critical elements
}

def centered_table_css():
    """Return CSS for centering values in Streamlit tables"""
    return """
    <style>
    table {
        width: 100%;
    }
    th, td {
        text-align: center !important;
    }
    .stDataFrame {
        width: 100%;
    }
    .stDataFrame table {
        width: 100%;
    }
    .stDataFrame th, .stDataFrame td {
        text-align: center !important;
    }
    .summary-bullet li {
        margin-bottom: 8px;
    }
    .insight-card {
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    .insight-card h3 {
        color: #333;
        margin-top: 0;
        margin-bottom: 15px;
        font-family: sans-serif;
    }
    .insight-card p {
        color: #333;
        margin-bottom: 10px;
        font-family: sans-serif;
        background: none;
        padding: 0;
        border: none;
        font-size: 16px;
        line-height: 1.5;
    }
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
    /* Make sure the exec summary bullets look good */
    .summary-bullet {
        margin-left: 20px;
        padding-left: 0;
    }
    /* Dashboard title with report period */
    .dashboard-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
    """

def detection_summary_dashboard():
    # Initialize session state variables if they don't exist
    if "executive_summary" not in st.session_state:
        st.session_state.executive_summary = ""
    if "data_processed" not in st.session_state:
        st.session_state.data_processed = False
    
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    
    # Apply centered table CSS
    st.markdown(centered_table_css(), unsafe_allow_html=True)
    
    # ========== SIDEBAR CONFIGURATION ==========
    with st.sidebar:
        st.title("🔧 Dashboard Settings")
        
        # Report Period
        st.header("📅 Report Configuration")
        report_period = st.text_input("Report Period", "February 2025")
        
        # Display options for top N
        st.header("📊 Display Options")
        top_n = st.radio("Display Top:", [3, 5, 10], index=1, horizontal=False)
        
        # Show/Hide Chart Definitions
        show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
        
        # Visual settings
        st.header("🎨 Visualization Settings")
        with st.expander("Chart Colors", expanded=False):
            objective_chart_color = st.color_picker("Objective Chart", CHART_COLORS['blue'])
            severity_chart_color = st.color_picker("Severity Chart", CHART_COLORS['orange'])
            country_chart_color = st.color_picker("Country Chart", CHART_COLORS['purple'])
            files_chart_color = st.color_picker("Files Chart", CHART_COLORS['green'])
            tactic_chart_color = st.color_picker("Tactic Chart", CHART_COLORS['teal'])
            resolution_chart_color = st.color_picker("Resolution Chart", CHART_COLORS['yellow'])
            mttr_chart_color = st.color_picker("MTTR Chart", CHART_COLORS['gray'])
            trend_chart_color = st.color_picker("Trend Chart", CHART_COLORS['blue'])
        
        with st.expander("Label Options", expanded=False):
            show_percentages = st.checkbox("Show Percentages", value=True)
            show_values = st.checkbox("Show Values", value=True)
            show_labels = st.checkbox("Show Labels", value=True)
        
        # Instructions for data input
        st.header("📋 Data Input Instructions")
        with st.expander("How to Use This Dashboard", expanded=False):
            st.write("""
            ### Dashboard Overview
            
            This dashboard analyzes security detections and their severity levels.
            
            **Expected Data Format:**
            Each row should represent one detection with tab-separated columns:
            
            ```
            UniqueNo | Hostname | SeverityName | DetectToClose | Tactic | Technique | Objective | Resolution | Status | Detect MALAYSIA TIME | FileName | LocalIP | Country
            ```
            
            **Date Format:** dd/mm/yyyy hh:mm
            Example: 28/2/2025 15:03
            
            **Dashboard Features:**
            1. Detection count by objective
            2. Device count by objective  
            3. Detection count by Severity
            4. Device count by severity
            5. Detections by country
            6. Files with most detections
            7. Detections by objective, tactic, and technique
            8. Resolution count
            9. Severity by tactic and technique
            10. Mean Time to Remediate by Severity
            11. Weekly detection trend
            
            Sample data is pre-loaded for demonstration.
            """)
        
        # Data Input Section
        st.header("📝 Data Input")
        
        sample_data = """UniqueNo\tHostname\tSeverityName\tDetectToClose\tTactic\tTechnique\tObjective\tResolution\tStatus\tDetect MALAYSIA TIME\tFileName\tLocalIP\tCountry
3\taacv\tHigh\t1h47m53s\tMachine Learning\tSensor-based ML\tFalcon Detection Method\t--\tclosed\t28/2/2025 15:03\tPlayit.exe\t192.168.10.47\tMY
10\taaad\tHigh\t20h30m30s\tMachine Learning\tCloud-based ML\tFalcon Detection Method\ttrue_positive\tclosed\t25/2/2025 14:57\twinwords.exe\t192.168.7.150\tSG
15\tsget\tHigh\t2h42s\tMachine Learning\tSensor-based ML\tFalcon Detection Method\ttrue_positive\tclosed\t25/2/2025 10:19\tRecycled.exe\t10.28.64\tSG
23\tfget\tMedium\t1h53m20s\tMachine Learning\tSensor-based ML\tFalcon Detection Method\tfalse_positive\tclosed\t13/2/2025 12:00\tmsedgewebview2.exe\t10.2.6.208\tSG
28\tddft\tCritical\t0h50m15s\tExecution\tPowerShell\tContact Controlled Systems\ttrue_positive\tclosed\t1/2/2025 08:15\tpowershell.exe\t192.168.1.45\tMY
35\thgts\tHigh\t3h25m10s\tDefense Evasion\tProcess Hollowing\tKeep Access\ttrue_positive\tclosed\t3/2/2025 09:30\texplorer.exe\t10.5.12.76\tSG
42\tklmn\tMedium\t5h12m30s\tLateral Movement\tRemote Services\tFollow Through\tfalse_positive\tclosed\t5/2/2025 14:20\trdp.exe\t192.168.5.90\tID
50\tmnop\tLow\t1h30m45s\tDiscovery\tNetwork Service Scanning\tFollow Through\t--\tclosed\t8/2/2025 11:45\tnmap.exe\t10.3.8.112\tSG
55\tqrst\tCritical\t1h05m20s\tExfiltration\tData Compressed\tContact Controlled Systems\ttrue_positive\tclosed\t10/2/2025 16:30\t7z.exe\t192.168.2.33\tMY
60\tuvwx\tMedium\t8h15m40s\tCommand and Control\tWeb Service\tContact Controlled Systems\ttrue_positive\tclosed\t12/2/2025 10:15\tcurl.exe\t10.7.14.29\tID
65\tyznw\tLow\t2h45m10s\tCredential Access\tCredentials from Web Browsers\tKeep Access\ttrue_positive\tclosed\t15/2/2025 13:40\tchrome.exe\t192.168.9.51\tSG
70\tabcd\tHigh\t4h20m35s\tPrivilege Escalation\tAccess Token Manipulation\tKeep Access\ttrue_positive\tclosed\t18/2/2025 09:05\tcmd.exe\t10.4.7.128\tMY
75\tefgh\tMedium\t3h10m50s\tCollection\tScreen Capture\tFollow Through\tfalse_positive\tclosed\t20/2/2025 15:25\tsnip.exe\t192.168.6.17\tSG
80\tijkl\tHigh\t2h35m15s\tImpact\tData Destruction\tFalcon Detection Method\ttrue_positive\tclosed\t22/2/2025 08:50\tsecureerase.exe\t10.9.3.64\tID
85\tmnop\tMedium\t5h45m25s\tPersistence\tRegistry Run Keys\tKeep Access\ttrue_positive\tclosed\t24/2/2025 11:10\tregedit.exe\t192.168.8.39\tMY"""
        
        detection_data_input = st.text_area(
            "Detection Data",
            value=sample_data,
            height=300,
            help="Enter detection data in the format shown"
        )
        
        # Generate button
        generate_dashboard = st.button("🚀 Generate Dashboard", type="primary")
        # Show success message in sidebar after button
        if 'data_processed' in st.session_state and st.session_state.data_processed:
            st.success("✅ Data processed successfully!")
        
        # Executive Summary section in sidebar
        st.header("📋 Executive Summary")
        st.write("The executive summary will be generated automatically based on the analysis.")
    
    # ========== MAIN DASHBOARD AREA ==========
    
    # Title with report period
    st.markdown(f"<h1 class='dashboard-title'>Detection and Severity Analysis Dashboard - {report_period}</h1>", unsafe_allow_html=True)
    
    # Process data and generate dashboard
    if generate_dashboard:
        try:
            # Convert text input to DataFrame
            lines = detection_data_input.strip().split('\n')
            headers = lines[0].split('\t')
            
            rows = []
            for line in lines[1:]:
                values = line.split('\t')
                if len(values) == len(headers):
                    rows.append(values)
            
            detection_data = pd.DataFrame(rows, columns=headers)
            
            # --- COLUMN NAME FLEXIBILITY FOR DETECT TIME ---
            # Accept both 'Detect MALAYSIA TIME' and 'Detect MALAYSIA TIME FORMULA'
            detect_time_col = None
            for col in ['Detect MALAYSIA TIME', 'Detect MALAYSIA TIME FORMULA']:
                if col in detection_data.columns:
                    detect_time_col = col
                    break
            if detect_time_col is None:
                st.warning("Warning: No valid detection time column found. Please ensure your data includes a 'Detect MALAYSIA TIME' or 'Detect MALAYSIA TIME FORMULA' column.")
                return
            
            # Parse detection time
            try:
                detection_data[detect_time_col] = pd.to_datetime(
                    detection_data[detect_time_col], 
                    format='%d/%m/%Y %H:%M',
                    errors='coerce'
                )
            except Exception as e:
                st.warning(f"Warning: Some date values could not be parsed correctly. Using a more flexible parser.")
                detection_data[detect_time_col] = pd.to_datetime(
                    detection_data[detect_time_col], 
                    errors='coerce'
                )
            
            # Parse DetectToClose to get time in hours
            def parse_time_to_hours(time_str):
                # Initialize hours, minutes, seconds
                total_hours = 0
                
                # Check for days (e.g., "1d2h38m")
                day_match = re.search(r'(\d+)d', time_str)
                if day_match:
                    total_hours += int(day_match.group(1)) * 24
                
                # Check for hours (e.g., "2h54m27s")
                hour_match = re.search(r'(\d+)h', time_str)
                if hour_match:
                    total_hours += int(hour_match.group(1))
                
                # Check for minutes (e.g., "54m27s")
                minute_match = re.search(r'(\d+)m', time_str)
                if minute_match:
                    total_hours += int(minute_match.group(1)) / 60
                
                # Check for seconds (e.g., "27s")
                second_match = re.search(r'(\d+)s', time_str)
                if second_match:
                    total_hours += int(second_match.group(1)) / 3600
                
                return total_hours
            
            # Apply the time parser to get hours
            detection_data['MTTR_Hours'] = detection_data['DetectToClose'].apply(parse_time_to_hours)
            
            # Convert to proper data types
            detection_data['UniqueNo'] = detection_data['UniqueNo'].astype(int)
            
            # Add week for trend analysis
            if pd.api.types.is_datetime64_dtype(detection_data[detect_time_col]):
                # Extract week number and week start date
                detection_data['Week'] = detection_data[detect_time_col].dt.isocalendar().week
                
                # Get the week starting date
                detection_data['Week_Start'] = detection_data[detect_time_col].dt.to_period('W').dt.start_time
                
                # Add a more user-friendly week label (Week 1, Week 2, etc.)
                min_week = detection_data['Week'].min()
                detection_data['Week_Label'] = detection_data['Week'].apply(lambda x: f"Week {x - min_week + 1}")
            
            # After successful data processing, set flag
            st.session_state.data_processed = True
            
            # Calculate basic metrics
            total_detections = len(detection_data)
            unique_devices = detection_data['Hostname'].nunique()
            critical_detections = len(detection_data[detection_data['SeverityName'] == 'Critical'])
            high_detections = len(detection_data[detection_data['SeverityName'] == 'High'])
            avg_mttr = detection_data['MTTR_Hours'].mean()
            
            # Display dashboard
            st.markdown(f"<h2 class='sub-header'>📊 Detection Overview</h2>", unsafe_allow_html=True)
            
            # Overview metrics - full width
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Detections", f"{total_detections:,}")
            
            with col2:
                st.metric("Unique Devices", f"{unique_devices:,}")
            
            with col3:
                st.metric("Critical Detections", f"{critical_detections:,}")
                
            with col4:
                st.metric("High Detections", f"{high_detections:,}")
            
            with col5:
                st.metric("Avg. MTTR", f"{avg_mttr:.1f} hrs")
            
            # 1. Detection count by objective - Apply top_n
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Count by Objective</h4>
                    <p><strong>Definition:</strong> Shows the number of detections grouped by their security objective.</p>
                    <p><strong>Use Case:</strong> Identify which threat objectives are most prevalent in your environment to prioritize your security focus areas.</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"<h3>🎯 Top {top_n} Detection Count by Objective</h3>", unsafe_allow_html=True)
            objective_counts = detection_data.groupby('Objective').size().reset_index(name='Count')
            objective_counts = objective_counts.sort_values('Count', ascending=False).copy()
            if not objective_counts.empty:
                display_objectives = objective_counts.head(top_n).copy()
                if show_percentages:
                    display_objectives['Percentage'] = (display_objectives['Count'] / total_detections * 100).round(2)
                # Pie/Donut chart
                pie_labels = display_objectives['Objective']
                pie_values = display_objectives['Count']
                pie_textinfo = 'percent+value+label' if show_percentages else 'value+label'
                fig_objective = go.Figure(go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    hole=0.4,  # donut
                    textinfo=pie_textinfo,
                    marker_colors=px.colors.qualitative.Plotly
                ))
                fig_objective.update_layout(
                    title=f'Top {top_n} Detection Count by Objective',
                    height=400
                )
                st.plotly_chart(fig_objective, use_container_width=True)
                # --- KEY INSIGHT ---
                top_obj = display_objectives.iloc[0]
                percentage_val = top_obj.get('Percentage', round(top_obj['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** The most prevalent objective is '{top_obj['Objective']}' with {top_obj['Count']} detections, representing {percentage_val}% of the top {top_n} objectives. Focus security efforts on this objective.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Detection Count by Objective - Data Table</h4>", unsafe_allow_html=True)
                display_df = display_objectives[['Objective', 'Count']].copy()
                if 'Percentage' in display_objectives.columns:
                    display_df['Percentage'] = display_objectives['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No objective data available to display.")
            
            # 2. Device count by objective - Apply top_n
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Device Count by Objective</h4>
                    <p><strong>Definition:</strong> Shows the number of unique devices affected by each security objective.</p>
                    <p><strong>Use Case:</strong> Understand the spread of threat objectives across your device fleet and identify if specific objectives are targeting many devices.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>💻 Top {top_n} Device Count by Objective</h3>", unsafe_allow_html=True)
            device_objective = detection_data.groupby('Objective')['Hostname'].nunique().reset_index(name='Count')
            device_objective = device_objective.sort_values('Count', ascending=False).copy()
            if not device_objective.empty:
                display_device_obj = device_objective.head(top_n).copy()
                if show_percentages:
                    display_device_obj['Percentage'] = (display_device_obj['Count'] / unique_devices * 100).round(2)
                # Pie/Donut chart
                pie_labels = display_device_obj['Objective']
                pie_values = display_device_obj['Count']
                pie_textinfo = 'percent+value+label' if show_percentages else 'value+label'
                fig_device_obj = go.Figure(go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    hole=0.4,  # donut
                    textinfo=pie_textinfo,
                    marker_colors=px.colors.qualitative.Plotly
                ))
                fig_device_obj.update_layout(
                    title=f'Top {top_n} Device Count by Objective',
                    height=400
                )
                st.plotly_chart(fig_device_obj, use_container_width=True)
                # --- KEY INSIGHT ---
                top_dev_obj = display_device_obj.iloc[0]
                percentage_val = top_dev_obj.get('Percentage', round(top_dev_obj['Count']/unique_devices*100,1))
                st.info(f"💡 **Key Insight:** The objective '{top_dev_obj['Objective']}' affected the most devices ({top_dev_obj['Count']}), accounting for {percentage_val}% of the top {top_n} objectives. Indicates widespread impact.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Device Count by Objective - Data Table</h4>", unsafe_allow_html=True)
                display_df = display_device_obj[['Objective', 'Count']].copy()
                if 'Percentage' in display_device_obj.columns:
                    display_df['Percentage'] = display_device_obj['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No device objective data available to display.")
            
            # 3. Detection count by Severity (not using top_n since there are only 4 severity levels)
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Count by Severity</h4>
                    <p><strong>Definition:</strong> Shows the number of detections for each severity level (Critical, High, Medium, Low).</p>
                    <p><strong>Use Case:</strong> Assess the overall risk profile of your environment and prioritize remediation efforts based on severity.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🚨 Detection Count by Severity</h3>", unsafe_allow_html=True)
            
            severity_counts = detection_data.groupby('SeverityName').size().reset_index(name='Count')
            
            # Ensure severity order is correct
            severity_order = ['Critical', 'High', 'Medium', 'Low']
            severity_counts['SeverityOrder'] = severity_counts['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            severity_counts = severity_counts.sort_values('SeverityOrder').copy()
            severity_counts = severity_counts.drop('SeverityOrder', axis=1)
            
            if not severity_counts.empty:
                # Calculate percentages
                if show_percentages:
                    severity_counts['Percentage'] = (severity_counts['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    severity_counts['Label'] = severity_counts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    severity_counts['Label'] = severity_counts.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    severity_counts['Label'] = severity_counts.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    severity_counts['Label'] = ""
                
                # Custom colors for severity - adjusted for better visibility
                severity_colors = {
                    'Critical': '#e74c3c',  # Red for Critical
                    'High': '#e67e22',      # Dark Orange for High
                    'Medium': '#2980b9',    # Blue for Medium
                    'Low': '#27ae60'        # Green for Low
                }
                
                # Map colors to the severity levels
                colors = severity_counts['SeverityName'].map(severity_colors)
                
                fig_severity = go.Figure(go.Bar(
                    x=severity_counts['SeverityName'],
                    y=severity_counts['Count'],
                    marker_color=colors,
                    text=severity_counts['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_severity.update_layout(
                    title='Detection Count by Severity',
                    xaxis_title='Severity',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_severity, use_container_width=True)
                # --- KEY INSIGHT ---
                top_sev = severity_counts.iloc[0]
                percentage_val = top_sev.get('Percentage', round(top_sev['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** '{top_sev['SeverityName']}' severity detections are most common ({top_sev['Count']}), making up {percentage_val}% of all detections. Prioritize response to this severity.")
                
                # Display data table
                st.markdown("<h4>📋 Detection Count by Severity - Data Table</h4>", unsafe_allow_html=True)
                display_df = severity_counts[['SeverityName', 'Count']].copy()
                if 'Percentage' in severity_counts.columns:
                    display_df['Percentage'] = severity_counts['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No severity data available to display.")
            
            # 4. Device count by severity (not using top_n since there are only 4 severity levels)
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Device Count by Severity</h4>
                    <p><strong>Definition:</strong> Shows the number of unique devices affected by each severity level.</p>
                    <p><strong>Use Case:</strong> Identify how many devices are impacted by high-severity threats, helping prioritize device remediation.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>💻 Device Count by Severity</h3>", unsafe_allow_html=True)
            
            device_severity = detection_data.groupby('SeverityName')['Hostname'].nunique().reset_index(name='Count')
            
            # Ensure severity order is correct
            device_severity['SeverityOrder'] = device_severity['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            device_severity = device_severity.sort_values('SeverityOrder').copy()
            device_severity = device_severity.drop('SeverityOrder', axis=1)
            
            if not device_severity.empty:
                # Calculate percentages
                if show_percentages:
                    device_severity['Percentage'] = (device_severity['Count'] / unique_devices * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    device_severity['Label'] = device_severity.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    device_severity['Label'] = device_severity.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    device_severity['Label'] = device_severity.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    device_severity['Label'] = ""
                
                # Map colors to the severity levels
                colors = device_severity['SeverityName'].map(severity_colors)
                
                fig_device_sev = go.Figure(go.Bar(
                    x=device_severity['SeverityName'],
                    y=device_severity['Count'],
                    marker_color=colors,
                    text=device_severity['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_device_sev.update_layout(
                    title='Device Count by Severity',
                    xaxis_title='Severity',
                    yaxis_title='Number of Devices',
                    height=400
                )
                
                st.plotly_chart(fig_device_sev, use_container_width=True)
                # --- KEY INSIGHT ---
                top_dev_sev = device_severity.iloc[0]
                percentage_val = top_dev_sev.get('Percentage', round(top_dev_sev['Count']/unique_devices*100,1))
                st.info(f"💡 **Key Insight:** '{top_dev_sev['SeverityName']}' severity affected the most devices ({top_dev_sev['Count']}), {percentage_val}% of all devices with detections.")
                
                # Display data table
                st.markdown("<h4>📋 Device Count by Severity - Data Table</h4>", unsafe_allow_html=True)
                display_df = device_severity[['SeverityName', 'Count']].copy()
                if 'Percentage' in device_severity.columns:
                    display_df['Percentage'] = device_severity['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No device severity data available to display.")
            
            # 5. Detections by country - Apply top_n
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detections by Country</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detections across different countries.</p>
                    <p><strong>Use Case:</strong> Identify geographic hotspots for security incidents, which may indicate targeted campaigns or region-specific vulnerabilities.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>🌍 Top {top_n} Detections by Country</h3>", unsafe_allow_html=True)
            
            # Use the Country column if available, otherwise use hostname first characters
            if 'Country' in detection_data.columns:
                country_counts = detection_data.groupby('Country').size().reset_index(name='Count')
            else:
                detection_data['Country'] = detection_data['Hostname'].str.slice(0, 2)
                country_counts = detection_data.groupby('Country').size().reset_index(name='Count')
            
            country_counts = country_counts.sort_values('Count', ascending=False).copy()
            
            if not country_counts.empty:
                # Apply top_n filter
                display_countries = country_counts.head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    display_countries['Percentage'] = (display_countries['Count'] / total_detections * 100).round(2)
                
                text_info = []
                if show_labels:
                    if show_values and show_percentages:
                        text_info = ['label+value+percent']
                    elif show_values:
                        text_info = ['label+value']
                    elif show_percentages:
                        text_info = ['label+percent']
                    else:
                        text_info = ['label']
                else:
                    text_info = ['none']
                
                # Create a discrete color scale for better visibility
                country_colors = px.colors.qualitative.Plotly
                
                fig_country = go.Figure(data=[go.Pie(
                    labels=display_countries['Country'],
                    values=display_countries['Count'],
                    textinfo=text_info[0],
                    hovertemplate='%{label}: %{value} detections (%{percent})<extra></extra>',
                    textfont_size=14,
                    marker_colors=country_colors
                )])
                
                fig_country.update_layout(
                    title=f'Top {top_n} Detections by Country',
                    height=500
                )
                
                st.plotly_chart(fig_country, use_container_width=True)
                # --- KEY INSIGHT ---
                top_country = display_countries.iloc[0]
                percentage_val = top_country.get('Percentage', round(top_country['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** The country '{top_country['Country']}' had the highest detection count ({top_country['Count']}), representing {percentage_val}% of the top {top_n} countries. Indicates a geographic hotspot.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Detections by Country - Data Table</h4>", unsafe_allow_html=True)
                display_df = display_countries[['Country', 'Count']].copy()
                if 'Percentage' in display_countries.columns:
                    display_df['Percentage'] = display_countries['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No country data available to display.")
            
            # 6. Files with most detections - Apply top_n
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Files with Most Detections</h4>
                    <p><strong>Definition:</strong> Shows the files that triggered the most security detections.</p>
                    <p><strong>Use Case:</strong> Identify potentially malicious files that are prevalent in your environment and require immediate attention.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>📁 Top {top_n} Files with Most Detections</h3>", unsafe_allow_html=True)
            
            file_counts = detection_data.groupby('FileName').size().reset_index(name='Count')
            file_counts = file_counts.sort_values('Count', ascending=False).copy()
            
            if not file_counts.empty:
                # Limit to top N based on user selection
                top_file_df = file_counts.head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    top_file_df['Percentage'] = (top_file_df['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    top_file_df['Label'] = top_file_df.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    top_file_df['Label'] = top_file_df.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    top_file_df['Label'] = top_file_df.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    top_file_df['Label'] = ""
                
                fig_files = go.Figure(go.Bar(
                    x=top_file_df['Count'],
                    y=top_file_df['FileName'],
                    orientation='h',
                    marker_color=files_chart_color,
                    text=top_file_df['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_files.update_layout(
                    title=f'Top {top_n} Files with Most Detections',
                    xaxis_title='Number of Detections',
                    yaxis_title='File Name',
                    height=400
                )
                
                st.plotly_chart(fig_files, use_container_width=True)
                # --- KEY INSIGHT ---
                top_file_row = top_file_df.iloc[0]
                percentage_val = top_file_row.get('Percentage', round(top_file_row['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** The file '{top_file_row['FileName']}' triggered the most detections ({top_file_row['Count']}), {percentage_val}% of the top {top_n} files. Investigate this file for potential threats.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Files with Most Detections - Data Table</h4>", unsafe_allow_html=True)
                display_df = top_file_df[['FileName', 'Count']].copy()
                if 'Percentage' in top_file_df.columns:
                    display_df['Percentage'] = top_file_df['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No file data available to display.")
            
            # 7. Detections by objective, tactic, and technique - Apply top_n to tactic chart
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detections by Objective, Tactic, and Technique</h4>
                    <p><strong>Definition:</strong> Shows a breakdown of detections based on their security objective, tactic, and specific technique.</p>
                    <p><strong>Use Case:</strong> Understand the attack patterns in your environment and how techniques relate to broader tactics and objectives.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🎯 Detections by Objective, Tactic, and Technique</h3>", unsafe_allow_html=True)
            
            # Create a table view instead of sunburst
            if not detection_data.empty:
                # Create a hierarchical groupby
                ott_counts = detection_data.groupby(['Objective', 'Tactic', 'Technique']).size().reset_index(name='Count')
                ott_counts = ott_counts.sort_values(['Objective', 'Count'], ascending=[True, False]).copy()
                
                # Calculate percentages
                if show_percentages:
                    ott_counts['Percentage'] = (ott_counts['Count'] / total_detections * 100).round(2)
                
                # Show the data as a table - limit based on top_n
                st.markdown(f"<h4>📋 Top {top_n} Detections by Objective, Tactic, and Technique - Data Table</h4>", unsafe_allow_html=True)
                # Sort by count and get top entries
                display_ott = ott_counts.sort_values('Count', ascending=False).head(top_n).copy()
                if 'Percentage' in display_ott.columns:
                    # Safely convert to numeric, then format
                    display_ott['Percentage'] = pd.to_numeric(display_ott['Percentage'], errors='coerce')
                    display_ott['Percentage'] = display_ott['Percentage'].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else '')
                st.dataframe(display_ott, use_container_width=True)
                
                # Create a bar chart grouped by objective and tactic - Apply top_n
                tactic_counts = detection_data.groupby(['Tactic']).size().reset_index(name='Count')
                tactic_counts = tactic_counts.sort_values('Count', ascending=False).copy()
                
                # Apply top_n filter
                display_tactics = tactic_counts.head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    display_tactics['Percentage'] = (display_tactics['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    display_tactics['Label'] = display_tactics.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    display_tactics['Label'] = display_tactics.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    display_tactics['Label'] = display_tactics.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    display_tactics['Label'] = ""
                
                fig_tactic = go.Figure(go.Bar(
                    x=display_tactics['Tactic'],
                    y=display_tactics['Count'],
                    marker_color=tactic_chart_color,
                    text=display_tactics['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_tactic.update_layout(
                    title=f'Top {top_n} Detections by Tactic',
                    xaxis_title='Tactic',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_tactic, use_container_width=True)
                # --- KEY INSIGHT ---
                top_tac = display_tactics.iloc[0]
                percentage_val = top_tac.get('Percentage', round(top_tac['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** The tactic '{top_tac['Tactic']}' is most frequently observed ({top_tac['Count']} detections), {percentage_val}% of the top {top_n} tactics. Indicates a favored attack approach.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Detections by Objective, Tactic, and Technique - Data Table</h4>", unsafe_allow_html=True)
                display_df = display_ott[['Objective', 'Tactic', 'Technique', 'Count']].copy()
                if 'Percentage' in display_ott.columns:
                    display_df['Percentage'] = display_ott['Percentage']
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No data available for objective, tactic, technique breakdown.")
            
            # 8. Resolution count - Apply top_n if more than 4 resolutions
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Resolution Count</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detection resolutions (e.g., true positive, false positive).</p>
                    <p><strong>Use Case:</strong> Evaluate detection accuracy and understand how many alerts require actual remediation versus those that are false alarms.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>✅ Top {top_n} Resolution Count</h3>", unsafe_allow_html=True)
            
            resolution_counts = detection_data.groupby('Resolution').size().reset_index(name='Count')
            resolution_counts = resolution_counts.sort_values('Count', ascending=False).copy()
            
            if not resolution_counts.empty:
                # Apply top_n filter if there are many resolutions
                display_resolutions = resolution_counts
                if len(resolution_counts) > top_n:
                    display_resolutions = resolution_counts.head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    display_resolutions['Percentage'] = (display_resolutions['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    display_resolutions['Label'] = display_resolutions.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    display_resolutions['Label'] = display_resolutions.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    display_resolutions['Label'] = display_resolutions.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    display_resolutions['Label'] = ""
                
                fig_resolution = go.Figure(go.Bar(
                    x=display_resolutions['Resolution'],
                    y=display_resolutions['Count'],
                    marker_color=resolution_chart_color,
                    text=display_resolutions['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                if len(resolution_counts) > top_n:
                    title = f'Top {top_n} Resolution Count'
                else:
                    title = 'Resolution Count'
                    
                fig_resolution.update_layout(
                    title=title,
                    xaxis_title='Resolution',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_resolution, use_container_width=True)
                # --- KEY INSIGHT ---
                top_res = display_resolutions.iloc[0]
                percentage_val = top_res.get('Percentage', round(top_res['Count']/total_detections*100,1))
                st.info(f"💡 **Key Insight:** The most common resolution is '{top_res['Resolution']}' ({top_res['Count']}), {percentage_val}% of the top {top_n} resolutions. Review this resolution process for accuracy.")
                
                # Display data table
                if len(resolution_counts) > top_n:
                    table_title = f"<h4>📋 Top {top_n} Resolution Count - Data Table</h4>"
                else:
                    table_title = "<h4>📋 Resolution Count - Data Table</h4>"
                st.markdown(table_title, unsafe_allow_html=True)
                
                display_df = display_resolutions[['Resolution', 'Count']].copy()
                if 'Percentage' in display_resolutions.columns:
                    display_df['Percentage'] = display_resolutions['Percentage'].apply(lambda x: f'{x:.2f}%')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No resolution data available to display.")
            
            # 9. Severity by tactic and technique - Apply top_n to technique chart
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Severity by Tactic and Technique</h4>
                    <p><strong>Definition:</strong> Shows how severity levels are distributed across different tactics and techniques.</p>
                    <p><strong>Use Case:</strong> Identify which attack techniques consistently trigger high-severity alerts, helping focus on the most critical attack vectors.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🚨 Severity by Tactic and Technique</h3>", unsafe_allow_html=True)
            
            # Alternative approach: Use grouped bar charts instead of heatmap
            if not detection_data.empty:
                # Create a pivot table of counts
                severity_tactic = pd.crosstab(
                    index=detection_data['Tactic'], 
                    columns=detection_data['SeverityName'],
                    margins=False
                )
                
                # Ensure all severity levels are represented
                for severity in severity_order:
                    if severity not in severity_tactic.columns:
                        severity_tactic[severity] = 0
                
                # Reorder columns
                available_severities = [s for s in severity_order if s in severity_tactic.columns]
                severity_tactic = severity_tactic[available_severities]
                
                # Get sum of each tactic for sorting
                tactic_totals = severity_tactic.sum(axis=1).sort_values(ascending=False)
                
                # Apply top_n to tactics based on total count
                top_tactics = tactic_totals.head(top_n).index.tolist()
                filtered_severity_tactic = severity_tactic.loc[top_tactics]
                
                # Convert to a format suitable for grouped bar chart
                severity_tactic_melted = filtered_severity_tactic.reset_index().melt(
                    id_vars=['Tactic'],
                    value_vars=available_severities,
                    var_name='Severity',
                    value_name='Count'
                )
                
                # Define a severity order for categorical axis
                severity_tactic_melted['Severity_Order'] = severity_tactic_melted['Severity'].apply(
                    lambda x: severity_order.index(x) if x in severity_order else 999
                )
                severity_tactic_melted = severity_tactic_melted.sort_values('Severity_Order')
                
                # Use the custom severity colors
                severity_colors_list = [severity_colors.get(s, '#95a5a6') for s in available_severities]
                
                # Create a grouped bar chart
                fig_severity_tactic = px.bar(
                    severity_tactic_melted, 
                    x='Tactic', 
                    y='Count', 
                    color='Severity',
                    barmode='group',
                    color_discrete_map={
                        'Critical': severity_colors['Critical'],
                        'High': severity_colors['High'],
                        'Medium': severity_colors['Medium'],
                        'Low': severity_colors['Low']
                    },
                    height=600
                )
                
                fig_severity_tactic.update_layout(
                    title=f'Top {top_n} Tactics by Severity Distribution',
                    xaxis_title='Tactic',
                    yaxis_title='Number of Detections',
                    legend_title='Severity Level',
                    xaxis={'categoryorder': 'total descending'}  # Order tactics by total detections
                )
                
                st.plotly_chart(fig_severity_tactic, use_container_width=True)
                # --- KEY INSIGHT ---
                top_tactic_sev = filtered_severity_tactic.sum(axis=1).idxmax()
                st.info(f"💡 **Key Insight:** The tactic '{top_tactic_sev}' has the highest detection volume across all severities in the top {top_n} tactics. Focus on this tactic for mitigation.")
                
                # Display data table
                st.markdown(f"<h4>📋 Top {top_n} Tactics - Severity Distribution - Data Table</h4>", unsafe_allow_html=True)
                display_df = filtered_severity_tactic.reset_index()
                st.dataframe(display_df, use_container_width=True)
                
                # Add a visualization for technique severity distribution for the top techniques
                st.markdown(f"<h4>🎯 Top {top_n} Techniques by Severity</h4>", unsafe_allow_html=True)
                
                # Get the top techniques by count
                technique_counts = detection_data.groupby('Technique').size().reset_index(name='Count')
                technique_counts = technique_counts.sort_values('Count', ascending=False).head(top_n).copy()
                
                # Create a crosstab for top techniques by severity
                top_techniques = technique_counts['Technique'].tolist()
                technique_data = detection_data[detection_data['Technique'].isin(top_techniques)]
                
                technique_severity = pd.crosstab(
                    index=technique_data['Technique'],
                    columns=technique_data['SeverityName'],
                    margins=False
                )
                
                # Ensure all severity levels are represented
                for severity in severity_order:
                    if severity not in technique_severity.columns:
                        technique_severity[severity] = 0
                
                # Reorder columns
                available_severities = [s for s in severity_order if s in technique_severity.columns]
                technique_severity = technique_severity[available_severities]
                
                # Convert to a format suitable for grouped bar chart
                technique_severity_melted = technique_severity.reset_index().melt(
                    id_vars=['Technique'],
                    value_vars=available_severities,
                    var_name='Severity',
                    value_name='Count'
                )
                
                # Create a grouped bar chart for techniques
                fig_technique_severity = px.bar(
                    technique_severity_melted, 
                    x='Technique', 
                    y='Count', 
                    color='Severity',
                    barmode='stack',  # Use stack mode for better visibility
                    color_discrete_map={
                        'Critical': severity_colors['Critical'],
                        'High': severity_colors['High'],
                        'Medium': severity_colors['Medium'],
                        'Low': severity_colors['Low']
                    },
                    height=500
                )
                
                fig_technique_severity.update_layout(
                    title=f'Top {top_n} Techniques by Severity',
                    xaxis_title='Technique',
                    yaxis_title='Number of Detections',
                    legend_title='Severity Level',
                    xaxis={'categoryorder': 'total descending'}  # Order techniques by total detections
                )
                
                st.plotly_chart(fig_technique_severity, use_container_width=True)
                # --- KEY INSIGHT ---
                top_technique_sev = technique_severity.sum(axis=1).idxmax()
                st.info(f"💡 **Key Insight:** The technique '{top_technique_sev}' is most associated with high detection counts in the top {top_n} techniques. Prioritize investigation of this technique.")
                
                # Show technique severity table
                st.markdown(f"<h4>📋 Top {top_n} Techniques Severity Distribution - Data Table</h4>", unsafe_allow_html=True)
                st.dataframe(technique_severity, use_container_width=True)
            else:
                st.warning("No data available for severity by tactic analysis.")
            
            # 10. Mean Time to Remediate by Severity (not using top_n since there are only 4 severity levels)
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Mean Time to Remediate by Severity</h4>
                    <p><strong>Definition:</strong> Shows the average time taken to close detections for each severity level.</p>
                    <p><strong>Use Case:</strong> Evaluate response efficiency and identify areas where remediation time needs improvement, particularly for critical and high-severity issues.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>⏱️ Mean Time to Remediate by Severity</h3>", unsafe_allow_html=True)
            
            # Calculate MTTR by severity
            mttr_severity = detection_data.groupby('SeverityName')['MTTR_Hours'].mean().reset_index()
            
            # Ensure severity order is correct
            mttr_severity['SeverityOrder'] = mttr_severity['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            mttr_severity = mttr_severity.sort_values('SeverityOrder').copy()
            mttr_severity = mttr_severity.drop('SeverityOrder', axis=1)
            
            if not mttr_severity.empty:
                # Create labels based on settings
                mttr_severity['Label'] = mttr_severity['MTTR_Hours'].round(2).astype(str) + " hrs"
                
                # Map colors to the severity levels - using the improved colors
                colors = mttr_severity['SeverityName'].map(severity_colors)
                
                fig_mttr = go.Figure(go.Bar(
                    x=mttr_severity['SeverityName'],
                    y=mttr_severity['MTTR_Hours'],
                    marker_color=colors,
                    text=mttr_severity['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_mttr.update_layout(
                    title='Mean Time to Remediate by Severity',
                    xaxis_title='Severity',
                    yaxis_title='Hours',
                    height=400
                )
                
                st.plotly_chart(fig_mttr, use_container_width=True)
                # --- KEY INSIGHT ---
                slowest_mttr = mttr_severity.iloc[mttr_severity['MTTR_Hours'].idxmax()]
                st.info(f"💡 **Key Insight:** '{slowest_mttr['SeverityName']}' severity has the slowest mean time to remediate ({slowest_mttr['MTTR_Hours']:.2f} hours). Consider process improvements for this severity.")
                
                # Display data table
                st.markdown("<h4>📋 Mean Time to Remediate by Severity - Data Table</h4>", unsafe_allow_html=True)
                display_df = mttr_severity[['SeverityName', 'MTTR_Hours']].copy()
                display_df['MTTR_Hours'] = display_df['MTTR_Hours'].round(2).astype(str) + " hours"
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No MTTR data available to display.")
            
            # 11. Weekly detection trend - Apply top_n to daily counts
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Weekly Detection Trend</h4>
                    <p><strong>Definition:</strong> Shows the number of detections over time, broken down by week.</p>
                    <p><strong>Use Case:</strong> Identify trends and patterns in detection volumes, which may correlate with security events, patches, or organizational changes.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>📈 Weekly Detection Trend</h3>", unsafe_allow_html=True)
            
            # Check if week data is available
            if 'Week_Label' in detection_data.columns and not detection_data['Week_Label'].isna().all():
                weekly_counts = detection_data.groupby(['Week_Label', 'Week_Start']).size().reset_index(name='Count')
                weekly_counts = weekly_counts.sort_values('Week_Start').copy()
                
                # Format dates for display
                weekly_counts['Display_Week'] = weekly_counts['Week_Start'].dt.strftime('%d/%m/%Y')
                
                # Create a bar chart for weekly trends instead of line
                fig_trend = go.Figure(go.Bar(
                    x=weekly_counts['Week_Label'],
                    y=weekly_counts['Count'],
                    marker_color=trend_chart_color,
                    text=weekly_counts['Count'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_trend.update_layout(
                    title='Weekly Detection Trend',
                    xaxis_title='Week',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
                # --- KEY INSIGHT ---
                max_week = weekly_counts.iloc[weekly_counts['Count'].idxmax()]
                st.info(f"💡 **Key Insight:** The week '{max_week['Week_Label']}' (starting {max_week['Display_Week']}) had the highest detection volume ({max_week['Count']} detections). Investigate events during this period.")
                
                # Display data table with week info
                st.markdown("<h4>📋 Weekly Detection Trend - Data Table</h4>", unsafe_allow_html=True)
                display_df = weekly_counts[['Week_Label', 'Display_Week', 'Count']].copy()
                display_df.columns = ['Week', 'Start Date', 'Detection Count']
                st.dataframe(display_df, use_container_width=True)
                
                # Display a table showing daily detection counts - Apply top_n
                st.markdown(f"<h4>📅 Top {top_n} Daily Detection Counts</h4>", unsafe_allow_html=True)
                daily_counts = detection_data.groupby(detection_data[detect_time_col].dt.date).size().reset_index(name='Count')
                daily_counts.columns = ['Date', 'Detection Count']
                daily_counts['Date'] = daily_counts['Date'].apply(lambda x: x.strftime('%d/%m/%Y'))
                
                # Sort by count descending and get top N
                top_daily_counts = daily_counts.sort_values('Detection Count', ascending=False).head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    top_daily_counts['Percentage'] = (top_daily_counts['Detection Count'] / total_detections * 100).round(2)
                    top_daily_counts['Percentage'] = top_daily_counts['Percentage'].apply(lambda x: f'{x:.2f}%')
                
                st.dataframe(top_daily_counts, use_container_width=True)
                # --- KEY INSIGHT ---
                top_day = top_daily_counts.iloc[0]
                st.info(f"💡 **Key Insight:** The day {top_day['Date']} had the highest daily detection count ({top_day['Detection Count']}). Review incidents on this date.")
            else:
                st.warning("No weekly trend data available to display. Check date formats.")
            
            # Generate and update executive summary
            if not detection_data.empty:
                # Prepare summary data
                # Use display_objectives for accurate percentage
                if 'display_objectives' in locals() and not display_objectives.empty:
                    top_objective = display_objectives.iloc[0]['Objective']
                    top_objective_count = display_objectives.iloc[0]['Count']
                    top_objective_pct = display_objectives.iloc[0]['Percentage'] if 'Percentage' in display_objectives.columns else round(top_objective_count / total_detections * 100, 2)
                else:
                    top_objective = objective_counts.iloc[0]['Objective'] if not objective_counts.empty else "N/A"
                    top_objective_count = objective_counts.iloc[0]['Count'] if not objective_counts.empty else 0
                    top_objective_pct = objective_counts.iloc[0]['Percentage'] if 'Percentage' in objective_counts.columns and not objective_counts.empty else 0
                
                critical_pct = (critical_detections / total_detections * 100) if total_detections > 0 else 0
                high_pct = (high_detections / total_detections * 100) if total_detections > 0 else 0
                
                critical_mttr = mttr_severity[mttr_severity['SeverityName'] == 'Critical']['MTTR_Hours'].values[0] if 'Critical' in mttr_severity['SeverityName'].values else 0
                
                top_file = top_file_df.iloc[0]['FileName'] if not top_file_df.empty else "N/A"
                top_file_count = top_file_df.iloc[0]['Count'] if not top_file_df.empty else 0
                
                true_positives = detection_data[detection_data['Resolution'] == 'true_positive'].shape[0]
                false_positives = detection_data[detection_data['Resolution'] == 'false_positive'].shape[0]
                
                # Create summary
                default_summary = f"""• During {report_period}, a total of {total_detections} security detections were observed across {unique_devices} unique devices.
• {critical_detections} Critical ({critical_pct:.1f}%) and {high_detections} High ({high_pct:.1f}%) severity detections were recorded, requiring immediate attention.
• The most common objective was "{top_objective}" with {top_objective_count} detections ({top_objective_pct:.1f}% of total).
• Mean Time to Remediate (MTTR) averaged {avg_mttr:.1f} hours across all severities, with Critical detections resolved in {critical_mttr:.1f} hours on average.
• The file "{top_file}" was involved in the most detections ({top_file_count}), suggesting it should be investigated further.
• Of the resolved detections, {true_positives} were confirmed as true positives and {false_positives} were identified as false positives."""

                # Add trend information if available
                if 'Week_Label' in detection_data.columns and not weekly_counts.empty:
                    highest_week = weekly_counts.loc[weekly_counts['Count'].idxmax()]
                    highest_week_label = highest_week['Week_Label']
                    highest_week_count = highest_week['Count']
                    highest_week_date = highest_week['Display_Week']
                    
                    default_summary += f"\n• The highest detection volume was observed in {highest_week_label} (starting {highest_week_date}) with {highest_week_count} detections."
                
                # Update session state if it's empty
                if not st.session_state.executive_summary.strip():
                    st.session_state.executive_summary = default_summary
            
            # Executive summary display
            st.markdown("<h2 class='sub-header'>📋 Executive Summary</h2>", unsafe_allow_html=True)
            
            # Display executive summary in blue container with correct bullet points
            summary_html = f"""
            <div class="executive-summary-blue">
                <ul class="summary-bullet">
                    <li>During {report_period}, a total of {total_detections} security detections were observed across {unique_devices} unique devices.</li>
                    <li>{critical_detections} Critical ({critical_pct:.1f}%) and {high_detections} High ({high_pct:.1f}%) severity detections were recorded.</li>
                    <li>The most common objective was "{top_objective}" with {top_objective_count} detections ({top_objective_pct:.1f}% of total).</li>
                    <li>Mean Time to Remediate averaged {avg_mttr:.1f} hours, with Critical detections resolved in {critical_mttr:.1f} hours.</li>
                    <li>The file "{top_file}" was involved in the most detections ({top_file_count}).</li>
                    <li>Of the resolved detections, {true_positives} were true positives and {false_positives} were false positives.</li>
                </ul>
            </div>
            """
            st.markdown(summary_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.data_processed = False
            st.error(f"❌ Error processing data: {e}")
            st.error("Please check your data format and try again.")
    else:
        st.session_state.data_processed = False
        # Initial state - no dashboard generated yet
        st.info("👈 Configure your settings and input data in the sidebar, then click 'Generate Dashboard' to begin.")
        st.markdown("""
        ### Welcome to the Detection and Severity Analysis Dashboard
        
        This dashboard provides comprehensive analysis of security detections including:
        
        - 📊 Detection patterns by objectives, tactics, and techniques
        - 🚨 Severity distribution analysis
        - 🌍 Geographic detection hotspots
        - 📁 File-based threat analysis
        - ⏱️ Mean Time to Remediate (MTTR) metrics
        - 📈 Trend analysis over time
        
        **Getting Started:**
        1. Use the sidebar to configure your report period and display preferences
        2. Input your detection data in the specified format
        3. Click 'Generate Dashboard' to create your analysis
        4. Customize the executive summary as needed
        
        Sample data is pre-loaded for demonstration purposes.
        """)

if __name__ == "__main__":
    detection_summary_dashboard()