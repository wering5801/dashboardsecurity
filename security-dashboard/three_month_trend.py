import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from theme_utils import setup_theme
import base64
import io

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
    /* Success and alert cards */
    .success-card {
        padding: 15px;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin-bottom: 15px;
        font-family: sans-serif;
    }
    .success-card h3 {
        color: #155724;
        margin-top: 0;
        margin-bottom: 10px;
    }
    .success-card p {
        color: #155724;
        margin-bottom: 5px;
    }
    .alert-card {
        padding: 15px;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 5px;
        margin-bottom: 15px;
        font-family: sans-serif;
    }
    .alert-card h3 {
        color: #721c24;
        margin-top: 0;
        margin-bottom: 10px;
    }
    .alert-card p {
        color: #721c24;
        margin-bottom: 5px;
    }
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2980b9;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin-top: 5px;
    }
    /* Input section styling */
    .input-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #007bff;
    }
    .input-section h4 {
        color: #2c3e50;
        margin-top: 0;
        margin-bottom: 15px;
    }
    </style>
    """

def three_month_trend_dashboard():
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    
    # Apply centered table CSS
    st.markdown(centered_table_css(), unsafe_allow_html=True)
    
    # ========== SIDEBAR CONFIGURATION ==========
    with st.sidebar:
        st.title("🔧 Three Month Trend Settings")
        
        # Report Period
        st.header("📅 Report Configuration")
        report_period = st.text_input("Report Period", "February - April 2025")
        
        # Display options for top N
        st.header("📊 Display Options")
        top_n = st.radio("Display Top:", [3, 5, 10], index=1, horizontal=False)
        
        # Show/Hide Chart Definitions
        show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
        
        # Visual settings
        st.header("🎨 Visualization Settings")
        with st.expander("Chart Colors", expanded=False):
            severity_chart_color = st.color_picker("Severity Chart", "#3498db")
            trend_chart_color = st.color_picker("Trend Chart", "#e74c3c")
            category_chart_color = st.color_picker("Category Chart", "#2ecc71")
            host_chart_color = st.color_picker("Host Chart", "#f39c12")
            
        with st.expander("Label Options", expanded=False):
            show_percentages = st.checkbox("Show Percentages", value=True)
            show_values = st.checkbox("Show Values", value=True)
            show_labels = st.checkbox("Show Labels", value=True)
        
        # Instructions for data input
        st.header("📋 Data Input Instructions")
        with st.expander("How to Use This Dashboard", expanded=False):
            st.write("""
            ### Dashboard Overview
            
            This dashboard analyzes three-month security detection trends.
            
            **Input Sections:**
            1. **Detection & Severity Data**: Monthly totals and severity breakdown
            2. **Geographic & Host Data**: Country, hostname, and time-based information
            3. **Detection Categories**: Category names and counts for each month
            
            **Dashboard Features:**
            - Monthly detection volume trends
            - Severity distribution changes over time
            - Top detection categories by month
            - Geographic and host analysis
            - Executive summary with insights
            """)
        
        # Executive Summary Editor
        st.header("📋 Executive Summary")
        if 'executive_summary_trend' not in st.session_state:
            st.session_state.executive_summary_trend = ""
        
        edited_summary_raw = st.text_area(
            "Edit Executive Summary", 
            value=st.session_state.executive_summary_trend,
            height=200,
            help="Edit the executive summary here. It will be displayed at the bottom of the dashboard."
        )
        
        # Update session state
        st.session_state.executive_summary_trend = edited_summary_raw
    
    # ========== MAIN DASHBOARD AREA ==========
    
    # Title with report period
    st.markdown(f"<h1 class='dashboard-title'>Three Month Security Trend Analysis - {report_period}</h1>", unsafe_allow_html=True)
    
    # ========== DATA INPUT SECTIONS ==========
    st.markdown("## 📝 Data Input")
    st.markdown("Please enter your data in the three sections below:")
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📊 Detection & Severity", "🌍 Geographic & Host", "🎯 Detection Categories"])
    
    with tab1:
        st.markdown("### Detection Counts and Severity Distribution")
        
        detection_severity_data = st.text_area(
            "Enter Detection & Severity Data (tab-separated)",
            value="""Month	Total_Detections	Critical	High	Medium	Low
