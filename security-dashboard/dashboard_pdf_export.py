"""
Falcon Security Dashboard - PDF Export Layout
Single-page dashboard matching PDF export format
Uses exact chart logic from pivot_table_builder.py with PDF styling
Developed by Izami Ariff © 2025
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any

# Import the perfected chart creation function from pivot_table_builder
import sys
import os
sys.path.append(os.path.dirname(__file__))
from pivot_table_builder import create_pivot_chart, create_pivot_table

# ============================================
# COLOR SCHEMES (Same as pivot_table_builder)
# ============================================

MONTHLY_COLORS = {
    'month_1': '#70AD47',  # Green (oldest)
    'month_2': '#5B9BD5',  # Blue (middle)
    'month_3': '#FFC000'   # Gold (latest)
}

SEVERITY_COLORS = {
    'Critical': '#DC143C',  # Crimson Red
    'High': '#ED7D31',      # Orange
    'Medium': '#5B9BD5',    # Blue
    'Low': '#70AD47'        # Green
}

# PDF Styling colors
SECTION_HEADER_COLOR = '#1f4e5f'  # Dark teal
PAGE_BACKGROUND = '#f0f0f0'       # Light gray
CHART_BACKGROUND = '#ffffff'      # White
BORDER_COLOR = '#d0d0d0'          # Light gray border


# ============================================
# CSS STYLING
# ============================================

def apply_dashboard_css():
    """Apply custom CSS for PDF-style dashboard layout optimized for A4"""
    st.markdown("""
        <style>
        /* Page background */
        .main {
            background-color: #f0f0f0;
        }

        /* Analysis section with gradient background */
        .analysis-section {
            background: transparent;
            border: none;
            border-radius: 0px;
            padding: 0px;
            margin-bottom: 8px;
            box-shadow: none;
        }

        /* Section headers */
        .section-header {
            background-color: #1f4e5f;
            color: white;
            padding: 5px 10px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 4px 4px 0 0;
            margin-top: 8px;
            margin-bottom: 3px;
            font-family: Arial, sans-serif;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        /* Page break control - Section A completes on Page 1 */
        .page-break-after {
            page-break-after: always;
            break-after: always;
        }

        /* Prevent breaking inside sections B partial */
        .no-page-break {
            page-break-inside: avoid;
            break-inside: avoid;
        }

        /* Chart containers */
        .chart-container {
            background-color: white;
            border: 2px solid #d0d0d0;
            border-radius: 5px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Chart title - optimized for 2-page A4 */
        .chart-title {
            font-family: Arial, sans-serif;
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 3px;
            margin-top: 3px;
            color: #333;
            background: linear-gradient(135deg, #e8e8e8 0%, #f5f5f5 100%);
            padding: 5px;
            border: none;
            border-radius: 3px;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        /* Dashboard title - optimized for 2-page A4 */
        .dashboard-title {
            background-color: #1f4e5f;
            color: white;
            padding: 8px;
            font-size: 13px;
            font-weight: bold;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 8px;
            font-family: Arial, sans-serif;
        }

        /* Remove default streamlit padding - optimized for 2-page A4 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0.8rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
            max-width: 100%;
        }

        /* Hide streamlit elements for clean PDF */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Print optimization for 2-page A4 */
        @media print {
            @page {
                size: A4 portrait;
                margin: 12mm;
            }
            body {
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }
            .page-break-after {
                page-break-after: always;
            }
        }

        /* Streamlit column gap - more breathing room for 2 pages */
        [data-testid="column"] {
            padding: 0px 6px !important;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================
# MAIN DASHBOARD FUNCTION
# ============================================

def falcon_dashboard_pdf_layout():
    """
    Main function to render the single-page PDF-style dashboard
    Uses exact chart logic from pivot_table_builder.py
    """
    # Apply custom CSS
    apply_dashboard_css()

    # ============================
    # SIDEBAR CONFIGURATION
    # ============================
    with st.sidebar:
        st.markdown("### 📝 Dashboard Configuration")
        st.markdown("---")

        # Get current month for default
        current_month = datetime.now().strftime("%B %Y")

        # Editable title
        default_title = f"SafeGuards Secure Solutions - CrowdStrike Falcon Monthly Report ({current_month})"
        dashboard_title = st.text_input(
            "Dashboard Title",
            value=default_title,
            help="Edit the main dashboard title"
        )

        # Confirmation button
        if st.button("✓ Confirm Title", type="secondary", use_container_width=True):
            st.success("✅ Title confirmed!")

        # Warning if using default title - in sidebar
        if dashboard_title == default_title:
            st.warning("⚠️ Using default title. Please confirm or edit above.")

        st.markdown("---")
        st.info("💡 This dashboard uses the exact same visualization logic as the Main Dashboard Report with PDF styling.")
        st.info("📸 Use browser extension 'GoFullPage' for full-page PDF capture")

    # Dashboard Title
    st.markdown(f"""
        <div class="dashboard-title">
            {dashboard_title}
        </div>
    """, unsafe_allow_html=True)

    # Check if data is available
    if not check_data_availability():
        st.warning("⚠️ No data available. Please process your data first using Falcon Data Generator.")
        return

    # Load data from session state
    host_data = st.session_state.get('host_analysis_results', {})
    detection_data = st.session_state.get('detection_analysis_results', {})
    time_data = st.session_state.get('time_analysis_results', {})

    # Extract months dynamically from data
    months = extract_months_from_data(host_data, detection_data, time_data)

    # ============================================
    # SECTION A: HOST SECURITY ANALYSIS
    # ============================================

    st.markdown('<div class="section-header">A. Host Security Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

    # A.1 Overview Detection (full width)
    st.markdown('<div class="chart-title">A.1. Host Overview Detection Across Three Months Trends</div>', unsafe_allow_html=True)
    if 'overview_key_metrics' in host_data:
        create_chart_with_pivot_logic(
            host_data['overview_key_metrics'],
            rows=['Month'],
            columns=['KEY METRICS'],
            values=['Count'],
            chart_type='Bar Chart',
            height=240,
            analysis_key='overview_key_metrics',
            use_monthly_colors=True,
            sort_by='Month'
        )

    # A.2 and A.3 side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-title">A.2. Top Hosts with Most Detections Across Three Months Trends - Top 5</div>', unsafe_allow_html=True)
        if 'overview_top_hosts' in host_data:
            create_chart_with_pivot_logic(
                host_data['overview_top_hosts'],
                rows=['TOP HOSTS WITH MOST DETECTIONS'],
                columns=['Month'],
                values=['Count'],
                chart_type='Bar Chart',
                height=220,
                analysis_key='overview_top_hosts',
                top_n={'enabled': True, 'field': 'TOP HOSTS WITH MOST DETECTIONS', 'n': 5, 'type': 'top', 'by_field': 'Count', 'per_month': False},
                use_monthly_colors=True
            )

    with col2:
        st.markdown('<div class="chart-title">A.3. Users with Most Detections Across Three Months Trends - Top 5</div>', unsafe_allow_html=True)
        if 'user_analysis' in host_data:
            create_chart_with_pivot_logic(
                host_data['user_analysis'],
                rows=['Username'],
                columns=['Month'],
                values=['Count of Detection'],
                chart_type='Bar Chart',
                height=220,
                analysis_key='user_analysis',
                top_n={'enabled': True, 'field': 'Username', 'n': 5, 'type': 'top', 'by_field': 'Count of Detection', 'per_month': False},
                use_monthly_colors=True
            )

    # A.4 Sensor Versions (full width)
    st.markdown('<div class="chart-title">A.4. Detections Hosts with Sensor Versions Status Across Three Months</div>', unsafe_allow_html=True)
    if 'sensor_analysis' in host_data:
        create_chart_with_pivot_logic(
            host_data['sensor_analysis'],
            rows=['Sensor Version', 'Month', 'Status'],
            columns=[],
            values=['Host Count'],
            chart_type='Bar Chart',
            height=240,
            analysis_key='sensor_analysis',
            use_monthly_colors=True
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Close Section A

    # PAGE BREAK AFTER SECTION A (End of Page 1)
    st.markdown('<div class="page-break-after"></div>', unsafe_allow_html=True)

    # ============================================
    # SECTION B: DETECTION AND SEVERITY ANALYSIS
    # ============================================

    st.markdown('<div class="section-header">B. Detection and Severity Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

    # B.1 Critical and High Detection Overview - Side by Side Layout
    st.markdown('<div class="chart-title">B.1. Detection Count by Severity Across Three Months Trends</div>', unsafe_allow_html=True)

    if 'critical_high_overview' in detection_data:
        # Get unique months sorted chronologically
        month_order = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }

        def get_month_sort_key(month_str):
            if pd.isna(month_str):
                return 999
            for month_name, order in month_order.items():
                if month_name in str(month_str):
                    return order
            return 0

        # Get sorted months
        if 'Month' in detection_data['critical_high_overview'].columns:
            months_list = detection_data['critical_high_overview']['Month'].unique()
            months = sorted([m for m in months_list if pd.notna(m)], key=get_month_sort_key)
        else:
            months = ['Single Month']

        # Create two columns: Critical | High
        col_critical, col_high = st.columns(2)

        # LEFT COLUMN: Critical Detections (3 boxes side-by-side horizontally)
        with col_critical:
            st.markdown('<div style="font-size: 10px; font-weight: bold; margin-bottom: 5px; color: #333; text-align: center;">Critical Detections</div>', unsafe_allow_html=True)

            # Monthly color mapping (consistent with chart colors from pivot_table_builder)
            monthly_colors = {
                'July 2025': '#70AD47',      # Green (month_1)
                'August 2025': '#5B9BD5',    # Blue (month_2)
                'September 2025': '#FFC000', # Gold (month_3)
                'Jul 2025': '#70AD47',
                'Aug 2025': '#5B9BD5',
                'Sep 2025': '#FFC000'
            }

            # Build list of box data
            box_data = []
            for month in months:
                # Filter data for Critical Detections in this month
                critical_data = detection_data['critical_high_overview'][
                    (detection_data['critical_high_overview']['KEY METRICS'] == 'Critical Detections') &
                    (detection_data['critical_high_overview']['Month'] == month)
                ]

                # Get count value
                if not critical_data.empty and 'Count' in critical_data.columns:
                    count_value = int(critical_data['Count'].iloc[0])
                else:
                    count_value = 0

                # Get month color
                month_color = monthly_colors.get(str(month), '#7cb342')  # Default to green
                box_data.append((month, count_value, month_color))

            # Create horizontal container for 3 boxes - compact fonts with monthly colors and black text
            boxes_html = '<div style="display: flex; gap: 5px; justify-content: center;">'
            for month, count_value, month_color in box_data:
                boxes_html += f'<div style="background-color: {month_color}; border-radius: 5px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border: 1px solid #d0d0d0; flex: 1; min-width: 60px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 8px; color: #000000; font-weight: 600; margin-bottom: 3px;">{month}</div><div style="font-size: 24px; color: #000000; font-weight: bold; margin: 3px 0;">{count_value}</div><div style="font-size: 7px; color: #000000;">Critical</div></div>'
            boxes_html += '</div>'
            st.markdown(boxes_html, unsafe_allow_html=True)

        # RIGHT COLUMN: High Detections (independent bar chart)
        with col_high:
            st.markdown('<div style="font-size: 10px; font-weight: bold; margin-bottom: 5px; color: #333; text-align: center;">High Detections</div>', unsafe_allow_html=True)

            # Filter for High Detections only
            high_only = detection_data['critical_high_overview'][
                detection_data['critical_high_overview']['KEY METRICS'] == 'High Detections'
            ].copy()

            if not high_only.empty:
                create_chart_with_pivot_logic(
                    high_only,
                    rows=['Month'],
                    columns=[],
                    values=['Count'],
                    chart_type='Bar Chart',
                    height=180,
                    analysis_key='critical_high_overview',
                    use_monthly_colors=True
                )

    # B.2 and B.3 side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-title">B.2. Detection Count by Severity Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'severity_trend' in detection_data:
            create_chart_with_pivot_logic(
                detection_data['severity_trend'],
                rows=['Month'],
                columns=['SeverityName'],
                values=['Count'],
                chart_type='Bar Chart',
                height=220,
                analysis_key='severity_trend',
                use_severity_colors=True
            )

    with col2:
        st.markdown('<div class="chart-title">B.3. Detection Count by Country Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'country_analysis' in detection_data:
            create_chart_with_pivot_logic(
                detection_data['country_analysis'],
                rows=['Country'],
                columns=['Month'],
                values=['Detection Count'],
                chart_type='Bar Chart',
                height=220,
                analysis_key='country_analysis',
                use_monthly_colors=True
            )

    # B.4 Files (bar chart with filename on x-axis)
    st.markdown('<div class="chart-title">B.4. File Name with Most Detections Across Three Months Trends - Top 5</div>', unsafe_allow_html=True)
    if 'file_analysis' in detection_data:
        create_chart_with_pivot_logic(
            detection_data['file_analysis'],
            rows=['File Name'],
            columns=['Month'],
            values=['Detection Count'],
            chart_type='Bar Chart',
            height=260,
            analysis_key='file_analysis',
            top_n={'enabled': True, 'field': 'File Name', 'n': 5, 'type': 'top', 'by_field': 'Detection Count', 'per_month': False},
            use_monthly_colors=True
        )

    # B.5 and B.6 side by side
    col1, col2 = st.columns(2)

    with col1:
        # B.5 Tactics (area chart)
        st.markdown('<div class="chart-title">B.5. Tactics by Severity Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'tactics_by_severity' in detection_data:
            create_chart_with_pivot_logic(
                detection_data['tactics_by_severity'],
                rows=['Month', 'SeverityName'],
                columns=['Tactic'],
                values=['Count'],
                chart_type='Area Chart',
                height=300,
                analysis_key='tactics_by_severity',
                use_severity_colors=True,
                use_monthly_colors=True
            )

    with col2:
        # B.6 Technique (area chart)
        st.markdown('<div class="chart-title">B.6. Technique by Severity Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'technique_by_severity' in detection_data:
            # Pre-sort data to put Adware/PUP first
            technique_df = detection_data['technique_by_severity'].copy()
            if 'Technique' in technique_df.columns:
                # Create sort key: Adware/PUP first, then by total count descending
                def sort_key(tech):
                    if pd.notna(tech) and 'Adware' in str(tech).upper() or 'PUP' in str(tech).upper():
                        return (0, str(tech))  # Priority 0 for Adware/PUP
                    return (1, str(tech))  # Priority 1 for others

                # Calculate totals and sort
                tech_totals = technique_df.groupby('Technique')['Count'].sum().reset_index()
                tech_totals['sort_key'] = tech_totals['Technique'].apply(lambda x: (0 if (pd.notna(x) and ('Adware' in str(x) or 'PUP' in str(x))) else 1, -tech_totals[tech_totals['Technique']==x]['Count'].iloc[0] if len(tech_totals[tech_totals['Technique']==x]) > 0 else 0))

            create_chart_with_pivot_logic(
                technique_df,
                rows=['Month', 'SeverityName'],
                columns=['Technique'],
                values=['Count'],
                chart_type='Area Chart',
                height=300,
                analysis_key='technique_by_severity_b6',  # Unique key for B.6
                top_n={'enabled': True, 'field': 'Technique', 'n': 10, 'type': 'top', 'by_field': 'Count', 'per_month': False},
                use_severity_colors=True,
                use_monthly_colors=True
            )

    st.markdown('</div>', unsafe_allow_html=True)  # Close Section B

    # ============================================
    # SECTION C: TIME-BASED ANALYSIS
    # ============================================

    st.markdown('<div class="section-header">C. Time-Based Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

    # C.1 Daily Trend (full width) - Use exact same logic as pivot table builder
    st.markdown('<div class="chart-title">C.1. Detection Over Multiple Days Across Three Months Trends - Top 3</div>', unsafe_allow_html=True)
    if 'daily_trends' in time_data:
        # Pre-process to remove month prefix from Date labels
        daily_df = time_data['daily_trends'].copy()
        if 'Date' in daily_df.columns:
            # Extract just the date part after the month name (e.g., "June Wed Jun 04 2025" -> "Wed Jun 04 2025")
            daily_df['Date'] = daily_df['Date'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else str(x))

        create_chart_with_pivot_logic(
            daily_df,
            rows=['Date', 'Month'],
            columns=[],
            values=['Detection Count'],
            chart_type='Bar Chart',
            height=240,
            analysis_key='daily_trends',
            top_n={'enabled': True, 'field': 'Date', 'n': 3, 'type': 'top', 'by_field': 'Detection Count', 'per_month': True},
            use_monthly_colors=True
        )

    # C.2 and C.3 side by side - EXACT SAME STYLING as pivot table builder
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-title">C.2. Hourly Distribution of Detections Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'hourly_analysis' in time_data:
            create_chart_with_pivot_logic(
                time_data['hourly_analysis'],
                rows=['Hour'],
                columns=[],
                values=['Detection Count'],
                chart_type='Line Chart',
                height=220,
                analysis_key='hourly_analysis',
                use_monthly_colors=False,
                sort_by='Hour',
                sort_direction='descending'
            )

    with col2:
        st.markdown('<div class="chart-title">C.3. Detection Frequency by Day of Week Across Three Months Trends</div>', unsafe_allow_html=True)
        if 'day_of_week' in time_data:
            create_chart_with_pivot_logic(
                time_data['day_of_week'],
                rows=['Day', 'Type'],
                columns=[],
                values=['Detection Count'],
                chart_type='Bar Chart',
                height=220,
                analysis_key='day_of_week',
                use_monthly_colors=False,
                sort_by='Day',
                sort_direction='descending'  # Descending gives Monday→Sunday due to (not sort_ascending) logic
            )

    st.markdown('</div>', unsafe_allow_html=True)  # Close Section C


def create_chart_with_pivot_logic(df, rows, columns, values, chart_type, height, analysis_key, top_n=None, use_severity_colors=False, use_monthly_colors=False, sort_by=None, sort_direction='descending'):
    """
    Create chart using the EXACT same logic as pivot_table_builder.py
    This ensures consistency across all dashboards
    """
    # Create config dict (same structure as pivot_table_builder)
    config = {
        'rows': rows,
        'columns': columns,
        'values': values,
        'aggregation': 'sum',
        'chart_type': chart_type,
        'sort_by_field': sort_by if sort_by else 'Value (Detection Count)',
        'chart_sort_direction': sort_direction,
        'filters': {},
        'top_n': top_n,
        'use_severity_colors': use_severity_colors,
        'use_monthly_colors': use_monthly_colors
    }
    
    try:
        # Apply TOP N filter if specified (before creating pivot)
        filtered_df = df.copy()
        
        if top_n and top_n.get('enabled'):
            filter_field = top_n['field']
            n_value = top_n['n']
            filter_type = top_n['type']
            by_field = top_n['by_field']
            per_month = top_n.get('per_month', False)
            
            if filter_field in filtered_df.columns and by_field in filtered_df.columns:
                if per_month and 'Month' in filtered_df.columns:
                    # Apply Top N per month
                    all_top_items = []
                    months = filtered_df['Month'].unique()
                    
                    for month in months:
                        month_df = filtered_df[filtered_df['Month'] == month]
                        totals = month_df.groupby(filter_field)[by_field].sum().reset_index()
                        totals = totals.rename(columns={by_field: '_total'})
                        
                        if filter_type == 'top':
                            top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                        else:
                            top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()
                        
                        for item in top_items:
                            all_top_items.append((month, item))
                    
                    filtered_df = filtered_df[
                        filtered_df.apply(lambda row: (row['Month'], row[filter_field]) in all_top_items, axis=1)
                    ]
                else:
                    # Global Top N filtering
                    totals = filtered_df.groupby(filter_field)[by_field].sum().reset_index()
                    totals = totals.rename(columns={by_field: '_total'})
                    
                    if filter_type == 'top':
                        top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                    else:
                        top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()
                    
                    filtered_df = filtered_df[filtered_df[filter_field].isin(top_items)]
        
        # Create pivot table using the exact function from pivot_table_builder
        pivot_table = create_pivot_table(filtered_df, config, analysis_key)

        if pivot_table is not None and not pivot_table.empty:
            # Create chart using the exact function from pivot_table_builder
            chart = create_pivot_chart(pivot_table, chart_type, height, config, analysis_key)

            if chart:
                # Apply PDF-specific styling to the chart
                apply_pdf_chart_styling(chart, analysis_key)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("⚠️ Could not create chart for this analysis")
        else:
            st.warning("⚠️ No data available for this analysis")
            
    except Exception as e:
        st.error(f"❌ Error creating chart: {str(e)}")
        st.info("💡 This might be due to missing or incompatible data fields")


def apply_pdf_chart_styling(chart, analysis_key=None):
    """
    Apply PDF-specific styling to charts:
    - Chart Titles: Arial 14pt bold
    - Axes/Labels/Legends: Arial 12pt
    - Data Labels: Black text on white background boxes, Arial 12pt, outside end
    """
    if chart is None:
        return

    # Preserve existing axis titles (e.g., "Total Tactics Count", "Total Technique Count")
    existing_xaxis_title = chart.layout.xaxis.title.text if chart.layout.xaxis.title else None
    existing_yaxis_title = chart.layout.yaxis.title.text if chart.layout.yaxis.title else None

    # Add specific x-axis titles for B.5 and B.6
    if analysis_key == 'tactics_by_severity':
        existing_xaxis_title = 'Tactic'
    elif analysis_key == 'technique_by_severity_b6':
        existing_xaxis_title = 'Technique'

    # Determine legend font size (larger for 2-page layout, smaller for B.6)
    legend_font_size = 9 if analysis_key == 'technique_by_severity_b6' else 11

    # Update layout with PDF fonts - optimized for 2-page readability
    chart.update_layout(
        # Remove chart title completely (we use HTML titles above charts instead)
        title='',
        showlegend=True,
        # Axes: Arial 11pt
        xaxis=dict(
            title=existing_xaxis_title,
            title_font=dict(family='Arial', size=11, color='#333333'),
            tickfont=dict(family='Arial', size=10, color='#333333')
        ),
        yaxis=dict(
            title=existing_yaxis_title,
            title_font=dict(family='Arial', size=11, color='#333333'),
            tickfont=dict(family='Arial', size=10, color='#333333')
        ),
        # Legend: Arial 11pt (9pt for B.6), positioned at right side
        legend=dict(
            font=dict(family='Arial', size=legend_font_size, color='#333333'),
            traceorder='reversed',  # Show highest values at top
            itemsizing='constant'   # Prevent scrolling
        ),
        # Uniform styling - readable
        font=dict(
            family='Arial',
            size=11,
            color='#333333'
        ),
        # Better margins for 2-page layout
        margin=dict(
            l=45,
            r=40,
            t=15,
            b=45
        )
    )

    # Update traces individually based on chart type
    for i, trace in enumerate(chart.data):
        if trace.type == 'bar':
            # Bar charts: Show data labels outside with black text
            # Get the values (y for vertical bars, x for horizontal bars)
            if hasattr(trace, 'orientation') and trace.orientation == 'h':
                # Horizontal bars (like B.4 Files)
                values = trace.x if hasattr(trace, 'x') else []
            else:
                # Vertical bars
                values = trace.y if hasattr(trace, 'y') else []

            # Hide labels for zero values - set empty string for zeros
            text_values = []
            for val in values:
                if val is not None and val != 0:
                    text_values.append(str(int(val)) if isinstance(val, (int, float)) else str(val))
                else:
                    text_values.append('')  # Empty string for zero or None

            trace.update(
                text=text_values,
                textposition='outside',
                textfont=dict(
                    family='Arial',
                    size=10,
                    color='#000000'
                ),
                cliponaxis=False
            )
        elif trace.type in ['scatter', 'scattergl']:
            # Line/Scatter charts: Show values on top of markers
            if trace.mode and 'markers' in trace.mode:
                # Get y values for text labels
                y_values = trace.y if hasattr(trace, 'y') else []
                text_values = [str(int(val)) if isinstance(val, (int, float)) and val != 0 else '' for val in y_values]

                trace.update(
                    text=text_values,
                    textfont=dict(
                        family='Arial',
                        size=10,
                        color='#000000'
                    ),
                    textposition='top center',
                    mode='lines+markers+text'
                )


def check_data_availability() -> bool:
    """Check if required data is available in session state"""
    return (
        'host_analysis_results' in st.session_state or
        'detection_analysis_results' in st.session_state or
        'time_analysis_results' in st.session_state
    )


def extract_months_from_data(host_data, detection_data, time_data):
    """Extract month names from available data"""
    months = []

    # Try to get months from different data sources
    if host_data and 'overview_key_metrics' in host_data:
        df = host_data['overview_key_metrics']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    if not months and detection_data and 'severity_trend' in detection_data:
        df = detection_data['severity_trend']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    if not months and time_data and 'daily_trends' in time_data:
        df = time_data['daily_trends']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    # Default fallback
    if not months:
        months = ['Month 1', 'Month 2', 'Month 3']

    return months[:3]  # Limit to 3 months


if __name__ == "__main__":
    falcon_dashboard_pdf_layout()
