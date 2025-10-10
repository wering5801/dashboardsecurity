"""
Detection & Severity Analysis Generator
Converts Detection Template to Analysis Results
Replicates detection & severity-dashboard-generator v3.2.html logic

Outputs:
B1. Critical and High Detection Overview
B2. Detection Count by Severity (3 Months Trend)
B3. Detection Count Across Country
B4. Files with Most Detections Across Three Months Trends - Top 5
B5. Tactics by Severity Across Three Months Trends
B6. Technique by Severity Across Three Months Trends
Raw Data: (Hostname, SeverityName, Tactic, Technique, Objective, Month)

With Month column for multi-month support
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_detection_severity_analysis(detection_template_df, num_months=1):
    """
    Generate detection & severity analysis results from template

    Parameters:
    - detection_template_df: DataFrame from falcon generator (Detection Analysis template)
    - num_months: Number of months in the dataset (1, 2, or 3)

    Returns:
    - Dictionary containing all analysis results as DataFrames
    """

    print(f"[Detection Analysis Generator] Processing {len(detection_template_df)} records for {num_months} month(s)...")

    # Ensure required columns exist
    required_cols = ['UniqueNo', 'Hostname', 'SeverityName', 'Period']

    missing_cols = [col for col in required_cols if col not in detection_template_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Clean data
    df = detection_template_df.copy()
    df = df[df['UniqueNo'].notna()]

    # Extract Month from Period if not exists
    if 'Month' not in df.columns and 'Period' in df.columns:
        df['Month'] = df['Period']

    # Fill missing values for categorical columns
    df['SeverityName'] = df['SeverityName'].fillna('Unknown')
    df['Hostname'] = df['Hostname'].fillna('Unknown')

    # Fill optional columns if they exist
    if 'Country' in df.columns:
        df['Country'] = df['Country'].fillna('Unknown')
    if 'FileName' in df.columns:
        df['FileName'] = df['FileName'].fillna('Unknown')
    if 'Tactic' in df.columns:
        df['Tactic'] = df['Tactic'].fillna('Unknown')
    if 'Technique' in df.columns:
        df['Technique'] = df['Technique'].fillna('Unknown')
    if 'Objective' in df.columns:
        df['Objective'] = df['Objective'].fillna('Unknown')

    print(f"[Detection Analysis Generator] Clean data: {len(df)} valid records")

    # Generate all analysis results
    results = {
        'critical_high_overview': generate_detection_key_metrics(df, num_months),
        'severity_trend': generate_top_severities(df, num_months),
        'country_analysis': generate_geographic_analysis(df, num_months),
        'file_analysis': generate_file_analysis(df, num_months),
        'tactics_by_severity': generate_tactics_by_severity(df, num_months),
        'technique_by_severity': generate_technique_by_severity(df, num_months),
        'raw_data_filtered': generate_raw_data_filtered(df, num_months),
        'raw_data': df  # Include full raw data for pivot table builder
    }

    print(f"[Detection Analysis Generator] ✅ Generated {len(results)} analysis outputs")

    return results


def generate_detection_key_metrics(df, num_months):
    """
    B1. Generate Critical and High Detection Overview - KEY METRICS in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - KEY METRICS: Metric name (ONLY: Total Detections, Unique Devices, Critical Detections, High Detections)
    - Month: Month name
    - Analysis: Always "Detection Analysis Overview"
    - DataSource: Always "Detection Analysis Overview"
    - Count: Metric value
    """

    long_format_rows = []

    if num_months > 1:
        # Multi-month analysis - create row for each metric × month
        for month in sorted(df['Month'].unique()):
            month_df = df[df['Month'] == month]

            total_detections = len(month_df)
            unique_devices = month_df['Hostname'].nunique()
            critical_count = len(month_df[month_df['SeverityName'].str.contains('Critical', case=False, na=False)])
            high_count = len(month_df[month_df['SeverityName'].str.contains('High', case=False, na=False)])

            # ONLY these 4 metrics as per HTML generator
            metrics = [
                ('Total Detections', total_detections),
                ('Unique Devices', unique_devices),
                ('Critical Detections', critical_count),
                ('High Detections', high_count)
            ]

            for metric_name, metric_value in metrics:
                long_format_rows.append({
                    'KEY METRICS': metric_name,
                    'Month': month,
                    'Analysis': 'Detection Analysis Overview',
                    'DataSource': 'Detection Analysis Overview',
                    'Count': metric_value
                })

    else:
        # Single month analysis
        month = df['Month'].iloc[0] if 'Month' in df.columns else 'Single Month'

        total_detections = len(df)
        unique_devices = df['Hostname'].nunique()
        critical_count = len(df[df['SeverityName'].str.contains('Critical', case=False, na=False)])
        high_count = len(df[df['SeverityName'].str.contains('High', case=False, na=False)])

        # ONLY these 4 metrics as per HTML generator
        metrics = [
            ('Total Detections', total_detections),
            ('Unique Devices', unique_devices),
            ('Critical Detections', critical_count),
            ('High Detections', high_count)
        ]

        for metric_name, metric_value in metrics:
            long_format_rows.append({
                'KEY METRICS': metric_name,
                'Month': month,
                'Analysis': 'Detection Analysis Overview',
                'DataSource': 'Detection Analysis Overview',
                'Count': metric_value
            })

    metrics_df = pd.DataFrame(long_format_rows)

    print(f"[Detection Analysis] B1 KEY METRICS generated: {len(metrics_df)} row(s) in LONG FORMAT (Total, Unique Devices, Critical, High only)")
    return metrics_df


def generate_top_severities(df, num_months, top_n=10):
    """
    Generate Overview - TOP SEVERITIES in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - SeverityName: Severity level (Critical, High, Medium, Low)
    - Month: Month name
    - Analysis: Always "Detection Analysis Overview"
    - DataSource: Always "Detection Analysis Overview"
    - Count: Detection count for this severity in this month
    """

    # Get detection counts per severity per month
    severity_month_counts = df.groupby(['SeverityName', 'Month']).size().reset_index(name='Count')

    # Add Analysis and DataSource columns
    severity_month_counts['Analysis'] = 'Detection Analysis Overview'
    severity_month_counts['DataSource'] = 'Detection Analysis Overview'

    # Reorder columns
    top_severities_df = severity_month_counts[['SeverityName', 'Month', 'Analysis', 'DataSource', 'Count']]

    # Sort by SeverityName and Month
    severity_order = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}
    top_severities_df['_sort_key'] = top_severities_df['SeverityName'].map(lambda x: severity_order.get(x, 5))
    top_severities_df = top_severities_df.sort_values(['_sort_key', 'Month'])
    top_severities_df = top_severities_df.drop(columns=['_sort_key'])

    print(f"[Detection Analysis] TOP SEVERITIES generated: {len(top_severities_df)} row(s) in LONG FORMAT")
    return top_severities_df


def generate_geographic_analysis(df, num_months, top_n=10):
    """
    Generate Geographic Analysis (by Country) in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - Country: Country name
    - Month: Month name
    - Analysis: Always "Detection Analysis Overview"
    - DataSource: Always "Detection Analysis Overview"
    - Count: Detection count for this country in this month
    """

    # Check if Country column exists
    if 'Country' not in df.columns:
        print("[Detection Analysis] GEOGRAPHIC ANALYSIS skipped - No Country column found")
        return pd.DataFrame({'Message': ['Country data not available']})

    df_geo = df[df['Country'].notna() & (df['Country'] != 'Unknown')]

    if len(df_geo) == 0:
        print("[Detection Analysis] GEOGRAPHIC ANALYSIS skipped - No country data")
        return pd.DataFrame({'Message': ['No country data available']})

    # Get detection counts per country per month
    country_month_counts = df_geo.groupby(['Country', 'Month']).size().reset_index(name='Detection Count')

    # Calculate total detections per country to identify top N
    country_totals = country_month_counts.groupby('Country')['Detection Count'].sum().reset_index(name='Total')
    top_countries = country_totals.nlargest(top_n, 'Total')['Country'].tolist()

    # Get all unique months in the dataset
    all_months = sorted(df_geo['Month'].unique())

    # Create a complete matrix: every top N country × every month
    complete_rows = []
    for country in top_countries:
        for month in all_months:
            # Check if this country-month combination exists
            existing = country_month_counts[
                (country_month_counts['Country'] == country) &
                (country_month_counts['Month'] == month)
            ]
            if len(existing) > 0:
                # Use existing count
                count = existing.iloc[0]['Detection Count']
            else:
                # Fill with 0 for missing months
                count = 0

            complete_rows.append({
                'Country': country,
                'Month': month,
                'Detection Count': count
            })

    # Create dataframe with complete matrix
    geo_analysis_df = pd.DataFrame(complete_rows)

    # Calculate percentage for each row (country-month combination)
    total_detections_per_month = geo_analysis_df.groupby('Month')['Detection Count'].sum().to_dict()
    geo_analysis_df['Percentage'] = geo_analysis_df.apply(
        lambda row: (row['Detection Count'] / total_detections_per_month[row['Month']] * 100) if total_detections_per_month[row['Month']] > 0 else 0,
        axis=1
    )
    geo_analysis_df['Percentage'] = geo_analysis_df['Percentage'].round(2)

    # Add DataSource and Geographic Analysis columns
    geo_analysis_df['DataSource'] = 'Detection_Ana Geographic Analysis'
    geo_analysis_df['Geographic Analysis'] = 'Detection_Ana Geographic Analysis'

    # Reorder columns to match required format
    geo_analysis_df = geo_analysis_df[['Country', 'Detection Count', 'Percentage', 'Month', 'DataSource', 'Geographic Analysis']]

    # Sort by Country and Month
    geo_analysis_df = geo_analysis_df.sort_values(['Country', 'Month'])

    print(f"[Detection Analysis] GEOGRAPHIC ANALYSIS generated: {len(geo_analysis_df)} row(s) in LONG FORMAT for {len(top_countries)} country/countries")
    return geo_analysis_df


def generate_file_analysis(df, num_months, top_n=10):
    """
    Generate File Analysis (Top files with most detections) in LONG FORMAT

    Output columns (Excel Pivot Table Ready):
    - FileName: File name
    - Month: Month name
    - Analysis: Always "Detection Analysis Overview"
    - DataSource: Always "Detection Analysis Overview"
    - Count: Detection count for this file in this month
    """

    # Check if FileName column exists
    if 'FileName' not in df.columns:
        print("[Detection Analysis] FILE ANALYSIS skipped - No FileName column found")
        return pd.DataFrame({'Message': ['FileName data not available']})

    df_files = df[df['FileName'].notna() & (df['FileName'] != 'Unknown') & (df['FileName'] != '')]

    if len(df_files) == 0:
        print("[Detection Analysis] FILE ANALYSIS skipped - No file data")
        return pd.DataFrame({'Message': ['No file data available']})

    # Get detection counts per file per month
    file_month_counts = df_files.groupby(['FileName', 'Month']).size().reset_index(name='Detection Count')

    # Calculate total detections per file to identify top N
    file_totals = file_month_counts.groupby('FileName')['Detection Count'].sum().reset_index(name='Total')
    top_files = file_totals.nlargest(top_n, 'Total')['FileName'].tolist()

    # Get all unique months in the dataset
    all_months = sorted(df_files['Month'].unique())

    # Create a complete matrix: every top N file × every month
    complete_rows = []
    for file_name in top_files:
        for month in all_months:
            # Check if this file-month combination exists
            existing = file_month_counts[
                (file_month_counts['FileName'] == file_name) &
                (file_month_counts['Month'] == month)
            ]
            if len(existing) > 0:
                # Use existing count
                count = existing.iloc[0]['Detection Count']
            else:
                # Fill with 0 for missing months
                count = 0

            complete_rows.append({
                'FileName': file_name,
                'Month': month,
                'Detection Count': count
            })

    # Create dataframe with complete matrix
    file_analysis_df = pd.DataFrame(complete_rows)

    # Calculate percentage for each row (file-month combination)
    total_detections_per_month = file_analysis_df.groupby('Month')['Detection Count'].sum().to_dict()
    file_analysis_df['Percentage'] = file_analysis_df.apply(
        lambda row: (row['Detection Count'] / total_detections_per_month[row['Month']] * 100) if total_detections_per_month[row['Month']] > 0 else 0,
        axis=1
    )
    file_analysis_df['Percentage'] = file_analysis_df['Percentage'].round(2)

    # Rename FileName to 'File Name' with space
    file_analysis_df = file_analysis_df.rename(columns={'FileName': 'File Name'})

    # Add DataSource and File Analysis columns
    file_analysis_df['DataSource'] = 'Detection_Ana File Analysis'
    file_analysis_df['File Analysis'] = 'Detection_Ana File Analysis'

    # Reorder columns to match required format
    file_analysis_df = file_analysis_df[['File Name', 'Detection Count', 'Percentage', 'Month', 'DataSource', 'File Analysis']]

    # Sort by File Name and Month
    file_analysis_df = file_analysis_df.sort_values(['File Name', 'Month'])

    print(f"[Detection Analysis] FILE ANALYSIS generated: {len(file_analysis_df)} row(s) in LONG FORMAT for {len(top_files)} file(s)")
    return file_analysis_df


def generate_tactics_by_severity(df, num_months):
    """
    B5. Tactics by Severity - RAW DATA FORMAT

    Output columns (Raw Data - not aggregated):
    - Hostname
    - SeverityName
    - Tactic
    - Technique
    - Objective
    - Month
    """

    # Define required fields
    required_fields = ['Hostname', 'SeverityName', 'Tactic', 'Technique', 'Objective', 'Month']

    # Check which fields exist in the dataframe
    available_fields = [f for f in required_fields if f in df.columns]

    if not available_fields:
        print("[Detection Analysis] TACTICS BY SEVERITY skipped - No required fields found")
        return pd.DataFrame({'Message': ['Required fields not available']})

    # Select only the available fields
    tactics_df = df[available_fields].copy()

    # Remove rows with missing critical data
    if 'Tactic' in tactics_df.columns:
        tactics_df = tactics_df[tactics_df['Tactic'].notna() & (tactics_df['Tactic'] != 'Unknown') & (tactics_df['Tactic'] != '')]

    if len(tactics_df) == 0:
        print("[Detection Analysis] TACTICS BY SEVERITY skipped - No valid data")
        return pd.DataFrame({'Message': ['No tactic data available']})

    # Add a Count column with value 1 for each row (for pivot table aggregation)
    tactics_df['Count'] = 1

    # Sort by Hostname, SeverityName, Month
    sort_cols = [c for c in ['Hostname', 'SeverityName', 'Month'] if c in tactics_df.columns]
    if sort_cols:
        tactics_df = tactics_df.sort_values(sort_cols)

    print(f"[Detection Analysis] TACTICS BY SEVERITY generated: {len(tactics_df)} row(s) - RAW DATA FORMAT")
    return tactics_df


def generate_technique_by_severity(df, num_months):
    """
    B6. Technique by Severity - RAW DATA FORMAT

    Output columns (Raw Data - not aggregated):
    - Hostname
    - SeverityName
    - Tactic
    - Technique
    - Objective
    - Month
    """

    # Define required fields
    required_fields = ['Hostname', 'SeverityName', 'Tactic', 'Technique', 'Objective', 'Month']

    # Check which fields exist in the dataframe
    available_fields = [f for f in required_fields if f in df.columns]

    if not available_fields:
        print("[Detection Analysis] TECHNIQUE BY SEVERITY skipped - No required fields found")
        return pd.DataFrame({'Message': ['Required fields not available']})

    # Select only the available fields
    tech_df = df[available_fields].copy()

    # Remove rows with missing critical data
    if 'Technique' in tech_df.columns:
        tech_df = tech_df[tech_df['Technique'].notna() & (tech_df['Technique'] != 'Unknown') & (tech_df['Technique'] != '')]

    if len(tech_df) == 0:
        print("[Detection Analysis] TECHNIQUE BY SEVERITY skipped - No valid data")
        return pd.DataFrame({'Message': ['No technique data available']})

    # Add a Count column with value 1 for each row (for pivot table aggregation)
    tech_df['Count'] = 1

    # Sort by Hostname, SeverityName, Month
    sort_cols = [c for c in ['Hostname', 'SeverityName', 'Month'] if c in tech_df.columns]
    if sort_cols:
        tech_df = tech_df.sort_values(sort_cols)

    print(f"[Detection Analysis] TECHNIQUE BY SEVERITY generated: {len(tech_df)} row(s) - RAW DATA FORMAT")
    return tech_df


def generate_raw_data_filtered(df, num_months):
    """
    Generate Raw Data with specific fields:
    - Hostname
    - SeverityName
    - Tactic
    - Technique
    - Objective
    - Month (if multi-month)

    This is the filtered raw data for pivot table builder
    """

    # Define columns to include
    required_fields = ['Hostname', 'SeverityName']
    optional_fields = ['Tactic', 'Technique', 'Objective']

    # Check which optional fields exist
    available_fields = required_fields.copy()
    for field in optional_fields:
        if field in df.columns:
            available_fields.append(field)

    # Add Month if multi-month
    if num_months > 1 and 'Month' in df.columns:
        available_fields.append('Month')

    # Create filtered dataframe
    raw_data_filtered = df[available_fields].copy()

    # Add a Count column with value 1 for each row (for pivot table aggregation)
    raw_data_filtered['Count'] = 1

    print(f"[Detection Analysis] RAW DATA FILTERED generated: {len(raw_data_filtered)} records with {len(available_fields)} fields")

    return raw_data_filtered


if __name__ == "__main__":
    # Test with sample data
    print("Detection & Severity Analysis Generator - Test Mode")

    # Create sample data
    sample_data = pd.DataFrame({
        'UniqueNo': range(1, 31),
        'Hostname': ['HOST-A', 'HOST-B', 'HOST-C'] * 10,
        'SeverityName': ['Critical', 'High', 'Medium', 'Low'] * 7 + ['Critical', 'High', 'Medium'],
        'Tactic': ['Initial Access', 'Execution', 'Persistence'] * 10,
        'Technique': ['T1566', 'T1059', 'T1547'] * 10,
        'Objective': ['Malware', 'Exploit', 'Backdoor'] * 10,
        'Country': ['Malaysia', 'Singapore', 'Thailand'] * 10,
        'FileName': ['file1.exe', 'file2.dll', 'file3.sys'] * 10,
        'Period': ['June 2025'] * 15 + ['July 2025'] * 15,
        'Month': ['June 2025'] * 15 + ['July 2025'] * 15
    })

    # Test
    results = generate_detection_severity_analysis(sample_data, num_months=2)

    print("\n=== KEY METRICS ===")
    print(results['overview_key_metrics'])

    print("\n=== TOP SEVERITIES ===")
    print(results['overview_top_severities'])

    print("\n=== GEOGRAPHIC ANALYSIS ===")
    print(results['geographic_analysis'])

    print("\n=== FILE ANALYSIS ===")
    print(results['file_analysis'])

    print("\n=== RAW DATA FILTERED ===")
    print(results['raw_data_filtered'].head(10))
