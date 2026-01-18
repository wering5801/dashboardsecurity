import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import base64
from io import BytesIO
from theme_utils import setup_theme

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
    /* Platform Distribution Card - light mode */
    .platform-card {
        background-color: #1e3a8a;
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .platform-card h2 {
        color: white;
        margin-top: 0;
        margin-bottom: 15px;
    }
    .platform-card p {
        color: white;
        font-size: 16px;
    }
    .platform-content {
        background-color: #1e3a8a;
        color: #333333;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    /* Executive summary styling */
    .executive-summary {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .executive-summary-blue {
        background-color: #1e3a8a;
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .executive-summary-blue li {
        color: white;
        margin-bottom: 10px;
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
    /* File upload validation styling */
    .validation-success {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .validation-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #dc3545;
    }
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .platform-content {
            background-color: #2d3748;
            color: #ffffff;
        }
        .insight-card {
            background-color: #2d3748;
        }
        .insight-card h3, .insight-card p {
            color: #ffffff;
        }
        .executive-summary {
            background-color: #2d3748;
            color: #ffffff;
        }
    }
    </style>
    """

def validate_host_file(df):
    """Validate if the uploaded file has the required columns"""
    required_columns = [
        'UniqueNo', 'Hostname', 'UserName', 'OS Version', 
        'Sensor Version', 'Site', 'OU', 'Detect MALAYSIA TIME FORMULA'
    ]
    
    validation_results = {
        'is_valid': True,
        'missing_columns': [],
        'found_columns': [],
        'total_rows': len(df)
    }
    
    for col in required_columns:
        if col in df.columns:
            validation_results['found_columns'].append(col)
        else:
            validation_results['missing_columns'].append(col)
            validation_results['is_valid'] = False
    
    return validation_results

def display_validation_results(validation_results):
    """Display validation results with green ticks and red crosses"""
    st.markdown("### 📋 Template Validation Report")
    
    required_columns = [
        'UniqueNo', 'Hostname', 'UserName', 'OS Version', 
        'Sensor Version', 'Site', 'OU', 'Detect MALAYSIA TIME FORMULA'
    ]
    
    for col in required_columns:
        if col in validation_results['found_columns']:
            st.markdown(f'<div class="validation-success">✅ Found required column: "{col}"</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="validation-error">❌ Missing required column: "{col}"</div>', 
                       unsafe_allow_html=True)
    
    if validation_results['is_valid']:
        st.success(f"✅ File validation successful! Found {validation_results['total_rows']} data rows.")
        return True
    else:
        st.error("❌ File validation failed! Please ensure your file contains all required columns.")
        return False

def host_analysis_dashboard():
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    st.markdown(centered_table_css(), unsafe_allow_html=True)

    # ========== SIDEBAR CONFIGURATION ==========
    with st.sidebar:
        st.markdown("## Host Analysis Settings")
        report_period = st.text_input("Report Period", "February 2025")
        st.markdown("<div>Display Top:</div>", unsafe_allow_html=True)
        top_n = st.radio(
            "Display Top:", 
            options=[3, 5, 10], 
            index=1,  # Default to 5 (index 1)
            horizontal=True,
            label_visibility="collapsed"
        )
        show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
        
        with st.expander("📊 Visualization Settings"):
            st.markdown("### Customize Chart Appearance")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Chart Colors")
                risk_chart_color = st.color_picker("Risk Chart", "#3498db")
                platform_chart_color = st.color_picker("Platform Chart", "#2ecc71")
                detections_chart_color = st.color_picker("Detections Chart", "#f39c12")
                host_chart_color = st.color_picker("Host Chart", "#9b59b6")
            with col2:
                st.markdown("#### Label Options")
                show_percentages = st.checkbox("Show Percentages", value=True)
                show_values = st.checkbox("Show Values", value=True)
                show_labels = st.checkbox("Show Labels", value=True)
        
        with st.expander("📋 Required File Format"):
            st.write("""
            ### Required Columns
            
            Your CSV file must contain these exact column names:
            
            ✅ **UniqueNo** - Unique identifier for each detection  
            ✅ **Hostname** - Computer/Host name where detection occurred  
            ✅ **UserName** - User account name associated with the detection  
            ✅ **OS Version** - Operating system version (e.g., Windows 10, Windows 11)  
            ✅ **Sensor Version** - Security sensor/agent version number  
            ✅ **Site** - Physical location or site name  
            ✅ **OU** - Organizational Unit in Active Directory  
            ✅ **Detect MALAYSIA TIME FORMULA** - Detection timestamp (DD/MM/YYYY HH:MM format)  
            
            **Note:** Column names must match exactly (case-sensitive).
            """)
        
        # File upload section
        st.markdown("### 📁 Upload Host Data File")
        uploaded_file = st.file_uploader(
            "Choose CSV file", 
            type=['csv'],
            help="Upload a CSV file with host detection data"
        )
        
        # Download sample template
        if st.button("📥 Download Sample Template"):
            sample_data = {
                'UniqueNo': [4, 9, 17, 66],
                'Hostname': ['aabbcc', 'aasfsx', 'acsre', 'fsawd'],
                'UserName': ['ali', 'abu', 'acong', 'boboy'],
                'OS Version': ['Windows 10', 'Windows 11', 'Windows 10', 'Windows 7'],
                'Sensor Version': ['7.23.19508.0', '7.23.19508.0', '7.23.19508.0', '7.16.18613.0'],
                'Site': ['Kuantan', 'Kuching', 'Johor-Bahru', 'HQ'],
                'OU': ['KUANTAN,EAST_COAST,BRANCHES,EndUsers', 'KUCHING,SARAWAK,BRANCHES,EndUsers', 'ZTEMP,HQ,EndUsers', 'LAHAD_DATU,SABAH,BRANCHES,EndUsers'],
                'Detect MALAYSIA TIME FORMULA': ['28/2/2025 15:03', '25/2/2025 14:57', '21/2/2025 10:54', '3/2/2025 8:06']
            }
            sample_df = pd.DataFrame(sample_data)
            csv_data = sample_df.to_csv(index=False)
            st.download_button(
                label="Download",
                data=csv_data,
                file_name="host_analysis_sample_template.csv",
                mime="text/csv"
            )
        
        # Generate button
        generate_button = st.button(
            label="🚀 Generate Dashboard", 
            type="primary",
            disabled=(uploaded_file is None)
        )
        
        # Executive Summary section in sidebar
        st.header("📋 Executive Summary")
        st.write("The executive summary will be generated automatically based on the analysis.")

    # ========== MAIN DASHBOARD AREA ==========

    # Title with report period
    st.markdown(f"<h1 class='dashboard-title'>Host Analysis Dashboard - {report_period}</h1>", unsafe_allow_html=True)

    # Show file upload status
    if uploaded_file is None:
        st.info("👈 Please upload a CSV file in the sidebar to begin analysis")
        st.markdown("""
        ### Welcome to Host Analysis Dashboard
        
        This dashboard provides comprehensive analysis of host-based security detections.
        
        **To get started:**
        1. Download the sample template from the sidebar
        2. Prepare your data in the same format
        3. Upload your CSV file
        4. Click "Generate Dashboard"
        
        **The dashboard will show:**
        - Hosts with Most Detections
        - Users with Most Detections  
        - Platform Distribution Analysis
        - Sensor Version Status
        - Detection Activity Over Time
        - Executive Summary with Key Insights
        """)
        return

    if generate_button and uploaded_file is not None:
        try:
            # Read the uploaded file
            host_data = pd.read_csv(uploaded_file)
            
            # Validate the file structure
            validation_results = validate_host_file(host_data)
            is_valid = display_validation_results(validation_results)
            
            if not is_valid:
                st.stop()
            
            # Process the data
            st.success("✅ File uploaded and validated successfully!")
            
            # Parse detection time
            try:
                host_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    host_data['Detect MALAYSIA TIME FORMULA'], 
                    format='%d/%m/%Y %H:%M',
                    errors='coerce'
                )
            except Exception as e:
                st.warning(f"Warning: Some date values could not be parsed correctly. Using a more flexible parser.")
                host_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    host_data['Detect MALAYSIA TIME FORMULA'], 
                    errors='coerce'
                )
            
            # Convert UniqueNo to numeric
            host_data['UniqueNo'] = pd.to_numeric(host_data['UniqueNo'], errors='coerce').fillna(0).astype(int)
            
            # Extract Platform from OS Version
            host_data['Platform'] = host_data['OS Version'].apply(
                lambda x: 'Windows' if 'Windows' in str(x) else ('macOS' if 'macOS' in str(x) else 'Other')
            )
            
            # Basic statistics
            total_hosts = host_data['Hostname'].nunique()
            total_detections = len(host_data)
            
            # Get most recent date
            latest_date = host_data['Detect MALAYSIA TIME FORMULA'].max()
            month_year = latest_date.strftime('%B %Y') if pd.notnull(latest_date) else report_period
            
            # Display dashboard
            st.markdown(f"<h2 class='sub-header'>Host Overview</h2>", unsafe_allow_html=True)
            
            # Overview metrics - full width
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Hosts", total_hosts)
            with col2:
                st.metric("Total Detections", total_detections)
            with col3:
                windows_count = len(host_data[host_data['Platform'] == 'Windows'])
                st.metric("Windows Hosts", windows_count)
            with col4:
                avg_detections = total_detections / total_hosts if total_hosts > 0 else 0
                st.metric("Avg. Detections per Host", f"{avg_detections:.1f}")
            
            # 1. Hosts with Most Detections - Using top_n from user selection
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Hosts with Most Detections</h4>
                    <p><strong>Definition:</strong> Shows the hosts with the highest number of security detections.</p>
                    <p><strong>Use Case:</strong> Identify the most vulnerable hosts in your environment that require immediate attention.</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"<h3>Top {top_n} Hosts with Most Detections</h3>", unsafe_allow_html=True)
            
            # Count detections by hostname
            host_counts = host_data.groupby('Hostname').size().reset_index(name='Count')
            host_counts = host_counts.sort_values('Count', ascending=False)
            
            if not host_counts.empty:
                # Get top N hosts based on user selection
                top_hosts = host_counts.head(top_n)
                
                # Calculate percentages
                if show_percentages:
                    top_hosts['Percentage'] = (top_hosts['Count'] / total_detections * 100).round(1)
                
                # Create labels
                if show_percentages and show_values:
                    top_hosts['Label'] = top_hosts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    top_hosts['Label'] = top_hosts['Percentage'].apply(lambda x: f"({x}%)")
                elif show_values:
                    top_hosts['Label'] = top_hosts['Count']
                else:
                    top_hosts['Label'] = ""
                
                # Create horizontal bar chart
                fig_hosts = go.Figure(data=[go.Bar(
                    x=top_hosts['Count'],
                    y=top_hosts['Hostname'],
                    text=top_hosts['Label'] if show_labels else None,
                    textposition='outside',
                    orientation='h',
                    marker_color=host_chart_color
                )])
                
                fig_hosts.update_layout(
                    title=f'Top {top_n} Hosts with Most Detections',
                    xaxis_title='Number of Detections',
                    yaxis_title='Hostname',
                    height=400
                )
                
                st.plotly_chart(fig_hosts, use_container_width=True)
                
                # Key analysis for Hosts with Most Detections
                key_host = f"The host(s) with the most detections are: {', '.join(top_hosts['Hostname'])}. This highlights the most vulnerable endpoints that require immediate attention."
                st.info(key_host)
                
                # Show detailed table of top hosts
                st.markdown("<h4>Details of Top Hosts</h4>", unsafe_allow_html=True)
                
                # Get additional info for top hosts
                top_host_details = []
                for host in top_hosts['Hostname']:
                    host_rows = host_data[host_data['Hostname'] == host]
                    latest_row = host_rows.sort_values('Detect MALAYSIA TIME FORMULA', ascending=False).iloc[0]
                    top_host_details.append({
                        'Hostname': host,
                        'OS Version': latest_row['OS Version'],
                        'UserName': latest_row['UserName'],
                        'Detections': host_counts[host_counts['Hostname'] == host]['Count'].values[0],
                        'Last Seen': latest_row['Detect MALAYSIA TIME FORMULA'],
                        'Site': latest_row['Site'],
                        'Sensor Version': latest_row['Sensor Version']
                    })
                
                top_host_df = pd.DataFrame(top_host_details)
                
                # Format dates
                if 'Last Seen' in top_host_df.columns and pd.api.types.is_datetime64_dtype(top_host_df['Last Seen']):
                    top_host_df['Last Seen'] = top_host_df['Last Seen'].dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(top_host_df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
            else:
                st.warning("No host detection data available.")
            
            # 2. Users with Most Detections - Using top_n from user selection
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Users with Most Detections</h4>
                    <p><strong>Definition:</strong> Shows the users associated with the most security detections.</p>
                    <p><strong>Use Case:</strong> Identify potential user-related security patterns and focus user awareness training on those with the most security issues.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>Top {top_n} Users with Most Detections</h3>", unsafe_allow_html=True)
            
            # Remove blank usernames before counting
            filtered_host_data = host_data[host_data['UserName'].str.strip() != '']
            # Count detections by user (excluding blank usernames)
            user_counts = filtered_host_data.groupby('UserName').size().reset_index(name='Count')
            user_counts = user_counts.sort_values('Count', ascending=False)
            
            if not user_counts.empty:
                # Get top N users based on user selection
                top_users = user_counts.head(top_n)
                
                # Calculate percentages
                if show_percentages:
                    top_users['Percentage'] = (top_users['Count'] / total_detections * 100).round(1)
                
                # Create labels
                if show_percentages and show_values:
                    top_users['Label'] = top_users.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
                elif show_percentages:
                    top_users['Label'] = top_users['Percentage'].apply(lambda x: f"({x}%)")
                elif show_values:
                    top_users['Label'] = top_users['Count']
                else:
                    top_users['Label'] = ""
                
                # Create horizontal bar chart
                fig_users = go.Figure(data=[go.Bar(
                    x=top_users['Count'],
                    y=top_users['UserName'],
                    text=top_users['Label'] if show_labels else None,
                    textposition='outside',
                    orientation='h',
                    marker_color=detections_chart_color
                )])
                
                fig_users.update_layout(
                    title=f'Top {top_n} Users with Most Detections',
                    xaxis_title='Number of Detections',
                    yaxis_title='User',
                    height=400
                )
                
                st.plotly_chart(fig_users, use_container_width=True)
                
                # Key analysis for Users with Most Detections
                key_user = f"The user(s) with the most detections are: {', '.join(top_users['UserName'])}. Focus user awareness and investigation on these accounts."
                st.info(key_user)
                
                # Show detailed user information
                st.markdown("<h4>User Details</h4>", unsafe_allow_html=True)
                
                # Get hosts for each top user
                user_details = []
                for user in top_users['UserName']:
                    user_rows = filtered_host_data[filtered_host_data['UserName'] == user]
                    unique_hosts = user_rows['Hostname'].nunique()
                    user_details.append({
                        'UserName': user,
                        'Detections': user_counts[user_counts['UserName'] == user]['Count'].values[0],
                        'Unique Hosts': unique_hosts,
                        'Sites': ', '.join(user_rows['Site'].unique())
                    })
                
                user_details_df = pd.DataFrame(user_details)
                st.dataframe(user_details_df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
            else:
                st.warning("No user detection data available.")
            
            # 3. Platform with Most Detections
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Platform Distribution</h4>
                    <p><strong>Definition:</strong> Shows the breakdown of detections by operating system platform.</p>
                    <p><strong>Use Case:</strong> Understand which platforms are most affected by security issues to focus security efforts accordingly.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Platform Distribution</h3>", unsafe_allow_html=True)
            
            # Count detections by platform and OS version
            platform_counts = host_data.groupby('Platform').size().reset_index(name='Count')
            platform_counts = platform_counts.sort_values('Count', ascending=False)
            
            os_counts = host_data.groupby('OS Version').size().reset_index(name='Count')
            os_counts = os_counts.sort_values('Count', ascending=False)
            
            # Platform Distribution Card - improved for better contrast
            if not platform_counts.empty:
                # Get the platform data
                top_platform = platform_counts.iloc[0]['Platform']
                top_platform_count = platform_counts.iloc[0]['Count']
                top_platform_pct = (top_platform_count / total_detections * 100) if total_detections > 0 else 0
                
                # Get top OS version
                top_os = ""
                top_os_count = 0
                top_os_pct = 0
                if not os_counts.empty:
                    top_os = os_counts.iloc[0]['OS Version']
                    top_os_count = os_counts.iloc[0]['Count']
                    top_os_pct = (top_os_count / total_detections * 100) if total_detections > 0 else 0
                
                # Create visualizations side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create the pie chart for platform distribution
                    fig_platform = px.pie(
                        platform_counts, 
                        values='Count', 
                        names='Platform',
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        height=350,
                        title="Detections by Platform"
                    )
                    
                    fig_platform.update_traces(
                        textinfo='percent+label' if show_percentages else 'label',
                        textfont_size=14
                    )
                    
                    fig_platform.update_layout(
                        margin=dict(t=30, b=0, l=0, r=0),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_platform, use_container_width=True)
                
                with col2:
                    # Create the bar chart for OS version - limited to top_n based on user selection
                    top_os_versions = os_counts.head(top_n)
                    
                    fig_os = go.Figure(data=[go.Bar(
                        x=top_os_versions['OS Version'],
                        y=top_os_versions['Count'],
                        marker_color=platform_chart_color
                    )])
                    
                    fig_os.update_layout(
                        title=f'Top {top_n} OS Versions',
                        xaxis_title='OS Version',
                        yaxis_title='Number of Detections',
                        height=350,
                        margin=dict(t=30, b=0, l=0, r=0)
                    )
                    
                    st.plotly_chart(fig_os, use_container_width=True)
                
                # Show OS version table - limited to top_n based on user selection
                st.markdown(f"<h4>Top {top_n} OS Version Distribution</h4>", unsafe_allow_html=True)
                
                # Add percentage to OS counts
                os_counts_display = os_counts.head(top_n).copy()
                os_counts_display['Percentage'] = (os_counts_display['Count'] / total_detections * 100).round(1)
                os_counts_display['Percentage'] = os_counts_display['Percentage'].astype(str) + '%'
                
                st.dataframe(os_counts_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
            else:
                st.warning("No platform data available to display.")
            
            # 4. Hosts with Sensor Version status
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Hosts with Sensor Version Status</h4>
                    <p><strong>Definition:</strong> Identifies hosts running different versions of security sensors, highlighting those with outdated versions.</p>
                    <p><strong>Use Case:</strong> Prioritize sensor updates to ensure all hosts have the latest security protections.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Hosts with Sensor Version Status</h3>", unsafe_allow_html=True)
            
            # Group by sensor version
            sensor_counts = host_data.groupby('Sensor Version').size().reset_index(name='Count')
            sensor_counts = sensor_counts.sort_values('Count', ascending=False)
            
            # Determine latest sensor version (assuming highest version number is latest)
            latest_sensor = None
            outdated_hosts = None
            
            if not sensor_counts.empty:
                # Extract version numbers and find the highest
                version_tuples = []
                for version in sensor_counts['Sensor Version']:
                    try:
                        # Extract version components (e.g. 7.23.19508.0 -> [7, 23, 19508, 0])
                        components = [int(x) for x in version.split('.')]
                        version_tuples.append((version, components))
                    except (ValueError, AttributeError):
                        # Skip versions that can't be parsed
                        continue
                
                if version_tuples:
                    # Sort by version components
                    version_tuples.sort(key=lambda x: x[1], reverse=True)
                    latest_sensor = version_tuples[0][0]
                    
                    # Find hosts with outdated sensors
                    outdated_hosts_data = []
                    for host in host_data['Hostname'].unique():
                        host_rows = host_data[host_data['Hostname'] == host]
                        latest_row = host_rows.sort_values('Detect MALAYSIA TIME FORMULA', ascending=False).iloc[0]
                        if latest_row['Sensor Version'] != latest_sensor:
                            outdated_hosts_data.append({
                                'Hostname': host,
                                'OS Version': latest_row['OS Version'],
                                'UserName': latest_row['UserName'],
                                'Current Sensor': latest_row['Sensor Version'],
                                'Latest Sensor': latest_sensor,
                                'Last Seen': latest_row['Detect MALAYSIA TIME FORMULA'],
                                'Site': latest_row['Site']
                            })
                    
                    outdated_hosts = pd.DataFrame(outdated_hosts_data)
               
                # Create bar chart of sensor versions with better colors - limited to top_n based on user selection
                # Only if there are more versions than top_n
                display_sensors = sensor_counts
                if len(sensor_counts) > top_n:
                    display_sensors = sensor_counts.head(top_n)
                
                fig_sensors = go.Figure(data=[go.Bar(
                    x=display_sensors['Sensor Version'],
                    y=display_sensors['Count'],
                    marker_color=[risk_chart_color if v == latest_sensor else '#e74c3c' for v in display_sensors['Sensor Version']]
                )])
                
                fig_sensors.update_layout(
                    title=f'Top {len(display_sensors)} Sensor Versions',
                    xaxis_title='Sensor Version',
                    yaxis_title='Number of Hosts',
                    height=400
                )
                
                st.plotly_chart(fig_sensors, use_container_width=True)
                
                # Key analysis for Sensor Version Status
                if outdated_hosts is not None and not outdated_hosts.empty:
                    key_sensor = f"{len(outdated_hosts)} host(s) are running outdated sensor versions. Update these hosts to the latest version ({latest_sensor}) to reduce risk."
                else:
                    key_sensor = "All hosts are running the latest sensor version."
                st.info(key_sensor)
                
                # Show outdated host information - limited to top_n based on user selection
                if outdated_hosts is not None and not outdated_hosts.empty:
                    # Sort outdated hosts by detection time (most recent first)
                    outdated_hosts = outdated_hosts.sort_values('Last Seen', ascending=False)
                    
                    total_outdated = len(outdated_hosts)
                    display_outdated = outdated_hosts
                    
                    if len(outdated_hosts) > top_n:
                        display_outdated = outdated_hosts.head(top_n)
                        st.markdown(f"<h4>Top {top_n} of {total_outdated} Hosts Running Outdated Sensor Versions</h4>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h4>{total_outdated} Hosts Running Outdated Sensor Versions</h4>", unsafe_allow_html=True)
                    
                    st.markdown(f"Current recommended version: **{latest_sensor}**", unsafe_allow_html=True)
                    
                    # Format dates
                    if 'Last Seen' in display_outdated.columns and pd.api.types.is_datetime64_dtype(display_outdated['Last Seen']):
                        display_outdated['Last Seen'] = display_outdated['Last Seen'].dt.strftime('%d/%m/%Y %H:%M')
                    
                    st.dataframe(display_outdated.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
                else:
                    st.success("All hosts are running the latest sensor version.")
            else:
                st.warning("No sensor version data available.")
            
            # 5. Most host date detection activity
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Most Host Date Detection Activity</h4>
                    <p><strong>Definition:</strong> Shows detection activity trends over time, highlighting days with the most security incidents.</p>
                    <p><strong>Use Case:</strong> Identify peak detection periods that may correlate with security events or organizational changes.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>Detection Activity Over Time</h3>", unsafe_allow_html=True)
            
            # Group detections by date
            if 'Detect MALAYSIA TIME FORMULA' in host_data.columns and not host_data['Detect MALAYSIA TIME FORMULA'].isna().all():
                host_data['Detection Date'] = host_data['Detect MALAYSIA TIME FORMULA'].dt.date
                date_counts = host_data.groupby('Detection Date').size().reset_index(name='Count')
                date_counts = date_counts.sort_values('Detection Date')
                
                # Find date with most detections
                max_date = date_counts.loc[date_counts['Count'].idxmax()]
                max_date_str = max_date['Detection Date'].strftime('%d/%m/%Y')
                max_count = max_date['Count']
                
                # Create line chart
                fig_dates = go.Figure(data=go.Scatter(
                    x=date_counts['Detection Date'],
                    y=date_counts['Count'],
                    mode='lines+markers',
                    line=dict(color=risk_chart_color, width=3),
                    marker=dict(size=8, color=risk_chart_color)
                ))
                
                fig_dates.update_layout(
                    title='Detection Activity Over Time',
                    xaxis_title='Date',
                    yaxis_title='Number of Detections',
                    height=400
                )
                
                # Add annotation for peak day
                fig_dates.add_annotation(
                    x=max_date['Detection Date'],
                    y=max_count,
                    text=f"Peak: {max_count} detections",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40
                )
                
                st.plotly_chart(fig_dates, use_container_width=True)
                
                # Key analysis for Detection Activity Over Time
                key_date = f"The peak detection day was {max_date_str} with {max_count} detections. Monitor for similar spikes to detect potential incidents early."
                st.info(key_date)
                
                # Show detection activity table - limited to top_n based on user selection
                st.markdown(f"<h4>Top {top_n} Days with Most Detections</h4>", unsafe_allow_html=True)
                
                # Format date for display and sort by count
                date_counts_display = date_counts.sort_values('Count', ascending=False).head(top_n).copy()
                date_counts_display['Detection Date'] = date_counts_display['Detection Date'].apply(lambda x: x.strftime('%d/%m/%Y'))
                date_counts_display['Percentage'] = (date_counts_display['Count'] / total_detections * 100).round(1)
                date_counts_display['Percentage'] = date_counts_display['Percentage'].astype(str) + '%'
                
                st.dataframe(date_counts_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
                
                # Show hosts detected on peak day - limited to top_n based on user selection
                peak_day_hosts = host_data[host_data['Detection Date'] == max_date['Detection Date']]
                
                # Sort peak day hosts by time and get top_n
                peak_day_hosts = peak_day_hosts.sort_values('Detect MALAYSIA TIME FORMULA', ascending=False)
                
                if len(peak_day_hosts) > top_n:
                    st.markdown(f"<h4>Top {top_n} Hosts Detected on Peak Day ({max_date_str})</h4>", unsafe_allow_html=True)
                    peak_day_hosts_display = peak_day_hosts.head(top_n)
                else:
                    st.markdown(f"<h4>Hosts Detected on Peak Day ({max_date_str})</h4>", unsafe_allow_html=True)
                    peak_day_hosts_display = peak_day_hosts
                
                peak_day_hosts_display = peak_day_hosts_display[['Hostname', 'UserName', 'OS Version', 'Site', 'Detect MALAYSIA TIME FORMULA']].copy()
                peak_day_hosts_display['Detect MALAYSIA TIME FORMULA'] = peak_day_hosts_display['Detect MALAYSIA TIME FORMULA'].dt.strftime('%d/%m/%Y %H:%M')
                peak_day_hosts_display.columns = ['Hostname', 'User', 'OS Version', 'Site', 'Detection Time']
                
                st.dataframe(peak_day_hosts_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
            else:
                st.warning("No detection date data available.")
            
            # Executive summary
            st.markdown("<h2>Executive Summary</h2>", unsafe_allow_html=True)
            
            # Generate default summary with bullet points
            if total_hosts > 0:
                # Create summary text
                summary_text = f"""• This report for {report_period} host analysis reveals {total_hosts} unique hosts with {total_detections} security detections."""
                
                # Add top host info if available
                if not host_counts.empty:
                    top_host = host_counts.iloc[0]['Hostname']
                    top_host_count = host_counts.iloc[0]['Count']
                    summary_text += f"""
• The host "{top_host}" shows the highest detection count at {top_host_count} ({(top_host_count / total_detections * 100):.1f}% of total)."""
                
                # Add platform info if available
                if not platform_counts.empty:
                    summary_text += f"""
• {top_platform} is the dominant platform ({top_platform_pct:.1f}% of detections), with {top_os} being the most common OS version."""
                
                # Add sensor version info if available
                if outdated_hosts is not None and not outdated_hosts.empty:
                    summary_text += f"""
• {len(outdated_hosts)} hosts are running outdated sensor versions, potentially increasing security risk, with the recommended version being {latest_sensor} for optimal protection."""
                
                # Add detection activity info if available
                if 'Detection Date' in locals() and 'max_date_str' in locals():
                    summary_text += f"""
• Detection activity analysis shows {max_count} detections on {max_date_str}, the most recent date in the dataset."""
                
                # Add user info if available
                if not user_counts.empty:
                    top_user = user_counts.iloc[0]['UserName']
                    top_user_count = user_counts.iloc[0]['Count']
                    summary_text += f"""
• Based on this analysis, prioritize remediation for the high-risk hosts, update sensor versions on outdated hosts, and focus security measures on the {top_user} user who has the highest number of detections ({top_user_count})."""
            else:
                summary_text = "Insufficient data to generate a comprehensive executive summary."
            
            # Display the summary in the blue container only
            # Process the summary text outside the f-string to avoid backslash issues
            formatted_summary = summary_text.replace('• ', '<li>').replace('\n• ', '</li><li>').replace('\n', '<br>')

            st.markdown(f"""
            <div class="executive-summary-blue">
                <ul class="summary-bullet">
                    {formatted_summary}
                </li></ul>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error processing data: {e}")
            st.error("Please check your data format and try again.")