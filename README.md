# Falcon Security Dashboard

A comprehensive security analysis dashboard for CrowdStrike Falcon detection data, built with Streamlit.

## Features

- **📊 Interactive Dashboards**: Multiple visualization options including Main Dashboard, PDF Export Layout, and Drag & Drop Dashboard Builder
- **🔍 Data Analysis**: Host security analysis, detection severity tracking, and time-based trend analysis
- **📈 Advanced Charts**: Pivot tables with dynamic filtering, multi-dimensional analysis, and custom chart types
- **🎨 Customizable Themes**: Multiple color themes including Dark, Light, Blue, Purple, and Green
- **📄 PDF Export**: Optimized 2-page A4 portrait layout with professional styling
- **🎯 Smart Filtering**: Top N filtering, per-month analysis, and severity-based sorting

## Dashboard Components

### 1. Main Dashboard Report
- Real-time security metrics
- Interactive visualizations
- Multi-month trend analysis
- Detection severity breakdown

### 2. PDF Export Dashboard
- Optimized for 2-page A4 printing
- Professional layout with page breaks
- Enhanced readability with larger fonts
- Browser-based PDF capture using GoFullPage extension

### 3. Drag & Drop Dashboard Builder
- Custom dashboard creation
- Pivot table functionality
- Dynamic chart configuration
- Export capabilities

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

2. Install dependencies:
```bash
cd security-dashboard
pip install -r requirements.txt
```

## Usage

### Running Locally

```bash
streamlit run security-dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`

### Generating Data

1. Navigate to **Falcon Data Generator** in the sidebar
2. Upload your CrowdStrike Falcon detection CSV files (up to 3 months)
3. Click **Generate Analysis Data**
4. Access the generated analysis in various dashboard views

### Using PDF Export

1. Navigate to **Dashboard - PDF Export Layout**
2. Close the sidebar for clean capture
3. Use browser extension **GoFullPage** to capture as PDF
4. Result: Professional 2-page A4 report

## Project Structure

```
security-dashboard/
├── app.py                          # Main application entry point
├── main_dashboard_report.py        # Main interactive dashboard
├── dashboard_pdf_export.py         # PDF-optimized dashboard (2-page A4)
├── pivot_table_builder.py          # Drag & drop dashboard builder
├── falcon_generator.py             # Data generator from CSV
├── host_analysis_generator.py      # Host security analysis
├── detection_severity_generator.py # Detection severity analysis
├── time_analysis_generator.py      # Time-based trend analysis
├── theme_utils.py                  # Theme management
├── requirements.txt                # Python dependencies
└── themes/                         # Theme configuration files
```

## Color Standardization

The dashboard uses consistent monthly colors across all visualizations:
- **July 2025**: `#70AD47` (Green)
- **August 2025**: `#5B9BD5` (Blue)
- **September 2025**: `#FFC000` (Gold)

Severity colors:
- **Critical**: `#DC143C` (Crimson Red)
- **High**: `#ED7D31` (Orange)
- **Medium**: `#5B9BD5` (Blue)
- **Low**: `#70AD47` (Green)

## Deployment

### Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app**
5. Select your repository
6. Set main file path: `security-dashboard/app.py`
7. Click **Deploy**

### Requirements for Deployment
- GitHub repository must be public or you need a Streamlit Teams account
- All dependencies listed in `requirements.txt`
- Python version specified in `.python-version` (optional)

## Documentation

- [Complete Workflow Guide](security-dashboard/COMPLETE_WORKFLOW_GUIDE.md)
- [Pivot Table Guide](security-dashboard/PIVOT_TABLE_GUIDE.md)
- [Pivot Table Quickstart](security-dashboard/PIVOT_TABLE_QUICKSTART.md)
- [PDF Dashboard Guide](security-dashboard/PDF_DASHBOARD_COMPLETE_GUIDE.md)

## Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive charting library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Matplotlib**: Additional plotting capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here]

## Author

Developed by Izami Ariff © 2025

## Support

For issues and questions, please open an issue in the GitHub repository.
