"""
Ticket Lifecycle Analysis Generator
Generates 3-month trend analysis for ticket status (Open, Pending, On-hold, Closed)
Developed by Izami Ariff © 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List

def generate_ticket_lifecycle_analysis(ticket_df: pd.DataFrame, num_months: int) -> Dict[str, pd.DataFrame]:
    """
    Generate ticket lifecycle analysis from ticket data

    Args:
        ticket_df: DataFrame with ticket data (must have 'Period', 'Status' columns)
        num_months: Number of months in the data (1-3)

    Returns:
        Dictionary with ticket lifecycle analysis results
    """

    results = {}

    if ticket_df.empty:
        return results

    # Ensure required columns exist
    if 'Period' not in ticket_df.columns:
        ticket_df['Period'] = 'Unknown'
    if 'Status' not in ticket_df.columns:
        ticket_df['Status'] = 'Unknown'

    # Create Month column (same as Period for consistency)
    ticket_df['Month'] = ticket_df['Period']

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

    # Define ticket statuses
    statuses = ['Open', 'Pending', 'On-hold', 'Closed']

    # Create placeholder data
    data = []
    ticket_id = 1

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
                data.append({
                    'TicketID': f'TKT-{ticket_id:05d}',
                    'Period': month,
                    'Status': status,
                    'CreatedDate': f'{month}-01',  # Placeholder date
                    'Category': 'Security Incident',  # Placeholder category
                    'Priority': 'Medium'  # Placeholder priority
                })
                ticket_id += 1

    return pd.DataFrame(data)
