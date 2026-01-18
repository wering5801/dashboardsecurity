# 🛡️ Falcon Security Dashboard

A comprehensive, interactive security analytics dashboard built with Streamlit for analyzing CrowdStrike Falcon detection data, host security metrics, and ticket lifecycle management.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

---

## 🌟 Features

### 🔐 Authentication System
- **Password-protected access** to all dashboard pages
- **Session management** with configurable timeout (default: 60 minutes)
- **Secure password hashing** (SHA-256)
- Professional login UI with user tracking
- Easy credential configuration
- Support for multiple users

### 📊 Main Dashboard Features

#### 1. **Main Dashboard Report**
   - Interactive security analysis with real-time filtering
   - Comprehensive visualizations for all security metrics
   - Export capabilities

#### 2. **PDF Export Dashboard (Single-Page)**
   - Optimized 2-page A4 portrait layout
   - Professional report generation
   - Dynamic section management
   - Print-ready formatting

#### 3. **Falcon Data Generator**
   - CSV import for CrowdStrike Falcon data
   - Support for 1-3 month analysis periods
   - Automatic data processing and template generation
   - Ticket lifecycle data integration

#### 4. **Pivot Table Builder (Excel-Style)**
   - Drag-and-drop interface for custom analysis
   - Dynamic field configuration
   - Multiple chart types (Bar, Line, Area, Pie, Heatmap)
   - Color scheme customization
   - Top N filtering
   - Manual category reordering

### 🎫 Ticket Lifecycle Management
- Track ticket status: **Open**, **Pending**, **On-hold**, **Closed**
- 3-month trend analysis
- CSV upload support
- Customizable color schemes:
  - Closed: Green
  - Open: Red
  - On-hold: Yellow
  - Pending: Grey
- Placeholder data generation

### 🔍 Analysis Categories

#### Host Security Analysis
- Host overview with detection counts
- Top hosts with most detections
- User activity analysis
- Sensor version tracking

#### Detection & Severity Analysis
- Critical and High severity tracking
- Detection trends by severity level
- Country-based analysis
- File and technique analysis
- MITRE ATT&CK tactics mapping

#### Time-Based Analysis
- Daily detection trends
- Hourly distribution patterns
- Day-of-week analysis
- Temporal anomaly detection

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/wering5801/falconreportdashboard.git
   cd falconreportdashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Login**
   - **Username:** `admin`
   - **Password:** `ThisSOCR3port2026`

   ⚠️ **Change the default password immediately!** See [AUTH_CONFIG.md](security-dashboard/AUTH_CONFIG.md)

---

## 📁 Project Structure

```
falconreportdashboard/
├── security-dashboard/
│   ├── app.py                          # Main application entry point
│   ├── auth.py                         # Authentication module
│   ├── falcon_generator.py             # Data import and processing
│   ├── pivot_table_builder.py          # Interactive pivot table builder
│   ├── dashboard_pdf_export.py         # PDF export functionality
│   ├── main_dashboard_report.py        # Main interactive dashboard
│   ├── ticket_lifecycle_generator.py   # Ticket analysis generator
│   ├── host_analysis_generator.py      # Host analysis module
│   ├── detection_severity_generator.py # Detection analysis module
│   ├── time_analysis_generator.py      # Time-based analysis module
│   ├── theme_utils.py                  # Theme configuration
│   ├── AUTHENTICATION_SETUP.md         # Auth quick start guide
│   ├── AUTH_CONFIG.md                  # Detailed auth configuration
│   ├── TICKET_DATA_FORMAT.md           # Ticket data format guide
│   └── sample_ticket_data.csv          # Sample ticket data
├── requirements.txt                     # Python dependencies
├── LICENSE                              # MIT License
└── README.md                            # This file
```

---

## 📖 Documentation

### Configuration Guides
- **[AUTHENTICATION_SETUP.md](security-dashboard/AUTHENTICATION_SETUP.md)** - Quick start for authentication
- **[AUTH_CONFIG.md](security-dashboard/AUTH_CONFIG.md)** - Comprehensive authentication configuration
- **[TICKET_DATA_FORMAT.md](security-dashboard/TICKET_DATA_FORMAT.md)** - Ticket data format specification

