"""
Host Analysis Generator
Converts Host Analysis Template to Analysis Results
Replicates host-analysis-dashboard-generator v2.1.html logic

Outputs:
1. Overview - KEY METRICS
2. Overview - TOP HOSTS WITH DETECTIONS
3. User Analysis
4. Sensor Analysis

With Month column for multi-month support
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_host_analysis(host_template_df, num_months=1):
    """
    Generate host analysis results from template

    Parameters:
    - host_template_df: DataFrame from falcon generator (Host Analysis template)
    - num_months: Number of months in the dataset (1, 2, or 3)

    Returns:
    - Dictionary containing all analysis results as DataFrames
    """

    print(f"[Host Analysis Generator] Processing {len(host_template_df)} records for {num_months} month(s)...")

    # Ensure required columns exist
    required_cols = ['UniqueNo', 'Hostname', 'UserName', 'OS Version', 'Sensor Version',
                     'Site', 'OU', 'Period']

    missing_cols = [col for col in required_cols if col not in host_template_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Clean data - remove empty rows
    df = host_template_df.copy()
    df = df[df['Hostname'].notna() & (df['Hostname'] != '')]
    df = df[df['UniqueNo'].notna()]

    # Extract Month from Period if not exists
    if 'Month' not in df.columns and 'Period' in df.columns:
        df['Month'] = df['Period']

    print(f"[Host Analysis Generator] Clean data: {len(df)} valid records")

    # Generate all analysis results
    results = {
        'overview_key_metrics': generate_overview_key_metrics(df, num_months),
        'overview_top_hosts': generate_top_hosts_with_detections(df, num_months),
        'user_analysis': generate_user_analysis(df, num_months),
        'sensor_analysis': generate_sensor_analysis(df, num_months),
        'raw_data': df  # Include raw data for pivot table builder
    }

    print(f"[Host Analysis Generator] Generated {len(results)} analysis outputs")

    return results


def generate_overview_key_metrics(df, num_months):
    """
    Generate Overview - KEY METRICS in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - KEY METRICS: Metric name (Total Hosts, Total Detections, etc.)
    - Month: Month name
    - Analysis: Always "Host Analysis Overview"
    - DataSource: Always "Host Analysis Overview"
    - Count: Metric value
    """

    long_format_rows = []

    if num_months > 1:
        # Multi-month analysis - create row for each metric x month
        for month in sorted(df['Month'].unique()):
            month_df = df[df['Month'] == month]

            total_hosts = month_df['Hostname'].nunique()
            total_detections = len(month_df)
            unique_users = month_df['UserName'].nunique()
            windows_hosts = month_df[month_df['OS Version'].str.contains('Windows', case=False, na=False)]['Hostname'].nunique()
            avg_detections = total_detections / total_hosts if total_hosts > 0 else 0

            # Create a row for each metric
            metrics = [
                ('Total Hosts', total_hosts),
                ('Total Detections', total_detections),
                ('Unique Users', unique_users),
                ('Windows Hosts', windows_hosts),
                ('Avg_Detection', round(avg_detections, 1))
            ]

            for metric_name, metric_value in metrics:
                long_format_rows.append({
                    'KEY METRICS': metric_name,
                    'Month': month,
                    'Analysis': 'Host Analysis Overview',
                    'DataSource': 'Host Analysis Overview',
                    'Count': metric_value
                })

    else:
        # Single month analysis
        month = df['Month'].iloc[0] if 'Month' in df.columns else 'Single Month'

        total_hosts = df['Hostname'].nunique()
        total_detections = len(df)
        unique_users = df['UserName'].nunique()
        windows_hosts = df[df['OS Version'].str.contains('Windows', case=False, na=False)]['Hostname'].nunique()
        avg_detections = total_detections / total_hosts if total_hosts > 0 else 0

        metrics = [
            ('Total Hosts', total_hosts),
            ('Total Detections', total_detections),
            ('Unique Users', unique_users),
            ('Windows Hosts', windows_hosts),
            ('Avg_Detection', round(avg_detections, 1))
        ]

        for metric_name, metric_value in metrics:
            long_format_rows.append({
                'KEY METRICS': metric_name,
                'Month': month,
                'Analysis': 'Host Analysis Overview',
                'DataSource': 'Host Analysis Overview',
                'Count': metric_value
            })

    metrics_df = pd.DataFrame(long_format_rows)

    print(f"[Host Analysis] KEY METRICS generated: {len(metrics_df)} row(s) in LONG FORMAT")
    return metrics_df


def generate_top_hosts_with_detections(df, num_months, top_n=10):
    """
    Generate Overview - TOP HOSTS WITH MOST DETECTIONS in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - TOP HOSTS WITH MOST DETECTIONS: Host computer name (for pivot table grouping)
    - Month: Month name
    - Analysis: Always "Host Analysis Overview"
    - DataSource: Always "Host Analysis Overview"
    - Count: Detection count for this host in this month
    - Percentage: Percentage of total detections

    Note: Returns top 10 hosts by default, but can be filtered to top 5 in pivot table
    """

    # Get detection counts per host per month
    host_month_counts = df.groupby(['Hostname', 'Month']).size().reset_index(name='Count')

    # Calculate total detections per host to identify top N
    host_totals = host_month_counts.groupby('Hostname')['Count'].sum().reset_index(name='Total')
    top_hosts = host_totals.nlargest(top_n, 'Total')['Hostname'].tolist()

    # Filter to only top N hosts
    top_hosts_df = host_month_counts[host_month_counts['Hostname'].isin(top_hosts)].copy()

    # Calculate percentage per month
    month_totals = df.groupby('Month').size().to_dict()
    top_hosts_df['Percentage'] = top_hosts_df.apply(
        lambda row: round((row['Count'] / month_totals.get(row['Month'], 1)) * 100, 1),
        axis=1
    )

    # Add Analysis and DataSource columns
    top_hosts_df['Analysis'] = 'Host Analysis Overview'
    top_hosts_df['DataSource'] = 'Host Analysis Overview'

    # Rename Hostname to clearer name
    top_hosts_df = top_hosts_df.rename(columns={'Hostname': 'TOP HOSTS WITH MOST DETECTIONS'})

    # Reorder columns to match Excel format
    top_hosts_df = top_hosts_df[['TOP HOSTS WITH MOST DETECTIONS', 'Month', 'Analysis', 'DataSource', 'Count', 'Percentage']]

    # Sort by total count (descending) then by Month
    # Calculate total for sorting
    host_total_map = host_totals.set_index('Hostname')['Total'].to_dict()
    top_hosts_df['_TotalCount'] = top_hosts_df['TOP HOSTS WITH MOST DETECTIONS'].map(host_total_map)
    top_hosts_df = top_hosts_df.sort_values(['_TotalCount', 'TOP HOSTS WITH MOST DETECTIONS', 'Month'], ascending=[False, True, True])
    top_hosts_df = top_hosts_df.drop(columns=['_TotalCount'])

    print(f"[Host Analysis] TOP HOSTS generated: {len(top_hosts_df)} row(s) in LONG FORMAT for {len(top_hosts)} host(s)")
    return top_hosts_df


def generate_user_analysis(df, num_months, top_n=5):
    """
    Generate User Analysis in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - Username: User account name
    - Month: Month name
    - AnalysisType: Always "Host Analysis: User Analysis"
    - DataSource: Always "Host Analysis: User Analysis"
    - Count of Detection: Detection count for this user in this month
    - Percentage: Percentage of total detections
    """

    # Filter out empty usernames
    df_users = df[df['UserName'].notna() & (df['UserName'] != '')]

    # Get detection counts per user per month
    user_month_counts = df_users.groupby(['UserName', 'Month']).size().reset_index(name='Count of Detection')

    # Calculate total detections per user to identify top N
    user_totals = user_month_counts.groupby('UserName')['Count of Detection'].sum().reset_index(name='Total')
    top_users = user_totals.nlargest(top_n, 'Total')['UserName'].tolist()

    # Filter to only top N users
    user_analysis_df = user_month_counts[user_month_counts['UserName'].isin(top_users)].copy()

    # Calculate percentage per month
    month_totals = df_users.groupby('Month').size().to_dict()
    user_analysis_df['Percentage'] = user_analysis_df.apply(
        lambda row: round((row['Count of Detection'] / month_totals.get(row['Month'], 1)) * 100, 1),
        axis=1
    )

    # Add AnalysisType and DataSource columns
    user_analysis_df['AnalysisType'] = 'Host Analysis: User Analysis'
    user_analysis_df['DataSource'] = 'Host Analysis: User Analysis'

    # Rename UserName to Username to match Excel
    user_analysis_df = user_analysis_df.rename(columns={'UserName': 'Username'})

    # Reorder columns to match Excel format
    user_analysis_df = user_analysis_df[['Username', 'Month', 'AnalysisType', 'DataSource', 'Count of Detection', 'Percentage']]

    # Sort by Username and Month
    user_analysis_df = user_analysis_df.sort_values(['Username', 'Month'])

    print(f"[Host Analysis] USER ANALYSIS generated: {len(user_analysis_df)} row(s) in LONG FORMAT for {len(top_users)} user(s)")
    return user_analysis_df


def generate_sensor_analysis(df, num_months, top_n=10):
    """
    Generate Sensor Version Analysis in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - Sensor Version: Sensor version number
    - Month: Month name
    - AnalysisType: Always "Host Analysis: Sensor Analysis"
    - DataSource: Always "Host Analysis: Sensor Analysis"
    - Host Count: Host count for this sensor version in this month
    - Percentage: Percentage of total hosts
    - Status: Latest or Outdated
    """

    # Sort versions (assuming semantic versioning like 7.23.19508.0)
    def version_key(v):
        try:
            parts = str(v).split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        except:
            return (0,)

    # Get host counts per sensor version per month
    # Count all records (detections), not unique hosts
    sensor_month_counts = df.groupby(['Sensor Version', 'Month']).size().reset_index(name='Host Count')

    # Calculate percentage per month (total detections per month)
    month_totals = df.groupby('Month').size().to_dict()
    sensor_month_counts['Percentage'] = sensor_month_counts.apply(
        lambda row: round((row['Host Count'] / month_totals.get(row['Month'], 1)) * 100, 1),
        axis=1
    )

    # Identify latest sensor version PER MONTH (not globally)
    # For each month, find the highest version number in that month
    latest_per_month = {}
    for month in sensor_month_counts['Month'].unique():
        month_versions = sensor_month_counts[sensor_month_counts['Month'] == month]['Sensor Version'].tolist()
        month_versions = [v for v in month_versions if pd.notna(v) and v != '']
        if month_versions:
            sorted_month_versions = sorted(month_versions, key=version_key, reverse=True)
            latest_per_month[month] = sorted_month_versions[0]
            print(f"[Host Analysis] Latest Sensor Version for {month}: {sorted_month_versions[0]}")

    # Add Status column based on latest version PER MONTH
    sensor_month_counts['Status'] = sensor_month_counts.apply(
        lambda row: 'Latest' if row['Sensor Version'] == latest_per_month.get(row['Month']) else 'Outdated',
        axis=1
    )

    # Add AnalysisType and DataSource columns
    sensor_month_counts['AnalysisType'] = 'Host Analysis: Sensor Analysis'
    sensor_month_counts['DataSource'] = 'Host Analysis: Sensor Analysis'

    # Keep original column name to match Excel
    sensor_analysis_df = sensor_month_counts[['Sensor Version', 'Month', 'AnalysisType', 'DataSource', 'Host Count', 'Percentage', 'Status']]

    # Sort by SensorVersion (latest first) and Month
    sensor_analysis_df['_sort_key'] = sensor_analysis_df['Sensor Version'].apply(version_key)
    sensor_analysis_df = sensor_analysis_df.sort_values(['_sort_key', 'Month'], ascending=[False, True])
    sensor_analysis_df = sensor_analysis_df.drop(columns=['_sort_key'])

    print(f"[Host Analysis] SENSOR ANALYSIS generated: {len(sensor_analysis_df)} row(s) in LONG FORMAT")
    return sensor_analysis_df


if __name__ == "__main__":
    # Test with sample data
    print("Host Analysis Generator - Test Mode")

    # Create sample data
    sample_data = pd.DataFrame({
        'UniqueNo': range(1, 21),
        'Hostname': ['HOST-A', 'HOST-B', 'HOST-C'] * 6 + ['HOST-D', 'HOST-E'],
        'UserName': ['user1', 'user2', 'user3'] * 6 + ['user4', 'user5'],
        'OS Version': ['Windows 10'] * 10 + ['Windows 11'] * 10,
        'Sensor Version': ['7.23.19508.0'] * 15 + ['7.16.18613.0'] * 5,
        'Site': ['HQ'] * 20,
        'OU': ['IT'] * 20,
        'Period': ['June 2025'] * 10 + ['July 2025'] * 10,
        'Month': ['June 2025'] * 10 + ['July 2025'] * 10
    })

    # Test
    results = generate_host_analysis(sample_data, num_months=2)

    print("\n=== KEY METRICS ===")
    print(results['overview_key_metrics'])

    print("\n=== TOP HOSTS ===")
    print(results['overview_top_hosts'])

    print("\n=== USER ANALYSIS ===")
    print(results['user_analysis'])

    print("\n=== SENSOR ANALYSIS ===")
    print(results['sensor_analysis'])
