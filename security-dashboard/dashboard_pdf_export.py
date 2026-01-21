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
# EXECUTIVE SUMMARY SECTION
# ============================================

def render_executive_summary(ticket_data, host_data, detection_data, time_data, num_months, section_letter='E'):
    """
    Generate Executive Summary Report with professional cybersecurity insights
    Written from perspective of experienced cybersecurity analyst

    Fixed: TypeError with peak_hour string comparison - now converts to int

    Args:
        ticket_data: Ticket lifecycle analysis results
        host_data: Host security analysis results
        detection_data: Detection and severity analysis results
        time_data: Time-based analysis results
        num_months: Number of months analyzed (1-3)
        section_letter: Section letter designation (default 'E')
    """
    st.markdown(f'<div class="section-header">{section_letter}. Executive Summary Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

    # Determine time period text
    if num_months == 1:
        period_text = "single-month period"
        comparison_context = "month-over-month historical trends"
    elif num_months == 2:
        period_text = "two-month period"
        comparison_context = "month-to-month progression"
    else:
        period_text = "three-month quarterly period"
        comparison_context = "quarterly trend analysis"

    # ============================================
    # OVERVIEW INTRODUCTION
    # ============================================
    overview_html = f"""
    <div style="background-color: #f8f9fa; border-left: 4px solid #1f4e5f; padding: 15px; margin-bottom: 15px; border-radius: 5px;">
        <div style="font-size: 12px; font-weight: bold; color: #1f4e5f; margin-bottom: 8px;">📊 EXECUTIVE OVERVIEW</div>
        <div style="font-size: 11px; color: #333; line-height: 1.6;">
            This executive summary provides strategic cybersecurity insights based on comprehensive analysis across the {period_text}.
            As security operations professionals, our assessment focuses on threat patterns, response effectiveness, and actionable
            recommendations to strengthen the organization's security posture.
        </div>
    </div>
    """
    st.markdown(overview_html, unsafe_allow_html=True)

    # ============================================
    # KEY FINDINGS SECTION
    # ============================================
    st.markdown('<div style="font-size: 12px; font-weight: bold; color: #1f4e5f; margin: 15px 0 10px 0;">🎯 KEY FINDINGS</div>', unsafe_allow_html=True)

    findings = []

    # TICKET LIFECYCLE INSIGHTS
    if ticket_data:
        # Get summary data from most recent month
        summary_keys = sorted([k for k in ticket_data.keys() if k.startswith('ticket_summary_')])
        if summary_keys:
            latest_summary = ticket_data[summary_keys[-1]]
            total_alerts = latest_summary.get('total_alerts', 0)
            resolved = latest_summary.get('alerts_resolved', 0)
            pending = latest_summary.get('alerts_pending', 0)

            if total_alerts > 0:
                resolution_rate = (resolved / total_alerts) * 100

                # Assess resolution performance
                if resolution_rate >= 90:
                    status_assessment = "exceptional"
                    status_color = "#28a745"
                elif resolution_rate >= 75:
                    status_assessment = "strong"
                    status_color = "#70AD47"
                elif resolution_rate >= 60:
                    status_assessment = "moderate"
                    status_color = "#FFC000"
                else:
                    status_assessment = "concerning"
                    status_color = "#DC143C"

                findings.append(f"""
                    <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid {status_color}; border-radius: 4px;">
                        <strong style="color: {status_color};">Alert Response Performance:</strong>
                        <span style="font-size: 11px;">
                        Incident response team achieved {resolution_rate:.1f}% resolution rate ({resolved} of {total_alerts} alerts resolved),
                        indicating {status_assessment} operational efficiency.
                        {f'{pending} alerts remain pending investigation and remediation.' if pending > 0 else 'All alerts have been addressed.'}
                        </span>
                    </div>
                """)

                # Analyze by severity if pivot data available
                pivot_keys = [k for k in ticket_data.keys() if k.startswith('request_severity_pivot_')]
                if pivot_keys:
                    latest_pivot = ticket_data[pivot_keys[-1]]
                    if not latest_pivot.empty:
                        # Count critical and high severity alerts
                        critical_count = latest_pivot['Critical'].sum()
                        high_count = latest_pivot['High'].sum()

                        if critical_count > 0 or high_count > 0:
                            priority_total = critical_count + high_count
                            findings.append(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid #DC143C; border-radius: 4px;">
                                    <strong style="color: #DC143C;">High-Priority Threats:</strong>
                                    <span style="font-size: 11px;">
                                    {priority_total} high-priority alerts detected ({critical_count} Critical, {high_count} High severity).
                                    These require immediate security team attention and executive awareness due to potential business impact.
                                    </span>
                                </div>
                            """)

    # HOST SECURITY INSIGHTS
    if host_data:
        # Analyze host detection patterns
        if 'host_detection_summary' in host_data:
            host_summary = host_data['host_detection_summary']
            if not host_summary.empty and 'DetectionCount' in host_summary.columns:
                total_hosts = len(host_summary)
                total_detections = host_summary['DetectionCount'].sum()
                avg_per_host = total_detections / total_hosts if total_hosts > 0 else 0

                # Identify high-risk hosts
                high_threshold = avg_per_host * 2  # Hosts with 2x average detections
                high_risk_hosts = len(host_summary[host_summary['DetectionCount'] >= high_threshold])

                if high_risk_hosts > 0:
                    risk_percentage = (high_risk_hosts / total_hosts) * 100
                    findings.append(f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid #FF8C00; border-radius: 4px;">
                            <strong style="color: #FF8C00;">Host Risk Profile:</strong>
                            <span style="font-size: 11px;">
                            {high_risk_hosts} endpoints ({risk_percentage:.1f}% of monitored hosts) exhibit elevated threat activity
                            with detection rates exceeding normal baseline. Recommend immediate isolation review and forensic analysis.
                            </span>
                        </div>
                    """)

    # DETECTION & SEVERITY INSIGHTS
    if detection_data:
        # Analyze detection trends
        if 'severity_trend' in detection_data:
            severity_df = detection_data['severity_trend']
            if not severity_df.empty and 'SeverityName' in severity_df.columns and 'Count' in severity_df.columns:
                total_detections = severity_df['Count'].sum()

                # Calculate severity distribution
                severity_dist = severity_df.groupby('SeverityName')['Count'].sum()

                if 'Critical' in severity_dist.index or 'High' in severity_dist.index:
                    critical = severity_dist.get('Critical', 0)
                    high = severity_dist.get('High', 0)
                    high_priority_pct = ((critical + high) / total_detections) * 100 if total_detections > 0 else 0

                    findings.append(f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid #5B9BD5; border-radius: 4px;">
                            <strong style="color: #5B9BD5;">Threat Severity Distribution:</strong>
                            <span style="font-size: 11px;">
                            {total_detections} total detections recorded across the analysis period.
                            High-priority threats (Critical/High) represent {high_priority_pct:.1f}% of all detections,
                            requiring prioritized security response and resource allocation.
                            </span>
                        </div>
                    """)

        # Analyze attack patterns (tactics/techniques)
        if 'tactics_by_severity' in detection_data:
            tactics_df = detection_data['tactics_by_severity']
            if not tactics_df.empty and 'Tactic' in tactics_df.columns:
                top_tactics = tactics_df.groupby('Tactic')['Count'].sum().nlargest(3)
                if len(top_tactics) > 0:
                    top_tactic_name = top_tactics.index[0]
                    top_tactic_count = top_tactics.iloc[0]

                    findings.append(f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid #70AD47; border-radius: 4px;">
                            <strong style="color: #70AD47;">Attack Pattern Analysis:</strong>
                            <span style="font-size: 11px;">
                            Primary adversary tactic observed: <strong>{top_tactic_name}</strong> ({top_tactic_count} incidents).
                            This MITRE ATT&CK pattern indicates targeted threat actor methodology requiring defensive posture adjustment.
                            </span>
                        </div>
                    """)

    # TIME-BASED INSIGHTS
    if time_data:
        if 'hourly_analysis' in time_data:
            hourly_df = time_data['hourly_analysis']
            if not hourly_df.empty and 'Hour' in hourly_df.columns and 'Detection Count' in hourly_df.columns:
                hourly_totals = hourly_df.groupby('Hour')['Detection Count'].sum()
                if len(hourly_totals) > 0:
                    peak_hour = hourly_totals.idxmax()
                    peak_count = hourly_totals.max()

                    # Convert peak_hour to integer for comparison
                    try:
                        peak_hour_int = int(peak_hour)
                    except (ValueError, TypeError):
                        peak_hour_int = 0

                    # Determine if peak is during business hours (8-17) or off-hours
                    if 8 <= peak_hour_int <= 17:
                        time_context = "business hours"
                        risk_note = "consistent with normal user activity patterns"
                    else:
                        time_context = "off-business hours"
                        risk_note = "potentially indicating automated or malicious activity requiring investigation"

                    findings.append(f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: white; border-left: 3px solid #9966CC; border-radius: 4px;">
                            <strong style="color: #9966CC;">Temporal Threat Patterns:</strong>
                            <span style="font-size: 11px;">
                            Peak detection activity occurs at {peak_hour_int:02d}:00 hours ({time_context}) with {int(peak_count)} alerts,
                            {risk_note}.
                            </span>
                        </div>
                    """)

    # Render findings
    if findings:
        for finding in findings:
            st.markdown(finding, unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 11px; color: #666; font-style: italic;">No significant findings identified in current analysis period.</div>', unsafe_allow_html=True)

    # ============================================
    # STRATEGIC RECOMMENDATIONS
    # ============================================
    st.markdown('<div style="font-size: 12px; font-weight: bold; color: #1f4e5f; margin: 20px 0 10px 0;">✅ RECOMMENDED ACTIONS</div>', unsafe_allow_html=True)

    recommendations = []

    # Generate targeted recommendations based on findings
    if ticket_data and summary_keys:
        latest_summary = ticket_data[summary_keys[-1]]
        pending = latest_summary.get('alerts_pending', 0)

        if pending > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Accelerate Alert Resolution',
                'detail': f'Prioritize closure of {pending} pending alerts through enhanced triage procedures and resource allocation to incident response team.',
                'color': '#DC143C'
            })

        # Check for critical severity in pending
        pivot_keys = [k for k in ticket_data.keys() if k.startswith('request_severity_pivot_')]
        if pivot_keys:
            latest_pivot = ticket_data[pivot_keys[-1]]
            pending_pivot = latest_pivot[latest_pivot['Status'].isin(['open', 'pending', 'on-hold', 'in_progress'])]
            if not pending_pivot.empty:
                pending_critical = pending_pivot['Critical'].sum()
                if pending_critical > 0:
                    recommendations.append({
                        'priority': 'CRITICAL',
                        'action': 'Critical Alert Escalation',
                        'detail': f'{pending_critical} Critical severity alerts require immediate executive attention and emergency response protocol activation.',
                        'color': '#8B0000'
                    })

    if host_data and 'host_detection_summary' in host_data:
        host_summary = host_data['host_detection_summary']
        if not host_summary.empty and len(host_summary) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Endpoint Security Hardening',
                'detail': 'Implement enhanced endpoint protection controls on high-detection hosts, including application whitelisting and behavioral monitoring.',
                'color': '#FF8C00'
            })

    if detection_data and 'tactics_by_severity' in detection_data:
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Threat Hunting Initiative',
            'detail': 'Launch proactive threat hunting campaigns targeting identified MITRE ATT&CK tactics to detect latent threats and advanced persistent threats (APTs).',
            'color': '#5B9BD5'
        })

    recommendations.append({
        'priority': 'ONGOING',
        'action': 'Security Metrics Review',
        'detail': f'Continue {comparison_context} monitoring and establish key performance indicators (KPIs) for security operations effectiveness measurement.',
        'color': '#70AD47'
    })

    # Render recommendations
    for rec in recommendations:
        rec_html = f"""
        <div style="margin-bottom: 8px; padding: 10px; background: white; border-left: 3px solid {rec['color']}; border-radius: 4px; display: flex; align-items: start;">
            <div style="background: {rec['color']}; color: white; font-size: 9px; font-weight: bold; padding: 3px 8px; border-radius: 3px; margin-right: 10px; white-space: nowrap;">
                {rec['priority']}
            </div>
            <div style="flex: 1;">
                <div style="font-weight: bold; font-size: 11px; color: #333; margin-bottom: 3px;">{rec['action']}</div>
                <div style="font-size: 10px; color: #555; line-height: 1.5;">{rec['detail']}</div>
            </div>
        </div>
        """
        st.markdown(rec_html, unsafe_allow_html=True)

    # ============================================
    # CONCLUSION STATEMENT
    # ============================================
    conclusion_html = f"""
    <div style="background-color: #e8f4f8; border: 1px solid #1f4e5f; padding: 12px; margin-top: 15px; border-radius: 5px;">
        <div style="font-size: 11px; color: #1f4e5f; line-height: 1.6; text-align: justify;">
            <strong>Professional Assessment:</strong> The security operations team demonstrates operational capability in threat detection
            and response across the {period_text}. Continued focus on high-priority alert remediation, endpoint hardening, and proactive
            threat hunting will strengthen the organization's defensive posture against evolving cyber threats. Regular executive review
            of these metrics ensures alignment between security operations and business risk management objectives.
        </div>
    </div>
    """
    st.markdown(conclusion_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close section


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

        # Editable title with placeholder format
        default_title = f"XXX COMPANY - CrowdStrike Falcon Monthly Report ({current_month})"

        st.markdown("### 📝 Report Title Configuration")
        st.markdown("**Important:** Please update the company name and verify the month/year before generating the report.")

        dashboard_title = st.text_input(
            "Dashboard Title",
            value=default_title,
            help="Replace 'XXX COMPANY' with your actual company name. Format: [Company Name] - CrowdStrike Falcon Monthly Report (Month Year)",
            placeholder="e.g., Acme Corporation - CrowdStrike Falcon Monthly Report (January 2026)"
        )

        # Validation warning
        if "XXX COMPANY" in dashboard_title:
            st.warning("⚠️ Please replace 'XXX COMPANY' with your actual company name before generating the PDF report.")

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
    ticket_data = st.session_state.get('ticket_lifecycle_results', {})

    # Extract months dynamically from data
    months = extract_months_from_data(host_data, detection_data, time_data)

    # Get actual number of months and create month text helper
    num_months = st.session_state.get('num_months', len(months))
    if num_months == 1:
        month_text = "Single Month"
    elif num_months == 2:
        month_text = "Two Months"
    else:
        month_text = "Three Months"

    # ============================================
    # SIDEBAR: SECTION SELECTION
    # ============================================
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Report Sections")
        st.markdown("Select sections to include in the report:")

        include_ticket_lifecycle = st.checkbox("Ticket Lifecycle Analysis", value=False, help="Include ticket status trend analysis", disabled=not ticket_data)
        include_host_analysis = st.checkbox("Host Security Analysis", value=True, help="Include host security metrics")
        include_detection_analysis = st.checkbox("Detection and Severity Analysis", value=True, help="Include detection and severity trends")
        include_time_analysis = st.checkbox("Time-Based Analysis", value=True, help="Include time-based detection patterns")
        include_executive_summary = st.checkbox("Executive Summary Report", value=True, help="Include professional executive summary with key findings and recommendations")

        if not ticket_data:
            st.caption("💡 Ticket Lifecycle Analysis is disabled (no ticket data available)")

    # ============================================
    # DYNAMIC SECTION LETTERING
    # ============================================
    # Calculate section letters dynamically based on what's included
    section_letters = {}
    current_letter_index = 0
    letters = ['A', 'B', 'C', 'D', 'E', 'F']

    if include_ticket_lifecycle and ticket_data:
        section_letters['ticket'] = letters[current_letter_index]
        current_letter_index += 1

    if include_host_analysis:
        section_letters['host'] = letters[current_letter_index]
        current_letter_index += 1

    if include_detection_analysis:
        section_letters['detection'] = letters[current_letter_index]
        current_letter_index += 1

    if include_time_analysis:
        section_letters['time'] = letters[current_letter_index]
        current_letter_index += 1

    if include_executive_summary:
        section_letters['executive'] = letters[current_letter_index]
        current_letter_index += 1

    # ============================================
    # TICKET LIFECYCLE ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_ticket_lifecycle and ticket_data:
        import plotly.graph_objects as go

        section_letter = section_letters.get('ticket', 'A')
        st.markdown(f'<div class="section-header">{section_letter}. Ticket Lifecycle Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Get available months from ticket data
        available_months = []
        month_data_map = {}

        for key in ticket_data.keys():
            if key.startswith('request_severity_pivot_'):
                month_name = key.replace('request_severity_pivot_', '').replace('_', ' ')
                available_months.append(month_name)
                month_data_map[month_name] = key

        if not available_months:
            st.warning("No ticket pivot data available")
        else:
            # Sort months chronologically
            def month_sort_key(month_str):
                """Sort months chronologically (January to December)"""
                try:
                    # Try to parse as "Month Year" format
                    date_obj = datetime.strptime(month_str, '%B %Y')
                    return (date_obj.year, date_obj.month)
                except:
                    # If parsing fails, return the string as-is for alphabetical sort
                    return (9999, month_str)

            sorted_months = sorted(available_months, key=month_sort_key)
            num_months = len(sorted_months)

            # Use actual month names from Falcon Generator (no custom naming needed)
            # Month names are already configured in Falcon Generator with month/year dropdowns
            custom_month_names = {month_name: month_name for month_name in sorted_months}

            # ============================
            # A.1: Combined Chart for All Months
            # ============================
            # Determine trend text
            if num_months == 1:
                trend_text = "Single Month"
            elif num_months == 2:
                trend_text = "Two Month Trends"
            elif num_months == 3:
                trend_text = "Three Month Trends"
            else:
                trend_text = f"{num_months} Month Trends"

            st.markdown(f'<div class="chart-title">{section_letter}.1. Ticket Status Count Across {trend_text} (Open, In-Progress, Pending, On-hold, Closed)</div>', unsafe_allow_html=True)

            # Create detailed breakdown charts side-by-side (like Main Dashboard Report)
            # Each month gets its own chart showing status breakdown
            if num_months == 1:
                chart_cols = [st.container()]
            else:
                chart_cols = st.columns(num_months)

            severity_colors = {
                'Critical': '#DC143C',
                'High': '#FF8C00',
                'Medium': '#4169E1',
                'Low': '#70AD47'
            }

            all_statuses = ['closed', 'in_progress', 'open', 'pending', 'on-hold']

            for idx, month_name in enumerate(sorted_months):
                pivot_key = month_data_map[month_name]
                pivot_df = ticket_data[pivot_key]

                if not isinstance(pivot_df, pd.DataFrame) or pivot_df.empty:
                    continue

                # Get display name for this month
                month_display = custom_month_names[month_name]

                # Aggregate by Status for this month
                month_agg = pivot_df.groupby('Status')[['Critical', 'High', 'Medium', 'Low']].sum().reset_index()

                # Create figure for this month
                fig = go.Figure()

                # Add bars for each severity
                for severity in ['Critical', 'High', 'Medium', 'Low']:
                    if severity in month_agg.columns:
                        fig.add_trace(go.Bar(
                            name=severity,
                            x=month_agg['Status'],
                            y=month_agg[severity],
                            marker_color=severity_colors[severity],
                            text=month_agg[severity],
                            textposition='outside',
                            hovertemplate=f'<b>{severity}</b><br>Status: %{{x}}<br>Count: %{{y}}<extra></extra>'
                        ))

                # Only show legend on the last (rightmost) chart
                show_legend = (idx == len(sorted_months) - 1)

                fig.update_layout(
                    barmode='group',
                    xaxis_title=dict(
                        text=month_display,
                        font=dict(size=12, color='#666666')
                    ),
                    yaxis_title=dict(
                        text="Number of Detections",
                        font=dict(size=10, color='#666666')
                    ),
                    yaxis=dict(
                        tickfont=dict(size=9, color='#666666')
                    ),
                    height=240,
                    showlegend=show_legend,
                    legend=dict(
                        title=dict(text="Severity", font=dict(size=11)),
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10)
                    ),
                    margin=dict(l=40, r=40, t=30, b=50),  # Increased top and bottom margins for text labels
                    uniformtext_minsize=8,
                    uniformtext_mode='hide'
                )

                # Update text position to prevent clipping at top
                fig.update_traces(
                    textposition='outside',
                    cliponaxis=False
                )

                # Display in appropriate column
                if num_months == 1:
                    with chart_cols[0]:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    with chart_cols[idx]:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # ============================
            # A.2: Ticket Detection Summary Overview (Per Month) - Horizontal Category Layout
            # ============================
            st.markdown(f'<div class="chart-title">{section_letter}.2. Ticket Detection Summary Overview</div>', unsafe_allow_html=True)

            # Collect data for all months first
            month_data_list = []
            for idx, month_name in enumerate(sorted_months):
                month_safe = month_name.replace(' ', '_').replace(',', '')
                month_display = custom_month_names[month_name]
                pivot_key = month_data_map[month_name]
                pivot_df = ticket_data[pivot_key]

                if not isinstance(pivot_df, pd.DataFrame) or pivot_df.empty:
                    continue

                # Get summary data for this month
                summary_key = f'ticket_summary_{month_safe}'
                summary_data = ticket_data.get(summary_key, {})

                # Default values
                total_alerts = summary_data.get('total_alerts', 0)
                alerts_resolved = summary_data.get('alerts_resolved', 0)
                alerts_pending = summary_data.get('alerts_pending', 0)

                # Use pending_request_ids from summary_data (allows manual override from builder)
                pending_request_str = summary_data.get('pending_request_ids', '')
                if not pending_request_str:
                    pending_request_str = "None"

                # Determine monthly color based on index (1st=Green, 2nd=Blue, 3rd=Gold)
                if idx == 0:
                    month_color = MONTHLY_COLORS['month_1']  # Green
                elif idx == 1:
                    month_color = MONTHLY_COLORS['month_2']  # Blue
                else:
                    month_color = MONTHLY_COLORS['month_3']  # Gold

                month_data_list.append({
                    'month_display': month_display,
                    'month_color': month_color,
                    'total_alerts': total_alerts,
                    'alerts_resolved': alerts_resolved,
                    'alerts_pending': alerts_pending,
                    'pending_request_str': pending_request_str
                })

            # Compact table-style layout - all data in organized rows
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

            # Build HTML table structure with card-style rows and spacing
            table_html = '<div style="display: flex; flex-direction: column; gap: 8px; margin: 10px 0;">'

            # Header row with month names
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 12px; font-weight: bold; color: #333; font-size: 13px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Metric</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 12px; text-align: center; font-weight: bold; background: {month_info["month_color"]}; color: black; font-size: 12px; border-radius: 8px;">{month_info["month_display"]}</div>'
            table_html += '</div>'

            # Row 1: Triggered Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Triggered</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["total_alerts"]}</span></div>'
            table_html += '</div>'

            # Row 2: Resolved Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Resolved</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["alerts_resolved"]}</span></div>'
            table_html += '</div>'

            # Row 3: Pending Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Pending</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["alerts_pending"]}</span></div>'
            table_html += '</div>'

            table_html += '</div>'

            st.markdown(table_html, unsafe_allow_html=True)

            # Pending Request IDs section below table - compact display
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            pending_cols = st.columns(num_months)
            for idx, month_info in enumerate(month_data_list):
                with pending_cols[idx]:
                    # Show all pending Request IDs with alert counts (no limit)
                    if month_info['pending_request_str'] != "None":
                        st.markdown(f"""
                            <div style='background: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid {month_info['month_color']};
                                        font-size: 11px;
                                        max-height: 150px;
                                        overflow-y: auto;'>
                                <strong style='color: #333; font-size: 12px;'>Pending Request IDs:</strong><br>
                                <span style='color: #666;'>{month_info['pending_request_str']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style='background: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid {month_info['month_color']};
                                        font-size: 11px;
                                        text-align: center;'>
                                <span style='color: #999; font-style: italic;'>No pending alerts</span>
                            </div>
                        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section A

        # PAGE BREAK AFTER SECTION A IF INCLUDED
        st.markdown('<div class="page-break-after"></div>', unsafe_allow_html=True)

    # ============================================
    # HOST SECURITY ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_host_analysis:
        section_letter = section_letters.get('host', 'A')
        st.markdown(f'<div class="section-header">{section_letter}. Host Security Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Overview Detection (full width)
        st.markdown(f'<div class="chart-title">{section_letter}.1. Host Overview Detection Across {month_text} Trends</div>', unsafe_allow_html=True)
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

        # Subsection 2 and 3 side by side
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="chart-title">{section_letter}.2. Top Hosts with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="chart-title">{section_letter}.3. Users with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
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

        # Sensor Versions (full width)
        st.markdown(f'<div class="chart-title">{section_letter}.4. Detections Hosts with Sensor Versions Status Across {month_text}</div>', unsafe_allow_html=True)
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

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section B

        # PAGE BREAK AFTER SECTION B (Only if ticket lifecycle was not included)
        if not include_ticket_lifecycle:
            st.markdown('<div class="page-break-after"></div>', unsafe_allow_html=True)

    # ============================================
    # DETECTION AND SEVERITY ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_detection_analysis:
        section_letter = section_letters.get('detection', 'B')
        st.markdown(f'<div class="section-header">{section_letter}. Detection and Severity Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Critical and High Detection Overview - Side by Side Layout
        st.markdown(f'<div class="chart-title">{section_letter}.1. Detection Count by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)

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

                # Build list of box data with index-based monthly colors (like A.2)
                box_data = []
                for idx, month in enumerate(months):
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

                    # Get month color based on index (1st=Green, 2nd=Blue, 3rd=Gold)
                    if idx == 0:
                        month_color = MONTHLY_COLORS['month_1']  # Green
                    elif idx == 1:
                        month_color = MONTHLY_COLORS['month_2']  # Blue
                    else:
                        month_color = MONTHLY_COLORS['month_3']  # Gold

                    box_data.append((month, count_value, month_color))

                # Create horizontal container for boxes with monthly colors and larger font (36px like A.2)
                boxes_html = '<div style="display: flex; gap: 8px; justify-content: center;">'
                for month, count_value, month_color in box_data:
                    boxes_html += f'<div style="background-color: {month_color}; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); flex: 1; min-width: 80px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 12px; color: #000000; font-weight: 600; margin-bottom: 5px;">{month}</div><div style="font-size: 36px; color: #000000; font-weight: bold; margin: 5px 0;">{count_value}</div><div style="font-size: 10px; color: #000000;">Critical</div></div>'
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

        # C.2 and C.3 side by side
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="chart-title">{section_letter}.2. Detection Count by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="chart-title">{section_letter}.3. Detection Count by Country Across {month_text} Trends</div>', unsafe_allow_html=True)
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

        # Files (bar chart with filename on x-axis)
        st.markdown(f'<div class="chart-title">{section_letter}.4. File Name with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
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

        # C.5 and C.6 side by side
        col1, col2 = st.columns(2)

        with col1:
            # Tactics (area chart)
            st.markdown(f'<div class="chart-title">{section_letter}.5. Tactics by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
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
            # Technique (area chart)
            st.markdown(f'<div class="chart-title">{section_letter}.6. Technique by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
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
                    analysis_key='technique_by_severity_c6',  # Unique key for C.6
                    top_n={'enabled': True, 'field': 'Technique', 'n': 10, 'type': 'top', 'by_field': 'Count', 'per_month': False},
                    use_severity_colors=True,
                    use_monthly_colors=True
                )

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section C

    # ============================================
    # TIME-BASED ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_time_analysis:
        section_letter = section_letters.get('time', 'C')
        st.markdown(f'<div class="section-header">{section_letter}. Time-Based Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Daily Trend (full width) - Use exact same logic as pivot table builder
        st.markdown(f'<div class="chart-title">{section_letter}.1. Detection Over Multiple Days Across {month_text} Trends - Top 3</div>', unsafe_allow_html=True)
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

        # D.2 and D.3 side by side - EXACT SAME STYLING as pivot table builder
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="chart-title">{section_letter}.2. Hourly Distribution of Detections Across {month_text} Trends</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="chart-title">{section_letter}.3. Detection Frequency by Day of Week Across {month_text} Trends</div>', unsafe_allow_html=True)
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

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section D

    # ============================================
    # EXECUTIVE SUMMARY SECTION (DYNAMIC)
    # ============================================
    if include_executive_summary:
        section_letter = section_letters.get('executive', 'E')
        render_executive_summary(
            ticket_data=ticket_data,
            host_data=host_data,
            detection_data=detection_data,
            time_data=time_data,
            num_months=num_months,
            section_letter=section_letter
        )


def create_chart_with_pivot_logic(df, rows, columns, values, chart_type, height, analysis_key, top_n=None, use_severity_colors=False, use_ticket_status_colors=False, use_monthly_colors=False, sort_by=None, sort_direction='descending'):
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
        'use_ticket_status_colors': use_ticket_status_colors,
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
        'time_analysis_results' in st.session_state or
        'ticket_lifecycle_results' in st.session_state
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