February	49	0	22	12	15
March	95	2	38	45	10
April	67	1	36	18	12""",
            height=150,
            help="Format: Month, Total_Detections, Critical, High, Medium, Low"
        )
    
    with tab2:
        st.markdown("### Geographic, Host, and Time-based Information")
        
        geo_host_data = st.text_area(
            "Enter Geographic & Host Data (tab-separated)", 
            value="""Month\tTop_Country\tCountry_Count\tTop_Hostname\tHost_Count\tTime_Peak_hours_detection\tPercentage\tHighest_detection_day_of_week_count\tDate
February\tMalaysia\t30\tAli\t13\t15:30\t60.5\t10\t28/2/2025
March\tSingapore\t22\tAcong\t18\t1:40\t48.2\t21\t13/3/2025
April\tMalaysia\t21\tAnand\t9\t17:15\t55.8\t15\t7/4/2025""",
            height=150,
            help="Format: Month, Top_Country, Country_Count, Top_Hostname, Host_Count, Time_Peak_hours_detection, Percentage, Highest_detection_day_of_week_count, Date (MTTR_Hours removed)"
        )
    
    with tab3:
        st.markdown("### Detection Categories by Month")
        
        category_data = st.text_area(
            "Enter Detection Categories Data (tab-separated)",
            value="""Month	Name	Count	Name	Count	Name	Count	Name	Count
