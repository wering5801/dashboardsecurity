import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objects as go
from theme_utils import setup_theme
import datetime
import calendar
from datetime import datetime, timedelta
import re

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
    /* Dashboard title with report period */
    .dashboard-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    /* Definition cards */
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
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 5px 0 5px 10px;
        margin: 20px 0 15px 0;
        border-left: 4px solid #3498db;
        background-color: #f8f9fa;
    }
    /* Metrics display */
    .metrics-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin: 20px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        width: 30%;
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
    /* Executive summary styling */
    .executive-summary-card {
        background-color: #f0f8ff;
        border-left: 4px solid #3498db;
        padding: 20px;
        margin-top: 20px;
        border-radius: 5px;
    }
    .executive-summary-card h3 {
        margin-top: 0;
        color: #2c3e50;
        font-size: 1.5rem;
    }
    .executive-summary-card ul {
        margin-top: 10px;
        margin-bottom: 0;
        padding-left: 20px;
    }
    .executive-summary-card li {
        margin-bottom: 8px;
        color: #2c3e50;
    }
    .insight-card {
        background-color: #f0f8ff;
        border-left: 4px solid #3498db;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 5px 5px 0;
    }
    .insight-card h4 {
        margin-top: 0;
        color: #2c3e50;
    }
    .insight-card p {
        margin-bottom: 0;
        color: #34495e;
    }
    /* Progress buttons */
    .progress-button {
        background-color: #3498db;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        margin-right: 10px;
        display: inline-block;
        text-align: center;
        font-weight: bold;
    }
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
    """

def preprocess_weekly_data(detection_data):
    """Process weekly data in a safer way"""
    # Return empty dataframe if no data
    if detection_data.empty:
        return pd.DataFrame({'Week_Num': [1], 'Count': [0], 'WoW_Change': [0.0]})
    
    # Extract weeks
    if 'Detect MALAYSIA TIME FORMULA' in detection_data.columns:
        try:
            # Make sure dates are parsed properly
            if not pd.api.types.is_datetime64_dtype(detection_data['Detect MALAYSIA TIME FORMULA']):
                detection_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    detection_data['Detect MALAYSIA TIME FORMULA'], 
                    errors='coerce'
                )
            
            # Extract week number
            detection_data['Week'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.isocalendar().week
            
            # Handle missing values
            detection_data = detection_data.dropna(subset=['Week'])
            
            # If no data left after dropping NA, return empty frame
            if len(detection_data) == 0:
                return pd.DataFrame({'Week_Num': [1], 'Count': [0], 'WoW_Change': [0.0]})
            
            # Adjust week numbers to relative (Week 1, 2, 3, 4)
            min_week = detection_data['Week'].min()
            detection_data['Week_Num'] = detection_data['Week'] - min_week + 1
            
            # Get weekly counts using value_counts instead of groupby
            week_counts = detection_data['Week_Num'].value_counts().sort_index()
            
            # Convert to dataframe with explicit index
            weekly_df = pd.DataFrame({'Week_Num': week_counts.index, 'Count': week_counts.values})
            
            # Ensure all weeks are represented
            max_week = int(weekly_df['Week_Num'].max())
            all_weeks = list(range(1, max_week + 1))
            complete_weeks = pd.DataFrame({'Week_Num': all_weeks})
            weekly_df = complete_weeks.merge(weekly_df, on='Week_Num', how='left').fillna(0)
            weekly_df['Count'] = weekly_df['Count'].astype(int)
            
            # Calculate changes
            changes = []
            for i in range(len(weekly_df)):
                if i == 0:
                    changes.append(0.0)
                else:
                    prev = weekly_df.iloc[i-1]['Count']
                    curr = weekly_df.iloc[i]['Count']
                    if prev > 0:
                        changes.append(((curr - prev) / prev * 100))
                    else:
                        changes.append(0.0)
            
            weekly_df['WoW_Change'] = changes
            return weekly_df
        except Exception as e:
            # If any error occurs, return empty dataframe
            print(f"Error in weekly data preprocessing: {e}")
            return pd.DataFrame({'Week_Num': [1], 'Count': [0], 'WoW_Change': [0.0]})
    else:
        # No date column available
        return pd.DataFrame({'Week_Num': [1], 'Count': [0], 'WoW_Change': [0.0]})

def time_based_analysis_dashboard():
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    
    # Apply centered table CSS
    st.markdown(centered_table_css(), unsafe_allow_html=True)
    
    # ========== SIDEBAR CONFIGURATION ==========
    with st.sidebar:
        st.title("🔧 Time-Based Analysis Settings")
        
        # Report Period
        st.header("📅 Report Configuration")
        report_period = st.text_input("Report Period", "February 2025")
        
        # Display options for top N
        #st.header("📊 Display Options")
        #top_n = st.radio("Display Top:", [3, 5, 10], index=1, horizontal=False)
        
        # Show/Hide Chart Definitions
        show_definitions = st.checkbox("Show Chart Definitions and Use Cases", value=False)
        
        # Visual settings
        st.header("🎨 Visualization Settings")
        with st.expander("Chart Colors", expanded=False):
            daily_trend_color = st.color_picker("Daily Trend", "#3498db")
            moving_avg_color = st.color_picker("Moving Average", "#e74c3c")
            hourly_color = st.color_picker("Hourly Chart", "#2ecc71")
            weekday_color = st.color_picker("Weekday Chart", "#9b59b6")
            weekend_color = st.color_picker("Weekend Chart", "#e74c3c")
            weekly_comp_color = st.color_picker("Weekly Comparison", "#f39c12")
        
        with st.expander("Label Options", expanded=False):
            show_percentages = st.checkbox("Show Percentages", value=True)
            show_values = st.checkbox("Show Values", value=True)
            show_grid = st.checkbox("Show Grid Lines", value=True)
            show_annotations = st.checkbox("Show Annotations", value=True)
        
        # Instructions for data input
        st.header("📋 Data Input Instructions")
        with st.expander("How to Use This Dashboard", expanded=False):
            st.write("""
            ### Dashboard Overview
            
            This dashboard analyzes security detections over time to identify patterns and trends.
            
            **Expected Data Format:**
            Each row should represent one detection with tab-separated columns:
            
            ```
            UniqueNo | Hostname | Detect MALAYSIA TIME FORMULA
            ```
            
            **Date Format:** dd/mm/yyyy hh:mm
            Example: 28/2/2025 15:03
            
            **Dashboard Features:**
            1. Daily detection counts with moving averages
            2. Detection distribution by hour of day
            3. Detection distribution by day of week
            4. Week-over-week comparison
            5. Temporal insights (business hours vs. non-business hours)
            6. Executive summary with key findings
            
            Sample data is pre-loaded for demonstration.
            """)
        
        # Data Input Section
        st.header("📝 Data Input")
        
        sample_data = """UniqueNo\tHostname\tDetect MALAYSIA TIME FORMULA
