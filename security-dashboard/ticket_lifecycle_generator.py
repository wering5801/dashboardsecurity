"""
Ticket Lifecycle Analysis Generator
Generates Detection Status by Severity with Request ID pivot table format
Shows: Request IDs grouped by Status, with Severity counts

CSV Format Required:
- Period: Month name (e.g., "October 2025", "November 2025")
- Status: closed, in_progress, open, pending, on-hold
- SeverityName: Critical, High, Medium, Low
- Request ID: Detection identifier (REQUIRED)

Developed by Izami Ariff © 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List

def generate_ticket_lifecycle_analysis(ticket_df: pd.DataFrame, num_months: int) -> Dict[str, pd.DataFrame]:
    """
    Generate detection status analysis by severity with Request ID pivot table

    Args:
        ticket_df: DataFrame with ticket data (must have 'Period', 'Status', 'SeverityName', 'Request ID' columns)
        num_months: Number of months in the data (1-3)

    Returns:
        Dictionary with analysis results including Request ID x Severity pivot tables
    """

    results = {}

    if ticket_df.empty:
        return results

    # Ensure required columns exist
    if 'Period' not in ticket_df.columns:
        ticket_df['Period'] = 'Unknown'
    if 'Status' not in ticket_df.columns:
        ticket_df['Status'] = 'Unknown'

    # Request ID is required for this format
    if 'Request ID' not in ticket_df.columns and 'RequestID' not in ticket_df.columns:
        ticket_df['Request ID'] = range(1, len(ticket_df) + 1)
    elif 'RequestID' in ticket_df.columns:
        ticket_df['Request ID'] = ticket_df['RequestID']

    # Check for SeverityName column (required)
    has_severity = 'SeverityName' in ticket_df.columns or 'Severity' in ticket_df.columns

    if not has_severity:
        # Add default severity if not provided
        ticket_df['SeverityName'] = 'N/A'
    elif 'Severity' in ticket_df.columns and 'SeverityName' not in ticket_df.columns:
        ticket_df['SeverityName'] = ticket_df['Severity']

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
        'LOW': 'Low',
        'N/A': 'N/A',
        'n/a': 'N/A'
    }
    ticket_df['SeverityName'] = ticket_df['SeverityName'].fillna('N/A').map(severity_mapping).fillna(ticket_df['SeverityName'])

    # Normalize status values
    status_mapping = {
        'closed': 'closed',
        'Closed': 'closed',
        'CLOSED': 'closed',
        'in_progress': 'in_progress',
        'In Progress': 'in_progress',
        'IN_PROGRESS': 'in_progress',
        'in progress': 'in_progress',
        'open': 'open',
        'Open': 'open',
        'OPEN': 'open',
        'pending': 'pending',
        'Pending': 'pending',
        'PENDING': 'pending',
        'on-hold': 'on-hold',
        'On-hold': 'on-hold',
        'ON-HOLD': 'on-hold',
        'on hold': 'on-hold'
    }
    ticket_df['Status'] = ticket_df['Status'].map(status_mapping).fillna(ticket_df['Status'])

    # Create Month column (same as Period for consistency)
    ticket_df['Month'] = ticket_df['Period']

    # Check if "Count of SeverityName" column exists (new format)
    has_count_column = 'Count of SeverityName' in ticket_df.columns

    # If count column exists, expand the data to individual rows
    if has_count_column:
        # Expand rows based on count
        expanded_rows = []
        for _, row in ticket_df.iterrows():
            count = int(row.get('Count of SeverityName', 1))
            for _ in range(count):
                expanded_rows.append(row.to_dict())
        ticket_df = pd.DataFrame(expanded_rows)

    # ============================================
    # Process each month separately
    # ============================================
    for month in ticket_df['Month'].unique():
        month_df = ticket_df[ticket_df['Month'] == month].copy()
        month_safe = month.replace(' ', '_').replace(',', '')

        # ============================================
        # 1. NEW FORMAT: Request ID x Severity Pivot Table
        # Rows: Grouped by Status, then Request ID
        # Columns: Critical, High, Medium, Low
        # ============================================

        # Create the pivot table with Request ID and Status as multi-index
        pivot_data = []

        # Group by Status first, then by Request ID within each status
        for status in ['closed', 'in_progress', 'open', 'pending', 'on-hold']:
            status_df = month_df[month_df['Status'] == status]

            if not status_df.empty:
                # Get unique Request IDs for this status
                request_ids = status_df['Request ID'].unique()

                for req_id in request_ids:
                    req_df = status_df[status_df['Request ID'] == req_id]

                    # Count severity for this Request ID
                    row_data = {
                        'Status': status,
                        'Request ID': req_id,
                        'Critical': len(req_df[req_df['SeverityName'] == 'Critical']),
                        'High': len(req_df[req_df['SeverityName'] == 'High']),
                        'Medium': len(req_df[req_df['SeverityName'] == 'Medium']),
                        'Low': len(req_df[req_df['SeverityName'] == 'Low'])
                    }
                    pivot_data.append(row_data)

        # Create DataFrame
        pivot_df = pd.DataFrame(pivot_data)

        # Store the pivot table
        results[f'request_severity_pivot_{month_safe}'] = pivot_df

        # ============================================
        # 2. Ticket Summary Metrics (Section A.2)
        # ============================================
        total_alerts = len(month_df)
        alerts_resolved = len(month_df[month_df['Status'] == 'closed'])
        alerts_pending = len(month_df[month_df['Status'].isin(['open', 'pending', 'on-hold', 'in_progress'])])

        summary_data = {
            'total_alerts': total_alerts,
            'alerts_resolved': alerts_resolved,
            'alerts_pending': alerts_pending
        }

        results[f'ticket_summary_{month_safe}'] = summary_data

        # ============================================
        # 3. Chart Data for visualization
        # ============================================
        # Stacked bar chart data: Request ID x Severity
        chart_data = month_df.groupby(['Request ID', 'Status', 'SeverityName']).size().reset_index(name='Count')
        results[f'chart_data_{month_safe}'] = chart_data

        # Store raw data for export
        results[f'raw_data_{month_safe}'] = month_df

    return results


def create_placeholder_ticket_data(months: List[str], custom_counts_per_month: Dict[str, Dict[str, int]] = None) -> pd.DataFrame:
    """
    Create placeholder ticket data structure with example values
    Users can replace these with real data

    Args:
        months: List of month names (e.g., ['October 2025', 'November 2025', 'December 2025'])
        custom_counts_per_month: Optional dictionary with custom ticket counts per month
                                e.g., {
                                    'October 2025': {'Open': 30, 'Pending': 20, 'On-hold': 15, 'Closed': 60},
                                    'November 2025': {'Open': 25, 'Pending': 18, 'On-hold': 12, 'Closed': 55}
                                }

    Returns:
        DataFrame with placeholder ticket data
    """

    # Define ticket statuses and severities
    statuses = ['Open', 'Pending', 'On-hold', 'Closed']
    severities = ['Critical', 'High', 'Medium', 'Low']

    # Severity distribution weights
    severity_weights = [0.1, 0.3, 0.4, 0.2]  # Critical, High, Medium, Low

    # Create placeholder data
    data = []
    ticket_id = 1

    import random

    for month in months:
        # Use custom counts for this specific month if provided, otherwise use defaults
        if custom_counts_per_month and month in custom_counts_per_month:
            ticket_counts = custom_counts_per_month[month]
        else:
            # Example distribution (default values)
            ticket_counts = {
                'Open': 25,      # Example: 25 open tickets
                'Pending': 15,   # Example: 15 pending tickets
                'On-hold': 10,   # Example: 10 on-hold tickets
                'Closed': 50     # Example: 50 closed tickets
            }

        # Create records for each status
        for status, count in ticket_counts.items():
            for _ in range(count):
                # Assign severity based on weights
                severity = random.choices(severities, weights=severity_weights)[0]

                data.append({
                    'TicketID': f'TKT-{ticket_id:05d}',
                    'Period': month,
                    'Status': status,
                    'SeverityName': severity,  # NEW: Add severity
                    'Request ID': 500000 + ticket_id,  # NEW: Add Request ID
                    'CreatedDate': f'{month}-01',  # Placeholder date
                    'Category': 'Security Incident',  # Placeholder category
                    'Priority': 'Medium'  # Placeholder priority
                })
                ticket_id += 1

    return pd.DataFrame(data)
