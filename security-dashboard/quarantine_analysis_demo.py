"""
Quarantined File Analysis Dashboard - Standalone Demo
Test interface for quarantine file analysis feature

Run with: streamlit run quarantine_analysis_demo.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from quarantine_file_analysis import (
    parse_quarantine_json,
    generate_quarantine_analysis,
    create_sample_quarantine_json,
    validate_quarantine_json
)
from host_analysis import centered_table_css
from theme_utils import setup_theme
import matplotlib.pyplot as plt

def quarantine_analysis_dashboard():
    """Main dashboard for quarantine file analysis"""

    # Apply theme and CSS
    plt_style = setup_theme()
    plt.style.use(plt_style)
    st.markdown(centered_table_css(), unsafe_allow_html=True)

    st.title("🔒 Quarantined File Analysis Dashboard")
    st.markdown("### Analyze Falcon quarantine data to identify threats and affected systems")
    st.markdown("<div style='text-align:right; color:gray; font-size:12px;'>developed by Izami Ariff © 2025</div>", unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        report_period = st.text_input("Report Period", "February 2025")

        st.markdown("### 📁 Upload Quarantine Data")
        st.info("Upload a JSON file containing Falcon quarantine data")

        uploaded_file = st.file_uploader(
            "Choose JSON file",
            type=['json'],
            help="Upload JSON file with quarantine data"
        )

        # Option to use sample data
        st.markdown("### 🧪 Test with Sample Data")
        if st.button("Load Sample Data"):
            sample_data = create_sample_quarantine_json(30)
            st.session_state['quarantine_data'] = sample_data
            st.success("✅ Sample data loaded!")
            st.rerun()

        # Download sample template
        if st.button("📥 Download Sample JSON"):
            sample_data = create_sample_quarantine_json(5)
            json_str = json.dumps(sample_data, indent=2)
            st.download_button(
                label="Download",
                data=json_str,
                file_name="quarantine_sample.json",
                mime="application/json"
            )

        # Visualization settings
        with st.expander("📊 Visualization Settings"):
            st.markdown("### Chart Colors")
            monthly_chart_color = st.color_picker("Monthly Trend", "#3498db")
            file_chart_color = st.color_picker("File Analysis", "#2ecc71")
            host_chart_color = st.color_picker("Host Analysis", "#f39c12")

            st.markdown("### Display Options")
            show_top_n = st.slider("Show Top N Items", 5, 20, 10)
            show_percentages = st.checkbox("Show Percentages", value=True)

    # Main content area
    if uploaded_file is None and 'quarantine_data' not in st.session_state:
        st.info("👈 Please upload a JSON file or load sample data from the sidebar")

        st.markdown("""
        ### Welcome to Quarantined File Analysis

        This dashboard analyzes Falcon quarantine data to help you:
        - Track quarantined files over time
        - Identify most affected hosts and users
        - Understand threat patterns
        - Generate comprehensive reports

        **To get started:**
        1. Upload your Falcon quarantine JSON file, OR
        2. Click "Load Sample Data" to test with sample data
        3. View the analysis and insights

        **Required JSON Format:**
        ```json
        [
          {
            "Date of Quarantine": "2026-02-12T07:12:55Z",
            "File Name": "malware.exe",
            "Hostname": "DESKTOP-001",
            "Agent ID": "d26758",
            "User": "john.doe",
            "Status": "quarantined"
          }
        ]
        ```
        """)
        return

    # Process uploaded file
    quarantine_data = None

    if uploaded_file is not None:
        try:
            # Read JSON file
            json_data = json.load(uploaded_file)

            # Validate JSON
            validation = validate_quarantine_json(json_data)

            if not validation['is_valid']:
                st.error("❌ Invalid JSON file!")
                for error in validation['errors']:
                    st.error(f"• {error}")
                return

            if validation['warnings']:
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")

            st.success(f"✅ File validated successfully! Found {validation['record_count']} records")
            quarantine_data = json_data

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return

    elif 'quarantine_data' in st.session_state:
        quarantine_data = st.session_state['quarantine_data']
        st.success(f"✅ Using loaded sample data ({len(quarantine_data)} records)")

    # Parse and analyze data
    try:
        # Parse JSON into DataFrame
        df = parse_quarantine_json(quarantine_data)

        # Generate analysis
        results = generate_quarantine_analysis(df)

        # Display dashboard
        st.markdown(f"<h2 class='sub-header'>Quarantine Overview - {report_period}</h2>", unsafe_allow_html=True)

        # Overview metrics
        overview = results['overview']
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Quarantined", overview['total_quarantined'])
        with col2:
            st.metric("Unique Files", overview['unique_files'])
        with col3:
            st.metric("Affected Hosts", overview['unique_hosts'])
        with col4:
            st.metric("Affected Users", overview['unique_users'])

        # Date range
        date_range = overview['date_range']
        st.info(f"📅 Data Range: {date_range['start'].strftime('%d/%m/%Y')} to {date_range['end'].strftime('%d/%m/%Y')}")

        # 1. Monthly Trend Bar Chart
        st.markdown("<h3>📊 Monthly Quarantine Trend</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="definition-card">
            <h4>Monthly Quarantine Count</h4>
            <p><strong>Definition:</strong> Shows the number of files quarantined each month.</p>
            <p><strong>Use Case:</strong> Identify trends in malware detection and assess if security incidents are increasing or decreasing over time.</p>
        </div>
        """, unsafe_allow_html=True)

        monthly_counts = results['monthly_counts']

        fig_monthly = go.Figure(data=[go.Bar(
            x=monthly_counts['Month Name'],
            y=monthly_counts['Count'],
            marker_color=monthly_chart_color,
            text=monthly_counts['Count'],
            textposition='outside'
        )])

        fig_monthly.update_layout(
            title='Files Quarantined by Month',
            xaxis_title='Month',
            yaxis_title='Number of Files Quarantined',
            height=400
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

        # Key insight
        max_month = monthly_counts.loc[monthly_counts['Count'].idxmax()]
        st.info(f"🔍 Peak quarantine activity occurred in **{max_month['Month Name']}** with **{max_month['Count']}** files quarantined.")

        # 2. Top Quarantined Files Summary
        st.markdown("<h3>🦠 Most Quarantined Files</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="definition-card">
            <h4>File Quarantine Summary</h4>
            <p><strong>Definition:</strong> Lists the files that have been quarantined most frequently across all hosts.</p>
            <p><strong>Use Case:</strong> Identify persistent threats that are appearing across multiple systems and may require additional security measures.</p>
        </div>
        """, unsafe_allow_html=True)

        detailed_files = results['detailed_file_summary'].head(show_top_n)

        # Bar chart for top files
        fig_files = go.Figure(data=[go.Bar(
            y=detailed_files['File Name'],
            x=detailed_files['Quarantine Count'],
            orientation='h',
            marker_color=file_chart_color,
            text=detailed_files['Quarantine Count'],
            textposition='outside'
        )])

        fig_files.update_layout(
            title=f'Top {show_top_n} Most Quarantined Files',
            xaxis_title='Quarantine Count',
            yaxis_title='File Name',
            height=400
        )

        st.plotly_chart(fig_files, use_container_width=True)

        # Detailed file table
        st.markdown(f"<h4>📋 Detailed File Summary (Top {show_top_n})</h4>", unsafe_allow_html=True)
        st.markdown("**Specific files and hosts that were affected:**")

        # Format the display table
        display_files = detailed_files.copy()
        if show_percentages:
            total_quarantines = overview['total_quarantined']
            display_files['Percentage'] = (display_files['Quarantine Count'] / total_quarantines * 100).round(1)
            display_files['Percentage'] = display_files['Percentage'].astype(str) + '%'

        st.dataframe(
            display_files[['File Name', 'Quarantine Count', 'Affected Hosts', 'Hosts List', 'First Seen', 'Last Seen'] +
                         (['Percentage'] if show_percentages else [])],
            use_container_width=True
        )

        # 3. Most Affected Hosts Summary
        st.markdown("<h3>💻 Most Affected Hosts</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="definition-card">
            <h4>Host Impact Summary</h4>
            <p><strong>Definition:</strong> Shows the hosts that have had the most files quarantined.</p>
            <p><strong>Use Case:</strong> Identify compromised or high-risk systems that may need additional investigation, reimaging, or enhanced security controls.</p>
        </div>
        """, unsafe_allow_html=True)

        detailed_hosts = results['detailed_host_summary'].head(show_top_n)

        # Bar chart for top hosts
        fig_hosts = go.Figure(data=[go.Bar(
            y=detailed_hosts['Hostname'],
            x=detailed_hosts['Total Quarantines'],
            orientation='h',
            marker_color=host_chart_color,
            text=detailed_hosts['Total Quarantines'],
            textposition='outside'
        )])

        fig_hosts.update_layout(
            title=f'Top {show_top_n} Most Affected Hosts',
            xaxis_title='Total Quarantines',
            yaxis_title='Hostname',
            height=400
        )

        st.plotly_chart(fig_hosts, use_container_width=True)

        # Detailed host table
        st.markdown(f"<h4>📋 Detailed Host Summary (Top {show_top_n})</h4>", unsafe_allow_html=True)
        st.markdown("**Specific hosts and files that were affected:**")

        # Format the display table
        display_hosts = detailed_hosts.copy()
        if show_percentages:
            total_quarantines = overview['total_quarantined']
            display_hosts['Percentage'] = (display_hosts['Total Quarantines'] / total_quarantines * 100).round(1)
            display_hosts['Percentage'] = display_hosts['Percentage'].astype(str) + '%'

        st.dataframe(
            display_hosts[['Hostname', 'Total Quarantines', 'Unique Files', 'Primary User', 'Files', 'Last Activity'] +
                         (['Percentage'] if show_percentages else [])],
            use_container_width=True
        )

        # 4. Status Distribution
        st.markdown("<h3>📊 Quarantine Status Distribution</h3>", unsafe_allow_html=True)

        status_dist = results['status_distribution']

        fig_status = px.pie(
            status_dist,
            values='Count',
            names='Status',
            title='Quarantine Status Breakdown',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_status.update_traces(textinfo='percent+label', textfont_size=14)
        st.plotly_chart(fig_status, use_container_width=True)

        # Executive Summary
        st.markdown("<h2>📋 Executive Summary</h2>", unsafe_allow_html=True)

        # Generate summary
        top_file = detailed_files.iloc[0] if not detailed_files.empty else None
        top_host = detailed_hosts.iloc[0] if not detailed_hosts.empty else None

        summary_text = f"""• During {report_period}, a total of **{overview['total_quarantined']} files** were quarantined across **{overview['unique_hosts']} unique hosts**, affecting **{overview['unique_users']} users**.
• The most frequently quarantined file is **"{top_file['File Name']}"** with **{top_file['Quarantine Count']} instances** across **{top_file['Affected Hosts']} hosts**.
• The most affected host is **"{top_host['Hostname']}"** with **{top_host['Total Quarantines']} quarantined files** ({top_host['Unique Files']} unique files), primarily used by **{top_host['Primary User']}**.
• Peak quarantine activity occurred in **{max_month['Month Name']}** with **{max_month['Count']} files** quarantined, indicating a potential security event or campaign during this period.
• Immediate remediation is recommended for the top {show_top_n} affected hosts to prevent further compromise and reduce organizational risk."""

        formatted_summary = summary_text.replace('• ', '<li>').replace('\n• ', '</li><li>')

        st.markdown(f"""
        <div class="executive-summary-blue">
            <ul class="summary-bullet">
                {formatted_summary}
            </li></ul>
        </div>
        """, unsafe_allow_html=True)

        # Export options
        st.markdown("---")
        st.markdown("### 📥 Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Export detailed files
            csv_files = detailed_files.to_csv(index=False)
            st.download_button(
                label="📄 Export Files Summary (CSV)",
                data=csv_files,
                file_name=f"quarantine_files_{report_period}.csv",
                mime="text/csv"
            )

        with col2:
            # Export detailed hosts
            csv_hosts = detailed_hosts.to_csv(index=False)
            st.download_button(
                label="💻 Export Hosts Summary (CSV)",
                data=csv_hosts,
                file_name=f"quarantine_hosts_{report_period}.csv",
                mime="text/csv"
            )

        with col3:
            # Export raw data
            csv_raw = df.to_csv(index=False)
            st.download_button(
                label="📊 Export Raw Data (CSV)",
                data=csv_raw,
                file_name=f"quarantine_raw_data_{report_period}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return


if __name__ == "__main__":
    st.set_page_config(
        page_title="Quarantine Analysis Dashboard",
        page_icon="🔒",
        layout="wide"
    )
    quarantine_analysis_dashboard()
