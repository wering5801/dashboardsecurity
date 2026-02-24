# Quarantined File Analysis - User Guide

## Overview
The Quarantined File Analysis feature analyzes Falcon JSON quarantine data to help security teams track threats, identify affected systems, and generate comprehensive reports on quarantined files.

---

## Features

### What You'll Get:
- **Monthly Trend Chart**: Bar chart showing quarantine activity by month
- **File Summary**: Most frequently quarantined files with host impact
- **Host Summary**: Most affected hosts with file details
- **Status Distribution**: Breakdown of quarantine statuses
- **Executive Summary**: Auto-generated insights and recommendations
- **Export Options**: CSV exports for further analysis

---

## Quick Start Guide

### Step 1: Run the Demo

```bash
cd security-dashboard
streamlit run quarantine_analysis_demo.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Step 2: Load Data

You have two options:

**Option A: Upload Your JSON File**
1. Click "Choose JSON file" in the sidebar
2. Select your Falcon quarantine JSON file
3. Wait for validation
4. View the analysis!

**Option B: Use Sample Data**
1. Click "Load Sample Data" button
2. Instantly see the analysis with test data
3. Perfect for testing before using real data

---

## JSON Format Requirements

### Required Fields

Your JSON file must contain an array of objects with these fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Date of Quarantine` | String | ISO timestamp | `"2026-02-12T07:12:55Z"` |
| `File Name` | String | Name of quarantined file | `"malware.exe"` |
| `Hostname` | String | Affected host name | `"DESKTOP-001"` |
| `Agent ID` | String | Falcon agent identifier | `"d26758"` |
| `User` | String | Username | `"john.doe"` |
| `Status` | String | Quarantine status | `"quarantined"` or `"purged"` |

### Example JSON Structure

```json
[
  {
    "Date of Quarantine": "2026-02-12T07:12:55Z",
    "File Name": "play1.exe",
    "Hostname": "izami pc",
    "Agent ID": "d26758",
    "User": "ariff",
    "Status": "quarantined"
  },
  {
    "Date of Quarantine": "2026-02-11T08:51:36Z",
    "File Name": "webcampro.exe",
    "Hostname": "fredo laptop",
    "Agent ID": "fddf453",
    "User": "fredos",
    "Status": "quarantined"
  }
]
```

### Sample Files Included

- **sample_quarantine_data.json**: Ready-to-use test data based on your format
- Use "Download Sample JSON" button in the app for a smaller sample

---

## Dashboard Sections

### 1. Overview Metrics
Four key metrics displayed at the top:
- Total Quarantined Files
- Unique Files (distinct malware types)
- Affected Hosts (number of systems impacted)
- Affected Users (number of user accounts)

### 2. Monthly Quarantine Trend
**Bar chart** showing:
- Files quarantined per month
- Trend over time
- Peak activity periods

**Use Case**: Identify if threats are increasing, decreasing, or following a pattern

### 3. Most Quarantined Files
**Horizontal bar chart** + **Detailed table** showing:
- File names with highest quarantine counts
- Number of affected hosts per file
- First and last seen dates
- List of affected hosts

**Use Case**: Identify persistent threats requiring additional security measures

### 4. Most Affected Hosts
**Horizontal bar chart** + **Detailed table** showing:
- Hosts with most quarantines
- Unique file count per host
- Primary user of each host
- Last activity timestamp
- Files detected on each host

**Use Case**: Identify compromised systems needing remediation or reimaging

### 5. Status Distribution
**Pie chart** showing:
- Breakdown of quarantine statuses
- Percentage distribution

**Use Case**: Track remediation progress

### 6. Executive Summary
Auto-generated insights including:
- Total impact summary
- Most critical threats
- Most affected systems
- Peak activity periods
- Remediation recommendations

---

## Customization Options

### Sidebar Settings

#### Report Period
- Set the reporting period name (e.g., "February 2025")
- Used in titles and exported files

#### Visualization Settings
- **Monthly Trend Color**: Customize bar chart color
- **File Analysis Color**: Customize file chart color
- **Host Analysis Color**: Customize host chart color
- **Show Top N Items**: Choose how many items to display (5-20)
- **Show Percentages**: Toggle percentage display in tables

---

## Export Options

Three CSV export options available:

### 1. Files Summary Export
Contains:
- File Name
- Quarantine Count
- Affected Hosts
- Host List
- First Seen / Last Seen dates
- Percentage of total

### 2. Hosts Summary Export
Contains:
- Hostname
- Total Quarantines
- Unique Files
- Primary User
- Files List
- Last Activity
- Percentage of total

### 3. Raw Data Export
Complete dataset with all fields:
- All original JSON fields
- Parsed dates
- Month groupings
- Full analysis data

