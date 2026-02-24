# Ticket Lifecycle Analysis - User Guide

## Overview
The Ticket Lifecycle Analysis feature provides insights into security detection tickets by tracking their status, severity, and resolution over time. It helps you understand ticket distribution, identify pending issues, and monitor resolution progress.

---

## What You'll Get

The analysis generates:
- **Pivot Table**: Request IDs grouped by Status with Severity counts (Critical, High, Medium, Low)
- **Summary Metrics**: Total alerts, resolved alerts, pending alerts
- **Pending Request IDs**: List of all pending tickets with alert counts
- **Chart Data**: Visualization-ready data for stacked bar charts

---

## Prerequisites

### Required Columns in Your Data

Your CSV file must include these columns:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `Period` | Month name | "October 2025", "November 2025" |
| `Status` | Current ticket status | closed, in_progress, open, pending, on-hold |
| `SeverityName` | Severity level | Critical, High, Medium, Low |
| `Request ID` | Unique ticket identifier | 500001, REQ-12345, TKT-001 |

### Optional Columns

| Column | Description | Example Values |
|--------|-------------|----------------|
| `Count of SeverityName` | If your data is aggregated | 5, 10, 3 |
| `CreatedDate` | Ticket creation date | "2025-10-01", "10/1/2025" |
| `Category` | Ticket category | "Security Incident", "Malware" |
| `Priority` | Ticket priority | "High", "Medium", "Low" |

---

## Step-by-Step Usage Guide

### Step 1: Prepare Your Data

Create a CSV file with your ticket data. Here's an example format:

```csv
Period,Status,SeverityName,Request ID,CreatedDate,Category
October 2025,closed,Critical,500001,2025-10-01,Security Incident
October 2025,closed,High,500001,2025-10-01,Security Incident
October 2025,open,Medium,500002,2025-10-15,Malware Detection
October 2025,pending,High,500003,2025-10-20,Phishing
November 2025,closed,Critical,500004,2025-11-05,Ransomware
November 2025,in_progress,High,500005,2025-11-10,Data Breach
```

**Important Notes:**
- Status values are case-insensitive (closed, Closed, CLOSED all work)
- Severity values are case-insensitive (critical, Critical, CRITICAL all work)
- Each row represents one detection/alert
- Multiple rows with same Request ID = multiple alerts for that ticket

---

### Step 2: Load Your Data

```python
import pandas as pd
from ticket_lifecycle_generator import generate_ticket_lifecycle_analysis

# Load your CSV file
ticket_df = pd.read_csv('your_ticket_data.csv')

# Verify your data
print(ticket_df.head())
print(f"Total rows: {len(ticket_df)}")
```

---

### Step 3: Generate the Analysis

```python
# Generate analysis for your data
# num_months: Specify how many months of data you have (1-3)
results = generate_ticket_lifecycle_analysis(ticket_df, num_months=2)

# The results dictionary contains multiple outputs
print("Available results:", results.keys())
```

---

### Step 4: Access Your Results

#### A. Get the Pivot Table (Request ID x Severity)

```python
# For October 2025 data
october_pivot = results['request_severity_pivot_October_2025']
print(october_pivot)
```

**Output Example:**
```
        Status  Request ID  Critical  High  Medium  Low
0       Closed      500001         1     1       0    0
1       Closed      500004         1     0       0    0
2         Open      500002         0     0       1    0
3      Pending      500003         0     1       0    0
4  In Progress      500005         0     1       0    0
```

---

#### B. Get Summary Metrics

```python
# For October 2025 data
october_summary = results['ticket_summary_October_2025']

print(f"Total Alerts: {october_summary['total_alerts']}")
print(f"Alerts Resolved: {october_summary['alerts_resolved']}")
print(f"Alerts Pending: {october_summary['alerts_pending']}")
print(f"Pending Request IDs: {october_summary['pending_request_ids']}")
```

**Output Example:**
```
Total Alerts: 5
Alerts Resolved: 3
Alerts Pending: 2
Pending Request IDs: 500002 - 1 alert, 500003 - 1 alert
```

---

#### C. Get Chart Data for Visualization

```python
# For October 2025 data
october_chart = results['chart_data_October_2025']
print(october_chart)
```

**Output Example:**
```
   Request ID       Status  SeverityName  Count
0      500001       Closed      Critical      1
1      500001       Closed          High      1
2      500002         Open        Medium      1
3      500003      Pending          High      1
```

---

#### D. Export to Excel

```python
# Export pivot table to Excel
october_pivot.to_excel('october_ticket_analysis.xlsx', index=False)

# Or export all months to separate sheets
with pd.ExcelWriter('ticket_lifecycle_full_report.xlsx') as writer:
    results['request_severity_pivot_October_2025'].to_excel(writer, sheet_name='October Pivot', index=False)
    results['request_severity_pivot_November_2025'].to_excel(writer, sheet_name='November Pivot', index=False)
```

---

## Understanding the Results

### Status Categories

| Status | Meaning | Display Label |
|--------|---------|---------------|
| `closed` | Ticket resolved | Closed |
| `in_progress` | Actively being worked on | In Progress |
| `open` | New/unassigned ticket | Open |
| `pending` | Waiting for information | Pending |
| `on-hold` | Temporarily paused | On-Hold |

### Severity Levels

| Severity | Priority | Typical Response Time |
|----------|----------|----------------------|
| Critical | Highest | Immediate |
| High | Second | < 24 hours |
| Medium | Third | < 72 hours |
| Low | Lowest | < 1 week |

---

## Complete Example

Here's a full working example:

