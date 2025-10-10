import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
import json
import uuid
import matplotlib.pyplot as plt
import os
import tempfile
from matplotlib.backends.backend_pdf import PdfPages

try:
    from three_month_trend_analysis import get_theme_options
except ImportError:
    def get_theme_options():
        return {
            "grid": {"left": "10%", "right": "10%", "bottom": "15%", "containLabel": True},
            "toolbox": {"feature": {"saveAsImage": {}, "dataZoom": {}, "restore": {}}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "dataZoom": [{"type": "inside"}, {"type": "slider"}]
        }

# --- ECharts theme support (load theme JSONs created by apache/echarts-theme-builder) ---
THEMES_DIR = os.path.join(os.path.dirname(__file__), "themes")

def ensure_themes_dir():
    try:
        os.makedirs(THEMES_DIR, exist_ok=True)
    except Exception:
        pass

def list_theme_files():
    ensure_themes_dir()
    try:
        return [f for f in os.listdir(THEMES_DIR) if f.lower().endswith('.json')]
    except Exception:
        return []

def load_theme_file(filename):
    path = os.path.join(THEMES_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def deep_merge(base, override):
    """Recursively merge two dicts. Values in override take precedence."""
    if not isinstance(base, dict):
        return override
    result = dict(base)
    for k, v in (override or {}).items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

# Wrap the imported st_echarts so themes are merged automatically if user selects one in session state
_st_echarts_original = st_echarts
def _st_echarts_with_theme(options=None, height=None, **kwargs):
    # If a theme is selected in session state, load and merge it
    try:
        selected = st.session_state.get('dashboard_selected_theme')
        if selected:
            theme = load_theme_file(selected)
            # Merge theme as base, then options override
            merged = deep_merge(theme or {}, options or {})
        else:
            merged = options or {}
    except Exception:
        merged = options or {}

    # Call original
    return _st_echarts_original(options=merged, height=height, **kwargs)

# Monkey-patch name in module so existing calls to st_echarts(...) use themed wrapper
st_echarts = _st_echarts_with_theme

class DragDropDashboardBuilder:
    def __init__(self):
        self.available_widgets = {
            "charts": {
                "detections_per_month": {
                    "name": "Detections per Month",
                    "type": "detection",
                    "icon": "📊",
                    "category": "Detection Analysis",
                    "description": "Bar chart showing detections count per month",
                    "chart_types": ["bar", "line", "area"]
                },
                "severity_trend": {
                    "name": "Severity Trend",
                    "type": "detection",
                    "icon": "⚠️",
                    "category": "Detection Analysis",
                    "description": "Stacked bar chart showing severity trends",
                    "chart_types": ["bar", "line", "stacked_area"]
                },
                "severity_distribution": {
                    "name": "Severity Distribution",
                    "type": "detection",
                    "icon": "🥧",
                    "category": "Detection Analysis",
                    "description": "Pie chart showing overall severity distribution",
                    "chart_types": ["pie", "donut", "bar"]
                },
                "top_objectives": {
                    "name": "Top Objectives",
                    "type": "detection",
                    "icon": "🎯",
                    "category": "Detection Analysis",
                    "description": "Top N objectives",
                    "chart_types": ["horizontal_bar", "bar", "pie"]
                },
                "top_countries": {
                    "name": "Top Countries",
                    "type": "detection",
                    "icon": "🌍",
                    "category": "Detection Analysis",
                    "description": "Top N countries by detections",
                    "chart_types": ["bar", "horizontal_bar", "pie"]
                },
                "top_files": {
                    "name": "Top Files",
                    "type": "detection",
                    "icon": "📄",
                    "category": "Detection Analysis",
                    "description": "Top N files with most detections",
                    "chart_types": ["horizontal_bar", "bar"]
                },
                "top_tactics": {
                    "name": "Top Tactics",
                    "type": "detection",
                    "icon": "⚔️",
                    "category": "Detection Analysis",
                    "description": "Top N tactics",
                    "chart_types": ["bar", "horizontal_bar"]
                },
                "top_techniques": {
                    "name": "Top Techniques",
                    "type": "detection",
                    "icon": "🔧",
                    "category": "Detection Analysis",
                    "description": "Top N techniques",
                    "chart_types": ["bar", "horizontal_bar"]
                },
                "unique_hosts_per_month": {
                    "name": "Unique Hosts per Month",
                    "type": "host",
                    "icon": "🖥️",
                    "category": "Host Analysis",
                    "description": "Line chart showing unique hosts over time",
                    "chart_types": ["line", "area", "bar"]
                },
                "top_hosts": {
                    "name": "Top N Hosts",
                    "type": "host",
                    "icon": "🏆",
                    "category": "Host Analysis",
                    "description": "Top hosts by detections",
                    "chart_types": ["bar", "horizontal_bar", "pie"]
                },
                "top_users": {
                    "name": "Top Users",
                    "type": "host",
                    "icon": "👥",
                    "category": "Host Analysis",
                    "description": "Top N users with most detections",
                    "chart_types": ["horizontal_bar", "bar", "pie"]
                },
                "platform_distribution": {
                    "name": "Platform Distribution",
                    "type": "host",
                    "icon": "💻",
                    "category": "Host Analysis",
                    "description": "OS platform distribution",
                    "chart_types": ["pie", "donut", "bar"]
                },
                "sensor_versions": {
                    "name": "Sensor Versions",
                    "type": "host",
                    "icon": "🔌",
                    "category": "Host Analysis",
                    "description": "Sensor version distribution",
                    "chart_types": ["bar", "horizontal_bar"]
                },
                "detection_activity_timeline": {
                    "name": "Detection Timeline",
                    "type": "host",
                    "icon": "📅",
                    "category": "Host Analysis",
                    "description": "Detection activity over time",
                    "chart_types": ["line", "area", "bar"]
                },
                "detection_trend_line": {
                    "name": "Detection Trend",
                    "type": "trend",
                    "icon": "📈",
                    "category": "Trend Analysis",
                    "description": "Line chart with trend analysis",
                    "chart_types": ["line", "area", "bar", "scatter"]
                },
                "business_hours_analysis": {
                    "name": "Business Hours Analysis",
                    "type": "time",
                    "icon": "⏰",
                    "category": "Time Analysis",
                    "description": "Business vs after hours detections",
                    "chart_types": ["bar", "pie"]
                },
                "hourly_pattern": {
                    "name": "Hourly Pattern",
                    "type": "time",
                    "icon": "🕐",
                    "category": "Time Analysis",
                    "description": "Hourly detection patterns",
                    "chart_types": ["line", "bar", "area"]
                },
                "weekly_pattern": {
                    "name": "Weekly Pattern",
                    "type": "time",
                    "icon": "📆",
                    "category": "Time Analysis",
                    "description": "Day of week patterns",
                    "chart_types": ["bar", "line"]
                }
            },
            "metrics": {
                "total_detections": {
                    "name": "Total Detections",
                    "type": "metric",
                    "icon": "🏷️",
                    "category": "Metrics",
                    "description": "Metric card showing total detections"
                },
                "unique_hosts": {
                    "name": "Unique Hosts",
                    "type": "metric",
                    "icon": "💻",
                    "category": "Metrics",
                    "description": "Metric card showing total unique hosts"
                }
            },
            "info": {
                "executive_summary": {
                    "name": "Executive Summary",
                    "type": "info",
                    "icon": "📋",
                    "category": "Information",
                    "description": "Text summary of key insights"
                },
                "data_preview": {
                    "name": "Data Preview",
                    "type": "info",
                    "icon": "📊",
                    "category": "Information",
                    "description": "Table preview of the data"
                }
            }
        }

        if 'dashboard_layout' not in st.session_state:
            st.session_state['dashboard_layout'] = {
                "widgets": [],
                "layout": {"columns": 3},
                "settings": {
                    "show_title": True, 
                    "title": "My Custom Dashboard",
                    "colors": {
                        "primary": "#2E8B57",    # SeaGreen
                        "secondary": "#4682B4",  # SteelBlue
                        "accent": "#FFD700",     # Gold
                        "background": "#F0F8FF"  # AliceBlue
                    }
                }
            }

    def render_dashboard_builder(self):
        st.title("🎨 Custom Drag & Drop Report Builder")

        if 'three_month_trend_data' not in st.session_state:
            st.warning("⚠️ No data available. Please use the Falcon Generator to upload and process data first.")
            st.info("💡 Go to 'Falcon Data Generator' in the sidebar, upload your files, and process them to generate the required data.")
            return

        agg = st.session_state['three_month_trend_data']

        # Sidebar for widget library and settings
        with st.sidebar:
            st.header("🔧 Dashboard Builder")

            # Layout Settings
            st.subheader("Layout Settings")
            cols = st.selectbox("Columns:", [1, 2, 3, 4], index=2)
            st.session_state['dashboard_layout']['layout'] = {"columns": cols}

            # Dashboard Settings
            st.subheader("Dashboard Settings")
            show_title = st.checkbox("Show Title", value=st.session_state['dashboard_layout']['settings']['show_title'])
            if show_title:
                title = st.text_input("Dashboard Title", value=st.session_state['dashboard_layout']['settings']['title'])
                st.session_state['dashboard_layout']['settings']['title'] = title
            st.session_state['dashboard_layout']['settings']['show_title'] = show_title

            # Widget Library
            # Color Customization
            st.subheader("🎨 Color Customization")
            with st.expander("Chart Colors", expanded=False):
                colors = st.session_state['dashboard_layout']['settings']['colors']
                new_primary = st.color_picker("Primary Color", colors['primary'])
                new_secondary = st.color_picker("Secondary Color", colors['secondary'])
                new_accent = st.color_picker("Accent Color", colors['accent'])
                new_background = st.color_picker("Background Color", colors['background'])
                
                # Update colors if changed
                colors.update({
                    'primary': new_primary,
                    'secondary': new_secondary,
                    'accent': new_accent,
                    'background': new_background
                })

            # Theme selection / upload
            st.subheader("🎛️ ECharts Themes")
            ensure_themes_dir()
            themes = list_theme_files()
            col1, col2 = st.columns([3, 1])
            with col1:
                theme_choice = st.selectbox("Select theme", options=[""] + themes, index=0, key="_theme_select")
            with col2:
                uploaded = st.file_uploader("Upload (.json)", type=["json"], key="_theme_upload")

            if uploaded is not None:
                try:
                    raw = uploaded.read()
                    if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')

                    # Validate JSON
                    theme_json = json.loads(raw)

                    # Sanitize filename and save pretty JSON
                    theme_name = os.path.basename(uploaded.name)
                    path = os.path.join(THEMES_DIR, theme_name)
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(theme_json, f, indent=2, ensure_ascii=False)

                    st.success(f"Saved theme {theme_name}")
                    st.experimental_rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Uploaded file is not valid JSON: {e}")
                except Exception as e:
                    st.error(f"Failed to save theme: {e}")

            # Apply selection to session state
            if theme_choice:
                st.session_state['dashboard_selected_theme'] = theme_choice
            else:
                st.session_state['dashboard_selected_theme'] = None

            # Export Options
            st.subheader("📋 Export Options")
            if st.button("📄 Export to PDF", type="primary"):
                # Use processed data in this scope
                self.export_to_pdf(agg)

            st.subheader("🎯 Widget Library")

            categories = list(set(widget["category"] for widget_type in self.available_widgets.values() for widget in widget_type.values()))

            for category in categories:
                with st.expander(f"{category}", expanded=False):
                    for widget_group in self.available_widgets.values():
                        for widget_id, widget_info in widget_group.items():
                            if widget_info["category"] == category:
                                if st.button(f"{widget_info['icon']} {widget_info['name']}", key=f"add_{widget_id}", help=widget_info['description']):
                                    self.add_widget(widget_id)

            # Manage Widgets & Chart Style Selection in Sidebar
            st.subheader("📋 Current Widgets")
            if st.session_state['dashboard_layout']['widgets']:
                for i, widget in enumerate(st.session_state['dashboard_layout']['widgets']):
                    widget_info = self.get_widget_info_by_id(widget['widget_id'])
                    if widget_info:
                        with st.expander(f"{widget_info['icon']} {widget_info['name']}", expanded=False):
                            # Chart type selector in sidebar
                            if 'chart_types' in widget_info and len(widget_info['chart_types']) > 1:
                                chart_type = st.selectbox(
                                    "Chart Style",
                                    options=widget_info['chart_types'],
                                    index=widget_info['chart_types'].index(widget['config'].get('chart_type', widget_info['chart_types'][0])),
                                    key=f"sidebar_chart_type_{widget['id']}"
                                )
                                widget['config']['chart_type'] = chart_type
                            
                            # Remove button
                            if st.button("🗑️ Remove", key=f"remove_{i}"):
                                st.session_state['dashboard_layout']['widgets'].pop(i)
                                st.rerun()

                if st.button("🗑️ Clear All Widgets"):
                    st.session_state['dashboard_layout']['widgets'] = []
                    st.rerun()
            else:
                st.info("No widgets added yet. Choose some from the library above!")

        # Main dashboard area
        if st.session_state['dashboard_layout']['settings']['show_title']:
            st.markdown("---")
            st.subheader(st.session_state['dashboard_layout']['settings']['title'])
            st.markdown("---")

        # Render dashboard with widgets
        self.render_dashboard(agg)

    def add_widget(self, widget_id):
        widget_info = self.get_widget_info_by_id(widget_id)
        if widget_info:
            default_chart_type = widget_info.get("chart_types", ["bar"])[0]
            
            widget_config = {
                "id": str(uuid.uuid4()),
                "type": widget_info["type"],
                "widget_id": widget_id,
                "config": {
                    "top_n": 5, 
                    "height": 400, 
                    "title": widget_info["name"],
                    "chart_type": default_chart_type
                }
            }
            st.session_state['dashboard_layout']['widgets'].append(widget_config)
            st.rerun()

    def get_widget_info_by_id(self, widget_id):
        for group in self.available_widgets.values():
            if widget_id in group:
                return group[widget_id]
        return None

    def render_dashboard(self, data):
        if not st.session_state['dashboard_layout']['widgets']:
            st.info("👆 Start building your dashboard by adding widgets from the sidebar!")
            st.markdown("""
            ### How to use:
            1. **Add Widgets**: Click on widgets in the sidebar to add them to your dashboard
            2. **Change Chart Styles**: Expand each widget in the sidebar to select different visualization styles
            3. **Arrange Layout**: Change the number of columns in the sidebar
            4. **View Results**: Your custom dashboard will appear here!
            """)
            return

        layout = st.session_state['dashboard_layout']['layout']
        columns = layout["columns"]
        widgets = st.session_state['dashboard_layout']['widgets']

        for row_start in range(0, len(widgets), columns):
            row_widgets = widgets[row_start:row_start + columns]
            cols = st.columns(columns)

            for col_idx, widget in enumerate(row_widgets):
                with cols[col_idx]:
                    self.render_widget(widget, data)

    def render_widget(self, widget, data):
        widget_info = self.get_widget_info_by_id(widget['widget_id'])
        if not widget_info:
            st.error(f"Unknown widget: {widget['widget_id']}")
            return

        config = widget['config']

        with st.container():
            st.markdown(f"**{widget_info['icon']} {config['title']}**")
            
            try:
                self.render_widget_content(widget['widget_id'], data, config)
            except Exception as e:
                st.error(f"Error rendering {widget_info['name']}: {str(e)}")

    def render_widget_content(self, widget_id, data, config):
        render_methods = {
            "detections_per_month": self.render_detections_per_month,
            "severity_trend": self.render_severity_trend,
            "severity_distribution": self.render_severity_distribution,
            "unique_hosts_per_month": self.render_unique_hosts_per_month,
            "top_hosts": self.render_top_hosts,
            "detection_trend_line": self.render_detection_trend,
            "top_objectives": self.render_top_objectives,
            "top_countries": self.render_top_countries,
            "top_files": self.render_top_files,
            "top_tactics": self.render_top_tactics,
            "top_techniques": self.render_top_techniques,
            "top_users": self.render_top_users,
            "platform_distribution": self.render_platform_distribution,
            "sensor_versions": self.render_sensor_versions,
            "detection_activity_timeline": self.render_detection_activity_timeline,
            "business_hours_analysis": self.render_business_hours_analysis,
            "hourly_pattern": self.render_hourly_pattern,
            "weekly_pattern": self.render_weekly_pattern,
            "total_detections": self.render_total_detections_metric,
            "unique_hosts": self.render_unique_hosts_metric,
            "executive_summary": self.render_executive_summary,
            "data_preview": self.render_data_preview
        }
        
        render_method = render_methods.get(widget_id)
        if render_method:
            render_method(data, config)
        else:
            st.warning(f"Render method for {widget_id} not implemented yet")

    def render_detections_per_month(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Period' not in df.columns:
            st.error("Period column not found")
            return

        det_per_month = df.groupby('Period').size().reset_index(name='Detections')
        chart_type = config.get('chart_type', 'bar')
        
        colors = st.session_state['dashboard_layout']['settings']['colors']
        series_config = {"data": det_per_month['Detections'].tolist(), "itemStyle": {"color": colors['primary']}}
        
        if chart_type == 'bar':
            series_config["type"] = "bar"
        elif chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        elif chart_type == 'area':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["areaStyle"] = {}

        options = {
            **get_theme_options(),
            "xAxis": {"type": "category", "data": det_per_month['Period'].tolist()},
            "yAxis": {"type": "value"},
            "series": [series_config]
        }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_severity_trend(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'SeverityName' not in df.columns or 'Period' not in df.columns:
            st.error("Required columns not found")
            return

        # Calculate severity trends
        sev_trend = df.groupby(['Period', 'SeverityName']).size().unstack(fill_value=0)
        periods = sev_trend.index.tolist()
        severity_levels = sev_trend.columns.tolist()
        
        # Calculate growth rates and trends
        growth_data = []
        for severity in severity_levels:
            counts = sev_trend[severity].tolist()
            if len(counts) > 1:
                growth = ((counts[-1] - counts[0]) / counts[0] * 100) if counts[0] != 0 else 0
                growth_data.append({
                    'Severity': severity,
                    'Growth': growth,
                    'Current': counts[-1],
                    'Previous': counts[0]
                })
        
        chart_type = config.get('chart_type', 'bar')

        series = []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, severity in enumerate(severity_levels):
            series_config = {
                "name": severity,
                "data": sev_trend[severity].tolist(),
                "itemStyle": {"color": colors[i % len(colors)]}
            }
            
            if chart_type == 'bar':
                series_config["type"] = "bar"
                series_config["stack"] = "total"
            elif chart_type == 'line':
                series_config["type"] = "line"
                series_config["smooth"] = True
            elif chart_type == 'stacked_area':
                series_config["type"] = "line"
                series_config["smooth"] = True
                series_config["areaStyle"] = {}
                series_config["stack"] = "total"
            
            series.append(series_config)

        options = {
            **get_theme_options(),
            "xAxis": {"type": "category", "data": periods},
            "yAxis": {"type": "value"},
            "legend": {"data": severity_levels},
            "series": series
        }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_severity_distribution(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'SeverityName' not in df.columns:
            st.error("SeverityName column not found")
            return

        # Calculate severity distribution with percentages
        sev_dist = df['SeverityName'].value_counts().reset_index()
        sev_dist.columns = ['Severity', 'Count']
        total = sev_dist['Count'].sum()
        sev_dist['Percentage'] = (sev_dist['Count'] / total * 100).round(1)
        chart_type = config.get('chart_type', 'pie')

        if chart_type in ['pie', 'donut']:
            radius = "50%" if chart_type == 'donut' else "60%"
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": ["30%", radius] if chart_type == 'donut' else radius,
                    "data": [{"value": int(row['Count']), "name": row['Severity']} for _, row in sev_dist.iterrows()],
                    "label": {"formatter": '{b}: {c} ({d}%)'}
                }]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": sev_dist['Severity'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "bar",
                    "data": sev_dist['Count'].tolist(),
                    "itemStyle": {"color": '#e74c3c'}
                }]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_unique_hosts_per_month(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return

        df = data['host_analysis']
        if 'Period' not in df.columns or 'Hostname' not in df.columns:
            st.error("Required columns not found")
            return

        hosts_per_month = df.groupby('Period')['Hostname'].nunique().reset_index(name='Unique Hosts')
        chart_type = config.get('chart_type', 'line')

        series_config = {"data": hosts_per_month['Unique Hosts'].tolist(), "itemStyle": {"color": '#2ecc71'}}
        
        if chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        elif chart_type == 'area':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["areaStyle"] = {}
        elif chart_type == 'bar':
            series_config["type"] = "bar"

        options = {
            **get_theme_options(),
            "xAxis": {"type": "category", "data": hosts_per_month['Period'].tolist()},
            "yAxis": {"type": "value"},
            "series": [series_config]
        }

        # Create a stable, unique key for this chart instance
        chart_key = f"unique_hosts_chart_{id(config)}"
        
        st_echarts(
            options=options,
            height=f"{config['height']}px",
            key=chart_key
        )

    def render_top_hosts(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return

        df = data['host_analysis']
        host_counts = df.groupby('Hostname').size().reset_index(name='Count').sort_values('Count', ascending=False).head(config['top_n'])
        chart_type = config.get('chart_type', 'bar')

        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": host_counts['Hostname'].tolist()},
                "series": [{"type": "bar", "data": host_counts['Count'].tolist(), "itemStyle": {"color": '#e74c3c'}}]
            }
        elif chart_type == 'bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": host_counts['Hostname'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": host_counts['Count'].tolist(), "itemStyle": {"color": '#e74c3c'}}]
            }
        else:
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": [{"value": int(row['Count']), "name": row['Hostname']} for _, row in host_counts.iterrows()],
                    "label": {"formatter": '{b}: {c}'}
                }]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_detection_trend(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Period' not in df.columns:
            st.error("Period column not found")
            return

        monthly_counts = df.groupby('Period').size().reset_index(name='Count').sort_values('Period')
        chart_type = config.get('chart_type', 'line')

        series_config = {"data": monthly_counts['Count'].tolist(), "itemStyle": {"color": '#3498db'}}
        
        if chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        elif chart_type == 'area':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["areaStyle"] = {}
        elif chart_type == 'bar':
            series_config["type"] = "bar"
        elif chart_type == 'scatter':
            series_config["type"] = "scatter"
            series_config["symbolSize"] = 10

        options = {
            **get_theme_options(),
            "xAxis": {"type": "category", "data": monthly_counts['Period'].tolist()},
            "yAxis": {"type": "value"},
            "series": [series_config]
        }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_top_objectives(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return
        
        df = data['detection_analysis']
        if 'Objective' not in df.columns:
            st.warning("Objective column not found in data")
            return
        
        obj_counts = df['Objective'].value_counts().head(config['top_n']).reset_index()
        obj_counts.columns = ['Objective', 'Count']
        chart_type = config.get('chart_type', 'horizontal_bar')
        
        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": obj_counts['Objective'].tolist()},
                "series": [{"type": "bar", "data": obj_counts['Count'].tolist()}]
            }
        elif chart_type == 'bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": obj_counts['Objective'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": obj_counts['Count'].tolist()}]
            }
        else:
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": [{"value": int(row['Count']), "name": row['Objective']} for _, row in obj_counts.iterrows()]
                }]
            }
        
        st_echarts(options=options, height=f"{config['height']}px")

    def render_top_countries(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return
        
        df = data['detection_analysis']
        if 'Country' not in df.columns:
            st.warning("Country column not found in data")
            return
        
        country_counts = df['Country'].value_counts().head(config['top_n']).reset_index()
        country_counts.columns = ['Country', 'Count']
        chart_type = config.get('chart_type', 'bar')
        
        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": country_counts['Country'].tolist()},
                "series": [{"type": "bar", "data": country_counts['Count'].tolist()}]
            }
        elif chart_type == 'bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": country_counts['Country'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": country_counts['Count'].tolist()}]
            }
        else:
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": [{"value": int(row['Count']), "name": row['Country']} for _, row in country_counts.iterrows()]
                }]
            }
        
        st_echarts(options=options, height=f"{config['height']}px")

    def render_top_files(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return
        
        df = data['detection_analysis']
        if 'FileName' not in df.columns:
            st.warning("FileName column not found in data")
            return
        
        file_counts = df['FileName'].value_counts().head(config['top_n']).reset_index()
        file_counts.columns = ['FileName', 'Count']
        chart_type = config.get('chart_type', 'horizontal_bar')
        
        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": file_counts['FileName'].tolist()},
                "series": [{"type": "bar", "data": file_counts['Count'].tolist()}]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": file_counts['FileName'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": file_counts['Count'].tolist()}]
            }
        
        st_echarts(options=options, height=f"{config['height']}px")
    
    def render_top_tactics(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Tactic' not in df.columns:
            st.warning("Tactic column not found in data")
            return

        # First get the tactics trend for each period
        tactic_trend = df.groupby(['Period', 'Tactic']).size().reset_index(name='Count')
            
        # Get top tactics
        top_tactics = df.groupby('Tactic').size().nlargest(config['top_n']).index.tolist()
            
        # Filter the trend data to only include top tactics
        tactic_trend = tactic_trend[tactic_trend['Tactic'].isin(top_tactics)]
            
        # Pivot the data for easier plotting
        pivot_data = tactic_trend.pivot(index='Period', columns='Tactic', values='Count').fillna(0)
            
        chart_type = config.get('chart_type', 'bar')

        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": pivot_data.columns.tolist()},
                "series": [{
                    "type": "bar",
                    "data": [int(x) for x in pivot_data.iloc[-1]], # Use latest period
                    "itemStyle": {"color": "#32CD32"},
                    "label": {"show": True, "position": "right"}
                }]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": [str(p) for p in pivot_data.index]},
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "name": tactic,
                        "type": "bar",
                        "data": [int(x) for x in pivot_data[tactic].values],
                        "itemStyle": {"color": "#32CD32"},
                        "label": {"show": True, "position": "top"}
                    } for tactic in pivot_data.columns
                ]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_top_techniques(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Technique' not in df.columns:
            st.warning("Technique column not found in data")
            return

        # First get the technique trend for each period
        technique_trend = df.groupby(['Period', 'Technique']).size().reset_index(name='Count')
            
        # Get top techniques
        top_techniques = df.groupby('Technique').size().nlargest(config['top_n']).index.tolist()
            
        # Filter the trend data to only include top techniques
        technique_trend = technique_trend[technique_trend['Technique'].isin(top_techniques)]
            
        # Pivot the data for easier plotting
        pivot_data = technique_trend.pivot(index='Period', columns='Technique', values='Count').fillna(0)
            
        chart_type = config.get('chart_type', 'bar')

        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": pivot_data.columns.tolist()},
                "series": [{
                    "type": "bar",
                    "data": [int(x) for x in pivot_data.iloc[-1]], # Use latest period
                    "itemStyle": {"color": "#4682B4"},
                    "label": {"show": True, "position": "right"}
                }]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": [str(p) for p in pivot_data.index]},
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "name": technique,
                        "type": "bar",
                        "data": [int(x) for x in pivot_data[technique].values],
                        "itemStyle": {"color": "#4682B4"},
                        "label": {"show": True, "position": "top"}
                    } for technique in pivot_data.columns
                ]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_top_users(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return

        df = data['host_analysis']
        if 'UserName' not in df.columns:
            st.warning("UserName column not found in data")
            return

        user_counts = df.groupby('Username').size().reset_index(name='Count').sort_values('Count', ascending=False).head(config['top_n'])
        chart_type = config.get('chart_type', 'horizontal_bar')

        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": user_counts['Username'].tolist()},
                "series": [{"type": "bar", "data": user_counts['Count'].tolist()}]
            }
        elif chart_type == 'bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": user_counts['Username'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": user_counts['Count'].tolist()}]
            }
        else:
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": [{"value": int(row['Count']), "name": row['Username']} for _, row in user_counts.iterrows()]
                }]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_platform_distribution(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return

        df = data['host_analysis']
        if 'OS Version' not in df.columns:
            st.warning("OS Version column not found in data")
            return

        platform_dist = df['OS Version'].value_counts().reset_index()
        platform_dist.columns = ['OS Version', 'Count']
        chart_type = config.get('chart_type', 'pie')

        if chart_type in ['pie', 'donut']:
            radius = "50%" if chart_type == 'donut' else "60%"
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": ["30%", radius] if chart_type == 'donut' else radius,
                    "data": [{"value": int(row['Count']), "name": row['OS Version']} for _, row in platform_dist.iterrows()],
                    "label": {"formatter": '{b}: {c} ({d}%)'}
                }]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": platform_dist['OS Version'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "bar",
                    "data": platform_dist['Count'].tolist(),
                    "itemStyle": {"color": '#9b59b6'}
                }]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_sensor_versions(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return

        df = data['host_analysis']
        if 'SensorVersion' not in df.columns:
            st.warning("SensorVersion column not found in data")
            return

        sensor_counts = df.groupby('SensorVersion').size().reset_index(name='Count').sort_values('Count', ascending=False).head(config['top_n'])
        chart_type = config.get('chart_type', 'bar')

        if chart_type == 'horizontal_bar':
            options = {
                **get_theme_options(),
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": sensor_counts['SensorVersion'].tolist()},
                "series": [{"type": "bar", "data": sensor_counts['Count'].tolist()}]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": sensor_counts['SensorVersion'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": sensor_counts['Count'].tolist()}]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_detection_activity_timeline(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Detect MALAYSIA TIME FORMULA' not in df.columns:
            st.warning("Detection time column not found in data")
            return

        # Convert to datetime and group by date with Malaysia time
        df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
        daily_counts = df.groupby(df['Detect MALAYSIA TIME FORMULA'].dt.date).size().reset_index(name='Count')
        daily_counts = daily_counts.sort_values('Detect MALAYSIA TIME FORMULA')
        chart_type = config.get('chart_type', 'line')

        series_config = {"data": daily_counts['Count'].tolist(), "itemStyle": {"color": '#e67e22'}}

        if chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        elif chart_type == 'area':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["areaStyle"] = {}
        elif chart_type == 'bar':
            series_config["type"] = "bar"

        options = {
            **get_theme_options(),
            "title": {"text": "Detection Activity Over Time"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "xAxis": {
                "type": "category",
                "data": [d.strftime('%Y-%m-%d') for d in daily_counts['Detect MALAYSIA TIME FORMULA']],
                "axisLabel": {"rotate": 45, "interval": "auto"}
            },
            "yAxis": {"type": "value", "name": "Number of Detections"},
            "series": [series_config]
        }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_business_hours_analysis(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Timestamp' not in df.columns:
            st.warning("Timestamp column not found in data")
            return

        # Convert to datetime and determine business hours (9 AM - 5 PM, Monday-Friday)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek

        # Business hours: 9 AM - 5 PM (9-17), Monday-Friday (0-4)
        business_hours = df[(df['Hour'].between(9, 17)) & (df['DayOfWeek'].between(0, 4))].shape[0]
        after_hours = df[~(df['Hour'].between(9, 17)) | ~(df['DayOfWeek'].between(0, 4))].shape[0]

        chart_type = config.get('chart_type', 'bar')

        if chart_type == 'pie':
            options = {
                **get_theme_options(),
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": [
                        {"value": business_hours, "name": "Business Hours"},
                        {"value": after_hours, "name": "After Hours"}
                    ],
                    "label": {"formatter": '{b}: {c} ({d}%)'}
                }]
            }
        else:
            options = {
                **get_theme_options(),
                "xAxis": {"type": "category", "data": ["Business Hours", "After Hours"]},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "bar",
                    "data": [business_hours, after_hours],
                    "itemStyle": {"color": '#27ae60'}
                }]
            }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_hourly_pattern(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Detect MALAYSIA TIME FORMULA' not in df.columns:
            st.warning("Detection time column not found in data")
            return

        # Convert to datetime and group by hour
        df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
        df['Hour'] = df['Detect MALAYSIA TIME FORMULA'].dt.hour
        hourly_counts = df.groupby('Hour').size().reset_index(name='Count')
        chart_type = config.get('chart_type', 'line')

        series_config = {"data": hourly_counts['Count'].tolist(), "itemStyle": {"color": '#8e44ad'}}

        if chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        elif chart_type == 'bar':
            series_config["type"] = "bar"
        elif chart_type == 'area':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["areaStyle"] = {}

        options = {
            **get_theme_options(),
            "xAxis": {"type": "category", "data": [f"{h}:00" for h in hourly_counts['Hour'].tolist()]},
            "yAxis": {"type": "value"},
            "series": [series_config]
        }

        st_echarts(options=options, height=f"{config['height']}px")

    def render_weekly_pattern(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return

        df = data['detection_analysis']
        if 'Detect MALAYSIA TIME FORMULA' not in df.columns:
            st.warning("Detection time column not found in data")
            return

        # Convert to datetime and group by day of week
        df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
        df['Day_of_Week'] = df['Detect MALAYSIA TIME FORMULA'].dt.day_name()
        weekly_counts = df.groupby('Day_of_Week').size().reset_index(name='Count')

        # Order days of week correctly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_counts['Day_of_Week'] = pd.Categorical(weekly_counts['Day_of_Week'], categories=days_order, ordered=True)
        weekly_counts = weekly_counts.sort_values('Day_of_Week')
        chart_type = config.get('chart_type', 'bar')

        series_config = {"data": weekly_counts['Count'].tolist(), "itemStyle": {"color": '#34495e'}}

        if chart_type == 'line':
            series_config["type"] = "line"
            series_config["smooth"] = True
            series_config["symbol"] = "circle"
        else:
            series_config["type"] = "bar"

        options = {
            **get_theme_options(),
            "title": {"text": "Detection Frequency by Day of Week"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": {"type": "category", "data": days_order, "name": "Day of Week"},
            "yAxis": {"type": "value", "name": "Number of Detections"},
            "series": [{
                "name": "Detections",
                "type": "bar",
                "data": weekly_counts['Count'].tolist(),
                "itemStyle": {"color": "#4682B4"},
                "label": {"show": True, "position": "top"}
            }]
        }

        st_echarts(options=options, height=f"{config['height']}px")
    
    def render_total_detections_metric(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return
        total = len(data['detection_analysis'])
        st.metric("Total Detections", f"{total:,}")
    
    def render_unique_hosts_metric(self, data, config):
        if 'host_analysis' not in data or data['host_analysis'].empty:
            st.error("Host analysis data not available")
            return
        unique_hosts = data['host_analysis']['Hostname'].nunique()
        st.metric("Unique Hosts", f"{unique_hosts:,}")
    
    def render_executive_summary(self, data, config):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Key Metrics")
            if 'detection_analysis' in data and not data['detection_analysis'].empty:
                total_detections = len(data['detection_analysis'])
                st.metric("Total Detections", f"{total_detections:,}")

                if 'SeverityName' in data['detection_analysis'].columns:
                    severity_counts = data['detection_analysis']['SeverityName'].value_counts()
                    high_severity = severity_counts.get('High', 0) + severity_counts.get('Critical', 0)
                    st.metric("High/Critical Severity", f"{high_severity:,}")

            if 'host_analysis' in data and not data['host_analysis'].empty:
                unique_hosts = data['host_analysis']['Hostname'].nunique()
                st.metric("Unique Hosts", f"{unique_hosts:,}")

        with col2:
            st.markdown("### 🎯 Top Insights")
            if 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']

                if 'Country' in df.columns:
                    top_country = df['Country'].value_counts().index[0]
                    country_count = df['Country'].value_counts().iloc[0]
                    st.write(f"• Most active country: **{top_country}** ({country_count:,} detections)")

                if 'Objective' in df.columns:
                    top_objective = df['Objective'].value_counts().index[0]
                    objective_count = df['Objective'].value_counts().iloc[0]
                    st.write(f"• Primary objective: **{top_objective}** ({objective_count:,} detections)")

                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                    date_range = f"{df['Timestamp'].min().strftime('%Y-%m-%d')} to {df['Timestamp'].max().strftime('%Y-%m-%d')}"
                    st.write(f"• Data period: **{date_range}**")

            if 'host_analysis' in data and not data['host_analysis'].empty:
                df = data['host_analysis']

                if 'OS Version' in df.columns:
                    top_platform = df['OS Version'].value_counts().index[0]
                    platform_count = df['OS Version'].value_counts().iloc[0]
                    st.write(f"• Most common platform: **{top_platform}** ({platform_count:,} hosts)")
    
    def render_data_preview(self, data, config):
        if 'detection_analysis' not in data or data['detection_analysis'].empty:
            st.error("Detection analysis data not available")
            return
        st.dataframe(data['detection_analysis'].head(10))

    def export_to_pdf(self, data):
        """Export the current dashboard to PDF using screenshots"""
        try:
            import tempfile, base64
            from matplotlib.backends.backend_pdf import PdfPages
            import matplotlib.pyplot as plt
            import os
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.utils import ImageReader
            from io import BytesIO
            from PIL import Image
            import time

            # Create a container for the dashboard-only view
            dashboard_container = st.empty()
            
            # Hide sidebar temporarily for clean screenshot
            st.markdown("""
                <style>
                    section[data-testid="stSidebar"] {display: none;}
                    .stDeployButton {display: none;}
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                </style>
            """, unsafe_allow_html=True)
            
            # Re-render dashboard without sidebar in the container
            with dashboard_container:
                # Add title
                if st.session_state['dashboard_layout']['settings']['show_title']:
                    st.markdown(f"# {st.session_state['dashboard_layout']['settings']['title']}")
                    st.markdown("---")
                
                # Re-render all widgets in the layout
                layout = st.session_state['dashboard_layout']['layout']
                columns = layout["columns"]
                widgets = st.session_state['dashboard_layout']['widgets']
                
                for row_start in range(0, len(widgets), columns):
                    row_widgets = widgets[row_start:row_start + columns]
                    cols = st.columns(columns)
                    for col_idx, widget in enumerate(row_widgets):
                        with cols[col_idx]:
                            self.render_widget(widget, data)
            
            # Small delay to ensure rendering completes
            time.sleep(2)
            
            # Get the screenshot from browser (this requires JavaScript injection)
            js_code = """
                async function captureScreenshot() {
                    let mainContent = document.querySelector('.main');
                    if (!mainContent) return null;
                    
                    try {
                        const canvas = await html2canvas(mainContent, {
                            scale: 2,
                            logging: false,
                            useCORS: true,
                            allowTaint: true
                        });
                        return canvas.toDataURL('image/png');
                    } catch (e) {
                        console.error('Screenshot failed:', e);
                        return null;
                    }
                }
                
                // Execute and return
                await captureScreenshot();
            """
            
            # Inject html2canvas library
            st.markdown(
                '<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>',
                unsafe_allow_html=True
            )
            
            # Get screenshot
            screenshot_b64 = st.components.v1.run_js(js_code)
            
            if screenshot_b64:
                # Decode base64 to image
                img_data = base64.b64decode(screenshot_b64.split(',')[1])
                img = Image.open(BytesIO(img_data))
                
                # Create PDF with screenshot
                pdf_buffer = BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                
                # Calculate aspect ratio and scale
                a4_w, a4_h = A4
                img_w, img_h = img.size
                scale = min(a4_w/img_w, a4_h/img_h) * 0.95  # 95% of page
                
                # Place image centered on page
                w = img_w * scale
                h = img_h * scale
                x = (a4_w - w) / 2
                y = (a4_h - h) / 2
                
                c.drawImage(ImageReader(img), x, y, width=w, height=h)
                c.showPage()
                c.save()
                
                # Offer download
                pdf_bytes = pdf_buffer.getvalue()
                st.download_button(
                    "📥 Download Dashboard PDF",
                    pdf_bytes,
                    "dashboard.pdf",
                    "application/pdf"
                )
                
                st.success("Dashboard PDF generated! Click the download button above to save.")
            else:
                st.error("Failed to capture dashboard screenshot. Please try again.")
            
            # Clean up - restore sidebar
            st.markdown("""
                <style>
                    section[data-testid="stSidebar"] {display: block;}
                    .stDeployButton {display: block;}
                    #MainMenu {visibility: visible;}
                    footer {visibility: visible;}
                </style>
            """, unsafe_allow_html=True)
            
            # Clear the temporary container
            dashboard_container.empty()

        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            # Ensure sidebar is restored on error
            st.markdown("""
                <style>
                    section[data-testid="stSidebar"] {display: block;}
                    .stDeployButton {display: block;}
                    #MainMenu {visibility: visible;}
                    footer {visibility: visible;}
                </style>
            """, unsafe_allow_html=True)

    def render_widget_to_pdf(self, widget, data, pdf):
        """Render a single widget to the PDF using Matplotlib (no Streamlit components).

        This avoids creating Streamlit components while exporting which causes duplicate
        component_instance ID errors. We implement lightweight Matplotlib renderers for
        common widget types; other widgets will show a placeholder text.
        """
        try:
            widget_info = self.get_widget_info_by_id(widget['widget_id'])
            config = widget['config']

            # Use custom colors from settings
            colors = st.session_state['dashboard_layout']['settings']['colors']

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor(colors.get('background', '#ffffff'))
            title = f"{widget_info.get('icon','')} {config.get('title','') }"
            ax.set_title(title)

            wid = widget['widget_id']

            # Detections per month
            if wid == 'detections_per_month' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Period' in df.columns:
                    det_per_month = df.groupby('Period').size().reset_index(name='Detections')
                    ax.bar(det_per_month['Period'].astype(str), det_per_month['Detections'], color=colors.get('primary','#2E8B57'))
                    ax.set_ylabel('Detections')
                    ax.set_xlabel('Period')
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            # Severity trend (stacked)
            elif wid == 'severity_trend' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Period' in df.columns and 'SeverityName' in df.columns:
                    sev_trend = df.groupby(['Period','SeverityName']).size().unstack(fill_value=0)
                    periods = [str(p) for p in sev_trend.index]
                    bottom = None
                    for col in sev_trend.columns:
                        vals = sev_trend[col].values
                        if bottom is None:
                            ax.bar(periods, vals, label=col)
                            bottom = vals
                        else:
                            ax.bar(periods, vals, bottom=bottom, label=col)
                            bottom = bottom + vals
                    ax.legend()
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            # Severity distribution (pie)
            elif wid == 'severity_distribution' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'SeverityName' in df.columns:
                    sev_dist = df['SeverityName'].value_counts()
                    ax.pie(sev_dist.values, labels=sev_dist.index, autopct='%1.1f%%', colors=None)

            # Unique hosts per month
            elif wid == 'unique_hosts_per_month' and 'host_analysis' in data and not data['host_analysis'].empty:
                df = data['host_analysis']
                if 'Period' in df.columns and 'Hostname' in df.columns:
                    hosts_per_month = df.groupby('Period')['Hostname'].nunique().reset_index(name='Unique Hosts')
                    ax.plot(hosts_per_month['Period'].astype(str), hosts_per_month['Unique Hosts'], marker='o', color=colors.get('secondary','#4682B4'))
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            # Top hosts/countries/files - bar chart
            elif wid in ('top_hosts','top_countries','top_files'):
                keycol = 'Hostname' if wid=='top_hosts' else ('Country' if wid=='top_countries' else 'FileName')
                src = 'host_analysis' if wid=='top_hosts' else 'detection_analysis'
                if src in data and not data[src].empty and keycol in data[src].columns:
                    df = data[src]
                    counts = df[keycol].value_counts().head(config.get('top_n',5))
                    ax.barh(counts.index.astype(str)[::-1], counts.values[::-1], color=colors.get('primary','#2E8B57'))
                    ax.set_xlabel('Count')

            # Detection trend
            elif wid == 'detection_trend_line' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Period' in df.columns:
                    monthly_counts = df.groupby('Period').size().reset_index(name='Count').sort_values('Period')
                    ax.plot(monthly_counts['Period'].astype(str), monthly_counts['Count'], marker='o', color=colors.get('accent','#FFD700'))
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            # Hourly pattern
            elif wid == 'hourly_pattern' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Detect MALAYSIA TIME FORMULA' in df.columns:
                    df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
                    df['Hour'] = df['Detect MALAYSIA TIME FORMULA'].dt.hour
                    hourly_counts = df.groupby('Hour').size().reindex(range(24), fill_value=0)
                    ax.bar(hourly_counts.index.astype(str), hourly_counts.values, color=colors.get('primary','#2E8B57'))
                    ax.set_xlabel('Hour')

            # Weekly pattern
            elif wid == 'weekly_pattern' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Detect MALAYSIA TIME FORMULA' in df.columns:
                    df['Detect MALAYSIA TIME FORMULA'] = pd.to_datetime(df['Detect MALAYSIA TIME FORMULA'], dayfirst=True, errors='coerce')
                    df['Day_of_Week'] = df['Detect MALAYSIA TIME FORMULA'].dt.day_name()
                    days_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                    weekly_counts = df['Day_of_Week'].value_counts().reindex(days_order, fill_value=0)
                    ax.bar(days_order, weekly_counts.values, color=colors.get('secondary','#4682B4'))
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            # Business hours analysis
            elif wid == 'business_hours_analysis' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                df = data['detection_analysis']
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                    df['Hour'] = df['Timestamp'].dt.hour
                    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
                    business_hours = df[(df['Hour'].between(9,17)) & (df['DayOfWeek'].between(0,4))].shape[0]
                    after_hours = len(df) - business_hours
                    ax.pie([business_hours, after_hours], labels=['Business Hours','After Hours'], autopct='%1.1f%%')

            # Metrics
            elif wid == 'total_detections' and 'detection_analysis' in data:
                total = len(data['detection_analysis'])
                ax.text(0.5, 0.5, f"Total Detections\n{total}", ha='center', va='center', fontsize=24)
                ax.axis('off')

            elif wid == 'unique_hosts' and 'host_analysis' in data:
                unique_hosts = data['host_analysis']['Hostname'].nunique()
                ax.text(0.5, 0.5, f"Unique Hosts\n{unique_hosts}", ha='center', va='center', fontsize=24)
                ax.axis('off')

            # Data preview
            elif wid == 'data_preview' and 'detection_analysis' in data and not data['detection_analysis'].empty:
                # Render a table snapshot
                tbl = data['detection_analysis'].head(10)
                ax.axis('off')
                table = ax.table(cellText=tbl.values, colLabels=tbl.columns, loc='center', cellLoc='left')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1.5)

            else:
                ax.text(0.5, 0.5, f"Preview not available for {wid}", ha='center', va='center')
                ax.axis('off')

            pdf.savefig(fig)
            plt.close(fig)

        except Exception as e:
            # Avoid crashing PDF export; show warning in Streamlit
            try:
                st.warning(f"Could not render {widget.get('widget_id')} to PDF: {str(e)}")
            except Exception:
                pass

# Main function to be called from app.py
def drag_drop_dashboard_function():
    """Main function to render the drag and drop dashboard builder"""
    builder = DragDropDashboardBuilder()
    builder.render_dashboard_builder()
