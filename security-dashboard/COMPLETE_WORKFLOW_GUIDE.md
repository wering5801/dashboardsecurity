# 📊 Complete Multi-Month Analysis Workflow

## Overview

This guide explains the complete workflow from uploading CSV files to generating pivot table PDF reports with multi-month trend analysis.

**Developed by:** Izami Ariff © 2025

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: FALCON DATA GENERATOR                                  │
│  ├── Upload 5 CSV files per month (1-3 months)                 │
│  ├── Process & Create Templates                                │
│  │   ├── Host Analysis Template                                │
│  │   ├── Detection Analysis Template                           │
│  │   └── Time Analysis Template                                │
│  └── ✅ Templates stored in session                            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: AUTOMATIC ANALYSIS GENERATION                          │
│  (Runs automatically after Step 1)                              │
│  ├── HOST ANALYSIS GENERATOR                                    │
│  │   ├── 1. Overview - KEY METRICS                             │
│  │   ├── 2. Overview - TOP HOSTS WITH DETECTIONS               │
│  │   ├── 3. User Analysis                                      │
│  │   └── 4. Sensor Analysis                                    │
│  ├── DETECTION & SEVERITY GENERATOR                             │
│  │   ├── 1. Overview - KEY METRICS                             │
│  │   ├── 2. Overview - TOP SEVERITIES                          │
│  │   ├── 3. Geographic Analysis                                │
│  │   ├── 4. File Analysis                                      │
│  │   └── 5. Raw Data (Hostname, Severity, Tactic, etc.)        │
│  └── TIME-BASED ANALYSIS GENERATOR                              │
│      ├── 1. Daily Trends                                        │
│      ├── 2. Hourly Analysis                                     │
│      └── 3. Day of Week                                         │
│  └── ✅ Analysis results stored in session                     │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: PIVOT TABLE BUILDER                                    │
│  ├── Select Analysis Category (Host/Detection/Time)            │
│  ├── Select Specific Analysis Output                           │
│  ├── Configure Pivot Fields (Rows, Columns, Values)            │
│  ├── Choose Chart Type                                          │
│  ├── Generate Pivot Table & Chart                              │
│  └── Export to PDF / Excel / CSV                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Guide

### **Step 1: Upload and Process Data**

1. Navigate to **"Falcon Data Generator"** in the sidebar

2. **Input Number of Months**:
   - Enter 1, 2, or 3 months

3. **Upload CSV Files** (5 files per month):
   - File 1: Detection summary data
   - File 2: Filename data
   - File 3: LocalIP data
   - File 4: Country data
   - File 5: DetectionTime data

4. **Click "Process All Months and Generate Templates"**

5. **Wait for Processing**:
   ```
   ✅ Templates Created:
   - Host Analysis Template
   - Detection Analysis Template
   - Time Analysis Template

   🔄 Generating analysis results from templates...

   ✅ Host Analysis: 4 analysis outputs generated
   ✅ Detection Analysis: 5 analysis outputs generated
   ✅ Time Analysis: 3 analysis outputs generated

   🎉 All analysis results generated successfully!
   ```

---

### **Step 2: Automatic Analysis Generation**

**This step runs automatically after Step 1 completes!**

#### **A. Host Analysis Outputs**

**1. Overview - KEY METRICS**

| Month      | Total Hosts | Total Detections | Unique Users | Windows Hosts | Avg. Detections per Host |
|------------|-------------|------------------|--------------|---------------|--------------------------|
| June 2025  | 12          | 31               | 6            | 31            | 2.6                      |
| July 2025  | 10          | 31               | 6            | 31            | 3.1                      |
| August 2025| 10          | 38               | 5            | 38            | 3.8                      |

**2. Overview - TOP HOSTS WITH DETECTIONS**

| Hostname   | June 2025 | July 2025 | August 2025 | Total |
|------------|-----------|-----------|-------------|-------|
| HOST-A     | 10        | 8         | 12          | 30    |
| HOST-B     | 8         | 9         | 10          | 27    |
| HOST-C     | 5         | 7         | 9           | 21    |

**3. User Analysis**

| UserName | June 2025 | July 2025 | August 2025 | Total | Unique Hosts |
|----------|-----------|-----------|-------------|-------|--------------|
| user1    | 15        | 12        | 18          | 45    | 5            |
| user2    | 10        | 13        | 12          | 35    | 4            |

**4. Sensor Analysis**

| Sensor Version | June 2025 | July 2025 | August 2025 | Total | Status   |
|----------------|-----------|-----------|-------------|-------|----------|
| 7.23.19508.0   | 25        | 28        | 30          | 83    | Latest   |
| 7.16.18613.0   | 6         | 3         | 8           | 17    | Outdated |