```python
import pandas as pd
from ticket_lifecycle_generator import generate_ticket_lifecycle_analysis

# 1. Prepare sample data
data = {
    'Period': ['October 2025', 'October 2025', 'October 2025', 'October 2025', 'November 2025'],
    'Status': ['closed', 'closed', 'open', 'pending', 'in_progress'],
    'SeverityName': ['Critical', 'High', 'Medium', 'High', 'Critical'],
    'Request ID': [500001, 500001, 500002, 500003, 500004],
    'CreatedDate': ['2025-10-01', '2025-10-01', '2025-10-15', '2025-10-20', '2025-11-05']
}

ticket_df = pd.DataFrame(data)

# 2. Generate analysis
results = generate_ticket_lifecycle_analysis(ticket_df, num_months=2)

# 3. Display October results
print("\n=== OCTOBER 2025 PIVOT TABLE ===")
print(results['request_severity_pivot_October_2025'])

print("\n=== OCTOBER 2025 SUMMARY ===")
oct_summary = results['ticket_summary_October_2025']
print(f"Total Alerts: {oct_summary['total_alerts']}")
print(f"Resolved: {oct_summary['alerts_resolved']}")
print(f"Pending: {oct_summary['alerts_pending']}")
print(f"Pending IDs: {oct_summary['pending_request_ids']}")

# 4. Export to Excel
results['request_severity_pivot_October_2025'].to_excel('october_analysis.xlsx', index=False)
print("\n✓ Exported to october_analysis.xlsx")
```

---

## Using Placeholder Data for Testing

If you want to test the feature before using real data:

```python
from ticket_lifecycle_generator import create_placeholder_ticket_data

# Create sample data for 3 months
months = ['October 2025', 'November 2025', 'December 2025']
sample_df = create_placeholder_ticket_data(months)

print(f"Created {len(sample_df)} sample tickets")
print(sample_df.head())

# Run analysis on sample data
results = generate_ticket_lifecycle_analysis(sample_df, num_months=3)
```

### Custom Placeholder Data with Specific Counts

```python
# Define custom ticket counts per month
custom_counts = {
    'October 2025': {
        'Open': 30,
        'Pending': 20,
        'On-hold': 15,
        'Closed': 60
    },
    'November 2025': {
        'Open': 25,
        'Pending': 18,
        'On-hold': 12,
        'Closed': 55
    }
}

sample_df = create_placeholder_ticket_data(
    months=['October 2025', 'November 2025'],
    custom_counts_per_month=custom_counts
)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Missing Required Columns
```
Error: 'Request ID' column not found
```
**Solution**: Ensure your CSV has a column named exactly `Request ID` or `RequestID`

---

#### Issue 2: Empty Results
```python
results = {}  # Empty dictionary
```
**Solution**: Check if your DataFrame is empty:
```python
print(f"Rows in DataFrame: {len(ticket_df)}")
print(ticket_df.head())
```

---

#### Issue 3: Month Names Not Matching
```python
# Results only show: request_severity_pivot_October2025
# But you expected: request_severity_pivot_October_2025
```
**Solution**: The function removes spaces and commas from month names. Use:
```python
# Instead of hardcoding the key
month_key = 'October 2025'.replace(' ', '_').replace(',', '')
pivot = results[f'request_severity_pivot_{month_key}']
```

---

#### Issue 4: Wrong Severity Counts
**Solution**: Check for duplicate rows or aggregated data:
```python
# If your data already has counts in a 'Count of SeverityName' column,
# the function will automatically expand the rows
print(ticket_df.columns)
```

---

## Integration with Streamlit Dashboard

To integrate this into your Streamlit app:

```python
import streamlit as st
import pandas as pd
from ticket_lifecycle_generator import generate_ticket_lifecycle_analysis

st.title("Ticket Lifecycle Analysis Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload Ticket Data CSV", type=['csv'])

if uploaded_file:
    # Load data
    ticket_df = pd.read_csv(uploaded_file)

    # Month selection
    months = ticket_df['Period'].unique()
    num_months = len(months)

    # Generate analysis
    results = generate_ticket_lifecycle_analysis(ticket_df, num_months=num_months)

    # Display results for each month
    for month in months:
        month_safe = month.replace(' ', '_').replace(',', '')

        st.subheader(f"Analysis for {month}")

        # Show pivot table
        pivot = results[f'request_severity_pivot_{month_safe}']
        st.dataframe(pivot)

        # Show summary
        summary = results[f'ticket_summary_{month_safe}']
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Alerts", summary['total_alerts'])
        col2.metric("Resolved", summary['alerts_resolved'])
        col3.metric("Pending", summary['alerts_pending'])

        if summary['pending_request_ids']:
            st.info(f"Pending: {summary['pending_request_ids']}")
```

---

## Tips for Best Results

1. **Consistent Data Entry**
   - Use consistent status names (all lowercase or all capitalized)
   - Use consistent date formats
   - Ensure Request IDs are unique per ticket

2. **Data Validation**
   - Remove empty rows before processing
   - Check for duplicate Request IDs with different statuses
   - Verify severity values are correct

3. **Monthly Analysis**
   - Keep data organized by month in the Period column
   - Use "Month YYYY" format for consistency (e.g., "October 2025")

4. **Performance**
   - For large datasets (>10,000 rows), consider filtering by date range first
   - Process one month at a time if memory is limited

---

## Support

For questions or issues:
- Check this guide first
- Review the example code provided
- Verify your data format matches the requirements
- Contact: Izami Ariff © 2025

---

## Version History

- **v1.0** (2025) - Initial release
  - Request ID x Severity pivot tables
  - Multi-month support
  - Summary metrics
  - Chart data generation
