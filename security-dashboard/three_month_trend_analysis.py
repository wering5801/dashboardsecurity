import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
import matplotlib.pyplot as plt

def convert_to_json_serializable(obj):
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    return obj

# Default color palettes
MAIN_COLOR = '#3498db'
SECONDARY_COLOR = '#2ecc71'
BAR_COLOR = '#f39c12'
CHART_COLORS = {
    'primary': '#2E8B57',    # SeaGreen
    'secondary': '#4682B4',  # SteelBlue
    'accent': '#FFD700',     # Gold
    'success': '#32CD32',    # LimeGreen
    'warning': '#FF6347',    # Tomato
    'info': '#17a2b8',       # LightSeaBlue
    'danger': '#dc3545'      # Red
}

# Default ECharts theme options
def get_theme_options():
    return {
        "grid": {
            "left": "10%",
            "right": "10%",
            "bottom": "15%",
            "containLabel": True
        },
        "toolbox": {
            "feature": {
                "saveAsImage": {},
                "dataZoom": {},
                "restore": {}
            }
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "dataZoom": [
            {"type": "inside"},
            {"type": "slider"}
        ]
    }

# Helper function to create base ECharts options with consistent styling
def create_base_chart_options(title=None, x_label=None, y_label=None):
    options = get_theme_options()
    if title:
        options["title"] = {"text": title}
    if x_label:
        options["xAxis"] = {"name": x_label}
    if y_label:
        options["yAxis"] = {"name": y_label}
    return options

def three_month_trend_analysis_dashboard():
    st.title("📈 Three-Month Trend Analysis Dashboard")
    st.markdown("""
    This dashboard visualizes trends across up to 3 months of Falcon data exactly matching the PDF specifications.
    """)

    # Sidebar controls matching PDF styling
    with st.sidebar:
        st.title("🔧 Dashboard Settings")
        st.header("📊 Analysis Type")
        analysis_type = st.selectbox("Select Analysis",
                                   ["Host Security Analysis", "Detection and Severity Analysis", "Time-Based Analysis"])

        st.header("📅 Period Configuration")
        period_filter = st.multiselect("Filter by Period (Month)", options=[], help="Select one or more periods to include in the analysis.")

        st.header("📊 Display Options")
        top_n = st.radio("Display Top:", [3, 5, 10], index=1, horizontal=False)

        st.header("🎨 Color Customization")
        with st.expander("Chart Colors", expanded=False):
            primary_color = st.color_picker("Primary Color", "#2E8B57")  # SeaGreen
            secondary_color = st.color_picker("Secondary Color", "#4682B4")  # SteelBlue
            accent_color = st.color_picker("Accent Color", "#FFD700")  # Gold
            background_color = st.color_picker("Background Color", "#F0F8FF")  # AliceBlue

        st.header("📋 Export Options")
        export_pdf = st.button("📄 Export to PDF", type="primary")

    # Apply custom CSS for PDF-like styling
    st.markdown("""
    <style>
    .pdf-section {
        background-color: #f8f9fa;
        padding: 20px;
        margin: 10px 0;
        border-radius: 5px;
        border-left: 4px solid #2E8B57;
    }
    .section-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    .chart-container {
        background-color: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Check if aggregated data is available
    if 'three_month_trend_data' not in st.session_state:
        st.warning("No aggregated multi-month data found. Please use the Falcon Generator to upload and process at least two months of data.")
        return

    agg = st.session_state['three_month_trend_data']

    # Select which template to analyze
    template = st.selectbox(
        "Select template for trend analysis:",
        ["Detection Analysis", "Host Analysis", "Time Analysis"]
    )

    df = agg['detection_analysis'] if template == "Detection Analysis" else (
        agg['host_analysis'] if template == "Host Analysis" else agg['time_analysis']
    )

    # Map each unique period to Month 1, Month 2, ... based on order of appearance
    if 'Period' in df.columns:
        unique_periods = list(df['Period'].dropna().unique())
        period_map = {p: f"Month {i+1}" for i, p in enumerate(unique_periods)}
        df['Month_Index'] = df['Period'].map(period_map)
        all_months = df['Month_Index'].unique().tolist()
        month_filter_default = all_months if not period_filter else [period_map[p] for p in period_filter if p in period_map]
        month_filter = st.sidebar.multiselect("Filter by File (Month)", options=all_months, default=month_filter_default, key="month_filter")
        if month_filter:
            df = df[df['Month_Index'].isin(month_filter)]

    if df.empty:
        st.error("No data available for the selected template and filters.")
        return

    # Show preview
    st.dataframe(df, use_container_width=True)

    # Store figures for PDF export
    figures = []

    # ========== HOST SECURITY ANALYSIS (A.1-A.4) ==========
    if template == "Host Analysis" and analysis_type == "Host Security Analysis":
        st.markdown('<div class="pdf-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">A. Host Security Analysis</h2>', unsafe_allow_html=True)

        # A.1 Overview Detection (3 Months Trend)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### A.1 Overview Detection (3 Months Trend)")

        if 'Period' in df.columns and 'Hostname' in df.columns:
            # Calculate metrics for each period
            overview_data = []
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                total_detections = len(period_df)
                total_hosts = period_df['Hostname'].nunique()
                unique_users = period_df['UserName'].nunique() if 'UserName' in period_df.columns else 0
                windows_hosts = period_df[period_df['OS Version'].str.contains('Windows', na=False)].shape[0] if 'OS Version' in period_df.columns else 0
                avg_detections_per_host = total_detections / total_hosts if total_hosts > 0 else 0

                overview_data.append({
                    'Period': period,
                    'Total_Detections': total_detections,
                    'Total_Hosts': total_hosts,
                    'Unique_Users': unique_users,
                    'Windows_Hosts': windows_hosts,
                    'Avg_Detections_per_Host': round(avg_detections_per_host, 2)
                })

            overview_df = pd.DataFrame(overview_data)

            # Create stacked bar chart exactly like PDF
            periods = overview_df['Period'].tolist()
            total_detections = overview_df['Total_Detections'].tolist()
            total_hosts = overview_df['Total_Hosts'].tolist()
            unique_users = overview_df['Unique_Users'].tolist()
            windows_hosts = overview_df['Windows_Hosts'].tolist()
            avg_detections = overview_df['Avg_Detections_per_Host'].tolist()

            options = {
                **get_theme_options(),
                "title": {"text": "Host Overview Detection Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {
                    "data": ["Total Detections", "Total Hosts", "Unique Users", "Windows Hosts", "Avg. Detections per Host"],
                    "top": "bottom"
                },
                "xAxis": {
                    "type": "category",
                    "data": periods,
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Count"
                },
                "series": [
                    {
                        "name": "Total Detections",
                        "type": "bar",
                        "data": total_detections,
                        "itemStyle": {"color": "#32CD32"},
                        "label": {"show": True, "position": "top"}
                    },
                    {
                        "name": "Total Hosts",
                        "type": "bar",
                        "data": total_hosts,
                        "itemStyle": {"color": "#4682B4"},
                        "label": {"show": True, "position": "top"}
                    },
                    {
                        "name": "Unique Users",
                        "type": "bar",
                        "data": unique_users,
                        "itemStyle": {"color": "#FFD700"},
                        "label": {"show": True, "position": "top"}
                    },
                    {
                        "name": "Windows Hosts",
                        "type": "bar",
                        "data": windows_hosts,
                        "itemStyle": {"color": "#FF6347"},
                        "label": {"show": True, "position": "top"}
                    },
                    {
                        "name": "Avg. Detections per Host",
                        "type": "line",
                        "yAxisIndex": 1,
                        "data": avg_detections,
                        "itemStyle": {"color": "#9370DB"},
                        "label": {"show": True, "position": "top", "formatter": "{c}"}
                    }
                ]
            }
            st_echarts(options=options, height="500px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # A.2 Top Hosts with most detections
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### A.2 Top Hosts with most detections (3 Months Trend)")

        if 'Hostname' in df.columns and 'Period' in df.columns:
            # Create horizontal bar chart for each period
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                host_counts = period_df.groupby('Hostname').size().reset_index(name='Count').sort_values('Count', ascending=False).head(5)

                options = {
                    **get_theme_options(),
                    "title": {"text": f"Top Hosts with Most Detections Across Three Months Trends - Top 5"},
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "xAxis": {"type": "value", "name": "Number of Detections"},
                    "yAxis": {
                        "type": "category",
                        "data": host_counts['Hostname'].tolist()[::-1],
                        "axisLabel": {"width": 150, "overflow": "break"}
                    },
                    "series": [{
                        "name": "Detections",
                        "type": "bar",
                        "data": host_counts['Count'].tolist()[::-1],
                        "itemStyle": {"color": "#32CD32"},
                        "label": {"show": True, "position": "right"}
                    }]
                }
                st_echarts(options=options, height="400px")
                figures.append(options)

                # Show data table
                st.dataframe(host_counts.iloc[::-1].reset_index(drop=True), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # A.3 Top 5 Users with Most Detections
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### A.3 Top 5 Users with Most Detections (3 Months Trend)")

        if 'UserName' in df.columns and 'Period' in df.columns:
            # Create horizontal bar chart for each period
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                filtered_df = period_df[period_df['UserName'].str.strip() != '']
                user_counts = filtered_df.groupby('UserName').size().reset_index(name='Count').sort_values('Count', ascending=False).head(5)

                options = {
                    **get_theme_options(),
                    "title": {"text": f"Users with Most Detections Across Three Months Trends - Top 5"},
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "xAxis": {"type": "value", "name": "Number of Detections"},
                    "yAxis": {
                        "type": "category",
                        "data": user_counts['UserName'].tolist()[::-1],
                        "axisLabel": {"width": 150, "overflow": "break"}
                    },
                    "series": [{
                        "name": "Detections",
                        "type": "bar",
                        "data": user_counts['Count'].tolist()[::-1],
                        "itemStyle": {"color": "#4682B4"},
                        "label": {"show": True, "position": "right"}
                    }]
                }
                st_echarts(options=options, height="400px")
                figures.append(options)

                # Show data table
                st.dataframe(user_counts.iloc[::-1].reset_index(drop=True), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # A.4 Total Hosts with Sensor Versions Status
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### A.4 Total Hosts with Sensor Versions Status")

        if 'Sensor Version' in df.columns:
            sensor_counts = df.groupby('Sensor Version').size().reset_index(name='Count').sort_values('Count', ascending=False)

            # Create data for Latest vs Outdated
            latest_count = sensor_counts[sensor_counts['Sensor Version'].str.contains('Latest', case=False, na=False)]['Count'].sum() if not sensor_counts.empty else 0
            outdated_count = sensor_counts[~sensor_counts['Sensor Version'].str.contains('Latest', case=False, na=False)]['Count'].sum() if not sensor_counts.empty else 0

            options = {
                **get_theme_options(),
                "title": {"text": "Detections Hosts with Sensor Versions Status Across Three Months"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {
                    "type": "category",
                    "data": ["Latest", "Outdated"],
                    "name": "Sensor Status"
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Hosts"
                },
                "series": [{
                    "name": "Hosts",
                    "type": "bar",
                    "data": [int(latest_count), int(outdated_count)],  # Convert to native Python int
                    "itemStyle": {"color": "#32CD32"},
                    "label": {"show": True, "position": "top"}
                }]
            }
            st_echarts(options=convert_to_json_serializable(options), height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ========== DETECTION AND SEVERITY ANALYSIS (B.1-B.6) ==========
    elif template == "Detection Analysis" and analysis_type == "Detection and Severity Analysis":
        st.markdown('<div class="pdf-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">B. Detection and Severity Analysis</h2>', unsafe_allow_html=True)

        # B.1 Critical and High Detection Overview
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.1 Critical and High Detection Overview (3 Months Trend)")

        if 'SeverityName' in df.columns and 'Period' in df.columns:
            # Calculate critical and high detections for each period
            critical_high_data = []
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                critical_count = (period_df['SeverityName'] == 'Critical').sum()
                high_count = (period_df['SeverityName'] == 'High').sum()
                critical_high_data.append({
                    'Period': period,
                    'Critical': critical_count,
                    'High': high_count
                })

            ch_df = pd.DataFrame(critical_high_data)

            # Create metric cards exactly like PDF
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background-color: #2E8B57; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; font-size: 2rem;">{ch_df['Critical'].sum()}</h3>
                    <p style="margin: 5px 0 0 0;">Critical Detections</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: #2E8B57; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; font-size: 2rem;">{ch_df['High'].sum()}</h3>
                    <p style="margin: 5px 0 0 0;">High Detections</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="background-color: #2E8B57; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; font-size: 2rem;">{ch_df['Critical'].sum() + ch_df['High'].sum()}</h3>
                    <p style="margin: 5px 0 0 0;">Total Critical & High</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # B.2 Detection Count by Severity
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.2 Detection Count by Severity (3 Months Trend)")

        if 'SeverityName' in df.columns and 'Period' in df.columns:
            severity_trend = df.groupby(['Period', 'SeverityName']).size().unstack(fill_value=0)

            # Convert numeric values to native Python types
            severity_data = {col: [int(x) for x in severity_trend[col]] for col in severity_trend.columns}
            
            options = {
                **get_theme_options(),
                "title": {"text": "Detection Count by Severity Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": [str(col) for col in severity_trend.columns]},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in severity_trend.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [
                    {
                        "name": str(severity),
                        "type": "bar",
                        "data": severity_data[severity],
                        "itemStyle": {"color": "#FF6347" if severity == "High" else "#32CD32" if severity == "Medium" else "#4682B4"},
                        "label": {"show": True, "position": "top"}
                    } for severity in severity_trend.columns
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # B.3 Detection count across Country
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.3 Detection count across Country")

        if 'Country' in df.columns and 'Period' in df.columns:
            country_trend = df.groupby(['Period', 'Country']).size().unstack(fill_value=0)

            options = {
                **get_theme_options(),
                "title": {"text": "Detection Count by Country Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": country_trend.columns.tolist()},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in country_trend.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [
                    {
                        "name": country,
                        "type": "bar",
                        "data": [int(x) for x in country_trend[country]],
                        "itemStyle": {"color": "#32CD32"},
                        "label": {"show": True, "position": "top"}
                    } for country in country_trend.columns
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # B.4 Files with Most Detections
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.4 Files with Most Detections Across Three Months Trends - Top 5")

        if 'FileName' in df.columns:
            file_counts = df['FileName'].value_counts().head(5).reset_index()
            file_counts.columns = ['FileName', 'Count']

            options = {
                **get_theme_options(),
                "title": {"text": "File Name with Most Detections Across Three Months Trends - Top 5"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {"type": "value", "name": "Number of Detections"},
                "yAxis": {
                    "type": "category",
                    "data": file_counts['FileName'].tolist()[::-1],
                    "axisLabel": {"width": 200, "overflow": "break"}
                },
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": file_counts['Count'].tolist()[::-1],
                    "itemStyle": {"color": "#32CD32"},
                    "label": {"show": True, "position": "right"}
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # B.5 Tactics by Severity
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.5 Tactics by Severity Across Three Months Trends")

        if 'Tactic' in df.columns and 'SeverityName' in df.columns and 'Period' in df.columns:
            # First get the severity trend for each tactic and period
            tactic_severity_trend = df.groupby(['Period', 'Tactic']).size().reset_index(name='Count')
            
            # Get top tactics
            top_tactics = df.groupby('Tactic').size().nlargest(5).index.tolist()
            
            # Filter the trend data to only include top tactics
            tactic_severity_trend = tactic_severity_trend[tactic_severity_trend['Tactic'].isin(top_tactics)]
            
            # Pivot the data for easier plotting
            pivot_data = tactic_severity_trend.pivot(index='Period', columns='Tactic', values='Count').fillna(0)

            options = {
                **get_theme_options(),
                "title": {"text": "Tactics by Severity Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": top_tactics},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in pivot_data.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [
                    {
                        "name": tactic,
                        "type": "bar",
                        "data": [int(x) for x in pivot_data[tactic].values],
                        "itemStyle": {"color": "#32CD32"},
                        "label": {"show": True, "position": "top"}
                    } for tactic in pivot_data.columns
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # B.6 Technique by Severity
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### B.6 Technique by Severity Across Three Months Trends")

        if 'Technique' in df.columns and 'SeverityName' in df.columns and 'Period' in df.columns:
            technique_severity_trend = df.groupby(['Period', 'Technique', 'SeverityName']).size().unstack(fill_value=0)

            # Get top techniques
            top_techniques = df.groupby('Technique').size().nlargest(5).index.tolist()

            options = {
                **get_theme_options(),
                "title": {"text": "Technique by Severity Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": top_techniques},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in technique_severity_trend.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [
                    {
                        "name": technique,
                        "type": "bar",
                        "data": [int(x) for x in technique_severity_trend[technique]],
                        "itemStyle": {"color": "#4682B4"},
                        "label": {"show": True, "position": "top"}
                    } for technique in top_techniques
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ========== TIME-BASED ANALYSIS (C.1-C.3) ==========
    elif template == "Time Analysis" and analysis_type == "Time-Based Analysis":
        st.markdown('<div class="pdf-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">C. Time-Based Analysis</h2>', unsafe_allow_html=True)

        # C.1 Daily Detection Trend
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### C.1 Daily Detection Trend (3 Months Trend)")

        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
            daily_counts = df.groupby(df['Detect MALAYSIA TIME FORMULA'].dt.date).size().reset_index(name='Count')
            daily_counts = daily_counts.sort_values('Detect MALAYSIA TIME FORMULA')

            options = {
                **get_theme_options(),
                "title": {"text": "Detection Over Multiple Days Across Three Months Trends - Top 3"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
                "xAxis": {
                    "type": "category",
                    "data": [d.strftime('%d/%m/%Y') for d in daily_counts['Detect MALAYSIA TIME FORMULA']],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": daily_counts['Count'].tolist(),
                    "itemStyle": {"color": "#32CD32"},
                    "label": {"show": True, "position": "top"}
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # C.2 Hourly Distribution
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### C.2 Hourly Distribution of Detections (3 Months Trend)")

        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
            df['Hour'] = df['Detect MALAYSIA TIME FORMULA'].dt.hour
            hourly_counts = df.groupby('Hour').size().reset_index(name='Count')

            options = {
                **get_theme_options(),
                "title": {"text": "Hourly Distribution of Detections Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
                "xAxis": {
                    "type": "category",
                    "data": [f"{h}:00" for h in range(24)],
                    "name": "Hour of Day"
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [{
                    "name": "Detections",
                    "type": "line",
                    "data": [int(hourly_counts[hourly_counts['Hour'] == h]['Count'].sum()) for h in range(24)],
                    "itemStyle": {"color": "#4682B4"},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "label": {"show": True, "position": "top"}
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)

        # C.3 Day of Week Frequency
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### C.3 Day of Weeks Frequency Detections (3 Months Trend)")

        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
            df['Day_of_Week'] = df['Detect MALAYSIA TIME FORMULA'].dt.day_name()
            weekly_counts = df.groupby('Day_of_Week').size().reset_index(name='Count')

            # Order days of week
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_counts['Day_of_Week'] = pd.Categorical(weekly_counts['Day_of_Week'], categories=days_order, ordered=True)
            weekly_counts = weekly_counts.sort_values('Day_of_Week')

            options = {
                **get_theme_options(),
                "title": {"text": "Detection Frequency by Day of Week Across Three Months Trends"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {
                    "type": "category",
                    "data": days_order,
                    "name": "Day of Week"
                },
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": weekly_counts['Count'].tolist(),
                    "itemStyle": {"color": "#4682B4"},
                    "label": {"show": True, "position": "top"}
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ========== PDF Export ==========
    if export_pdf and figures:
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
                pdf_path = tmpfile.name
                with PdfPages(pdf_path) as pdf:
                    for fig in figures:
                        pdf.savefig(fig, bbox_inches='tight')
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="Download All Visuals as PDF",
                        data=f.read(),
                        file_name="three_month_trend_visuals.pdf",
                        mime="application/pdf"
                    )
            st.success("PDF generated! Download using the button above.")
            # Clean up temp file
            os.remove(pdf_path)
        except Exception as e:
            st.error(f"PDF export failed: {e}")

    st.info("You can further extend this dashboard to add more trend visualizations as needed.")

    # ========== Detection Analysis Visualizations ==========
    if template == "Detection Analysis":
        st.header("Detections per File (Month)")
        if 'Month_Index' in df.columns:
            det_per_month = df.groupby('Month_Index').size().reset_index(name='Detections')
            # Convert numeric values to native Python types
            detection_data = [int(x) for x in det_per_month['Detections']]
            month_labels = [str(x) for x in det_per_month['Month_Index']]
            
            options = {
                **get_theme_options(),
                "title": {"text": "Detections per File (Month)"},
                "xAxis": {
                    "type": "category",
                    "data": month_labels,
                    "name": "File (Month)",
                    "nameLocation": "middle",
                    "nameGap": 30,
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections",
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": detection_data,
                    "itemStyle": {"color": MAIN_COLOR},
                    "label": {
                        "show": True,
                        "position": "top"
                    }
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        # Severity trend
        if 'SeverityName' in df.columns and 'Month_Index' in df.columns:
            st.header("Detections by Severity per File (Month)")
            sev_trend = df.groupby(['Month_Index', 'SeverityName']).size().reset_index(name='Count')
            severity_levels = sev_trend['SeverityName'].unique().tolist()
            months = sev_trend['Month_Index'].unique().tolist()
            series = []
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            for i, severity in enumerate(severity_levels):
                # Calculate and convert data points to native Python integers
                data_points = []
                for month in months:
                    count = sev_trend[(sev_trend['Month_Index'] == month) & (sev_trend['SeverityName'] == severity)]['Count'].sum()
                    data_points.append(int(count))
                
                series.append({
                    "name": str(severity),  # Ensure severity is a string
                    "type": "bar",
                    "stack": "total",
                    "itemStyle": {"color": colors[i % len(colors)]},
                    "label": {"show": True, "position": "inside"},
                    "emphasis": {"focus": "series"},
                    "data": data_points
                })
            options = {
                **get_theme_options(),
                "title": {"text": "Detections by Severity per File (Month)"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": severity_levels, "selectedMode": "multiple"},
                "xAxis": {"type": "category", "data": months, "name": "File (Month)", "axisLabel": {"rotate": 45}},
                "yAxis": {"type": "value", "name": "Number of Detections"},
                "series": series
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

        # Detection and Severity Analysis Summary
        st.header("Detection and Severity Analysis")
        
        # Calculate overall metrics
        total_detections = len(df)
        unique_severities = df['SeverityName'].nunique() if 'SeverityName' in df.columns else 0
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Detections", total_detections)
        col2.metric("Unique Severity Levels", unique_severities)
        
        # Severity Distribution
        if 'SeverityName' in df.columns:
            st.subheader("Severity Distribution Overview")
            sev_dist = df['SeverityName'].value_counts().reset_index()
            sev_dist.columns = ['Severity', 'Count']
            sev_dist['Percentage'] = (sev_dist['Count'] / sev_dist['Count'].sum() * 100).round(2)
            
            # Create pie chart for severity distribution
            options = {
                **get_theme_options(),
                "title": {"text": "Overall Severity Distribution"},
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{a} <br/>{b}: {c} ({d}%)"
                },
                "legend": {
                    "orient": "vertical",
                    "right": 10,
                    "data": sev_dist['Severity'].tolist()
                },
                "series": [{
                    "name": "Severity Distribution",
                    "type": "pie",
                    "radius": "60%",
                    "data": [
                        {"value": int(row['Count']), "name": row['Severity']} 
                        for _, row in sev_dist.iterrows()
                    ],
                    "label": {
                        "show": True,
                        "formatter": "{b}: {d}%"
                    }
                }]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

            # Show severity distribution table
            st.dataframe(sev_dist, use_container_width=True)

        # Detection Trend Analysis
        if 'Period' in df.columns:
            st.subheader("Detection Trend Analysis")
            monthly_counts = df.groupby('Period').size().reset_index(name='Count')
            monthly_counts = monthly_counts.sort_values('Period')
            
            # Calculate growth rates
            monthly_counts['Growth'] = monthly_counts['Count'].pct_change() * 100
            
            # Create trend visualization
            options = {
                **get_theme_options(),
                "title": {"text": "Detection Count and Growth Trend"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "legend": {
                    "data": ["Detection Count", "Growth Rate"]
                },
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in monthly_counts['Period']],
                    "name": "Month",
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": [
                    {
                        "type": "value",
                        "name": "Number of Detections",
                        "position": "left"
                    },
                    {
                        "type": "value",
                        "name": "Growth Rate (%)",
                        "position": "right",
                        "axisLabel": {
                            "formatter": "{value}%"
                        }
                    }
                ],
                "series": [
                    {
                        "name": "Detection Count",
                        "type": "line",
                        "data": [int(x) for x in monthly_counts['Count']],
                        "symbol": "circle",
                        "symbolSize": 10,
                        "itemStyle": {"color": MAIN_COLOR},
                        "label": {"show": True, "position": "top"}
                    },
                    {
                        "name": "Growth Rate",
                        "type": "line",
                        "yAxisIndex": 1,
                        "data": [round(x, 2) for x in monthly_counts['Growth'].fillna(0)],
                        "symbol": "triangle",
                        "symbolSize": 10,
                        "itemStyle": {"color": SECONDARY_COLOR},
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}%"
                        }
                    }
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

            # Detection Pattern Analysis
            st.subheader("Pattern Overview")
            
            # Calculate trend metrics
            avg_detections = monthly_counts['Count'].mean()
            total_growth = ((monthly_counts['Count'].iloc[-1] - monthly_counts['Count'].iloc[0]) / monthly_counts['Count'].iloc[0] * 100) if len(monthly_counts) > 1 else 0
            max_period = monthly_counts.loc[monthly_counts['Count'].idxmax(), 'Period']
            min_period = monthly_counts.loc[monthly_counts['Count'].idxmin(), 'Period']
            trend_direction = "� Increasing" if total_growth > 5 else "� Decreasing" if total_growth < -5 else "➡️ Stable"
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average Detections", f"{int(avg_detections):,}", f"{total_growth:+.1f}%")
            col2.metric("Overall Trend", trend_direction)
            col3.metric("Peak Month", f"{max_period} ({int(monthly_counts['Count'].max()):,})")
            col4.metric("Lowest Month", f"{min_period} ({int(monthly_counts['Count'].min()):,})")

            # Severity Distribution Trend
            if 'SeverityName' in df.columns:
                st.subheader("Severity Distribution Over Time")
                severity_trend = df.groupby(['Period', 'SeverityName']).size().unstack(fill_value=0)
                
                # Calculate severity percentages
                severity_pct = severity_trend.div(severity_trend.sum(axis=1), axis=0) * 100
                
                # Create stacked area chart
                options = {
                    **get_theme_options(),
                    "title": {"text": "Severity Distribution Trend"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "cross"}
                    },
                    "legend": {
                        "data": severity_trend.columns.tolist()
                    },
                    "xAxis": {
                        "type": "category",
                        "data": [str(p) for p in severity_trend.index],
                        "name": "Month"
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Percentage",
                        "axisLabel": {
                            "formatter": "{value}%"
                        }
                    },
                    "series": [
                        {
                            "name": severity,
                            "type": "line",
                            "stack": "percentage",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": [round(x, 2) for x in severity_pct[severity]],
                            "label": {"show": True, "formatter": "{c}%"}
                        } for severity in severity_trend.columns
                    ]
                }
                st_echarts(options=options, height="400px")
                figures.append(options)

            # Detection Categories Analysis
            if 'Objective' in df.columns:
                st.subheader("Top Detection Categories Trend")
                objective_trend = df.groupby(['Period', 'Objective']).size().unstack(fill_value=0)
                top_objectives = objective_trend.sum().nlargest(5).index.tolist()
                
                options = {
                    **get_theme_options(),
                    "title": {"text": "Top 5 Detection Categories Over Time"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "cross"}
                    },
                    "legend": {
                        "data": top_objectives,
                        "type": "scroll"
                    },
                    "xAxis": {
                        "type": "category",
                        "data": [str(p) for p in objective_trend.index],
                        "name": "Month"
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Number of Detections"
                    },
                    "series": [
                        {
                            "name": objective,
                            "type": "line",
                            "data": [int(x) for x in objective_trend[objective]],
                            "symbol": "circle",
                            "symbolSize": 8,
                            "label": {"show": True}
                        } for objective in top_objectives
                    ]
                }
                st_echarts(options=options, height="400px")
                figures.append(options)

        # Executive Summary
        st.header("Executive Summary")
        
        # Calculate key metrics and trends for summary
        top_severity = df['SeverityName'].mode().iloc[0] if 'SeverityName' in df.columns else 'N/A'
        avg_monthly_growth = monthly_counts['Growth'].mean()
        trend_strength = abs(avg_monthly_growth)
        trend_description = (
            "strongly increasing" if avg_monthly_growth > 15 else
            "moderately increasing" if avg_monthly_growth > 5 else
            "strongly decreasing" if avg_monthly_growth < -15 else
            "moderately decreasing" if avg_monthly_growth < -5 else
            "stable"
        )
        
        # Calculate severity trends
        if 'SeverityName' in df.columns:
            severity_counts = df.groupby(['Period', 'SeverityName']).size().unstack(fill_value=0)
            critical_trend = (
                "increasing" if severity_counts.get('Critical', pd.Series()).is_monotonic_increasing else
                "decreasing" if severity_counts.get('Critical', pd.Series()).is_monotonic_decreasing else
                "fluctuating"
            )
        else:
            critical_trend = "N/A"
        
        summary_lines = [
            f"📊 Analysis Overview:",
            f"   • Analyzed {total_detections:,} detections across {len(monthly_counts)} months",
            f"   • Detection volume shows a {trend_description} trend ({avg_monthly_growth:+.1f}% average monthly change)",
            f"   • Peak activity observed in {monthly_counts.loc[monthly_counts['Count'].idxmax(), 'Period']} with {int(monthly_counts['Count'].max()):,} detections",
            "",
            f"� Severity Analysis:",
            f"   • Most common severity level: {top_severity}",
            f"   • Critical severity detections are {critical_trend}",
            f"   • {unique_severities} distinct severity levels tracked",
            "",
            "💡 Key Insights:",
            f"   • {'Attention needed: Detection volume is rising significantly' if avg_monthly_growth > 15 else 'Positive trend: Detection volume is decreasing' if avg_monthly_growth < -5 else 'Stable detection pattern observed'}",
            f"   • Average of {int(monthly_counts['Count'].mean()):,} detections per month",
            f"   • Month-over-month variation indicates {'high' if trend_strength > 15 else 'moderate' if trend_strength > 5 else 'low'} volatility"
        ]
        
        st.markdown("\n".join(summary_lines))

        # Top N Objectives per Month
        if 'Objective' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Objectives per Month")
            obj_trend = df.groupby(['Period', 'Objective']).size().reset_index(name='Count')
            
            periods = df['Period'].unique().tolist()
            
            # Create tabs for each period using Streamlit tabs
            tabs = st.tabs(periods)
            
            for tab, period in zip(tabs, periods):
                with tab:
                    period_df = obj_trend[obj_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create ECharts options for horizontal bar chart
                    options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Objectives"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "xAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "yAxis": {
                            "type": "category",
                            "data": period_df['Objective'].tolist()[::-1],  # Reverse for top-to-bottom order
                            "axisLabel": {
                                "width": 150,
                                "overflow": "break"
                            }
                        },
                        "series": [{
                            "name": "Detections",
                            "type": "bar",
                            "data": period_df['Count'].tolist()[::-1],
                            "itemStyle": {"color": SECONDARY_COLOR},
                            "label": {
                                "show": True,
                                "position": "right",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the plot
                    st_echarts(
                        options=options,
                        height=f"{max(400, 50 * len(period_df))}px"
                    )
                    figures.append(options)  # Store for PDF export

        # Top N Countries Comparison
        if 'Country' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Countries Comparison Across Months")
            country_trend = df.groupby(['Period', 'Country']).size().reset_index(name='Count')
            
            # Get the overall top N countries
            top_countries = df.groupby('Country')['Period'].count().nlargest(top_n).index.tolist()
            
            # Filter for top countries and pivot data
            country_trend_filtered = country_trend[country_trend['Country'].isin(top_countries)]
            country_trend_pivot = country_trend_filtered.pivot(index='Period', columns='Country', values='Count').fillna(0)
            
            # Create side-by-side bar chart
            options = {
                **get_theme_options(),
                "title": {"text": f"Top {top_n} Countries Detection Trend"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": top_countries, "top": 25},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in country_trend_pivot.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "series": [
                    {
                        "name": country,
                        "type": "bar",
                        "data": [int(x) for x in country_trend_pivot[country]],
                        "label": {"show": True, "position": "top"}
                    } for country in top_countries
                ]
            }
            st_echarts(options=options, height="500px")
            figures.append(options)

            # Show summary table
            st.subheader("Summary Table")
            country_summary = df.groupby('Country').size().sort_values(ascending=False).head(top_n)
            summary_df = pd.DataFrame({
                'Country': country_summary.index,
                'Total Detections': country_summary.values,
                'Percentage': (country_summary.values / country_summary.sum() * 100).round(2)
            })
            st.dataframe(summary_df, use_container_width=True)
            tabs = []
            # Create tabs container for each period
            period_tabs = st.tabs(list(df['Period'].unique()))
            for period, tab in zip(df['Period'].unique(), period_tabs):
                with tab:
                    period_df = country_trend[country_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create bar chart options
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Countries"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": period_df['Country'].tolist(),
                            "name": "Country",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0,
                                "width": 120,
                                "overflow": "break"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "type": "bar",
                            "data": period_df['Count'].tolist(),
                            "itemStyle": {"color": BAR_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height="400px"
                    )
                    figures.append(bar_options)  # Store for PDF export
                    
                    # Display data table below chart
                    st.dataframe(period_df)
        # Top N Files Analysis
        if 'FileName' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Files with Most Detections")
            file_trend = df.groupby(['Period', 'FileName']).size().reset_index(name='Count')
            
            # Get the overall top N files
            top_files = df.groupby('FileName')['Period'].count().nlargest(top_n).index.tolist()
            
            # Filter for top files and pivot data
            file_trend_filtered = file_trend[file_trend['FileName'].isin(top_files)]
            file_trend_pivot = file_trend_filtered.pivot(index='Period', columns='FileName', values='Count').fillna(0)
            
            # Create side-by-side bar chart
            options = {
                **get_theme_options(),
                "title": {"text": f"Top {top_n} Files Detection Trend"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {
                    "data": top_files,
                    "top": 25,
                    "textStyle": {"width": 150, "overflow": "truncate"}
                },
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in file_trend_pivot.index],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "series": [
                    {
                        "name": file,
                        "type": "bar",
                        "data": [int(x) for x in file_trend_pivot[file]],
                        "label": {"show": True, "position": "top"}
                    } for file in top_files
                ]
            }
            st_echarts(options=options, height="500px")
            figures.append(options)

            # Show summary table
            st.subheader("Summary Table")
            file_summary = df.groupby('FileName').size().sort_values(ascending=False).head(top_n)
            summary_df = pd.DataFrame({
                'File Name': file_summary.index,
                'Total Detections': file_summary.values,
                'Percentage': (file_summary.values / file_summary.sum() * 100).round(2)
            })
            st.dataframe(summary_df, use_container_width=True)
            for period, tab in zip(df['Period'].unique(), period_tabs):
                with tab:
                    period_df = file_trend[file_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create bar chart options
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Files"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "top": "50",
                            "bottom": "50",
                            "left": "30%",
                            "right": "10%"
                        },
                        "yAxis": {
                            "type": "category",
                            "data": period_df['FileName'].tolist(),
                            "inverse": True,
                            "axisLabel": {
                                "width": 200,
                                "overflow": "break"
                            }
                        },
                        "xAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "type": "bar",
                            "data": period_df['Count'].tolist(),
                            "itemStyle": {"color": MAIN_COLOR},
                            "label": {
                                "show": True,
                                "position": "right",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Calculate height based on number of bars (min 400px)
                    chart_height = max(400, 50 * len(period_df) + 150)
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height=f"{chart_height}px"
                    )
                    figures.append(bar_options)  # Store for PDF export
                    
                    # Display data table below chart
                    st.dataframe(period_df)

        # Top N Tactics per Month
        if 'Tactic' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Tactics per Month")
            tactic_trend = df.groupby(['Period', 'Tactic']).size().reset_index(name='Count')
            
            periods = df['Period'].unique().tolist()
            
            # Create tabs for each period using Streamlit tabs
            tabs = st.tabs(periods)
            
            for tab, period in zip(tabs, periods):
                with tab:
                    period_df = tactic_trend[tactic_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create ECharts options for bar chart
                    options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Tactics"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "xAxis": {
                            "type": "category",
                            "data": period_df['Tactic'].tolist(),
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "name": "Detections",
                            "type": "bar",
                            "data": period_df['Count'].tolist(),
                            "itemStyle": {"color": SECONDARY_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the plot
                    st_echarts(
                        options=options,
                        height="400px"
                    )
                    figures.append(options)  # Store for PDF export

        # Top N Techniques per Month
        if 'Technique' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Techniques per Month")
            tech_trend = df.groupby(['Period', 'Technique']).size().reset_index(name='Count')
            
            # Create tabs container for each period
            period_tabs = st.tabs(list(df['Period'].unique()))
            for period, tab in zip(df['Period'].unique(), period_tabs):
                with tab:
                    period_df = tech_trend[tech_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create bar chart options
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Techniques"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": period_df['Technique'].tolist(),
                            "name": "Technique",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0,
                                "width": 120,
                                "overflow": "break"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "type": "bar",
                            "data": period_df['Count'].tolist(),
                            "itemStyle": {"color": BAR_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height="400px"
                    )
                    figures.append(bar_options)  # Store for PDF export
                    
                    # Display data table below chart
                    st.dataframe(period_df)

        # Top N Resolutions per Month
        if 'Resolution' in df.columns and 'Period' in df.columns:
            st.header(f"Top {top_n} Resolutions per Month")
            res_trend = df.groupby(['Period', 'Resolution']).size().reset_index(name='Count')
            
            # Create tabs container for each period
            period_tabs = st.tabs(list(df['Period'].unique()))
            for period, tab in zip(df['Period'].unique(), period_tabs):
                with tab:
                    period_df = res_trend[res_trend['Period'] == period].sort_values('Count', ascending=False).head(top_n)
                    
                    # Create bar chart options
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top {top_n} Resolutions"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": period_df['Resolution'].tolist(),
                            "name": "Resolution",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0,
                                "width": 120,
                                "overflow": "break"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "type": "bar",
                            "data": period_df['Count'].tolist(),
                            "itemStyle": {"color": MAIN_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height="400px"
                    )
                    figures.append(bar_options)  # Store for PDF export
                    
                    # Display data table below chart
                    st.dataframe(period_df)

    # ========== Host Analysis Visualizations (3-Month Trend) ==========
    elif template == "Host Analysis":
        st.header("Host Analysis: 3-Month Trend")
        # Ensure datetime for detection time
        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], errors='coerce')

        # Overview metrics (aggregate)
        total_hosts = df['Hostname'].nunique() if 'Hostname' in df.columns else 0
        total_detections = len(df)
        windows_hosts = df[df['OS Version'].str.contains('Windows', na=False)]['Hostname'].nunique() if 'OS Version' in df.columns else 0
        avg_detections = round(total_detections / total_hosts, 2) if total_hosts > 0 else 0
        st.subheader("Aggregate Metrics (All Months)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Hosts", total_hosts)
        col2.metric("Total Detections", total_detections)
        col3.metric("Windows Hosts", windows_hosts)
        col4.metric("Avg. Detections/Host", avg_detections)

        # Trend: Unique Hosts per Month
        if 'Period' in df.columns and 'Hostname' in df.columns:
            hosts_per_month = df.groupby('Period')['Hostname'].nunique().reset_index(name='Unique Hosts')
            
            # Create ECharts options for line chart
            options = {
                **get_theme_options(),
                "title": {"text": "Unique Hosts per Month"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "xAxis": {
                    "type": "category",
                    "data": hosts_per_month['Period'].tolist(),
                    "name": "Month",
                    "nameLocation": "middle",
                    "nameGap": 30,
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Unique Hosts",
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": [{
                    "name": "Unique Hosts",
                    "type": "line",
                    "data": hosts_per_month['Unique Hosts'].tolist(),
                    "itemStyle": {"color": SECONDARY_COLOR},
                    "symbol": "circle",
                    "symbolSize": 10,
                    "label": {
                        "show": True,
                        "position": "top"
                    }
                }]
            }
            
            # Show the plot
            st_echarts(
                options=options,
                height="400px"
            )
            figures.append(options)  # Store for PDF export

            # Trend: Detections per Month
            if 'Period' in df.columns:
                det_per_month = df.groupby('Period').size().reset_index(name='Detections')
                
                # Create ECharts options for bar chart
                options = {
                    **get_theme_options(),
                    "title": {"text": "Detections per Month"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "xAxis": {
                        "type": "category",
                        "data": det_per_month['Period'].tolist(),
                        "name": "Month",
                        "nameLocation": "middle",
                        "nameGap": 30,
                        "axisLabel": {"rotate": 45}
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Number of Detections",
                        "nameLocation": "middle",
                        "nameGap": 50
                    },
                    "series": [{
                        "name": "Detections",
                        "type": "bar",
                        "data": det_per_month['Detections'].tolist(),
                        "itemStyle": {"color": MAIN_COLOR},
                        "label": {
                            "show": True,
                            "position": "top"
                        }
                    }]
                }
                
                # Show the plot
                st_echarts(
                    options=options,
                    height="400px"
                )
                figures.append(options)  # Store for PDF export        # Top N Hosts (aggregate)
        if 'Hostname' in df.columns:
            st.header(f"Top {top_n} Hosts with Most Detections (Aggregate)")
            host_counts = df.groupby('Hostname').size().reset_index(name='Count').sort_values('Count', ascending=False).head(top_n)
            
            # Create ECharts options for horizontal bar chart
            options = {
                **get_theme_options(),
                "title": {"text": f"Top {top_n} Hosts with Most Detections (All Months)"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"}
                },
                "xAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "yAxis": {
                    "type": "category",
                    "data": host_counts['Hostname'].tolist()[::-1],  # Reverse for top-to-bottom order
                    "axisLabel": {
                        "width": 150,
                        "overflow": "break"
                    }
                },
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": host_counts['Count'].tolist()[::-1],
                    "itemStyle": {"color": SECONDARY_COLOR},
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{c}"
                    }
                }]
            }
            
            # Show the plot
            st_echarts(
                options=options,
                height=f"{max(400, 50 * len(host_counts))}px"
            )
            figures.append(options)  # Store for PDF export
            st.dataframe(host_counts.iloc[::-1], use_container_width=True)

        # Top N Users (aggregate)
        if 'UserName' in df.columns:
            st.header(f"Top {top_n} Users with Most Detections (Aggregate)")
            filtered_df = df[df['UserName'].str.strip() != '']
            user_counts = filtered_df.groupby('UserName').size().reset_index(name='Count').sort_values('Count', ascending=False).head(top_n)
            
            # Create ECharts options for horizontal bar chart
            options = {
                **get_theme_options(),
                "title": {"text": f"Top {top_n} Users with Most Detections (All Months)"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"}
                },
                "xAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "yAxis": {
                    "type": "category",
                    "data": user_counts['UserName'].tolist()[::-1],  # Reverse for top-to-bottom order
                    "axisLabel": {
                        "width": 150,
                        "overflow": "break"
                    }
                },
                "series": [{
                    "name": "Detections",
                    "type": "bar",
                    "data": user_counts['Count'].tolist()[::-1],
                    "itemStyle": {"color": MAIN_COLOR},
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{c}"
                    }
                }]
            }
            
            # Show the plot
            st_echarts(
                options=options,
                height=f"{max(400, 50 * len(user_counts))}px"
            )
            figures.append(options)  # Store for PDF export
            st.dataframe(user_counts.iloc[::-1], use_container_width=True)

        # Platform Distribution (aggregate)
        if 'Platform' in df.columns:
            st.header("Platform Distribution (Aggregate)")
            platform_counts = df.groupby('Platform').size().reset_index(name='Count').sort_values('Count', ascending=False)
            os_counts = df.groupby('OS Version').size().reset_index(name='Count').sort_values('Count', ascending=False)
            
            if not platform_counts.empty:
                # Calculate percentages for pie chart
                colors = [MAIN_COLOR, SECONDARY_COLOR, BAR_COLOR][:len(platform_counts)]
                
                # Create pie chart options
                pie_options = {
                    **get_theme_options(),
                    "title": {"text": "Platform Distribution (All Months)"},
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{b}: {c} ({d}%)"
                    },
                    "legend": {
                        "orient": "vertical",
                        "right": 10,
                        "top": "center"
                    },
                    "series": [{
                        "type": "pie",
                        "radius": "75%",
                        "data": [
                            {
                                "name": row.Platform,
                                "value": row.Count,
                                "itemStyle": {"color": color}
                            }
                            for row, color in zip(platform_counts.itertuples(), colors)
                        ],
                        "label": {
                            "show": True,
                            "formatter": "{b}\n{d}%"
                        },
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)"
                            }
                        }
                    }]
                }
                
                # Show the pie chart
                st_echarts(
                    options=pie_options,
                    height="400px"
                )
                figures.append(pie_options)  # Store for PDF export
            
            if not os_counts.empty:
                # Create bar chart options
                bar_options = {
                    **get_theme_options(),
                    "title": {"text": "Top OS Versions (All Months)"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "xAxis": {
                        "type": "category",
                        "data": os_counts['OS Version'].tolist(),
                        "axisLabel": {
                            "rotate": 45,
                            "interval": 0,
                            "width": 100,
                            "overflow": "break"
                        }
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Number of Detections"
                    },
                    "series": [{
                        "name": "OS Versions",
                        "type": "bar",
                        "data": os_counts['Count'].tolist(),
                        "itemStyle": {"color": SECONDARY_COLOR},
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        }
                    }]
                }
                
                # Show the bar chart
                st_echarts(
                    options=bar_options,
                    height="400px"
                )
                figures.append(bar_options)  # Store for PDF export
                st.dataframe(os_counts.head(top_n), use_container_width=True)

        # Sensor Version Status (aggregate)
        if 'Sensor Version' in df.columns:
            st.header("Hosts with Sensor Version Status (Aggregate)")
            sensor_counts = df.groupby('Sensor Version').size().reset_index(name='Count').sort_values('Count', ascending=False)
            if not sensor_counts.empty:
                # Create bar chart options
                bar_options = {
                    **get_theme_options(),
                    "title": {"text": "Top Sensor Versions (All Months)"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "xAxis": {
                        "type": "category",
                        "data": sensor_counts['Sensor Version'].tolist(),
                        "axisLabel": {
                            "rotate": 45,
                            "interval": 0,
                            "width": 100,
                            "overflow": "break"
                        }
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Number of Hosts"
                    },
                    "series": [{
                        "name": "Sensor Versions",
                        "type": "bar",
                        "data": sensor_counts['Count'].tolist(),
                        "itemStyle": {"color": BAR_COLOR},
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        }
                    }]
                }
                
                # Show the bar chart
                st_echarts(
                    options=bar_options,
                    height="400px"
                )
                figures.append(bar_options)  # Store for PDF export
                st.dataframe(sensor_counts.head(top_n), use_container_width=True)

        # Detection Activity Over Time (aggregate) with trend and heatmap
        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            st.header("Detection Activity Over Time (All Months)")
            # Ensure datetime
            if not pd.api.types.is_datetime64_any_dtype(df['Detect MALAYSIA TIME FORMULA']):
                df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], errors='coerce')
            
            valid_dates = df['Detect MALAYSIA TIME FORMULA'].dropna()
            if not valid_dates.empty:
                # Daily trend line
                date_counts = df.groupby(df['Detect MALAYSIA TIME FORMULA'].dt.date).size().reset_index(name='Count')
                date_counts = date_counts.sort_values('Detect MALAYSIA TIME FORMULA')
                
                # Convert dates to string format for ECharts
                date_str = [d.strftime('%Y-%m-%d') for d in date_counts['Detect MALAYSIA TIME FORMULA']]
                
                # Create line chart options
                line_options = {
                    **get_theme_options(),
                    "title": {"text": "Detection Trend Over Time"},
                    "tooltip": {
                        "trigger": "axis",
                        "formatter": "Date: {b}<br/>Detections: {c}"
                    },
                    "xAxis": {
                        "type": "category",
                        "data": date_str,
                        "boundaryGap": False,
                        "axisLabel": {
                            "rotate": 45,
                            "interval": "auto"
                        }
                    },
                    "yAxis": {
                        "type": "value",
                        "name": "Number of Detections"
                    },
                    "series": [{
                        "name": "Detections",
                        "type": "line",
                        "data": date_counts['Count'].tolist(),
                        "itemStyle": {"color": MAIN_COLOR},
                        "lineStyle": {"color": MAIN_COLOR},
                        "symbol": "circle",
                        "symbolSize": 6,
                        "label": {
                            "show": False
                        }
                    }]
                }
                
                # Show the line chart
                st_echarts(
                    options=line_options,
                    height="400px"
                )
                figures.append(line_options)  # Store for PDF export

                # Create weekly heatmap
                df['Week'] = df['Detect MALAYSIA TIME FORMULA'].dt.isocalendar().week
                df['Weekday'] = df['Detect MALAYSIA TIME FORMULA'].dt.day_name()
                weekly_counts = df.groupby(['Week', 'Weekday']).size().reset_index(name='Count')
                
                # Pivot the data for the heatmap
                pivot_table = weekly_counts.pivot(index='Week', columns='Weekday', values='Count')
                # Reorder days of week
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                pivot_table = pivot_table.reindex(columns=days_order)
                
                # Prepare data for ECharts heatmap
                weeks = pivot_table.index.tolist()
                days = pivot_table.columns.tolist()
                data = []
                for i, week in enumerate(weeks):
                    for j, day in enumerate(days):
                        value = pivot_table.loc[week, day]
                        count = value if pd.notnull(value) else 0
                        data.append([j, len(weeks) - 1 - i, count])  # Reverse week order
                
                max_count = pivot_table.max().max()
                
                # Create heatmap options
                heatmap_options = {
                    **get_theme_options(),
                    "title": {"text": "Weekly Detection Activity Heatmap"},
                    "tooltip": {
                        "position": "top",
                        "formatter": "Week {b}, {a}: {c}"
                    },
                    "animation": True,
                    "grid": {
                        "height": "80%",
                        "top": "10%"
                    },
                    "xAxis": {
                        "type": "category",
                        "data": days,
                        "splitArea": {
                            "show": True
                        }
                    },
                    "yAxis": {
                        "type": "category",
                        "data": [str(w) for w in weeks][::-1],  # Reverse for proper orientation
                        "splitArea": {
                            "show": True
                        }
                    },
                    "visualMap": {
                        "min": 0,
                        "max": max_count,
                        "calculable": True,
                        "orient": "horizontal",
                        "left": "center",
                        "bottom": "5%",
                        "inRange": {
                            "color": ['#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
                        }
                    },
                    "series": [{
                        "name": "Detections",
                        "type": "heatmap",
                        "data": data,
                        "label": {
                            "show": False
                        },
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowColor": "rgba(0, 0, 0, 0.5)"
                            }
                        }
                    }]
                }
                # Show the heatmap
                st_echarts(
                    options=heatmap_options,
                    height="400px"
                )
                figures.append(heatmap_options)  # Store for PDF export

                
                # Show detailed statistics
                st.subheader("Detection Activity Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Daily Detections", 
                            f"{date_counts['Count'].mean():.1f}")
                with col2:
                    st.metric("Peak Daily Detections", 
                            f"{date_counts['Count'].max()}")
                with col3:
                    peak_date = date_counts.loc[date_counts['Count'].idxmax(), 'Detect MALAYSIA TIME FORMULA']
                    st.metric("Peak Detection Date", 
                            peak_date.strftime('%Y-%m-%d'))
                
                # Show data table
                st.dataframe(date_counts.rename(
                    columns={'Detect MALAYSIA TIME FORMULA': 'Date', 'Count': 'Detections'}
                ).sort_values('Date', ascending=False), 
                use_container_width=True)

        # Executive Summary (aggregate)
        st.header("Executive Summary (Aggregate)")
        top_host = df.groupby('Hostname').size().idxmax() if not df.empty and 'Hostname' in df.columns else ''
        top_host_count = df.groupby('Hostname').size().max() if not df.empty and 'Hostname' in df.columns else 0
        summary_lines = [
            f"This 3-month trend report reveals {total_hosts} unique hosts with {total_detections} security detections.",
            f"The host '{top_host}' shows the highest detection count at {top_host_count}.",
            f"Windows is the dominant platform ({windows_hosts} Windows hosts).",
            "Prioritize remediation for high-risk hosts and update sensor versions on outdated hosts."
        ]
        st.markdown("\n".join([f"- {line}" for line in summary_lines]))
    elif template == "Host Analysis":
        # Overview metrics (aggregate and per month)
        st.header("Host Overview Metrics")
        if 'Hostname' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                total_hosts = period_df['Hostname'].nunique()
                total_detections = len(period_df)
                windows_hosts = period_df[period_df['OS Version'].str.contains('Windows', na=False)]['Hostname'].nunique() if 'OS Version' in period_df.columns else 0
                avg_detections = round(total_detections / total_hosts, 2) if total_hosts > 0 else 0
                st.subheader(f"{period} - Metrics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Hosts", total_hosts)
                col2.metric("Total Detections", total_detections)
                col3.metric("Windows Hosts", windows_hosts)
                col4.metric("Avg. Detections/Host", avg_detections)

        # Top N Hosts with Most Detections (bar chart + table)
        st.header(f"Top {top_n} Hosts with Most Detections (per Month)")
        if 'Hostname' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                host_counts = period_df.groupby('Hostname').size().reset_index(name='Count').sort_values('Count', ascending=False).head(top_n)
                # Create horizontal bar chart with ECharts
                bar_options = {
                    **get_theme_options(),
                    "title": {"text": f"{period} - Top {top_n} Hosts with Most Detections"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "grid": {
                        "top": "50",
                        "bottom": "50",
                        "left": "25%",
                        "right": "10%"
                    },
                    "yAxis": {
                        "type": "category",
                        "data": host_counts['Hostname'].tolist(),
                        "inverse": True,
                        "axisLabel": {
                            "width": 150,
                            "overflow": "break"
                        }
                    },
                    "xAxis": {
                        "type": "value",
                        "name": "Number of Detections"
                    },
                    "series": [{
                        "type": "bar",
                        "data": host_counts['Count'].tolist(),
                        "itemStyle": {"color": SECONDARY_COLOR},
                        "label": {
                            "show": True,
                            "position": "right",
                            "formatter": "{c}"
                        }
                    }]
                }
                
                # Show the horizontal bar chart
                st_echarts(
                    options=bar_options,
                    height="400px"
                )
                figures.append(bar_options)
                st.dataframe(host_counts, use_container_width=True)

        # Top N Users with Most Detections (bar chart + table)
        st.header(f"Top {top_n} Users with Most Detections (per Month)")
        if 'UserName' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                filtered_df = period_df[period_df['UserName'].str.strip() != '']
                user_counts = filtered_df.groupby('UserName').size().reset_index(name='Count').sort_values('Count', ascending=False).head(top_n)
                # Create horizontal bar chart with ECharts
                bar_options = {
                    **get_theme_options(),
                    "title": {"text": f"{period} - Top {top_n} Users with Most Detections"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "grid": {
                        "top": "50",
                        "bottom": "50",
                        "left": "25%",
                        "right": "10%"
                    },
                    "yAxis": {
                        "type": "category",
                        "data": user_counts['UserName'].tolist(),
                        "inverse": True,
                        "axisLabel": {
                            "width": 150,
                            "overflow": "break"
                        }
                    },
                    "xAxis": {
                        "type": "value",
                        "name": "Number of Detections"
                    },
                    "series": [{
                        "type": "bar",
                        "data": user_counts['Count'].tolist(),
                        "itemStyle": {"color": MAIN_COLOR},
                        "label": {
                            "show": True,
                            "position": "right",
                            "formatter": "{c}"
                        }
                    }]
                }
                
                # Show the horizontal bar chart
                st_echarts(
                    options=bar_options,
                    height="400px"
                )
                figures.append(bar_options)
                st.dataframe(user_counts, use_container_width=True)

        # Platform Distribution (pie chart + bar chart for OS versions)
        st.header("Platform Distribution (per Month)")
        if 'Platform' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                platform_counts = period_df.groupby('Platform').size().reset_index(name='Count').sort_values('Count', ascending=False)
                os_counts = period_df.groupby('OS Version').size().reset_index(name='Count').sort_values('Count', ascending=False)
                if not platform_counts.empty:
                    fig, ax = plt.subplots()
                    ax.pie(platform_counts['Count'], labels=platform_counts['Platform'], autopct='%1.1f%%', colors=[MAIN_COLOR, SECONDARY_COLOR, BAR_COLOR])
                    ax.set_title(f"{period} - Platform Distribution")
                    st.pyplot(fig)
                    figures.append(fig)
                if not os_counts.empty:
                    # Create bar chart with ECharts
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top OS Versions"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": os_counts['OS Version'].tolist(),
                            "name": "OS Version",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0,
                                "width": 120,
                                "overflow": "break"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [{
                            "type": "bar",
                            "data": os_counts['Count'].tolist(),
                            "itemStyle": {"color": SECONDARY_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height="400px"
                    )
                    figures.append(bar_options)
                    st.dataframe(os_counts.head(top_n), use_container_width=True)

        # Sensor Version Status (bar chart)
        st.header("Hosts with Sensor Version Status (per Month)")
        if 'Sensor Version' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                sensor_counts = period_df.groupby('Sensor Version').size().reset_index(name='Count').sort_values('Count', ascending=False)
                if not sensor_counts.empty:
                    # Create bar chart with ECharts
                    bar_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Top Sensor Versions"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": sensor_counts['Sensor Version'].tolist(),
                            "name": "Sensor Version",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0,
                                "width": 120,
                                "overflow": "break"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Hosts"
                        },
                        "series": [{
                            "type": "bar",
                            "data": sensor_counts['Count'].tolist(),
                            "itemStyle": {"color": BAR_COLOR},
                            "label": {
                                "show": True,
                                "position": "top",
                                "formatter": "{c}"
                            }
                        }]
                    }
                    
                    # Show the bar chart
                    st_echarts(
                        options=bar_options,
                        height="400px"
                    )
                    figures.append(bar_options)
                    st.dataframe(sensor_counts.head(top_n), use_container_width=True)

        # Detection Activity Over Time (line chart)
        st.header("Detection Activity Over Time (per Month)")
        if 'Detect MALAYSIA TIME FORMULA' in df.columns and 'Period' in df.columns:
            for period in df['Period'].unique():
                period_df = df[df['Period'] == period]
                if not df['Detect MALAYSIA TIME FORMULA'].isna().all():
                    date_counts = df.groupby(df['Detect MALAYSIA TIME FORMULA'].dt.date).size().reset_index(name='Count')
                    # Create line chart with ECharts
                    line_options = {
                        **get_theme_options(),
                        "title": {"text": "Detection Activity Over Time (All Months)"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "cross"}
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "bottom": "15%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": [d.strftime('%Y-%m-%d') for d in date_counts['Detect MALAYSIA TIME FORMULA']],
                            "name": "Date",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": "auto"
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Detections"
                        },
                        "series": [{
                            "name": "Detections",
                            "type": "line",
                            "data": date_counts['Count'].tolist(),
                            "itemStyle": {"color": MAIN_COLOR},
                            "symbol": "circle",
                            "symbolSize": 6,
                            "lineStyle": {"width": 2},
                            "label": {
                                "show": False
                            }
                        }]
                    }
                    
                    # Show the line chart
                    st_echarts(
                        options=line_options,
                        height="400px"
                    )
                    figures.append(line_options)
                    st.dataframe(date_counts, use_container_width=True)

            # Executive Summary (aggregate, improved markdown)
            st.header("Executive Summary (Aggregate)")
            top_host = df.groupby('Hostname').size().idxmax() if not df.empty and 'Hostname' in df.columns else ''
            top_host_count = df.groupby('Hostname').size().max() if not df.empty and 'Hostname' in df.columns else 0
            summary_lines = [
                f"This 3-month trend report reveals {total_hosts} unique hosts with {total_detections} security detections.",
                f"The host '{top_host}' shows the highest detection count at {top_host_count}.",
                f"Windows is the dominant platform ({windows_hosts} Windows hosts).",
                "Prioritize remediation for high-risk hosts and update sensor versions on outdated hosts."
            ]
            st.markdown("\n".join([f"- {line}" for line in summary_lines]))
    # ========== Time Analysis Visualizations ==========
    elif template == "Time Analysis":
        st.header("Time-Based Trend Analysis")

        # Prepare time-based data
        if 'Detect MALAYSIA TIME FORMULA' in df.columns:
            # Robust datetime parsing for mixed formats
            df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(
                df['Detect MALAYSIA TIME FORMULA'],
                dayfirst=True, errors='coerce'
            )
            # Extract time components
            df['Hour'] = df['Detect MALAYSIA TIME FORMULA'].dt.hour
            df['Day_of_Week'] = df['Detect MALAYSIA TIME FORMULA'].dt.dayofweek
            df['Day_Name'] = df['Detect MALAYSIA TIME FORMULA'].dt.day_name()
            
            # Basic metrics
            total_detections = len(df)
            
            # === 1. Monthly Activity Pattern Analysis ===
            st.subheader("Monthly Activity Patterns")
            
            # Business Hours vs Non-Business Hours by Month
            business_hours = df[df['Hour'].between(9, 16)]  # 9 AM to 5 PM
            monthly_time_dist = pd.DataFrame({
                'Period': df['Period'].unique()
            })
            
            for period in monthly_time_dist['Period']:
                period_data = df[df['Period'] == period]
                period_business = business_hours[business_hours['Period'] == period]
                total_count = len(period_data)
                if total_count > 0:
                    business_pct = len(period_business) / total_count * 100
                else:
                    business_pct = 0
                monthly_time_dist.loc[monthly_time_dist['Period'] == period, 'Business_Hours_Pct'] = business_pct
                monthly_time_dist.loc[monthly_time_dist['Period'] == period, 'After_Hours_Pct'] = 100 - business_pct
            
            # Create visualization
            options = {
                **get_theme_options(),
                "title": {"text": "Business Hours vs After Hours Detection Trend"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Business Hours (9AM-5PM)", "After Hours"]},
                "xAxis": {
                    "type": "category",
                    "data": [str(p) for p in monthly_time_dist['Period']],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Percentage",
                    "axisLabel": {"formatter": "{value}%"}
                },
                "series": [
                    {
                        "name": "Business Hours (9AM-5PM)",
                        "type": "bar",
                        "stack": "total",
                        "data": [round(x, 1) for x in monthly_time_dist['Business_Hours_Pct']],
                        "label": {"show": True, "formatter": "{c}%"}
                    },
                    {
                        "name": "After Hours",
                        "type": "bar",
                        "stack": "total",
                        "data": [round(x, 1) for x in monthly_time_dist['After_Hours_Pct']],
                        "label": {"show": True, "formatter": "{c}%"}
                    }
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

            # === 2. Hourly Pattern Analysis ===
            st.subheader("Hourly Detection Patterns Across Months")
            
            hourly_dist = df.groupby(['Period', 'Hour']).size().reset_index(name='Count')
            periods = hourly_dist['Period'].unique()
            
            # Create visualization
            options = {
                **get_theme_options(),
                "title": {"text": "Hourly Detection Distribution by Month"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": [str(p) for p in periods]},
                "xAxis": {
                    "type": "category",
                    "data": list(range(24)),
                    "name": "Hour of Day",
                    "axisLabel": {"formatter": "{value}:00"}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "series": [
                    {
                        "name": str(period),
                        "type": "line",
                        "data": [int(hourly_dist[(hourly_dist['Period'] == period) & 
                                               (hourly_dist['Hour'] == hour)]['Count'].sum())
                                for hour in range(24)],
                        "symbol": "circle",
                        "symbolSize": 8,
                        "label": {"show": True}
                    } for period in periods
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

            # === 3. Day of Week Analysis ===
            st.subheader("Day of Week Patterns Across Months")
            
            dow_dist = df.groupby(['Period', 'Day_Name', 'Day_of_Week']).size().reset_index(name='Count')
            dow_dist = dow_dist.sort_values('Day_of_Week')
            
            # Create visualization
            options = {
                **get_theme_options(),
                "title": {"text": "Weekly Detection Pattern by Month"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": [str(p) for p in periods]},
                "xAxis": {
                    "type": "category",
                    "data": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "series": [
                    {
                        "name": str(period),
                        "type": "bar",
                        "data": [int(dow_dist[(dow_dist['Period'] == period) & 
                                            (dow_dist['Day_of_Week'] == day)]['Count'].sum())
                                for day in range(7)]
                    } for period in periods
                ]
            }
            st_echarts(options=options, height="400px")
            figures.append(options)

            # === 4. Time-Based Pattern Summary ===
            st.subheader("Time-Based Pattern Summary")
            
            # Calculate summary metrics
            peak_hours = df.groupby('Hour')['Period'].count().idxmax()
            peak_day = df.groupby('Day_Name')['Period'].count().idxmax()
            
            # Business hours percentage trend
            business_hours_trend = "increasing" if monthly_time_dist['Business_Hours_Pct'].is_monotonic_increasing else \
                                 "decreasing" if monthly_time_dist['Business_Hours_Pct'].is_monotonic_decreasing else \
                                 "fluctuating"
            
            # Create metrics display
            col1, col2, col3 = st.columns(3)
            col1.metric("Peak Activity Hour", f"{peak_hours}:00")
            col2.metric("Most Active Day", peak_day)
            col3.metric("Business Hours Trend", business_hours_trend)

            # Display temporal insights
            st.markdown("### 🔍 Temporal Insights")
            insights = [
                f"📅 Peak detection activity occurs at {peak_hours}:00 across all months",
                f"📊 {peak_day} shows consistently higher detection volumes",
                f"⏰ Business hours detection pattern is {business_hours_trend}",
                "🔄 Monthly comparison shows " + (
                    "consistent patterns" if len(set(monthly_time_dist['Business_Hours_Pct'])) <= 2
                    else "varying patterns"
                ) + " in detection timing"
            ]
            
            for insight in insights:
                st.markdown(f"- {insight}")

        else:
            st.warning("Time analysis requires the 'Detect MALAYSIA TIME FORMULA' column to be present in the data.")
            det_per_month = df.groupby('Period').size().reset_index(name='Detections')

            # Calculate trend line
            x_trend = np.arange(len(det_per_month))
            y_trend = np.poly1d(np.polyfit(x_trend, det_per_month['Detections'], 1))(x_trend)
            
            # Create line chart options
            line_options = {
                **get_theme_options(),
                "title": {"text": "Detections per Month (Time Analysis)"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "legend": {
                    "data": ["Detections", "Trend"],
                    "top": "bottom"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "boundaryGap": False,
                    "data": det_per_month['Period'].tolist(),
                },
                "yAxis": {
                    "type": "value",
                    "name": "Number of Detections"
                },
                "series": [
                    {
                        "name": "Detections",
                        "type": "line",
                        "data": det_per_month['Detections'].tolist(),
                        "symbolSize": 10,
                        "itemStyle": {"color": MAIN_COLOR},
                        "lineStyle": {"width": 2},
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        }
                    },
                    {
                        "name": "Trend",
                        "type": "line",
                        "data": y_trend.tolist(),
                        "symbolSize": 0,
                        "lineStyle": {
                            "width": 2,
                            "type": "dashed",
                            "color": "#999"
                        },
                        "label": {"show": False}
                    }
                ]
            }
            
            # Show the line chart
            st_echarts(
                options=line_options,
                height="400px"
            )
            figures.append(line_options)  # Store for PDF export

        # Hourly trend (if Hour column exists)
        if 'Hour' in df.columns and 'Period' in df.columns:
            st.header("Hourly Detection Trend per Month")
            hour_trend = df.groupby(['Period', 'Hour']).size().reset_index(name='Count')
            
            # Create tabs for each period
            # Create tabs container
            tabs_container = st.tabs(list(df['Period'].unique()))
            for period, tab in zip(df['Period'].unique(), tabs_container):
                with tab:
                    period_df = hour_trend[hour_trend['Period'] == period]
                    hours = sorted(period_df['Hour'].unique())
                    
                    # Create mixed chart options
                    mixed_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Hourly Detection Trend"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "cross"}
                        },
                        "legend": {
                            "data": ["Bar", "Trend Line"],
                            "top": "bottom"
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": [str(h) for h in hours],
                            "name": "Hour of Day",
                            "axisLabel": {"formatter": "{value}:00"}
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [
                            {
                                "name": "Bar",
                                "type": "bar",
                                "data": period_df['Count'].tolist(),
                                "itemStyle": {"color": SECONDARY_COLOR, "opacity": 0.6},
                                "label": {
                                    "show": False
                                }
                            },
                            {
                                "name": "Trend Line",
                                "type": "line",
                                "data": period_df['Count'].tolist(),
                                "smooth": True,
                                "symbolSize": 6,
                                "itemStyle": {"color": MAIN_COLOR},
                                "lineStyle": {"width": 2},
                                "label": {
                                    "show": False
                                }
                            }
                        ]
                    }
                    
                    # Show the mixed chart
                    st_echarts(
                        options=mixed_options,
                        height="400px"
                    )
                    figures.append(mixed_options)  # Store for PDF export


        # Day of week trend (if Day_Name column exists)
        if 'Day_Name' in df.columns and 'Period' in df.columns:
            st.header("Day of Week Detection Trend per Month")
            day_trend = df.groupby(['Period', 'Day_Name']).size().reset_index(name='Count')
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Create tabs container for each period
            period_tabs = st.tabs(list(df['Period'].unique()))
            for period, tab in zip(df['Period'].unique(), period_tabs):
                with tab:
                    period_df = day_trend[day_trend['Period'] == period]
                    # Sort the data by day of week
                    period_df['Day_Name'] = pd.Categorical(period_df['Day_Name'], categories=days_order, ordered=True)
                    period_df = period_df.sort_values('Day_Name')
                    
                    # Create mixed chart options
                    mixed_options = {
                        **get_theme_options(),
                        "title": {"text": f"{period} - Day of Week Detection Trend"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "cross"}
                        },
                        "legend": {
                            "data": ["Bar", "Trend Line"],
                            "top": "bottom"
                        },
                        "grid": {
                            "left": "3%",
                            "right": "4%",
                            "containLabel": True
                        },
                        "xAxis": {
                            "type": "category",
                            "data": days_order,
                            "name": "Day of Week",
                            "axisLabel": {
                                "rotate": 45,
                                "interval": 0
                            }
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "Number of Detections"
                        },
                        "series": [
                            {
                                "name": "Bar",
                                "type": "bar",
                                "data": period_df['Count'].tolist(),
                                "itemStyle": {"color": BAR_COLOR, "opacity": 0.6},
                                "label": {
                                    "show": True,
                                    "position": "top",
                                    "formatter": "{c}"
                                }
                            },
                            {
                                "name": "Trend Line",
                                "type": "line",
                                "data": period_df['Count'].tolist(),
                                "smooth": True,
                                "symbolSize": 6,
                                "itemStyle": {"color": MAIN_COLOR},
                                "lineStyle": {"width": 2},
                                "label": {"show": False}
                            }
                        ]
                    }
                    
                    # Show the mixed chart
                    st_echarts(
                        options=mixed_options,
                        height="400px"
                    )
                    figures.append(mixed_options)  # Store for PDF export

    # ========== PDF Export ==========
    if export_pdf and figures:
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
                pdf_path = tmpfile.name
                with PdfPages(pdf_path) as pdf:
                    for fig in figures:
                        pdf.savefig(fig, bbox_inches='tight')
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="Download All Visuals as PDF",
                        data=f.read(),
                        file_name="three_month_trend_visuals.pdf",
                        mime="application/pdf"
                    )
            st.success("PDF generated! Download using the button above.")
            # Clean up temp file
            os.remove(pdf_path)
        except Exception as e:
            st.error(f"PDF export failed: {e}")

    st.info("You can further extend this dashboard to add more trend visualizations as needed.")
