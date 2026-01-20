import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as reportlab_colors
import tempfile
import os

def pivot_table_builder_dashboard():
    """
    Interactive Pivot Table Builder - Flexmonster Style
    Allows users to drag and drop fields to create custom pivot tables and charts
    """
    st.title("📊 Interactive Pivot Table Builder")
    st.markdown("### Create custom pivot tables and charts from your multi-month data")
    st.markdown("<div style='text-align:right; color:gray; font-size:12px;'>developed by Izami Ariff © 2025</div>", unsafe_allow_html=True)

    # Check if analysis results are available
    if 'host_analysis_results' not in st.session_state and \
       'detection_analysis_results' not in st.session_state and \
       'time_analysis_results' not in st.session_state and \
       'ticket_lifecycle_results' not in st.session_state:
        st.warning("⚠️ No analysis results available. Please use the Falcon Generator to upload and process data first.")
        st.info("💡 Go to 'Falcon Data Generator' in the sidebar, upload your files, and click 'Process All Months and Generate Templates'. The analysis results will be generated automatically.")
        return

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Pivot Table Configuration")

        # Step 1: Select Analysis Category
        st.subheader("📁 Step 1: Select Analysis Category")
        available_categories = []
        if 'ticket_lifecycle_results' in st.session_state:
            available_categories.append("Ticket Lifecycle Analysis")
        if 'host_analysis_results' in st.session_state:
            available_categories.append("Host Analysis")
        if 'detection_analysis_results' in st.session_state:
            available_categories.append("Detection & Severity Analysis")
        if 'time_analysis_results' in st.session_state:
            available_categories.append("Time-Based Analysis")

        if not available_categories:
            st.error("No analysis results available!")
            return

        analysis_category = st.selectbox("Choose Analysis Category", available_categories)

        # Map category to results
        category_map = {
            "Ticket Lifecycle Analysis": 'ticket_lifecycle_results',
            "Host Analysis": 'host_analysis_results',
            "Detection & Severity Analysis": 'detection_analysis_results',
            "Time-Based Analysis": 'time_analysis_results'
        }

        selected_results_key = category_map[analysis_category]
        analysis_results = st.session_state[selected_results_key]

        # Step 2: Select Specific Analysis Output
        st.subheader("📊 Step 2: Select Analysis Output")

        # Get available analysis outputs (excluding 'raw_data' and 'raw_data_filtered')
        available_analyses = [k for k in analysis_results.keys() if k not in ['raw_data', 'raw_data_filtered']]

        # Create friendly names
        friendly_names = {
            # Ticket Lifecycle Analysis
            'ticket_status_trend': '1. Ticket Status Trend',
            'ticket_status_pivot': '2. Ticket Status Pivot',
            'monthly_summary': '3. Monthly Summary',
            'monthly_totals': '4. Monthly Totals',
            'status_distribution': '5. Status Distribution',
            # Host Analysis
            'overview_key_metrics': '1. Overview - KEY METRICS',
            'overview_top_hosts': '2. Overview - TOP HOSTS WITH DETECTIONS',
            'user_analysis': '3. User Analysis',
            'sensor_analysis': '4. Sensor Analysis',
            # Detection Analysis
            'critical_high_overview': '1. Overview - KEY METRICS',
            'severity_trend': '2. Overview - TOP SEVERITIES',
            'country_analysis': '3. GEOGRAPHIC ANALYSIS',
            'file_analysis': '4. FILE ANALYSIS',
            'tactics_by_severity': '5. Tactics by Severity',
            'technique_by_severity': '6. Technique by Severity',
            # 'raw_data_filtered': '7. Raw Data',  # Hidden - not currently used
            # Time Analysis
            'daily_trends': '1. Daily Trends',
            'hourly_analysis': '2. Hourly Analysis',
            'day_of_week': '3. Day of Week'
        }

        # Display names for selection
        display_options = [friendly_names.get(k, k.replace('_', ' ').title()) for k in available_analyses]

        selected_analysis_display = st.selectbox("Choose Specific Analysis", display_options)

        # Get the actual key from display name
        selected_analysis_key = available_analyses[display_options.index(selected_analysis_display)]

        # Check if analysis has changed - show warning if fields are configured
        current_analysis_id = f"{analysis_category}_{selected_analysis_key}"
        if 'last_analysis_id' not in st.session_state:
            st.session_state['last_analysis_id'] = current_analysis_id

        analysis_changed = st.session_state['last_analysis_id'] != current_analysis_id

        # Get the selected analysis dataframe
        df = analysis_results[selected_analysis_key].copy()

        if df.empty:
            st.error(f"No data available for {selected_analysis_display}")
            return

        st.success(f"✅ Loaded: {selected_analysis_display}")
        st.info(f"📊 {len(df)} rows × {len(df.columns)} columns")

        # Define default field configurations for each analysis
        default_configs = {
            # Ticket Lifecycle Analysis
            'ticket_status_trend': {
                'rows': ['Month'],
                'columns': ['Status'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Month',
                'use_ticket_status_colors': True,  # Auto-enable ticket status colors
                'use_monthly_colors': False
            },
            'ticket_status_pivot': {
                'rows': ['Status'],
                'columns': ['Month'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'use_monthly_colors': True
            },
            'monthly_summary': {
                'rows': ['Month'],
                'columns': ['Status'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'use_ticket_status_colors': True
            },
            'monthly_totals': {
                'rows': ['Month'],
                'columns': [],
                'values': ['Total Tickets'],
                'aggregation': 'sum',
                'chart_type': 'Line Chart',
                'use_monthly_colors': False
            },
            'status_distribution': {
                'rows': ['Status'],
                'columns': [],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Pie Chart',
                'use_ticket_status_colors': True
            },

            # Host Analysis
            'overview_key_metrics': {
                'rows': ['Month'],
                'columns': ['KEY METRICS'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Month',
                'use_monthly_colors': True
            },
            'overview_top_hosts': {
                'rows': ['TOP HOSTS WITH MOST DETECTIONS'],
                'columns': ['Month'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Value (Detection Count)',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'TOP HOSTS WITH MOST DETECTIONS',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Count',
                    'per_month': False
                }
            },
            'user_analysis': {
                'rows': ['Username'],
                'columns': ['Month'],
                'values': ['Count of Detection'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Value (Detection Count)',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'Username',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Count of Detection',
                    'per_month': False
                }
            },
            'sensor_analysis': {
                'rows': ['Sensor Version', 'Month', 'Status'],
                'columns': [],
                'values': ['Host Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Month',
                'chart_sort_direction': 'descending'
            },

            # Detection Analysis
            'critical_high_overview': {
                'rows': ['KEY METRICS'],
                'columns': ['Month'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'KEY METRICS',
                'filters': {
                    'KEY METRICS': ['Critical Detections']
                }
            },
            'severity_trend': {
                'rows': ['Month'],
                'columns': ['SeverityName'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Month',
                'use_severity_colors': True  # Auto-enable severity colors
            },
            'country_analysis': {
                'rows': ['Country'],
                'columns': ['Month'],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Detection Count',
                'chart_sort_direction': 'descending',
                'use_monthly_colors': True,
                'top_n': None  # Top N Filter disabled by default
            },
            'file_analysis': {
                'rows': ['File Name'],
                'columns': ['Month'],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Horizontal Bar',
                'sort_by': 'Detection Count',
                'chart_sort_direction': 'descending',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'File Name',
                    'n': 5,
                    'type': 'top',
                    'by_field': 'Detection Count',
                    'per_month': False
                }
            },
            'tactics_by_severity': {
                'rows': ['Month', 'SeverityName'],
                'columns': ['Tactic'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Tactic',
                'use_severity_colors': True,
                'use_monthly_colors': False
            },
            'technique_by_severity': {
                'rows': ['Month', 'SeverityName'],
                'columns': ['Technique'],
                'values': ['Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Technique',
                'use_severity_colors': True,
                'use_monthly_colors': False,
                'top_n': {
                    'enabled': True,
                    'field': 'Technique',
                    'n': 10,
                    'type': 'top',
                    'by_field': 'Count',
                    'per_month': False
                }
            },

            # Time Analysis
            'daily_trends': {
                'rows': ['Date', 'Month'],
                'columns': [],
                'values': ['Detection Count'],
                'aggregation': 'sum',
                'chart_type': 'Bar Chart',
                'sort_by': 'Value (Detection Count)',
                'chart_sort_direction': 'ascending',
                'use_monthly_colors': True,
                'top_n': {
                    'enabled': True,
                    'field': 'Date',
                    'n': 3,
                    'type': 'top',
                    'by_field': 'Detection Count',
                    'per_month': True
                }
            },
            'hourly_analysis': {'rows': ['Hour'], 'columns': [], 'values': ['Detection Count'], 'aggregation': 'sum', 'chart_type': 'Line Chart', 'sort_by': 'Hour', 'chart_sort_direction': 'descending'},
            'day_of_week': {'rows': ['Day', 'Type'], 'columns': [], 'values': ['Detection Count'], 'aggregation': 'sum', 'chart_type': 'Bar Chart', 'sort_by': 'Day'},
        }

        # Show unique months in the data for debugging
        if 'Month' in df.columns:
            unique_months = df['Month'].unique()
            num_months = len(unique_months)
            st.info(f"📅 Data contains {num_months} month(s): {', '.join(map(str, unique_months))}")
        else:
            st.warning("⚠️ No 'Month' column found in data")

        # Initialize pivot configuration in session state
        if 'pivot_config' not in st.session_state:
            st.session_state['pivot_config'] = {
                'rows': [],
                'columns': [],
                'values': [],
                'filters': {},
                'aggregation': 'count',
                'top_n': None,
                'chart_type': 'Bar Chart',
                'sort_by_field': 'Value (Detection Count)',
                'chart_sort_direction': 'descending'
            }

        # Apply default configuration when analysis changes or first load
        if analysis_changed:
            # Load default config for this analysis if available
            if selected_analysis_key in default_configs:
                default = default_configs[selected_analysis_key]

                # Only apply defaults if fields exist in the dataframe
                valid_rows = [r for r in default.get('rows', []) if r in df.columns]
                valid_columns = [c for c in default.get('columns', []) if c in df.columns]
                valid_values = [v for v in default.get('values', []) if v in df.columns]

                st.session_state['pivot_config']['rows'] = valid_rows
                st.session_state['pivot_config']['columns'] = valid_columns
                st.session_state['pivot_config']['values'] = valid_values
                st.session_state['pivot_config']['aggregation'] = default.get('aggregation', 'count')
                st.session_state['pivot_config']['chart_type'] = default.get('chart_type', 'Bar Chart')
                st.session_state['pivot_config']['sort_by_field'] = default.get('sort_by', 'Value (Detection Count)')
                st.session_state['pivot_config']['filters'] = default.get('filters', {})
                st.session_state['pivot_config']['top_n'] = default.get('top_n', None)
                st.session_state['pivot_config']['use_severity_colors'] = default.get('use_severity_colors', False)
                st.session_state['pivot_config']['use_ticket_status_colors'] = default.get('use_ticket_status_colors', False)
                st.session_state['pivot_config']['use_monthly_colors'] = default.get('use_monthly_colors', True)

                st.info(f"💡 Default configuration loaded for {selected_analysis_display}. You can customize the fields below.")
            else:
                # No default config - clear fields
                if 'pivot_config' in st.session_state:
                    config = st.session_state['pivot_config']
                    has_fields_configured = (len(config.get('rows', [])) > 0 or
                                            len(config.get('columns', [])) > 0 or
                                            len(config.get('values', [])) > 0)

                    if has_fields_configured:
                        st.warning("⚠️ **Analysis changed!** Previously selected fields may not be compatible. Please click 🔄 Reset button below to clear field configuration.")

            # Update last_analysis_id
            st.session_state['last_analysis_id'] = current_analysis_id

        st.markdown("---")

        # Field selection interface - Flexmonster style
        # Create two columns for header: title on left, reset button on right
        col_title, col_reset = st.columns([3, 1])
        with col_title:
            st.subheader("🎯 Step 3: Field Configuration")
        with col_reset:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            if st.button("🔄 Reset", key="reset_config_top", help="Reset all configuration"):
                st.session_state['pivot_config'] = {
                    'rows': [],
                    'columns': [],
                    'values': [],
                    'filters': {},
                    'aggregation': 'count',
                    'top_n': None,
                    'chart_sort_direction': 'descending'
                }
                # Update last_analysis_id to current analysis (no more warning after reset)
                st.session_state['last_analysis_id'] = current_analysis_id
                st.rerun()

        available_fields = list(df.columns)

        # Rows
        st.markdown("**📋 Rows**")
        rows = st.multiselect(
            "Drag fields to Rows",
            available_fields,
            default=st.session_state['pivot_config']['rows'],
            key="pivot_rows"
        )
        st.session_state['pivot_config']['rows'] = rows

        # Columns
        st.markdown("**📊 Columns**")
        columns = st.multiselect(
            "Drag fields to Columns",
            available_fields,
            default=st.session_state['pivot_config']['columns'],
            key="pivot_columns"
        )
        st.session_state['pivot_config']['columns'] = columns

        # Check for duplicate fields in rows and columns
        if rows and columns:
            duplicate_fields = set(rows) & set(columns)
            if duplicate_fields:
                st.warning(f"⚠️ Warning: The following field(s) appear in both Rows and Columns: {', '.join(duplicate_fields)}. This may cause errors. Please remove duplicates.")

        # Values
        st.markdown("**🔢 Values**")
        values = st.multiselect(
            "Drag fields to Values",
            available_fields,
            default=st.session_state['pivot_config']['values'],
            key="pivot_values"
        )
        st.session_state['pivot_config']['values'] = values

        # Aggregation function
        st.markdown("**🔄 Aggregation Function**")
        agg_func = st.selectbox(
            "Select aggregation",
            ['count', 'sum', 'mean', 'median', 'min', 'max', 'nunique'],
            index=['count', 'sum', 'mean', 'median', 'min', 'max', 'nunique'].index(st.session_state['pivot_config']['aggregation'])
        )
        st.session_state['pivot_config']['aggregation'] = agg_func

        # Top N Filter (Excel-style Value Filter)
        st.markdown("**🔝 Top N Filter**")
        current_top_n = st.session_state['pivot_config'].get('top_n')
        enable_top_n = st.checkbox("Enable Top N Filter", value=(current_top_n is not None and current_top_n.get('enabled', False)))
        if enable_top_n:
            st.info("💡 Filters items by their total value (like Excel's Value Filter)")

            # Get default values from config
            default_field = current_top_n.get('field', '') if current_top_n else ''
            default_n = current_top_n.get('n', 5) if current_top_n else 5
            default_type = current_top_n.get('type', 'top') if current_top_n else 'top'
            default_by_field = current_top_n.get('by_field', '') if current_top_n else ''

            # Select which field to filter
            filter_field_options = [col for col in available_fields if col not in ['Month', 'Analysis', 'DataSource', 'AnalysisType']]
            default_field_index = filter_field_options.index(default_field) if default_field in filter_field_options else 0
            top_n_field = st.selectbox(
                "Filter field (e.g., File Name, Hostname, Country)",
                filter_field_options,
                index=default_field_index,
                key='top_n_field'
            )

            # Select Top/Bottom
            top_or_bottom_options = ["Top", "Bottom"]
            default_type_index = 0 if default_type == 'top' else 1
            top_or_bottom = st.selectbox("Show", top_or_bottom_options, index=default_type_index, key='top_or_bottom')

            # Number of items
            top_n_value = st.number_input("Number of items", min_value=1, max_value=100, value=default_n, step=1)

            # Select value field to rank by
            value_field_options = [col for col in available_fields if 'Count' in col or 'Percentage' in col or col in values]
            if not value_field_options and values:
                value_field_options = values

            default_by_field_index = value_field_options.index(default_by_field) if default_by_field in value_field_options else 0
            top_n_by_field = st.selectbox(
                "Ranked by",
                value_field_options if value_field_options else ['Count'],
                index=default_by_field_index,
                key='top_n_by_field'
            )

            # Per-Month filtering option (for Time-Based Analysis)
            per_month_filter = False
            if 'Month' in available_fields:
                current_top_n = st.session_state['pivot_config'].get('top_n')
                default_per_month = current_top_n.get('per_month', False) if current_top_n else False
                per_month_filter = st.checkbox(
                    "📅 Apply Top N per Month",
                    value=default_per_month,
                    help="Show Top N items for EACH month separately (e.g., Top 3 dates per month for Daily Trends)"
                )

            st.session_state['pivot_config']['top_n'] = {
                'enabled': True,
                'field': top_n_field,
                'n': top_n_value,
                'type': top_or_bottom.lower(),
                'by_field': top_n_by_field,
                'per_month': per_month_filter
            }
        else:
            st.session_state['pivot_config']['top_n'] = None

        st.markdown("---")

        # Filters
        st.markdown("**🔍 Filters**")
        with st.expander("Add Filters", expanded=False):
            filter_field = st.selectbox("Select field to filter", ["None"] + available_fields)

            if filter_field != "None":
                unique_values = df[filter_field].unique()
                filter_values = st.multiselect(
                    f"Select {filter_field} values",
                    unique_values
                )

                if filter_values:
                    st.session_state['pivot_config']['filters'][filter_field] = filter_values

                # Show active filters
                if st.session_state['pivot_config']['filters']:
                    st.markdown("**Active Filters:**")
                    for fld, vals in st.session_state['pivot_config']['filters'].items():
                        st.write(f"• {fld}: {len(vals)} selected")
                        if st.button(f"Remove {fld}", key=f"remove_{fld}"):
                            del st.session_state['pivot_config']['filters'][fld]
                            st.rerun()

        st.markdown("---")

        # Chart configuration
        st.subheader("📈 Chart Settings")
        chart_types = ["Bar Chart", "Horizontal Bar", "Clustered Bar", "Horizontal Clustered Bar", "Stacked Bar", "Horizontal Stacked Bar", "Line Chart", "Area Chart", "Pie Chart", "Heatmap"]
        current_chart_type = st.session_state['pivot_config'].get('chart_type', 'Bar Chart')
        default_index = chart_types.index(current_chart_type) if current_chart_type in chart_types else 0

        chart_type = st.selectbox(
            "Chart Type",
            chart_types,
            index=default_index
        )
        st.session_state['pivot_config']['chart_type'] = chart_type

        chart_height = st.slider("Chart Height (px)", 300, 800, 500, 50)

        # Chart sort configuration
        st.markdown("**↕️ Chart Sort Order**")

        # Sort by field selection
        sort_by_options = ["Value (Detection Count)"] + available_fields
        current_sort_by = st.session_state['pivot_config'].get('sort_by_field', 'Value (Detection Count)')

        sort_by_field = st.selectbox(
            "Sort by",
            sort_by_options,
            index=sort_by_options.index(current_sort_by) if current_sort_by in sort_by_options else 0,
            help="Choose which field to sort the chart by"
        )
        st.session_state['pivot_config']['sort_by_field'] = sort_by_field

        # Sort direction (checkbox instead of radio)
        is_descending = st.session_state['pivot_config'].get('chart_sort_direction', 'descending') == 'descending'
        sort_descending = st.checkbox(
            "Descending (Z→A, 23→0, High→Low)",
            value=is_descending,
            help="Check for descending sort, uncheck for ascending sort"
        )
        st.session_state['pivot_config']['chart_sort_direction'] = 'descending' if sort_descending else 'ascending'

        # Severity Color Settings
        st.markdown("---")
        st.markdown("**🎨 Severity Color Scheme**")

        # Auto-detect if severity field exists in the data
        has_severity_field = False
        if df is not None and not df.empty:
            severity_columns = [col for col in df.columns if 'severity' in col.lower()]
            has_severity_field = len(severity_columns) > 0

        # Get default from config or auto-enable if severity detected
        default_use_severity_colors = st.session_state['pivot_config'].get('use_severity_colors', has_severity_field)

        use_severity_colors = st.checkbox(
            "Apply Severity Colors",
            value=default_use_severity_colors,
            help="Automatically color charts by severity level (Critical=Red, High=Orange, Medium=Blue, Low=Green)"
        )
        st.session_state['pivot_config']['use_severity_colors'] = use_severity_colors

        if use_severity_colors:
            st.caption("🔴 Critical  🟠 High  🔵 Medium  🟢 Low")

        # Ticket Status Color Settings
        st.markdown("---")
        st.markdown("**🎫 Ticket Status Colors**")

        # Auto-detect if Status field exists in the data
        has_status_field = False
        if df is not None and not df.empty:
            status_columns = [col for col in df.columns if 'status' in col.lower()]
            has_status_field = len(status_columns) > 0

        # Get default from config or auto-enable if status detected
        default_use_ticket_status_colors = st.session_state['pivot_config'].get('use_ticket_status_colors', has_status_field)

        use_ticket_status_colors = st.checkbox(
            "Apply Ticket Status Colors",
            value=default_use_ticket_status_colors,
            help="Automatically color charts by ticket status (Closed=Green, Open=Red, On-hold=Yellow, Pending=Grey)"
        )
        st.session_state['pivot_config']['use_ticket_status_colors'] = use_ticket_status_colors

        if use_ticket_status_colors:
            st.caption("🟢 Closed  🔴 Open  🟡 On-hold  ⚫ Pending")

        # Ticket Lifecycle Summary Configuration
        if analysis_category == "Ticket Lifecycle Analysis":
            st.markdown("---")
            st.markdown("**📊 Ticket Lifecycle Summary Settings**")
            st.caption("Configure the values shown in Section A.2 (Summary for Detections)")

            # Initialize ticket_lifecycle_summary if not exists
            if 'ticket_lifecycle_summary' not in st.session_state.get('pivot_config', {}):
                st.session_state['pivot_config']['ticket_lifecycle_summary'] = {}

            # Get current values from session state or defaults
            ticket_summary_config = st.session_state['pivot_config']['ticket_lifecycle_summary']

            col1, col2 = st.columns(2)
            with col1:
                total_alerts = st.number_input(
                    "🔢 Number of alerts triggered",
                    min_value=0,
                    value=ticket_summary_config.get('total_alerts', 17),
                    step=1,
                    help="Total number of alerts triggered this month",
                    key="config_total_alerts"
                )

            with col2:
                alerts_resolved = st.number_input(
                    "✅ Number of alerts resolved",
                    min_value=0,
                    value=ticket_summary_config.get('alerts_resolved', 16),
                    step=1,
                    help="Number of alerts that are closed/resolved",
                    key="config_alerts_resolved"
                )

            alerts_pending = st.number_input(
                "⏳ Number of alerts pending",
                min_value=0,
                value=ticket_summary_config.get('alerts_pending', 1),
                step=1,
                help="Number of alerts still in pending/open/on-hold/in_progress status",
                key="config_alerts_pending"
            )

            # Store in session state
            st.session_state['pivot_config']['ticket_lifecycle_summary'] = {
                'total_alerts': total_alerts,
                'alerts_resolved': alerts_resolved,
                'alerts_pending': alerts_pending
            }

            st.caption("💡 These values will be displayed in the Ticket Lifecycle Summary section")

        # Monthly Color Settings
        st.markdown("---")
        st.markdown("**📅 Monthly Trend Colors**")

        # Auto-detect if Month field exists in the data
        has_month_field = False
        if df is not None and not df.empty:
            has_month_field = 'Month' in df.columns

        # Get default from config or auto-enable if Month detected
        default_use_monthly_colors = st.session_state['pivot_config'].get('use_monthly_colors', has_month_field)

        use_monthly_colors_checkbox = st.checkbox(
            "Apply Monthly Colors",
            value=default_use_monthly_colors,
            help="Automatically color charts by month (1st month=Green, 2nd=Blue, 3rd=Gold)"
        )
        st.session_state['pivot_config']['use_monthly_colors'] = use_monthly_colors_checkbox

        if use_monthly_colors_checkbox:
            st.caption("🟢 Month 1 (oldest)  🔵 Month 2 (middle)  🟡 Month 3 (latest)")

        # Manual bar/category reordering
        st.markdown("---")
        st.markdown("**🔄 Manual Category Reordering**")
        enable_manual_order = st.checkbox(
            "Enable Manual Reordering",
            value=st.session_state['pivot_config'].get('manual_order_enabled', False),
            help="Manually control the order of categories/bars in the chart (overrides automatic sorting)"
        )
        st.session_state['pivot_config']['manual_order_enabled'] = enable_manual_order

        if enable_manual_order:
            st.caption("💡 After creating the pivot, you'll see a list of categories below. Use ⬆️ ⬇️ buttons to reorder them.")

            # Initialize manual order storage
            if 'manual_category_order' not in st.session_state['pivot_config']:
                st.session_state['pivot_config']['manual_category_order'] = []

            #The reordering interface will appear after the pivot table is created

        # Special selector for B1 Detection KEY METRICS independent bar chart
        if (analysis_category == "Detection & Severity Analysis" and
            selected_analysis_key == 'critical_high_overview'):
            st.markdown("---")
            st.markdown("**📊 B1 - Bar Chart Metrics**")
            st.caption("Select metrics to display in independent bar chart:")

            all_available_metrics = ['Total Detections', 'Unique Devices', 'Critical Detections', 'High Detections']

            selected_metrics_for_chart = st.multiselect(
                "Metrics for Bar Chart",
                options=all_available_metrics,
                default=['High Detections'],
                key="b1_chart_metrics",
                help="These metrics will appear in the independent bar chart (separate from card filters)"
            )

            # Store in session state
            st.session_state['b1_selected_metrics'] = selected_metrics_for_chart

        st.markdown("---")

        # Export options
        st.subheader("📥 Export Options")
        if st.button("📄 Export to PDF", type="primary"):
            st.session_state['export_pdf'] = True

        if st.button("📊 Download as Excel"):
            st.session_state['export_excel'] = True

    # Main content area
    st.markdown("---")

    # Apply filters to dataframe
    filtered_df = df.copy()
    for filter_field, filter_values in st.session_state['pivot_config']['filters'].items():
        if filter_field in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[filter_field].isin(filter_values)]

    # Apply TOP N filter (Excel-style Value Filter)
    top_n_config = st.session_state['pivot_config'].get('top_n')
    if top_n_config and top_n_config.get('enabled'):
        try:
            filter_field = top_n_config['field']
            n_value = top_n_config['n']
            filter_type = top_n_config['type']  # 'top' or 'bottom'
            by_field = top_n_config['by_field']
            per_month = top_n_config.get('per_month', False)

            if filter_field in filtered_df.columns and by_field in filtered_df.columns:
                # Check if per-month filtering is enabled
                if per_month and 'Month' in filtered_df.columns:
                    # Apply Top N PER MONTH
                    all_top_items = []
                    months = filtered_df['Month'].unique()

                    for month in months:
                        month_df = filtered_df[filtered_df['Month'] == month]

                        # Calculate total for each item in this month
                        totals = month_df.groupby(filter_field)[by_field].sum().reset_index()
                        totals = totals.rename(columns={by_field: '_total'})

                        # Get top N or bottom N items for this month
                        if filter_type == 'top':
                            top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                        else:  # bottom
                            top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()

                        # Store items with their month
                        for item in top_items:
                            all_top_items.append((month, item))

                    # Filter to show only Top N items per month
                    filtered_df = filtered_df[
                        filtered_df.apply(lambda row: (row['Month'], row[filter_field]) in all_top_items, axis=1)
                    ]

                    st.info(f"🔝 Showing {filter_type.title()} {n_value} {filter_field} per month by {by_field} ({len(months)} months × {n_value} = {len(months) * n_value} items)")
                else:
                    # Original global Top N filtering
                    # Calculate total for each item in the filter field
                    totals = filtered_df.groupby(filter_field)[by_field].sum().reset_index()
                    totals = totals.rename(columns={by_field: '_total'})

                    # Get top N or bottom N items
                    if filter_type == 'top':
                        top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                    else:  # bottom
                        top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()

                    # Filter dataframe to only include top/bottom N items
                    filtered_df = filtered_df[filtered_df[filter_field].isin(top_items)]

                    st.info(f"🔝 Showing {filter_type.title()} {n_value} items by {by_field} for {filter_field}")
        except Exception as e:
            st.warning(f"⚠️ Could not apply TOP N filter: {str(e)}")

    st.info(f"📊 Showing {len(filtered_df)} records (filtered from {len(df)} total)")

    # Generate pivot table
    config = st.session_state['pivot_config']

    if not config['rows'] and not config['columns']:
        st.info("👈 Select fields from the sidebar to build your pivot table")
        st.markdown("""
        ### How to use:

        1. **Select Data Source**: Choose which template to analyze (Host, Detection, or Time Analysis)
        2. **Configure Fields**:
           - **Rows**: Fields to group by vertically
           - **Columns**: Fields to group by horizontally
           - **Values**: Fields to aggregate (count, sum, etc.)
        3. **Add Filters**: Narrow down your data
        4. **Choose Chart Type**: Visualize your pivot table
        5. **Export**: Download as PDF or Excel

        **Example Configurations:**

        **📊 LONG FORMAT Examples (Excel Pivot Table Ready):**

        **Host Analysis - KEY METRICS Pivot:**
        - Rows: KEY METRICS
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        *(Creates pivot like: Metrics as rows, months as columns)*

        **Detection Analysis - B1. Critical and High Detection Overview:**
        - Rows: KEY METRICS
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        *(Creates pivot with metrics as rows, months as columns - shows card visualization)*

        **Host Analysis - TOP HOSTS Trend:**
        - Rows: TOP HOSTS WITH MOST DETECTIONS
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        - Enable Top N Filter: Check ✓, Set to 5
        *(Creates pivot showing top 5 host detections across months)*

        **Host Analysis - User Analysis:**
        - Rows: Username
        - Columns: Month
        - Values: Count of Detection
        - Aggregation: sum
        *(Shows user detection counts across months)*

        **Host Analysis - Sensor Analysis:**
        - Rows: Month, Sensor Version
        - Columns: Status
        - Values: Host Count
        - Aggregation: sum
        *(Shows sensor versions by status across months)*

        **Detection Analysis - B2. Detection Count by Severity:**
        - Rows: SeverityName
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        *(Shows severity distribution across months)*

        **Detection Analysis - B3. Detection Count Across Country:**
        - Rows: Country
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        *(Shows detections by country across months)*

        **Detection Analysis - B4. Files with Most Detections:**
        - Rows: FileName
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        - Enable Top N Filter: Check ✓, Set to 5
        *(Shows top 5 files with most detections)*

        **Detection Analysis - B5. Tactics by Severity:**
        - Rows: Month, SeverityName
        - Columns: Tactic
        - Values: Count
        - Aggregation: sum
        *(Shows tactics grouped by severity and month)*

        **Detection Analysis - B6. Technique by Severity:**
        - Rows: SeverityName, Month
        - Columns: Technique
        - Values: Count
        - Aggregation: sum
        *(Shows techniques grouped by severity and month)*

        **Time Analysis - HOURLY Pattern:**
        - Rows: Hour
        - Columns: Month
        - Values: Count
        - Aggregation: sum
        *(Shows hourly detection patterns across months)*

        **📝 Note:** All analysis outputs are now in LONG FORMAT with standardized columns:
        - Dimension columns (KEY METRICS, Hostname, SeverityName, etc.)
        - Month (always included)
        - Analysis/AnalysisType (data source identifier)
        - DataSource (data source identifier)
        - Count/Host Count/Count of Detection (the metric value)
        - Percentage (where applicable)

        This format is **ready to paste directly into Excel** for pivot table analysis!

        **🎯 Using Top N Filter:**
        1. Check "Enable Top N Filter" checkbox in the sidebar
        2. Set the number (e.g., 5 for top 5 items)
        3. The pivot table will automatically filter to show only the top N items by total value
        4. Charts will display sorted with highest values on the left
        """)

        # Show data preview
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(filtered_df.head(20), use_container_width=True)

        return

    # Create pivot table
    try:
        pivot_table = create_pivot_table(filtered_df, config, selected_analysis_key)

        if pivot_table is not None and not pivot_table.empty:
            # Display pivot table
            st.subheader("📊 Pivot Table")
            st.dataframe(pivot_table, use_container_width=True)

            # Download pivot table as CSV
            csv = pivot_table.to_csv()
            st.download_button(
                label="📥 Download Pivot Table (CSV)",
                data=csv,
                file_name=f"pivot_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

            # Show manual reordering interface in main area if enabled
            if st.session_state['pivot_config'].get('manual_order_enabled', False):
                with st.expander("🔄 Manual Reordering", expanded=True):
                    st.info("Reorder X-axis categories AND colored bars/series. Changes apply immediately to the chart.")

                    # Create tabs for different reordering types
                    tab1, tab2 = st.tabs(["📊 X-Axis Categories (Rows)", "🎨 Data Series (Columns)"])

                    # TAB 1: Reorder X-axis categories (Rows)
                    with tab1:
                        rows = config['rows']
                        if rows and len(rows) >= 1:
                            # Get unique category combinations
                            if len(rows) == 2:
                                # Hierarchical labels
                                categories = pivot_table.apply(
                                    lambda row: f"{row[rows[1]]}<br>{row[rows[0]]}" if rows[1] in pivot_table.columns and rows[0] in pivot_table.columns else str(row[rows[0]]),
                                    axis=1
                                ).tolist()
                            elif len(rows) == 1 and rows[0] in pivot_table.columns:
                                categories = pivot_table[rows[0]].unique().tolist()
                            else:
                                categories = []

                            if categories:
                                # Initialize manual order if not set
                                if not st.session_state['pivot_config'].get('manual_category_order'):
                                    st.session_state['pivot_config']['manual_category_order'] = categories.copy()

                                manual_order = st.session_state['pivot_config']['manual_category_order']

                                # Display reorderable list
                                st.caption(f"**{len(manual_order)} categories** (Position 1 = Leftmost/First)")

                                for i, category in enumerate(manual_order):
                                    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

                                    with col1:
                                        st.text(f"{i+1}. {category}")

                                    with col2:
                                        if i > 0:
                                            if st.button("⬆️", key=f"cat_up_{i}_{category}"):
                                                manual_order[i], manual_order[i-1] = manual_order[i-1], manual_order[i]
                                                st.session_state['pivot_config']['manual_category_order'] = manual_order
                                                st.rerun()

                                    with col3:
                                        if i < len(manual_order) - 1:
                                            if st.button("⬇️", key=f"cat_down_{i}_{category}"):
                                                manual_order[i], manual_order[i+1] = manual_order[i+1], manual_order[i]
                                                st.session_state['pivot_config']['manual_category_order'] = manual_order
                                                st.rerun()

                                if st.button("🔄 Reset Categories to Auto"):
                                    st.session_state['pivot_config']['manual_category_order'] = categories.copy()
                                    st.rerun()

                    # TAB 2: Reorder data series (Columns) - the colored bars!
                    with tab2:
                        columns = config['columns']
                        if columns and len(columns) >= 1:
                            # Get data series names (column values that create the colored bars)
                            # These are the actual column names in the pivot table (after pivoting)
                            numeric_cols = [col for col in pivot_table.columns if col not in rows and pd.api.types.is_numeric_dtype(pivot_table[col])]

                            if numeric_cols:
                                # Initialize manual series order if not set
                                if not st.session_state['pivot_config'].get('manual_series_order'):
                                    st.session_state['pivot_config']['manual_series_order'] = numeric_cols.copy()

                                series_order = st.session_state['pivot_config']['manual_series_order']

                                # Display reorderable list
                                st.caption(f"**{len(series_order)} data series** (Position 1 = First colored bar in each category)")
                                st.caption("💡 These are the different colored bars within each X-axis category")

                                for i, series in enumerate(series_order):
                                    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

                                    with col1:
                                        st.text(f"{i+1}. {series}")

                                    with col2:
                                        if i > 0:
                                            if st.button("⬆️", key=f"series_up_{i}_{series}"):
                                                series_order[i], series_order[i-1] = series_order[i-1], series_order[i]
                                                st.session_state['pivot_config']['manual_series_order'] = series_order
                                                st.rerun()

                                    with col3:
                                        if i < len(series_order) - 1:
                                            if st.button("⬇️", key=f"series_down_{i}_{series}"):
                                                series_order[i], series_order[i+1] = series_order[i+1], series_order[i]
                                                st.session_state['pivot_config']['manual_series_order'] = series_order
                                                st.rerun()

                                if st.button("🔄 Reset Series to Auto"):
                                    st.session_state['pivot_config']['manual_series_order'] = numeric_cols.copy()
                                    st.rerun()
                            else:
                                st.warning("No data series found. This feature works when you have values in the Columns field.")
                        else:
                            st.warning("No columns selected. Add fields to the Columns area to reorder data series.")

            # Generate visualization
            st.subheader("📈 Visualization")

            # Special handling for Detection Analysis B1 - KEY METRICS
            if (analysis_category == "Detection & Severity Analysis" and
                selected_analysis_key == 'critical_high_overview'):

                # PART 1: Card Visualization (respects filters)
                st.markdown("#### 📊 Card View")
                st.info("💡 Card visualization respects filter selections above")
                create_detection_key_metrics_cards(filtered_df)

                st.markdown("---")

                # PART 2: Independent Bar Chart (does NOT respect filters)
                st.markdown("#### 📈 Bar Chart View (Independent)")
                st.info("💡 Bar chart metrics are selected in the sidebar under 'Chart Settings'")

                # Get selected metrics from session state (set in sidebar)
                selected_metrics_for_chart = st.session_state.get('b1_selected_metrics', ['High Detections'])

                if selected_metrics_for_chart:
                    # Filter the ORIGINAL df (not filtered_df) to get all data for selected metrics
                    # This ensures bar chart is independent of card filters
                    chart_df = df[df['KEY METRICS'].isin(selected_metrics_for_chart)]

                    # Create bar chart
                    chart = create_detection_key_metrics_bar_chart(chart_df, chart_height)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                else:
                    st.warning("⚠️ Please select at least one metric in the sidebar (Chart Settings → B1 - Bar Chart Metrics)")

            else:
                # Normal chart visualization for all analyses (including B2 TOP SEVERITIES)
                chart = create_pivot_chart(pivot_table, chart_type, chart_height, config, selected_analysis_key)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

            # Export to PDF
            if st.session_state.get('export_pdf', False):
                pdf_buffer = export_to_pdf(pivot_table, chart, config, data_source)
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"pivot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.session_state['export_pdf'] = False

            # Export to Excel
            if st.session_state.get('export_excel', False):
                excel_buffer = export_to_excel(pivot_table, config, data_source)
                st.download_button(
                    label="📥 Download Excel Report",
                    data=excel_buffer,
                    file_name=f"pivot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.session_state['export_excel'] = False

            # Show insights
            with st.expander("🔍 Insights & Statistics", expanded=False):
                show_pivot_insights(pivot_table, config)

        else:
            st.warning("⚠️ No data available with current configuration. Try adjusting your filters or field selection.")

    except Exception as e:
        st.error(f"❌ Error creating pivot table: {str(e)}")
        st.info("💡 Tip: Make sure your field selections are compatible with the aggregation function chosen.")


def create_pivot_table(df, config, selected_analysis_key=None):
    """Create pivot table based on configuration"""
    rows = config['rows']
    columns = config['columns']
    values = config['values']
    agg_func = config['aggregation']

    try:
        if not rows and not columns:
            return None

        # Check for duplicate fields in rows and columns
        if rows and columns:
            duplicate_fields = set(rows) & set(columns)
            if duplicate_fields:
                st.error(f"❌ Error: The following field(s) cannot appear in both Rows and Columns: {', '.join(duplicate_fields)}")
                st.info("💡 Please remove the duplicate field(s) from either Rows or Columns.")
                return None

        # If no values specified, count all records
        if not values:
            if rows and columns:
                pivot = pd.crosstab(
                    index=[df[r] for r in rows],
                    columns=[df[c] for c in columns],
                    margins=True,
                    margins_name="Total"
                )
                # Reset index to flatten MultiIndex for display
                pivot = pivot.reset_index()
            elif rows:
                pivot = df.groupby(rows).size().reset_index(name='Count')
            elif columns:
                pivot = df.groupby(columns).size().reset_index(name='Count')
            else:
                pivot = df
        else:
            # Use specified values
            if rows and columns:
                # Create pivot table with both rows and columns
                pivot = pd.pivot_table(
                    df,
                    values=values[0] if len(values) == 1 else values,
                    index=rows,
                    columns=columns,
                    aggfunc=agg_func,
                    fill_value=0,
                    margins=True,
                    margins_name="Total"
                )
                # Reset index to flatten MultiIndex for display
                pivot = pivot.reset_index()
            elif rows:
                # Only rows specified
                if agg_func == 'count':
                    pivot = df.groupby(rows)[values].count().reset_index()
                elif agg_func == 'sum':
                    pivot = df.groupby(rows)[values].sum().reset_index()
                elif agg_func == 'mean':
                    pivot = df.groupby(rows)[values].mean().reset_index()
                elif agg_func == 'median':
                    pivot = df.groupby(rows)[values].median().reset_index()
                elif agg_func == 'min':
                    pivot = df.groupby(rows)[values].min().reset_index()
                elif agg_func == 'max':
                    pivot = df.groupby(rows)[values].max().reset_index()
                elif agg_func == 'nunique':
                    pivot = df.groupby(rows)[values].nunique().reset_index()
                else:
                    pivot = df.groupby(rows)[values].agg(agg_func).reset_index()
            elif columns:
                # Only columns specified
                if agg_func == 'count':
                    pivot = df.groupby(columns)[values].count().reset_index()
                elif agg_func == 'sum':
                    pivot = df.groupby(columns)[values].sum().reset_index()
                elif agg_func == 'mean':
                    pivot = df.groupby(columns)[values].mean().reset_index()
                elif agg_func == 'median':
                    pivot = df.groupby(columns)[values].median().reset_index()
                elif agg_func == 'min':
                    pivot = df.groupby(columns)[values].min().reset_index()
                elif agg_func == 'max':
                    pivot = df.groupby(columns)[values].max().reset_index()
                elif agg_func == 'nunique':
                    pivot = df.groupby(columns)[values].nunique().reset_index()
                else:
                    pivot = df.groupby(columns)[values].agg(agg_func).reset_index()
            else:
                pivot = df

        # TOP N filtering is now applied to SOURCE DATA before creating pivot (see lines 322-347)
        # No need to filter the pivot table itself

        # Sort months chronologically if Month is in the data
        if 'Month' in pivot.columns:
            # Define month order
            month_order = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12,
                # Handle abbreviated formats
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }

            # Create a sort key for months
            def get_month_sort_key(month_str):
                if pd.isna(month_str) or month_str == 'Total':
                    return 999  # Put Total at the end
                # Try to extract month name from string like "June 2025"
                for month_name, order in month_order.items():
                    if month_name in str(month_str):
                        return order
                return 0

            pivot['_month_sort'] = pivot['Month'].apply(get_month_sort_key)

            # Sort by other criteria if they exist, then by month
            if rows and len(rows) > 0 and values and len(values) > 0:
                # If we have a row field and value, sort by value descending, then month ascending
                pivot = pivot.sort_values(['_month_sort'], ascending=[True])
            else:
                pivot = pivot.sort_values('_month_sort')

            pivot = pivot.drop(columns=['_month_sort'])

        return pivot

    except Exception as e:
        st.error(f"Error creating pivot: {str(e)}")
        return None


def create_detection_key_metrics_cards(df):
    """
    Create card-based visualization for Detection Analysis B1 - KEY METRICS
    Shows cards for metrics that exist in the FILTERED dataframe
    Respects user filter selections - only shows filtered metrics
    """
    try:
        # Get ONLY the metrics that exist in the filtered dataframe
        # This respects the user's filter selections
        if 'KEY METRICS' in df.columns:
            available_metrics = df['KEY METRICS'].unique().tolist()
        else:
            available_metrics = []

        if not available_metrics:
            st.info("📊 No metrics to display with current filter selection.")
            return

        # Define the order for metrics (if they exist in filtered data)
        metric_order = ['Total Detections', 'Unique Devices', 'Critical Detections', 'High Detections']

        # Sort available metrics by the defined order
        all_metrics = [m for m in metric_order if m in available_metrics]

        # Get unique months and sort chronologically
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

        if 'Month' in df.columns:
            months = sorted(df['Month'].unique(), key=get_month_sort_key)
        else:
            months = ['Single Month']

        # Color scheme for each metric (matching image - teal/dark theme)
        metric_colors = {
            'Total Detections': '#1e5a5a',      # Dark teal
            'Unique Devices': '#2d7a7a',        # Medium teal
            'Critical Detections': '#3d9a9a',   # Light teal
            'High Detections': '#4dbaba'        # Lighter teal
        }

        # Display cards for EACH metric
        for metric in all_metrics:
            st.markdown(f"### {metric}")

            # Create columns for each month
            cols = st.columns(len(months))

            for idx, month in enumerate(months):
                with cols[idx]:
                    # Filter data for this metric and month
                    if 'Month' in df.columns:
                        filtered = df[(df['KEY METRICS'] == metric) & (df['Month'] == month)]
                    else:
                        filtered = df[df['KEY METRICS'] == metric]

                    # Get count value
                    if not filtered.empty and 'Count' in filtered.columns:
                        count_value = int(filtered['Count'].iloc[0])
                    else:
                        count_value = 0

                    # Get color for this metric
                    card_color = metric_colors.get(metric, '#1e5a5a')

                    # Create card using HTML/CSS
                    card_html = f"""
                    <div style="
                        background-color: {card_color};
                        border-radius: 10px;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        margin-bottom: 15px;
                    ">
                        <div style="
                            font-size: 16px;
                            color: white;
                            font-weight: 600;
                            margin-bottom: 10px;
                        ">{month}</div>
                        <div style="
                            font-size: 48px;
                            color: white;
                            font-weight: bold;
                            margin: 15px 0;
                        ">{count_value}</div>
                        <div style="
                            font-size: 14px;
                            color: rgba(255, 255, 255, 0.9);
                            font-weight: 500;
                        ">{metric}</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error creating card visualization: {str(e)}")
        st.info("💡 Falling back to standard chart visualization")


def create_severity_trend_stacked_bar_chart(df, height):
    """
    Create stacked bar chart for Detection Analysis B2 - Severity Trend
    Fixed colors: High=Orange, Medium=Blue, Low=Green
    Shows months on X-axis with stacked severity bars
    """
    try:
        if df.empty:
            st.warning("No data available for severity trend chart")
            return None

        # Sort months chronologically
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

        # Get unique months sorted chronologically
        if 'Month' in df.columns:
            months = sorted(df['Month'].unique(), key=get_month_sort_key)
        else:
            months = ['Single Month']

        # FIXED severity colors (Global Standard)
        severity_colors = {
            'Critical': '#DC143C',  # Crimson Red (if exists)
            'High': '#ED7D31',      # Orange
            'Medium': '#5B9BD5',    # Blue/Teal
            'Low': '#70AD47'        # Green
        }

        # Severity order for stacking (High -> Medium -> Low from bottom to top)
        severity_order = ['Low', 'Medium', 'High']

        # Create stacked bar chart
        fig = go.Figure()

        # Add bars for each severity level
        for severity in severity_order:
            counts = []
            for month in months:
                # Filter for this severity and month
                severity_data = df[(df['SeverityName'].str.contains(severity, case=False, na=False)) &
                                  (df['Month'] == month)]

                if not severity_data.empty and 'Count' in severity_data.columns:
                    counts.append(int(severity_data['Count'].sum()))
                else:
                    counts.append(0)

            color = severity_colors.get(severity, '#808080')

            fig.add_trace(go.Bar(
                name=severity,
                x=months,
                y=counts,
                marker_color=color,
                text=counts,
                textposition='inside',
                textfont=dict(color='white', size=12)
            ))

        fig.update_layout(
            title="Detection Count by Severity (3 Months Trend)",
            xaxis_title="Month",
            yaxis_title="Count",
            barmode='stack',
            height=height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            showlegend=True
        )

        return fig

    except Exception as e:
        st.error(f"Error creating severity trend chart: {str(e)}")
        return None


def create_detection_key_metrics_bar_chart(df, height):
    """
    Create independent bar chart for Detection Analysis B1 - KEY METRICS
    Shows selected metrics on X-axis with months as grouped bars
    """
    try:
        if df.empty:
            st.warning("No data available for bar chart")
            return None

        # Sort months chronologically
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

        # Get unique months and metrics
        if 'Month' in df.columns:
            months = sorted(df['Month'].unique(), key=get_month_sort_key)
        else:
            months = ['Single Month']

        # Define metric order
        metric_order = ['Total Detections', 'Unique Devices', 'Critical Detections', 'High Detections']
        available_metrics = df['KEY METRICS'].unique().tolist()
        metrics = [m for m in metric_order if m in available_metrics]

        # Create grouped bar chart with METRICS on X-axis
        fig = go.Figure()

        # Global Standard: Monthly Trend Colors
        # Assign colors based on chronological position (1st month = green, 2nd = blue, 3rd = gold)
        month_color_mapping = {}
        if len(months) >= 1:
            month_color_mapping[months[0]] = '#70AD47'  # Green (oldest month)
        if len(months) >= 2:
            month_color_mapping[months[1]] = '#5B9BD5'  # Blue (middle month)
        if len(months) >= 3:
            month_color_mapping[months[2]] = '#FFC000'  # Gold (latest month)

        # Add a bar for each MONTH (months become the groups)
        for month in months:
            month_data = df[df['Month'] == month]

            # Get counts for each metric
            counts = []
            for metric in metrics:
                metric_data = month_data[month_data['KEY METRICS'] == metric]
                if not metric_data.empty and 'Count' in metric_data.columns:
                    counts.append(int(metric_data['Count'].iloc[0]))
                else:
                    counts.append(0)

            color = month_color_mapping.get(month, '#999999')

            fig.add_trace(go.Bar(
                name=month,
                x=metrics,
                y=counts,
                marker_color=color,
                # Removed text labels on top of bars
            ))

        fig.update_layout(
            # Removed title
            xaxis_title="Total",
            yaxis_title="Count",
            barmode='group',
            height=height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    except Exception as e:
        st.error(f"Error creating bar chart: {str(e)}")
        return None


def create_pivot_chart(pivot_table, chart_type, height, config, selected_analysis_key=None):
    """Create chart from pivot table with fixed color schemes for severity and monthly trends"""
    try:
        if pivot_table is None or pivot_table.empty:
            return None

        # FIXED COLOR SCHEMES (Global Standard)
        SEVERITY_COLORS = {
            'Critical': '#DC143C',  # Crimson Red (Critical only)
            'High': '#ED7D31',      # Orange
            'Medium': '#5B9BD5',    # Blue/Teal
            'Low': '#70AD47'        # Green
        }

        MONTHLY_COLORS = {
            'month_1': '#70AD47',   # Green (oldest month)
            'month_2': '#5B9BD5',   # Blue (middle month)
            'month_3': '#FFC000'    # Gold (latest month)
        }

        TICKET_STATUS_COLORS = {
            'Closed': '#70AD47',    # Green (resolved)
            'Open': '#DC143C',      # Red (needs attention)
            'On-hold': '#FFC000',   # Yellow (paused)
            'Pending': '#A9A9A9'    # Grey (waiting)
        }

        # Remove 'Total' row/column for cleaner visualization
        clean_pivot = pivot_table.copy()

        # Remove Total from index (rows)
        if 'Total' in clean_pivot.index:
            clean_pivot = clean_pivot.drop('Total')

        # Remove Total from columns
        if isinstance(clean_pivot.columns, pd.MultiIndex):
            if 'Total' in clean_pivot.columns.get_level_values(0):
                clean_pivot = clean_pivot.drop('Total', axis=1, level=0)
        elif 'Total' in clean_pivot.columns:
            clean_pivot = clean_pivot.drop('Total', axis=1)

        # Also filter out any rows where any column equals 'Total'
        for col in clean_pivot.columns:
            if clean_pivot[col].dtype == 'object':
                clean_pivot = clean_pivot[clean_pivot[col] != 'Total']

        rows = config['rows']
        columns = config['columns']
        values = config.get('values', [])

        # Month order for chronological sorting (define BEFORE using it)
        month_order = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
            'June': 6, 'July': 7, 'August': 8  # Full month names
        }

        def get_month_sort_key(month_str):
            if pd.isna(month_str):
                return 999
            for month_name, order in month_order.items():
                if month_name in str(month_str):
                    return order
            return 0

        # Detect data type and assign colors (NOW after month_order is defined)
        # Check if Month is in the pivot columns OR in the config columns (before pivot)
        has_month = 'Month' in clean_pivot.columns or 'Month' in columns or 'Month' in rows

        # Get plot columns (exclude row fields)
        plot_cols = [col for col in clean_pivot.columns if col not in rows]

        # Check if columns contain severity levels (Critical, High, Medium, Low)
        severity_keywords = ['critical', 'high', 'medium', 'low']
        has_severity = any(any(keyword in str(col).lower() for keyword in severity_keywords) for col in plot_cols)

        # Check if columns contain ticket status (Open, Pending, On-hold, Closed)
        ticket_status_keywords = ['open', 'pending', 'on-hold', 'closed']
        has_ticket_status = any(any(keyword in str(col).lower() for keyword in ticket_status_keywords) for col in plot_cols)

        # Determine which color scheme to use
        use_severity_colors = False
        use_ticket_status_colors = False
        use_monthly_colors = False
        color_mapping = {}

        # Check if user enabled color schemes in settings
        user_enabled_severity_colors = config.get('use_severity_colors', False)
        user_enabled_ticket_status_colors = config.get('use_ticket_status_colors', False)
        user_enabled_monthly_colors = config.get('use_monthly_colors', True)  # Default True for backwards compatibility

        # Priority: Severity colors > Ticket Status colors > Monthly colors
        if user_enabled_severity_colors and has_severity:
            # Use severity colors for charts with severity data
            use_severity_colors = True
            for col in plot_cols:
                col_str = str(col)
                if 'critical' in col_str.lower():
                    color_mapping[col] = SEVERITY_COLORS['Critical']
                elif 'high' in col_str.lower():
                    color_mapping[col] = SEVERITY_COLORS['High']
                elif 'medium' in col_str.lower():
                    color_mapping[col] = SEVERITY_COLORS['Medium']
                elif 'low' in col_str.lower():
                    color_mapping[col] = SEVERITY_COLORS['Low']

        elif user_enabled_ticket_status_colors and has_ticket_status:
            # Use ticket status colors for charts with ticket status data
            use_ticket_status_colors = True
            for col in plot_cols:
                col_str = str(col)
                if 'closed' in col_str.lower():
                    color_mapping[col] = TICKET_STATUS_COLORS['Closed']
                elif 'open' in col_str.lower():
                    color_mapping[col] = TICKET_STATUS_COLORS['Open']
                elif 'on-hold' in col_str.lower() or 'onhold' in col_str.lower():
                    color_mapping[col] = TICKET_STATUS_COLORS['On-hold']
                elif 'pending' in col_str.lower():
                    color_mapping[col] = TICKET_STATUS_COLORS['Pending']

        elif user_enabled_monthly_colors and has_month and columns:
            # Use monthly colors for month trend charts (without severity)
            use_monthly_colors = True

            # Check if Month is in columns or rows
            if 'Month' in columns or any('Month' in str(c) for c in columns):
                # Month is in columns - color the month columns
                plot_cols = [col for col in clean_pivot.columns if col not in rows]
                # Find all month columns
                month_cols = sorted([c for c in plot_cols if any(m in str(c) for m in month_order.keys())],
                                  key=lambda x: get_month_sort_key(x))

                for idx, month_col in enumerate(month_cols):
                    if idx == 0:
                        color_mapping[month_col] = MONTHLY_COLORS['month_1']
                    elif idx == 1:
                        color_mapping[month_col] = MONTHLY_COLORS['month_2']
                    elif idx == 2:
                        color_mapping[month_col] = MONTHLY_COLORS['month_3']
            elif 'Month' in rows or any('Month' in str(r) for r in rows):
                # Month is in rows - color the column series (KEY METRICS, etc.)
                # This handles Host Analysis #1 (rows=Month, columns=KEY METRICS)
                plot_cols = [col for col in clean_pivot.columns if col not in rows]
                # Since Month is in rows, the bars represent different columns (metrics)
                # We want to color by month, so we need to create separate traces per month
                # This will be handled differently in the bar chart generation
                # For now, assign default colors to metrics
                for idx, col in enumerate(plot_cols):
                    if idx < 3:
                        color_mapping[col] = ['#5B9BD5', '#70AD47', '#FFC000'][idx]  # Default metric colors

        # Get chart sort direction from config
        chart_sort_direction = config.get('chart_sort_direction', 'descending')
        sort_ascending = (chart_sort_direction == 'ascending')

        # Determine how to sort based on rows and columns configuration
        if rows and columns:
            # We have both rows and columns
            # Two cases:
            # 1. Month in COLUMNS (e.g., TOP HOSTS in rows, Month in columns) - sort ROWS by TOTAL
            # 2. Month in ROWS (e.g., Month in rows, Hostnames in columns) - sort rows chronologically, columns by total

            if any('Month' in str(c) for c in columns) and 'Month' not in rows:
                # Case 1: Month in columns, non-month dimension in rows
                # Check if rows contain SeverityName - if so, sort by severity order
                has_severity_rows = any('severity' in str(r).lower() for r in rows)

                numeric_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if numeric_cols and rows and len(rows) > 0:
                    if has_severity_rows and 'SeverityName' in clean_pivot.columns:
                        # Sort rows by severity order: Critical > High > Medium > Low
                        severity_order_map = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}

                        def get_severity_row_sort_key(row):
                            severity = row['SeverityName']
                            return severity_order_map.get(severity, 999)

                        clean_pivot['_severity_sort'] = clean_pivot.apply(get_severity_row_sort_key, axis=1)
                        clean_pivot = clean_pivot.sort_values('_severity_sort')
                        clean_pivot = clean_pivot.drop(columns=['_severity_sort'])
                    else:
                        # Sort ROWS by TOTAL across all month columns (highest total on left)
                        clean_pivot['_row_total'] = clean_pivot[numeric_cols].sum(axis=1)
                        # Sort by total (descending = highest first, ascending = lowest first)
                        clean_pivot = clean_pivot.sort_values('_row_total', ascending=sort_ascending)
                        clean_pivot = clean_pivot.drop(columns=['_row_total'])

                # Also sort month columns chronologically
                month_cols = [col for col in numeric_cols if any(m in str(col) for m in month_order.keys())]
                if month_cols:
                    # Sort month columns chronologically
                    month_col_order = sorted(month_cols, key=lambda x: get_month_sort_key(x))
                    other_cols = [col for col in clean_pivot.columns if col not in month_cols]
                    clean_pivot = clean_pivot[other_cols + month_col_order]

            elif any('Month' in str(r) for r in rows) and 'Month' in clean_pivot.columns:
                # Case 2: Month in rows
                # Sort rows chronologically by month
                clean_pivot['_month_sort'] = clean_pivot['Month'].apply(get_month_sort_key)
                clean_pivot = clean_pivot.sort_values('_month_sort')
                clean_pivot = clean_pivot.drop(columns=['_month_sort'])

                # Sort columns (non-month dimensions)
                numeric_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if numeric_cols:
                    # Check if columns are severity levels - if so, sort by severity order
                    severity_keywords = ['critical', 'high', 'medium', 'low']
                    has_severity_cols = any(any(keyword in str(col).lower() for keyword in severity_keywords) for col in numeric_cols)

                    if has_severity_cols:
                        # Sort by severity order: Critical > High > Medium > Low
                        severity_order_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}

                        def get_severity_sort_key(col):
                            col_lower = str(col).lower()
                            for sev, order in severity_order_map.items():
                                if sev in col_lower:
                                    return order
                            return 999  # Non-severity columns at end

                        sorted_col_names = sorted(numeric_cols, key=get_severity_sort_key)
                    else:
                        # Sort by total value for non-severity columns
                        col_totals = {col: clean_pivot[col].sum() for col in numeric_cols}
                        sorted_cols = sorted(col_totals.items(), key=lambda x: x[1], reverse=(not sort_ascending))
                        sorted_col_names = [col for col, _ in sorted_cols]

                    # Reorder columns
                    other_cols = [col for col in clean_pivot.columns if col not in numeric_cols]
                    clean_pivot = clean_pivot[other_cols + sorted_col_names]
            else:
                # No month dimension - sort by row totals
                numeric_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if numeric_cols and rows and len(rows) > 0:
                    clean_pivot['_row_total'] = clean_pivot[numeric_cols].sum(axis=1)
                    clean_pivot = clean_pivot.sort_values('_row_total', ascending=sort_ascending)
                    clean_pivot = clean_pivot.drop(columns=['_row_total'])

        elif rows and not columns:
            # Only rows (simple grouping) - sort by the selected field or value column
            numeric_cols = clean_pivot.select_dtypes(include=[np.number]).columns.tolist()

            # Check if user selected a custom sort field
            sort_by_field = config.get('sort_by_field', 'Value (Detection Count)')

            if sort_by_field != 'Value (Detection Count)' and sort_by_field in clean_pivot.columns:
                # User selected a specific field to sort by (e.g., Hour, Date, Day)
                sort_field = sort_by_field

                # Special handling for Hour field (need to sort numerically)
                if sort_field == 'Hour':
                    # Extract numeric hour from "HH:00" format for proper sorting
                    clean_pivot['_hour_num'] = clean_pivot['Hour'].str.extract(r'(\d+):', expand=False).astype(int)
                    clean_pivot = clean_pivot.sort_values('_hour_num', ascending=not sort_ascending)
                    clean_pivot = clean_pivot.drop(columns=['_hour_num'])
                # Special handling for Day field (Monday → Sunday)
                elif sort_field == 'Day':
                    # Use Sort column for proper day ordering (Monday=1, Sunday=7)
                    if 'Sort' in clean_pivot.columns:
                        # Ascending: Monday (1) → Sunday (7)
                        # Descending: Sunday (7) → Monday (1)
                        clean_pivot = clean_pivot.sort_values('Sort', ascending=(not sort_ascending))
                        print(f"[DEBUG] Sorting by Day using Sort column, ascending={not sort_ascending}")
                    else:
                        # Fallback: manual day order
                        day_order_map = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
                                        'Friday': 5, 'Saturday': 6, 'Sunday': 7}
                        clean_pivot['_day_sort'] = clean_pivot['Day'].map(day_order_map).fillna(99)
                        clean_pivot = clean_pivot.sort_values('_day_sort', ascending=(not sort_ascending))
                        clean_pivot = clean_pivot.drop(columns=['_day_sort'])
                        print(f"[DEBUG] Sorting by Day using manual order, ascending={not sort_ascending}")
                # Special handling for Sort field (if exists)
                elif 'Sort' in clean_pivot.columns and sort_field in rows:
                    # Use Sort column for proper ordering
                    clean_pivot = clean_pivot.sort_values('Sort', ascending=not sort_ascending)
                # Special handling for Month field
                elif sort_field == 'Month':
                    clean_pivot['_month_sort'] = clean_pivot['Month'].apply(get_month_sort_key)
                    clean_pivot = clean_pivot.sort_values('_month_sort', ascending=not sort_ascending)
                    clean_pivot = clean_pivot.drop(columns=['_month_sort'])
                else:
                    # Regular field - sort alphabetically or numerically
                    clean_pivot = clean_pivot.sort_values(sort_field, ascending=not sort_ascending)

            elif numeric_cols and len(numeric_cols) > 0:
                # Default: Sort by value (only if user hasn't selected a custom sort field)
                # Special handling for Daily Trends: Sort by Month, then by Detection Count (descending)
                if 'Month' in clean_pivot.columns and 'Date' in rows and sort_by_field == 'Value (Detection Count)':
                    # Daily Trends: Sort by Month (chronologically), then by Detection Count (highest first)
                    clean_pivot['_month_sort'] = clean_pivot['Month'].apply(get_month_sort_key)
                    # Sort by month first, then by detection count (descending for highest on left)
                    clean_pivot = clean_pivot.sort_values(['_month_sort', numeric_cols[0]], ascending=[True, not sort_ascending])
                    clean_pivot = clean_pivot.drop(columns=['_month_sort'])
                    print(f"[DEBUG] Daily Trends sorted by Month, then Detection Count (descending={not sort_ascending})")
                elif 'Month' in clean_pivot.columns and 'Hour' in rows and sort_by_field == 'Value (Detection Count)':
                    # Hourly Analysis: Sort by Month, then by Hour (0:00 → 23:00)
                    # Preserve original order from data source (already sorted correctly)
                    print(f"[DEBUG] Preserving original Hourly Analysis order")
                    pass
                elif 'Month' in clean_pivot.columns and 'Day' in rows and sort_by_field == 'Value (Detection Count)':
                    # Day of Week: Sort by Day (Mon → Sun), then by Month
                    # Preserve original order from data source (already sorted correctly)
                    print(f"[DEBUG] Preserving original Day of Week order")
                    pass
                elif 'Month' in clean_pivot.columns:
                    # Other analyses with Month - sort chronologically
                    clean_pivot['_month_sort'] = clean_pivot['Month'].apply(get_month_sort_key)
                    clean_pivot = clean_pivot.sort_values('_month_sort')
                    clean_pivot = clean_pivot.drop(columns=['_month_sort'])
                else:
                    # Sort by the numeric value (use chart_sort_direction)
                    clean_pivot = clean_pivot.sort_values(numeric_cols[0], ascending=sort_ascending)

        if chart_type == "Bar Chart":
            if rows and not columns:
                # Simple bar chart - use row dimension values for X-axis
                # If multiple row fields, concatenate them for X-axis labels
                if len(rows) > 1:
                    # Special formatting for day_of_week: "Day<br>Type" (line break instead of dash)
                    if selected_analysis_key == 'day_of_week':
                        x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        x_title = 'Day of Weeks'
                    elif selected_analysis_key == 'daily_trends':
                        # Daily trends: "Date - Month"
                        x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        x_title = 'Detection Over Multiple Days'
                    else:
                        # Concatenate multiple row fields (e.g., "June - 7.25.19706.0")
                        x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        # Custom title for sensor_analysis
                        if selected_analysis_key == 'sensor_analysis':
                            x_title = 'Sensor Versions Status Across Months'
                        else:
                            x_title = ' + '.join(rows)
                else:
                    x_values = clean_pivot[rows[0]].tolist() if rows[0] in clean_pivot.columns else clean_pivot.index.tolist()
                    # Custom title for overview_key_metrics
                    if selected_analysis_key == 'overview_key_metrics':
                        x_title = 'Host Overview Detection Across Months'
                    elif selected_analysis_key == 'day_of_week':
                        x_title = 'Day of Weeks'
                    else:
                        x_title = rows[0]

                y_col = [col for col in clean_pivot.columns if col not in rows][0] if len([col for col in clean_pivot.columns if col not in rows]) > 0 else clean_pivot.columns[-1]

                # Special handling for analyses with Month in rows - color bars by month
                if 'Month' in clean_pivot.columns and (selected_analysis_key == 'sensor_analysis' or
                                                       selected_analysis_key == 'daily_trends' or
                                                       selected_analysis_key == 'day_of_week' or
                                                       user_enabled_monthly_colors):
                    # Extract month from each row and assign colors
                    # Get unique months in chronological order
                    unique_months = clean_pivot['Month'].unique()
                    sorted_months = sorted(unique_months, key=lambda x: get_month_sort_key(x))

                    # Assign colors based on position (first month = green, second = blue, third = gold)
                    month_colors = {}
                    if len(sorted_months) >= 1:
                        month_colors[sorted_months[0]] = MONTHLY_COLORS['month_1']  # Green
                    if len(sorted_months) >= 2:
                        month_colors[sorted_months[1]] = MONTHLY_COLORS['month_2']  # Blue
                    if len(sorted_months) >= 3:
                        month_colors[sorted_months[2]] = MONTHLY_COLORS['month_3']  # Gold

                    # Assign colors to each bar based on its month
                    bar_colors = [month_colors.get(row['Month'], '#999999') for _, row in clean_pivot.iterrows()]

                    # Create custom hover text with month info
                    hover_text = [f"{x}<br>Month: {month}<br>Count: {count}"
                                  for x, month, count in zip(x_values,
                                                             clean_pivot['Month'].tolist(),
                                                             clean_pivot[y_col].tolist())]

                    fig = go.Figure(data=[
                        go.Bar(
                            x=x_values,
                            y=clean_pivot[y_col].tolist(),
                            marker_color=bar_colors,
                            hovertext=hover_text,
                            hoverinfo='text',
                            showlegend=False  # Hide the main bar trace from legend
                        )
                    ])

                    # Add legend entries for months only (using squares like other analyses)
                    for month in sorted_months:
                        fig.add_trace(go.Bar(
                            x=[None], y=[None],
                            marker_color=month_colors.get(month, '#999999'),
                            showlegend=True,
                            name=month
                        ))
                else:
                    # Default single-color bar chart
                    # For C.3 Day of Week and similar single-trace charts, show "Total" in legend
                    show_legend = selected_analysis_key in ['day_of_week', 'hourly_analysis']

                    fig = go.Figure(data=[
                        go.Bar(
                            name='Total' if show_legend else '',
                            x=x_values,
                            y=clean_pivot[y_col].tolist(),
                            marker_color='steelblue',
                            showlegend=show_legend
                        )
                    ])

                # For C.2 Hourly and C.3 Day of Week, set y-axis label to "Total"
                if selected_analysis_key in ['hourly_analysis', 'day_of_week']:
                    y_axis_title = 'Total'
                else:
                    y_axis_title = y_col

                fig.update_layout(
                    title=f"{config['aggregation'].title()} by {', '.join(rows)}",
                    xaxis_title=x_title,
                    yaxis_title=y_axis_title,
                    height=height,
                    showlegend=show_legend if 'show_legend' in locals() else False
                )
            else:
                # Grouped bar chart - X-axis shows row dimension, bars grouped by column dimension
                fig = go.Figure()

                # Hierarchical X-axis for ANY two-field combination (like Excel grouped axis)
                if rows and len(rows) == 2:
                    field1, field2 = rows[0], rows[1]

                    # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                    # 1st: Month (January → December)
                    # 2nd: Severity (Critical → High → Medium → Low → Info)
                    # 3rd: Value Count (Highest → Lowest, left to right)

                    # Calculate total value for each row (for sorting within groups)
                    value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                    if value_cols:
                        clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                    else:
                        clean_pivot['_row_total'] = 0

                    # Check if Month field exists
                    if 'Month' in rows:
                        month_field = 'Month'
                        other_field = field2 if field1 == 'Month' else field1

                        # 1st priority: Month order (Jan → Dec)
                        clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                        # 2nd priority: Severity order (Critical → Info) or alphabetical
                        if 'severity' in other_field.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                        # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                        clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                               ascending=[True, True, not sort_ascending])

                        # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                        x_values = clean_pivot.apply(
                            lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                        ).tolist()
                    else:
                        # No month - sort by both fields + value
                        # Check if fields are severity
                        if 'severity' in field1.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                        if 'severity' in field2.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                        # Sort: 1) Field1, 2) Field2, 3) Value
                        clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                               ascending=[True, True, not sort_ascending])

                        # Create labels: "Field2<br>Field1"
                        x_values = clean_pivot.apply(
                            lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                        ).tolist()

                    # Clean up sort columns
                    for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                        if col in clean_pivot.columns:
                            clean_pivot = clean_pivot.drop(columns=[col])

                    # Apply manual category ordering if enabled
                    if config.get('manual_order_enabled', False) and config.get('manual_category_order'):
                        manual_order = config['manual_category_order']
                        # Reorder clean_pivot based on manual_category_order
                        # Create a mapping of x_values to their manual order position
                        current_x_values = x_values.copy()
                        ordered_indices = []

                        for category in manual_order:
                            if category in current_x_values:
                                idx = current_x_values.index(category)
                                ordered_indices.append(idx)

                        # Add any categories not in manual_order at the end
                        for i, cat in enumerate(current_x_values):
                            if i not in ordered_indices:
                                ordered_indices.append(i)

                        # Reorder clean_pivot and x_values
                        clean_pivot = clean_pivot.iloc[ordered_indices].reset_index(drop=True)
                        x_values = [x_values[i] for i in ordered_indices]

                    x_title = ''  # No title for hierarchical axis

                # Handle normal multiple row fields (more than 2)
                elif rows and len(rows) > 2:
                    # Special formatting for day_of_week
                    if selected_analysis_key == 'day_of_week':
                        x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        x_title = 'Day of Weeks'
                    else:
                        # Concatenate multiple row fields for X-axis
                        x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        # Custom title for sensor_analysis
                        if selected_analysis_key == 'sensor_analysis':
                            x_title = 'Sensor Versions Status Across Months'
                        else:
                            x_title = ' + '.join(rows)
                elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                    x_values = clean_pivot[rows[0]].tolist()
                    if selected_analysis_key == 'day_of_week':
                        x_title = 'Day of Weeks'
                    else:
                        x_title = rows[0]
                else:
                    x_values = clean_pivot.index.tolist()
                    x_title = ''

                # Get columns to plot (exclude row fields)
                plot_cols = [col for col in clean_pivot.columns if col not in rows]

                # Apply manual series ordering if enabled
                if config.get('manual_order_enabled', False) and config.get('manual_series_order'):
                    manual_series = config['manual_series_order']
                    # Reorder plot_cols based on manual_series_order
                    ordered_cols = []
                    for series in manual_series:
                        if series in plot_cols:
                            ordered_cols.append(series)
                    # Add any columns not in manual order at the end
                    for col in plot_cols:
                        if col not in ordered_cols:
                            ordered_cols.append(col)
                    plot_cols = ordered_cols

                # Add a bar for each column dimension
                for col in plot_cols:
                    if col in clean_pivot.columns:
                        # Get color from mapping if available
                        bar_color = color_mapping.get(col, None)
                        fig.add_trace(go.Bar(
                            name=str(col),
                            x=x_values,
                            y=clean_pivot[col].tolist(),
                            marker_color=bar_color
                        ))

                # Custom x-axis labels for specific analyses
                if selected_analysis_key == 'tactics_by_severity':
                    custom_xaxis_title = 'Total Tactics Count'
                elif selected_analysis_key == 'technique_by_severity':
                    custom_xaxis_title = 'Total Technique Count'
                else:
                    custom_xaxis_title = x_title

                fig.update_layout(
                    title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                    barmode='group',
                    xaxis_title=custom_xaxis_title,
                    height=height
                )

        elif chart_type == "Horizontal Bar":
            # Horizontal bar chart - swap X and Y axes
            if rows and not columns:
                # Simple horizontal bar chart
                if len(rows) > 1:
                    # Special formatting for day_of_week
                    if selected_analysis_key == 'day_of_week':
                        y_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        y_title = 'Day of Weeks'
                    else:
                        y_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        y_title = ' + '.join(rows)
                else:
                    y_values = clean_pivot[rows[0]].tolist() if rows[0] in clean_pivot.columns else clean_pivot.index.tolist()
                    if selected_analysis_key == 'day_of_week':
                        y_title = 'Day of Weeks'
                    else:
                        y_title = rows[0]

                x_col = [col for col in clean_pivot.columns if col not in rows][0] if len([col for col in clean_pivot.columns if col not in rows]) > 0 else clean_pivot.columns[-1]

                fig = go.Figure(data=[
                    go.Bar(
                        y=y_values,
                        x=clean_pivot[x_col].tolist(),
                        orientation='h',
                        marker_color='steelblue'
                    )
                ])
                fig.update_layout(
                    title=f"{config['aggregation'].title()} by {', '.join(rows)}",
                    yaxis_title=y_title,
                    xaxis_title=x_col,
                    height=height
                )
            else:
                # Grouped horizontal bar chart
                fig = go.Figure()

                # Hierarchical Y-axis for ANY two-field combination
                if rows and len(rows) == 2:
                    field1, field2 = rows[0], rows[1]

                    # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                    # 1st: Month (January → December)
                    # 2nd: Severity (Critical → High → Medium → Low → Info)
                    # 3rd: Value Count (Highest → Lowest, top to bottom)

                    # Calculate total value for each row (for sorting within groups)
                    value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                    if value_cols:
                        clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                    else:
                        clean_pivot['_row_total'] = 0

                    # Check if Month field exists
                    if 'Month' in rows:
                        month_field = 'Month'
                        other_field = field2 if field1 == 'Month' else field1

                        # 1st priority: Month order (Jan → Dec)
                        clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                        # 2nd priority: Severity order (Critical → Info) or alphabetical
                        if 'severity' in other_field.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                        # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                        clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                               ascending=[True, True, not sort_ascending])

                        # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                        y_values = clean_pivot.apply(
                            lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                        ).tolist()
                    else:
                        # No month - sort by both fields + value
                        # Check if fields are severity
                        if 'severity' in field1.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                        if 'severity' in field2.lower():
                            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                            clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                        else:
                            clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                        # Sort: 1) Field1, 2) Field2, 3) Value
                        clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                               ascending=[True, True, not sort_ascending])

                        # Create labels: "Field2<br>Field1"
                        y_values = clean_pivot.apply(
                            lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                        ).tolist()

                    # Clean up sort columns
                    for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                        if col in clean_pivot.columns:
                            clean_pivot = clean_pivot.drop(columns=[col])

                    y_title = ''
                elif rows and len(rows) > 2:
                    # Special formatting for day_of_week
                    if selected_analysis_key == 'day_of_week':
                        y_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        y_title = 'Day of Weeks'
                    else:
                        y_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                        y_title = ' + '.join(rows)
                elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                    y_values = clean_pivot[rows[0]].tolist()
                    if selected_analysis_key == 'day_of_week':
                        y_title = 'Day of Weeks'
                    else:
                        y_title = rows[0]
                else:
                    y_values = clean_pivot.index.tolist()
                    y_title = ''

                plot_cols = [col for col in clean_pivot.columns if col not in rows]

                for col in plot_cols:
                    if col in clean_pivot.columns:
                        bar_color = color_mapping.get(col, None)
                        fig.add_trace(go.Bar(
                            name=str(col),
                            y=y_values,
                            x=clean_pivot[col].tolist(),
                            orientation='h',
                            marker_color=bar_color
                        ))

                fig.update_layout(
                    title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                    barmode='group',
                    yaxis_title=y_title,
                    height=height
                )

        elif chart_type == "Clustered Bar":
            # Clustered Bar is the same as grouped Bar Chart
            fig = go.Figure()

            # Hierarchical X-axis for ANY two-field combination (like Excel grouped axis)
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                # 1st: Month (January → December)
                # 2nd: Severity (Critical → High → Medium → Low → Info)
                # 3rd: Value Count (Highest → Lowest, left to right)

                # Calculate total value for each row (for sorting within groups)
                value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if value_cols:
                    clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                else:
                    clean_pivot['_row_total'] = 0

                # Check if Month field exists
                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    # 1st priority: Month order (Jan → Dec)
                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                    # 2nd priority: Severity order (Critical → Info) or alphabetical
                    if 'severity' in other_field.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                    clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                    ).tolist()
                else:
                    # No month - sort by both fields + value
                    # Check if fields are severity
                    if 'severity' in field1.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                    if 'severity' in field2.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                    # Sort: 1) Field1, 2) Field2, 3) Value
                    clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "Field2<br>Field1"
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                    ).tolist()

                # Clean up sort columns
                for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                    if col in clean_pivot.columns:
                        clean_pivot = clean_pivot.drop(columns=[col])

                x_title = ''  # No title for hierarchical axis

            # Handle normal multiple row fields (more than 2)
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = 'Day of Weeks'
                else:
                    # Concatenate multiple row fields for X-axis
                    x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    # Custom title for sensor_analysis
                    if selected_analysis_key == 'sensor_analysis':
                        x_title = 'Sensor Versions Status Across Months'
                    else:
                        x_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                x_values = clean_pivot[rows[0]].tolist()
                # Custom title for overview_key_metrics and day_of_week
                if selected_analysis_key == 'overview_key_metrics':
                    x_title = 'Host Overview Detection Across Months'
                elif selected_analysis_key == 'day_of_week':
                    x_title = 'Day of Weeks'
                else:
                    x_title = rows[0]
            else:
                x_values = clean_pivot.index.tolist()
                x_title = ''

            # Get columns to plot (exclude row fields)
            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            # Apply manual series ordering if enabled
            if config.get('manual_order_enabled', False) and config.get('manual_series_order'):
                manual_series = config['manual_series_order']
                ordered_cols = []
                for series in manual_series:
                    if series in plot_cols:
                        ordered_cols.append(series)
                for col in plot_cols:
                    if col not in ordered_cols:
                        ordered_cols.append(col)
                plot_cols = ordered_cols

            # Add a bar for each column dimension (clustered/grouped)
            for col in plot_cols:
                if col in clean_pivot.columns:
                    # Get color from mapping if available
                    bar_color = color_mapping.get(col, None)
                    fig.add_trace(go.Bar(
                        name=str(col),
                        x=x_values,
                        y=clean_pivot[col].tolist(),
                        marker_color=bar_color
                    ))

            fig.update_layout(
                title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                barmode='group',  # Clustered bars
                xaxis_title=x_title,
                height=height
            )

        elif chart_type == "Stacked Bar":
            fig = go.Figure()

            # Hierarchical X-axis for ANY two-field combination (like Excel grouped axis)
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                # 1st: Month (January → December)
                # 2nd: Severity (Critical → High → Medium → Low → Info)
                # 3rd: Value Count (Highest → Lowest, left to right)

                # Calculate total value for each row (for sorting within groups)
                value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if value_cols:
                    clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                else:
                    clean_pivot['_row_total'] = 0

                # Check if Month field exists
                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    # 1st priority: Month order (Jan → Dec)
                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                    # 2nd priority: Severity order (Critical → Info) or alphabetical
                    if 'severity' in other_field.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                    clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                    ).tolist()
                else:
                    # No month - sort by both fields + value
                    # Check if fields are severity
                    if 'severity' in field1.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                    if 'severity' in field2.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                    # Sort: 1) Field1, 2) Field2, 3) Value
                    clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "Field2<br>Field1"
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                    ).tolist()

                # Clean up sort columns
                for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                    if col in clean_pivot.columns:
                        clean_pivot = clean_pivot.drop(columns=[col])

                x_title = ''  # No title for hierarchical axis

            # Get X-axis values - handle multiple row fields (more than 2)
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = 'Day of Weeks'
                else:
                    x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                x_values = clean_pivot[rows[0]].tolist()
                # Custom title for overview_key_metrics and day_of_week
                if selected_analysis_key == 'overview_key_metrics':
                    x_title = 'Host Overview Detection Across Months'
                elif selected_analysis_key == 'day_of_week':
                    x_title = 'Day of Weeks'
                else:
                    x_title = rows[0]
            else:
                x_values = clean_pivot.index.tolist()
                x_title = ''

            # Get columns to plot (exclude row fields)
            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            # Add a bar for each column dimension
            for col in plot_cols:
                if col in clean_pivot.columns:
                    # Get color from mapping if available
                    bar_color = color_mapping.get(col, None)
                    fig.add_trace(go.Bar(
                        name=str(col),
                        x=x_values,
                        y=clean_pivot[col].tolist(),
                        marker_color=bar_color
                    ))

            fig.update_layout(
                title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                barmode='stack',
                xaxis_title=x_title,
                height=height
            )

        elif chart_type == "Horizontal Clustered Bar":
            # Horizontal clustered bar chart
            fig = go.Figure()

            # Hierarchical Y-axis for ANY two-field combination
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    if 'severity' in other_field.lower():
                        severity_order = {'High': 1, 'Medium': 2, 'Low': 3, 'Critical': 0}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)
                    clean_pivot = clean_pivot.sort_values(['_field_sort', '_month_sort'])
                else:
                    clean_pivot = clean_pivot.sort_values([field1, field2])

                y_values = clean_pivot.apply(
                    lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                ).tolist()

                if '_field_sort' in clean_pivot.columns:
                    clean_pivot = clean_pivot.drop(columns=['_field_sort'])
                if '_month_sort' in clean_pivot.columns:
                    clean_pivot = clean_pivot.drop(columns=['_month_sort'])

                y_title = ''
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    y_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    y_title = 'Day of Weeks'
                else:
                    y_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    y_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                y_values = clean_pivot[rows[0]].tolist()
                y_title = rows[0]
            else:
                y_values = clean_pivot.index.tolist()
                y_title = ''

            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            for col in plot_cols:
                if col in clean_pivot.columns:
                    bar_color = color_mapping.get(col, None)
                    fig.add_trace(go.Bar(
                        name=str(col),
                        y=y_values,
                        x=clean_pivot[col].tolist(),
                        orientation='h',
                        marker_color=bar_color
                    ))

            fig.update_layout(
                title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                barmode='group',
                yaxis_title=y_title,
                height=height
            )

        elif chart_type == "Horizontal Stacked Bar":
            # Horizontal stacked bar chart
            fig = go.Figure()

            # Hierarchical Y-axis for ANY two-field combination
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    if 'severity' in other_field.lower():
                        severity_order = {'High': 1, 'Medium': 2, 'Low': 3, 'Critical': 0}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)
                    clean_pivot = clean_pivot.sort_values(['_field_sort', '_month_sort'])
                else:
                    clean_pivot = clean_pivot.sort_values([field1, field2])

                y_values = clean_pivot.apply(
                    lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                ).tolist()

                if '_field_sort' in clean_pivot.columns:
                    clean_pivot = clean_pivot.drop(columns=['_field_sort'])
                if '_month_sort' in clean_pivot.columns:
                    clean_pivot = clean_pivot.drop(columns=['_month_sort'])

                y_title = ''
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    y_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    y_title = 'Day of Weeks'
                else:
                    y_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    y_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                y_values = clean_pivot[rows[0]].tolist()
                y_title = rows[0]
            else:
                y_values = clean_pivot.index.tolist()
                y_title = ''

            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            for col in plot_cols:
                if col in clean_pivot.columns:
                    bar_color = color_mapping.get(col, None)
                    fig.add_trace(go.Bar(
                        name=str(col),
                        y=y_values,
                        x=clean_pivot[col].tolist(),
                        orientation='h',
                        marker_color=bar_color
                    ))

            fig.update_layout(
                title=f"{config['aggregation'].title()} by {', '.join(rows + columns if columns else rows)}",
                barmode='stack',
                yaxis_title=y_title,
                height=height
            )

        elif chart_type == "Line Chart":
            fig = go.Figure()

            # Hierarchical X-axis for ANY two-field combination (like Excel grouped axis)
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                # 1st: Month (January → December)
                # 2nd: Severity (Critical → High → Medium → Low → Info)
                # 3rd: Value Count (Highest → Lowest, left to right)

                # Calculate total value for each row (for sorting within groups)
                value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if value_cols:
                    clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                else:
                    clean_pivot['_row_total'] = 0

                # Check if Month field exists
                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    # 1st priority: Month order (Jan → Dec)
                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                    # 2nd priority: Severity order (Critical → Info) or alphabetical
                    if 'severity' in other_field.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                    clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                    ).tolist()
                else:
                    # No month - sort by both fields + value
                    # Check if fields are severity
                    if 'severity' in field1.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                    if 'severity' in field2.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                    # Sort: 1) Field1, 2) Field2, 3) Value
                    clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "Field2<br>Field1"
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                    ).tolist()

                # Clean up sort columns
                for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                    if col in clean_pivot.columns:
                        clean_pivot = clean_pivot.drop(columns=[col])

                x_title = ''  # No title for hierarchical axis

            # Get X-axis values - handle multiple row fields (more than 2)
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = 'Day of Weeks'
                else:
                    x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                x_values = clean_pivot[rows[0]].tolist()
                # Custom title for overview_key_metrics and day_of_week
                if selected_analysis_key == 'overview_key_metrics':
                    x_title = 'Host Overview Detection Across Months'
                elif selected_analysis_key == 'day_of_week':
                    x_title = 'Day of Weeks'
                else:
                    x_title = rows[0]
            else:
                x_values = clean_pivot.index.tolist()
                x_title = ''

            # Get columns to plot (exclude row fields)
            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            # Add a line for each column dimension
            for col in plot_cols:
                if col in clean_pivot.columns:
                    # Get color from mapping if available
                    line_color = color_mapping.get(col, None)

                    # For single-line charts (hourly_analysis, day_of_week), use "Total" as legend name
                    if selected_analysis_key in ['hourly_analysis', 'day_of_week'] and len(plot_cols) == 1:
                        trace_name = 'Total'
                    else:
                        trace_name = str(col)

                    fig.add_trace(go.Scatter(
                        name=trace_name,
                        x=x_values,
                        y=clean_pivot[col].tolist(),
                        mode='lines+markers',
                        line=dict(color=line_color) if line_color else None,
                        marker=dict(color=line_color) if line_color else None,
                        showlegend=True  # Ensure legend is shown
                    ))

            # For C.2 Hourly and C.3 Day of Week, set y-axis label to "Total"
            if selected_analysis_key in ['hourly_analysis', 'day_of_week']:
                y_axis_title = 'Total'
            else:
                y_axis_title = config.get('values', [''])[0] if 'values' in config else ''

            fig.update_layout(
                title=f"{config['aggregation'].title()} Trend",
                xaxis_title=x_title,
                yaxis_title=y_axis_title,
                height=height,
                showlegend=True  # Ensure legend is displayed
            )

        elif chart_type == "Area Chart":
            fig = go.Figure()

            # Hierarchical X-axis for ANY two-field combination (like Excel grouped axis)
            if rows and len(rows) == 2:
                field1, field2 = rows[0], rows[1]

                # SORTING PRIORITY FOR ALL DASHBOARD ANALYSES:
                # 1st: Month (January → December)
                # 2nd: Severity (Critical → High → Medium → Low → Info)
                # 3rd: Value Count (Highest → Lowest, left to right)

                # Calculate total value for each row (for sorting within groups)
                value_cols = [col for col in clean_pivot.columns if col not in rows and pd.api.types.is_numeric_dtype(clean_pivot[col])]
                if value_cols:
                    clean_pivot['_row_total'] = clean_pivot[value_cols].sum(axis=1)
                else:
                    clean_pivot['_row_total'] = 0

                # Check if Month field exists
                if 'Month' in rows:
                    month_field = 'Month'
                    other_field = field2 if field1 == 'Month' else field1

                    # 1st priority: Month order (Jan → Dec)
                    clean_pivot['_month_sort'] = clean_pivot[month_field].apply(get_month_sort_key)

                    # 2nd priority: Severity order (Critical → Info) or alphabetical
                    if 'severity' in other_field.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field_sort'] = clean_pivot[other_field].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field_sort'] = clean_pivot[other_field].astype(str)

                    # Sort: 1) Month, 2) Severity/Field, 3) Value (highest first)
                    clean_pivot = clean_pivot.sort_values(['_month_sort', '_field_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "OtherField<br>Month" (e.g., "High<br>July")
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[other_field]}<br>{row[month_field]}", axis=1
                    ).tolist()
                else:
                    # No month - sort by both fields + value
                    # Check if fields are severity
                    if 'severity' in field1.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field1_sort'] = clean_pivot[field1].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field1_sort'] = clean_pivot[field1].astype(str)

                    if 'severity' in field2.lower():
                        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4, 'Information': 4}
                        clean_pivot['_field2_sort'] = clean_pivot[field2].map(lambda x: severity_order.get(x, 99))
                    else:
                        clean_pivot['_field2_sort'] = clean_pivot[field2].astype(str)

                    # Sort: 1) Field1, 2) Field2, 3) Value
                    clean_pivot = clean_pivot.sort_values(['_field1_sort', '_field2_sort', '_row_total'],
                                                           ascending=[True, True, not sort_ascending])

                    # Create labels: "Field2<br>Field1"
                    x_values = clean_pivot.apply(
                        lambda row: f"{row[field2]}<br>{row[field1]}", axis=1
                    ).tolist()

                # Clean up sort columns
                for col in ['_month_sort', '_field_sort', '_field1_sort', '_field2_sort', '_row_total']:
                    if col in clean_pivot.columns:
                        clean_pivot = clean_pivot.drop(columns=[col])

                x_title = ''  # No title for hierarchical axis

            # Get X-axis values - handle multiple row fields (more than 2)
            elif rows and len(rows) > 2:
                # Special formatting for day_of_week
                if selected_analysis_key == 'day_of_week':
                    x_values = clean_pivot.apply(lambda row: '<br>'.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = 'Day of Weeks'
                else:
                    x_values = clean_pivot.apply(lambda row: ' - '.join([str(row[r]) for r in rows if r in clean_pivot.columns]), axis=1).tolist()
                    x_title = ' + '.join(rows)
            elif rows and len(rows) > 0 and rows[0] in clean_pivot.columns:
                x_values = clean_pivot[rows[0]].tolist()
                # Custom title for overview_key_metrics and day_of_week
                if selected_analysis_key == 'overview_key_metrics':
                    x_title = 'Host Overview Detection Across Months'
                elif selected_analysis_key == 'day_of_week':
                    x_title = 'Day of Weeks'
                else:
                    x_title = rows[0]
            else:
                x_values = clean_pivot.index.tolist()
                x_title = ''

            # Get columns to plot (exclude row fields)
            plot_cols = [col for col in clean_pivot.columns if col not in rows]

            # Add an area for each column dimension
            for col in plot_cols:
                if col in clean_pivot.columns:
                    # Get color from mapping if available
                    area_color = color_mapping.get(col, None)
                    fig.add_trace(go.Scatter(
                        name=str(col),
                        x=x_values,
                        y=clean_pivot[col].tolist(),
                        mode='lines',
                        fill='tonexty',
                        line=dict(color=area_color) if area_color else None,
                        fillcolor=area_color if area_color else None
                    ))

            fig.update_layout(
                title=f"{config['aggregation'].title()} Trend",
                xaxis_title=x_title,
                height=height
            )

        elif chart_type == "Pie Chart":
            # Pie chart works best with Columns field (for category breakdown)
            # If using multiple row fields, we'll sum across all combinations

            if columns and len(columns) > 0:
                # Case 1: COLUMNS POPULATED (e.g., Tactic in Columns)
                # Use columns as pie slices - sum all row combinations
                plot_cols = [col for col in clean_pivot.columns if col not in rows]

                if plot_cols:
                    # Sum all values for each column
                    labels = plot_cols
                    values = [clean_pivot[col].sum() for col in plot_cols]

                    # Apply color mapping
                    colors = [color_mapping.get(col, None) for col in plot_cols]

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.3,
                        marker=dict(colors=colors) if any(colors) else None
                    )])
                else:
                    # Fallback if no valid columns
                    st.warning("No data columns available for pie chart with current configuration.")
                    fig = None

            elif rows and len(rows) == 1:
                # Case 2: SINGLE ROW FIELD (e.g., just SeverityName)
                # Show each unique value as a pie slice
                if rows[0] in clean_pivot.columns:
                    labels = clean_pivot[rows[0]].tolist()
                    values_col = [col for col in clean_pivot.columns if col not in rows]

                    if values_col and len(values_col) > 0:
                        # Use first value column
                        values = clean_pivot[values_col[0]].tolist()
                    else:
                        # No value columns, count occurrences
                        value_counts = clean_pivot[rows[0]].value_counts()
                        labels = value_counts.index.tolist()
                        values = value_counts.values.tolist()

                    # Apply color mapping for labels
                    colors = [color_mapping.get(label, None) for label in labels]

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.3,
                        marker=dict(colors=colors) if any(colors) else None
                    )])
                else:
                    st.warning(f"Row field '{rows[0]}' not found in pivot data.")
                    fig = None

            elif rows and len(rows) >= 2:
                # Case 3: MULTIPLE ROW FIELDS (e.g., Month + SeverityName)
                # Group by first row field and sum all values
                group_col = rows[0]

                if group_col in clean_pivot.columns:
                    value_cols = [col for col in clean_pivot.columns if col not in rows]

                    if value_cols and len(value_cols) > 0:
                        # Sum across all value columns for each group
                        grouped = clean_pivot.groupby(group_col)[value_cols].sum().sum(axis=1).reset_index()
                        grouped.columns = [group_col, 'Total']
                        labels = grouped[group_col].tolist()
                        values = grouped['Total'].tolist()
                    else:
                        # No value columns, count by group
                        grouped = clean_pivot.groupby(group_col).size().reset_index(name='Count')
                        labels = grouped[group_col].tolist()
                        values = grouped['Count'].tolist()

                    # Apply color mapping
                    colors = [color_mapping.get(label, None) for label in labels]

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.3,
                        marker=dict(colors=colors) if any(colors) else None
                    )])
                else:
                    st.warning(f"Row field '{group_col}' not found in pivot data.")
                    fig = None
            else:
                st.warning("Please select at least one field in Rows or Columns for pie chart.")
                fig = None

            if fig:
                fig.update_layout(
                    title=f"{config['aggregation'].title()} Distribution",
                    height=height
                )

        elif chart_type == "Heatmap":
            if isinstance(clean_pivot, pd.DataFrame) and len(clean_pivot.columns) > 1:
                fig = go.Figure(data=go.Heatmap(
                    z=clean_pivot.values,
                    x=clean_pivot.columns,
                    y=clean_pivot.index,
                    colorscale='RdYlGn',
                    text=clean_pivot.values,
                    texttemplate='%{text}',
                    textfont={"size": 10}
                ))

                fig.update_layout(
                    title=f"Heatmap: {config['aggregation'].title()}",
                    height=height
                )
            else:
                return None

        else:
            return None

        return fig

    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None


def show_pivot_insights(pivot_table, config):
    """Display insights from pivot table"""
    st.markdown("### 📊 Summary Statistics")

    # Get numeric columns
    numeric_cols = pivot_table.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            total = pivot_table[numeric_cols].sum().sum()
            st.metric("Total", f"{total:,.0f}")

        with col2:
            avg = pivot_table[numeric_cols].mean().mean()
            st.metric("Average", f"{avg:,.2f}")

        with col3:
            maximum = pivot_table[numeric_cols].max().max()
            st.metric("Maximum", f"{maximum:,.0f}")

        # Top values
        st.markdown("### 🏆 Top Values")

        if len(config['rows']) > 0:
            # Find row with highest total
            row_totals = pivot_table[numeric_cols].sum(axis=1)
            top_row_idx = row_totals.idxmax()
            top_row_value = row_totals.max()

            st.info(f"**Highest Total**: {top_row_idx} with {top_row_value:,.0f}")

        # Show distribution
        st.markdown("### 📈 Distribution")
        st.bar_chart(pivot_table[numeric_cols].iloc[:10] if len(pivot_table) > 10 else pivot_table[numeric_cols])


def export_to_pdf(pivot_table, chart, config, data_source):
    """Export pivot table and chart to PDF"""
    buffer = io.BytesIO()

    try:
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=reportlab_colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=1  # Center
        )

        story.append(Paragraph(f"Pivot Table Report - {data_source}", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Configuration details
        story.append(Paragraph("Configuration", styles['Heading2']))
        config_text = f"""
        <b>Rows:</b> {', '.join(config['rows']) if config['rows'] else 'None'}<br/>
        <b>Columns:</b> {', '.join(config['columns']) if config['columns'] else 'None'}<br/>
        <b>Values:</b> {', '.join(config['values']) if config['values'] else 'Count'}<br/>
        <b>Aggregation:</b> {config['aggregation']}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(config_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Pivot table
        story.append(Paragraph("Pivot Table", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        # Convert pivot table to reportlab table
        table_data = []

        # Header
        header = [''] + list(pivot_table.columns)
        table_data.append(header)

        # Data rows (limit to first 20 for PDF)
        for idx, row in pivot_table.head(20).iterrows():
            table_data.append([str(idx)] + [str(val) for val in row])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), reportlab_colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), reportlab_colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), reportlab_colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, reportlab_colors.black)
        ]))

        story.append(table)
        story.append(PageBreak())

        # Chart (if available)
        if chart:
            story.append(Paragraph("Visualization", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))

            # Save chart as image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                chart.write_image(tmp.name, width=800, height=600)
                img = Image(tmp.name, width=6*inch, height=4.5*inch)
                story.append(img)
                os.unlink(tmp.name)

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        return buffer.getvalue()

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


def export_to_excel(pivot_table, config, data_source):
    """Export pivot table to Excel with formatting"""
    buffer = io.BytesIO()

    try:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Write pivot table
            pivot_table.to_excel(writer, sheet_name='Pivot Table', index=True)

            # Write configuration
            config_df = pd.DataFrame({
                'Setting': ['Data Source', 'Rows', 'Columns', 'Values', 'Aggregation', 'Generated'],
                'Value': [
                    data_source,
                    ', '.join(config['rows']) if config['rows'] else 'None',
                    ', '.join(config['columns']) if config['columns'] else 'None',
                    ', '.join(config['values']) if config['values'] else 'Count',
                    config['aggregation'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            })
            config_df.to_excel(writer, sheet_name='Configuration', index=False)

        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        st.error(f"Error generating Excel: {str(e)}")
        return None


if __name__ == "__main__":
    pivot_table_builder_dashboard()
