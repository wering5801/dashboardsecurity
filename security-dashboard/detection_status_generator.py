"""
Detection Status Generator
Combines Ticket Status with Detection Severity Analysis
Shows: Total Detections Count by Status and Severity for each month

Expected CSV Format:
- Status: closed, in_progress, open, pending, on-hold
- SeverityName: Critical, High, Medium, Low
- Request ID: Detection identifier
- Month/Period: Date or month name

Developed by Izami Ariff © 2025
"""

import pandas as pd
import streamlit as st
from datetime import datetime

def generate_detection_status_analysis(df_list, month_names=None):
    """
    Generate detection status analysis combining ticket status with severity

    Args:
        df_list: List of DataFrames (one per month)
        month_names: List of month names

    Returns:
        Dictionary containing analysis results
    """

    if not df_list or all(df is None or df.empty for df in df_list):
        return None

    results = {}

    # Process each month's data
    for idx, df in enumerate(df_list):
        if df is None or df.empty:
            continue

        # Get month name
        if month_names and idx < len(month_names):
            month_name = month_names[idx]
        else:
            month_name = f"Month {idx + 1}"

        # Clean and normalize column names
        df.columns = df.columns.str.strip()

        # Required columns
        required_cols = {
            'status': ['Status', 'status', 'TICKET_STATUS', 'TicketStatus'],
            'severity': ['SeverityName', 'Severity', 'severity', 'SEVERITY'],
            'request_id': ['Request ID', 'RequestID', 'request_id', 'DetectionID', 'ID']
        }

        # Find actual column names
        col_mapping = {}
        for key, possible_names in required_cols.items():
            for col in df.columns:
                if col in possible_names:
                    col_mapping[key] = col
                    break

        # Check if required columns exist
        if 'status' not in col_mapping or 'severity' not in col_mapping:
            st.warning(f"Missing required columns in {month_name}. Required: Status and SeverityName")
            continue

        # Create working dataframe with normalized columns
        work_df = pd.DataFrame()
        work_df['Status'] = df[col_mapping['status']].fillna('Unknown')
        work_df['SeverityName'] = df[col_mapping['severity']].fillna('Unknown')

        # Add Request ID if available
        if 'request_id' in col_mapping:
            work_df['RequestID'] = df[col_mapping['request_id']]
        else:
            work_df['RequestID'] = range(len(work_df))

        # Normalize status values
        status_mapping = {
            'closed': 'closed',
            'Closed': 'closed',
            'CLOSED': 'closed',
            'in_progress': 'in_progress',
            'In Progress': 'in_progress',
            'IN_PROGRESS': 'in_progress',
            'open': 'open',
            'Open': 'open',
            'OPEN': 'open',
            'pending': 'pending',
            'Pending': 'pending',
            'PENDING': 'pending',
            'on-hold': 'on-hold',
            'On-hold': 'on-hold',
            'ON-HOLD': 'on-hold'
        }
        work_df['Status'] = work_df['Status'].map(status_mapping).fillna(work_df['Status'])

        # Normalize severity values
        severity_mapping = {
            'critical': 'Critical',
            'Critical': 'Critical',
            'CRITICAL': 'Critical',
            'high': 'High',
            'High': 'High',
            'HIGH': 'High',
            'medium': 'Medium',
            'Medium': 'Medium',
            'MEDIUM': 'Medium',
            'low': 'Low',
            'Low': 'Low',
            'LOW': 'Low'
        }
        work_df['SeverityName'] = work_df['SeverityName'].map(severity_mapping).fillna(work_df['SeverityName'])

        # 1. Create Pivot Table: Status x Severity with Request IDs as columns
        pivot_by_request = pd.pivot_table(
            work_df,
            values='RequestID',
            index='Status',
            columns='SeverityName',
            aggfunc='count',
            fill_value=0
        )

        # Add Grand Total column and row
        pivot_by_request['Grand Total'] = pivot_by_request.sum(axis=1)
        pivot_by_request.loc['Grand Total'] = pivot_by_request.sum(axis=0)

        # 2. Create data for stacked bar chart
        chart_data = work_df.groupby(['Status', 'SeverityName']).size().reset_index(name='Count')

        # 3. Summary statistics
        total_detections = len(work_df)
        status_counts = work_df['Status'].value_counts().to_dict()
        severity_counts = work_df['SeverityName'].value_counts().to_dict()

        # 4. Critical metrics
        critical_closed = len(work_df[(work_df['Status'] == 'closed') & (work_df['SeverityName'] == 'Critical')])
        high_closed = len(work_df[(work_df['Status'] == 'closed') & (work_df['SeverityName'] == 'High')])
        critical_open = len(work_df[(work_df['Status'].isin(['open', 'in_progress'])) & (work_df['SeverityName'] == 'Critical')])
        high_open = len(work_df[(work_df['Status'].isin(['open', 'in_progress'])) & (work_df['SeverityName'] == 'High')])

        # Store results for this month
        results[month_name] = {
            'pivot_table': pivot_by_request,
            'chart_data': chart_data,
            'raw_data': work_df,
            'total_detections': total_detections,
            'status_counts': status_counts,
            'severity_counts': severity_counts,
            'metrics': {
                'critical_closed': critical_closed,
                'high_closed': high_closed,
                'critical_open': critical_open,
                'high_open': high_open,
                'closure_rate': (len(work_df[work_df['Status'] == 'closed']) / total_detections * 100) if total_detections > 0 else 0
            }
        }

    return results


def create_placeholder_detection_status_data(num_months=1):
    """
    Create placeholder data for detection status analysis

    Args:
        num_months: Number of months to generate

    Returns:
        List of DataFrames with sample data
    """

    import random

    month_names = [
        "October 2025", "November 2025", "December 2025",
        "January 2026", "February 2026", "March 2026"
    ]

    statuses = ['closed', 'in_progress', 'open', 'pending']
    severities = ['Critical', 'High', 'Medium', 'Low']

    df_list = []

    for i in range(num_months):
        records = []
        request_id_base = 503000 + (i * 1000)

        # Generate 15-25 records per month
        num_records = random.randint(15, 25)

        for j in range(num_records):
            # Higher chance of closed status
            status_weights = [0.6, 0.2, 0.1, 0.1]  # closed, in_progress, open, pending
            status = random.choices(statuses, weights=status_weights)[0]

            # Severity distribution
            severity_weights = [0.1, 0.3, 0.4, 0.2]  # Critical, High, Medium, Low
            severity = random.choices(severities, weights=severity_weights)[0]

            records.append({
                'Status': status,
                'SeverityName': severity,
                'Request ID': request_id_base + j,
                'Month': month_names[i] if i < len(month_names) else f"Month {i+1}"
            })

        df_list.append(pd.DataFrame(records))

    return df_list, month_names[:num_months]
