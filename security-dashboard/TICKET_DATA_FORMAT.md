# Detection Status by Severity Data Format Guide

This guide explains how to prepare your detection data for the **Detection Status by Severity** analysis - showing detections by both Status AND Severity level.

## 📋 Required CSV Format

Your detection data CSV file must contain the following **required columns**:

### Required Columns:

1. **Period** (string)
   - Format: "Month YYYY" (e.g., "October 2025", "November 2025", "December 2025")
   - Must match the month names used in your Falcon data
   - Example: `"October 2025"`, `"November 2025"`, `"December 2025"`

2. **Status** (string)
   - Must be one of these values:
     - `"closed"` - Resolved detections
     - `"in_progress"` - Detections being investigated
     - `"open"` - New/active detections
     - `"pending"` - Awaiting action/response
     - `"on-hold"` - Temporarily paused
   - Note: lowercase preferred but will be normalized automatically

3. **SeverityName** (string) - **NEW REQUIRED COLUMN**
   - Must be one of these values:
     - `"Critical"` - Most severe detections
     - `"High"` - High severity detections
     - `"Medium"` - Medium severity detections
     - `"Low"` - Low severity detections
   - This creates the Status x Severity pivot table

4. **Request ID** (string/number)
   - Detection identifier (e.g., "503457", "503528", "513757")
   - Can use "N/A" if no ID available
   - Used for counting detections

### Optional Columns:

These columns are not required but can be included for record-keeping:

- **TicketID** (string) - Unique ticket identifier (e.g., "TKT-00001")
- **CreatedDate** (date/string) - Date detection was created (e.g., "2025-10-05")
- **Category** (string) - Detection category (e.g., "Malware", "Phishing")
- **Priority** (string) - Priority level

---

## 📄 Sample CSV File

A sample CSV file ([sample_ticket_data.csv](sample_ticket_data.csv)) is provided with the exact format matching your November 2025 data:

```csv
Period,Status,SeverityName,Request ID
November 2025,closed,Critical,503528
November 2025,closed,High,503457
November 2025,closed,High,503479
November 2025,closed,High,503528
November 2025,closed,Low,N/A
November 2025,closed,Medium,503900
November 2025,in_progress,Medium,513757
```

### Output - Pivot Table:

This CSV creates a pivot table showing **Total Detections Count by Status and Severity**:

```
Status       | Critical | High | Medium | Low | Grand Total
-------------|----------|------|--------|-----|------------
closed       |    1     |  10  |   3    |  2  |     16
in_progress  |    0     |   0  |   1    |  0  |      1
Grand Total  |    1     |  10  |   4    |  2  |     17
TKT-00012,December 2025,Closed,2025-12-04,Security Incident,Critical
```

---

## 🎯 Example Data Distribution

Here's an example of how ticket counts might look across 3 months:

| Month | Open | Pending | On-hold | Closed | Total |
|-------|------|---------|---------|--------|-------|
| October 2025 | 5 | 8 | 3 | 25 | 41 |
| November 2025 | 7 | 10 | 5 | 30 | 52 |
| December 2025 | 4 | 6 | 2 | 35 | 47 |

---

## 📊 What the Dashboard Shows

Once you upload your ticket data, the dashboard will display:

1. **Section A.1: Ticket Status Count Across Three Months**
   - Grouped bar chart showing Open, Pending, On-hold, and Closed counts
   - Each month displayed with consistent color coding:
     - First month: Green (#70AD47)
     - Second month: Blue (#5B9BD5)
     - Third month: Gold (#FFC000)
   - Easy comparison of status trends over time

---

## 🔧 How to Use

### Option 1: Upload Your Own CSV File

1. Go to **"Falcon Data Generator"** in the sidebar
2. Scroll to **"🎫 Ticket Lifecycle Data (Optional)"**
3. Check **"Include Ticket Lifecycle Analysis"**
4. Select **"Upload CSV file"**
5. Click **"Upload Ticket Data CSV"** and select your prepared CSV file
6. Click **"🚀 Process All Months and Generate Templates"**

### Option 2: Use Placeholder Data

1. Check **"Include Ticket Lifecycle Analysis"**
2. Select **"Use placeholder data"**
3. Click **"🚀 Process All Months and Generate Templates"**
4. The system will generate example data with these counts:
   - Open: 25 tickets per month
   - Pending: 15 tickets per month
   - On-hold: 10 tickets per month
   - Closed: 50 tickets per month

**Note:** You can customize placeholder values by editing `ticket_lifecycle_generator.py` (lines 70-77)

---

## ✅ Data Validation

The system will automatically:

- Count tickets by Status for each Period (Month)
- Group data for visualization
- Handle missing or additional columns gracefully
- Display error messages if required columns are missing

---

## 💡 Tips

1. **Match Month Names:** Ensure your Period column matches the month format used in your Falcon CSV files
2. **Consistent Statuses:** Use only the four approved status values (Open, Pending, On-hold, Closed)
3. **One Row Per Ticket:** Each row should represent a unique ticket
4. **UTF-8 Encoding:** Save your CSV file with UTF-8 encoding to avoid character issues
5. **No Empty Status:** Every ticket should have a status value

---

## 🚨 Common Issues

### Issue: "No data available"
**Solution:** Verify that your CSV has both 'Period' and 'Status' columns with correct spelling

### Issue: "Ticket analysis failed"
**Solution:** Check that Status values are exactly: "Open", "Pending", "On-hold", or "Closed" (case-sensitive)

### Issue: Chart not appearing
**Solution:** Make sure you checked the "A. Ticket Lifecycle Management" checkbox in the PDF Export Dashboard sidebar

---

## 📞 Support

If you encounter issues with the ticket data format, please:
1. Check the sample file: `sample_ticket_data.csv`
2. Verify required columns are present
3. Ensure status values match exactly (case-sensitive)
4. Review error messages in the status container

---

**Developed by Izami Ariff © 2025**