#### **B. Detection & Severity Analysis Outputs**

**1. Overview - KEY METRICS**

| Month       | Total Detections | Critical | High | Medium | Low | Unique Hosts |
|-------------|------------------|----------|------|--------|-----|--------------|
| June 2025   | 31               | 5        | 15   | 8      | 3   | 12           |
| July 2025   | 31               | 2        | 18   | 9      | 2   | 10           |
| August 2025 | 38               | 8        | 20   | 7      | 3   | 10           |

**2. Overview - TOP SEVERITIES**

| SeverityName | June 2025 | July 2025 | August 2025 | Total | Percentage |
|--------------|-----------|-----------|-------------|-------|------------|
| High         | 15        | 18        | 20          | 53    | 53.0%      |
| Medium       | 8         | 9         | 7           | 24    | 24.0%      |
| Critical     | 5         | 2         | 8           | 15    | 15.0%      |

**3. Geographic Analysis**

| Country   | June 2025 | July 2025 | August 2025 | Total | Percentage |
|-----------|-----------|-----------|-------------|-------|------------|
| Malaysia  | 20        | 22        | 25          | 67    | 67.0%      |
| Singapore | 8         | 6         | 10          | 24    | 24.0%      |

**4. File Analysis**

| FileName    | June 2025 | July 2025 | August 2025 | Total | Percentage |
|-------------|-----------|-----------|-------------|-------|------------|
| file1.exe   | 10        | 8         | 12          | 30    | 30.0%      |
| file2.dll   | 8         | 9         | 10          | 27    | 27.0%      |

**5. Raw Data (Filtered)**

| Hostname | SeverityName | Tactic          | Technique | Objective | Month       |
|----------|--------------|-----------------|-----------|-----------|-------------|
| HOST-A   | Critical     | Initial Access  | T1566     | Malware   | June 2025   |
| HOST-B   | High         | Execution       | T1059     | Exploit   | June 2025   |

#### **C. Time-Based Analysis Outputs**

**1. Daily Trends**

| Date       | Month       | Detection Count | Day of Week | Percentage |
|------------|-------------|-----------------|-------------|------------|
| 2025-06-01 | June 2025   | 3               | Sunday      | 3.0%       |
| 2025-06-02 | June 2025   | 5               | Monday      | 5.0%       |
| 2025-07-01 | July 2025   | 4               | Tuesday     | 4.0%       |

**2. Hourly Analysis**

| Hour  | June 2025 | July 2025 | August 2025 | Total | Percentage |
|-------|-----------|-----------|-------------|-------|------------|
| 08:00 | 5         | 6         | 7           | 18    | 18.0%      |
| 09:00 | 8         | 7         | 9           | 24    | 24.0%      |
| 14:00 | 6         | 8         | 10          | 24    | 24.0%      |

**3. Day of Week**

| DayOfWeek | June 2025 | July 2025 | August 2025 | Total | Percentage |
|-----------|-----------|-----------|-------------|-------|------------|
| Monday    | 8         | 9         | 10          | 27    | 27.0%      |
| Tuesday   | 6         | 7         | 8           | 21    | 21.0%      |
| Friday    | 10        | 8         | 12          | 30    | 30.0%      |

---

### **Step 3: Create Pivot Tables and Export**

1. **Navigate to "Pivot Table Builder (Excel-Style)"**

2. **Step 1: Select Analysis Category**
   - Choose: Host Analysis / Detection & Severity / Time-Based Analysis

3. **Step 2: Select Analysis Output**
   - Example: "1. Overview - KEY METRICS"

4. **Step 3: Configure Pivot Fields**
   - **Rows**: Month
   - **Columns**: (leave empty for single series)
   - **Values**: Total Detections
   - **Aggregation**: sum

5. **Choose Chart Type**
   - Bar Chart, Line Chart, etc.

6. **Export**
   - Click "📄 Export to PDF"
   - Click "📊 Download as Excel"

---

## 🎯 Common Use Cases

### **Use Case 1: Executive Summary Report**

**Goal**: Create a 3-month executive summary with key metrics

**Steps**:
1. Upload 3 months of data (15 CSV files total)
2. Go to Pivot Table Builder
3. Select: **Host Analysis** → **Overview - KEY METRICS**
4. Configure:
   - Rows: Month
   - Values: Total Hosts, Total Detections, Unique Users
5. Chart: Bar Chart
6. Export to PDF

