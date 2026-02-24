@echo off
echo ============================================
echo  Quarantine Analysis Dashboard Launcher
echo  Developed by Izami Ariff © 2025
echo ============================================
echo.
echo Starting Streamlit server...
echo.
echo Once started, open your browser and go to:
echo   http://localhost:8502
echo.
echo Press Ctrl+C to stop the server
echo.
streamlit run quarantine_analysis_demo.py --server.port 8502
