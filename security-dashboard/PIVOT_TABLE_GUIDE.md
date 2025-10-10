# 📊 Pivot Table Builder - User Guide

## Overview

The **Pivot Table Builder** is a Flexmonster-style interactive pivot table interface that allows you to create custom multi-month trend analysis reports from your Falcon data templates.

**Developed by:** Izami Ariff © 2025

---

## 🚀 Getting Started

### Prerequisites

1. **Process your data first** using the **Falcon Data Generator**:
   - Upload 5 CSV files per month (1-3 months supported)
   - Click "Process All Months and Generate Templates"
   - This creates the templates needed for pivot analysis

2. **Navigate to Pivot Table Builder** from the dashboard selector

---

## 🎯 How to Use

### Step 1: Select Data Source

Choose which template to analyze:
- **Host Analysis**: Host-related security data
- **Detection Analysis**: Detection and severity data
- **Time Analysis**: Time-based detection patterns

### Step 2: Configure Fields (Drag & Drop Style)

The interface works like Excel pivot tables or Flexmonster:

#### **📋 Rows**
Fields you want to group vertically (row headers)

**Example:**
- Select `Period` to show months as rows
- Select `Hostname` to show hosts as rows

#### **📊 Columns**
Fields you want to group horizontally (column headers)

**Example:**
- Select `SeverityName` to show Critical, High, Medium, Low as columns
- Select `Period` for month-by-month comparison

#### **🔢 Values**
Fields you want to aggregate/calculate

**Example:**
- Select `UniqueNo` to count detections
- Select `Hostname` to count unique hosts

#### **🔄 Aggregation Function**
How to calculate values:
- `count` - Count records
- `sum` - Sum values
- `mean` - Average values
- `median` - Median values
- `min` - Minimum value
- `max` - Maximum value
- `nunique` - Count unique values

#### **🔍 Filters**
Narrow down your data:
- Select a field to filter
- Choose specific values to include
- Remove filters anytime

---

## 📈 Example Configurations

### Example 1: Three-Month Detection Trend

**Goal:** Show total detections per month

**Configuration:**
- Rows: `Period`
- Columns: _(empty)_
- Values: `UniqueNo`
- Aggregation: `count`

**Result:**
```
Period          | Count
----------------|------
June 2025       | 31
July 2025       | 31
August 2025     | 38
```

---

### Example 2: Host Overview by Month

**Goal:** Show unique hosts and detections by month

**Configuration:**
- Rows: `Period`
- Columns: _(empty)_
- Values: `Hostname`, `UniqueNo`
- Aggregation: `nunique` (for Hostname), `count` (for UniqueNo)

**Result:**
```
Period          | Unique Hosts | Total Detections
----------------|--------------|------------------
June 2025       | 12           | 31
July 2025       | 10           | 31
August 2025     | 10           | 38
```

---

### Example 3: Severity Distribution by Month

**Goal:** Show detections by severity level across months

**Configuration:**
- Rows: `Period`
- Columns: `SeverityName`
- Values: `UniqueNo`
- Aggregation: `count`

**Result:**
```
Period          | Critical | High | Medium | Low
----------------|----------|------|--------|----
June 2025       | 5        | 15   | 8      | 3
July 2025       | 2        | 18   | 9      | 2
August 2025     | 8        | 20   | 7      | 3
```

---

### Example 4: Top Hosts with Most Detections

**Goal:** Identify hosts with highest detection counts

**Configuration:**
- Rows: `Hostname`
- Columns: `Period`
- Values: `UniqueNo`
- Aggregation: `count`
- Filter: _(optional)_ Select specific hosts

**Result:**
```
Hostname        | June 2025 | July 2025 | August 2025 | Total
----------------|-----------|-----------|-------------|------
Host-A          | 10        | 8         | 12          | 30
Host-B          | 8         | 9         | 10          | 27
Host-C          | 5         | 7         | 9           | 21
```

---

### Example 5: User Analysis by Site

**Goal:** Show user detection counts by site location

**Configuration:**
- Rows: `Site`
- Columns: `UserName`
- Values: `UniqueNo`
- Aggregation: `count`

---

### Example 6: Detection Count by Country

**Goal:** Geographic distribution of detections

**Configuration:**
- Rows: `Country`
- Columns: _(empty)_
- Values: `UniqueNo`
- Aggregation: `count`

---

## 📊 Chart Types

