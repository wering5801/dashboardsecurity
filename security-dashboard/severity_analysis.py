import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from theme_utils import setup_theme
from copy_utils import add_copy_button_to_figure, copy_all_button

def severity_analysis_dashboard():
    # Apply the current theme
    plt_style = setup_theme()
    plt.style.use(plt_style)
    
    # Allow users to customize the report period
    report_period = st.text_input("Report Period", "February 2025", key="severity_report_period")
    
    st.markdown(f"<h1 class='main-header'>Severity Analysis - {report_period}</h1>", unsafe_allow_html=True)
    
    # Instructions for data input
    with st.expander("📋 Data Input Instructions"):
        st.write("""
        Please enter the following data from your reports:
        - Severity distribution (Critical, High, Medium, Low)
        - Severity by system type
        - Severity by detection category
        - Mean time to remediate by severity
        """)
    
    # Input form for severity data
    with st.form("severity_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity Distribution
            st.subheader("Severity Distribution")
            severities = st.text_area(
                "Severities (comma separated)", 
                "Critical, High, Medium, Low",
                help="Enter values separated by commas, with a space after each comma",
                key="severity_levels"
            )
            severity_counts = st.text_area(
                "Counts (comma separated)", 
                "15, 32, 48, 25",
                help="Enter values separated by commas, with a space after each comma",
                key="severity_counts"
            )
            
            # System Types
            st.subheader("System Types")
            systems = st.text_area(
                "Systems (comma separated)", 
                "Servers, Workstations, Network Devices, Cloud Services",
                help="Enter values separated by commas, with a space after each comma",
                key="severity_systems"
            )
            
            # Severity by System
            st.subheader("Critical Severity by System")
            critical_by_system = st.text_area(
                "Counts (comma separated)", 
                "8, 4, 2, 1",
                help="Enter values separated by commas, with a space after each comma",
                key="critical_by_system"
            )
        
        with col2:
            # Detection Categories
            st.subheader("Detection Categories")
            categories = st.text_area(
                "Categories (comma separated)", 
                "Malware, Exploit, Reconnaissance, Lateral Movement, Exfiltration",
                help="Enter values separated by commas, with a space after each comma",
                key="severity_categories"
            )
            
            # High Severity by Category
            st.subheader("High Severity by Category")
            high_by_category = st.text_area(
                "Counts (comma separated)", 
                "12, 9, 5, 4, 2",
                help="Enter values separated by commas, with a space after each comma",
                key="high_by_category"
            )
            
            # Mean Time to Remediate
            st.subheader("Mean Time to Remediate (hours)")
            mttr_values = st.text_area(
                "Hours (comma separated)", 
                "4, 12, 36, 72",
                help="Enter values separated by commas, with a space after each comma",
                key="mttr_values"
            )
        
        submit_button = st.form_submit_button(label="Generate Dashboard")
    
    if submit_button or True:  # For demonstration, always show the dashboard
        # Parse input data
        severity_data = {
            'Severity': [s.strip() for s in severities.split(",")],
            'Count': [int(c.strip()) for c in severity_counts.split(",")]
        }
        
        systems_list = [s.strip() for s in systems.split(",")]
        critical_by_system_values = [int(c.strip()) for c in critical_by_system.split(",")]
        
        critical_by_system_data = {
            'System': systems_list,
            'Count': critical_by_system_values
        }
        
        categories_list = [c.strip() for c in categories.split(",")]
        high_by_category_values = [int(c.strip()) for c in high_by_category.split(",")]
        
        high_by_category_data = {
            'Category': categories_list,
            'Count': high_by_category_values
        }
        
        mttr_data = {
            'Severity': [s.strip() for s in severities.split(",")],
            'Hours': [float(h.strip()) for h in mttr_values.split(",")]
        }
        
        # Create DataFrames
        severity_df = pd.DataFrame(severity_data)
        critical_by_system_df = pd.DataFrame(critical_by_system_data)
        high_by_category_df = pd.DataFrame(high_by_category_data)
        mttr_df = pd.DataFrame(mttr_data)
        
        # Calculate totals
        total_detections = sum(severity_df['Count'])
        critical_count = severity_df[severity_df['Severity'] == 'Critical']['Count'].iloc[0]
        high_count = severity_df[severity_df['Severity'] == 'High']['Count'].iloc[0]
        
        # Keep track of chart IDs for copy functionality
        chart_ids = []
        
        # Display dashboard
        st.markdown("<h2 class='sub-header'>Severity Overview</h2>", unsafe_allow_html=True)
        
        # Severity metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{total_detections}</div>
                <div class='metric-label'>Total Detections</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{critical_count}</div>
                <div class='metric-label'>Critical Detections</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col3:
            critical_pct = 100 * critical_count / total_detections
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{critical_pct:.1f}%</div>
                <div class='metric-label'>Critical Percentage</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Severity Distribution
        st.markdown("<h3>Severity Distribution</h3>", unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
        bars = ax1.bar(severity_df['Severity'], severity_df['Count'], color=colors)
        ax1.set_ylabel('Number of Detections')
        ax1.set_title('Severity Distribution')
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            percentage = f"{100 * height / total_detections:.1f}%"
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{height}\n({percentage})", ha='center', va='bottom')
        
        # Use a unique ID for this chart
        chart_id = "severity_dist_chart"
        chart_ids.append(chart_id)
        
        # Display the figure with a copy button
        st_fig = st.pyplot(fig1)
        st_fig_html = str(st_fig)
        st.markdown(add_copy_button_to_figure(st_fig_html, chart_id), unsafe_allow_html=True)
        
        # Critical Severity by System
        st.markdown("<h3>Critical Severity by System</h3>", unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        bars = ax2.barh(critical_by_system_df['System'][::-1], critical_by_system_df['Count'][::-1], color='#e74c3c')
        ax2.set_xlabel('Number of Critical Detections')
        ax2.set_title('Critical Severity by System Type')
        
        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            percentage = f"{100 * width / critical_count:.1f}%"
            ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f"{width} ({percentage})", va='center')
        
        # Use a unique ID for this chart
        chart_id = "critical_by_system_chart"
        chart_ids.append(chart_id)
        
        # Display the figure with a copy button
        st_fig = st.pyplot(fig2)
        st_fig_html = str(st_fig)
        st.markdown(add_copy_button_to_figure(st_fig_html, chart_id), unsafe_allow_html=True)
        
        # High Severity by Category
        st.markdown("<h3>High Severity by Category</h3>", unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        bars = ax3.barh(high_by_category_df['Category'][::-1], high_by_category_df['Count'][::-1], color='#f39c12')
        ax3.set_xlabel('Number of High Severity Detections')
        ax3.set_title('High Severity by Detection Category')
        
        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            percentage = f"{100 * width / high_count:.1f}%"
            ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f"{width} ({percentage})", va='center')
        
        # Use a unique ID for this chart
        chart_id = "high_by_category_chart"
        chart_ids.append(chart_id)
        
        # Display the figure with a copy button
        st_fig = st.pyplot(fig3)
        st_fig_html = str(st_fig)
        st.markdown(add_copy_button_to_figure(st_fig_html, chart_id), unsafe_allow_html=True)
        
        # Mean Time to Remediate
        st.markdown("<h3>Mean Time to Remediate by Severity</h3>", unsafe_allow_html=True)
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        bars = ax4.bar(mttr_df['Severity'], mttr_df['Hours'], color=colors)
        ax4.set_ylabel('Hours')
        ax4.set_title('Mean Time to Remediate by Severity')
        
        # Add hour labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{height} hrs", ha='center', va='bottom')
        
        # Use a unique ID for this chart
        chart_id = "mttr_chart"
        chart_ids.append(chart_id)
        
        # Display the figure with a copy button
        st_fig = st.pyplot(fig4)
        st_fig_html = str(st_fig)
        st.markdown(add_copy_button_to_figure(st_fig_html, chart_id), unsafe_allow_html=True)
        
        # Add a "Copy All" button
        st.markdown(copy_all_button(chart_ids), unsafe_allow_html=True)
        
        # Risk insights
        st.markdown("<h2 class='sub-header'>Security Insights</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # If critical + high is more than 40% of total
            if (critical_count + high_count) / total_detections > 0.4:
                st.markdown(f"""
                <div class='alert-card'>
                    <h3>High Risk Level</h3>
                    <p>{critical_count + high_count} critical and high severity detections 
                    ({100*(critical_count + high_count)/total_detections:.1f}% of total) 
                    indicate an elevated risk posture requiring immediate attention.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='success-card'>
                    <h3>Manageable Risk Level</h3>
                    <p>Critical and high severity detections are at manageable levels 
                    ({100*(critical_count + high_count)/total_detections:.1f}% of total).</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # If MTTR for critical is over 8 hours
            if mttr_df[mttr_df['Severity'] == 'Critical']['Hours'].iloc[0] > 8:
                st.markdown(f"""
                <div class='alert-card'>
                    <h3>Remediation Time Concern</h3>
                    <p>Mean time to remediate critical detections 
                    ({mttr_df[mttr_df['Severity'] == 'Critical']['Hours'].iloc[0]} hours) 
                    exceeds target of 8 hours.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='success-card'>
                    <h3>Effective Remediation</h3>
                    <p>Critical detections are being remediated within target timeframes 
                    ({mttr_df[mttr_df['Severity'] == 'Critical']['Hours'].iloc[0]} hours).</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Executive summary
        st.markdown("<h2 class='sub-header'>Executive Summary</h2>", unsafe_allow_html=True)
        
        # Generate default summary
        default_summary = f"""
        Analysis of {total_detections} detections during {report_period} shows {critical_count} critical 
        ({100*critical_count/total_detections:.1f}%) and {high_count} high severity 
        ({100*high_count/total_detections:.1f}%) security events.
        
        Servers are the most affected systems for critical detections ({critical_by_system_df.iloc[0]['Count']} instances, 
        {100*critical_by_system_df.iloc[0]['Count']/critical_count:.1f}% of critical), while 
        {high_by_category_df.iloc[0]['Category']} is the leading category for high severity events 
        ({high_by_category_df.iloc[0]['Count']} instances).
        
        Mean time to remediate critical detections is {mttr_df[mttr_df['Severity'] == 'Critical']['Hours'].iloc[0]} hours, 
        {mttr_df[mttr_df['Severity'] == 'Critical']['Hours'].iloc[0] > 8 and 'which exceeds our target of 8 hours' or 'which is within our target of 8 hours'}.
        """
        
        # Let users edit the summary
        edited_summary = st.text_area("Edit Executive Summary", value=default_summary, height=150, key="severity_summary_editor")
        
        # Display the edited summary
        st.markdown(f"<div class='insight-card'>{edited_summary}</div>", unsafe_allow_html=True)