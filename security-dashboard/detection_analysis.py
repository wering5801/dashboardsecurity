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
    </style>
    """

def detection_analysis_dashboard():
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    
    # Apply centered table CSS
    st.markdown(centered_table_css(), unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>Detection and Severity Analysis Dashboard</h1>", unsafe_allow_html=True)
    
    # Report Period (keep as requested)
    col1, col2 = st.columns([2, 2])
    with col1:
        report_period = st.text_input("Report Period", "February-April 2025")
    
    # Display options for top N
    top_n = st.radio("Display Top:", [3, 5, 10], index=1, horizontal=True)
    
    # Show/Hide Chart Definitions
    show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
    
    # Visual settings
    with st.expander("📊 Visualization Settings"):
        st.markdown("### Customize Chart Appearance")
        
        # Color scheme
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Chart Colors")
            objective_chart_color = st.color_picker("Objective Chart", CHART_COLORS['blue'])
            severity_chart_color = st.color_picker("Severity Chart", CHART_COLORS['orange'])
            country_chart_color = st.color_picker("Country Chart", CHART_COLORS['purple'])
            files_chart_color = st.color_picker("Files Chart", CHART_COLORS['green'])
            tactic_chart_color = st.color_picker("Tactic Chart", CHART_COLORS['teal'])
            resolution_chart_color = st.color_picker("Resolution Chart", CHART_COLORS['yellow'])
            mttr_chart_color = st.color_picker("MTTR Chart", CHART_COLORS['gray'])
            trend_chart_color = st.color_picker("Trend Chart", CHART_COLORS['blue'])
        
        with col2:
            st.markdown("#### Label Options")
            show_percentages = st.checkbox("Show Percentages", value=True)
            show_values = st.checkbox("Show Values", value=True)
            show_labels = st.checkbox("Show Labels", value=True)
    
    # Instructions for data input
    with st.expander("📋 Data Input Instructions"):
        st.write("""
        ### How to Use This Dashboard
        
        This dashboard analyzes security detections and their severity levels.
        
        Enter your detection data in the text area below. Each row should represent one detection.
        The expected format is a table with the following columns (tab or multiple spaces separated):
        
        ```
        UniqueNo | Hostname | SeverityName | DetectToClose | Tactic | Technique | Objective | Resolution | Status | Detect MALAYSIA TIME FORMULA | FileName
        ```
        
        For Detect MALAYSIA TIME FORMULA, use the format: dd/mm/yyyy hh:mm:ss
        For example: 25/2/2025 13:41
        
        The dashboard will visualize:
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
        
        Sample data is shown in the text area.
        """)
    
    # Input form for manual data entry
    with st.form("detection_form"):
        st.markdown("""
        ### Enter Detection Data
        
        Enter your detection data in the text area below. Each row should represent one detection.
        """)
        
        sample_data = """UniqueNo\tHostname\tSeverityName\tDetectToClose\tTactic\tTechnique\tObjective\tResolution\tStatus\tDetect MALAYSIA TIME FORMULA\tFileName