Choose visualization that best fits your data:

### **Bar Chart**
- Best for: Comparing values across categories
- Use when: Rows have few categories (< 10)

### **Stacked Bar**
- Best for: Showing composition over time
- Use when: You have both Rows and Columns configured

### **Line Chart**
- Best for: Showing trends over time
- Use when: Period/Date is in Rows

### **Area Chart**
- Best for: Cumulative trends
- Use when: Showing volume over time

### **Pie Chart**
- Best for: Showing proportions
- Use when: Single dimension analysis (Rows only)

### **Heatmap**
- Best for: Showing intensity/patterns
- Use when: Both Rows and Columns configured with numeric values

---

## 💾 Export Options

### **📄 Export to PDF**
Creates a professional report containing:
- Configuration details
- Full pivot table (first 20 rows)
- Visualization chart
- Timestamp

**Use for:** Executive reports, documentation

### **📊 Download as Excel**
Creates an Excel workbook with:
- Pivot Table sheet
- Configuration sheet
- Full data (no row limit)

**Use for:** Further analysis, sharing with team

### **📥 Download Pivot Table (CSV)**
Quick CSV export of current pivot table

**Use for:** Quick data export, import into other tools

---

## 🔍 Insights & Statistics

The dashboard automatically shows:
- **Total**: Sum of all values
- **Average**: Mean of all values
- **Maximum**: Highest value
- **Top Values**: Highest row totals
- **Distribution Chart**: Visual distribution of top 10 values

---

## 💡 Pro Tips

1. **Start Simple**: Begin with just Rows, then add Columns
2. **Use Filters**: Narrow down data before creating complex pivots
3. **Period in Rows**: For time-based analysis, put `Period` in Rows
4. **Multiple Values**: Select multiple fields in Values for comparison
5. **Reset Anytime**: Use "Reset Configuration" to start fresh
6. **Save Configs**: Document your successful configurations for reuse

---

## 🎓 Common Use Cases

### Monthly Security Report
- Rows: Period
- Values: UniqueNo (count), Hostname (nunique)
- Chart: Bar Chart

### Severity Trend Analysis
- Rows: Period
- Columns: SeverityName
- Values: UniqueNo (count)
- Chart: Stacked Bar

### Host Vulnerability Assessment
- Rows: Hostname
- Values: SeverityName (count)
- Filter: SeverityName = Critical, High
- Chart: Horizontal Bar

### Geographic Analysis
- Rows: Country
- Values: UniqueNo (count)
- Chart: Pie Chart

### User Activity Report
- Rows: UserName
- Columns: Period
- Values: UniqueNo (count)
- Chart: Heatmap

---

## ⚠️ Troubleshooting

### "No data available"
- ✅ Process data in Falcon Generator first
- ✅ Select correct data source

### "Error creating pivot table"
- ✅ Check field compatibility with aggregation function
- ✅ Ensure numeric fields for sum/mean/median
- ✅ Try different field combinations

### "Chart not displaying"
- ✅ Verify pivot table has data
- ✅ Try different chart type
- ✅ Check if data structure suits the chart type

### PDF export fails
- ✅ Ensure all dependencies installed: `pip install kaleido reportlab`
- ✅ Check if chart is displaying correctly first

---

## 📚 Field Reference

### Host Analysis Fields
- `UniqueNo` - Detection ID
- `Hostname` - Computer name
- `UserName` - User account
- `OS Version` - Operating system
- `Sensor Version` - Security agent version
- `Site` - Physical location
- `OU` - Organizational Unit
- `Period` - Month label

### Detection Analysis Fields
- `UniqueNo` - Detection ID
- `Hostname` - Computer name
- `SeverityName` - Critical/High/Medium/Low
- `Tactic` - Attack tactic
- `Technique` - Attack technique
- `Objective` - Detection objective
- `Status` - Detection status
- `FileName` - File involved
- `LocalIP` - Internal IP address
- `Country` - Country code
- `Period` - Month label

### Time Analysis Fields
- `UniqueNo` - Detection ID
- `Hostname` - Computer name
- `Detect MALAYSIA TIME FORMULA` - Timestamp
- `Period` - Month label

---

## 🆘 Support

For issues or questions:
1. Check this guide first
2. Review example configurations
3. Try resetting configuration
4. Report issues with screenshots

---

**Version:** 1.0
**Last Updated:** 2025-01-06
**Developed by:** Izami Ariff