February	Malware	28	Data Exfiltration	11	Malware	4	Data Exfiltration	5
March	Ransomware	28	Exploit	28	Data Exfiltration	28	Malware	8
April	Data Exfiltration	20	Malware	18	Malware	28	Ransomware	1""",
            height=150,
            help="Format: Month, Name, Count, Name, Count, Name, Count, Name, Count (4 categories per month)"
        )
    
    # Generate button
    if st.button("🚀 Generate Three Month Trend Dashboard", type="primary"):
        try:
            # Process Detection & Severity Data
            detection_lines = detection_severity_data.strip().split('\n')
            detection_headers = detection_lines[0].split('\t')
            detection_rows = [line.split('\t') for line in detection_lines[1:]]
            detection_df = pd.DataFrame(detection_rows, columns=detection_headers)
            
            # Convert numeric columns
            numeric_cols = ['Total_Detections', 'Critical', 'High', 'Medium', 'Low']
            for col in numeric_cols:
                if col in detection_df.columns:
                    detection_df[col] = pd.to_numeric(detection_df[col], errors='coerce').fillna(0)
            
            # Process Geographic & Host Data
            geo_lines = geo_host_data.strip().split('\n')
            geo_headers = geo_lines[0].split('\t')
            geo_rows = [line.split('\t') for line in geo_lines[1:]]
            geo_df = pd.DataFrame(geo_rows, columns=geo_headers)
            
            # Convert numeric columns for geo data
            geo_numeric_cols = ['Country_Count', 'Host_Count', 'Percentage', 'Highest_detection_day_of_week_count']
            for col in geo_numeric_cols:
                if col in geo_df.columns:
                    geo_df[col] = pd.to_numeric(geo_df[col], errors='coerce').fillna(0)
            
            # Process Categories Data
            cat_lines = category_data.strip().split('\n')
            cat_headers = cat_lines[0].split('\t')
            cat_rows = [line.split('\t') for line in cat_lines[1:]]
            cat_raw_df = pd.DataFrame(cat_rows, columns=cat_headers)
            
            # Parse category data into proper format
            categories_list = []
            for _, row in cat_raw_df.iterrows():
                month = row['Month']
                # Process Name/Count pairs
                for i in range(1, len(cat_headers), 2):
                    if i < len(cat_headers) and i+1 < len(cat_headers):
                        if cat_headers[i] == 'Name' and cat_headers[i+1] == 'Count':
                            category_name = str(row.iloc[i]).strip()
                            category_count = pd.to_numeric(row.iloc[i+1], errors='coerce')
                            
                            if pd.notna(category_count) and category_count > 0 and category_name and category_name != 'nan':
                                categories_list.append({
                                    'Month': month,
                                    'Category': category_name,
                                    'Count': int(category_count)
                                })
            
            categories_df = pd.DataFrame(categories_list)
            
            # Merge all data
            trend_data = detection_df.merge(geo_df, on='Month', how='inner')
            
            st.success("✅ Data processed successfully!")
            
            # Calculate metrics with safe operations
            total_detections = int(trend_data['Total_Detections'].sum())
            avg_detections = float(trend_data['Total_Detections'].mean())
            
            # Safe calculation for changes
            first_detection = float(trend_data['Total_Detections'].iloc[0])
            last_detection = float(trend_data['Total_Detections'].iloc[-1])
            total_change = last_detection - first_detection
            total_change_pct = (total_change / first_detection * 100) if first_detection > 0 else 0
            
            first_critical = float(trend_data['Critical'].iloc[0])
            last_critical = float(trend_data['Critical'].iloc[-1])
            critical_change = last_critical - first_critical
            critical_change_pct = (critical_change / max(first_critical, 1) * 100)
            
            # Display dashboard
            st.markdown("---")
            st.markdown("<h2 class='sub-header'>📊 Three Month Overview</h2>", unsafe_allow_html=True)
            
            # Overview metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Detections", f"{total_detections:,}", f"{total_change:+.0f}")
            with col2:
                st.metric("Avg Monthly Detections", f"{avg_detections:.0f}")
            with col3:
                st.metric("Detection Volume Change", f"{total_change_pct:+.1f}%")
            
            # Trend metrics cards
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{total_change_pct:+.1f}%</div>
                    <div class='metric-label'>Detection Volume Change</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{critical_change_pct:+.1f}%</div>
                    <div class='metric-label'>Critical Severity Change</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 1. Monthly Severity Distribution
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Monthly Severity Distribution</h4>
                    <p><strong>Definition:</strong> Shows how security detection severity levels change across the three-month period.</p>
                    <p><strong>Use Case:</strong> Track improvements or deterioration in security posture over time.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🚨 Monthly Severity Distribution</h3>", unsafe_allow_html=True)
            fig_severity = go.Figure()
            fig_severity.add_trace(go.Bar(
                x=trend_data['Month'],
                y=trend_data['Critical'],
                name='Critical',
                marker_color='#e74c3c'))
            fig_severity.add_trace(go.Bar(
                x=trend_data['Month'],
                y=trend_data['High'],
                name='High',
                marker_color='#f39c12'))
            fig_severity.add_trace(go.Bar(
                x=trend_data['Month'],
                y=trend_data['Medium'],
                name='Medium',
                marker_color='#f1c40f'))
            fig_severity.add_trace(go.Bar(
                x=trend_data['Month'],
                y=trend_data['Low'],
                name='Low',
                marker_color='#3498db'))
            fig_severity.update_layout(
                barmode='stack',
                title='Severity Distribution by Month',
                xaxis={'title': 'Month'},
                yaxis={'title': 'Number of Detections'},
                legend={'title': 'Severity'},
                height=500)
            st.plotly_chart(fig_severity, use_container_width=True)
            
            # Key insight for severity
            if critical_change < 0:
                st.info(f"💡 **Key Insight:** Critical detections decreased by {abs(critical_change):.0f} ({abs(critical_change_pct):.1f}%) from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}, indicating improved security posture.")
            else:
                st.warning(f"⚠️ **Key Insight:** Critical detections increased by {critical_change:.0f} ({critical_change_pct:.1f}%) from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}, requiring attention.")
            
            # 2. Top Hosts Analysis
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Top Hosts with Most Detections</h4>
                    <p><strong>Definition:</strong> Shows the hosts with highest detection counts across the three-month period.</p>
                    <p><strong>Use Case:</strong> Identify consistently problematic hosts that require remediation.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>💻 Top Hosts with Most Detections</h3>", unsafe_allow_html=True)
            
            # Create host data for visualization
            host_data = []
            for _, row in trend_data.iterrows():
                host_data.append({
                    'Host': str(row['Top_Hostname']),
                    'Count': int(row['Host_Count']),
                    'Month': str(row['Month'])
                })
            
            hosts_df = pd.DataFrame(host_data)
            
            # Create grouped bar chart for hosts by month
            fig_hosts = px.bar(hosts_df, 
                             x='Host', 
                             y='Count', 
                             color='Month',
                             title='Top Hosts by Month',
                             labels={'Count': 'Detection Count'},
                             height=400)
            st.plotly_chart(fig_hosts, use_container_width=True)
            
            # Display host data table
            st.markdown("<h4>📋 Host Detection Summary</h4>", unsafe_allow_html=True)
            host_summary = trend_data[['Month', 'Top_Hostname', 'Host_Count']].copy()
            host_summary.columns = ['Month', 'Top Host', 'Detection Count']
            st.dataframe(host_summary, use_container_width=True)
            
            # 3. Detection Categories Comparison
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Categories Comparison</h4>
                    <p><strong>Definition:</strong> Shows the evolution of different threat categories across the three months.</p>
                    <p><strong>Use Case:</strong> Identify emerging threats and declining threat types.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🎯 Detection Categories Comparison Across Three Months</h3>", unsafe_allow_html=True)
            
            if not categories_df.empty:
                # Create treemap for each month
                col_tech1, col_tech2, col_tech3 = st.columns(3)
                
                months = categories_df['Month'].unique()
                colors = ['Blues', 'Greens', 'Reds']
                
                for i, (month, color) in enumerate(zip(months, colors)):
                    month_data = categories_df[categories_df['Month'] == month].head(top_n)
                    if not month_data.empty:
                        fig_treemap = px.treemap(
                            month_data,
                            path=['Category'],
                            values='Count',
                            color='Count',
                            color_continuous_scale=color,
                            title=f'Top {top_n} Categories - {month}')
                        fig_treemap.update_traces(textinfo='label+value+percent parent')
                        
                        if i == 0:
                            with col_tech1:
                                st.plotly_chart(fig_treemap, use_container_width=True)
                        elif i == 1:
                            with col_tech2:
                                st.plotly_chart(fig_treemap, use_container_width=True)
                        else:
                            with col_tech3:
                                st.plotly_chart(fig_treemap, use_container_width=True)
                
                # Category trend analysis
                st.markdown("<h4>📈 Category Trend Analysis</h4>", unsafe_allow_html=True)
                
                # Calculate category insights
                months_list = list(months)
                if len(months_list) >= 2:
                    first_month = months_list[0]
                    last_month = months_list[-1]
                    
                    first_month_categories = set(categories_df[categories_df['Month'] == first_month]['Category'])
                    last_month_categories = set(categories_df[categories_df['Month'] == last_month]['Category'])
                    
                    persistent_categories = first_month_categories & last_month_categories
                    new_categories = last_month_categories - first_month_categories
                    declining_categories = first_month_categories - last_month_categories
                    
                    category_col1, category_col2 = st.columns(2)
                    
                    with category_col1:
                        st.markdown(f"""
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                            <h5>Persistent Threat Categories</h5>
                            <p>Categories present in both {first_month} and {last_month}: <strong>{', '.join(persistent_categories) if persistent_categories else 'None'}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                            <h5>Emerging Threat Categories</h5>
                            <p>New in {last_month}: <strong>{', '.join(new_categories) if new_categories else 'None'}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with category_col2:
                        st.markdown(f"""
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                            <h5>Declining Threat Categories</h5>
                            <p>Present in {first_month} but not in {last_month}: <strong>{', '.join(declining_categories) if declining_categories else 'None'}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # 4. Geographic and Peak Time Analysis
            st.markdown("<h3>🌍 Geographic Distribution and Peak Times</h3>", unsafe_allow_html=True)
            
            geo_col1, geo_col2 = st.columns(2)
            
            with geo_col1:
                st.markdown("<h4>Top Countries by Month</h4>", unsafe_allow_html=True)
                geo_data_display = trend_data[['Month', 'Top_Country', 'Country_Count']].copy()
                geo_data_display.columns = ['Month', 'Top Country', 'Detection Count']
                st.dataframe(geo_data_display, use_container_width=True)
            
            with geo_col2:
                st.markdown("<h4>Peak Detection Times</h4>", unsafe_allow_html=True)
                time_data = trend_data[['Month', 'Time_Peak_hours_detection', 'Percentage']].copy()
                time_data.columns = ['Month', 'Peak Time', 'Percentage']
                st.dataframe(time_data, use_container_width=True)
            
            # 5. Trend Insights
            st.markdown("<h2 class='sub-header'>🔍 Trend Insights</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Detection volume trend
                if total_change < 0:
                    st.markdown(f"""
                    <div class='success-card'>
                        <h3>Improved Security Posture</h3>
                        <p>Total detection volume decreased by {abs(total_change):.0f} ({abs(total_change_pct):.1f}%) 
                        from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <h3>Increasing Threat Activity</h3>
                        <p>Total detection volume increased by {total_change:.0f} ({total_change_pct:+.1f}%) 
                        from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Critical severity trend
                if critical_change < 0:
                    st.markdown(f"""
                    <div class='success-card'>
                        <h3>Critical Risk Reduction</h3>
                        <p>Critical severity detections decreased by {abs(critical_change):.0f} ({abs(critical_change_pct):.1f}%) 
                        from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <h3>Critical Risk Increase</h3>
                        <p>Critical severity detections increased by {critical_change:.0f} ({critical_change_pct:+.1f}%) 
                        from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]}.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Generate and update executive summary
            if not trend_data.empty:
                # Get key insights with safe operations
                try:
                    country_data = trend_data.groupby('Top_Country')['Country_Count'].sum()
                    top_country = str(country_data.idxmax()) if not country_data.empty else "Unknown"
                    
                    max_host_idx = trend_data['Host_Count'].idxmax()
                    top_host = str(trend_data.loc[max_host_idx, 'Top_Hostname'])
                    
                    max_detection_idx = trend_data['Total_Detections'].idxmax()
                    peak_month = str(trend_data.loc[max_detection_idx, 'Month'])
                    peak_detections = int(trend_data['Total_Detections'].max())
                    
                    # Calculate averages
                    avg_critical = float(trend_data['Critical'].mean())
                    avg_detections = float(trend_data['Total_Detections'].mean())
                    
                    # Create summary
                    default_summary = f"""• Three-month security analysis from {trend_data['Month'].iloc[0]} to {trend_data['Month'].iloc[-1]} shows a {total_change_pct:+.1f}% change in overall detection volume.
• Total detections across all three months: {total_detections:,}, with an average of {avg_detections:.0f} detections per month.
• Critical severity detections {'decreased' if critical_change < 0 else 'increased'} by {abs(critical_change):.0f} ({abs(critical_change_pct):.1f}%), with an average of {avg_critical:.1f} critical detections per month.
• {peak_month} showed the highest detection volume with {peak_detections} detections, requiring focused investigation.
• {top_country} emerged as the primary geographic concern, while {top_host} was the most problematic host during this period.
• Detection categories show evolving threat patterns with various persistent and emerging concerns.
• Overall trend indicates {'positive progress' if total_change < 0 else 'mixed results requiring attention'}, with security operations maintaining effectiveness."""
                    
                    # Update session state if it's empty
                    if not st.session_state.executive_summary_trend.strip():
                        st.session_state.executive_summary_trend = default_summary
                        
                except Exception as e:
                    st.warning(f"Could not generate full summary due to data processing: {e}")
            
            # Executive summary display
            st.markdown("<h2 class='sub-header'>📋 Executive Summary</h2>", unsafe_allow_html=True)
            
            if st.session_state.executive_summary_trend.strip():
                # Convert bullet points to HTML list
                summary_lines = st.session_state.executive_summary_trend.strip().split('\n')
                summary_html = "<ul class='summary-bullet'>"
                for line in summary_lines:
                    if line.strip():
                        clean_line = line.strip().lstrip('• ')
                        summary_html += f"<li>{clean_line}</li>"
                summary_html += "</ul>"
                
                # Display the summary
                st.markdown(f"<div class='insight-card'>{summary_html}</div>", unsafe_allow_html=True)
            else:
                st.info("📝 Use the sidebar to edit the executive summary after generating the dashboard.")
                
        except Exception as e:
            st.error(f"❌ Error processing data: {e}")
            st.error("Please check your data format and try again.")
            st.error("Make sure all three data sections are filled in correctly.")
    else:
        # Initial state - no dashboard generated yet
        st.info("👈 Configure your settings in the sidebar, then fill in the three data sections above and click 'Generate Dashboard'.")
        st.markdown("""
        ### Welcome to the Three Month Security Trend Analysis Dashboard
        
        This dashboard provides comprehensive three-month trend analysis including:
        
        - 📈 Monthly detection volume trends
        - 🚨 Severity distribution changes over time
        - 🎯 Detection category evolution
        - 💻 Host and geographic analysis
        - ⏱️ MTTR trend monitoring
        - 🔍 Emerging and declining threat patterns
        
        **Getting Started:**
        1. Use the sidebar to configure your report period and display preferences
        2. Fill in the three data input sections above:
           - **Detection & Severity**: Monthly totals and severity breakdown
           - **Geographic & Host**: Country, hostname, and time-based information  
           - **Detection Categories**: Category names and counts for each month
        3. Click 'Generate Three Month Trend Dashboard' to create your analysis
        4. Customize the executive summary in the sidebar as needed
        
        Sample data is pre-loaded for demonstration purposes.
        """)

if __name__ == "__main__":
    three_month_trend_dashboard()