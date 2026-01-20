# Detection Status by Severity Data Format Guide

## Overview

This guide explains the CSV format required for the **Ticket Lifecycle Analysis** feature, which displays:
1. **Section A.1**: Request ID Pivot Table showing Count of SeverityName/Status/Request ID
2. **Section A.2**: Summary for Detections (alerts triggered, resolved, pending)

## Required CSV Format

### Required Columns

| Column Name | Type | Description | Example Values |
|------------|------|-------------|----------------|
| `Period` | String | Month name | "November 2025", "December 2025" |
| `Status` | String | Detection status | closed, in_progress, open, pending, on-hold |
| `SeverityName` | String | **REQUIRED** - Severity level | Critical, High, Medium, Low |
| `Request ID` | String/Number | Detection identifier | 503457, 503528, 513757 |

### Status Values

The system accepts the following status values (case-insensitive):
- **closed** / Closed / CLOSED
- **in_progress** / In Progress / IN_PROGRESS
- **open** / Open / OPEN
- **pending** / Pending / PENDING
- **on-hold** / On-hold / ON-HOLD

### Severity Values

The system accepts the following severity values (case-insensitive):
- **Critical** / critical / CRITICAL
- **High** / high / HIGH
- **Medium** / medium / MEDIUM
- **Low** / low / LOW

## Sample CSV Format

```csv
Period,Status,SeverityName,Request ID
November 2025,closed,High,503457
November 2025,closed,High,503457
November 2025,closed,High,503479
November 2025,closed,Critical,503528
November 2025,closed,High,503528
November 2025,closed,High,503528
November 2025,closed,High,503528
November 2025,closed,Medium,503900
November 2025,closed,Medium,503900
November 2025,closed,Medium,503900
November 2025,closed,Low,N/A
November 2025,closed,Low,N/A
November 2025,in_progress,Medium,513757
```

## Expected Output

### Section A.1: Count of SeverityName/Status/Request ID

The pivot table will group by Status and show Request IDs with severity counts:

**CLOSED**

| Request ID | Critical | High | Medium | Low |
|------------|----------|------|--------|-----|
| 503457     | 0        | 2    | 0      | 0   |
| 503479     | 0        | 1    | 0      | 0   |
| 503528     | 1        | 7    | 0      | 0   |
| 503900     | 0        | 0    | 3      | 0   |
| N/A        | 0        | 0    | 0      | 2   |

**IN_PROGRESS**

| Request ID | Critical | High | Medium | Low |
|------------|----------|------|--------|-----|
| 513757     | 0        | 0    | 1      | 0   |

### Section A.2: Summary for November Detections

| Summary for November Detections | Value | Details |
|----------------------------------|-------|---------|
| Number of alert triggered this month | 17 | |
| Number of alert resolve | 16 | |
| Number of alert pending | 1 | Request ID : 513757 |

**Calculations:**
- **Total alerts triggered** = Total number of rows in the CSV
- **Alerts resolved** = Count of rows where Status = "closed"
- **Alerts pending** = Count of rows where Status is "open", "pending", "on-hold", or "in_progress"

## Chart Output

The system will also generate a stacked bar chart showing:
- **X-axis**: Request IDs grouped by Status (e.g., "503457 (closed)", "513757 (in_progress)")
- **Y-axis**: Number of Detections
- **Bars**: Stacked by Severity (Critical=Red, High=Orange, Medium=Blue, Low=Green)

## Configuring Summary Values

You can override the automatically calculated values in the **Pivot Table Builder** configuration page:

1. Go to **Pivot Table Builder (Excel-Style)** in the sidebar
2. Select **"Ticket Lifecycle Analysis"** as the category
3. Scroll to **"Ticket Lifecycle Summary Settings"**
4. Modify the values:
   - 🔢 Number of alerts triggered
   - ✅ Number of alerts resolved
   - ⏳ Number of alerts pending

These configured values will be used in the Main Dashboard Report.

## Multi-Month Support

You can upload data for multiple months. Each month will be processed separately and displayed as:
- **Section A.1**: Count of SeverityName/Status/Request ID for October 2025
- **Section A.2**: Summary for October Detections
- **Section A.1**: Count of SeverityName/Status/Request ID for November 2025
- **Section A.2**: Summary for November Detections
- etc.

**Example multi-month CSV:**

```csv
Period,Status,SeverityName,Request ID
October 2025,closed,High,502001
October 2025,closed,Critical,502002
October 2025,in_progress,Medium,502003
November 2025,closed,High,503457
November 2025,closed,Critical,503528
November 2025,in_progress,Medium,513757
December 2025,closed,High,504001
December 2025,open,Critical,504002
```

## Download Sample Template

A sample CSV template is available for download in the **Falcon Data Generator** page:

1. Go to **Falcon Data Generator** in the sidebar
2. Check **"Include Ticket Lifecycle Analysis"**
3. Click **"📥 Download Sample CSV Template"**
4. Fill in your detection data following the format
5. Upload the file to generate the analysis

---

**Developed by Izami Ariff © 2025**
