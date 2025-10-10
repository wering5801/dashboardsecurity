# 📊 Pivot Table Builder - Quick Start

## 🚀 3-Step Quick Start

### Step 1: Process Your Data
1. Go to **"Falcon Data Generator"** dashboard
2. Upload your CSV files (5 files per month)
3. Click **"Process All Months and Generate Templates"**

### Step 2: Build Your Pivot
1. Go to **"Pivot Table Builder (Excel-Style)"** dashboard
2. Select data source (Host/Detection/Time Analysis)
3. Drag fields:
   - **Rows**: What to group vertically (e.g., Period, Hostname)
   - **Columns**: What to group horizontally (e.g., SeverityName)
   - **Values**: What to count/sum (e.g., UniqueNo)
4. Choose aggregation (count, sum, mean, etc.)

### Step 3: Visualize & Export
1. Select chart type (Bar, Line, Pie, etc.)
2. Click **"Export to PDF"** or **"Download as Excel"**

---

## 🎯 Top 5 Most Useful Configurations

### 1️⃣ Three-Month Detection Overview
```
Rows: Period
Values: UniqueNo (count)
Chart: Bar Chart
```
📊 Shows total detections per month

### 2️⃣ Severity Breakdown by Month
```
Rows: Period
Columns: SeverityName
Values: UniqueNo (count)
Chart: Stacked Bar
```
📊 Shows how severity levels change over time

### 3️⃣ Top Hosts with Most Detections
```
Rows: Hostname
Columns: Period
Values: UniqueNo (count)
Chart: Heatmap
```
📊 Identifies problematic hosts across months

### 4️⃣ Geographic Distribution
```
Rows: Country
Values: UniqueNo (count)
Chart: Pie Chart
```
📊 Shows detection hotspots by location

### 5️⃣ User Activity Analysis
```
Rows: UserName
Columns: Period
Values: UniqueNo (count)
Chart: Bar Chart
Filter: Top 10 users
```
📊 Tracks user-related security incidents

---

## 💡 Pro Tips

✅ **Always start with Period in Rows** for time-based trends
✅ **Use Filters** to focus on specific hosts, users, or severities
✅ **Try different chart types** - same data, different insights
✅ **Export to Excel** for detailed analysis
✅ **Export to PDF** for executive reports

---

## 🎓 Example Workflow

**Goal:** Create a 3-month security executive report

1. **Load Data**: Falcon Generator → Upload 15 CSV files (3 months × 5 files)
2. **Overview Pivot**:
   - Rows: Period | Values: UniqueNo (count), Hostname (nunique)
   - Export as Bar Chart to PDF
3. **Severity Pivot**:
   - Rows: Period | Columns: SeverityName | Values: UniqueNo (count)
   - Export as Stacked Bar to PDF
4. **Top Hosts Pivot**:
   - Rows: Hostname | Columns: Period | Values: UniqueNo (count)
   - Filter: Top 5 hosts | Export as Heatmap to PDF
5. **Combine PDFs** into final executive report

---

## 📚 Full Guide

For detailed documentation, see [PIVOT_TABLE_GUIDE.md](PIVOT_TABLE_GUIDE.md)

---

**Happy Analyzing! 📊**