11\tAAB\tMedium\t1d2h38m\tImpact\tInhibit System Recovery\tFollow Through\t--\tclosed\t25/2/2025 13:41\tRecoveryDrive.exe
35\tAAX\tMedium\t18h1m24s\tMachine Learning\tSensor-based ML\tFalcon Detection Method\tfalse_positive\tclosed\t12/2/2025 19:52\tdemovm.exe
46\tAAF\tLow\t1d4h7m10s\tMachine Learning\tMalware/PUP\tFalcon Detection Method\t--\tclosed\t11/2/2025 18:11\t3.6.0_4715.exe
64\tAAK\tLow\t2h54m27s\tMalware\tPUP\tFalcon Detection Method\ttrue_positive\tclosed\t5/2/2025 11:25\tipscan.exe
72\tABB\tHigh\t5h12m8s\tPersistence\tRegistry Run Keys\tKeep Access\ttrue_positive\tclosed\t28/2/2025 09:33\tsvchost.exe
83\tABC\tCritical\t1h45m32s\tExecution\tPowerShell\tContact Controlled Systems\ttrue_positive\tclosed\t1/3/2025 14:22\tpowershell.exe
90\tABC\tHigh\t8h30m15s\tDefense Evasion\tProcess Hollowing\tKeep Access\ttrue_positive\tclosed\t2/3/2025 11:10\texplorer.exe
102\tAAX\tMedium\t12h18m42s\tLateral Movement\tRemote Services\tFollow Through\tfalse_positive\tclosed\t5/3/2025 16:45\trdp.exe
115\tAAK\tLow\t4h5m18s\tDiscovery\tNetwork Service Scanning\tFollow Through\t--\tclosed\t8/3/2025 10:30\tnmap.exe
128\tABD\tCritical\t2h10m5s\tExfiltration\tData Compressed\tContact Controlled Systems\ttrue_positive\tclosed\t10/3/2025 08:15\t7z.exe
135\tABF\tMedium\t1d1h25m\tCommand and Control\tWeb Service\tContact Controlled Systems\ttrue_positive\tclosed\t12/3/2025 13:40\tcurl.exe
147\tAAF\tLow\t5h42m10s\tCredential Access\tCredentials from Web Browsers\tKeep Access\ttrue_positive\tclosed\t15/3/2025 09:20\tchrome.exe
155\tABG\tHigh\t3h8m45s\tPrivilege Escalation\tAccess Token Manipulation\tKeep Access\ttrue_positive\tclosed\t18/3/2025 14:55\tcmd.exe
162\tABH\tMedium\t9h32m17s\tCollection\tScreen Capture\tFollow Through\tfalse_positive\tclosed\t20/3/2025 11:30\tsnip.exe
173\tABB\tHigh\t4h15m22s\tImpact\tData Destruction\tFalcon Detection Method\ttrue_positive\tclosed\t22/3/2025 16:10\tsecureerase.exe"""
        
        detection_data_input = st.text_area(
            "Detection Data",
            value=sample_data,
            height=300,
            help="Enter detection data in the format shown"
        )
        
        submit_button = st.form_submit_button(label="Generate Dashboard")
    
    # Process data and generate dashboard
    if submit_button:
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
            
            # Parse detection time
            try:
                detection_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    detection_data['Detect MALAYSIA TIME FORMULA'], 
                    format='%d/%m/%Y %H:%M',
                    errors='coerce'
                )
            except Exception as e:
                st.warning(f"Warning: Some date values could not be parsed correctly. Using a more flexible parser.")
                detection_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    detection_data['Detect MALAYSIA TIME FORMULA'], 
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
            
            # Extract country from hostname (first two characters)
            # This is a simplification - in reality you might want a more robust method
            detection_data['Country'] = detection_data['Hostname'].str.slice(0, 2)
            
            # Convert to proper data types
            detection_data['UniqueNo'] = detection_data['UniqueNo'].astype(int)
            
            # Add week for trend analysis
            if pd.api.types.is_datetime64_dtype(detection_data['Detect MALAYSIA TIME FORMULA']):
                detection_data['Week'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.isocalendar().week
                detection_data['Week_Start'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.to_period('W').dt.start_time
            
            st.success("Data processed successfully!")
            
            # Calculate basic metrics
            total_detections = len(detection_data)
            unique_devices = detection_data['Hostname'].nunique()
            critical_detections = len(detection_data[detection_data['SeverityName'] == 'Critical'])
            high_detections = len(detection_data[detection_data['SeverityName'] == 'High'])
            avg_mttr = detection_data['MTTR_Hours'].mean()
            
            # Display dashboard
            st.markdown(f"<h2 class='sub-header'>Detection Overview for {report_period}</h2>", unsafe_allow_html=True)
            
            # Overview metrics - full width
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{total_detections:,}</div>
                    <div class='metric-label'>Total Detections</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{unique_devices:,}</div>
                    <div class='metric-label'>Unique Devices</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{critical_detections:,}</div>
                    <div class='metric-label'>Critical Detections</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{high_detections:,}</div>
                    <div class='metric-label'>High Detections</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{avg_mttr:.1f} hrs</div>
                    <div class='metric-label'>Avg. MTTR</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 1. Detection count by objective
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Count by Objective</h4>
                    <p><strong>Definition:</strong> Shows the number of detections grouped by their security objective.</p>
                    <p><strong>Use Case:</strong> Identify which threat objectives are most prevalent in your environment to prioritize your security focus areas.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Detection Count by Objective</h3>", unsafe_allow_html=True)
            
            objective_counts = detection_data.groupby('Objective').size().reset_index(name='Count')
            objective_counts = objective_counts.sort_values('Count', ascending=False).copy()
            
            if not objective_counts.empty:
                # Calculate percentages
                if show_percentages:
                    objective_counts.loc[:, 'Percentage'] = (objective_counts['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    objective_counts.loc[:, 'Label'] = objective_counts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    objective_counts.loc[:, 'Label'] = objective_counts.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    objective_counts.loc[:, 'Label'] = objective_counts.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    objective_counts.loc[:, 'Label'] = ""
                
                fig_objective = go.Figure(go.Bar(
                    x=objective_counts['Objective'],
                    y=objective_counts['Count'],
                    marker_color=objective_chart_color,
                    text=objective_counts['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_objective.update_layout(
                    title='Detection Count by Objective',
                    xaxis_title='Objective',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_objective, use_container_width=True)
            else:
                st.warning("No objective data available to display.")
            
            # 2. Device count by objective
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Device Count by Objective</h4>
                    <p><strong>Definition:</strong> Shows the number of unique devices affected by each security objective.</p>
                    <p><strong>Use Case:</strong> Understand the spread of threat objectives across your device fleet and identify if specific objectives are targeting many devices.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Device Count by Objective</h3>", unsafe_allow_html=True)
            
            device_objective = detection_data.groupby('Objective')['Hostname'].nunique().reset_index(name='Count')
            device_objective = device_objective.sort_values('Count', ascending=False).copy()
            
            if not device_objective.empty:
                # Calculate percentages
                if show_percentages:
                    device_objective.loc[:, 'Percentage'] = (device_objective['Count'] / unique_devices * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    device_objective.loc[:, 'Label'] = device_objective.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    device_objective.loc[:, 'Label'] = device_objective.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    device_objective.loc[:, 'Label'] = device_objective.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    device_objective.loc[:, 'Label'] = ""
                
                fig_device_obj = go.Figure(go.Bar(
                    x=device_objective['Objective'],
                    y=device_objective['Count'],
                    marker_color=objective_chart_color,
                    text=device_objective['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_device_obj.update_layout(
                    title='Device Count by Objective',
                    xaxis_title='Objective',
                    yaxis_title='Number of Devices',
                    height=400
                )
                
                st.plotly_chart(fig_device_obj, use_container_width=True)
            else:
                st.warning("No device objective data available to display.")
            
            # 3. Detection count by Severity
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Count by Severity</h4>
                    <p><strong>Definition:</strong> Shows the number of detections for each severity level (Critical, High, Medium, Low).</p>
                    <p><strong>Use Case:</strong> Assess the overall risk profile of your environment and prioritize remediation efforts based on severity.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Detection Count by Severity</h3>", unsafe_allow_html=True)
            
            severity_counts = detection_data.groupby('SeverityName').size().reset_index(name='Count')
            
            # Ensure severity order is correct
            severity_order = ['Critical', 'High', 'Medium', 'Low']
            severity_counts['SeverityOrder'] = severity_counts['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            severity_counts = severity_counts.sort_values('SeverityOrder').copy()
            severity_counts = severity_counts.drop('SeverityOrder', axis=1)
            
            if not severity_counts.empty:
                # Calculate percentages
                if show_percentages:
                    severity_counts.loc[:, 'Percentage'] = (severity_counts['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    severity_counts.loc[:, 'Label'] = severity_counts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    severity_counts.loc[:, 'Label'] = severity_counts.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    severity_counts.loc[:, 'Label'] = severity_counts.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    severity_counts.loc[:, 'Label'] = ""
                
                # Custom colors for severity
                severity_colors = {
                    'Critical': '#e74c3c',  # Red for Critical
                    'High': '#f39c12',      # Orange for High
                    'Medium': '#f1c40f',    # Yellow for Medium
                    'Low': '#3498db'        # Blue for Low
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
            else:
                st.warning("No severity data available to display.")
            
            # 4. Device count by severity
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Device Count by Severity</h4>
                    <p><strong>Definition:</strong> Shows the number of unique devices affected by each severity level.</p>
                    <p><strong>Use Case:</strong> Identify how many devices are impacted by high-severity threats, helping prioritize device remediation.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Device Count by Severity</h3>", unsafe_allow_html=True)
            
            device_severity = detection_data.groupby('SeverityName')['Hostname'].nunique().reset_index(name='Count')
            
            # Ensure severity order is correct
            device_severity['SeverityOrder'] = device_severity['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            device_severity = device_severity.sort_values('SeverityOrder').copy()
            device_severity = device_severity.drop('SeverityOrder', axis=1)
            
            if not device_severity.empty:
                # Calculate percentages
                if show_percentages:
                    device_severity.loc[:, 'Percentage'] = (device_severity['Count'] / unique_devices * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    device_severity.loc[:, 'Label'] = device_severity.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    device_severity.loc[:, 'Label'] = device_severity.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    device_severity.loc[:, 'Label'] = device_severity.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    device_severity.loc[:, 'Label'] = ""
                
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
            else:
                st.warning("No device severity data available to display.")
            
            # 5. Detections by country
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detections by Country</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detections across different countries (derived from hostname prefixes).</p>
                    <p><strong>Use Case:</strong> Identify geographic hotspots for security incidents, which may indicate targeted campaigns or region-specific vulnerabilities.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Detections by Country</h3>", unsafe_allow_html=True)
            
            country_counts = detection_data.groupby('Country').size().reset_index(name='Count')
            country_counts = country_counts.sort_values('Count', ascending=False).copy()
            
            if not country_counts.empty:
                # Calculate percentages
                if show_percentages:
                    country_counts.loc[:, 'Percentage'] = (country_counts['Count'] / total_detections * 100).round(2)
                
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
                
                fig_country = go.Figure(data=[go.Pie(
                    labels=country_counts['Country'],
                    values=country_counts['Count'],
                    textinfo=text_info[0],
                    hovertemplate='%{label}: %{value} detections (%{percent})<extra></extra>',
                    textfont_size=14,
                    marker_colors=[country_chart_color]
                )])
                
                fig_country.update_layout(
                    title='Detections by Country',
                    height=500
                )
                
                st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.warning("No country data available to display.")
            
            # 6. Files with most detections
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Files with Most Detections</h4>
                    <p><strong>Definition:</strong> Shows the files that triggered the most security detections.</p>
                    <p><strong>Use Case:</strong> Identify potentially malicious files that are prevalent in your environment and require immediate attention.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>Top {top_n} Files with Most Detections</h3>", unsafe_allow_html=True)
            
            file_counts = detection_data.groupby('FileName').size().reset_index(name='Count')
            file_counts = file_counts.sort_values('Count', ascending=False).copy()
            
            if not file_counts.empty:
                # Limit to top N based on user selection
                top_file_df = file_counts.head(top_n).copy()
                
                # Calculate percentages
                if show_percentages:
                    top_file_df.loc[:, 'Percentage'] = (top_file_df['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    top_file_df.loc[:, 'Label'] = top_file_df.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    top_file_df.loc[:, 'Label'] = top_file_df.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    top_file_df.loc[:, 'Label'] = top_file_df.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    top_file_df.loc[:, 'Label'] = ""
                
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
            else:
                st.warning("No file data available to display.")
            
            # 7. Detections by objective, tactic, and technique
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detections by Objective, Tactic, and Technique</h4>
                    <p><strong>Definition:</strong> Shows a hierarchical breakdown of detections based on their security objective, tactic, and specific technique.</p>
                    <p><strong>Use Case:</strong> Understand the attack patterns in your environment and how techniques relate to broader tactics and objectives.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Detections by Objective, Tactic, and Technique</h3>", unsafe_allow_html=True)
            
            # Create a sunburst chart
            if not detection_data.empty:
                fig_sunburst = px.sunburst(
                    detection_data,
                    path=['Objective', 'Tactic', 'Technique'],
                    color_discrete_sequence=[tactic_chart_color]
                )
                
                fig_sunburst.update_layout(
                    title='Detections by Objective, Tactic, and Technique',
                    height=600
                )
                
                st.plotly_chart(fig_sunburst, use_container_width=True)
            else:
                st.warning("No data available for hierarchical breakdown.")
            
            # 8. Resolution count
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Resolution Count</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detection resolutions (e.g., true positive, false positive).</p>
                    <p><strong>Use Case:</strong> Evaluate detection accuracy and understand how many alerts require actual remediation versus those that are false alarms.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Resolution Count</h3>", unsafe_allow_html=True)
            
            resolution_counts = detection_data.groupby('Resolution').size().reset_index(name='Count')
            resolution_counts = resolution_counts.sort_values('Count', ascending=False).copy()
            
            if not resolution_counts.empty:
                # Calculate percentages
                if show_percentages:
                    resolution_counts.loc[:, 'Percentage'] = (resolution_counts['Count'] / total_detections * 100).round(2)
                
                # Create labels based on settings
                if show_percentages and show_values:
                    resolution_counts.loc[:, 'Label'] = resolution_counts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    resolution_counts.loc[:, 'Label'] = resolution_counts.apply(lambda row: f"({row['Percentage']}%)", axis=1)
                elif show_values:
                    resolution_counts.loc[:, 'Label'] = resolution_counts.apply(lambda row: f"{row['Count']}", axis=1)
                else:
                    resolution_counts.loc[:, 'Label'] = ""
                
                fig_resolution = go.Figure(go.Bar(
                    x=resolution_counts['Resolution'],
                    y=resolution_counts['Count'],
                    marker_color=resolution_chart_color,
                    text=resolution_counts['Label'] if show_labels else None,
                    textposition='outside'
                ))
                
                fig_resolution.update_layout(
                    title='Resolution Count',
                    xaxis_title='Resolution',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_resolution, use_container_width=True)
            else:
                st.warning("No resolution data available to display.")
            
            # 9. Severity by tactic and technique
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Severity by Tactic and Technique</h4>
                    <p><strong>Definition:</strong> Shows how severity levels are distributed across different tactics and techniques.</p>
                    <p><strong>Use Case:</strong> Identify which attack techniques consistently trigger high-severity alerts, helping focus on the most critical attack vectors.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Severity by Tactic and Technique</h3>", unsafe_allow_html=True)
            
            # Create a heatmap of severity by tactic and technique
            if not detection_data.empty:
                # Create a pivot table of counts
                severity_pivot = pd.crosstab(
                    index=detection_data['Tactic'],
                    columns=detection_data['SeverityName'],
                    normalize='index'
                ) * 100  # Convert to percentage
                
                # Ensure all severity levels are represented
                for severity in severity_order:
                    if severity not in severity_pivot.columns:
                        severity_pivot[severity] = 0
                
                # Reorder columns
                severity_pivot = severity_pivot[severity_order]
                
                # Create heatmap
                fig_heatmap = px.imshow(
                    severity_pivot,
                    labels=dict(x="Severity", y="Tactic", color="Percentage"),
                    x=severity_pivot.columns,
                    y=severity_pivot.index,
                    color_continuous_scale='RdYlBu_r',
                    aspect="auto"
                )
                
                fig_heatmap.update_layout(
                    title='Severity Distribution by Tactic (%)',
                    height=500
                )
                
                # Add percentage annotations
                for i, tactic in enumerate(severity_pivot.index):
                    for j, severity in enumerate(severity_pivot.columns):
                        value = severity_pivot.loc[tactic, severity]
                        fig_heatmap.add_annotation(
                            x=severity,
                            y=tactic,
                            text=f"{value:.1f}%",
                            showarrow=False,
                            font=dict(color="black" if value < 50 else "white")
                        )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning("No data available for severity by tactic heatmap.")
            
            # 10. Mean Time to Remediate by Severity
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Mean Time to Remediate by Severity</h4>
                    <p><strong>Definition:</strong> Shows the average time taken to close detections for each severity level.</p>
                    <p><strong>Use Case:</strong> Evaluate response efficiency and identify areas where remediation time needs improvement, particularly for critical and high-severity issues.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Mean Time to Remediate by Severity</h3>", unsafe_allow_html=True)
            
            # Calculate MTTR by severity
            mttr_severity = detection_data.groupby('SeverityName')['MTTR_Hours'].mean().reset_index()
            
            # Ensure severity order is correct
            mttr_severity['SeverityOrder'] = mttr_severity['SeverityName'].apply(lambda x: severity_order.index(x) if x in severity_order else 999)
            mttr_severity = mttr_severity.sort_values('SeverityOrder').copy()
            mttr_severity = mttr_severity.drop('SeverityOrder', axis=1)
            
            if not mttr_severity.empty:
                # Create labels based on settings
                mttr_severity.loc[:, 'Label'] = mttr_severity['MTTR_Hours'].round(2).astype(str) + " hrs"
                
                # Map colors to the severity levels
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
            else:
                st.warning("No MTTR data available to display.")
            
            # 11. Weekly detection trend
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Weekly Detection Trend</h4>
                    <p><strong>Definition:</strong> Shows the number of detections over time, broken down by week.</p>
                    <p><strong>Use Case:</strong> Identify trends and patterns in detection volumes, which may correlate with security events, patches, or organizational changes.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Weekly Detection Trend</h3>", unsafe_allow_html=True)
            
            # Check if week data is available
            if 'Week_Start' in detection_data.columns and not detection_data['Week_Start'].isna().all():
                weekly_counts = detection_data.groupby('Week_Start').size().reset_index(name='Count')
                weekly_counts = weekly_counts.sort_values('Week_Start').copy()
                
                # Format dates for display
                weekly_counts.loc[:, 'Display_Week'] = weekly_counts['Week_Start'].dt.strftime('%d/%m/%Y')
                
                fig_trend = go.Figure(go.Scatter(
                    x=weekly_counts['Display_Week'],
                    y=weekly_counts['Count'],
                    mode='lines+markers',
                    line=dict(color=trend_chart_color, width=3),
                    marker=dict(size=10, color=trend_chart_color)
                ))
                
                fig_trend.update_layout(
                    title='Weekly Detection Trend',
                    xaxis_title='Week Starting',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning("No weekly trend data available to display. Check date formats.")
            
            # Executive summary
            st.markdown("<h2 class='sub-header'>Executive Summary</h2>", unsafe_allow_html=True)
            
            # Generate default summary with bullet points
            if not detection_data.empty:
                # Prepare summary data
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
                default_summary = f"""<ul class="summary-bullet">
