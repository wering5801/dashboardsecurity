"""
Ticket Lifecycle Analysis Generator
Generates analysis for Detection Status by Severity (Status x Severity pivot)
Shows: Total Detections Count by Status and Severity for each month

CSV Format Required:
- Period: Month name (e.g., "October 2025", "November 2025")
- Status: closed, in_progress, open, pending, on-hold
- SeverityName: Critical, High, Medium, Low
- Request ID: Detection identifier (optional)

Developed by Izami Ariff © 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List

def generate_ticket_lifecycle_analysis(ticket_df: pd.DataFrame, num_months: int) -> Dict[str, pd.DataFrame]:
    """
    Generate detection status analysis by severity

    Args:
        ticket_df: DataFrame with ticket data (must have 'Period', 'Status', 'SeverityName' columns)
        num_months: Number of months in the data (1-3)

    Returns:
        Dictionary with analysis results including Status x Severity pivot tables
    """

    results = {}

    if ticket_df.empty:
        return results

    # Ensure required columns exist
    if 'Period' not in ticket_df.columns:
        ticket_df['Period'] = 'Unknown'
    if 'Status' not in ticket_df.columns:
        ticket_df['Status'] = 'Unknown'

    # Check for SeverityName column (new requirement)
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

    # Add Request ID if not present
    if 'Request ID' not in ticket_df.columns and 'RequestID' not in ticket_df.columns:
        ticket_df['Request ID'] = range(1, len(ticket_df) + 1)

    # ============================================
    # 1. Ticket Status Overview (3-month trend)
    # ============================================
    # Count tickets by Status and Month
    status_counts = ticket_df.groupby(['Month', 'Status']).size().reset_index(name='Count')

    # Pivot to have Status as rows, Month as columns for easier visualization
    status_pivot = status_counts.pivot_table(
        index='Status',
        columns='Month',
        values='Count',
        fill_value=0
    ).reset_index()

    # Also create a format suitable for bar charts (Month, Status, Count)
    results['ticket_status_trend'] = status_counts
    results['ticket_status_pivot'] = status_pivot

    # ============================================
    # 2. Monthly Ticket Summary (for key metrics cards)
    # ============================================
    # Total tickets per month
    monthly_totals = ticket_df.groupby('Month').size().reset_index(name='Total Tickets')

    # Status breakdown per month
    monthly_breakdown = ticket_df.groupby(['Month', 'Status']).size().reset_index(name='Count')

    # Pivot for easier access
    monthly_breakdown_pivot = monthly_breakdown.pivot_table(
        index='Month',
        columns='Status',
        values='Count',
        fill_value=0
    ).reset_index()

    results['monthly_summary'] = monthly_breakdown_pivot
    results['monthly_totals'] = monthly_totals

    # ============================================
    # 3. Status Distribution (for pie/donut charts)
    # ============================================
    # Overall status distribution across all months
    status_distribution = ticket_df.groupby('Status').size().reset_index(name='Count')
    status_distribution['Percentage'] = (status_distribution['Count'] / status_distribution['Count'].sum() * 100).round(2)
    results['status_distribution'] = status_distribution

    # ============================================
    # 4. Detection Status by Severity (NEW - Status x Severity Pivot)
    # ============================================
    # Create pivot table: Status (rows) x Severity (columns) with Request ID count
    # This shows "Total Detections Count by Status and Severity" per month

    # Process each month separately
    for month in ticket_df['Month'].unique():
        month_df = ticket_df[ticket_df['Month'] == month].copy()

        # Create pivot table: Status x SeverityName
        status_severity_pivot = pd.pivot_table(
            month_df,
            values='Request ID',
            index='Count of SeverityName\nStatus',  # This creates the row header
            columns='SeverityName',
            aggfunc='count',
            fill_value=0
        )

        # Actually, let's create it properly with Status as index
        status_severity_pivot = pd.crosstab(
            month_df['Status'],
            month_df['SeverityName'],
            margins=True,
            margins_name='Grand Total'
        )

        # Store with month-specific key
        month_safe = month.replace(' ', '_').replace(',', '')
        results[f'status_severity_{month_safe}'] = status_severity_pivot

        # Also create data suitable for stacked bar charts
        chart_data = month_df.groupby(['Status', 'SeverityName']).size().reset_index(name='Count')
        results[f'status_severity_chart_{month_safe}'] = chart_data

    # Create overall Status x Severity pivot (all months combined)
    status_severity_overall = pd.crosstab(
        ticket_df['Status'],
        ticket_df['SeverityName'],
        margins=True,
        margins_name='Grand Total'
    )
    results['status_severity_overall'] = status_severity_overall

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