### Workflow Guides
- **Falcon Data Import** - See Falcon Data Generator page
- **Custom Dashboard Creation** - See Pivot Table Builder guide
- **PDF Export** - See PDF Export Dashboard documentation

---

## 🔧 Configuration

### Change Default Credentials

1. Open `security-dashboard/auth.py`
2. Modify lines 16-17:
   ```python
   DEFAULT_USERNAME = "your_username"
   DEFAULT_PASSWORD = "YourSecurePassword2026"
   ```
3. Restart the dashboard

### Adjust Session Timeout

1. Open `security-dashboard/auth.py`
2. Modify line 20:
   ```python
   SESSION_TIMEOUT_MINUTES = 120  # Change to desired timeout
   ```

### Add Multiple Users

See [AUTH_CONFIG.md](security-dashboard/AUTH_CONFIG.md) for detailed instructions.

---

## 📊 Data Requirements

### Falcon CSV Files

The dashboard expects the following CSV files from CrowdStrike Falcon:

1. **Host Export File** - Host information and sensor data
2. **Detection Summary Files** (up to 4) - Detection details with:
   - Detection timestamps
   - Severity levels
   - Tactics and techniques
   - File names
   - Country information

### Ticket Data (Optional)

CSV file with required columns:
- `Period` - Month name (e.g., "October 2025")
- `Status` - One of: "Open", "Pending", "On-hold", "Closed"

See [sample_ticket_data.csv](security-dashboard/sample_ticket_data.csv) for an example.

---

## 🎨 Features Showcase

### Color Schemes

#### Severity Colors
- 🔴 Critical: Red
- 🟠 High: Orange
- 🔵 Medium: Blue
- 🟢 Low: Green

#### Ticket Status Colors
- 🟢 Closed: Green
- 🔴 Open: Red
- 🟡 On-hold: Yellow
- ⚫ Pending: Grey

#### Monthly Colors
- 🟢 Month 1: Green (#70AD47)
- 🔵 Month 2: Blue (#5B9BD5)
- 🟡 Month 3: Gold (#FFC000)

---

## 🔒 Security Features

- ✅ Password-protected access
- ✅ Session management with timeout
- ✅ Secure password hashing (SHA-256)
- ✅ Session duration tracking
- ✅ Configurable multi-user support
- ✅ No plaintext password storage

### Security Best Practices

1. **Change default credentials** immediately
2. **Use strong passwords** (12+ characters)
3. **Enable HTTPS** in production
4. **Regular password rotation**
5. **Monitor access logs**
6. **Never commit credentials** to version control

---

## 🚀 Deployment

### Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your GitHub repository
4. Set environment variables for credentials (recommended)

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY security-dashboard/ .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Izami Ariff**

---

## 🙏 Acknowledgments

- CrowdStrike Falcon for security data
- Streamlit for the amazing framework
- Plotly for interactive visualizations
- Pandas for data manipulation

---

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/wering5801/falconreportdashboard/issues)
- Check the documentation in the `/docs` folder
- Review the configuration guides

---

## 🔄 Changelog

### Version 2.0.0 (2025-01-19)

**Major Updates:**
- ✨ Added complete authentication system
- 🎫 Introduced Ticket Lifecycle Analysis
- 📊 Enhanced PDF Export Dashboard
- 🎨 Added ticket status color configuration
- 📚 Comprehensive documentation

**Authentication Features:**
- Password-protected access
- Session management (60-min timeout)
- Secure password hashing
- Professional login UI

**Ticket Lifecycle Features:**
- Status tracking (Open/Pending/On-hold/Closed)
- 3-month trend analysis
- CSV upload support
- Custom color schemes

**Dashboard Enhancements:**
- User configuration integration
- Dynamic section management
- Consistent color schemes
- Improved layout optimization

---

## 🎯 Roadmap

- [ ] Role-based access control (RBAC)
- [ ] Two-factor authentication (2FA)
- [ ] Active Directory/LDAP integration
- [ ] Advanced data filtering
- [ ] Custom alert thresholds
- [ ] Email report scheduling
- [ ] API integration
- [ ] Database backend support

---

**Developed with ❤️ by Izami Ariff © 2025**