<li>During {report_period}, a total of {total_detections} security detections were observed across {unique_devices} unique devices.</li>
<li>{critical_detections} Critical ({critical_pct:.1f}%) and {high_detections} High ({high_pct:.1f}%) severity detections were recorded, requiring immediate attention.</li>
<li>The most common objective was "{top_objective}" with {top_objective_count} detections ({top_objective_pct:.1f}% of total).</li>
<li>Mean Time to Remediate (MTTR) averaged {avg_mttr:.1f} hours across all severities, with Critical detections resolved in {critical_mttr:.1f} hours on average.</li>
<li>The file "{top_file}" was involved in the most detections ({top_file_count}), suggesting it should be investigated further.</li>
<li>Of the resolved detections, {true_positives} were confirmed as true positives and {false_positives} were identified as false positives.</li>
"""

                # Add trend information if available
                if 'Week_Start' in detection_data.columns and not weekly_counts.empty:
                    first_week = weekly_counts.iloc[0]['Display_Week']
                    last_week = weekly_counts.iloc[-1]['Display_Week']
                    first_count = weekly_counts.iloc[0]['Count']
                    last_count = weekly_counts.iloc[-1]['Count']
                    trend_change = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
                    
                    default_summary += f"<li>Detection volume {trend_change > 0 and 'increased' or 'decreased'} by {abs(trend_change):.1f}% from the week of {first_week} ({first_count} detections) to the week of {last_week} ({last_count} detections).</li>\n"
                
                default_summary += "</ul>"
            else:
                default_summary = """<ul class="summary-bullet">
<li>Insufficient data to generate a comprehensive executive summary.</li>
<li>Please ensure your data includes detection information, severity levels, and timestamps.</li>
</ul>"""
            
            # Let users edit the summary
            edited_summary_raw = st.text_area("Edit Executive Summary", value=default_summary.replace('<ul class="summary-bullet">', '').replace('</ul>', '').replace('<li>', '• ').replace('</li>', '\n'), height=200)
            
            # Convert back to HTML with bullet points
            edited_summary = f'<ul class="summary-bullet">{edited_summary_raw.replace("• ", "<li>").replace("\n", "</li>")}</li></ul>'
            
            # Display the edited summary
            st.markdown(f"<div class='insight-card'>{edited_summary}</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error processing data: {e}")
            st.error("Please check your data format and try again.")