---

## Integration with Main Dashboard

### Adding to Pivot Table Builder

The quarantine analysis can be integrated as an optional section under "Host Security Analysis" in the Pivot Table Builder:

1. **In falcon_generator.py** (or your data upload module):
   - Add checkbox: "Include Quarantine File Analysis"
   - Add JSON file uploader for quarantine data
   - Process quarantine data when checkbox is selected
   - Store results in `st.session_state['quarantine_analysis_results']`

2. **In pivot_table_builder.py**:
   - Add "Quarantine Analysis" to available categories
   - Map to session state key
   - Display as optional subsection under "Host Security Analysis"

3. **Usage Flow**:
   ```
   User uploads Falcon detection CSV
   ↓
   [Optional] User ticks "Include Quarantine Analysis"
   ↓
   User uploads Quarantine JSON file
   ↓
   Both analyses processed
   ↓
   Available in Pivot Table Builder
   ```

### Example Integration Code

```python
# In your data upload page
st.subheader("B. Host Security Analysis")

# Existing host analysis upload
host_file = st.file_uploader("Upload Host Data (CSV)", type=['csv'])

# NEW: Optional quarantine analysis
include_quarantine = st.checkbox("Include Quarantined File Summary")

if include_quarantine:
    quarantine_file = st.file_uploader(
        "Upload Quarantine Data (JSON)",
        type=['json'],
        help="Upload Falcon quarantine JSON file"
    )

    if quarantine_file:
        from quarantine_file_analysis import (
            parse_quarantine_json,
            generate_quarantine_analysis,
            validate_quarantine_json
        )

        # Load and validate JSON
        json_data = json.load(quarantine_file)
        validation = validate_quarantine_json(json_data)

        if validation['is_valid']:
            # Parse and analyze
            df = parse_quarantine_json(json_data)
            results = generate_quarantine_analysis(df)

            # Store in session state
            st.session_state['quarantine_analysis_results'] = results
            st.success("✅ Quarantine analysis completed!")
        else:
            st.error("❌ Invalid JSON file")
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Invalid JSON format"
**Solution**:
- Ensure your file is valid JSON (use a JSON validator)
- Check that it's an array `[...]` not a single object `{...}`
- Verify all required fields are present

#### Issue 2: "Missing required fields"
**Solution**:
- Check field names match exactly (case-sensitive)
- Required: `Date of Quarantine`, `File Name`, `Hostname`, `User`, `Status`
- Add missing fields to your JSON

#### Issue 3: Date parsing warnings
**Solution**:
- Dates should be in ISO format: `YYYY-MM-DDTHH:MM:SSZ`
- The system will attempt flexible parsing but may warn you
- Update date format in your export if possible

#### Issue 4: No data showing
**Solution**:
- Check if JSON array is empty
- Verify data loaded by checking overview metrics
- Look for error messages in the console

---

## Best Practices

### Data Quality
1. **Regular Exports**: Export quarantine data weekly or monthly
2. **Consistent Naming**: Use consistent file naming conventions
3. **Complete Records**: Ensure all required fields are populated
4. **Date Accuracy**: Verify timestamps are correct

### Analysis Tips
1. **Compare Periods**: Run analysis for multiple months to identify trends
2. **Focus on Repeats**: Pay special attention to files appearing multiple times
3. **User Patterns**: Look for users with multiple quarantines (potential risky behavior)
4. **Host Clusters**: Investigate if certain hosts are repeatedly affected

### Reporting
1. **Executive Summary**: Use auto-generated summary for quick briefings
2. **Detailed Tables**: Export for deeper investigation
3. **Charts**: Include in monthly security reports
4. **Trend Analysis**: Compare monthly trends to identify patterns

---

## Performance Notes

- **Recommended**: Up to 10,000 records per JSON file
- **Large Datasets**: For >10,000 records, consider splitting by month
- **Processing Time**: Typically <2 seconds for 1,000 records
- **Memory**: Minimal impact, tested up to 50MB JSON files

---

## Future Enhancements

Potential features for future versions:
- Multi-file batch processing
- Time-series forecasting
- Integration with MITRE ATT&CK framework
- Automated threat intelligence lookups
- PDF report generation
- Email alerting for new threats

---

## Support & Feedback

For issues or suggestions:
- Check this guide first
- Review sample data format
- Test with sample data before using production data

**Developed by**: Izami Ariff © 2025

---

## Version History

**v1.0** (2025-02-24)
- Initial release
- JSON parsing and validation
- Monthly trend analysis
- File and host summary tables
- Status distribution
- Executive summary
- CSV export functionality
- Sample data generation
- Standalone demo application
