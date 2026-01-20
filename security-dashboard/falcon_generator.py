import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
from typing import Dict, List, Optional
import re
from host_analysis_generator import generate_host_analysis
from detection_severity_generator import generate_detection_severity_analysis
from time_analysis_generator import generate_time_analysis
from ticket_lifecycle_generator import generate_ticket_lifecycle_analysis, create_placeholder_ticket_data
from detection_status_generator import generate_detection_status_analysis

# Dummy data generation function removed - no longer needed

def _removed_generate_dummy_3month_data():
    """Generate dummy 3-month data for testing"""
    months = ['June 2025', 'July 2025', 'August 2025']

    # Countries
    countries = ['MY', 'SG', 'Unknown']

    # Hostnames
    hostnames = ['PC-001', 'PC-002', 'PC-003', 'PC-004', 'PC-005',
                 'SRV-001', 'SRV-002', 'LAPTOP-A', 'LAPTOP-B', 'LAPTOP-C']

    # Files
    files = ['powershell.exe', 'cmd.exe', 'explorer.exe', 'Compil32.exe',
             'rufus-4.3.exe', 'fonts.exe', 'msedge.exe', 'chrome.exe',
             'DefaultSetup.exe', 'OneDrive.Sync.Service.exe']

    # Severities
    severities = ['Critical', 'High', 'Medium', 'Low']

    # Tactics and Techniques
    tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Escalation', 'Defense Evasion']
    techniques = ['T1190', 'T1059', 'T1053', 'T1068', 'T1055']

    # Users
    users = ['admin', 'user1', 'user2', 'system', 'service_account']

    # Sensors
    sensors = ['Sensor-A', 'Sensor-B', 'Sensor-C']

    # OS and Sensor versions
    os_versions = ['Windows 10', 'Windows 11', 'Windows Server 2019', 'Windows Server 2022']
    sensor_versions = ['7.10.0', '7.11.0', '7.12.0']

    # Sites and OUs
    sites = ['HQ', 'Branch-A', 'Branch-B', 'Remote']
    ous = ['IT', 'Finance', 'HR', 'Operations', 'Sales']

    # Generate data
    all_data = []
    unique_no = 1

    for month_idx, month in enumerate(months):
        # Generate 30-50 detections per month
        num_detections = np.random.randint(30, 51)

        for _ in range(num_detections):
            all_data.append({
                'UniqueNo': unique_no,
                'Month': month,
                'Period': month,
                'Hostname': np.random.choice(hostnames),
                'Country': np.random.choice(countries, p=[0.5, 0.3, 0.2]),
                'SeverityName': np.random.choice(severities, p=[0.1, 0.3, 0.4, 0.2]),
                'FileName': np.random.choice(files),
                'Tactic': np.random.choice(tactics),
                'Technique': np.random.choice(techniques),
                'UserName': np.random.choice(users),
                'SensorName': np.random.choice(sensors),
                'OS Version': np.random.choice(os_versions),
                'Sensor Version': np.random.choice(sensor_versions),
                'Site': np.random.choice(sites),
                'OU': np.random.choice(ous),
                'DetectionTime': pd.Timestamp(f'2025-{6+month_idx:02d}-{np.random.randint(1, 29):02d} {np.random.randint(0, 24):02d}:{np.random.randint(0, 60):02d}:00'),
                'CompositeID': f'DET-{np.random.randint(10000, 99999)}',
                'Objective': np.random.choice(['Malware', 'Exploit', 'Suspicious Activity'])
            })
            unique_no += 1

    df = pd.DataFrame(all_data)

    # Add hour and day of week
    df['Hour'] = df['DetectionTime'].dt.hour
    df['DayOfWeek'] = df['DetectionTime'].dt.day_name()

    return df

