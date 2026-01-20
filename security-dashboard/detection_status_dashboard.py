"""
Detection Status Dashboard
Displays detection analysis by Status and Severity

Developed by Izami Ariff © 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def detection_status_dashboard():
    """Display detection status analysis results"""

    st.title("📊 Detection Status Analysis")
    st.markdown("**Analyze detections by Status and Severity level**")
    st.markdown("---")

    # Check if analysis results exist
    if 'detection_status_results' not in st.session_state:
        st.warning("⚠️ No detection status data available.")
        st.info("""
        **To use this dashboard:**
        1. Go to **Falcon Data Generator**
        2. Enable **"Include Detection Status Analysis"**
        3. Upload CSV files with Status, SeverityName, and Request ID columns
        4. Process the data
        5. Return here to view the analysis
        """)

        # Show sample format
        with st.expander("📖 View Required CSV Format"):
            st.markdown("""
            **Required Columns:**
            - `Status`: Detection status (closed, in_progress, open, pending, on-hold)
            - `SeverityName`: Severity level (Critical, High, Medium, Low)
            - `Request ID`: Detection identifier

            **Sample Data:**
            ```
            Status,SeverityName,Request ID
            closed,Critical,503528
            closed,High,503457
            in_progress,Medium,513757
            open,High,503900
            ```
            """)
        return

    # Get results
    results = st.session_state['detection_status_results']

    # Month selector
    months = list(results.keys())
    selected_month = st.selectbox("📅 Select Month", months)

    if selected_month not in results:
        st.error(f"No data available for {selected_month}")
        return

    month_data = results[selected_month]

    # Display metrics
    st.markdown(f"## {selected_month}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Detections",
            month_data['total_detections'],
            help="Total number of detections in this period"
        )

    with col2:
        closure_rate = month_data['metrics']['closure_rate']
        st.metric(
            "Closure Rate",
            f"{closure_rate:.1f}%",
            help="Percentage of closed detections"
        )

    with col3:
        critical_closed = month_data['metrics']['critical_closed']
        high_closed = month_data['metrics']['high_closed']
        st.metric(
            "Critical/High Closed",
            f"{critical_closed + high_closed}",
            help="Critical and High severity detections that are closed"
        )

    with col4:
        critical_open = month_data['metrics']['critical_open']
        high_open = month_data['metrics']['high_open']
        st.metric(
            "Critical/High Open",
            f"{critical_open + high_open}",
            delta=f"-{critical_open + high_open}",
            delta_color="inverse",
            help="Critical and High severity detections still open or in progress"
        )

    st.markdown("---")

    # Pivot Table
    st.markdown(f"### 📋 Total Detections Count by Status and Severity for {selected_month}")

    pivot_df = month_data['pivot_table']

    # Style the dataframe
    def style_pivot_table(val):
        if isinstance(val, (int, float)):
            if val == 0:
                return 'background-color: #f0f0f0; color: #999999'
            elif val > 10:
                return 'background-color: #ffcccc; font-weight: bold'
            elif val > 5:
                return 'background-color: #ffffcc'
        return ''

    styled_df = pivot_df.style.applymap(style_pivot_table)

    st.dataframe(styled_df, use_container_width=True)

    # Chart
    st.markdown(f"### 📊 Detection Status Count by Status and Severity for {selected_month}")

    chart_data = month_data['chart_data']

    # Create stacked bar chart
    fig = go.Figure()

    # Color mapping for severities
    severity_colors = {
        'Critical': '#DC143C',  # Red
        'High': '#FF8C00',      # Orange
        'Medium': '#4169E1',    # Blue
        'Low': '#70AD47'        # Green
    }

    # Get unique statuses and severities
    statuses = chart_data['Status'].unique()
    severities = ['Critical', 'High', 'Medium', 'Low']

    # Add bars for each severity
    for severity in severities:
        severity_data = chart_data[chart_data['SeverityName'] == severity]

        # Create data for all statuses (fill with 0 if missing)
        counts = []
        for status in statuses:
            status_data = severity_data[severity_data['Status'] == status]
            if len(status_data) > 0:
                counts.append(status_data['Count'].values[0])
            else:
                counts.append(0)

        fig.add_trace(go.Bar(
            name=severity,
            x=statuses,
            y=counts,
            marker_color=severity_colors.get(severity, '#999999'),
            text=counts,
            textposition='inside',
            textfont=dict(color='white', size=12),
            hovertemplate=f'<b>{severity}</b><br>Status: %{{x}}<br>Count: %{{y}}<extra></extra>'
        ))

    fig.update_layout(
        barmode='stack',
        title=dict(
            text=f"Total Detections Count by Status and Severity for {selected_month}",
            font=dict(size=16)
        ),
        xaxis_title="Detection Request Status",
        yaxis_title="Number of Detections",
        height=500,
        showlegend=True,
        legend=dict(
            title="Severity",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Breakdown by Status
    st.markdown("---")
    st.markdown("### 📈 Status Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Detections by Status**")
        status_counts = month_data['status_counts']

        # Create pie chart
        fig_status = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.3,
            marker=dict(
                colors=['#70AD47', '#FFC000', '#DC143C', '#A9A9A9']
            ),
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig_status.update_layout(
            title="Distribution by Status",
            height=400
        )

        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("**Detections by Severity**")
        severity_counts = month_data['severity_counts']

        # Create pie chart
        fig_severity = go.Figure(data=[go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            hole=0.3,
            marker=dict(
                colors=[severity_colors.get(k, '#999999') for k in severity_counts.keys()]
            ),
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig_severity.update_layout(
            title="Distribution by Severity",
            height=400
        )

        st.plotly_chart(fig_severity, use_container_width=True)

    # Export options
    st.markdown("---")
    st.markdown("### 💾 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        # Export pivot table to CSV
        csv = pivot_df.to_csv()
        st.download_button(
            label="📥 Download Pivot Table (CSV)",
            data=csv,
            file_name=f"detection_status_{selected_month.replace(' ', '_')}.csv",
            mime="text/csv"
        )

    with col2:
        # Export raw data
        raw_csv = month_data['raw_data'].to_csv(index=False)
        st.download_button(
            label="📥 Download Raw Data (CSV)",
            data=raw_csv,
            file_name=f"detection_status_raw_{selected_month.replace(' ', '_')}.csv",
            mime="text/csv"
        )
