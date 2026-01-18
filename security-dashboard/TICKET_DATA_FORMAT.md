# Ticket Lifecycle Data Format Guide

This guide explains how to prepare your ticket data for the Ticket Lifecycle Management section of the Falcon Security Dashboard.

## 📋 Required CSV Format

Your ticket data CSV file must contain the following **required columns**:

### Required Columns:

1. **Period** (string)
   - Format: "Month YYYY" (e.g., "October 2025", "November 2025", "December 2025")
   - Must match the month names used in your Falcon data
   - Example: `"October 2025"`, `"November 2025"`, `"December 2025"`

2. **Status** (string)
   - Must be exactly one of these four values:
     - `"Open"` - Active tickets awaiting action
     - `"Pending"` - Tickets awaiting response/information
     - `"On-hold"` - Tickets temporarily paused
     - `"Closed"` - Resolved tickets
   - ⚠️ **Case-sensitive**: Use exact capitalization as shown above

### Optional Columns:

These columns are not required but can be included for record-keeping:

- **TicketID** (string) - Unique ticket identifier (e.g., "TKT-00001")
- **CreatedDate** (date/string) - Date ticket was created (e.g., "2025-10-05")
- **Category** (string) - Ticket category (e.g., "Security Incident", "Access Request")
- **Priority** (string) - Ticket priority level (e.g., "Critical", "High", "Medium", "Low")

---

## 📄 Sample CSV File

A sample CSV file ([sample_ticket_data.csv](sample_ticket_data.csv)) is provided in the project folder with the following structure:

```csv
TicketID,Period,Status,CreatedDate,Category,Priority
TKT-00001,October 2025,Open,2025-10-05,Security Incident,High
TKT-00002,October 2025,Pending,2025-10-08,Security Incident,High
TKT-00003,October 2025,On-hold,2025-10-10,Security Incident,Medium
TKT-00004,October 2025,Closed,2025-10-03,Security Incident,Critical
TKT-00005,November 2025,Open,2025-11-02,Security Incident,High
TKT-00006,November 2025,Pending,2025-11-07,Security Incident,Low
TKT-00007,November 2025,On-hold,2025-11-11,Security Incident,High
TKT-00008,November 2025,Closed,2025-11-05,Security Incident,Critical
TKT-00009,December 2025,Open,2025-12-03,Security Incident,High
TKT-00010,December 2025,Pending,2025-12-06,Security Incident,High
TKT-00011,December 2025,On-hold,2025-12-11,Security Incident,Low
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