**Result**: Clean executive summary showing month-over-month trends

---

### **Use Case 2: Severity Trend Analysis**

**Goal**: Track severity distribution across 3 months

**Steps**:
1. Select: **Detection & Severity** → **Overview - TOP SEVERITIES**
2. The data already has months as columns!
3. No pivot needed - direct export
4. Choose: Stacked Bar Chart
5. Export to PDF

**Result**: Multi-month severity breakdown visualization

---

### **Use Case 3: Host Vulnerability Assessment**

**Goal**: Identify hosts with most detections over 3 months

**Steps**:
1. Select: **Host Analysis** → **Overview - TOP HOSTS WITH DETECTIONS**
2. Data already pivoted by month!
3. Choose: Heatmap
4. Export to PDF

**Result**: Visual identification of problematic hosts

---

### **Use Case 4: Time Pattern Analysis**

**Goal**: Identify peak detection hours

**Steps**:
1. Select: **Time-Based Analysis** → **Hourly Analysis**
2. Data shows all months in columns
3. Choose: Line Chart
4. Export to PDF

**Result**: Time-based pattern identification

---

## 💡 Key Features

### **✅ Multi-Month Support**

All analysis outputs automatically include a **Month column** when processing multiple months:

- **Single Month**: Shows totals and percentages
- **Multiple Months**: Shows month columns + Total + Percentage

### **✅ Automatic Analysis**

No manual processing needed! After uploading CSV files:
1. Templates created automatically
2. Analysis results generated automatically
3. Ready for pivot table building

### **✅ Pre-Built Analysis Outputs**

12 pre-built analysis outputs across 3 categories:
- Host Analysis: 4 outputs
- Detection & Severity: 5 outputs
- Time-Based: 3 outputs

### **✅ Flexible Pivot Building**

- Drag and drop field configuration
- Multiple aggregation functions
- Dynamic filtering
- 6 chart types

### **✅ Professional Exports**

- PDF reports with charts and tables
- Excel workbooks with multiple sheets
- CSV for quick data export

---

## 🔧 Technical Details

### **File Structure**

```
security-dashboard/
├── falcon_generator.py              # Step 1: Upload & Create Templates
├── host_analysis_generator.py       # Step 2A: Generate Host Analysis
├── detection_severity_generator.py  # Step 2B: Generate Detection Analysis
├── time_analysis_generator.py       # Step 2C: Generate Time Analysis
├── pivot_table_builder.py           # Step 3: Pivot & Export
└── app.py                            # Main application
```

### **Session State Variables**

```python
# After Falcon Generator (Step 1)
st.session_state['three_month_trend_data'] = {
    'host_analysis': DataFrame,      # Template
    'detection_analysis': DataFrame, # Template
    'time_analysis': DataFrame       # Template
}

# After Automatic Generation (Step 2)
st.session_state['host_analysis_results'] = {
    'overview_key_metrics': DataFrame,
    'overview_top_hosts': DataFrame,
    'user_analysis': DataFrame,
    'sensor_analysis': DataFrame,
    'raw_data': DataFrame
}

st.session_state['detection_analysis_results'] = {
    'overview_key_metrics': DataFrame,
    'overview_top_severities': DataFrame,
    'geographic_analysis': DataFrame,
    'file_analysis': DataFrame,
    'raw_data_filtered': DataFrame,
    'raw_data': DataFrame
}

st.session_state['time_analysis_results'] = {
    'daily_trends': DataFrame,
    'hourly_analysis': DataFrame,
    'day_of_week': DataFrame,
    'raw_data': DataFrame
}
```

---

## 🆘 Troubleshooting

### **Issue: "No analysis results available"**

**Solution**: Run Falcon Generator first
1. Go to "Falcon Data Generator"
2. Upload files
3. Click "Process All Months and Generate Templates"

### **Issue: "No data available for {analysis}"**

**Solution**: Check if the template has required data
- Geographic Analysis requires Country column
- File Analysis requires FileName column

### **Issue: Analysis shows single month only**

**Solution**: Check `num_months` input
- Ensure you entered 2 or 3 in the Falcon Generator
- Upload correct number of CSV files (10 or 15 files)

---

## 📚 Related Documentation

- [PIVOT_TABLE_GUIDE.md](PIVOT_TABLE_GUIDE.md) - Detailed pivot table usage
- [PIVOT_TABLE_QUICKSTART.md](PIVOT_TABLE_QUICKSTART.md) - Quick start guide

---

**Version:** 2.0
**Last Updated:** 2025-01-06
**Developed by:** Izami Ariff

**Happy Analyzing! 📊**
