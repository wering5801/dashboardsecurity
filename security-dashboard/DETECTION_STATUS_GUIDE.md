# 📊 Detection Status Analysis Guide

Complete guide to using the Detection Status Analysis feature that combines ticket status with detection severity.

---

## 🎯 What Is This Feature?

The **Detection Status Analysis** combines two dimensions in one view:
- **Status**: closed, in_progress, open, pending, on-hold
- **Severity**: Critical, High, Medium, Low

This creates a powerful **pivot table** showing exactly how many detections of each severity level are in each status.

### Example Output:

```
Status       | Critical | High | Medium | Low | Grand Total
-------------|----------|------|--------|-----|------------
closed       |    1     |  10  |   3    |  2  |     16
in_progress  |    0     |   0  |   1    |  0  |      1
Grand Total  |    1     |  10  |   4    |  2  |     17
```

---

## 📝 CSV Format Required

Your CSV file must have these columns:

| Column | Description | Example Values |
|--------|-------------|----------------|
| **Status** | Detection status | closed, in_progress, open, pending, on-hold |
| **SeverityName** | Detection severity | Critical, High, Medium, Low |
| **Request ID** | Detection identifier | 503457, 503528, 513757 |

### Sample CSV:

```csv
Status,SeverityName,Request ID
closed,Critical,503528
closed,High,503457
closed,High,503479
in_progress,Medium,513757
open,High,503900
```

📥 **Download sample:** `sample_detection_status_november.csv`

---

## 🚀 How to Use

### Step 1: Prepare Your Data

1. Export detection data from your system
2. Ensure it has: Status, SeverityName, Request ID columns
3. Save as CSV file (one file per month)

### Step 2: Upload to Dashboard

1. Go to **Falcon Data Generator**
2. Scroll to **"Detection Status by Severity"** section
3. Check **"Include Detection Status Analysis"**
4. Upload your CSV file(s) - one per month
5. Click **"🚀 Process All Months"**

### Step 3: View Analysis

1. Go to **"📊 Detection Status Analysis"** dashboard
2. Select the month you want to view
3. See:
   - Pivot table (Status x Severity)
   - Stacked bar chart
   - Key metrics (closure rate, critical/high open, etc.)
   - Distribution charts

---

## 📊 Dashboard Features

### 1. Key Metrics Cards

- **Total Detections**: Total count for the month
- **Closure Rate**: Percentage of closed detections
- **Critical/High Closed**: Count of resolved high-priority items
- **Critical/High Open**: Count of open high-priority items (needs attention!)

### 2. Pivot Table

Shows exact counts in a grid format:
- Rows = Status (closed, in_progress, etc.)
- Columns = Severity (Critical, High, Medium, Low)
- Values = Count of detections

Color coding:
- Gray = 0 detections
- Yellow = 5-10 detections
- Red = >10 detections

### 3. Stacked Bar Chart

Visual representation showing:
- X-axis: Status
- Y-axis: Number of detections
- Colors: Severity levels stacked

### 4. Distribution Charts

Two pie charts showing:
- **By Status**: Breakdown of all detections by status
- **By Severity**: Breakdown of all detections by severity

### 5. Export Options

- **Download Pivot Table**: CSV format
- **Download Raw Data**: Original detection records

---

## 💡 Use Cases

### 1. Tracking Closure Progress

**Question:** "How many Critical and High severity detections have we closed?"

**Answer:** Look at the pivot table:
- Row: `closed`
- Columns: `Critical` + `High`
- This shows your team's success in resolving high-priority issues

### 2. Identifying Bottlenecks

**Question:** "Which severity level has the most open detections?"

**Answer:** Look at rows `open` and `in_progress`:
- Compare numbers across severity columns
- Focus resources on the highest counts

### 3. Monthly Comparison

**Question:** "Are we improving month over month?"

**Answer:** Compare multiple months:
- Upload data for Month 1, Month 2, Month 3
- Check closure rate trend
- Compare Critical/High open counts

### 4. Executive Reporting

**Question:** "What's our detection management status?"

**Answer:** Key metrics provide executive summary:
- "We have an 85% closure rate"
- "Only 3 Critical/High severity detections remain open"
- "16 out of 17 total detections are closed"

---

## 🎨 Color Scheme

### Status Colors (when visualized separately):
- 🟢 **Closed**: Green (#70AD47)
- 🟡 **On-hold**: Yellow (#FFC000)
- 🔴 **Open**: Red (#DC143C)
- ⚫ **Pending**: Grey (#A9A9A9)

### Severity Colors:
- 🔴 **Critical**: Red (#DC143C)
- 🟠 **High**: Orange (#FF8C00)
- 🔵 **Medium**: Blue (#4169E1)
- 🟢 **Low**: Green (#70AD47)

---

## ❓ FAQ

### Q: Can I upload multiple months at once?
**A:** Yes! In the Falcon Data Generator, you can upload separate CSV files for each month (up to 3 months).

### Q: What if my CSV has different column names?
**A:** The system tries to auto-detect columns, but it's best to use exact names: `Status`, `SeverityName`, `Request ID`

### Q: Can I edit the data after uploading?
**A:** No, but you can download the processed data, edit it, and re-upload.

### Q: How is this different from Ticket Lifecycle Analysis?
**A:** 
- **Ticket Lifecycle**: Tracks ticket status over time (Open → Closed)
- **Detection Status**: Combines status WITH severity level for deeper insight

### Q: Can I use this for historical analysis?
**A:** Yes! Upload data from previous months to track trends over time.

---

## 🔧 Troubleshooting

### Issue: "Missing required columns"
**Solution:** Ensure your CSV has exactly these column names:
- `Status`
- `SeverityName`
- `Request ID`

### Issue: "No data available"
**Solution:** 
1. Go to Falcon Data Generator
2. Enable "Include Detection Status Analysis"
3. Upload CSV files
4. Click "Process All Months"

### Issue: Chart not displaying correctly
**Solution:** Check that:
- Status values are: closed, in_progress, open, pending, on-hold
- Severity values are: Critical, High, Medium, Low
- No empty/null values

---

## 📚 Related Features

- **Pivot Table Builder**: Create custom analysis
- **Main Dashboard Report**: Overall security metrics
- **PDF Export Dashboard**: Print-ready reports

---

**Developed by Izami Ariff © 2025**
