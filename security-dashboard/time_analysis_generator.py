"""
Time-Based Analysis Generator
Converts Time Analysis Template to Analysis Results
Replicates time-based-analysis-dashboard-generator v3.0.html logic

Outputs:
1. Daily Trends
2. Hourly Analysis
3. Day of Week

With Month column for multi-month support
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_time_analysis(time_template_df, num_months=1):
    """
    Generate time-based analysis results from template

    Parameters:
    - time_template_df: DataFrame from falcon generator (Time Analysis template)
    - num_months: Number of months in the dataset (1, 2, or 3)

    Returns:
    - Dictionary containing all analysis results as DataFrames
    """

    print(f"[Time Analysis Generator] Processing {len(time_template_df)} records for {num_months} month(s)...")
    print(f"[Time Analysis Generator] Columns in data: {time_template_df.columns.tolist()}")

    # Check if Period column exists (this is the user-selected month)
    has_period = 'Period' in time_template_df.columns
    if has_period:
        unique_periods = time_template_df['Period'].unique().tolist()
        print(f"[Time Analysis Generator] Unique Periods in raw data: {unique_periods}")

    # Check for timestamp column (can have different names)
    timestamp_col = None
    possible_timestamp_cols = ['Detect MALAYSIA TIME FORMULA', 'Detect MALAYSIA TIME', 'DetectionTime', 'Timestamp']

    for col in possible_timestamp_cols:
        if col in time_template_df.columns:
            timestamp_col = col
            break

    if timestamp_col is None:
        raise ValueError(f"No timestamp column found. Expected one of: {possible_timestamp_cols}")

    print(f"[Time Analysis Generator] Using timestamp column: {timestamp_col}")

    # Clean data - use .copy() to avoid SettingWithCopyWarning
    df = time_template_df.copy()

    # Debug: Show records before filtering
    print(f"[Time Analysis Generator] Total records before filtering: {len(df)}")
    if has_period:
        for period in df['Period'].unique():
            count = len(df[df['Period'] == period])
            print(f"[Time Analysis Generator]   - {period}: {count} records")

    df = df[df['UniqueNo'].notna()].copy()
    print(f"[Time Analysis Generator] Records after UniqueNo filter: {len(df)}")

    # Check timestamp column for empty/null values per period
    if has_period:
        for period in df['Period'].unique():
            period_df = df[df['Period'] == period]
            non_null_timestamps = period_df[timestamp_col].notna().sum()
            null_timestamps = period_df[timestamp_col].isna().sum()
            empty_timestamps = (period_df[timestamp_col] == '').sum()
            print(f"[Time Analysis Generator]   - {period}: {non_null_timestamps} valid, {null_timestamps} null, {empty_timestamps} empty timestamps")

    df = df[df[timestamp_col].notna()].copy()
    df = df[df[timestamp_col] != ''].copy()  # Also filter empty strings
    print(f"[Time Analysis Generator] Records after timestamp filter: {len(df)}")

    # Debug: Show sample timestamps BEFORE parsing
    print(f"[Time Analysis Generator] Sample raw timestamps (first 10):")
    print(df[timestamp_col].head(10).tolist())

    # Parse datetime from timestamp column
    # Support multiple formats:
    # - "2025/08/10 09:12:52 PM" (YYYY/MM/DD HH:MM:SS AM/PM)
    # - "31/07/2025 01:31:09 AM" (DD/MM/YYYY HH:MM:SS AM/PM)
    # - "21/01/2026 05:16:40 PM" (DD/MM/YYYY HH:MM:SS AM/PM)

    print(f"[Time Analysis Generator] Parsing timestamps with MIXED format support...")
    print(f"[Time Analysis Generator] Sample timestamps to parse: {df[timestamp_col].head(3).tolist()}")

    # Initialize ParsedDateTime column
    df['ParsedDateTime'] = pd.NaT

    # Try multiple date formats in order of preference
    date_formats = [
        '%Y/%m/%d %I:%M:%S %p',   # 2025/08/10 09:12:52 PM
        '%d/%m/%Y %I:%M:%S %p',   # 31/07/2025 01:31:09 AM or 21/01/2026 05:16:40 PM
        '%Y-%m-%d %H:%M:%S',      # 2025-08-10 09:12:52 (24-hour)
        '%d-%m-%Y %H:%M:%S',      # 10-08-2025 09:12:52 (24-hour)
        '%Y/%m/%d %H:%M:%S',      # 2025/08/10 09:12:52 (24-hour)
        '%d/%m/%Y %H:%M:%S',      # 31/07/2025 09:12:52 (24-hour)
    ]

    for fmt in date_formats:
        failed_mask = df['ParsedDateTime'].isna()
        if not failed_mask.any():
            break  # All parsed successfully

        failed_count = failed_mask.sum()
        print(f"[Time Analysis Generator] Trying format '{fmt}' for {failed_count} unparsed records...")

        df.loc[failed_mask, 'ParsedDateTime'] = pd.to_datetime(
            df.loc[failed_mask, timestamp_col],
            errors='coerce',
            format=fmt
        )

        newly_parsed = failed_count - df['ParsedDateTime'].isna().sum()
        if newly_parsed > 0:
            print(f"[Time Analysis Generator] Successfully parsed {newly_parsed} records with format '{fmt}'")

    # For any remaining failures, try flexible parsing with dayfirst=True
    still_failed_mask = df['ParsedDateTime'].isna()
    still_failed_count = still_failed_mask.sum()

    if still_failed_count > 0:
        print(f"[Time Analysis Generator] {still_failed_count} records still failed, trying flexible parsing (dayfirst=True)...")
        df.loc[still_failed_mask, 'ParsedDateTime'] = pd.to_datetime(
            df.loc[still_failed_mask, timestamp_col],
            errors='coerce',
            dayfirst=True
        )

    # Final fallback: try without dayfirst
    final_failed_mask = df['ParsedDateTime'].isna()
    final_failed_count = final_failed_mask.sum()

    if final_failed_count > 0:
        print(f"[Time Analysis Generator] {final_failed_count} records still failed, trying flexible parsing (dayfirst=False)...")
        df.loc[final_failed_mask, 'ParsedDateTime'] = pd.to_datetime(
            df.loc[final_failed_mask, timestamp_col],
            errors='coerce',
            dayfirst=False
        )

    # Debug: Check final failure count
    final_null_count = df['ParsedDateTime'].isna().sum()
    if final_null_count > 0:
        print(f"[Time Analysis Generator] WARNING: {final_null_count} records failed ALL parsing attempts")
        failed_samples = df[df['ParsedDateTime'].isna()][timestamp_col].head(5).tolist()
        print(f"[Time Analysis Generator] Sample failed timestamps: {failed_samples}")

        # FALLBACK: Use Period column for failed records if available
        if 'Period' in df.columns:
            failed_mask = df['ParsedDateTime'].isna()
            print(f"[Time Analysis Generator] Using Period column as fallback for {failed_mask.sum()} records...")

            # For failed records, create a dummy datetime from Period (first day of month)
            for idx in df[failed_mask].index:
                period = df.loc[idx, 'Period']
                if pd.notna(period):
                    try:
                        # Parse "January 2026" format
                        dummy_date = pd.to_datetime(f"1 {period}", format='%d %B %Y')
                        df.loc[idx, 'ParsedDateTime'] = dummy_date
                    except:
                        pass

            recovered = failed_mask.sum() - df['ParsedDateTime'].isna().sum()
            print(f"[Time Analysis Generator] Recovered {recovered} records using Period fallback")
    else:
        print(f"[Time Analysis Generator] SUCCESS: All {len(df)} timestamps parsed successfully!")

    # Show unique months detected BEFORE filtering
    df_temp = df[df['ParsedDateTime'].notna()].copy()
    df_temp['_TempMonth'] = df_temp['ParsedDateTime'].dt.strftime('%B %Y')
    print(f"[Time Analysis Generator] Unique months from parsed timestamps: {df_temp['_TempMonth'].unique().tolist()}")

    # Remove rows with invalid dates
    df = df[df['ParsedDateTime'].notna()]

    # Debug: Show sample PARSED dates
    print(f"[Time Analysis Generator] Sample parsed dates (first 10):")
    print(df['ParsedDateTime'].head(10).tolist())

    # Extract time components
    df['Date'] = df['ParsedDateTime'].dt.date
    df['Hour'] = df['ParsedDateTime'].dt.hour
    df['DayOfWeek'] = df['ParsedDateTime'].dt.day_name()
    df['DayOfWeekNum'] = df['ParsedDateTime'].dt.dayofweek  # 0=Monday, 6=Sunday

    # Extract Month from ParsedDateTime (format: "June 2025", "July 2025", etc.)
    df['Month'] = df['ParsedDateTime'].dt.strftime('%B %Y')

    # Debug: Show unique months detected
    unique_months_detected = df['Month'].unique()
    print(f"[Time Analysis Generator] Clean data: {len(df)} valid records with parsed timestamps")
    print(f"[Time Analysis Generator] Unique months detected from timestamps: {list(unique_months_detected)}")

    # Generate all analysis results
    results = {
        'daily_trends': generate_daily_trends(df, num_months),
        'hourly_analysis': generate_hourly_analysis(df, num_months),
        'day_of_week': generate_day_of_week_analysis(df, num_months),
        'raw_data': df  # Include raw data for pivot table builder
    }

    print(f"[Time Analysis Generator] Generated {len(results)} analysis outputs")

    return results


def generate_daily_trends(df, num_months):
    """
    Generate Daily Trends in LONG FORMAT

    SOP Field Names (C.1 Daily Trend Analysis):
    - Date: Date in readable format
    - Detection Count: Number of detections on this date
    - Cumulative: Running total of detections (per month)
    - Month: Month name (Edit Notes to Month)
    """

    # Group by Date and Month
    daily_counts = df.groupby(['Date', 'Month']).size().reset_index(name='Detection Count')

    # Add temporary column for date sorting and month sorting
    daily_counts['_DateSort'] = pd.to_datetime(daily_counts['Date'])

    # Create month sort order (January 2025 = 0, February 2025 = 1, etc.)
    month_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                   'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    def get_month_sort_key(month_str):
        # Extract month name and year from "July 2025" format
        parts = month_str.split()
        if len(parts) == 2:
            month_name, year = parts
            return int(year) * 100 + month_order.get(month_name, 99)
        return 999999

    daily_counts['_MonthSort'] = daily_counts['Month'].apply(get_month_sort_key)

    # IMPORTANT SORTING ORDER for Daily Trends:
    # 1. Month (chronological: June -> July -> August)
    # 2. Detection Count (descending: Highest -> Lowest within each month)
    # 3. Date (chronological as tiebreaker)
    daily_counts = daily_counts.sort_values(['_MonthSort', 'Detection Count', '_DateSort'],
                                           ascending=[True, False, True])

    # Calculate Cumulative sum PER MONTH (in chronological date order)
    # Need to re-sort by date within each month for cumulative calculation
    temp_df = daily_counts.copy()
    temp_df = temp_df.sort_values(['_MonthSort', '_DateSort'])
    temp_df['Cumulative'] = temp_df.groupby('Month')['Detection Count'].cumsum()

    # Merge cumulative back to the Detection Count sorted dataframe
    daily_counts = daily_counts.merge(
        temp_df[['Date', 'Month', 'Cumulative']],
        on=['Date', 'Month'],
        how='left'
    )

    # Format Date as string (e.g., "Tue Jun 03 2025")
    daily_counts['Date'] = daily_counts['_DateSort'].dt.strftime('%a %b %d %Y')

    # Drop temporary sorting columns
    daily_counts = daily_counts.drop(columns=['_DateSort', '_MonthSort'])

    # Reorder columns: Date, Detection Count, Cumulative, Month
    daily_counts = daily_counts[['Date', 'Detection Count', 'Cumulative', 'Month']]

    print(f"[Time Analysis] DAILY TRENDS generated: {len(daily_counts)} row(s) - Fields: Date, Detection Count, Cumulative, Month")
    print(f"[Time Analysis] Sorted by: Month (chronological) -> Detection Count (highest first) -> Date")
    return daily_counts


def generate_hourly_analysis(df, num_months):
    """
    Generate Hourly Analysis (24-hour breakdown) in LONG FORMAT

    SOP Field Names (C.2 Hourly Analysis):
    - Hour: Hour in HH:00 format (0:00 to 23:00)
    - Detection Count: Number of detections in this hour
    - Percentage: Percentage of total detections (per month)
    - Period: Business Hours / Non-Business Hours
    - Sort: Numeric sorting (1-24 for hours 0:00-23:00)
    - Month: Month name (for multi-month support)

    IMPORTANT: Shows ALL 24 hours (0:00 to 23:00) even if Detection Count = 0
    """

    # Get all unique months in the data
    unique_months = df['Month'].unique()

    # Create a complete template with ALL 24 hours for EACH month
    all_hours = list(range(0, 24))  # 0 to 23
    template_data = []

    for month in unique_months:
        for hour in all_hours:
            template_data.append({
                'Hour_Num': hour,
                'Month': month
            })

    # Create template dataframe with all hour-month combinations
    template_df = pd.DataFrame(template_data)

    # Group actual data by Hour and Month
    hourly_counts = df.groupby(['Hour', 'Month']).size().reset_index(name='Detection Count')
    hourly_counts = hourly_counts.rename(columns={'Hour': 'Hour_Num'})

    # Merge template with actual data (left join to keep all 24 hours)
    hourly_complete = template_df.merge(hourly_counts, on=['Hour_Num', 'Month'], how='left')

    # Fill missing detection counts with 0
    hourly_complete['Detection Count'] = hourly_complete['Detection Count'].fillna(0).astype(int)

    # Calculate percentage PER MONTH
    total_per_month = hourly_complete.groupby('Month')['Detection Count'].transform('sum')
    hourly_complete['Percentage'] = (hourly_complete['Detection Count'] / total_per_month * 100).round(1)
    hourly_complete['Percentage'] = hourly_complete['Percentage'].astype(str) + '%'

    # Add Period column (Business Hours: 8:00-17:59, Non-Business Hours: 18:00-7:59)
    def classify_period(hour):
        if 8 <= hour < 18:
            return 'Business Hours'
        else:
            return 'Non-Business Hours'

    hourly_complete['Period'] = hourly_complete['Hour_Num'].apply(classify_period)

    # Add Sort column (1-24 for ordering: 0:00=1, 1:00=2, ..., 23:00=24)
    hourly_complete['Sort'] = hourly_complete['Hour_Num'] + 1

    # Format Hour as HH:00 format (e.g., "0:00", "1:00", "23:00")
    hourly_complete['Hour'] = hourly_complete['Hour_Num'].apply(lambda h: f"{h}:00")

    # Create month sort order
    month_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                   'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    def get_month_sort_key(month_str):
        parts = month_str.split()
        if len(parts) == 2:
            month_name, year = parts
            return int(year) * 100 + month_order.get(month_name, 99)
        return 999999

    hourly_complete['_MonthSort'] = hourly_complete['Month'].apply(get_month_sort_key)

    # IMPORTANT SORTING ORDER for Hourly Analysis:
    # 1st: Month (chronological: June -> July -> August)
    # 2nd: Sort/Hour (chronological: 0:00 -> 23:00)
    hourly_complete = hourly_complete.sort_values(['_MonthSort', 'Sort'])

    # Drop temporary columns
    hourly_complete = hourly_complete.drop(columns=['_MonthSort', 'Hour_Num'])

    # Reorder columns: Hour, Detection Count, Percentage, Period, Sort, Month
    hourly_complete = hourly_complete[['Hour', 'Detection Count', 'Percentage', 'Period', 'Sort', 'Month']]

    print(f"[Time Analysis] HOURLY ANALYSIS generated: {len(hourly_complete)} row(s) - Fields: Hour, Detection Count, Percentage, Period, Sort, Month")
    print(f"[Time Analysis] ALL 24 hours (0:00 -> 23:00) included for each month, even with 0 detections")
    print(f"[Time Analysis] Sorted by: Month (chronological) -> Hour (0:00 -> 23:00)")
    return hourly_complete


def generate_day_of_week_analysis(df, num_months):
    """
    Generate Day of Week Analysis in LONG FORMAT

    SOP Field Names (C.3 Day of Week Analysis):
    - Day: Day name (Monday, Tuesday, ..., Sunday)
    - Detection Count: Number of detections on this day of week
    - Percentage: Percentage of total detections (per month)
    - Type: Weekday / Weekend
    - Sort: Numeric sorting (1-7 for Monday-Sunday)
    - Month: Month name (for multi-month support)

    IMPORTANT: Shows ALL 7 days (Monday-Sunday) even if Detection Count = 0
    """

    # Define day order for sorting (Monday = 1, Sunday = 7)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_sort_map = {day: idx + 1 for idx, day in enumerate(day_order)}

    # Get all unique months in the data
    unique_months = df['Month'].unique()

    # Create a complete template with ALL 7 days for EACH month
    template_data = []
    for month in unique_months:
        for day in day_order:
            template_data.append({
                'DayOfWeek': day,
                'Month': month
            })

    # Create template dataframe with all day-month combinations
    template_df = pd.DataFrame(template_data)

    # Group actual data by DayOfWeek and Month
    dow_counts = df.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Detection Count')

    # Merge template with actual data (left join to keep all 7 days)
    dow_complete = template_df.merge(dow_counts, on=['DayOfWeek', 'Month'], how='left')

    # Fill missing detection counts with 0
    dow_complete['Detection Count'] = dow_complete['Detection Count'].fillna(0).astype(int)

    # Calculate percentage PER MONTH
    total_per_month = dow_complete.groupby('Month')['Detection Count'].transform('sum')
    # Avoid division by zero
    dow_complete['Percentage'] = dow_complete.apply(
        lambda row: 0.0 if total_per_month[row.name] == 0 else (row['Detection Count'] / total_per_month[row.name] * 100),
        axis=1
    ).round(1)
    dow_complete['Percentage'] = dow_complete['Percentage'].astype(str) + '%'

    # Add Type column (Weekday / Weekend)
    def classify_type(day):
        if day in ['Saturday', 'Sunday']:
            return 'Weekend'
        else:
            return 'Weekday'

    dow_complete['Type'] = dow_complete['DayOfWeek'].apply(classify_type)

    # Add Sort column (Monday=1, Tuesday=2, ..., Sunday=7)
    dow_complete['Sort'] = dow_complete['DayOfWeek'].map(day_sort_map)

    # Rename DayOfWeek to Day
    dow_complete = dow_complete.rename(columns={'DayOfWeek': 'Day'})

    # Create month sort order
    month_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                   'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    def get_month_sort_key(month_str):
        parts = month_str.split()
        if len(parts) == 2:
            month_name, year = parts
            return int(year) * 100 + month_order.get(month_name, 99)
        return 999999

    dow_complete['_MonthSort'] = dow_complete['Month'].apply(get_month_sort_key)

    # IMPORTANT SORTING ORDER for Day of Week Analysis:
    # 1st: Month (chronological: June -> July -> August)
    # 2nd: Day (Monday -> Sunday using Sort column)
    dow_complete = dow_complete.sort_values(['_MonthSort', 'Sort'])

    # Drop temporary sort column
    dow_complete = dow_complete.drop(columns=['_MonthSort'])

    # Reorder columns: Day, Detection Count, Percentage, Type, Sort, Month
    dow_complete = dow_complete[['Day', 'Detection Count', 'Percentage', 'Type', 'Sort', 'Month']]

    print(f"[Time Analysis] DAY OF WEEK ANALYSIS generated: {len(dow_complete)} row(s) - Fields: Day, Detection Count, Percentage, Type, Sort, Month")
    print(f"[Time Analysis] ALL 7 days (Monday -> Sunday) included for each month, even with 0 detections")
    print(f"[Time Analysis] Sorted by: Month (chronological) -> Day (Monday -> Sunday)")
    return dow_complete


if __name__ == "__main__":
    # Test with sample data
    print("Time-Based Analysis Generator - Test Mode")

    # Create sample data with timestamps
    dates = pd.date_range('2025-06-01', periods=30, freq='D')
    hours = [8, 9, 10, 14, 15, 16, 17, 18, 20, 21] * 3

    sample_data = pd.DataFrame({
        'UniqueNo': range(1, 31),
        'Hostname': ['HOST-A', 'HOST-B', 'HOST-C'] * 10,
        'Detect MALAYSIA TIME FORMULA': [
            f"{d.strftime('%d/%m/%Y')} {h:02d}:{m:02d}"
            for d, h, m in zip(dates, hours, [0, 15, 30, 45, 0, 15, 30, 45, 0, 15] * 3)
        ],
        'Period': ['June 2025'] * 15 + ['July 2025'] * 15,
        'Month': ['June 2025'] * 15 + ['July 2025'] * 15
    })

    # Test
    results = generate_time_analysis(sample_data, num_months=2)

    print("\n=== DAILY TRENDS ===")
    print(results['daily_trends'].head(10))

    print("\n=== HOURLY ANALYSIS ===")
    print(results['hourly_analysis'])

    print("\n=== DAY OF WEEK ===")
    print(results['day_of_week'])
