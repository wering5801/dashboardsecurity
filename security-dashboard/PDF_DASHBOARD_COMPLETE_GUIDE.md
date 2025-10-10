# PDF Dashboard - Complete Implementation Guide

## ✅ COMPLETED CHANGES

### 1. Gradient Background CSS (DONE)
Already added `.analysis-section` class with gradient in `apply_dashboard_css()`:
```css
.analysis-section {
    background: linear-gradient(135deg, #e8e8e8 0%, #f5f5f5 100%);
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}
```

To use: Wrap each section in `<div class="analysis-section">...</div>`

---

## 🔧 REMAINING TASKS

### 2. B.1 Side-by-Side Layout

**Current (lines 273-374):** Critical boxes, then High chart below

**Change to:**
```python
# B.1 Critical and High Detection Overview - Side by Side
st.markdown('<div class="chart-title">B.1. Critical and High Detection Overview</div>')

if 'critical_high_overview' in detection_data:
    col_critical, col_high = st.columns(2)

    # LEFT: Critical Detections (3 boxes vertically)
    with col_critical:
        st.markdown('<div style="font-size: 12px; font-weight: bold; text-align: center;">Critical Detections</div>')

        for month in months:
            critical_data = detection_data['critical_high_overview'][
                (detection_data['critical_high_overview']['KEY METRICS'] == 'Critical Detections') &
                (detection_data['critical_high_overview']['Month'] == month)
            ]
            count = int(critical_data['Count'].iloc[0]) if not critical_data.empty else 0

            # Smaller card for A4
            st.markdown(f'''
                <div style="background-color: #4db8b8; border-radius: 8px; padding: 12px;
                text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 12px; color: white; font-weight: 600;">{month}</div>
                    <div style="font-size: 32px; color: white; font-weight: bold;">{count}</div>
                    <div style="font-size: 10px; color: white;">Critical</div>
                </div>
            ''', unsafe_allow_html=True)

    # RIGHT: High Detections (independent bar chart)
    with col_high:
        st.markdown('<div style="font-size: 12px; font-weight: bold; text-align: center;">High Detections</div>')

        high_only = detection_data['critical_high_overview'][
            detection_data['critical_high_overview']['KEY METRICS'] == 'High Detections'
        ].copy()

        if not high_only.empty:
            create_chart_with_pivot_logic(
                high_only,
                rows=['KEY METRICS'],
                columns=['Month'],
                values=['Count'],
                chart_type='Bar Chart',
                height=250,  # Reduced for A4
                analysis_key='critical_high_overview',
                use_monthly_colors=True
            )
```

---

### 3. Full-Page Screen Capture & PDF Export

Add at the top after dashboard title (around line 175):

```python
# Screen Capture and PDF Export Button
if st.button("📸 Capture & Export as PDF", type="primary", use_container_width=True):
    st.markdown("""
        <script>
        // Trigger browser print dialog
        window.print();
        </script>
    """, unsafe_allow_html=True)

    st.info("💡 Use your browser's Print dialog (Ctrl+P / Cmd+P) and select 'Save as PDF'")
    st.success("✅ Set paper size to A4 Portrait for best results")
```

**Alternative (better) - Add HTML2Canvas + jsPDF:**

```python
def add_pdf_export_button():
    """Add screen capture and PDF export functionality"""

    # Load required JavaScript libraries
    st.markdown("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

        <script>
        function captureDashboard() {
            const element = document.querySelector('.main');

            html2canvas(element, {
                scale: 2,
                useCORS: true,
                logging: false,
                width: 793,  // A4 width at 96 DPI
                height: 1122  // A4 height at 96 DPI
            }).then(canvas => {
                const imgData = canvas.toDataURL('image/png');
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('p', 'mm', 'a4');

                const imgWidth = 210; // A4 width in mm
                const imgHeight = canvas.height * imgWidth / canvas.width;

                pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
                pdf.save('Falcon_Security_Dashboard.pdf');
            });
        }
        </script>

        <button onclick="captureDashboard()" style="
            background-color: #1f4e5f;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-bottom: 15px;
        ">
            📸 Capture & Export as PDF
        </button>
    """, unsafe_allow_html=True)
```

