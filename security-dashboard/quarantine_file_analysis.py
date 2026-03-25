"""
Quarantined File Analysis Module
Parses Falcon JSON data to analyze quarantined files
Shows monthly count and summary of affected files/hosts

JSON Format Required:
- Date of Quarantine: Timestamp (e.g., "2026-02-12T07:12:55Z")
- File Name: Name of quarantined file
- Hostname: Affected host
- Agent ID: Falcon agent identifier
- User: Username
- Status: Quarantine status

Developed by Izami Ariff © 2025
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List
import numpy as np

def parse_quarantine_json(json_data: str or dict or list) -> pd.DataFrame:
    """
    Parse Falcon quarantine JSON data into a DataFrame

    Args:
        json_data: JSON string, dict, or list containing quarantine data

    Returns:
        DataFrame with parsed quarantine data
    """
    try:
        # Handle different input types
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Ensure data is a list
        if isinstance(data, dict):
            # If it's a single object, wrap in list
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("JSON data must be a list or dictionary")

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Validate required columns
        required_columns = ['Date of Quarantine', 'File Name', 'Hostname', 'Status']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # User is optional — fill with empty string if not present
        if 'User' not in df.columns:
            df['User'] = ''
        else:
            df['User'] = df['User'].fillna('')

        # Parse date
        df['Date of Quarantine'] = pd.to_datetime(df['Date of Quarantine'], errors='coerce')

        # Extract month and year for grouping
        df['Month'] = df['Date of Quarantine'].dt.to_period('M').astype(str)
        df['Year'] = df['Date of Quarantine'].dt.year
        df['Month Name'] = df['Date of Quarantine'].dt.strftime('%B %Y')
        df['Date Only'] = df['Date of Quarantine'].dt.date

        # Sort by date
        df = df.sort_values('Date of Quarantine', ascending=False)

        return df

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing quarantine data: {str(e)}")


def generate_quarantine_analysis(df: pd.DataFrame) -> Dict:
    """
    Generate quarantine file analysis from parsed DataFrame

    Args:
        df: DataFrame with parsed quarantine data

    Returns:
        Dictionary containing analysis results
    """
    results = {}

    if df.empty:
        return results

    # 1. Overall Statistics
    total_quarantined = len(df)
    unique_files = df['File Name'].nunique()
    unique_hosts = df['Hostname'].nunique()
    unique_users = df['User'].replace('', pd.NA).dropna().nunique()

    results['overview'] = {
        'total_quarantined': total_quarantined,
        'unique_files': unique_files,
        'unique_hosts': unique_hosts,
        'unique_users': unique_users,
        'date_range': {
            'start': df['Date of Quarantine'].min(),
            'end': df['Date of Quarantine'].max()
        }
    }

    # 2. Monthly Count (for bar chart)
    monthly_counts = df.groupby('Month Name').size().reset_index(name='Count')
    monthly_counts = monthly_counts.sort_values('Month Name')
    results['monthly_counts'] = monthly_counts

    # 3. File Summary - Most quarantined files
    file_summary = df.groupby('File Name').agg({
        'Hostname': 'nunique',
        'User': 'nunique',
        'Date of Quarantine': 'count'
    }).reset_index()
    file_summary.columns = ['File Name', 'Affected Hosts', 'Affected Users', 'Quarantine Count']
    file_summary = file_summary.sort_values('Quarantine Count', ascending=False)
    results['file_summary'] = file_summary

    # 4. Host Summary - Most affected hosts
    host_summary = df.groupby('Hostname').agg({
        'File Name': 'nunique',
        'User': lambda x: x[x != ''].mode()[0] if not x[x != ''].empty else 'N/A',
        'Date of Quarantine': 'count'
    }).reset_index()
    host_summary.columns = ['Hostname', 'Unique Files', 'Primary User', 'Total Quarantines']
    host_summary = host_summary.sort_values('Total Quarantines', ascending=False)
    results['host_summary'] = host_summary

    # 5. Status Distribution
    status_counts = df.groupby('Status').size().reset_index(name='Count')
    status_counts = status_counts.sort_values('Count', ascending=False)
    results['status_distribution'] = status_counts

    # 6. Daily Trend
    daily_counts = df.groupby('Date Only').size().reset_index(name='Count')
    daily_counts = daily_counts.sort_values('Date Only')
    results['daily_trend'] = daily_counts

    # 7. Top 10 Most Quarantined Files with Details
    top_files = file_summary.head(10).copy()

    # Get detailed info for top files
    detailed_files = []
    for file_name in top_files['File Name']:
        file_df = df[df['File Name'] == file_name]
        hosts_affected = ', '.join(file_df['Hostname'].unique()[:5])  # Show first 5 hosts
        if file_df['Hostname'].nunique() > 5:
            hosts_affected += f" (+{file_df['Hostname'].nunique() - 5} more)"

        detailed_files.append({
            'File Name': file_name,
            'Quarantine Count': len(file_df),
            'Affected Hosts': file_df['Hostname'].nunique(),
            'Hosts List': hosts_affected,
            'First Seen': file_df['Date of Quarantine'].min().strftime('%d/%m/%Y %H:%M'),
            'Last Seen': file_df['Date of Quarantine'].max().strftime('%d/%m/%Y %H:%M')
        })

    results['detailed_file_summary'] = pd.DataFrame(detailed_files)

    # 8. Top 10 Most Affected Hosts with Details
    top_hosts = host_summary.head(10).copy()

    # Get detailed info for top hosts
    detailed_hosts = []
    for hostname in top_hosts['Hostname']:
        host_df = df[df['Hostname'] == hostname]
        files_quarantined = ', '.join(host_df['File Name'].unique()[:3])  # Show first 3 files
        if host_df['File Name'].nunique() > 3:
            files_quarantined += f" (+{host_df['File Name'].nunique() - 3} more)"

        detailed_hosts.append({
            'Hostname': hostname,
            'Total Quarantines': len(host_df),
            'Unique Files': host_df['File Name'].nunique(),
            'Primary User': host_df['User'][host_df['User'] != ''].mode()[0] if not host_df['User'][host_df['User'] != ''].empty else 'N/A',
            'Files': files_quarantined,
            'Last Activity': host_df['Date of Quarantine'].max().strftime('%d/%m/%Y %H:%M')
        })

    results['detailed_host_summary'] = pd.DataFrame(detailed_hosts)

    # 9. Store raw data for export
    results['raw_data'] = df

    return results


def create_sample_quarantine_json(num_records: int = 20) -> List[Dict]:
    """
    Create sample quarantine JSON data for testing

    Args:
        num_records: Number of sample records to create

    Returns:
        List of dictionaries with sample quarantine data
    """
    import random
    from datetime import timedelta

    sample_files = [
        'play1.exe', 'webcampro.exe', 'ZIPX.exe', 'svhost.exe',
        'malware.exe', 'trojan.dll', 'ransomware.exe', 'keylogger.exe',
        'cryptominer.exe', 'backdoor.exe', 'spyware.dll', 'rootkit.sys'
    ]

    sample_hosts = [
        'izami pc', 'fredo laptop', 'Rahul PC1', 'Bin Bong Mac',
        'DESKTOP-ABC123', 'LAPTOP-XYZ789', 'WORKSTATION-001', 'SERVER-DMZ'
    ]

    sample_users = [
        'ariff', 'fredos', 'Rahuls', 'Bin Bongs',
        'admin', 'john.doe', 'jane.smith', 'security_team'
    ]

    sample_statuses = ['quarantined', 'purged', 'pending']

    base_date = datetime.now()
    sample_data = []

    for i in range(num_records):
        # Generate random date within last 60 days
        days_ago = random.randint(0, 60)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        quarantine_date = base_date - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        record = {
            'Date of Quarantine': quarantine_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'File Name': random.choice(sample_files),
            'Hostname': random.choice(sample_hosts),
            'Agent ID': f"{random.choice(['d26758', 'fddf453', 'ge2430', '386562'])}{random.randint(100, 999)}",
            'User': random.choice(sample_users),
            'Status': random.choice(sample_statuses)
        }

        sample_data.append(record)

    return sample_data


def validate_quarantine_json(json_data: str or dict or list) -> Dict[str, any]:
    """
    Validate quarantine JSON data structure

    Args:
        json_data: JSON string, dict, or list to validate

    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'record_count': 0
    }

    try:
        # Parse JSON
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Check if data is list
        if not isinstance(data, list):
            if isinstance(data, dict):
                data = [data]
                validation_result['warnings'].append("JSON is a single object, wrapped in list for processing")
            else:
                validation_result['is_valid'] = False
                validation_result['errors'].append("JSON must be a list or dictionary")
                return validation_result

        validation_result['record_count'] = len(data)

        if len(data) == 0:
            validation_result['warnings'].append("JSON array is empty")
            return validation_result

        # Check required fields in first record
        required_fields = ['Date of Quarantine', 'File Name', 'Hostname', 'Status']
        first_record = data[0]

        missing_fields = [field for field in required_fields if field not in first_record]
        if missing_fields:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Missing required fields: {', '.join(missing_fields)}")

        # Check date format
        try:
            datetime.fromisoformat(first_record['Date of Quarantine'].replace('Z', '+00:00'))
        except:
            validation_result['warnings'].append("Date format may not be ISO format, will attempt flexible parsing")

    except json.JSONDecodeError as e:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"Validation error: {str(e)}")

    return validation_result
