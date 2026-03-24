"""
Sensor Offline Analysis Module
Parses Falcon CSV host export to identify servers with offline sensors
Groups by Last Seen date to show monthly offline count and breakdown

CSV Format: Falcon Host Export (from Hosts page)
Required columns: Hostname, Last Seen
Optional (auto-detected): Platform, OS Version, Type, Site, Host Groups, Last Logged In User Account

Developed by Izami Ariff © 2025
"""

import pandas as pd
from datetime import datetime
from typing import Dict
import io


def parse_sensor_offline_csv(file_obj) -> pd.DataFrame:
    """
    Parse Falcon sensor CSV export into a DataFrame.

    Args:
        file_obj: File-like object (Streamlit UploadedFile or path)

    Returns:
        DataFrame with parsed and enriched data
    """
    try:
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            df = pd.read_csv(io.StringIO(content))
        else:
            df = pd.read_csv(file_obj)

        required_columns = ['Hostname', 'Last Seen']
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        # Parse Last Seen datetime
        df['Last Seen'] = pd.to_datetime(df['Last Seen'], errors='coerce')
        df = df.dropna(subset=['Last Seen'])

        # Time grouping fields
        df['Month Name'] = df['Last Seen'].dt.strftime('%B %Y')
        df['Month'] = df['Last Seen'].dt.to_period('M').astype(str)
        df['Year'] = df['Last Seen'].dt.year

        # Fill optional columns
        for col in ['Platform', 'OS Version', 'Type', 'Site', 'Host Groups', 'Last Logged In User Account']:
            if col not in df.columns:
                df[col] = 'Unknown'
            else:
                df[col] = df[col].fillna('Unknown').astype(str).str.strip()

        df = df.sort_values('Last Seen', ascending=False).reset_index(drop=True)
        return df

    except Exception as e:
        raise ValueError(f"Error parsing sensor offline CSV: {str(e)}")


def generate_sensor_offline_analysis(df: pd.DataFrame) -> Dict:
    """
    Generate sensor offline analysis results from parsed DataFrame.

    Args:
        df: DataFrame from parse_sensor_offline_csv()

    Returns:
        Dictionary of analysis results
    """
    results = {}
    if df.empty:
        return results

    # Overview stats
    results['overview'] = {
        'total_offline': len(df),
        'unique_platforms': df['Platform'].nunique(),
        'unique_os': df['OS Version'].nunique(),
        'date_range': {
            'start': df['Last Seen'].min(),
            'end': df['Last Seen'].max()
        }
    }

    # Monthly offline count — exposed to Pivot Table Builder
    offline_monthly_counts = df.groupby('Month Name').size().reset_index(name='Count')
    results['offline_monthly_counts'] = offline_monthly_counts

    # Platform breakdown
    platform_counts = df.groupby('Platform').size().reset_index(name='Count')
    platform_counts = platform_counts.sort_values('Count', ascending=False)
    results['platform_counts'] = platform_counts

    # OS Version breakdown (top 10)
    os_counts = df.groupby('OS Version').size().reset_index(name='Count')
    os_counts = os_counts.sort_values('Count', ascending=False).head(10)
    results['os_counts'] = os_counts

    # Raw data for detailed display
    results['raw_data'] = df

    return results


def validate_sensor_offline_csv(df: pd.DataFrame) -> Dict:
    """
    Validate that the uploaded CSV DataFrame has required columns.

    Args:
        df: DataFrame to validate

    Returns:
        Validation result dict
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'record_count': len(df)
    }
    required = ['Hostname', 'Last Seen']
    missing = [c for c in required if c not in df.columns]
    if missing:
        result['is_valid'] = False
        result['errors'].append(f"Missing required columns: {', '.join(missing)}")
    if result['is_valid'] and len(df) == 0:
        result['warnings'].append("CSV has no data rows")
    return result