---

### 4. A4 Portrait Optimization

**Chart Heights - Reduce all:**
- A.1: 350 → **250px**
- A.2, A.3: 350 → **220px**
- A.4: 400 → **250px**
- B.2, B.3: 350 → **220px**
- B.4: 400 → **240px**
- B.5, B.6: 400 → **260px**
- C.1: 450 → **260px**
- C.2, C.3: 400 → **220px**

**Margins - Reduce in `apply_pdf_chart_styling()`:**
```python
margin=dict(
    l=40,  # Reduced from 60
    r=40,  # Reduced from 60
    t=50,  # Reduced from 80
    b=60   # Reduced from 80
)
```

---

### 5. Font Size Optimization for A4

**In `apply_dashboard_css()`:**
```css
.dashboard-title {
    font-size: 14px;  /* Was 16px */
    padding: 12px;    /* Was 15px */
}

.section-header {
    font-size: 12px;  /* Was 14px */
    padding: 8px 15px; /* Was 10px 18px */
}

.chart-title {
    font-size: 9px;   /* Was 11px */
    padding: 6px;     /* Was 8px */
}
```

**In `apply_pdf_chart_styling()` function (around line 590):**
```python
chart.update_layout(
    # Title: Arial 11pt (was 14pt)
    title_font=dict(
        family='Arial',
        size=11,
        color='#333333'
    ),
    # Axes: Arial 9pt (was 12pt)
    xaxis=dict(
        title=existing_xaxis_title,
        title_font=dict(family='Arial', size=9, color='#333333'),
        tickfont=dict(family='Arial', size=8, color='#333333')
    ),
    yaxis=dict(
        title=existing_yaxis_title,
        title_font=dict(family='Arial', size=9, color='#333333'),
        tickfont=dict(family='Arial', size=8, color='#333333')
    ),
    # Legend: Arial 9pt (was 12pt)
    legend=dict(
        font=dict(family='Arial', size=9, color='#333333')
    ),
    font=dict(
        family='Arial',
        size=9,  # Was 12
        color='#333333'
    ),
    margin=dict(
        l=40, r=40, t=50, b=60
    )
)

# Data labels: 9pt (was 12pt)
for trace in chart.data:
    if trace.type == 'bar':
        trace.update(
            textfont=dict(
                family='Arial',
                size=9,  # Was 12
                color='#000000'
            )
        )
```

---

### 6. Wrap Sections in Gradient Background

**For each major section, wrap in analysis-section div:**

```python
# Example for Section A:
st.markdown('<div class="section-header">A. Host Security Analysis</div>')
st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

# ... all A.1, A.2, A.3, A.4 charts ...

st.markdown('</div>', unsafe_allow_html=True)  # Close analysis-section
```

Repeat for sections B and C.

---

## 📋 IMPLEMENTATION CHECKLIST

- [x] 1. Gradient background CSS added
- [ ] 2. B.1 changed to side-by-side layout
- [ ] 3. PDF export button added
- [ ] 4. All chart heights reduced for A4
- [ ] 5. All fonts optimized for A4
- [ ] 6. Margins reduced in chart styling
- [ ] 7. Sections wrapped in gradient divs
- [ ] 8. Test on actual A4 paper size

---

## 🎯 EXPECTED RESULT

- **Gradient grey background** on each analysis section
- **B.1**: Critical (left 3 boxes) | High (right bar chart)
- **PDF Export Button**: One-click capture to PDF
- **A4 Portrait**: Everything fits without scrolling/cutoff
- **Fonts**: Smaller but readable, optimized for print
- **Professional look**: Clean, organized, print-ready

---

## 📝 NOTES

1. Test print preview frequently (Ctrl+P)
2. Adjust chart heights if content still doesn't fit
3. Consider removing chart titles if space is tight
4. Use browser zoom (90%) for better fit if needed
5. Ensure all data labels are visible after size reduction