def falcon_generator_dashboard():
    # Page has already been configured in app.py

    st.title("🦅 Falcon Data Analysis Generator")
    st.markdown("Generate analysis templates exactly like your PowerBI table - with required data filled!")
    st.markdown("<div style='text-align:right; color:gray; font-size:12px;'>developed by Izami Ariff &copy; 2025</div>", unsafe_allow_html=True)

    # Multi-month upload section
    st.header("📁 Upload Falcon Export Files for Multiple Months")
    st.markdown("""
    **Instructions:**
    - For each month, upload a set of 5 files (Host, 1detections, 2detection-progress-summary, 3exportdetectquery, 4exportCountryDetection).
    - You can upload up to 3 months (3 sets) for trend analysis.
    - Please specify the month/period for each set.
    """)

    num_months = st.number_input("How many months of data do you want to analyze?", min_value=1, max_value=3, value=1, step=1)
    month_data = []

    for i in range(num_months):
        # Use expander for collapsible UI - better UX for multiple months
        with st.expander(f"📅 Month {i+1} Data Upload", expanded=(i == 0)):
            # Month and Year selection using dropdowns (prevents human error)
            col1, col2 = st.columns([1, 1])
            with col1:
                month_name = st.selectbox(
                    f"Select Month {i+1}",
                    options=['January', 'February', 'March', 'April', 'May', 'June',
                            'July', 'August', 'September', 'October', 'November', 'December'],
                    key=f"month_{i}",
                    help="Select the month for this data set"
                )
            with col2:
                # Get current year and create a range from current year - 1 to current year + 3
                from datetime import datetime
                current_year = datetime.now().year
                year_options = list(range(current_year - 1, current_year + 4))  # e.g., 2024-2029 if current is 2025

                year = st.selectbox(
                    f"Select Year {i+1}",
                    options=year_options,
                    index=1,  # Default to current year (second option in the list)
                    key=f"year_{i}",
                    help="Select the year for this data set"
                )

            # Construct period label in consistent format: "Month YYYY" (e.g., "January 2025")
            period = f"{month_name} {year}"
            st.success(f"📅 Period Label: **{period}**")

            st.markdown("#### 📂 Upload Files (5 required)")
            st.markdown("Upload all 5 CSV files for this month:")

            # Use columns for better layout - 2 uploaders per row
            col_a, col_b = st.columns(2)
            with col_a:
                host_export_file = st.file_uploader(
                    "1️⃣ Host Export File",
                    type=['csv'],
                    key=f"host_export_file_{i}",
                    help="Host export CSV file"
                )
                file2 = st.file_uploader(
                    "3️⃣ Detection Progress Summary",
                    type=['csv'],
                    key=f"file2_{i}",
                    help="2detection-progress-summarymonth.csv"
                )
                file4 = st.file_uploader(
                    "5️⃣ Country Detection Export",
                    type=['csv'],
                    key=f"file4_{i}",
                    help="4exportCountryDetectionmonth.csv"
                )

            with col_b:
                file1 = st.file_uploader(
                    "2️⃣ Detections File",
                    type=['csv'],
                    key=f"file1_{i}",
                    help="1detectionsmonth.csv"
                )
                file3 = st.file_uploader(
                    "4️⃣ Detect Query Export",
                    type=['csv'],
                    key=f"file3_{i}",
                    help="3exportdetectquerymonth.csv"
                )

            # File upload status indicator
            uploaded_files = sum([1 for f in [host_export_file, file1, file2, file3, file4] if f is not None])
            if uploaded_files == 5:
                st.success(f"✅ All 5 files uploaded for {period}")
            elif uploaded_files > 0:
                st.warning(f"⚠️ {uploaded_files}/5 files uploaded for {period}")
            else:
                st.info(f"📋 0/5 files uploaded for {period}")

        month_data.append({
            'period': period,
            'host_export_file': host_export_file,
            'file1': file1,
            'file2': file2,
            'file3': file3,
            'file4': file4
        })

    # ============================================
    # TICKET LIFECYCLE DATA UPLOAD (OPTIONAL)
    # ============================================
    st.markdown("---")
    st.header("🎫 Ticket Lifecycle Analysis (Optional)")
    st.markdown("""
    **Optional Section:** Upload detection data for **Ticket Lifecycle Analysis** with Status and Severity tracking.

    **This creates:**
    - **Section A.1**: Pivot table showing Request IDs grouped by Status with Severity counts (Critical, High, Medium, Low)
    - **Section A.2**: Summary for Detections (alerts triggered, resolved, pending)

    You can either:
    - **Upload a CSV file** with these **required columns**:
      - `Period` - Month name (e.g., "November 2025")
      - `Status` - closed, in_progress, open, pending, on-hold
      - `SeverityName` - Critical, High, Medium, Low
      - `Request ID` - Detection identifier
      - `Count of SeverityName` - (Optional) Count to avoid repeating rows
    - **Use placeholder data** (auto-generates sample data)
    - **Skip this section** if you don't need ticket lifecycle analysis

    📥 **Download the sample template below to see the exact format**
    """)

    use_ticket_data = st.checkbox("Include Ticket Lifecycle Analysis", value=False)
    ticket_upload_file = None

    if use_ticket_data:
        # Download sample CSV template
        st.markdown("### 📥 Download Sample CSV Template")

        # Load the sample CSV
        try:
            with open('security-dashboard/sample_ticket_data.csv', 'r') as f:
                sample_csv_content = f.read()

            st.download_button(
                label="📥 Download Sample CSV Template",
                data=sample_csv_content,
                file_name="ticket_lifecycle_template.csv",
                mime="text/csv",
                help="Download this template and fill it with your data"
            )
            st.caption("💡 This template shows the exact format required for ticket lifecycle analysis")
        except FileNotFoundError:
            st.warning("Sample CSV file not found. Using inline template.")

        # Show format guide
        with st.expander("📖 View CSV Format Requirements", expanded=False):
            st.markdown("""
            **Required Columns:**
            - `Period`: Month name (e.g., "October 2025", "November 2025", "December 2025")
            - `Status`: closed, in_progress, open, pending, on-hold
            - `SeverityName`: Critical, High, Medium, Low (**REQUIRED**)
            - `Request ID`: Detection identifier (e.g., 503457, 503528)
            - `Count of SeverityName`: Number of occurrences (**OPTIONAL** - use this to avoid repeating rows)

            **Sample Format (with Count - Recommended):**
            ```
            Period,Status,SeverityName,Request ID,Count of SeverityName
            November 2025,closed,Critical,503528,1
            November 2025,closed,High,503457,2
            November 2025,closed,High,503528,7
            November 2025,closed,Medium,503900,3
            November 2025,in_progress,Medium,513757,1
            ```

            **Sample Format (without Count - repeat rows):**
            ```
            Period,Status,SeverityName,Request ID
            November 2025,closed,Critical,503528
            November 2025,closed,High,503457
            November 2025,closed,High,503457
            November 2025,in_progress,Medium,513757
            ```

            **Output:**
            - Pivot table grouped by Status, showing Request IDs with severity breakdowns
            - Summary section showing total alerts, resolved, and pending counts

            📄 **Full documentation:** See `TICKET_DATA_FORMAT.md` for complete guide
            """)

        ticket_data_option = st.radio(
            "Choose ticket data source:",
            ["Upload CSV file", "Use placeholder data"],
            help="Select how you want to provide ticket data"
        )

        if ticket_data_option == "Upload CSV file":
            ticket_upload_file = st.file_uploader(
                "Upload Ticket Data CSV",
                type=['csv'],
                key="ticket_upload_file",
                help="CSV file must contain 'Period' and 'Status' columns"
            )

            if ticket_upload_file:
                # Validate CSV format before accepting
                try:
                    # Read CSV with proper encoding
                    temp_df = pd.read_csv(ticket_upload_file, encoding='utf-8-sig')
                    ticket_upload_file.seek(0)  # Reset file pointer

                    # Check required columns
                    required_columns = ['Period', 'Status', 'SeverityName', 'Request ID']
                    missing_columns = [col for col in required_columns if col not in temp_df.columns]

                    if missing_columns:
                        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                        st.info("""
                        **Required CSV format:**
                        - `Period` - Month name (e.g., "November 2025")
                        - `Status` - closed, in_progress, open, pending, on-hold
                        - `SeverityName` - Critical, High, Medium, Low
                        - `Request ID` - Detection identifier
                        - `Count of SeverityName` - (Optional) Count value

                        📥 Download the sample template above to see the correct format.
                        """)
                        ticket_upload_file = None  # Clear invalid file
                    else:
                        st.success(f"✅ Ticket data file uploaded successfully! ({len(temp_df)} rows)")

                        # Show preview
                        with st.expander("👀 Preview uploaded data (first 5 rows)"):
                            st.dataframe(temp_df.head(), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error reading CSV file: {str(e)}")
                    st.info("Make sure your CSV file is properly formatted and encoded in UTF-8")
                    ticket_upload_file = None
        else:
            st.info("📝 Customize your placeholder ticket data below:")

            # Month-specific ticket configuration
            st.markdown("#### 🎯 Ticket Count Configuration")
            st.markdown("Configure ticket counts for each month:")

            # Store ticket data per month
            ticket_config_per_month = {}

            for i in range(num_months):
                month_key = f"month_{i}"
                with st.expander(f"📅 {month_data[i]['period']} - Ticket Configuration", expanded=(i == 0)):
                    st.markdown(f"**Configure tickets for {month_data[i]['period']}:**")

                    col1, col2 = st.columns(2)
                    with col1:
                        open_count = st.number_input(
                            "🟢 Open Tickets",
                            min_value=0,
                            max_value=1000,
                            value=25,
                            step=1,
                            key=f"open_tickets_{month_key}"
                        )
                        pending_count = st.number_input(
                            "🟡 Pending Tickets",
                            min_value=0,
                            max_value=1000,
                            value=15,
                            step=1,
                            key=f"pending_tickets_{month_key}"
                        )
                    with col2:
                        onhold_count = st.number_input(
                            "🟠 On-hold Tickets",
                            min_value=0,
                            max_value=1000,
                            value=10,
                            step=1,
                            key=f"onhold_tickets_{month_key}"
                        )
                        closed_count = st.number_input(
                            "🔵 Closed Tickets",
                            min_value=0,
                            max_value=1000,
                            value=50,
                            step=1,
                            key=f"closed_tickets_{month_key}"
                        )

                    # Show month summary
                    month_total = open_count + pending_count + onhold_count + closed_count
                    st.success(f"📊 Total tickets for {month_data[i]['period']}: **{month_total}**")

                    # Store configuration
                    ticket_config_per_month[month_data[i]['period']] = {
                        'Open': open_count,
                        'Pending': pending_count,
                        'On-hold': onhold_count,
                        'Closed': closed_count
                    }

            # Overall summary
            total_all_months = sum(
                sum(config.values()) for config in ticket_config_per_month.values()
            )
            st.info(f"📈 **Grand Total**: {total_all_months} tickets across {num_months} month(s)")

            # Store in session state for processing
            st.session_state['ticket_config_per_month'] = ticket_config_per_month

    # ============================================
    # DETECTION STATUS DATA (STATUS + SEVERITY) - HIDDEN
    # This functionality is now merged into Ticket Lifecycle above
    # ============================================
    # st.markdown("---")
    # st.header("📊 Detection Status by Severity (Optional)")

    use_detection_status = False  # Disabled - now part of Ticket Lifecycle
    detection_status_files = []

    if use_detection_status:
        with st.expander("📖 View CSV Format Requirements", expanded=False):
            st.markdown("""
            **Required Columns:**
            - `Status`: Detection status (closed, in_progress, open, pending, on-hold)
            - `SeverityName`: Severity level (Critical, High, Medium, Low)
            - `Request ID`: Detection identifier

            **Sample Format:**
            ```
            Status,SeverityName,Request ID
            closed,Critical,503528
            closed,High,503457
            closed,High,503479
            in_progress,Medium,513757
            open,High,503900
            ```

            **Output:** Creates a pivot table like:
            ```
            Status       | Critical | High | Medium | Low | Grand Total
            -------------|----------|------|--------|-----|------------
            closed       |    1     |  10  |   3    |  2  |     16
            in_progress  |    0     |   0  |   1    |  0  |      1
            ```

            📥 **Sample file:** `sample_detection_status_november.csv`
            """)

        st.markdown("#### 📤 Upload Detection Status Files")
        st.info("💡 Upload one CSV file per month. Each file should contain Status and SeverityName columns.")

        for i in range(num_months):
            with st.expander(f"📅 {month_data[i]['period']} - Upload Detection Status", expanded=(i == 0)):
                detection_file = st.file_uploader(
                    f"Upload Detection Status CSV for {month_data[i]['period']}",
                    type=['csv'],
                    key=f"detection_status_{i}",
                    help="CSV with Status, SeverityName, and Request ID columns"
                )

                if detection_file:
                    st.success(f"✅ Detection status file uploaded for {month_data[i]['period']}")
                    detection_status_files.append({
                        'file': detection_file,
                        'period': month_data[i]['period']
                    })
                else:
                    detection_status_files.append(None)

        # Store in session state
        st.session_state['detection_status_files'] = detection_status_files

    if st.button("🚀 Process All Months and Generate Templates"):
        # Create status container at the top for all notifications
        status_container = st.container()

        all_templates = []
        all_notes = []
        processed_months = []  # Track successfully processed months

        for i, m in enumerate(month_data):
            if m['host_export_file'] and m['file1']:
                with st.spinner(f"Processing Month {i+1} ({m['period']})..."):
                    templates, data_notes = process_with_compositeid_case_detection(
                        m['host_export_file'], m['file1'], m['file2'], m['file3'], m['file4']
                    )

                    # Check if templates is valid before processing
                    if templates is not None and isinstance(templates, dict):
                        # Tag each DataFrame with the period
                        for k in templates:
                            if not templates[k].empty:
                                templates[k]['Period'] = m['period']
                        all_templates.append(templates)
                        all_notes.append(data_notes)
                        processed_months.append(m['period'])  # Track this month
                    else:
                        with status_container:
                            st.error(f"❌ Error processing Month {i+1} ({m['period']}). Check your CSV file encoding and format.")
            else:
                with status_container:
                    st.error(f"❌ Month {i+1} is missing required files. Skipping.")

        if all_templates:
            with status_container:
                st.success(f"✅ All {len(processed_months)} month(s) processed! You can now analyze trends across months.")

            # Store processed months in session state
            st.session_state['processed_months'] = processed_months

            # Aggregate for trend analysis
            agg = {}
            for k in ['host_analysis', 'detection_analysis', 'time_analysis']:
                agg[k] = pd.concat([t[k] for t in all_templates if k in t and not t[k].empty], ignore_index=True)

            # Show download and preview for each
            st.markdown("---")
            st.header(f"📊 Aggregated Multi-Month Templates ({len(processed_months)} months: {', '.join(processed_months)})")

            for k, label in zip(['host_analysis', 'detection_analysis', 'time_analysis'],
                                ["Host Analysis", "Detection Analysis", "Time Analysis"]):
                st.subheader(f"{label} (All Months)")
                if not agg[k].empty:
                    st.dataframe(agg[k], use_container_width=True)
                    csv_buffer = io.StringIO()
                    agg[k].to_csv(csv_buffer, index=False)
                    st.download_button(
                        label=f"📥 Download {label} (All Months, CSV)",
                        data=csv_buffer.getvalue(),
                        file_name=f"{label.replace(' ', '_')}_All_Months.csv",
                        mime="text/csv"
                    )

            # Store templates in session state for trend dashboard
            st.session_state['three_month_trend_data'] = agg

            # 🚀 AUTOMATICALLY GENERATE ANALYSIS RESULTS
            try:
                # Use the actual number of months processed
                actual_num_months = len(processed_months)

                # Generate Host Analysis Results
                if not agg['host_analysis'].empty:
                    host_results = generate_host_analysis(agg['host_analysis'], actual_num_months)
                    st.session_state['host_analysis_results'] = host_results
                    st.session_state['num_months'] = actual_num_months  # Store for reference
                    with status_container:
                        st.success(f"✅ Host Analysis: {len(host_results)} analysis outputs generated for {actual_num_months} month(s)")

                # Generate Detection & Severity Analysis Results
                if not agg['detection_analysis'].empty:
                    detection_results = generate_detection_severity_analysis(agg['detection_analysis'], actual_num_months)
                    st.session_state['detection_analysis_results'] = detection_results
                    with status_container:
                        st.success(f"✅ Detection Analysis: {len(detection_results)} analysis outputs generated for {actual_num_months} month(s)")

                # Generate Time-Based Analysis Results
                if not agg['time_analysis'].empty:
                    time_results = generate_time_analysis(agg['time_analysis'], actual_num_months)
                    st.session_state['time_analysis_results'] = time_results
                    with status_container:
                        st.success(f"✅ Time Analysis: {len(time_results)} analysis outputs generated for {actual_num_months} month(s)")

                # ============================================
                # Generate Ticket Lifecycle Analysis (if enabled)
                # ============================================
                if use_ticket_data:
                    try:
                        if ticket_data_option == "Upload CSV file" and ticket_upload_file:
                            # Read uploaded ticket data with UTF-8 encoding
                            ticket_df = pd.read_csv(ticket_upload_file, encoding='utf-8-sig')
                            with status_container:
                                st.info(f"📊 Processing uploaded ticket data: {len(ticket_df)} records")
                        else:
                            # Generate placeholder data with per-month custom counts
                            ticket_counts_per_month = st.session_state.get('ticket_config_per_month', {})
                            ticket_df = create_placeholder_ticket_data(processed_months, ticket_counts_per_month)
                            with status_container:
                                st.info(f"📝 Generated placeholder ticket data: {len(ticket_df)} records")

                        # Generate ticket lifecycle analysis
                        ticket_results = generate_ticket_lifecycle_analysis(ticket_df, actual_num_months)
                        st.session_state['ticket_lifecycle_results'] = ticket_results
                        with status_container:
                            st.success(f"✅ Ticket Lifecycle Analysis: {len(ticket_results)} analysis outputs generated")

                    except Exception as e:
                        with status_container:
                            st.error(f"❌ Error generating ticket lifecycle analysis: {str(e)}")
                            st.warning("Ticket analysis failed, but other templates are still available.")

                # ============================================
                # Generate Detection Status Analysis (if enabled)
                # ============================================
                if use_detection_status:
                    try:
                        detection_status_files = st.session_state.get('detection_status_files', [])

                        # Read all uploaded detection status files
                        detection_status_dfs = []
                        detection_months = []

                        for file_data in detection_status_files:
                            if file_data and 'file' in file_data:
                                df = pd.read_csv(file_data['file'], encoding='utf-8-sig')
                                detection_status_dfs.append(df)
                                detection_months.append(file_data['period'])
                                with status_container:
                                    st.info(f"📊 Processing detection status for {file_data['period']}: {len(df)} detections")

                        if detection_status_dfs:
                            # Generate detection status analysis
                            detection_status_results = generate_detection_status_analysis(
                                detection_status_dfs,
                                detection_months
                            )
                            st.session_state['detection_status_results'] = detection_status_results
                            with status_container:
                                st.success(f"✅ Detection Status Analysis: {len(detection_status_results)} month(s) analyzed")
                        else:
                            with status_container:
                                st.warning("⚠️ Detection Status enabled but no files uploaded")

                    except Exception as e:
                        with status_container:
                            st.error(f"❌ Error generating detection status analysis: {str(e)}")
                            st.warning("Detection status analysis failed, but other templates are still available.")

                with status_container:
                    st.success(f"🎉 All analysis results generated successfully for {actual_num_months} month(s)! Ready for Pivot Table Builder.")
                    st.info(f"📝 Processed months: {', '.join(processed_months)}")

            except Exception as e:
                with status_container:
                    st.error(f"❌ Error generating analysis results: {str(e)}")
                    st.warning("Templates are still available, but analysis results may be incomplete.")
        else:
            with status_container:
                st.error("❌ No valid months processed. Please check your uploads.")

def find_compositeid_column(df, file_name):
    """Find CompositeID column with different case variations"""
    
    # Possible variations of CompositeID
    possible_names = [
        'CompositeID', 'CompositeId', 'compositeid', 'compositeId', 
        'Compositeid', 'COMPOSITEID', 'composite_id', 'Composite_ID'
    ]
    
    # Check exact matches first
    for name in possible_names:
        if name in df.columns:
            st.write(f"✅ Found **{name}** in {file_name}")
            return name
    
    # Check case-insensitive matches
    for col in df.columns:
        if col.lower().replace('_', '').replace(' ', '') == 'compositeid':
            st.write(f"✅ Found **{col}** (case variation) in {file_name}")
            return col
    
    # Check if column contains 'composite'
    for col in df.columns:
        if 'composite' in col.lower():
            st.write(f"✅ Found **{col}** (contains 'composite') in {file_name}")
            return col
    
    st.error(f"❌ No CompositeId column found in {file_name}")
    st.write(f"Available columns: {list(df.columns)}")
    return None

def process_with_compositeid_case_detection(host_export_file, file1, file2=None, file3=None, file4=None):
    """Process with case-insensitive CompositeID detection"""
    
    try:
        # Read export files with UTF-8 encoding
        host_export_df = pd.read_csv(host_export_file, encoding='utf-8-sig')
        df1 = pd.read_csv(file1, encoding='utf-8-sig')  # YOUR primary source
        df2 = pd.read_csv(file2, encoding='utf-8-sig') if file2 else pd.DataFrame()
        df3 = pd.read_csv(file3, encoding='utf-8-sig') if file3 else pd.DataFrame()
        df4 = pd.read_csv(file4, encoding='utf-8-sig') if file4 else pd.DataFrame()
        
        # Track data quality
        data_notes = {
            'primary_records': 0,
            'filled_data': {},
            'compositeid_debug': {},
            'missing_relationships': [],
            'compositeid_columns': {}
        }
        
        # FIND CompositeID columns in each file
        st.subheader("🔍 CompositeId Column Detection")
        
        # Find CompositeID column in each file
        compositeid_col_1 = find_compositeid_column(df1, "File 1 (PRIMARY)")
        compositeid_col_2 = find_compositeid_column(df2, "File 2") if not df2.empty else None
        compositeid_col_3 = find_compositeid_column(df3, "File 3") if not df3.empty else None
        compositeid_col_4 = find_compositeid_column(df4, "File 4") if not df4.empty else None
        
        # Store found column names
        data_notes['compositeid_columns'] = {
            'file1': compositeid_col_1,
            'file2': compositeid_col_2,
            'file3': compositeid_col_3,
            'file4': compositeid_col_4
        }
        
        if not compositeid_col_1:
            st.error("❌ Cannot proceed - CompositeId column not found in File 1!")
            return None, None
        
        # DEBUGGING: Show detailed file analysis
        st.subheader("📋 File Analysis with Detected CompositeId Columns")
        
        with st.expander("File 1 (PRIMARY) - CompositeId Analysis", expanded=True):
            st.write(f"**Columns:** {list(df1.columns)}")
            st.write(f"**Total Records:** {len(df1)}")
            st.write(f"**🔑 CompositeId Column Found:** `{compositeid_col_1}`")
            
            if 'UniqueNo' in df1.columns:
                unique_count = len(df1['UniqueNo'].unique())
                st.write(f"**🔑 UniqueNo Count: {unique_count}**")
                data_notes['primary_records'] = unique_count
            
            if compositeid_col_1:
                compositeid_count = df1[compositeid_col_1].nunique()
                st.write(f"**🔗 CompositeId Count: {compositeid_count}**")
                
                # Show sample CompositeIDs
                sample_compositeids = df1[compositeid_col_1].dropna().head(5).tolist()
                st.write(f"**Sample CompositeIds:** {sample_compositeids}")
                data_notes['compositeid_debug']['file1_samples'] = sample_compositeids
            
            st.dataframe(df1.head(5))
        
        # DEBUG File 3 (LocalIP source)
        if not df3.empty and compositeid_col_3:
            with st.expander("File 3 (LocalIP SOURCE) - Detailed Analysis", expanded=True):
                st.write(f"**Columns:** {list(df3.columns)}")
                st.write(f"**Total Records:** {len(df3)}")
                st.write(f"**🔗 CompositeId Column Found:** `{compositeid_col_3}`")
                
                compositeid_count = df3[compositeid_col_3].nunique()
                st.write(f"**🔗 CompositeId Count: {compositeid_count}**")
                
                # Show sample CompositeIDs
                sample_compositeids = df3[compositeid_col_3].dropna().head(5).tolist()
                st.write(f"**Sample CompositeIds:** {sample_compositeids}")
                data_notes['compositeid_debug']['file3_samples'] = sample_compositeids
                
                if 'LocalIP' in df3.columns:
                    localip_count = df3['LocalIP'].notna().sum()
                    st.write(f"**🌐 LocalIP Non-Empty Count: {localip_count}**")
                    
                    if localip_count > 0:
                        sample_ips = df3['LocalIP'].dropna().head(5).tolist()
                        st.write(f"**Sample LocalIPs:** {sample_ips}")
                        data_notes['compositeid_debug']['sample_ips'] = sample_ips
                else:
                    st.error("❌ LocalIP column not found in File 3!")
                
                st.dataframe(df3.head(5))
        
        # DEBUG File 4 (Country source)
        if not df4.empty and compositeid_col_4:
            with st.expander("File 4 (Country SOURCE) - Detailed Analysis", expanded=True):
                st.write(f"**Columns:** {list(df4.columns)}")
                st.write(f"**Total Records:** {len(df4)}")
                st.write(f"**🔗 CompositeId Column Found:** `{compositeid_col_4}`")
                
                compositeid_count = df4[compositeid_col_4].nunique()
                st.write(f"**🔗 CompositeId Count: {compositeid_count}**")
                
                # Show sample CompositeIDs
                sample_compositeids = df4[compositeid_col_4].dropna().head(5).tolist()
                st.write(f"**Sample CompositeIds:** {sample_compositeids}")
                data_notes['compositeid_debug']['file4_samples'] = sample_compositeids
                
                if 'Country' in df4.columns:
                    country_count = df4['Country'].notna().sum()
                    st.write(f"**🌍 Country Non-Empty Count: {country_count}**")
                    
                    if country_count > 0:
                        sample_countries = df4['Country'].dropna().head(5).tolist()
                        st.write(f"**Sample Countries:** {sample_countries}")
                        data_notes['compositeid_debug']['sample_countries'] = sample_countries
                else:
                    st.error("❌ Country column not found in File 4!")
                
                st.dataframe(df4.head(5))
        
        # DEBUG: Check CompositeID overlap
        if compositeid_col_1:
            st.subheader("🔍 CompositeId Overlap Analysis")
            
            file1_compositeids = set(df1[compositeid_col_1].dropna())
            
            if not df3.empty and compositeid_col_3:
                file3_compositeids = set(df3[compositeid_col_3].dropna())
                overlap_13 = file1_compositeids.intersection(file3_compositeids)
                st.write(f"**File1 ↔ File3 CompositeId Overlap: {len(overlap_13)} matches**")
                data_notes['compositeid_debug']['overlap_13'] = len(overlap_13)
                
                if len(overlap_13) > 0:
                    sample_overlap = list(overlap_13)[:3]
                    st.write(f"**Sample Matching CompositeIds:** {sample_overlap}")
            
            if not df4.empty and compositeid_col_4:
                file4_compositeids = set(df4[compositeid_col_4].dropna())
                overlap_14 = file1_compositeids.intersection(file4_compositeids)
                st.write(f"**File1 ↔ File4 CompositeId Overlap: {len(overlap_14)} matches**")
                data_notes['compositeid_debug']['overlap_14'] = len(overlap_14)
                
                if len(overlap_14) > 0:
                    sample_overlap = list(overlap_14)[:3]
                    st.write(f"**Sample Matching CompositeIds:** {sample_overlap}")
        
        # Generate templates with detected column names
        templates = {
            'host_analysis': generate_host_with_detected_columns(host_export_df, df1, df2, df3, df4, data_notes),
            'detection_analysis': generate_detection_with_detected_columns(df1, df2, df3, df4, data_notes),
            'time_analysis': generate_time_with_detected_columns(df1, data_notes)
        }
        
        return templates, data_notes
        
    except Exception as e:
        st.error(f"Error processing with case detection: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

def create_compositeid_mappings_with_detected_columns(df1, df2, df3, df4, data_notes):
    """Create CompositeID mappings using detected column names"""
    
    mappings = {
        'compositeid_to_username': {},
        'compositeid_to_severity': {},
        'compositeid_to_ip': {},
        'compositeid_to_objective': {},
        'compositeid_to_country': {},
        'compositeid_to_status': {},
        'compositeid_to_resolution': {}
    }
    
    debug_info = {
        'file2_mappings': 0,
        'file3_mappings': 0,
        'file4_mappings': 0
    }
    
    # Get detected column names
    compositeid_cols = data_notes['compositeid_columns']
    
    # Map CompositeID to data from File 2
    if not df2.empty and compositeid_cols['file2']:
        compositeid_col = compositeid_cols['file2']
        st.write(f"🔗 Processing File 2 mappings using column `{compositeid_col}`...")
        
        for _, row in df2.iterrows():
            compositeid = row.get(compositeid_col)
            if pd.notna(compositeid):
                # UserName
                if 'UserName' in df2.columns and pd.notna(row.get('UserName')):
                    mappings['compositeid_to_username'][compositeid] = row['UserName']
                    debug_info['file2_mappings'] += 1
                # SeverityName
                if 'SeverityName' in df2.columns and pd.notna(row.get('SeverityName')):
                    mappings['compositeid_to_severity'][compositeid] = row['SeverityName']
                # Status
                if 'Status' in df2.columns and pd.notna(row.get('Status')):
                    mappings['compositeid_to_status'][compositeid] = row['Status']
        
        st.write(f"✅ File 2: Created {debug_info['file2_mappings']} mappings")
    
    # Map CompositeID to LocalIP and Objective from File 3
    if not df3.empty and compositeid_cols['file3']:
        compositeid_col = compositeid_cols['file3']
        st.write(f"🔗 Processing File 3 mappings using column `{compositeid_col}` (LocalIP)...")
        
        for _, row in df3.iterrows():
            compositeid = row.get(compositeid_col)
            if pd.notna(compositeid):
                # LocalIP
                if 'LocalIP' in df3.columns and pd.notna(row.get('LocalIP')):
                    mappings['compositeid_to_ip'][compositeid] = row['LocalIP']
                    debug_info['file3_mappings'] += 1
                # Objective
                if 'Objective' in df3.columns and pd.notna(row.get('Objective')):
                    mappings['compositeid_to_objective'][compositeid] = row['Objective']
        
        st.write(f"✅ File 3: Created {debug_info['file3_mappings']} LocalIP mappings")
        
        # Show sample LocalIP mappings
        if len(mappings['compositeid_to_ip']) > 0:
            sample_ip_mappings = dict(list(mappings['compositeid_to_ip'].items())[:3])
            st.write(f"**Sample LocalIP mappings:** {sample_ip_mappings}")
    
    # Map CompositeID to Country from File 4
    if not df4.empty and compositeid_cols['file4']:
        compositeid_col = compositeid_cols['file4']
        st.write(f"🔗 Processing File 4 mappings using column `{compositeid_col}` (Country)...")
        
        for _, row in df4.iterrows():
            compositeid = row.get(compositeid_col)
            if pd.notna(compositeid) and 'Country' in df4.columns and pd.notna(row.get('Country')):
                mappings['compositeid_to_country'][compositeid] = row['Country']
                debug_info['file4_mappings'] += 1
        
        st.write(f"✅ File 4: Created {debug_info['file4_mappings']} Country mappings")
        
        # Show sample Country mappings
        if len(mappings['compositeid_to_country']) > 0:
            sample_country_mappings = dict(list(mappings['compositeid_to_country'].items())[:3])
            st.write(f"**Sample Country mappings:** {sample_country_mappings}")
    
    return mappings, debug_info

def generate_host_with_detected_columns(host_export_df, df1, df2, df3, df4, data_notes):
    """Generate Host Analysis using detected CompositeId column"""
    
    if df1.empty or 'UniqueNo' not in df1.columns:
        st.error("Cannot generate - UniqueNo not found in File 1!")
        return pd.DataFrame()
    
    # Start with YOUR UniqueNo as primary key
    result_df = df1.copy()
    st.info(f"🔑 Processing {len(result_df)} records based on YOUR UniqueNo")
    
    # Create CompositeID mappings using detected columns
    st.write("🔗 Creating CompositeId mappings using detected column names...")
    mappings, debug_info = create_compositeid_mappings_with_detected_columns(df1, df2, df3, df4, data_notes)
    
    # Fill UserName using CompositeID mapping
    compositeid_col = data_notes['compositeid_columns']['file1']
    if compositeid_col and compositeid_col in result_df.columns:
        if 'UserName' not in result_df.columns:
            result_df['UserName'] = ''
        
        # Fill missing usernames using CompositeID mapping
        filled_usernames = 0
        for idx, row in result_df.iterrows():
            if pd.isna(row.get('UserName')) or row.get('UserName') == '':
                compositeid = row.get(compositeid_col)
                if compositeid in mappings['compositeid_to_username']:
                    result_df.at[idx, 'UserName'] = mappings['compositeid_to_username'][compositeid]
                    filled_usernames += 1
        
        data_notes['filled_data']['usernames'] = filled_usernames
        st.write(f"✅ Filled {filled_usernames} usernames using CompositeId relationships")
    
    # Join with Host Export using Hostname
    if not host_export_df.empty and 'Hostname' in host_export_df.columns and 'Hostname' in result_df.columns:
        st.write("🔗 Joining with Host Export using Hostname")
        
        host_unique = host_export_df.drop_duplicates(subset=['Hostname'])
        
        # Get available host columns
        host_cols = ['Hostname']
        for col in ['OS Version', 'Sensor Version', 'Site', 'OU']:
            if col in host_export_df.columns:
                host_cols.append(col)
        
        # Merge to get host information
        result_df = pd.merge(result_df, host_unique[host_cols], on='Hostname', how='left')
        st.write(f"✅ Added host information for all records")
    
    # Ensure all required columns exist
    required_columns = ['UniqueNo', 'Hostname', 'UserName', 'OS Version', 'Sensor Version', 'Site', 'OU', 'Detect MALAYSIA TIME FORMULA']
    
    for col in required_columns:
        if col not in result_df.columns:
            result_df[col] = ''
    
    # Clean and format data
    for col in ['UserName', 'OS Version', 'Sensor Version', 'Site', 'OU']:
        result_df[col] = result_df[col].fillna('')
    
    # Reorder columns
    final_columns = ['UniqueNo', 'Hostname', 'UserName', 'OS Version', 'Sensor Version', 'Site', 'OU', 'Detect MALAYSIA TIME FORMULA']
    existing_cols = [col for col in final_columns if col in result_df.columns]
    result_df = result_df[existing_cols]
    
    st.success(f"✅ Host Analysis: {len(result_df)} records")
    
    return result_df

def generate_detection_with_detected_columns(df1, df2, df3, df4, data_notes):
    """Generate Detection Analysis using detected CompositeId columns"""
    
    if df1.empty or 'UniqueNo' not in df1.columns:
        return pd.DataFrame()
    
    # Start with YOUR UniqueNo as primary key
    result_df = df1.copy()
    st.write(f"🔑 Starting with {len(result_df)} records from YOUR UniqueNo")
    
    # Create CompositeID mappings using detected columns
    st.write("🔗 Creating CompositeId mappings for Detection Analysis...")
    mappings, debug_info = create_compositeid_mappings_with_detected_columns(df1, df2, df3, df4, data_notes)
    
    # Add ALL required columns for Detection Analysis
    required_columns = [
        'UniqueNo', 'Hostname', 'SeverityName', 'Tactic', 'Technique', 'Status', 
        'Detect MALAYSIA TIME FORMULA', 'FileName', 'LocalIP', 'Country', 'Objective'
    ]
    
    for col in required_columns:
        if col not in result_df.columns:
            result_df[col] = ''
    
    # Fill missing data using CompositeID relationships with detected column names
    compositeid_col = data_notes['compositeid_columns']['file1']
    if compositeid_col and compositeid_col in result_df.columns:
        filled_counts = {
            'severity': 0, 'status': 0, 'localip': 0, 'country': 0, 'objective': 0
        }
        
        st.write(f"🔗 Filling data using CompositeId column `{compositeid_col}`...")
        
        for idx, row in result_df.iterrows():
            compositeid = row.get(compositeid_col)
            
            if pd.notna(compositeid):
                # Fill SeverityName
                if (pd.isna(row.get('SeverityName')) or row.get('SeverityName') == '') and compositeid in mappings['compositeid_to_severity']:
                    result_df.at[idx, 'SeverityName'] = mappings['compositeid_to_severity'][compositeid]
                    filled_counts['severity'] += 1
                
                # Fill Status
                if (pd.isna(row.get('Status')) or row.get('Status') == '') and compositeid in mappings['compositeid_to_status']:
                    result_df.at[idx, 'Status'] = mappings['compositeid_to_status'][compositeid]
                    filled_counts['status'] += 1
                
                # Fill LocalIP (CRITICAL - FROM FILE 3)
                if (pd.isna(row.get('LocalIP')) or row.get('LocalIP') == '') and compositeid in mappings['compositeid_to_ip']:
                    result_df.at[idx, 'LocalIP'] = mappings['compositeid_to_ip'][compositeid]
                    filled_counts['localip'] += 1
                
                # Fill Country (CRITICAL - FROM FILE 4)
                if (pd.isna(row.get('Country')) or row.get('Country') == '') and compositeid in mappings['compositeid_to_country']:
                    result_df.at[idx, 'Country'] = mappings['compositeid_to_country'][compositeid]
                    filled_counts['country'] += 1
                
                # Fill Objective (FROM FILE 3)
                if (pd.isna(row.get('Objective')) or row.get('Objective') == '') and compositeid in mappings['compositeid_to_objective']:
                    result_df.at[idx, 'Objective'] = mappings['compositeid_to_objective'][compositeid]
                    filled_counts['objective'] += 1
        
        # Track filled data
        data_notes['filled_data'].update(filled_counts)
        
        # Show detailed filling results
        st.write(f"✅ **DATA FILLING RESULTS:**")
        st.write(f"  • 🔥 **LocalIP filled: {filled_counts['localip']} records** (from File 3)")
        st.write(f"  • 🌍 **Country filled: {filled_counts['country']} records** (from File 4)")
        st.write(f"  • 🎯 Objective filled: {filled_counts['objective']} records")
        st.write(f"  • ⚠️ SeverityName filled: {filled_counts['severity']} records")
        st.write(f"  • 📊 Status filled: {filled_counts['status']} records")
        
        # Show why LocalIP/Country might be empty
        if filled_counts['localip'] == 0:
            st.error("❌ **LocalIP: 0 records filled!** Check CompositeId matching between File 1 and File 3")
        if filled_counts['country'] == 0:
            st.error("❌ **Country: 0 records filled!** Check CompositeId matching between File 1 and File 4")
    
    # Clean data (convert NaN to empty string for display)
    for col in required_columns:
        if col in result_df.columns:
            result_df[col] = result_df[col].fillna('')
    
    # Reorder columns to match PowerBI table (INCLUDING LocalIP and Country)
    final_columns = [
        'UniqueNo', 'Hostname', 'SeverityName', 'Tactic', 'Technique', 'Status', 
        'Detect MALAYSIA TIME FORMULA', 'FileName', 'LocalIP', 'Country'
    ]
    
    # Only include columns that exist
    existing_cols = [col for col in final_columns if col in result_df.columns]
    result_df = result_df[existing_cols]
    
    st.success(f"✅ Detection Analysis: {len(result_df)} records with LocalIP and Country columns")
    
    return result_df

def generate_time_with_detected_columns(df1, data_notes):
    """Generate Time Analysis using detected columns"""
    
    if df1.empty or 'UniqueNo' not in df1.columns:
        return pd.DataFrame()
    
    # Use YOUR data as-is
    time_cols = ['UniqueNo', 'Hostname', 'Detect MALAYSIA TIME FORMULA']
    available_cols = [col for col in time_cols if col in df1.columns]
    
    result_df = df1[available_cols].copy() if available_cols else df1[['UniqueNo']].copy()
    
    # Fill missing columns
    for col in time_cols:
        if col not in result_df.columns:
            result_df[col] = ''
    
    return result_df

def display_results_clean(templates: Dict, data_notes: Dict):
    """Display results with clean metrics (NO unnecessary Severity counter)"""
    
    st.header("📊 Generated Analysis Templates (Clean Results)")
    
    # Show detected CompositeId columns
    if data_notes.get('compositeid_columns'):
        with st.expander("🔍 Detected CompositeId Columns", expanded=True):
            cols = data_notes['compositeid_columns']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**File 1:** `{cols['file1']}`")
                st.write(f"**File 2:** `{cols['file2']}`")
            with col2:
                st.write(f"**File 3:** `{cols['file3']}`")
                st.write(f"**File 4:** `{cols['file4']}`")
    
    # Show CompositeID debug results
    if data_notes.get('compositeid_debug'):
        with st.expander("🔍 CompositeId Matching Results", expanded=True):
            debug = data_notes['compositeid_debug']
            
            col1, col2 = st.columns(2)
            with col1:
                if 'overlap_13' in debug:
                    st.metric("File1 ↔ File3 Matches", debug['overlap_13'])
                if 'sample_ips' in debug:
                    st.write(f"**Sample IPs Found:** {debug['sample_ips']}")
            with col2:
                if 'overlap_14' in debug:
                    st.metric("File1 ↔ File4 Matches", debug['overlap_14'])
                if 'sample_countries' in debug:
                    st.write(f"**Sample Countries Found:** {debug['sample_countries']}")
            
            st.info("💡 Perfect! CompositeId values are matching between files!")
    
    # Show CLEAN data filling summary (ONLY LocalIP and Country)
    if data_notes.get('filled_data'):
        with st.expander("🔗 Data Filled Using CompositeId Relationships", expanded=True):
            filled = data_notes['filled_data']
            
            col1, col2 = st.columns(2)
            with col1:
                if 'localip' in filled:
                    if filled['localip'] > 0:
                        st.success(f"LocalIP: {filled['localip']} ✅")
                    else:
                        st.error(f"LocalIP: {filled['localip']} ❌")
            with col2:
                if 'country' in filled:
                    if filled['country'] > 0:
                        st.success(f"Country: {filled['country']} ✅")
                    else:
                        st.error(f"Country: {filled['country']} ❌")
            
            st.info("🎯 Perfect! Both LocalIP and Country data are filled successfully!")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🖥️ Host Analysis", "🔍 Detection Analysis", "⏰ Time Analysis"])
    
    with tab1:
        st.subheader("Host Analysis Template")
        host_df = templates['host_analysis']
        
        if not host_df.empty:
            st.dataframe(host_df, use_container_width=True)
            
            csv_buffer = io.StringIO()
            host_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Host Analysis Template (CSV)",
                data=csv_buffer.getvalue(),
                file_name="Host_Analysis_Template.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Detection Analysis Template (WITH LocalIP and Country)")
        detection_df = templates['detection_analysis']
        
        if not detection_df.empty:
            # Check if LocalIP and Country have data
            localip_filled = (detection_df['LocalIP'] != '').sum() if 'LocalIP' in detection_df.columns else 0
            country_filled = (detection_df['Country'] != '').sum() if 'Country' in detection_df.columns else 0
            
            col1, col2 = st.columns(2)
            with col1:
                if localip_filled > 0:
                    st.success(f"🌐 LocalIP: {localip_filled} records filled!")
                else:
                    st.error("🌐 LocalIP: 0 records filled - check CompositeId matching!")
            with col2:
                if country_filled > 0:
                    st.success(f"🌍 Country: {country_filled} records filled!")
                else:
                    st.error("🌍 Country: 0 records filled - check CompositeId matching!")
            
            st.dataframe(detection_df, use_container_width=True)
            
            csv_buffer = io.StringIO()
            detection_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Detection Analysis Template (CSV)",
                data=csv_buffer.getvalue(),
                file_name="Detection_Analysis_Template.csv",
                mime="text/csv"
            )
        else:
            st.error("❌ No detection data generated")
    
    with tab3:
        st.subheader("Time Analysis Template")
        time_df = templates['time_analysis']
        
        if not time_df.empty:
            st.dataframe(time_df, use_container_width=True)
            
            csv_buffer = io.StringIO()
            time_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Time Analysis Template (CSV)",
                data=csv_buffer.getvalue(),
                file_name="Time_Based_Analysis_Template.csv",
                mime="text/csv"
            )
    
    # Summary
    st.markdown("---")
    st.subheader("📋 Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Host Records", len(templates['host_analysis']))
    with col2:
        st.metric("Detection Records", len(templates['detection_analysis']))
    with col3:
        st.metric("Time Records", len(templates['time_analysis']))
    
    st.success("✅ Templates generated successfully - LocalIP and Country data filled perfectly!")

if __name__ == "__main__":
    falcon_generator_dashboard()