3\tAli\t28/2/2025 15:03
11\tCline\t25/2/2025 13:41
25\tKat\t13/2/2025 2:06
40\tChrist\t12/2/2025 3:01
41\tMeiLing\t12/2/2025 3:01
43\tMohd\t12/2/2025 1:29
45\tPaul\t11/2/2025 18:11
58\tZedd\t7/2/2025 17:15
62\tAhmad\t6/2/2025 14:25
75\tSari\t5/2/2025 10:30
83\tLee\t4/2/2025 16:45
91\tTan\t3/2/2025 9:15
105\tWong\t2/2/2025 11:20
118\tLim\t1/2/2025 13:35"""
        
        detection_data_input = st.text_area(
            "Detection Data",
            value=sample_data,
            height=300,
            help="Enter detection data in the format shown"
        )
        
        # Generate button
        generate_dashboard = st.button("🚀 Generate Dashboard", type="primary")
        
        # Executive Summary Editor (will be populated after data processing)
        st.header("📋 Executive Summary")
        if 'executive_summary' not in st.session_state:
            st.session_state.executive_summary = ""
        
        edited_summary_raw = st.text_area(
            "Edit Executive Summary", 
            value=st.session_state.executive_summary,
            height=200,
            help="Edit the executive summary here. It will be displayed at the bottom of the dashboard."
        )
        
        # Update session state
        st.session_state.executive_summary = edited_summary_raw
    
    # ========== MAIN DASHBOARD AREA ==========
    
    # Title with report period
    st.markdown(f"<h1 class='dashboard-title'>Time-Based Security Analysis Dashboard - {report_period}</h1>", unsafe_allow_html=True)
    
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
            
            # Parse detection time
            try:
                detection_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    detection_data['Detect MALAYSIA TIME FORMULA'], 
                    format='%d/%m/%Y %H:%M',
                    errors='coerce'
                )
            except Exception:
                detection_data['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                    detection_data['Detect MALAYSIA TIME FORMULA'], 
                    errors='coerce'
                )
            
            # Extract date and time components for analysis
            detection_data['Date'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.date
            detection_data['Hour'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.hour
            detection_data['Day_of_Week'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.dayofweek
            detection_data['Day_Name'] = detection_data['Detect MALAYSIA TIME FORMULA'].dt.day_name()
            
            st.success("✅ Data processed successfully!")
            
            # Basic statistics for dashboard
            total_detections = len(detection_data)
            unique_hosts = detection_data['Hostname'].nunique()
            
            # Handle empty data gracefully
            if total_detections > 0:
                peak_hour = detection_data.groupby('Hour').size().idxmax()
            else:
                peak_hour = 0
            
            # Determine date range for the report
            if total_detections > 0:
                min_date = detection_data['Detect MALAYSIA TIME FORMULA'].min().date()
                max_date = detection_data['Detect MALAYSIA TIME FORMULA'].max().date()
                date_range = (max_date - min_date).days + 1
            else:
                min_date = datetime.now().date()
                max_date = datetime.now().date()
                date_range = 1
            
            # Create a date range for all days in the period
            all_dates = pd.date_range(start=min_date, end=max_date)
            all_dates_df = pd.DataFrame({'Date': all_dates.date})
            
            # Daily detection counts
            daily_counts = detection_data.groupby('Date').size().reset_index(name='Count')
            
            # Merge with all dates to include days with zero detections
            daily_counts = pd.merge(all_dates_df, daily_counts, on='Date', how='left').fillna(0)
            daily_counts['Count'] = daily_counts['Count'].astype(int)
            
            # Calculate 7-day moving average
            daily_counts['Moving_Avg'] = daily_counts['Count'].rolling(window=7, min_periods=1).mean()
            
            # Hour of day analysis
            hourly_counts = detection_data.groupby('Hour').size().reset_index(name='Count')
            hourly_counts = hourly_counts.sort_values('Hour')
            
            # Complete the hours (0-23)
            all_hours = pd.DataFrame({'Hour': range(0, 24)})
            hourly_counts = pd.merge(all_hours, hourly_counts, on='Hour', how='left').fillna(0)
            hourly_counts['Count'] = hourly_counts['Count'].astype(int)
            
            # Day of week analysis
            day_counts = detection_data.groupby(['Day_of_Week', 'Day_Name']).size().reset_index(name='Count')
            day_counts = day_counts.sort_values('Day_of_Week')
            
            # Complete all days of week
            all_days = pd.DataFrame({
                'Day_of_Week': range(0, 7),
                'Day_Name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            })
            day_counts = pd.merge(all_days, day_counts, on=['Day_of_Week', 'Day_Name'], how='left').fillna(0)
            day_counts['Count'] = day_counts['Count'].astype(int)
            
            # Add percentage to day counts
            total_day_count = day_counts['Count'].sum()
            if total_day_count > 0:
                day_counts['Percentage'] = (day_counts['Count'] / total_day_count * 100).round(1)
            else:
                day_counts['Percentage'] = 0.0
            
            # Weekly analysis using the preprocessing function
            weekly_counts = preprocess_weekly_data(detection_data)
            
            # Business hours vs. non-business hours
            business_hours_data = detection_data[detection_data['Hour'].between(9, 16)]  # 9am-5pm (9-16 inclusive)
            business_hours_count = len(business_hours_data)
            business_hours_pct = round(business_hours_count / total_detections * 100, 1) if total_detections > 0 else 0.0
            
            # Weekday vs. weekend
            weekday_data = detection_data[detection_data['Day_of_Week'] < 5]  # Monday-Friday
            weekday_count = len(weekday_data)
            weekday_pct = round(weekday_count / total_detections * 100, 1) if total_detections > 0 else 0.0
            
            # Display dashboard
            st.markdown("<h2 class='section-header'>📊 Temporal Detection Patterns</h2>", unsafe_allow_html=True)
            
            # Metrics display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Detections", f"{total_detections:,}")
            
            with col2:
                st.metric("Unique Hosts", f"{unique_hosts:,}")
                
            with col3:
                st.metric("Peak Detection Hour", f"{peak_hour}:00")
            
            # 1. Daily Detection Trend visualization
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Daily Detection Trend</h4>
                    <p><strong>Definition:</strong> Shows the number of security detections per day over time with a 7-day moving average.</p>
                    <p><strong>Use Case:</strong> Identify trends and anomalies in detection volume, which may correlate with security events or changes in the environment.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h3>📈 Daily Detection Trend - {report_period}</h3>", unsafe_allow_html=True)
            
            if not daily_counts.empty:
                # Create a plotly figure for daily trend
                daily_trend_fig = go.Figure()
                
                # Add the daily detection counts
                daily_trend_fig.add_trace(go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts['Count'],
                    mode='lines+markers',
                    name='Daily Detections',
                    line=dict(color=daily_trend_color, width=2),
                    marker=dict(size=8)
                ))
                
                # Add the 7-day moving average
                daily_trend_fig.add_trace(go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts['Moving_Avg'],
                    mode='lines',
                    name='7-Day Moving Avg',
                    line=dict(color=moving_avg_color, width=2, dash='dash')
                ))
                
                # Update layout
                daily_trend_fig.update_layout(
                    title='Daily Detection Trend',
                    xaxis_title='Day of Month',
                    yaxis_title='Number of Detections',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    height=400,
                    margin=dict(l=40, r=40, t=40, b=40),
                    hovermode='x unified'
                )
                
                # Show grid if requested
                if show_grid:
                    daily_trend_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    daily_trend_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                
                # Display the plot
                st.plotly_chart(daily_trend_fig, use_container_width=True)
                
                # Key insight
                max_day_idx = daily_counts['Count'].idxmax()
                max_day_count = daily_counts['Count'].max()
                max_day_date = daily_counts.iloc[max_day_idx]['Date'].strftime('%d/%m/%Y')
                st.info(f"💡 **Key Insight:** The highest detection day was {max_day_date} with {max_day_count} detections.")
            else:
                st.info("No daily trend data available to display.")
            
            # 2. Hour of Day visualization
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Distribution by Hour of Day</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detections across the 24 hours of the day.</p>
                    <p><strong>Use Case:</strong> Identify the hours with highest security activity, which helps in optimizing security monitoring schedules.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>🕐 Detection Distribution by Hour of Day</h3>", unsafe_allow_html=True)
            
            if not hourly_counts.empty:
                # Create color coding for business hours vs. non-business hours
                hour_colors = []
                for hour in hourly_counts['Hour']:
                    if 9 <= hour < 17:  # Business hours
                        hour_colors.append('#3498db')  # Blue for business hours
                    else:
                        hour_colors.append('#2ecc71')  # Green for non-business hours
                
                # Create a plotly figure for hourly distribution
                hourly_fig = go.Figure()
                
                hourly_fig.add_trace(go.Bar(
                    x=hourly_counts['Hour'],
                    y=hourly_counts['Count'],
                    marker_color=hour_colors,
                    text=hourly_counts['Count'] if show_values else None,
                    textposition='outside'
                ))
                
                # Update layout
                hourly_fig.update_layout(
                    title='Detection Distribution by Hour of Day',
                    xaxis_title='Hour of Day (24-Hour Format)',
                    yaxis_title='Number of Detections',
                    height=500,
                    margin=dict(l=40, r=40, t=40, b=40),
                    xaxis=dict(tickmode='array', tickvals=list(range(0, 24)))
                )
                
                # Show grid if requested
                if show_grid:
                    hourly_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    hourly_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                
                # Display the plot
                st.plotly_chart(hourly_fig, use_container_width=True)
                
                # Key insight
                st.info(f"💡 **Key Insight:** Peak detection hour is {peak_hour}:00. {business_hours_pct}% of detections occur during business hours (9:00-17:00).")
            else:
                st.info("No hourly distribution data available to display.")
            
            # 3. Day of Week visualization
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Detection Distribution by Day of Week</h4>
                    <p><strong>Definition:</strong> Shows the distribution of detections across the days of the week.</p>
                    <p><strong>Use Case:</strong> Identify patterns in security activity across different days, which may indicate specific vulnerabilities or attack patterns.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>📅 Detection Distribution by Day of Week</h3>", unsafe_allow_html=True)
            
            if not day_counts.empty and day_counts['Count'].sum() > 0:
                # Create color coding for weekdays vs. weekends
                day_colors = []
                for day in day_counts['Day_of_Week']:
                    if day < 5:  # Weekdays (Monday-Friday)
                        day_colors.append(weekday_color)  # Purple for weekdays
                    else:
                        day_colors.append(weekend_color)  # Red for weekends
                
                # Create a plotly figure for day of week distribution
                day_fig = go.Figure()
                
                # Create text labels with percentages if requested
                if show_percentages and show_values:
                    text_labels = [f"{count} ({pct}%)" for count, pct in zip(day_counts['Count'], day_counts['Percentage'])]
                elif show_percentages:
                    text_labels = [f"({pct}%)" for pct in day_counts['Percentage']]
                elif show_values:
                    text_labels = day_counts['Count']
                else:
                    text_labels = None
                
                day_fig.add_trace(go.Bar(
                    x=day_counts['Day_Name'],
                    y=day_counts['Count'],
                    marker_color=day_colors,
                    text=text_labels,
                    textposition='outside'
                ))
                
                # Update layout
                day_fig.update_layout(
                    title='Detection Distribution by Day of Week',
                    xaxis_title='Day of Week',
                    yaxis_title='Number of Detections',
                    height=500,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                
                # Show grid if requested
                if show_grid:
                    day_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    day_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                
                # Display the plot
                st.plotly_chart(day_fig, use_container_width=True)
                
                # Key insight
                peak_day_name = day_counts.iloc[day_counts['Count'].idxmax()]['Day_Name']
                peak_day_count = day_counts['Count'].max()
                st.info(f"💡 **Key Insight:** {peak_day_name} has the highest detection count ({peak_day_count} detections). {weekday_pct}% of detections occur on weekdays.")
            else:
                st.info("No day of week distribution data available to display.")
            
            # 4. Week-over-Week Comparison
            if show_definitions:
                st.markdown("""
                <div class="definition-card">
                    <h4>Week-over-Week Detection Comparison</h4>
                    <p><strong>Definition:</strong> Shows detection counts for each week and the percentage change compared to the previous week.</p>
                    <p><strong>Use Case:</strong> Track how security incidents evolve over time and identify significant changes that may require investigation.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<h3>📊 Week-over-Week Detection Comparison</h3>", unsafe_allow_html=True)
            
            if not weekly_counts.empty and weekly_counts['Count'].sum() > 0:
                # Create a plotly figure for week-over-week comparison
                wow_fig = go.Figure()
                
                # Create the bar chart
                wow_fig.add_trace(go.Bar(
                    x=[f'Week {int(week)}' for week in weekly_counts['Week_Num']],
                    y=weekly_counts['Count'],
                    marker_color=weekly_comp_color,
                    text=weekly_counts['Count'] if show_values else None,
                    textposition='outside'
                ))
                
                # Add week-over-week change annotations if requested
                if show_annotations:
                    for i, row in weekly_counts.iterrows():
                        if i > 0 and row['WoW_Change'] != 0:  # Skip first week and zero changes
                            wow_fig.add_annotation(
                                x=i,
                                y=row['Count'] + max(5, row['Count'] * 0.08),  # Position above the bar
                                text=f"{'+' if row['WoW_Change'] > 0 else ''}{row['WoW_Change']:.1f}%",
                                showarrow=False,
                                font=dict(
                                    size=12,
                                    color='green' if row['WoW_Change'] > 0 else 'red'
                                )
                            )
                
                # Update layout
                wow_fig.update_layout(
                    title='Week-over-Week Detection Comparison',
                    xaxis_title='Week',
                    yaxis_title='Number of Detections',
                    height=500,
                    margin=dict(l=40, r=40, t=40, b=60)
                )
                
                # Show grid if requested
                if show_grid:
                    wow_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    wow_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                
                # Display the plot
                st.plotly_chart(wow_fig, use_container_width=True)
                
                # Key insight
                latest_week = weekly_counts.iloc[-1]
                latest_week_change = latest_week['WoW_Change']
                change_direction = 'increase' if latest_week_change >= 0 else 'decrease'
                st.info(f"💡 **Key Insight:** The most recent week showed a {latest_week_change:.1f}% {change_direction} compared to the previous week.")
                
                # Add a table with details
                st.markdown("<h4>📋 Week-over-Week Changes</h4>", unsafe_allow_html=True)
                
                # Format the table data
                wow_table = weekly_counts.copy()
                wow_table['Week'] = [f'Week {int(w)}' for w in wow_table['Week_Num']]
                wow_table['WoW_Change'] = wow_table['WoW_Change'].apply(
                    lambda x: f"{'+' if x > 0 else ''}{x:.1f}%" if x != 0 else "0.0%"
                )
                
                # Display the table
                st.dataframe(wow_table[['Week', 'Count', 'WoW_Change']], use_container_width=True)
            else:
                st.info("No weekly trend data available to display.")
            
            # 5. Temporal Insights section
            st.markdown("<h2 class='section-header'>🔍 Temporal Insights</h2>", unsafe_allow_html=True)
            
            # Create two columns for business hours and weekday insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>Business Hours vs. Non-Business Hours</h4>
                    <p>{business_hours_pct}% of detections occur during business hours (9:00-17:00).</p>
                    <p>Peak detection hour is {peak_hour}:00.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>Weekday vs. Weekend</h4>
                    <p>{weekday_pct}% of detections occur on weekdays.</p>
                    <p>{day_counts.iloc[0]['Day_Name']} has the highest detection count ({day_counts.iloc[0]['Count']} detections).</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Recent trend insights
            recent_trend_text = ""
            if len(weekly_counts) > 1:
                latest_week = weekly_counts.iloc[-1]
                latest_week_num = int(latest_week['Week_Num'])
                latest_week_change = latest_week['WoW_Change']
                change_direction = 'increase' if latest_week_change >= 0 else 'decrease'
                recent_trend_text = f"Week {latest_week_num} showed a {latest_week_change:.1f}% {change_direction} compared to the previous week."
            
            highest_detection_text = ""
            if not daily_counts.empty and daily_counts['Count'].max() > 0:
                highest_day_idx = daily_counts['Count'].idxmax()
                highest_day_date = daily_counts.iloc[highest_day_idx]['Date'].strftime('%d/%m/%Y')
                highest_day_count = daily_counts['Count'].max()
                highest_detection_text = f"The highest detection day was {highest_day_date} with {highest_day_count} detections."
            
            st.markdown(f"""
            <div class="insight-card">
                <h4>Recent Trend Observations</h4>
                <p>{recent_trend_text}</p>
                <p>{highest_detection_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate and update executive summary
            if not detection_data.empty and total_detections > 0:
                # Get the week with highest detections
                peak_week_num = int(weekly_counts.iloc[weekly_counts['Count'].idxmax()]['Week_Num']) if not weekly_counts.empty else 1
                peak_week_count = weekly_counts['Count'].max() if not weekly_counts.empty else 0
                
                # Get highest day of week
                peak_day_name = day_counts.iloc[day_counts['Count'].idxmax()]['Day_Name'] if not day_counts.empty and day_counts['Count'].max() > 0 else "Monday"
                peak_day_count = day_counts['Count'].max() if not day_counts.empty else 0
                
                # Get latest week's change
                latest_week_change = weekly_counts.iloc[-1]['WoW_Change'] if len(weekly_counts) > 1 else 0.0
                
                # Create summary
                default_summary = f"""• Time-based analysis of {total_detections} detections during {report_period} reveals several important patterns.
• Detection volume shows Week {peak_week_num} experiencing the highest activity ({peak_week_count} detections).
• {business_hours_pct}% of detections occur during business hours (9:00-17:00), with peak activity at {peak_hour}:00.
• {weekday_pct}% of detections occur on weekdays, with {peak_day_name} showing the highest frequency ({peak_day_count} detections).
• The most recent week showed a {latest_week_change:.1f}% {'increase' if latest_week_change >= 0 else 'decrease'} in detection volume compared to the previous week.
• These patterns suggest that security monitoring should be enhanced during {peak_day_name}s around {peak_hour}:00, and that security operations should be appropriately staffed during business hours when most incidents occur."""
                
                # Update session state if it's empty
                if not st.session_state.executive_summary.strip():
                    st.session_state.executive_summary = default_summary
            
            # Executive summary display
            st.markdown("<h2 class='section-header'>📋 Executive Summary</h2>", unsafe_allow_html=True)
            
            if st.session_state.executive_summary.strip():
                # Convert bullet points to HTML list
                summary_lines = st.session_state.executive_summary.strip().split('\n')
                summary_html = "<ul class='summary-bullet'>"
                for line in summary_lines:
                    if line.strip():
                        clean_line = line.strip().lstrip('• ')
                        summary_html += f"<li>{clean_line}</li>"
                summary_html += "</ul>"
                
                # Display the summary
                st.markdown(f"<div class='executive-summary-card'>{summary_html}</div>", unsafe_allow_html=True)
            else:
                st.info("📝 Use the sidebar to edit the executive summary after generating the dashboard.")
                
        except Exception as e:
            st.error(f"❌ Error processing data: {e}")
            st.error("Please check your data format and try again.")
    else:
        # Initial state - no dashboard generated yet
        st.info("👈 Configure your settings and input data in the sidebar, then click 'Generate Dashboard' to begin.")
        st.markdown("""
        ### Welcome to the Time-Based Security Analysis Dashboard
        
        This dashboard provides comprehensive time-based analysis of security detections including:
        
        - 📈 Daily detection trends with moving averages
        - 🕐 Hourly distribution patterns
        - 📅 Day-of-week analysis
        - 📊 Week-over-week comparisons
        - 🔍 Business hours vs. non-business hours insights
        - 📋 Executive summary with key findings
        
        **Getting Started:**
        1. Use the sidebar to configure your report period and display preferences
        2. Input your detection data in the specified format
        3. Click 'Generate Dashboard' to create your time-based analysis
        4. Customize the executive summary as needed
        
        Sample data is pre-loaded for demonstration purposes.
        """)

if __name__ == "__main__":
    time_based_analysis_dashboard()