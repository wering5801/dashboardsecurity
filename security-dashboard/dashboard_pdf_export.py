"""
Falcon Security Dashboard - PDF Export Layout
Single-page dashboard matching PDF export format
Uses exact chart logic from pivot_table_builder.py with PDF styling
Developed by Izami Ariff © 2025
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any

# Import the perfected chart creation function from pivot_table_builder
import sys
import os
sys.path.append(os.path.dirname(__file__))
from pivot_table_builder import create_pivot_chart, create_pivot_table

# ============================================
# COLOR SCHEMES (Same as pivot_table_builder)
# ============================================

MONTHLY_COLORS = {
    'month_1': '#70AD47',  # Green (oldest)
    'month_2': '#5B9BD5',  # Blue (middle)
    'month_3': '#FFC000'   # Gold (latest)
}

SEVERITY_COLORS = {
    'Critical': '#DC143C',  # Crimson Red
    'High': '#ED7D31',      # Orange
    'Medium': '#5B9BD5',    # Blue
    'Low': '#70AD47'        # Green
}

# PDF Styling colors
SECTION_HEADER_COLOR = '#1f4e5f'  # Dark teal
PAGE_BACKGROUND = '#f0f0f0'       # Light gray
CHART_BACKGROUND = '#ffffff'      # White
BORDER_COLOR = '#d0d0d0'          # Light gray border


# ============================================
# CSS STYLING
# ============================================

def apply_dashboard_css():
    """Apply custom CSS for PDF-style dashboard layout optimized for A4"""
    st.markdown("""
        <style>
        /* Page background */
        .main {
            background-color: #f0f0f0;
        }

        /* Analysis section with gradient background */
        .analysis-section {
            background: transparent;
            border: none;
            border-radius: 0px;
            padding: 0px;
            margin-bottom: 8px;
            box-shadow: none;
        }

        /* Section headers */
        .section-header {
            background-color: #1f4e5f;
            color: white;
            padding: 5px 10px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 4px 4px 0 0;
            margin-top: 8px;
            margin-bottom: 3px;
            font-family: Arial, sans-serif;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        /* Page break control - Section A completes on Page 1 */
        .page-break-after {
            page-break-after: always;
            break-after: always;
        }

        /* Prevent breaking inside sections B partial */
        .no-page-break {
            page-break-inside: avoid;
            break-inside: avoid;
        }

        /* Chart containers */
        .chart-container {
            background-color: white;
            border: 2px solid #d0d0d0;
            border-radius: 5px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Chart title - optimized for 2-page A4 */
        .chart-title {
            font-family: Arial, sans-serif;
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 3px;
            margin-top: 3px;
            color: #333;
            background: linear-gradient(135deg, #e8e8e8 0%, #f5f5f5 100%);
            padding: 5px;
            border: none;
            border-radius: 3px;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        /* Dashboard title - optimized for 2-page A4 */
        .dashboard-title {
            background-color: #1f4e5f;
            color: white;
            padding: 8px;
            font-size: 13px;
            font-weight: bold;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 8px;
            font-family: Arial, sans-serif;
        }

        /* Remove default streamlit padding - optimized for 2-page A4 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0.8rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
            max-width: 100%;
        }

        /* Hide streamlit elements for clean PDF */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Print optimization for 2-page A4 */
        @media print {
            @page {
                size: A4 portrait;
                margin: 12mm;
            }
            body {
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }
            .page-break-after {
                page-break-after: always;
            }
        }

        /* Streamlit column gap - more breathing room for 2 pages */
        [data-testid="column"] {
            padding: 0px 6px !important;
        }

        /* Sidebar collapse/expand toggle button — styled icon */
        [data-testid="collapsedControl"] {
            background-color: #1f4e5f !important;
            border-radius: 50% !important;
            width: 28px !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25) !important;
            top: 50% !important;
        }
        [data-testid="collapsedControl"] svg {
            stroke: #ffffff !important;
            fill: none !important;
            width: 14px !important;
            height: 14px !important;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================
# EXECUTIVE SUMMARY SECTION
# ============================================

def _exec_card(label, body, border='#1f4e5f', label_color='#1f4e5f'):
    """Return a single finding card as an HTML string — all inline, no orphaned tags."""
    return (
        f'<div style="margin-bottom:12px;padding:14px 16px;background:#ffffff;'
        f'border-left:3px solid {border};border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
        f'<span style="font-size:13px;font-weight:700;color:{label_color};">{label}</span>'
        f'<span style="font-size:13px;color:#374151;line-height:1.7;"> {body}</span>'
        f'</div>'
    )

def _exec_rec(priority, action, detail, badge_color):
    """Return a single recommendation row as an HTML string."""
    return (
        f'<div style="margin-bottom:10px;padding:12px 14px;background:#ffffff;'
        f'border:1px solid #e5e7eb;border-radius:5px;display:flex;align-items:flex-start;gap:12px;">'
        f'<div style="background:{badge_color};color:#fff;font-size:10px;font-weight:700;'
        f'padding:3px 10px;border-radius:3px;white-space:nowrap;margin-top:1px;">{priority}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:3px;">{action}</div>'
        f'<div style="font-size:12px;color:#4b5563;line-height:1.6;">{detail}</div>'
        f'</div></div>'
    )

def _analyze_resolution(raw_monthly_detections):
    """
    Analyse Resolution column in each month's raw detection DataFrame.
    Returns (stats_dict, sorted_months, latest_month) where stats_dict is keyed by month name:
      {
        'has_data':      bool,   # False if month missing or no Resolution column
        'empty':         bool,   # True if all non-in_progress rows have blank Resolution
        'total':         int,
        'in_progress':   int,
        'false_positive':int,
        'true_positive': int,
      }
    """
    _mo = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
           'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    def _ms(m):
        p = str(m).split()
        return (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999, _mo.get(p[0], 99))

    sorted_months = sorted(raw_monthly_detections.keys(), key=_ms)
    stats = {}

    for month in sorted_months:
        df = raw_monthly_detections.get(month)
        if df is None or df.empty or 'Resolution' not in df.columns:
            stats[month] = {'has_data': False}
            continue

        has_status = 'Status' in df.columns
        if has_status:
            in_prog_mask = df['Status'].astype(str).str.strip().str.lower() == 'in_progress'
        else:
            in_prog_mask = pd.Series([False] * len(df), index=df.index)

        in_prog_count = int(in_prog_mask.sum())
        rest = df[~in_prog_mask].copy()
        res_vals = rest['Resolution'].astype(str).str.strip().str.lower()
        blank = res_vals.isin(['', 'nan', 'none', '--', 'n/a'])
        non_blank = res_vals[~blank]

        if len(rest) > 0 and len(non_blank) == 0:
            stats[month] = {
                'has_data': True, 'empty': True,
                'total': len(df), 'in_progress': in_prog_count,
                'false_positive': 0, 'true_positive': 0,
            }
            continue

        fp = int((res_vals == 'false_positive').sum())
        tp = int((res_vals == 'true_positive').sum())
        stats[month] = {
            'has_data': True, 'empty': False,
            'total': len(df), 'in_progress': in_prog_count,
            'false_positive': fp, 'true_positive': tp,
        }

    latest = sorted_months[-1] if sorted_months else None
    return stats, sorted_months, latest


def _insight_box(text):
    """Render a compact data-driven insight callout below a chart. Call inside a Streamlit render context."""
    st.markdown(
        f'<div style="background:#f0f9ff;border-left:3px solid #1f4e5f;border-radius:4px;'
        f'padding:10px 14px;margin:4px 0 14px 0;font-size:12.5px;color:#1e3a5f;line-height:1.7;">'
        f'<span style="font-weight:700;letter-spacing:0.5px;text-transform:uppercase;font-size:10px;'
        f'color:#6b7280;">Key Finding &nbsp;&#9654;&nbsp; </span>{text}</div>',
        unsafe_allow_html=True
    )


def render_executive_summary(ticket_data, host_data, detection_data, time_data, num_months, section_letter='E'):
    """
    Generate Executive Summary Report — fully data-driven from actual analysis results.
    """
    st.markdown(f'<div class="section-header">{section_letter}. Executive Summary Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

    # Shared CSS for this section only
    st.markdown("""
    <style>
    .exec-section-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #6b7280;
        margin: 20px 0 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Derive actual month names ─────────────────────────────────────────────
    actual_months = []
    if detection_data and 'severity_trend' in detection_data:
        sev_df = detection_data['severity_trend']
        if 'Month' in sev_df.columns:
            _mo = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                   'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
            def _ms(m):
                p = str(m).split()
                return (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999, _mo.get(p[0],99) if p else 99)
            actual_months = sorted(sev_df['Month'].dropna().unique().tolist(), key=_ms)

    period_text  = ' → '.join(actual_months) if actual_months else f"{num_months}-month period"
    month_range  = (f"{actual_months[0]} to {actual_months[-1]}" if len(actual_months) > 1
                    else (actual_months[0] if actual_months else period_text))

    # ── Pull key numbers ──────────────────────────────────────────────────────
    total_det_overview = 0
    unique_hosts_overview = 0
    if detection_data and 'severity_trend' in detection_data:
        total_det_overview = int(detection_data['severity_trend']['Count'].sum())
    # Use detection-based unique host count (same source as B.1)
    if host_data and 'raw_data' in host_data and not host_data['raw_data'].empty and 'Hostname' in host_data['raw_data'].columns:
        unique_hosts_overview = host_data['raw_data']['Hostname'].nunique()
    elif host_data and 'overview_key_metrics' in host_data:
        _om2 = host_data['overview_key_metrics']
        if 'KEY METRICS' in _om2.columns and 'Count' in _om2.columns:
            _th2 = _om2[_om2['KEY METRICS'] == 'Total Hosts']['Count']
            unique_hosts_overview = int(_th2.max()) if not _th2.empty else 0

    # Pre-compute numbers used in both Overview and Assessment
    _crit_ov, _high_ov, _med_ov, _low_ov, _hp_pct_ov = 0, 0, 0, 0, 0.0
    if detection_data and 'severity_trend' in detection_data:
        _svdf_ov = detection_data['severity_trend']
        if not _svdf_ov.empty and 'SeverityName' in _svdf_ov.columns:
            _sd = _svdf_ov.groupby('SeverityName')['Count'].sum()
            _crit_ov = int(_sd.get('Critical', 0))
            _high_ov = int(_sd.get('High', 0))
            _med_ov  = int(_sd.get('Medium', 0))
            _low_ov  = int(_sd.get('Low', 0))
            _hp_pct_ov = (_crit_ov + _high_ov) / total_det_overview * 100 if total_det_overview > 0 else 0.0

    _top_host_ov, _top_host_cnt_ov = '', 0
    if host_data and 'overview_top_hosts' in host_data:
        _thdf_ov = host_data['overview_top_hosts']
        if not _thdf_ov.empty and 'TOP HOSTS WITH MOST DETECTIONS' in _thdf_ov.columns:
            _th_series = _thdf_ov.groupby('TOP HOSTS WITH MOST DETECTIONS')['Count'].sum()
            _top_host_ov = _th_series.idxmax()
            _top_host_cnt_ov = int(_th_series.max())

    _outdated_ov, _latest_month_ov = 0, ''
    if host_data and 'sensor_analysis' in host_data:
        _sdf_ov = host_data['sensor_analysis']
        if not _sdf_ov.empty and 'Status' in _sdf_ov.columns and 'Month' in _sdf_ov.columns:
            _s_mo_ov = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                        'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
            def _sms_ov(m):
                p = str(m).split()
                return (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999, _s_mo_ov.get(p[0],99))
            _sm_ov = sorted(_sdf_ov['Month'].dropna().unique().tolist(), key=_sms_ov)
            _latest_month_ov = _sm_ov[-1] if _sm_ov else ''
            if _latest_month_ov:
                _ldf_ov = _sdf_ov[_sdf_ov['Month'] == _latest_month_ov]
                # Count UNIQUE outdated hosts (not detection rows) to match B.4a card count
                _sv_ov_lkp = {str(r['Sensor Version']): r['Status'] for _, r in _ldf_ov.iterrows()}
                _det_raw_ov = host_data.get('raw_data', pd.DataFrame())
                if not _det_raw_ov.empty and 'Hostname' in _det_raw_ov.columns and 'Sensor Version' in _det_raw_ov.columns:
                    _mc_ov = 'Month' if 'Month' in _det_raw_ov.columns else 'Period'
                    _lm_ov = _det_raw_ov[_det_raw_ov[_mc_ov] == _latest_month_ov][['Hostname', 'Sensor Version']].drop_duplicates('Hostname')
                    _outdated_ov = int((_lm_ov['Sensor Version'].astype(str).map(_sv_ov_lkp) == 'Outdated').sum())
                else:
                    _outdated_ov = int(_ldf_ov[_ldf_ov['Status'] == 'Outdated']['Host Count'].sum())

    _top_tactic_ov, _top_tactic_cnt_ov = '', 0
    if detection_data and 'tactics_by_severity' in detection_data:
        _tdf_ov = detection_data['tactics_by_severity']
        if not _tdf_ov.empty and 'Tactic' in _tdf_ov.columns:
            _t_series = _tdf_ov.groupby('Tactic')['Count'].sum()
            _top_tactic_ov = _t_series.idxmax()
            _top_tactic_cnt_ov = int(_t_series.max())

    _peak_hour_str_ov, _peak_hour_int_ov, _peak_cnt_ov = '', 0, 0
    if time_data and 'hourly_analysis' in time_data:
        _hdf_ov = time_data['hourly_analysis']
        if not _hdf_ov.empty and 'Hour' in _hdf_ov.columns and 'Detection Count' in _hdf_ov.columns:
            _htot_ov = _hdf_ov.groupby('Hour')['Detection Count'].sum()
            if len(_htot_ov):
                _peak_hour_str_ov = str(_htot_ov.idxmax())
                try: _peak_hour_int_ov = int(_peak_hour_str_ov.split(':')[0])
                except: _peak_hour_int_ov = 0
                _peak_cnt_ov = int(_htot_ov.max())

    summary_keys = []
    _tk_total_ov, _tk_resolved_ov, _tk_pending_ov, _tk_rate_ov, _tk_latest_ov = 0, 0, 0, 0.0, ''
    if ticket_data:
        summary_keys = sorted([k for k in ticket_data.keys() if k.startswith('ticket_summary_')])
        if summary_keys:
            _ls_ov = ticket_data[summary_keys[-1]]
            _tk_latest_ov = summary_keys[-1].replace('ticket_summary_', '').replace('_', ' ')
            _tk_total_ov    = _ls_ov.get('total_alerts', 0)
            _tk_resolved_ov = _ls_ov.get('alerts_resolved', 0)
            _tk_pending_ov  = _ls_ov.get('alerts_pending', 0)
            _tk_rate_ov = (_tk_resolved_ov / _tk_total_ov * 100) if _tk_total_ov > 0 else 0.0

    # ── OVERVIEW BOX ─────────────────────────────────────────────────────────
    _avg_per_host = f"{total_det_overview / unique_hosts_overview:.1f}" if unique_hosts_overview > 0 else 'N/A'
    _sev_summary = ', '.join(f"{v} {k}" for k, v in [('Critical', _crit_ov), ('High', _high_ov), ('Medium', _med_ov), ('Low', _low_ov)] if v > 0)
    st.markdown(
        f'<div style="background:#f8fafc;border-left:4px solid #1f4e5f;border-radius:5px;'
        f'padding:18px 20px;margin-bottom:20px;">'
        f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        f'color:#6b7280;margin-bottom:8px;">Executive Overview</div>'
        f'<div style="font-size:14px;color:#111827;line-height:1.9;">'
        f'This report covers the period <strong>{period_text}</strong> ({num_months} month{"s" if num_months > 1 else ""}). '
        f'A total of <strong>{total_det_overview:,} detections</strong> were recorded'
        f'{f" across <strong>{unique_hosts_overview} monitored device(s)</strong>, averaging <strong>{_avg_per_host} alerts per device</strong>" if unique_hosts_overview > 0 else ""}. '
        f'{"Severity breakdown: " + _sev_summary + f" — high-priority (Critical + High) represent <strong>{_hp_pct_ov:.1f}%</strong> of all detections." if _sev_summary else ""}'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ── RECOMMENDED ACTIONS ───────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        'color:#6b7280;margin:24px 0 12px 0;">Recommended Actions</div>',
        unsafe_allow_html=True
    )

    recs = []

    if ticket_data and summary_keys:
        if _tk_pending_ov > 0:
            recs.append(_exec_rec('HIGH', 'Close Pending Tickets',
                f'{_tk_pending_ov} ticket(s) still open as of {_tk_latest_ov}. Assign these to the responsible team and aim to close before the next reporting cycle.',
                '#991b1b'))
        pk = [k for k in ticket_data.keys() if k.startswith('request_severity_pivot_')]
        if pk:
            lp = ticket_data[sorted(pk)[-1]]
            if not lp.empty:
                open_s = ['open', 'pending', 'on-hold', 'in_progress']
                pr = lp[lp['Status'].isin(open_s)] if 'Status' in lp.columns else pd.DataFrame()
                if not pr.empty:
                    pc2 = int(pr['Critical'].sum()) if 'Critical' in pr.columns else 0
                    if pc2 > 0:
                        recs.append(_exec_rec('CRITICAL', 'Act on Open Critical Tickets',
                            f'{pc2} Critical ticket(s) remain open. These should be treated as the highest priority — loop in senior team members and do not wait for the next cycle.',
                            '#7f1d1d'))

    if _top_host_ov:
        recs.append(_exec_rec('HIGH', f'Review Activity on {_top_host_ov}',
            f'This device recorded the most alerts ({_top_host_cnt_ov} detections). Recent logins, running programs, and outbound connections on this endpoint should be checked to see if the alerts are real threats.',
            '#b45309'))

    if _outdated_ov > 0:
        recs.append(_exec_rec('MEDIUM', 'Update Falcon Sensors on Outdated Devices',
            f'{_outdated_ov} device(s) as of {_latest_month_ov} are running an older sensor version. An outdated sensor may not detect newer attack methods — update these as soon as possible.',
            '#1f4e5f'))

    if _top_tactic_ov:
        recs.append(_exec_rec('MEDIUM', f'Review "{_top_tactic_ov}" Activity',
            f'This was the most common attack pattern across the period ({_top_tactic_cnt_ov} occurrences). Existing detection rules and access controls should be reviewed to ensure this type of behaviour is being caught and blocked effectively.',
            '#1f4e5f'))

    recs.append(_exec_rec('ONGOING', 'Maintain Monthly Review Cadence',
        f'{month_range} serves as the baseline for the next reporting period. Keeping a monthly review habit helps catch issues early before they grow into bigger problems.',
        '#374151'))

    st.markdown(''.join(recs), unsafe_allow_html=True)

    # ── PROFESSIONAL ASSESSMENT ───────────────────────────────────────────────
    _pa_parts = []

    # ── Resolution-first: determine latest month verdict ──────────────────────
    _pa_raw_monthly = st.session_state.get('raw_monthly_detections', {})
    _pa_res_stats, _pa_res_months, _pa_res_latest = _analyze_resolution(_pa_raw_monthly) if _pa_raw_monthly else ({}, [], None)

    _pa_latest_tp = 0
    _pa_latest_fp = 0
    _pa_latest_ip = 0
    _pa_is_fp_month = False
    _pa_has_res = False

    if _pa_res_latest:
        _pa_rs = _pa_res_stats.get(_pa_res_latest, {})
        if _pa_rs.get('has_data') and not _pa_rs.get('empty'):
            _pa_has_res = True
            _pa_latest_tp = _pa_rs['true_positive']
            _pa_latest_fp = _pa_rs['false_positive']
            _pa_latest_ip = _pa_rs['in_progress']
            _pa_is_fp_month = (_pa_latest_tp == 0 and _pa_latest_fp > 0)

    # Month-on-month detection volume trend
    _pa_monthly_vols = {}
    if detection_data and 'severity_trend' in detection_data:
        _sv_pa = detection_data['severity_trend']
        if not _sv_pa.empty and 'Month' in _sv_pa.columns:
            _pa_monthly_vols = _sv_pa.groupby('Month')['Count'].sum().to_dict()

    _pa_vol_parts = ', '.join(
        f"<strong>{_m}</strong>: {int(_c):,}" for _m, _c in sorted(
            _pa_monthly_vols.items(),
            key=lambda x: (
                (lambda p: (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999,
                            {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                             'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}.get(p[0],99))
                )(str(x[0]).split())
            )
        )
    ) if _pa_monthly_vols else ''

    # Trend direction (latest vs previous) — must use chronologically sorted order, not raw dict order
    _pa_mo_order = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                    'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    def _pa_ms(m):
        p = str(m).split()
        return (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999, _pa_mo_order.get(p[0], 99))
    _pa_vol_list = [_pa_monthly_vols[_m] for _m in sorted(_pa_monthly_vols.keys(), key=_pa_ms)]
    _pa_trend = ''
    if len(_pa_vol_list) >= 2:
        _diff = _pa_vol_list[-1] - _pa_vol_list[-2]
        _pct_diff = abs(_diff) / _pa_vol_list[-2] * 100 if _pa_vol_list[-2] > 0 else 0
        if _diff > 0:
            _pa_trend = f"Detection volume in {_pa_res_latest or actual_months[-1] if actual_months else 'the latest month'} <strong>increased by {abs(int(_diff))} ({_pct_diff:.0f}%)</strong> compared to the previous month."
        elif _diff < 0:
            _pa_trend = f"Detection volume in {_pa_res_latest or actual_months[-1] if actual_months else 'the latest month'} <strong>decreased by {abs(int(_diff))} ({_pct_diff:.0f}%)</strong> compared to the previous month."
        else:
            _pa_trend = f"Detection volume remained consistent month-on-month."

    # Opening: resolution verdict for latest month
    if _pa_has_res and _pa_is_fp_month:
        _pa_parts.append(
            f"For <strong>{_pa_res_latest}</strong>, all <strong>{_pa_latest_fp}</strong> assessed detection(s) were confirmed <strong>false positive</strong> — "
            f"meaning no real security threats were identified this month. "
            + (f"<strong>{_pa_latest_ip}</strong> detection(s) remain under investigation and will be reported once resolved. " if _pa_latest_ip > 0 else "")
        )
    elif _pa_has_res and _pa_latest_tp > 0:
        _pa_parts.append(
            f"For <strong>{_pa_res_latest}</strong>, <strong>{_pa_latest_tp} true positive</strong> threat(s) were confirmed out of "
            f"{_pa_rs.get('total', 0)} total detection(s). The assessment below focuses on these confirmed threats. "
            + (f"<strong>{_pa_latest_ip}</strong> detection(s) are still under investigation. " if _pa_latest_ip > 0 else "")
        )

    # Month-on-month volume comparison
    if _pa_vol_parts:
        _pa_parts.append(
            f"Detection volumes across {month_range}: {_pa_vol_parts}. "
            + (_pa_trend + " " if _pa_trend else "")
        )
    elif total_det_overview > 0:
        _pa_parts.append(f"<strong>{total_det_overview:,}</strong> total detection(s) recorded across {month_range}. ")

    # If false positive month, no need to deep-dive severity/host/tactic — state it clearly
    if _pa_has_res and _pa_is_fp_month and _pa_latest_ip == 0:
        _pa_parts.append(
            f"As all detections this period were resolved as false positive, no active threats require escalation at this time. "
            f"The figures reported (severity, host counts, tactics) reflect the full detection volume but do not represent confirmed attacks. "
        )
    else:
        # Severity signal — focus on true positives if available, otherwise full dataset
        if _crit_ov > 0:
            _pa_parts.append(
                f"<strong>{_crit_ov} Critical-severity</strong> detection(s) were recorded — in Falcon, Critical alerts are the most serious and usually mean an active attack is happening or very close to it. "
                f"Together with <strong>{_high_ov} High</strong> alerts, these high-priority items make up <strong>{_hp_pct_ov:.1f}%</strong> of all detections. "
            )
        elif _high_ov > 0:
            _pa_parts.append(
                f"No Critical detections were observed. <strong>{_high_ov} High-severity</strong> alert(s) were recorded — these are signs of potential threats and should be looked into. "
            )

        # Top endpoint
        if _top_host_ov:
            _pa_parts.append(
                f"<strong>{_top_host_ov}</strong> recorded the highest alert count with <strong>{_top_host_cnt_ov} detection(s)</strong>. "
                f"When one machine keeps getting alerts, it usually means something is not yet fixed on that endpoint, or it is being actively targeted. "
            )

        # Sensor compliance
        if _outdated_ov > 0 and _latest_month_ov:
            _pa_parts.append(
                f"As of {_latest_month_ov}, <strong>{_outdated_ov} device(s)</strong> are on an outdated Falcon sensor — "
                f"an outdated sensor may not catch newer attack methods, so those machines have weaker coverage than the rest. "
            )

        # Top tactic
        if _top_tactic_ov:
            _pa_parts.append(
                f"The most recurring attack pattern observed was <strong>{_top_tactic_ov}</strong> ({_top_tactic_cnt_ov} occurrences). "
                f"Seeing the same attack type show up repeatedly usually means the current defenses are not fully stopping it yet. "
            )

    # Ticket resolution (always included if available)
    if _tk_total_ov > 0:
        if _tk_rate_ov >= 90:
            _grade_pa = "excellent — the team is keeping pace with the workload effectively"
        elif _tk_rate_ov >= 75:
            _grade_pa = "solid, though response speed can still be improved"
        elif _tk_rate_ov >= 60:
            _grade_pa = "moderate — capacity may need to be reviewed"
        else:
            _grade_pa = "below target — a backlog is building and requires immediate attention"
        _pa_parts.append(
            f"Ticket resolution as of {_tk_latest_ov} stands at <strong>{_tk_resolved_ov}/{_tk_total_ov} ({_tk_rate_ov:.0f}%)</strong> — {_grade_pa}."
            + (f" <strong>{_tk_pending_ov}</strong> ticket(s) remain open." if _tk_pending_ov > 0 else "")
        )

    _pa_text = ' '.join(_pa_parts) if _pa_parts else "Data must be processed through the Falcon Data Generator before a full assessment can be generated."

    st.markdown(
        f'<div style="background:#f0f9ff;border:1px solid #bfdbfe;border-radius:5px;'
        f'padding:16px 20px;margin-top:20px;">'
        f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        f'color:#1e40af;margin-bottom:10px;">Professional Assessment</div>'
        f'<div style="font-size:13px;color:#1e3a5f;line-height:1.9;">{_pa_text}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# SCREEN CAPTURE TO PDF - SIDEBAR TOOL
# ============================================

def render_capture_modal():
    """
    Screen capture tool - opens PNG to PDF converter in new tab
    User captures with GoFullPage, then uploads PNG to convert
    """
    import streamlit.components.v1 as components

    st.markdown("---")
    st.markdown("#### 📸 How to Use")
    st.markdown("""
    1. Use **GoFullPage** extension to capture
    2. Save as **PNG** file
    3. Click button below to open converter
    4. Upload PNG → Preview → Download PDF
    """)

    # Button to open PNG to PDF converter in new tab
    components.html("""
    <style>
        .open-btn {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            width: 100%;
            margin: 10px 0;
        }
        .open-btn:hover {
            background: linear-gradient(135deg, #00e5ff, #00aadd);
            transform: translateY(-1px);
        }
    </style>

    <button class="open-btn" onclick="openConverter()">
        📄 Open PNG to PDF Converter
    </button>

    <script>
    function openConverter() {
        const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PNG to PDF Converter - Falcon Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/jspdf@4.2.0/dist/jspdf.umd.min.js"><\\/script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8rem;
            color: #00d4ff;
        }
        .upload-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            border: 2px dashed #00d4ff;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .upload-section:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: #00ff88;
        }
        .upload-section.dragover {
            background: rgba(0, 212, 255, 0.2);
            border-color: #00ff88;
        }
        .upload-icon { font-size: 48px; margin-bottom: 15px; }
        .upload-text { font-size: 1.1rem; color: #ccc; }
        #fileInput { display: none; }
        .preview-section {
            display: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .preview-section.active { display: block; }
        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .preview-title { font-size: 1.2rem; color: #00d4ff; }
        .file-info { font-size: 0.9rem; color: #aaa; }
        .preview-container {
            background: #fff;
            border-radius: 10px;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
            max-height: 400px;
            overflow: auto;
        }
        #imagePreview { max-width: 100%; max-height: 380px; object-fit: contain; }
        .pdf-preview-section {
            display: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .pdf-preview-section.active { display: block; }
        .pdf-preview-container {
            background: #fff;
            border-radius: 10px;
            width: 100%;
            height: 400px;
        }
        #pdfPreview { width: 100%; height: 100%; border: none; border-radius: 10px; }
        .buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 30px;
            font-size: 1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-convert {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #fff;
        }
        .btn-convert:hover { transform: translateY(-2px); }
        .btn-download {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #1a1a2e;
        }
        .btn-download:hover { transform: translateY(-2px); }
        .btn-reset {
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
        }
        .btn-reset:hover { background: rgba(255, 255, 255, 0.3); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .status {
            text-align: center;
            margin-top: 20px;
            font-size: 0.95rem;
            color: #00ff88;
        }
        .status.error { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 PNG to PDF Converter</h1>

        <div class="upload-section" id="uploadSection">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Click or drag & drop PNG image here</div>
            <input type="file" id="fileInput" accept="image/png,image/jpeg,image/jpg">
        </div>

        <div class="preview-section" id="previewSection">
            <div class="preview-header">
                <span class="preview-title">Image Preview</span>
                <span class="file-info" id="fileInfo"></span>
            </div>
            <div class="preview-container">
                <img id="imagePreview" alt="Preview">
            </div>
        </div>

        <div class="pdf-preview-section" id="pdfPreviewSection">
            <div class="preview-header">
                <span class="preview-title">PDF Preview</span>
            </div>
            <div class="pdf-preview-container">
                <iframe id="pdfPreview"></iframe>
            </div>
        </div>

        <div class="buttons">
            <button class="btn btn-convert" id="convertBtn" disabled>✅ Convert to PDF</button>
            <button class="btn btn-download" id="downloadBtn" disabled>⬇️ Download PDF</button>
            <button class="btn btn-reset" id="resetBtn">🔄 Reset</button>
        </div>

        <div class="status" id="status"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        const uploadSection = document.getElementById('uploadSection');
        const fileInput = document.getElementById('fileInput');
        const previewSection = document.getElementById('previewSection');
        const imagePreview = document.getElementById('imagePreview');
        const fileInfo = document.getElementById('fileInfo');
        const pdfPreviewSection = document.getElementById('pdfPreviewSection');
        const pdfPreview = document.getElementById('pdfPreview');
        const convertBtn = document.getElementById('convertBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const resetBtn = document.getElementById('resetBtn');
        const status = document.getElementById('status');

        let currentImage = null;
        let pdfBlobUrl = null;

        uploadSection.addEventListener('click', () => fileInput.click());

        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('dragover');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleFile(file);
            } else {
                showStatus('Please upload an image file (PNG/JPG).', true);
            }
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) handleFile(file);
        });

        function handleFile(file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                currentImage = new Image();
                currentImage.onload = () => {
                    imagePreview.src = currentImage.src;
                    fileInfo.textContent = file.name + ' (' + currentImage.width + ' x ' + currentImage.height + 'px)';
                    previewSection.classList.add('active');
                    pdfPreviewSection.classList.remove('active');
                    convertBtn.disabled = false;
                    downloadBtn.disabled = true;
                    showStatus('Image loaded. Click "Convert to PDF" to proceed.');
                };
                currentImage.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        convertBtn.addEventListener('click', () => {
            if (!currentImage) return;
            showStatus('Converting to PDF...');

            const imgWidth = currentImage.width;
            const imgHeight = currentImage.height;
            const pxToMm = 25.4 / 96;
            let pdfWidth = imgWidth * pxToMm;
            let pdfHeight = imgHeight * pxToMm;

            // Max A1 size for large captures
            const maxWidth = 594;
            const maxHeight = 841;

            if (pdfWidth > maxWidth) {
                const scale = maxWidth / pdfWidth;
                pdfWidth = maxWidth;
                pdfHeight = pdfHeight * scale;
            }
            if (pdfHeight > maxHeight) {
                const scale = maxHeight / pdfHeight;
                pdfHeight = maxHeight;
                pdfWidth = pdfWidth * scale;
            }

            pdfWidth = Math.max(pdfWidth, 50);
            pdfHeight = Math.max(pdfHeight, 50);

            const orientation = pdfWidth > pdfHeight ? 'landscape' : 'portrait';
            const pdf = new jsPDF({
                orientation: orientation,
                unit: 'mm',
                format: [pdfWidth, pdfHeight]
            });

            pdf.addImage(currentImage.src, 'PNG', 0, 0, pdfWidth, pdfHeight);

            if (pdfBlobUrl) URL.revokeObjectURL(pdfBlobUrl);
            pdfBlobUrl = URL.createObjectURL(pdf.output('blob'));

            pdfPreview.src = pdfBlobUrl;
            pdfPreviewSection.classList.add('active');
            downloadBtn.disabled = false;
            showStatus('PDF created! Preview above. Click "Download PDF" to save.');
        });

        downloadBtn.addEventListener('click', () => {
            if (!pdfBlobUrl) return;
            const link = document.createElement('a');
            link.href = pdfBlobUrl;
            const ts = new Date().toISOString().slice(0,10).replace(/-/g,'');
            link.download = 'falcon-dashboard-' + ts + '.pdf';
            link.click();
            showStatus('PDF downloaded!');
        });

        resetBtn.addEventListener('click', () => {
            currentImage = null;
            if (pdfBlobUrl) { URL.revokeObjectURL(pdfBlobUrl); pdfBlobUrl = null; }
            fileInput.value = '';
            imagePreview.src = '';
            pdfPreview.src = '';
            previewSection.classList.remove('active');
            pdfPreviewSection.classList.remove('active');
            convertBtn.disabled = true;
            downloadBtn.disabled = true;
            status.textContent = '';
        });

        function showStatus(message, isError = false) {
            status.textContent = message;
            status.className = 'status' + (isError ? ' error' : '');
        }
    <\\/script>
</body>
</html>`;

        // Open in new tab using blob URL
        const blob = new Blob([html], {type: 'text/html'});
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
    }
    </script>
    """, height=70)

    st.caption("💡 Opens in a new browser tab")

    if st.button("✖️ Close", key="close_capture_modal", use_container_width=True):
        st.session_state.show_capture_modal = False
        st.rerun()


# ============================================
# MAIN DASHBOARD FUNCTION
# ============================================

def falcon_dashboard_pdf_layout():
    """
    Main function to render the single-page PDF-style dashboard
    Uses exact chart logic from pivot_table_builder.py
    """
    # Apply custom CSS
    apply_dashboard_css()

    # ============================
    # SIDEBAR CONFIGURATION
    # ============================
    with st.sidebar:
        st.markdown("### 📝 Dashboard Configuration")
        st.markdown("---")

        # Get current month for default
        current_month = datetime.now().strftime("%B %Y")

        # Editable title with placeholder format
        default_title = f"XXX COMPANY - CrowdStrike Falcon Monthly Report ({current_month})"

        st.markdown("### 📝 Report Title Configuration")
        st.markdown("**Important:** Please update the company name and verify the month/year before generating the report.")

        dashboard_title = st.text_input(
            "Dashboard Title",
            value=default_title,
            help="Replace 'XXX COMPANY' with your actual company name. Format: [Company Name] - CrowdStrike Falcon Monthly Report (Month Year)",
            placeholder="e.g., Acme Corporation - CrowdStrike Falcon Monthly Report (January 2026)"
        )

        # Validation warning
        if "XXX COMPANY" in dashboard_title:
            st.warning("⚠️ Please replace 'XXX COMPANY' with your actual company name before generating the PDF report.")

        # Confirmation button
        if st.button("✓ Confirm Title", type="secondary", use_container_width=True):
            st.success("✅ Title confirmed!")

        # Warning if using default title - in sidebar
        if dashboard_title == default_title:
            st.warning("⚠️ Using default title. Please confirm or edit above.")

        st.markdown("---")
        st.info("💡 This dashboard uses the exact same visualization logic as the Main Dashboard Report with PDF styling.")

        # ============================
        # SCREEN CAPTURE TO PDF FEATURE
        # ============================
        st.markdown("### 📸 Screen Capture to PDF")
        st.markdown("Capture the full dashboard as a single-page PDF")

        # Initialize session state for capture modal
        if 'show_capture_modal' not in st.session_state:
            st.session_state.show_capture_modal = False

        if st.button("📷 Capture Full Page to PDF", type="primary", use_container_width=True):
            st.session_state.show_capture_modal = True

        st.caption("💡 This captures the entire dashboard and converts it to a single-page PDF")

        # Show popup launcher in sidebar when activated
        if st.session_state.get('show_capture_modal', False):
            render_capture_modal()

    # Dashboard Title
    st.markdown(f"""
        <div class="dashboard-title">
            {dashboard_title}
        </div>
    """, unsafe_allow_html=True)

    # Check if data is available
    if not check_data_availability():
        st.warning("⚠️ No data available. Please process your data first using Falcon Data Generator.")
        return

    # Load data from session state
    host_data = st.session_state.get('host_analysis_results', {})
    detection_data = st.session_state.get('detection_analysis_results', {})
    time_data = st.session_state.get('time_analysis_results', {})
    ticket_data = st.session_state.get('ticket_lifecycle_results', {})
    quarantine_data = st.session_state.get('quarantine_analysis_results', {})
    sensor_offline_data = st.session_state.get('sensor_offline_results', {})

    # Extract months dynamically from data
    months = extract_months_from_data(host_data, detection_data, time_data)

    # Get actual number of months and create month text helper
    num_months = st.session_state.get('num_months', len(months))
    if num_months == 1:
        month_text = "Single Month"
    elif num_months == 2:
        month_text = "Two Months"
    else:
        month_text = "Three Months"

    # ============================================
    # SIDEBAR: SECTION SELECTION
    # ============================================
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Report Sections")
        st.markdown("Select sections to include in the report:")

        include_ticket_lifecycle = st.checkbox("Ticket Lifecycle Analysis", value=False, help="Include ticket status trend analysis", disabled=not ticket_data)
        include_host_analysis = st.checkbox("Host Security Analysis", value=True, help="Include host security metrics")

        # Sub-option for sensor offline (indented under Host Security Analysis)
        include_sensor_offline = False
        include_sensor_outdated = False
        if include_host_analysis:
            include_sensor_offline = st.checkbox(
                "    ↳ Sensor Offline Summary",
                value=False,
                help="Include offline server monthly trend in Host section",
                disabled=not sensor_offline_data
            )
            if not sensor_offline_data and include_host_analysis:
                st.caption("        💡 Sensor Offline disabled (no offline sensor data)")

            has_sensor_data = bool(host_data and 'sensor_analysis' in host_data)
            include_sensor_outdated = st.checkbox(
                "    ↳ Outdated Sensor Version Details",
                value=False,
                help="Show per-hostname cards for endpoints still running an outdated sensor in the latest month",
                disabled=not has_sensor_data
            )
            if not has_sensor_data and include_host_analysis:
                st.caption("        💡 Outdated Sensor Details disabled (no sensor data)")

        include_detection_analysis = st.checkbox("Detection and Severity Analysis", value=True, help="Include detection and severity trends")

        # Sub-option for quarantine analysis (indented under Detection and Severity)
        include_quarantine_analysis = False
        if include_detection_analysis:
            include_quarantine_analysis = st.checkbox(
                "    ↳ Quarantined File Summary",
                value=False,
                help="Include quarantine file monthly trend in Detection section",
                disabled=not quarantine_data
            )
            if not quarantine_data and include_detection_analysis:
                st.caption("        💡 Quarantine analysis disabled (no quarantine data)")

        include_time_analysis = st.checkbox("Time-Based Analysis", value=True, help="Include time-based detection patterns")
        include_chart_insights = st.checkbox("Chart Key Findings", value=False, help="Show data-driven insight callouts below each chart — can be turned off for a cleaner layout")
        include_executive_summary = st.checkbox("Executive Summary Report", value=False, help="Include professional executive summary with key findings and recommendations")

        st.markdown("---")
        with st.expander("📊 How Percentages Are Calculated", expanded=False):
            st.markdown("""
**Detection Volume Trend (%)**
> (Latest month − Previous month) ÷ Previous month × 100
> *Example: March=124, Feb=69 → (124−69) ÷ 69 × 100 = **80%** increase*

**High-Priority Detection Rate (%)**
> (Critical + High detections) ÷ Total detections × 100

**Average Detections per Device**
> Total detections ÷ Unique hosts with detections

**Ticket Resolution Rate (%)**
> Resolved tickets ÷ Total tickets × 100

**Outdated Sensor Rate (%)**
> Unique hosts on outdated sensor (latest month) ÷ Total unique hosts (latest month) × 100

**Top Host Detection Share (%)**
> Host's detection count ÷ Total detections in that month × 100

**False Positive / True Positive Rate**
> Counted directly from the `Resolution` column in the detection file, after excluding in-progress rows (`Status = in_progress`)
            """)

        if not ticket_data:
            st.caption("💡 Ticket Lifecycle Analysis is disabled (no ticket data available)")

    # ============================================
    # DYNAMIC SECTION LETTERING
    # ============================================
    # Calculate section letters dynamically based on what's included
    section_letters = {}
    current_letter_index = 0
    letters = ['A', 'B', 'C', 'D', 'E', 'F']

    if include_ticket_lifecycle and ticket_data:
        section_letters['ticket'] = letters[current_letter_index]
        current_letter_index += 1

    if include_host_analysis:
        section_letters['host'] = letters[current_letter_index]
        current_letter_index += 1

    if include_detection_analysis:
        section_letters['detection'] = letters[current_letter_index]
        current_letter_index += 1

    if include_time_analysis:
        section_letters['time'] = letters[current_letter_index]
        current_letter_index += 1

    if include_executive_summary:
        section_letters['executive'] = letters[current_letter_index]
        current_letter_index += 1

    # ============================================
    # TICKET LIFECYCLE ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_ticket_lifecycle and ticket_data:
        section_letter = section_letters.get('ticket', 'A')
        st.markdown(f'<div class="section-header">{section_letter}. Ticket Lifecycle Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Get available months from ticket data
        available_months = []
        month_data_map = {}

        for key in ticket_data.keys():
            if key.startswith('request_severity_pivot_'):
                month_name = key.replace('request_severity_pivot_', '').replace('_', ' ')
                available_months.append(month_name)
                month_data_map[month_name] = key

        if not available_months:
            st.warning("No ticket pivot data available")
        else:
            # Sort months chronologically
            def month_sort_key(month_str):
                """Sort months chronologically (January to December)"""
                try:
                    # Try to parse as "Month Year" format
                    date_obj = datetime.strptime(month_str, '%B %Y')
                    return (date_obj.year, date_obj.month)
                except:
                    # If parsing fails, return the string as-is for alphabetical sort
                    return (9999, month_str)

            sorted_months = sorted(available_months, key=month_sort_key)
            num_months = len(sorted_months)

            # Use actual month names from Falcon Generator (no custom naming needed)
            # Month names are already configured in Falcon Generator with month/year dropdowns
            custom_month_names = {month_name: month_name for month_name in sorted_months}

            # ============================
            # A.1: Combined Chart for All Months
            # ============================
            # Determine trend text
            if num_months == 1:
                trend_text = "Single Month"
            elif num_months == 2:
                trend_text = "Two Month Trends"
            elif num_months == 3:
                trend_text = "Three Month Trends"
            else:
                trend_text = f"{num_months} Month Trends"

            st.markdown(f'<div class="chart-title">{section_letter}.1. Ticket Status Count Across {trend_text} (Open, In-Progress, Pending, On-hold, Closed)</div>', unsafe_allow_html=True)

            # Create detailed breakdown charts side-by-side (like Main Dashboard Report)
            # Each month gets its own chart showing status breakdown
            if num_months == 1:
                chart_cols = [st.container()]
            else:
                chart_cols = st.columns(num_months)

            severity_colors = {
                'Critical': '#DC143C',
                'High': '#FF8C00',
                'Medium': '#4169E1',
                'Low': '#70AD47'
            }

            all_statuses = ['closed', 'in_progress', 'open', 'pending', 'on-hold']

            for idx, month_name in enumerate(sorted_months):
                pivot_key = month_data_map[month_name]
                pivot_df = ticket_data[pivot_key]

                if not isinstance(pivot_df, pd.DataFrame) or pivot_df.empty:
                    continue

                # Get display name for this month
                month_display = custom_month_names[month_name]

                # Aggregate by Status for this month
                month_agg = pivot_df.groupby('Status')[['Critical', 'High', 'Medium', 'Low']].sum().reset_index()

                # Create figure for this month
                fig = go.Figure()

                # Add bars for each severity
                for severity in ['Critical', 'High', 'Medium', 'Low']:
                    if severity in month_agg.columns:
                        fig.add_trace(go.Bar(
                            name=severity,
                            x=month_agg['Status'],
                            y=month_agg[severity],
                            marker_color=severity_colors[severity],
                            text=month_agg[severity],
                            textposition='outside',
                            hovertemplate=f'<b>{severity}</b><br>Status: %{{x}}<br>Count: %{{y}}<extra></extra>'
                        ))

                # Only show legend on the last (rightmost) chart
                show_legend = (idx == len(sorted_months) - 1)

                fig.update_layout(
                    barmode='group',
                    xaxis_title=dict(
                        text=month_display,
                        font=dict(size=12, color='#666666')
                    ),
                    yaxis_title=dict(
                        text="Number of Detections",
                        font=dict(size=10, color='#666666')
                    ),
                    yaxis=dict(
                        tickfont=dict(size=9, color='#666666')
                    ),
                    height=240,
                    showlegend=show_legend,
                    legend=dict(
                        title=dict(text="Severity", font=dict(size=11)),
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10)
                    ),
                    margin=dict(l=40, r=40, t=30, b=50),  # Increased top and bottom margins for text labels
                    uniformtext_minsize=8,
                    uniformtext_mode='hide'
                )

                # Update text position to prevent clipping at top
                fig.update_traces(
                    textposition='outside',
                    cliponaxis=False
                )

                # Display in appropriate column
                if num_months == 1:
                    with chart_cols[0]:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    with chart_cols[idx]:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # ============================
            # A.2: Ticket Detection Summary Overview (Per Month) - Horizontal Category Layout
            # ============================
            st.markdown(f'<div class="chart-title">{section_letter}.2. Ticket Detection Summary Overview</div>', unsafe_allow_html=True)

            # Collect data for all months first
            month_data_list = []
            for idx, month_name in enumerate(sorted_months):
                month_safe = month_name.replace(' ', '_').replace(',', '')
                month_display = custom_month_names[month_name]
                pivot_key = month_data_map[month_name]
                pivot_df = ticket_data[pivot_key]

                if not isinstance(pivot_df, pd.DataFrame) or pivot_df.empty:
                    continue

                # Get summary data for this month
                summary_key = f'ticket_summary_{month_safe}'
                summary_data = ticket_data.get(summary_key, {})

                # Default values
                total_alerts = summary_data.get('total_alerts', 0)
                alerts_resolved = summary_data.get('alerts_resolved', 0)
                alerts_pending = summary_data.get('alerts_pending', 0)

                # Use pending_request_ids from summary_data (allows manual override from builder)
                pending_request_str = summary_data.get('pending_request_ids', '')
                if not pending_request_str:
                    pending_request_str = "None"

                # Determine monthly color based on index (1st=Green, 2nd=Blue, 3rd=Gold)
                if idx == 0:
                    month_color = MONTHLY_COLORS['month_1']  # Green
                elif idx == 1:
                    month_color = MONTHLY_COLORS['month_2']  # Blue
                else:
                    month_color = MONTHLY_COLORS['month_3']  # Gold

                month_data_list.append({
                    'month_display': month_display,
                    'month_color': month_color,
                    'total_alerts': total_alerts,
                    'alerts_resolved': alerts_resolved,
                    'alerts_pending': alerts_pending,
                    'pending_request_str': pending_request_str
                })

            # Compact table-style layout - all data in organized rows
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

            # Build HTML table structure with card-style rows and spacing
            table_html = '<div style="display: flex; flex-direction: column; gap: 8px; margin: 10px 0;">'

            # Header row with month names
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 12px; font-weight: bold; color: #333; font-size: 13px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Metric</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 12px; text-align: center; font-weight: bold; background: {month_info["month_color"]}; color: black; font-size: 12px; border-radius: 8px;">{month_info["month_display"]}</div>'
            table_html += '</div>'

            # Row 1: Triggered Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Triggered</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["total_alerts"]}</span></div>'
            table_html += '</div>'

            # Row 2: Resolved Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Resolved</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["alerts_resolved"]}</span></div>'
            table_html += '</div>'

            # Row 3: Pending Alerts
            table_html += '<div style="display: flex; gap: 8px;">'
            table_html += '<div style="flex: 0 0 220px; padding: 14px 12px; font-size: 12px; color: #555; font-weight: 600; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">Alert Detections Pending</div>'
            for month_info in month_data_list:
                table_html += f'<div style="flex: 1; padding: 14px 12px; text-align: center; background: {month_info["month_color"]}; color: black; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 28px; font-weight: bold;">{month_info["alerts_pending"]}</span></div>'
            table_html += '</div>'

            table_html += '</div>'

            st.markdown(table_html, unsafe_allow_html=True)

            # Pending Request IDs section below table - compact display
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            pending_cols = st.columns(num_months)
            for idx, month_info in enumerate(month_data_list):
                with pending_cols[idx]:
                    # Show all pending Request IDs with alert counts (no limit)
                    if month_info['pending_request_str'] != "None":
                        st.markdown(f"""
                            <div style='background: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid {month_info['month_color']};
                                        font-size: 11px;
                                        max-height: 150px;
                                        overflow-y: auto;'>
                                <strong style='color: #333; font-size: 12px;'>Pending Request IDs:</strong><br>
                                <span style='color: #666;'>{month_info['pending_request_str']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style='background: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid {month_info['month_color']};
                                        font-size: 11px;
                                        text-align: center;'>
                                <span style='color: #999; font-style: italic;'>No pending alerts</span>
                            </div>
                        """, unsafe_allow_html=True)

        if include_chart_insights and month_data_list:
            _tk_total = sum(d['total_alerts'] for d in month_data_list)
            _tk_resolved = sum(d['alerts_resolved'] for d in month_data_list)
            _tk_pending = sum(d['alerts_pending'] for d in month_data_list)
            _tk_latest = month_data_list[-1]['month_display'] if month_data_list else ''
            _tk_rate = (_tk_resolved / _tk_total * 100) if _tk_total > 0 else 0
            _tk_col = '#065f46' if _tk_rate >= 90 else '#1f4e5f' if _tk_rate >= 75 else '#92400e' if _tk_rate >= 60 else '#991b1b'
            _insight_box(
                f"<strong>{_tk_total}</strong> total ticket(s) across {month_text} — "
                f"<strong style='color:{_tk_col};'>{_tk_resolved} resolved ({_tk_rate:.1f}%)</strong>"
                f"{f', <strong>{_tk_pending}</strong> still pending as of {_tk_latest}.' if _tk_pending > 0 else '. All tickets resolved.'}"
            )

        # ── RESOLUTION VERDICT (always shown when ticket section is included) ──
        _raw_monthly = st.session_state.get('raw_monthly_detections', {})
        if _raw_monthly:
            _res_stats, _res_months, _res_latest = _analyze_resolution(_raw_monthly)

            # Warn about empty Resolution data (show for ALL months, not just latest)
            for _rm in _res_months:
                _rs = _res_stats.get(_rm, {})
                if _rs.get('has_data') and _rs.get('empty'):
                    st.warning(
                        f"Resolution data for **{_rm}** appears to be empty — "
                        f"the `Resolution` column in the uploaded detection file has no values filled in. "
                        f"Please update the file with `false_positive` or `true_positive` values before generating the final report. "
                        f"This month will be skipped in the resolution analysis until data is provided."
                    )

            # Resolution Key Finding for the latest month
            if _res_latest:
                _rs_l = _res_stats.get(_res_latest, {})
                if _rs_l.get('has_data') and not _rs_l.get('empty'):
                    _tp_l  = _rs_l['true_positive']
                    _fp_l  = _rs_l['false_positive']
                    _ip_l  = _rs_l['in_progress']
                    _tot_l = _rs_l['total']

                    if _tp_l == 0 and _fp_l > 0:
                        _verdict_color = '#065f46'
                        _verdict_text  = (
                            f"All <strong>{_fp_l}</strong> assessed detection(s) for <strong>{_res_latest}</strong> "
                            f"were confirmed <strong style='color:#065f46;'>false positive</strong> — "
                            f"no real threats identified this month."
                            + (f" <strong>{_ip_l}</strong> detection(s) still under investigation (in-progress)." if _ip_l > 0 else "")
                        )
                    elif _tp_l > 0:
                        _verdict_color = '#991b1b'
                        _verdict_text  = (
                            f"<strong style='color:#991b1b;'>{_tp_l} true positive</strong> threat(s) confirmed for "
                            f"<strong>{_res_latest}</strong> out of {_tot_l} total detection(s) "
                            f"({_fp_l} false positive, {_ip_l} in-progress). "
                            f"The analysis below focuses on these confirmed threats only."
                        )
                    else:
                        _verdict_color = '#92400e'
                        _verdict_text  = (
                            f"<strong>{_res_latest}</strong>: {_tot_l} detection(s) recorded — "
                            f"<strong>{_ip_l}</strong> still under investigation. No resolution confirmed yet."
                        )

                    st.markdown(
                        f'<div style="background:#f8fafc;border-left:4px solid {_verdict_color};'
                        f'border-radius:5px;padding:12px 16px;margin:8px 0 14px 0;">'
                        f'<div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
                        f'color:{_verdict_color};margin-bottom:5px;">Detection Resolution — {_res_latest}</div>'
                        f'<div style="font-size:13px;color:#1e293b;line-height:1.7;">{_verdict_text}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section A

        # PAGE BREAK AFTER SECTION A IF INCLUDED
        st.markdown('<div class="page-break-after"></div>', unsafe_allow_html=True)

    # ============================================
    # HOST SECURITY ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_host_analysis:
        section_letter = section_letters.get('host', 'A')
        st.markdown(f'<div class="section-header">{section_letter}. Host Security Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Overview Detection (full width)
        st.markdown(f'<div class="chart-title">{section_letter}.1. Host Overview Detection Across {month_text} Trends</div>', unsafe_allow_html=True)
        if 'overview_key_metrics' in host_data:
            create_chart_with_pivot_logic(
                host_data['overview_key_metrics'],
                rows=['Month'],
                columns=['KEY METRICS'],
                values=['Count'],
                chart_type='Bar Chart',
                height=240,
                analysis_key='overview_key_metrics',
                use_monthly_colors=True,
                sort_by='Month'
            )

        if include_chart_insights and 'overview_key_metrics' in host_data:
            _om = host_data['overview_key_metrics']
            if not _om.empty and 'KEY METRICS' in _om.columns and 'Count' in _om.columns:
                _td_rows = _om[_om['KEY METRICS'] == 'Total Detections']
                if not _td_rows.empty and 'Month' in _td_rows.columns:
                    _monthly_parts = ', '.join(
                        f"<strong>{_m}</strong>: {int(_c)}"
                        for _m, _c in _td_rows.groupby('Month')['Count'].sum().items()
                    )
                    _grand = int(_td_rows['Count'].sum())
                    _insight_box(f"Total alerts detected across {month_text}: <strong>{_grand:,}</strong>. Monthly totals — {_monthly_parts}.")
                elif not _td_rows.empty:
                    _grand = int(_td_rows['Count'].sum())
                    _insight_box(f"<strong>{_grand:,}</strong> total alerts detected across {month_text}.")

        # Subsection 2 and 3 side by side
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="chart-title">{section_letter}.2. Top Hosts with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
            if 'overview_top_hosts' in host_data:
                create_chart_with_pivot_logic(
                    host_data['overview_top_hosts'],
                    rows=['TOP HOSTS WITH MOST DETECTIONS'],
                    columns=['Month'],
                    values=['Count'],
                    chart_type='Bar Chart',
                    height=220,
                    analysis_key='overview_top_hosts',
                    top_n={'enabled': True, 'field': 'TOP HOSTS WITH MOST DETECTIONS', 'n': 5, 'type': 'top', 'by_field': 'Count', 'per_month': False},
                    use_monthly_colors=True
                )

        with col2:
            st.markdown(f'<div class="chart-title">{section_letter}.3. Users with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
            if 'user_analysis' in host_data:
                create_chart_with_pivot_logic(
                    host_data['user_analysis'],
                    rows=['Username'],
                    columns=['Month'],
                    values=['Count of Detection'],
                    chart_type='Bar Chart',
                    height=220,
                    analysis_key='user_analysis',
                    top_n={'enabled': True, 'field': 'Username', 'n': 5, 'type': 'top', 'by_field': 'Count of Detection', 'per_month': False},
                    use_monthly_colors=True
                )

        if include_chart_insights and 'overview_top_hosts' in host_data:
            _thdf = host_data['overview_top_hosts']
            if not _thdf.empty and 'TOP HOSTS WITH MOST DETECTIONS' in _thdf.columns and 'Count' in _thdf.columns:
                _top3 = _thdf.groupby('TOP HOSTS WITH MOST DETECTIONS')['Count'].sum().nlargest(3)
                if len(_top3):
                    _top_h = _top3.index[0]
                    _top_c = int(_top3.iloc[0])
                    _insight_box(f"<strong>{_top_h}</strong> recorded the most alerts with <strong>{_top_c}</strong> detections across {month_text}.")

        # Sensor Versions (full width)
        st.markdown(f'<div class="chart-title">{section_letter}.4. Detections Hosts with Sensor Versions Status Across {month_text}</div>', unsafe_allow_html=True)
        if 'sensor_analysis' in host_data:
            create_chart_with_pivot_logic(
                host_data['sensor_analysis'],
                rows=['Sensor Version', 'Month', 'Status'],
                columns=[],
                values=['Host Count'],
                chart_type='Bar Chart',
                height=240,
                analysis_key='sensor_analysis',
                use_monthly_colors=True
            )

        if include_chart_insights and 'sensor_analysis' in host_data:
            _sdf = host_data['sensor_analysis']
            if not _sdf.empty and 'Status' in _sdf.columns and 'Host Count' in _sdf.columns and 'Month' in _sdf.columns:
                _s_mo = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                         'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
                def _s_ms(m):
                    p = str(m).split()
                    return (int(p[1]) if len(p)==2 and p[1].isdigit() else 9999, _s_mo.get(p[0],99))
                _s_months = sorted(_sdf['Month'].dropna().unique().tolist(), key=_s_ms)
                _latest_m = _s_months[-1] if _s_months else None
                if _latest_m:
                    _ldf = _sdf[_sdf['Month'] == _latest_m]
                    # Count UNIQUE hosts per status in latest month (matches B.4a card count)
                    _sv_si_lkp = {str(r['Sensor Version']): r['Status'] for _, r in _ldf.iterrows()}
                    _det_raw_si = host_data.get('raw_data', pd.DataFrame())
                    if not _det_raw_si.empty and 'Hostname' in _det_raw_si.columns and 'Sensor Version' in _det_raw_si.columns:
                        _mc_si = 'Month' if 'Month' in _det_raw_si.columns else 'Period'
                        _lm_si = _det_raw_si[_det_raw_si[_mc_si] == _latest_m][['Hostname', 'Sensor Version']].drop_duplicates('Hostname')
                        _out = int((_lm_si['Sensor Version'].astype(str).map(_sv_si_lkp) == 'Outdated').sum())
                        _tot = len(_lm_si)
                    else:
                        _out = int(_ldf[_ldf['Status'] == 'Outdated']['Host Count'].sum())
                        _tot = int(_ldf['Host Count'].sum())
                    if _tot > 0 and _out > 0:
                        _pct = _out / _tot * 100
                        _col = '#991b1b' if _pct > 30 else '#92400e' if _pct > 10 else '#065f46'
                        _insight_box(f"As of <strong>{_latest_m}</strong>: <strong style='color:{_col};'>{_out} device(s) ({_pct:.0f}%)</strong> are still on an outdated sensor version and need to be updated.")
                    else:
                        _insight_box(f"As of <strong>{_latest_m}</strong>: all monitored devices are running the latest Falcon sensor version.")

        # ============================
        # A.4a: Sensor Version Details - Card Layout per Hostname
        # ============================
        if include_sensor_outdated:
          st.markdown(f'<div class="chart-title">{section_letter}.4a. Sensor Version Details by Hostname - Outdated</div>', unsafe_allow_html=True)

          raw_host_df = st.session_state.get('three_month_trend_data', {}).get('host_analysis', pd.DataFrame())
          sensor_df = host_data.get('sensor_analysis', pd.DataFrame())

          if (not raw_host_df.empty and not sensor_df.empty
                and 'Hostname' in raw_host_df.columns
                and 'Sensor Version' in raw_host_df.columns
                and 'Status' in sensor_df.columns):

            # Build (Sensor Version, Month) → Status lookup from aggregated analysis
            month_col = 'Month' if 'Month' in raw_host_df.columns else 'Period'
            status_lookup = {}
            for _, row in sensor_df.iterrows():
                key = (str(row['Sensor Version']), str(row['Month']))
                status_lookup[key] = row['Status']

            # Determine the latest month in the data (chronological)
            _month_order = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                            'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
            def _month_sort_key(m):
                parts = str(m).split()
                return (int(parts[1]) if len(parts)==2 and parts[1].isdigit() else 9999,
                        _month_order.get(parts[0], 99) if parts else 99)
            all_months_in_data = sorted(sensor_df['Month'].dropna().unique().tolist(), key=_month_sort_key)
            latest_month = all_months_in_data[-1] if all_months_in_data else None

            # Unique per-hostname records with sensor version + month
            host_records = raw_host_df[['Hostname', 'Sensor Version', month_col]].drop_duplicates().copy()
            host_records = host_records.rename(columns={month_col: 'Month'})
            host_records['Status'] = host_records.apply(
                lambda r: status_lookup.get((str(r['Sensor Version']), str(r['Month'])), 'Unknown'),
                axis=1
            )

            # Aggregate per hostname — store per-version-per-month entries
            hostname_cards = []
            for hostname in sorted(raw_host_df['Hostname'].dropna().unique()):
                hdf = host_records[host_records['Hostname'] == hostname]
                # Build sorted list of (version, month, status) — one row per unique combo
                sv_month_entries = (
                    hdf[['Sensor Version', 'Month', 'Status']]
                    .drop_duplicates()
                    .sort_values('Month', key=lambda col: col.map(_month_sort_key))
                    .to_dict('records')
                )
                statuses = hdf['Status'].unique().tolist()
                primary_status = 'Outdated' if 'Outdated' in statuses else 'Latest'
                outdated_months = [e['Month'] for e in sv_month_entries if e['Status'] == 'Outdated']
                # Count detections from the LATEST MONTH only (not cumulative across all months)
                det_count = len(raw_host_df[
                    (raw_host_df['Hostname'] == hostname) &
                    (raw_host_df[month_col] == latest_month)
                ])

                # Determine status in the latest month specifically
                latest_month_entries = [e for e in sv_month_entries if e['Month'] == latest_month]
                status_in_latest = latest_month_entries[0]['Status'] if latest_month_entries else None

                hostname_cards.append({
                    'hostname': hostname,
                    'sv_month_entries': sv_month_entries,
                    'status': primary_status,
                    'outdated_months': outdated_months,
                    'status_in_latest': status_in_latest,
                    'det_count': det_count,
                })

            # Only show hosts that are STILL Outdated in the latest month
            # (if they updated in the latest month → Latest → exclude from this list)
            hostname_cards = [
                c for c in hostname_cards
                if c['status_in_latest'] == 'Outdated'
            ]
            hostname_cards.sort(key=lambda x: (-len(x['outdated_months']), x['hostname']))

            # Determine max outdated months (for priority highlight)
            max_outdated = max((len(c['outdated_months']) for c in hostname_cards), default=0)

            status_style = {
                'Latest':   ('#70AD47', '#fff'),
                'Outdated': ('#DC143C', '#fff'),
                'Unknown':  ('#888888', '#fff'),
            }

            cards_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px;'>"
            for card in hostname_cards:
                is_priority = len(card['outdated_months']) == max_outdated and max_outdated > 0
                border_color = '#DC143C'
                # Priority hosts get a stronger shadow + warning label
                priority_badge = (
                    "<div style='background:#DC143C; color:#fff; font-size:7.5px; font-weight:700; "
                    "padding:2px 6px; border-radius:3px; margin-bottom:6px; display:inline-block; "
                    "letter-spacing:0.5px;'>⚠ ACTION REQUIRED</div>" if is_priority else ""
                )
                shadow = '0 2px 10px rgba(220,20,60,0.30)' if is_priority else '0 2px 6px rgba(0,0,0,0.08)'

                # Per-version-per-month rows — version | month | status badge
                sv_html = ''
                for entry in card['sv_month_entries']:
                    s_color, s_fg = status_style.get(entry['Status'], ('#888', '#fff'))
                    sv_html += (
                        f"<div style='display:flex; align-items:center; gap:4px; "
                        f"margin-bottom:4px; flex-wrap:wrap;'>"
                        f"<span style='font-size:8px; color:{s_color}; font-weight:700; "
                        f"background:{s_color}15; padding:2px 5px; border-radius:3px; "
                        f"word-break:break-all; flex:1;'>{entry['Sensor Version']}</span>"
                        f"<span style='font-size:7.5px; color:#666; white-space:nowrap;'>{entry['Month']}</span>"
                        f"<span style='background:{s_color}; color:{s_fg}; font-size:7px; "
                        f"padding:1px 5px; border-radius:3px; font-weight:700; "
                        f"white-space:nowrap;'>{entry['Status'].upper()}</span>"
                        f"</div>"
                    )

                cards_html += f"""
                <div style='flex: 1 1 200px; min-width: 180px; max-width: 240px;
                            background: #ffffff; border-radius: 8px;
                            border-top: 4px solid {border_color};
                            box-shadow: {shadow};
                            padding: 12px 14px;'>
                    {priority_badge}
                    <div style='font-size: 9.5px; color: #333; word-break: break-all;
                                margin-bottom: 4px; font-weight: 700; line-height: 1.3;'>🖥 {card['hostname']}</div>
                    <div style='font-size: 20px; font-weight: bold; color: {border_color};
                                line-height: 1;'>{card['det_count']}</div>
                    <div style='font-size: 9px; color: #888; margin-bottom: 8px;'>detections ({latest_month})</div>
                    <div>{sv_html}</div>
                </div>"""

            cards_html += "</div>"
            st.markdown(cards_html, unsafe_allow_html=True)

            # Summary footer
            # Sum per-month "Total Hosts" from overview_key_metrics — same source as B.1 bars.
            # This gives the same numbers the user sees in B.1 (per-month unique detection hosts summed),
            # avoiding confusion from a deduplicated count that appears lower than the B.1 bars.
            _om_b4a = host_data.get('overview_key_metrics', pd.DataFrame())
            if not _om_b4a.empty and 'KEY METRICS' in _om_b4a.columns and 'Count' in _om_b4a.columns:
                _th_b4a = _om_b4a[_om_b4a['KEY METRICS'] == 'Total Hosts']
                total_all_hosts = int(_th_b4a['Count'].sum()) if not _th_b4a.empty else 0
            else:
                _det_raw = host_data.get('raw_data', pd.DataFrame())
                total_all_hosts = _det_raw['Hostname'].nunique() if not _det_raw.empty and 'Hostname' in _det_raw.columns else 0
            st.markdown(f"""
                <div style='display: flex; gap: 10px; margin-top: 12px;'>
                    <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                border-left: 4px solid #DC143C;'>
                        <strong style='color: #333; font-size: 11px;'>Outdated Sensor Hosts</strong><br>
                        <span style='font-size: 22px; font-weight: bold; color: #DC143C;'>{len(hostname_cards)}</span>
                        <span style='font-size: 10px; color: #666;'> host(s)</span>
                    </div>
                    <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                border-left: 4px solid {SECTION_HEADER_COLOR};'>
                        <strong style='color: #333; font-size: 11px;'>Total Hosts in Period</strong><br>
                        <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{total_all_hosts}</span>
                        <span style='font-size: 10px; color: #666;'> host(s)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
          if include_chart_insights and hostname_cards:
            _attn = [c for c in hostname_cards if c.get('attention')]
            _insight_box(
                f"<strong>{len(hostname_cards)}</strong> device(s) still running an outdated Falcon sensor as of <strong>{latest_month or month_text}</strong>"
                f"{f' — <strong>{len(_attn)}</strong> device(s) flagged for immediate attention.' if _attn else '.'}"
            )
          else:
            st.info("No sensor hostname data available. Ensure data has been processed via Falcon Data Generator.")

        # ============================
        # SENSOR OFFLINE ANALYSIS (OPTIONAL SUB-SECTION)
        # ============================
        if include_sensor_offline and sensor_offline_data and 'offline_monthly_counts' in sensor_offline_data:

            offline_monthly_df = sensor_offline_data['offline_monthly_counts'].copy()

            # Build chronological month order and color map
            month_name_to_num_so = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }

            def offline_month_sort_key(month_str):
                import re as _re
                year_match = _re.search(r'(\d{4})', str(month_str))
                year = int(year_match.group(1)) if year_match else 2000
                month_num = next((n for name, n in month_name_to_num_so.items() if name in str(month_str)), 0)
                return (year, month_num)

            offline_monthly_df['_sort'] = offline_monthly_df['Month Name'].apply(offline_month_sort_key)
            offline_monthly_df = offline_monthly_df.sort_values('_sort').drop(columns=['_sort']).reset_index(drop=True)

            so_month_color_keys = ['month_1', 'month_2', 'month_3']
            so_months = offline_monthly_df['Month Name'].tolist()
            so_month_color_map = {
                m: MONTHLY_COLORS[so_month_color_keys[i] if i < 3 else 'month_3']
                for i, m in enumerate(so_months)
            }

            # B.5 — Offline Server Details (pie + table)
            st.markdown(f'<div class="chart-title">{section_letter}.5. Offline Server Details (Servers with a sensor that went offline within last 30 days)</div>', unsafe_allow_html=True)

            if 'raw_data' in sensor_offline_data:
                so_raw_df = sensor_offline_data['raw_data'].copy()

                # OS version counts — vertical column bar chart
                os_counts = so_raw_df.groupby('OS Version').size().reset_index(name='Count')
                os_counts = os_counts.sort_values('Count', ascending=False)

                bar_palette = [
                    '#70AD47', '#5B9BD5', '#FFC000', '#DC143C', '#ED7D31',
                    '#9B59B6', '#1ABC9C', '#E74C3C', '#3498DB', '#F39C12'
                ]
                bar_colors_so = [bar_palette[i % len(bar_palette)] for i in range(len(os_counts))]

                so_pie_fig = go.Figure(data=[go.Bar(
                    x=os_counts['OS Version'].tolist(),
                    y=os_counts['Count'].tolist(),
                    marker=dict(color=bar_colors_so, line=dict(color='white', width=0.5)),
                    text=os_counts['Count'].tolist(),
                    textposition='outside',
                    textfont=dict(family='Arial', size=9),
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                )])
                so_pie_fig.update_layout(
                    title=dict(
                        text='Offline Servers by OS Version',
                        font=dict(family='Arial', size=11, color='#333333'),
                        x=0.5, xanchor='center'
                    ),
                    height=300,
                    margin=dict(t=40, b=80, l=40, r=20),
                    xaxis=dict(tickfont=dict(family='Arial', size=9), tickangle=-30),
                    yaxis=dict(title=dict(text='Count', font=dict(family='Arial', size=10)),
                               tickfont=dict(family='Arial', size=9)),
                    bargap=0.3,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )

                # Sort by Last Seen ascending = oldest (longest offline) first, group same dates
                so_display = so_raw_df.copy()
                so_display['_ls_dt'] = pd.to_datetime(so_display['Last Seen'], errors='coerce')
                so_display = so_display.sort_values('_ls_dt', ascending=True).head(20)
                so_display['_ls_str'] = so_display['_ls_dt'].dt.strftime('%d %b %Y')

                # Build ordered date groups
                from collections import OrderedDict as _OD
                date_groups = _OD()
                for _, row in so_display.iterrows():
                    ds = row['_ls_str']
                    if ds not in date_groups:
                        date_groups[ds] = []
                    date_groups[ds].append(row)

                col_pie_so, col_tbl_so = st.columns([5, 4])
                with col_pie_so:
                    st.plotly_chart(so_pie_fig, use_container_width=True, config={'displayModeBar': False})
                with col_tbl_so:
                    tbl_html_so = (
                        '<table style="width:100%; border-collapse: collapse; font-size: 9.5px; margin-top: 8px;">'
                        '<thead>'
                        f'<tr style="background: {SECTION_HEADER_COLOR}; color: white;">'
                        '<th style="padding: 6px 7px; text-align: center;">Last Seen</th>'
                        '<th style="padding: 6px 7px; text-align: left;">Hostname</th>'
                        '<th style="padding: 6px 5px; text-align: center;">Platform</th>'
                        '</tr></thead><tbody>'
                    )
                    for date_idx, (date_str, rows) in enumerate(date_groups.items()):
                        bg = '#f0f4f8' if date_idx % 2 == 0 else '#ffffff'
                        rowspan = len(rows)
                        for i, row in enumerate(rows):
                            hostname = row.get('Hostname', '')
                            platform = row.get('Platform', 'Unknown')
                            tbl_html_so += f'<tr style="background: {bg}; border-bottom: 1px solid #e8e8e8;">'
                            if i == 0:
                                tbl_html_so += (
                                    f'<td rowspan="{rowspan}" style="padding: 6px 7px; text-align: center; '
                                    f'font-weight: bold; color: {SECTION_HEADER_COLOR}; vertical-align: middle; '
                                    f'border-right: 2px solid #d0d0d0; white-space: nowrap;">{date_str}</td>'
                                )
                            tbl_html_so += (
                                f'<td style="padding: 5px 7px;">{hostname}</td>'
                                f'<td style="padding: 5px 5px; text-align: center;">{platform}</td>'
                                f'</tr>'
                            )
                    tbl_html_so += '</tbody></table>'
                    st.markdown(tbl_html_so, unsafe_allow_html=True)

                # Footer info cards
                total_offline = sensor_offline_data.get('overview', {}).get('total_offline', 0)
                unique_platforms = sensor_offline_data.get('overview', {}).get('unique_platforms', 0)
                unique_os = sensor_offline_data.get('overview', {}).get('unique_os', 0)
                st.markdown(f"""
                    <div style='display: flex; gap: 10px; margin-top: 14px;'>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>Total Offline Servers</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{total_offline}</span>
                            <span style='font-size: 10px; color: #666;'> servers</span>
                        </div>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>Platforms</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{unique_platforms}</span>
                            <span style='font-size: 10px; color: #666;'> platform(s)</span>
                        </div>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>OS Versions</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{unique_os}</span>
                            <span style='font-size: 10px; color: #666;'> OS type(s)</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        if include_chart_insights and include_sensor_offline and sensor_offline_data:
            _so_ov = sensor_offline_data.get('overview', {})
            _so_tot = _so_ov.get('total_offline', 0)
            _so_plat = _so_ov.get('unique_platforms', 0)
            if _so_tot > 0:
                _insight_box(f"<strong>{_so_tot}</strong> server(s) detected with an offline Falcon sensor within the last 30 days, across <strong>{_so_plat}</strong> platform(s).")

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section B

        # PAGE BREAK AFTER SECTION B (Only if ticket lifecycle was not included)
        if not include_ticket_lifecycle:
            st.markdown('<div class="page-break-after"></div>', unsafe_allow_html=True)

    # ============================================
    # DETECTION AND SEVERITY ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_detection_analysis:
        section_letter = section_letters.get('detection', 'B')
        st.markdown(f'<div class="section-header">{section_letter}. Detection and Severity Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Critical and High Detection Overview - Side by Side Layout
        st.markdown(f'<div class="chart-title">{section_letter}.1. Detection Count by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)

        if 'critical_high_overview' in detection_data:
            # Get unique months sorted chronologically (by year AND month)
            month_name_to_num = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12,
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }

            def get_month_sort_key(month_str):
                """Sort by year first, then month (chronological order)"""
                if pd.isna(month_str):
                    return (9999, 99)
                month_str = str(month_str)

                # Extract year (4-digit number)
                import re
                year_match = re.search(r'(\d{4})', month_str)
                year = int(year_match.group(1)) if year_match else 2000

                # Extract month number
                month_num = 0
                for month_name, num in month_name_to_num.items():
                    if month_name in month_str:
                        month_num = num
                        break

                return (year, month_num)

            # Get sorted months
            if 'Month' in detection_data['critical_high_overview'].columns:
                months_list = detection_data['critical_high_overview']['Month'].unique()
                months = sorted([m for m in months_list if pd.notna(m)], key=get_month_sort_key)
            else:
                months = ['Single Month']

            # Create two columns: Critical | High
            col_critical, col_high = st.columns(2)

            # LEFT COLUMN: Critical Detections (3 boxes side-by-side horizontally)
            with col_critical:
                st.markdown('<div style="font-size: 10px; font-weight: bold; margin-bottom: 5px; color: #333; text-align: center;">Critical Detections</div>', unsafe_allow_html=True)

                # Build list of box data with index-based monthly colors (like A.2)
                box_data = []
                for idx, month in enumerate(months):
                    # Filter data for Critical Detections in this month
                    critical_data = detection_data['critical_high_overview'][
                        (detection_data['critical_high_overview']['KEY METRICS'] == 'Critical Detections') &
                        (detection_data['critical_high_overview']['Month'] == month)
                    ]

                    # Get count value
                    if not critical_data.empty and 'Count' in critical_data.columns:
                        count_value = int(critical_data['Count'].iloc[0])
                    else:
                        count_value = 0

                    # Get month color based on index (1st=Green, 2nd=Blue, 3rd=Gold)
                    if idx == 0:
                        month_color = MONTHLY_COLORS['month_1']  # Green
                    elif idx == 1:
                        month_color = MONTHLY_COLORS['month_2']  # Blue
                    else:
                        month_color = MONTHLY_COLORS['month_3']  # Gold

                    box_data.append((month, count_value, month_color))

                # Create horizontal container for boxes with monthly colors and larger font (36px like A.2)
                boxes_html = '<div style="display: flex; gap: 8px; justify-content: center;">'
                for month, count_value, month_color in box_data:
                    boxes_html += f'<div style="background-color: {month_color}; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); flex: 1; min-width: 80px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 12px; color: #000000; font-weight: 600; margin-bottom: 5px;">{month}</div><div style="font-size: 36px; color: #000000; font-weight: bold; margin: 5px 0;">{count_value}</div><div style="font-size: 10px; color: #000000;">Critical</div></div>'
                boxes_html += '</div>'
                st.markdown(boxes_html, unsafe_allow_html=True)

            # RIGHT COLUMN: High Detections (independent bar chart)
            with col_high:
                st.markdown('<div style="font-size: 10px; font-weight: bold; margin-bottom: 5px; color: #333; text-align: center;">High Detections</div>', unsafe_allow_html=True)

                # Filter for High Detections only
                high_only = detection_data['critical_high_overview'][
                    detection_data['critical_high_overview']['KEY METRICS'] == 'High Detections'
                ].copy()

                if not high_only.empty:
                    create_chart_with_pivot_logic(
                        high_only,
                        rows=['Month'],
                        columns=[],
                        values=['Count'],
                        chart_type='Bar Chart',
                        height=180,
                        analysis_key='critical_high_overview',
                        use_monthly_colors=True
                    )

        # ==============================================
        # CRITICAL DETECTION DETAILS LISTING
        # Show detailed info when critical count > 0
        # ==============================================
        # Check if any month has critical detections
        has_critical = any(count > 0 for _, count, _ in box_data)

        if has_critical:
            # Get raw detection data from session state
            raw_detection_data = st.session_state.get('three_month_trend_data', {}).get('detection_analysis', pd.DataFrame())

            if not raw_detection_data.empty and 'SeverityName' in raw_detection_data.columns:
                # Filter for Critical severity only
                critical_records = raw_detection_data[
                    raw_detection_data['SeverityName'].str.lower() == 'critical'
                ].copy()

                if not critical_records.empty:
                    st.markdown(f'<div class="chart-title" style="margin-top: 15px;">{section_letter}.1a. Critical Severity Detection Details</div>', unsafe_allow_html=True)

                    # Define columns to display (check which ones exist)
                    display_columns = []
                    column_mapping = {
                        'Hostname': 'Hostname',
                        'UserName': 'Username',
                        'FileName': 'Filename',
                        'Objective': 'Objective',
                        'Tactic': 'Tactic',
                        'Technique': 'Technique'
                    }

                    for col, display_name in column_mapping.items():
                        if col in critical_records.columns:
                            display_columns.append(col)

                    if display_columns:
                        # Create display dataframe with only relevant columns
                        display_df = critical_records[display_columns].copy()

                        # Rename columns for display
                        display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]

                        # Add Month column if available (from Detect MALAYSIA TIME FORMULA)
                        if 'Detect MALAYSIA TIME FORMULA' in critical_records.columns:
                            try:
                                # Parse using dd/mm/yyyy format (Excel format used across all data)
                                _date_formats = [
                                    '%d/%m/%Y %I:%M:%S %p',  # 31/07/2025 01:31:09 AM
                                    '%d/%m/%Y %H:%M:%S',      # 31/07/2025 09:12:52
                                    '%Y/%m/%d %I:%M:%S %p',  # 2025/07/31 01:31:09 AM
                                    '%Y-%m-%d %H:%M:%S',      # 2025-07-31 09:12:52
                                ]
                                _parsed = pd.Series(
                                    [pd.NaT] * len(critical_records),
                                    index=critical_records.index
                                )
                                for _fmt in _date_formats:
                                    _mask = _parsed.isna()
                                    if not _mask.any():
                                        break
                                    _parsed[_mask] = pd.to_datetime(
                                        critical_records.loc[_mask, 'Detect MALAYSIA TIME FORMULA'],
                                        errors='coerce',
                                        format=_fmt
                                    )
                                # Fallback: flexible parsing with dayfirst=True
                                _still_na = _parsed.isna()
                                if _still_na.any():
                                    _parsed[_still_na] = pd.to_datetime(
                                        critical_records.loc[_still_na, 'Detect MALAYSIA TIME FORMULA'],
                                        errors='coerce',
                                        dayfirst=True
                                    )
                                critical_records['Month'] = _parsed.dt.strftime('%B %Y')
                                display_df.insert(0, 'Month', critical_records['Month'])
                            except:
                                pass

                        # Style the table with compact formatting for PDF
                        st.markdown("""
                        <style>
                        .critical-table {
                            font-size: 9px !important;
                            width: 100%;
                        }
                        .critical-table th {
                            background-color: #f8d7da !important;
                            color: #721c24 !important;
                            padding: 4px 6px !important;
                            text-align: left !important;
                            font-weight: 600 !important;
                            border-bottom: 2px solid #f5c6cb !important;
                        }
                        .critical-table td {
                            padding: 3px 6px !important;
                            border-bottom: 1px solid #dee2e6 !important;
                            font-size: 8px !important;
                        }
                        .critical-table tr:nth-child(even) {
                            background-color: #f8f9fa !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        # Convert to HTML table
                        html_table = '<table class="critical-table"><thead><tr>'
                        for col in display_df.columns:
                            html_table += f'<th>{col}</th>'
                        html_table += '</tr></thead><tbody>'

                        for _, row in display_df.iterrows():
                            html_table += '<tr>'
                            for col in display_df.columns:
                                value = row[col] if pd.notna(row[col]) else '-'
                                # Truncate long values for display
                                if isinstance(value, str) and len(value) > 30:
                                    value = value[:27] + '...'
                                html_table += f'<td>{value}</td>'
                            html_table += '</tr>'

                        html_table += '</tbody></table>'
                        st.markdown(html_table, unsafe_allow_html=True)

        if include_chart_insights and 'critical_high_overview' in detection_data:
            _cho = detection_data['critical_high_overview']
            if not _cho.empty and 'KEY METRICS' in _cho.columns and 'Count' in _cho.columns:
                _crit_tot = int(_cho[_cho['KEY METRICS'] == 'Critical Detections']['Count'].sum())
                _high_tot = int(_cho[_cho['KEY METRICS'] == 'High Detections']['Count'].sum())
                _col = '#991b1b' if _crit_tot > 0 else '#92400e'
                _insight_box(f"<strong style='color:{_col};'>{_crit_tot} Critical</strong> and <strong>{_high_tot} High</strong> severity detections recorded across {month_text}.")

        # C.2 and C.3 side by side
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="chart-title">{section_letter}.2. Detection Count by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
            if 'severity_trend' in detection_data:
                create_chart_with_pivot_logic(
                    detection_data['severity_trend'],
                    rows=['Month'],
                    columns=['SeverityName'],
                    values=['Count'],
                    chart_type='Bar Chart',
                    height=220,
                    analysis_key='severity_trend',
                    use_severity_colors=True
                )

        with col2:
            st.markdown(f'<div class="chart-title">{section_letter}.3. Detection Count by Country Across {month_text} Trends</div>', unsafe_allow_html=True)
            if 'country_analysis' in detection_data:
                create_chart_with_pivot_logic(
                    detection_data['country_analysis'],
                    rows=['Country'],
                    columns=['Month'],
                    values=['Detection Count'],
                    chart_type='Bar Chart',
                    height=220,
                    analysis_key='country_analysis',
                    use_monthly_colors=True
                )

        if include_chart_insights and 'severity_trend' in detection_data:
            _svdf = detection_data['severity_trend']
            if not _svdf.empty and 'SeverityName' in _svdf.columns and 'Count' in _svdf.columns:
                _sdist = _svdf.groupby('SeverityName')['Count'].sum()
                _total_d = int(_svdf['Count'].sum())
                _crit_d = int(_sdist.get('Critical', 0))
                _high_d = int(_sdist.get('High', 0))
                _hp = (_crit_d + _high_d) / _total_d * 100 if _total_d > 0 else 0
                if 'country_analysis' in detection_data:
                    _cdf = detection_data['country_analysis']
                    if not _cdf.empty and 'Country' in _cdf.columns and 'Detection Count' in _cdf.columns:
                        _top_country = _cdf.groupby('Country')['Detection Count'].sum().idxmax()
                        _insight_box(f"<strong>{_total_d:,}</strong> total detections — high-priority (Critical + High) represent <strong>{_hp:.1f}%</strong>. Top source country: <strong>{_top_country}</strong>.")
                    else:
                        _insight_box(f"<strong>{_total_d:,}</strong> total detections across {month_text} — high-priority items represent <strong>{_hp:.1f}%</strong>.")
                else:
                    _insight_box(f"<strong>{_total_d:,}</strong> total detections across {month_text} — high-priority items represent <strong>{_hp:.1f}%</strong>.")

        # Files (bar chart with filename on x-axis)
        st.markdown(f'<div class="chart-title">{section_letter}.4. File Name with Most Detections Across {month_text} Trends - Top 5</div>', unsafe_allow_html=True)
        if 'file_analysis' in detection_data:
            create_chart_with_pivot_logic(
                detection_data['file_analysis'],
                rows=['File Name'],
                columns=['Month'],
                values=['Detection Count'],
                chart_type='Bar Chart',
                height=260,
                analysis_key='file_analysis',
                top_n={'enabled': True, 'field': 'File Name', 'n': 5, 'type': 'top', 'by_field': 'Detection Count', 'per_month': False},
                use_monthly_colors=True
            )

        if include_chart_insights and 'file_analysis' in detection_data:
            _fdf = detection_data['file_analysis']
            if not _fdf.empty and 'File Name' in _fdf.columns and 'Detection Count' in _fdf.columns:
                _ftop = _fdf.groupby('File Name')['Detection Count'].sum().nlargest(1)
                if len(_ftop):
                    _fname = _ftop.index[0]
                    _fcnt = int(_ftop.iloc[0])
                    _insight_box(f"Most frequently detected file: <strong>{_fname}</strong> with <strong>{_fcnt}</strong> occurrence(s) across {month_text}.")

        # ============================
        # QUARANTINE FILE ANALYSIS (OPTIONAL SUB-SECTION)
        # ============================
        if include_quarantine_analysis and quarantine_data and 'monthly_counts' in quarantine_data:
            st.markdown(f'<div class="chart-title">{section_letter}.5. Quarantined File Trend Across {month_text}</div>', unsafe_allow_html=True)

            quarantine_monthly_df = quarantine_data['monthly_counts'].copy()

            # Sort chronologically by year then month number
            month_name_to_num = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }

            def quarantine_month_sort_key(month_str):
                import re as _re
                year_match = _re.search(r'(\d{4})', str(month_str))
                year = int(year_match.group(1)) if year_match else 2000
                month_num = next((num for name, num in month_name_to_num.items() if name in str(month_str)), 0)
                return (year, month_num)

            quarantine_monthly_df['_sort'] = quarantine_monthly_df['Month Name'].apply(quarantine_month_sort_key)
            quarantine_monthly_df = quarantine_monthly_df.sort_values('_sort').drop(columns=['_sort']).reset_index(drop=True)

            # Assign monthly colors in chronological order (Green → Blue → Gold)
            month_color_keys = ['month_1', 'month_2', 'month_3']
            quarantine_monthly_df['_color'] = [
                MONTHLY_COLORS[month_color_keys[i]] if i < 3 else MONTHLY_COLORS['month_3']
                for i in range(len(quarantine_monthly_df))
            ]

            # Build bar chart manually to respect chronological order and monthly colors
            q_fig = go.Figure()
            for i, row in quarantine_monthly_df.iterrows():
                q_fig.add_trace(go.Bar(
                    x=[row['Month Name']],
                    y=[row['Count']],
                    marker_color=row['_color'],
                    text=[str(row['Count'])],
                    textposition='outside',
                    showlegend=True,
                    name=row['Month Name']
                ))
            q_max = quarantine_monthly_df['Count'].max() if not quarantine_monthly_df.empty else 1
            q_fig.update_layout(
                xaxis={'categoryorder': 'array', 'categoryarray': quarantine_monthly_df['Month Name'].tolist(),
                       'title': None,
                       'tickfont': dict(family='Arial', size=10)},
                yaxis={'title': dict(text='Count', font=dict(family='Arial', size=11)),
                       'tickfont': dict(family='Arial', size=10),
                       'range': [0, q_max * 1.3]},
                height=260,
                margin=dict(t=45, b=40, l=40, r=120),
                plot_bgcolor='white',
                paper_bgcolor='white',
                bargap=0.3,
                legend=dict(
                    font=dict(family='Arial', size=10, color='#333333'),
                    orientation='v',
                    x=1.02,
                    y=0.5,
                    xanchor='left',
                    yanchor='middle',
                    itemsizing='constant'
                )
            )
            st.plotly_chart(q_fig, use_container_width=True, config={'displayModeBar': False})

            # ============================
            # C.6: Quarantined Files Details - Card Layout (like Ticket Detection Summary)
            # ============================
            st.markdown(f'<div class="chart-title">{section_letter}.6. Quarantined Files Details</div>', unsafe_allow_html=True)

            if 'raw_data' in quarantine_data:
                quarantine_raw_df = quarantine_data['raw_data'].copy()
                all_q_months = quarantine_monthly_df['Month Name'].tolist()

                # Month color map: chronological order → Green/Blue/Gold
                month_color_map = {
                    m: MONTHLY_COLORS[month_color_keys[i] if i < 3 else 'month_3']
                    for i, m in enumerate(all_q_months)
                }

                # Per-file: dominant month (most events), latest date, all statuses
                def get_file_meta(file_name):
                    fdf = quarantine_raw_df[quarantine_raw_df['File Name'] == file_name]
                    # dominant month by count
                    best_month, best_count = all_q_months[0], 0
                    for m in all_q_months:
                        cnt = len(fdf[fdf['Month Name'] == m])
                        if cnt > best_count:
                            best_count, best_month = cnt, m
                    dom_color = month_color_map[best_month]
                    # latest quarantine date
                    latest_dt = fdf['Date of Quarantine'].max()
                    # statuses — unique, sorted
                    statuses = sorted(fdf['Status'].dropna().unique().tolist())
                    return best_month, dom_color, latest_dt, statuses

                # Status badge colors
                status_style = {
                    'quarantined': ('#DC143C', '#fff'),
                    'released':    ('#ED7D31', '#fff'),
                    'purged':      ('#555555', '#fff'),
                }

                # Build per-file rows, sorted by latest date descending (newest first)
                tbl_rows = []
                pie_colors = []
                file_list = quarantine_raw_df['File Name'].unique().tolist()
                for fn in file_list:
                    fdf = quarantine_raw_df[quarantine_raw_df['File Name'] == fn]
                    total = len(fdf)
                    hosts = fdf['Hostname'].nunique()
                    dom_month, dom_color, latest_dt, statuses = get_file_meta(fn)
                    tbl_rows.append({'name': fn, 'total': total, 'hosts': hosts,
                                     'color': dom_color, 'month': dom_month,
                                     'latest_dt': latest_dt, 'statuses': statuses})
                    pie_colors.append(dom_color)

                # Sort by latest date descending (newest first), then limit to top 10
                tbl_rows.sort(key=lambda r: r['latest_dt'] if pd.notna(r['latest_dt']) else pd.Timestamp.min, reverse=True)
                tbl_rows = tbl_rows[:10]

                # Card grid — sorted newest → oldest, colored Green→Blue→Gold by month
                cards_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px;'>"
                for r in tbl_rows:
                    latest_str = r['latest_dt'].strftime('%d %b %Y') if pd.notna(r['latest_dt']) else 'N/A'
                    status_badges = ''
                    for s in r['statuses']:
                        bg, fg = status_style.get(s.lower(), ('#888', '#fff'))
                        status_badges += (
                            f"<span style='background:{bg}; color:{fg}; font-size:8px; "
                            f"padding:2px 6px; border-radius:3px; font-weight:600; "
                            f"margin-right:3px; white-space:nowrap;'>{s.upper()}</span>"
                        )
                    cards_html += f"""
                    <div style='flex: 1 1 180px; min-width: 160px; max-width: 220px;
                                background: #ffffff; border-radius: 8px;
                                border-top: 4px solid {r['color']};
                                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                                padding: 12px 14px;'>
                        <div style='font-size: 9.5px; color: #555; word-break: break-all;
                                    margin-bottom: 6px; font-weight: 600; line-height: 1.3;'>{r['name']}</div>
                        <div style='font-size: 22px; font-weight: bold; color: {r['color']};
                                    line-height: 1;'>{r['total']}</div>
                        <div style='font-size: 9px; color: #888; margin-bottom: 6px;'>quarantine events</div>
                        <div style='font-size: 9px; color: #555; margin-bottom: 5px;'>
                            <span style='background: #f0f4f8; padding: 2px 6px; border-radius: 3px;'>
                                📅 {latest_str}
                            </span>
                        </div>
                        <div style='font-size: 9px; color: #555; margin-bottom: 5px;'>
                            <span style='background: #f0f4f8; padding: 2px 6px; border-radius: 3px;'>
                                🖥 {r['hosts']} host(s)
                            </span>
                        </div>
                        <div style='margin-bottom: 5px;'>{status_badges}</div>
                        <div>
                            <span style='background: {r['color']}22; color: {r['color']};
                                         font-size: 8px; padding: 2px 6px; border-radius: 3px;
                                         font-weight: 600; border: 1px solid {r['color']}55;
                                         white-space: nowrap;'>{r['month']}</span>
                        </div>
                    </div>"""
                cards_html += "</div>"
                st.markdown(cards_html, unsafe_allow_html=True)

                # Footer info cards
                total_quarantined = quarantine_data.get('overview', {}).get('total_quarantined', 0)
                unique_files_count = quarantine_data.get('overview', {}).get('unique_files', 0)
                num_months = len(all_q_months)
                st.markdown(f"""
                    <div style='display: flex; gap: 10px; margin-top: 14px;'>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>Total Quarantine Events</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{total_quarantined}</span>
                            <span style='font-size: 10px; color: #666;'> events</span>
                        </div>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>Unique Files Detected</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{unique_files_count}</span>
                            <span style='font-size: 10px; color: #666;'> files</span>
                        </div>
                        <div style='flex: 1; background: #f8f9fa; padding: 12px; border-radius: 8px;
                                    border-left: 4px solid {SECTION_HEADER_COLOR};'>
                            <strong style='color: #333; font-size: 11px;'>Months Analysed</strong><br>
                            <span style='font-size: 22px; font-weight: bold; color: {SECTION_HEADER_COLOR};'>{num_months}</span>
                            <span style='font-size: 10px; color: #666;'> month(s)</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size: 11px; color: #999; padding: 15px; text-align: center; background: white; border: 2px solid #d0d0d0; border-radius: 5px;">No quarantine file details available</div>', unsafe_allow_html=True)

        if include_chart_insights and include_quarantine_analysis and quarantine_data:
            _qov = quarantine_data.get('overview', {})
            _qtot = _qov.get('total_quarantined', 0)
            _qfiles = _qov.get('unique_files', 0)
            if _qtot > 0:
                _insight_box(f"<strong>{_qtot}</strong> quarantine event(s) recorded involving <strong>{_qfiles}</strong> unique file(s) across {month_text}.")

        # Dynamic numbering for Tactics and Techniques
        # If quarantine analysis is included: C.7 and C.8
        # If quarantine analysis is NOT included: C.5 and C.6
        tactics_num = 7 if (include_quarantine_analysis and quarantine_data) else 5
        technique_num = 8 if (include_quarantine_analysis and quarantine_data) else 6

        col1, col2 = st.columns(2)

        with col1:
            # Tactics (area chart)
            st.markdown(f'<div class="chart-title">{section_letter}.{tactics_num}. Tactics by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
            if 'tactics_by_severity' in detection_data:
                create_chart_with_pivot_logic(
                    detection_data['tactics_by_severity'],
                    rows=['Month', 'SeverityName'],
                    columns=['Tactic'],
                    values=['Count'],
                    chart_type='Area Chart',
                    height=380,
                    analysis_key='tactics_by_severity',
                    use_severity_colors=True,
                    use_monthly_colors=True
                )

        with col2:
            # Technique (area chart)
            st.markdown(f'<div class="chart-title">{section_letter}.{technique_num}. Technique by Severity Across {month_text} Trends</div>', unsafe_allow_html=True)
            if 'technique_by_severity' in detection_data:
                # Pre-sort data to put Adware/PUP first
                technique_df = detection_data['technique_by_severity'].copy()
                if 'Technique' in technique_df.columns:
                    # Create sort key: Adware/PUP first, then by total count descending
                    def sort_key(tech):
                        if pd.notna(tech) and 'Adware' in str(tech).upper() or 'PUP' in str(tech).upper():
                            return (0, str(tech))  # Priority 0 for Adware/PUP
                        return (1, str(tech))  # Priority 1 for others

                    # Calculate totals and sort
                    tech_totals = technique_df.groupby('Technique')['Count'].sum().reset_index()
                    tech_totals['sort_key'] = tech_totals['Technique'].apply(lambda x: (0 if (pd.notna(x) and ('Adware' in str(x) or 'PUP' in str(x))) else 1, -tech_totals[tech_totals['Technique']==x]['Count'].iloc[0] if len(tech_totals[tech_totals['Technique']==x]) > 0 else 0))

                create_chart_with_pivot_logic(
                    technique_df,
                    rows=['Month', 'SeverityName'],
                    columns=['Technique'],
                    values=['Count'],
                    chart_type='Area Chart',
                    height=380,
                    analysis_key='technique_by_severity_c6',  # Unique key for C.6
                    top_n={'enabled': True, 'field': 'Technique', 'n': 10, 'type': 'top', 'by_field': 'Count', 'per_month': False},
                    use_severity_colors=True,
                    use_monthly_colors=True
                )

        if include_chart_insights and 'tactics_by_severity' in detection_data:
            _tac_df = detection_data['tactics_by_severity']
            if not _tac_df.empty and 'Tactic' in _tac_df.columns and 'Count' in _tac_df.columns:
                _tac_top3 = _tac_df.groupby('Tactic')['Count'].sum().nlargest(3)
                if len(_tac_top3):
                    _tac1 = _tac_top3.index[0]
                    _tac1_c = int(_tac_top3.iloc[0])
                    _tac_others = ', '.join(_tac_top3.index[1:].tolist()) if len(_tac_top3) > 1 else ''
                    _tac_body = f"Most observed attack tactic: <strong>{_tac1}</strong> with <strong>{_tac1_c}</strong> occurrence(s)."
                    if _tac_others:
                        _tac_body += f" Also seen: {_tac_others}."
                    _insight_box(_tac_body)

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section C

    # ============================================
    # TIME-BASED ANALYSIS SECTION (DYNAMIC)
    # ============================================
    if include_time_analysis:
        section_letter = section_letters.get('time', 'C')
        st.markdown(f'<div class="section-header">{section_letter}. Time-Based Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        # Daily Trend (full width) - Use exact same logic as pivot table builder
        st.markdown(f'<div class="chart-title">{section_letter}.1. Detection Over Multiple Days Across {month_text} Trends - Top 3</div>', unsafe_allow_html=True)
        if 'daily_trends' in time_data:
            # Pre-process to remove month prefix from Date labels
            daily_df = time_data['daily_trends'].copy()
            if 'Date' in daily_df.columns:
                # Extract just the date part after the month name (e.g., "June Wed Jun 04 2025" -> "Wed Jun 04 2025")
                daily_df['Date'] = daily_df['Date'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else str(x))

            create_chart_with_pivot_logic(
                daily_df,
                rows=['Date', 'Month'],
                columns=[],
                values=['Detection Count'],
                chart_type='Bar Chart',
                height=240,
                analysis_key='daily_trends',
                top_n={'enabled': True, 'field': 'Date', 'n': 3, 'type': 'top', 'by_field': 'Detection Count', 'per_month': True},
                use_monthly_colors=True
            )

        if include_chart_insights and 'daily_trends' in time_data:
            _dtdf = time_data['daily_trends']
            if not _dtdf.empty and 'Detection Count' in _dtdf.columns:
                _dtop = _dtdf.groupby('Date')['Detection Count'].sum().nlargest(1)
                if len(_dtop):
                    _peak_date = str(_dtop.index[0])
                    _peak_date_cnt = int(_dtop.iloc[0])
                    _insight_box(f"Highest single-day activity: <strong>{_peak_date}</strong> with <strong>{_peak_date_cnt}</strong> detections.")

        # D.2 - Full width
        st.markdown(f'<div class="chart-title">{section_letter}.2. Hourly Distribution of Detections Across {month_text} Trends</div>', unsafe_allow_html=True)
        if 'hourly_analysis' in time_data:
            create_chart_with_pivot_logic(
                time_data['hourly_analysis'],
                rows=['Hour'],
                columns=[],
                values=['Detection Count'],
                chart_type='Line Chart',
                height=280,
                analysis_key='hourly_analysis',
                use_monthly_colors=False,
                sort_by='Hour',
                sort_direction='descending'
            )

        if include_chart_insights and 'hourly_analysis' in time_data:
            _hdf2 = time_data['hourly_analysis']
            if not _hdf2.empty and 'Hour' in _hdf2.columns and 'Detection Count' in _hdf2.columns:
                _htot2 = _hdf2.groupby('Hour')['Detection Count'].sum()
                if len(_htot2):
                    _ph2_raw = _htot2.idxmax()
                    try: _phi2 = int(str(_ph2_raw).split(':')[0])
                    except: _phi2 = 0
                    _pc2 = int(_htot2.max())
                    _ctx2 = "business hours" if 8 <= _phi2 <= 17 else "outside business hours"
                    _note2 = "review for insider threat patterns" if 8 <= _phi2 <= 17 else "may indicate automated or off-hours malicious activity"
                    _insight_box(f"Peak detection hour: <strong>{_ph2_raw}</strong> ({_ctx2}) with <strong>{_pc2}</strong> alerts.")

        # D.3 - Full width
        st.markdown(f'<div class="chart-title">{section_letter}.3. Detection Frequency by Day of Week Across {month_text} Trends</div>', unsafe_allow_html=True)
        if 'day_of_week' in time_data:
            create_chart_with_pivot_logic(
                time_data['day_of_week'],
                rows=['Day', 'Type'],
                columns=[],
                values=['Detection Count'],
                chart_type='Bar Chart',
                height=280,
                analysis_key='day_of_week',
                use_monthly_colors=False,
                sort_by='Day',
                sort_direction='descending'
            )

        if include_chart_insights and 'day_of_week' in time_data:
            _dowdf = time_data['day_of_week']
            if not _dowdf.empty and 'Day' in _dowdf.columns and 'Detection Count' in _dowdf.columns:
                _dtot2 = _dowdf.groupby('Day')['Detection Count'].sum()
                if len(_dtot2):
                    _peak_dow = _dtot2.idxmax()
                    _peak_dow_cnt = int(_dtot2.max())
                    _is_wknd = _peak_dow in ['Saturday', 'Sunday']
                    _note_dow = "weekend activity warrants investigation for unauthorized or automated access" if _is_wknd else "weekday peak aligns with typical business operations — review for insider activity"
                    _insight_box(f"Highest detection day: <strong>{_peak_dow}</strong> with <strong>{_peak_dow_cnt}</strong> alerts.")

        st.markdown('</div>', unsafe_allow_html=True)  # Close Section D

    # ============================================
    # EXECUTIVE SUMMARY SECTION (DYNAMIC)
    # ============================================
    if include_executive_summary:
        section_letter = section_letters.get('executive', 'E')
        render_executive_summary(
            ticket_data=ticket_data,
            host_data=host_data,
            detection_data=detection_data,
            time_data=time_data,
            num_months=num_months,
            section_letter=section_letter
        )


def create_chart_with_pivot_logic(df, rows, columns, values, chart_type, height, analysis_key, top_n=None, use_severity_colors=False, use_ticket_status_colors=False, use_monthly_colors=False, sort_by=None, sort_direction='descending'):
    """
    Create chart using the EXACT same logic as pivot_table_builder.py
    This ensures consistency across all dashboards
    """
    # Create config dict (same structure as pivot_table_builder)
    config = {
        'rows': rows,
        'columns': columns,
        'values': values,
        'aggregation': 'sum',
        'chart_type': chart_type,
        'sort_by_field': sort_by if sort_by else 'Value (Detection Count)',
        'chart_sort_direction': sort_direction,
        'filters': {},
        'top_n': top_n,
        'use_severity_colors': use_severity_colors,
        'use_ticket_status_colors': use_ticket_status_colors,
        'use_monthly_colors': use_monthly_colors
    }
    
    try:
        # Apply TOP N filter if specified (before creating pivot)
        filtered_df = df.copy()
        
        if top_n and top_n.get('enabled'):
            filter_field = top_n['field']
            n_value = top_n['n']
            filter_type = top_n['type']
            by_field = top_n['by_field']
            per_month = top_n.get('per_month', False)
            
            if filter_field in filtered_df.columns and by_field in filtered_df.columns:
                if per_month and 'Month' in filtered_df.columns:
                    # Apply Top N per month
                    all_top_items = []
                    months = filtered_df['Month'].unique()
                    
                    for month in months:
                        month_df = filtered_df[filtered_df['Month'] == month]
                        totals = month_df.groupby(filter_field)[by_field].sum().reset_index()
                        totals = totals.rename(columns={by_field: '_total'})
                        
                        if filter_type == 'top':
                            top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                        else:
                            top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()
                        
                        for item in top_items:
                            all_top_items.append((month, item))
                    
                    filtered_df = filtered_df[
                        filtered_df.apply(lambda row: (row['Month'], row[filter_field]) in all_top_items, axis=1)
                    ]
                else:
                    # Global Top N filtering
                    totals = filtered_df.groupby(filter_field)[by_field].sum().reset_index()
                    totals = totals.rename(columns={by_field: '_total'})
                    
                    if filter_type == 'top':
                        top_items = totals.nlargest(n_value, '_total')[filter_field].tolist()
                    else:
                        top_items = totals.nsmallest(n_value, '_total')[filter_field].tolist()
                    
                    filtered_df = filtered_df[filtered_df[filter_field].isin(top_items)]
        
        # Create pivot table using the exact function from pivot_table_builder
        pivot_table = create_pivot_table(filtered_df, config, analysis_key)

        # Strip 'Total' rows/columns added by margins=True — they appear as unwanted bars in charts
        if pivot_table is not None and not pivot_table.empty:
            for _rc in rows:
                if _rc in pivot_table.columns:
                    pivot_table = pivot_table[pivot_table[_rc].astype(str) != 'Total']
            if 'Total' in pivot_table.columns:
                pivot_table = pivot_table.drop(columns=['Total'])

        if pivot_table is not None and not pivot_table.empty:
            # Create chart using the exact function from pivot_table_builder
            chart = create_pivot_chart(pivot_table, chart_type, height, config, analysis_key)

            if chart:
                # Apply PDF-specific styling to the chart
                apply_pdf_chart_styling(chart, analysis_key)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("⚠️ Could not create chart for this analysis")
        else:
            st.warning("⚠️ No data available for this analysis")
            
    except Exception as e:
        st.error(f"❌ Error creating chart: {str(e)}")
        st.info("💡 This might be due to missing or incompatible data fields")


def apply_pdf_chart_styling(chart, analysis_key=None):
    """
    Apply PDF-specific styling to charts:
    - Chart Titles: Arial 14pt bold
    - Axes/Labels/Legends: Arial 12pt
    - Data Labels: Black text on white background boxes, Arial 12pt, outside end
    """
    if chart is None:
        return

    # Preserve existing axis titles (e.g., "Total Tactics Count", "Total Technique Count")
    existing_xaxis_title = chart.layout.xaxis.title.text if chart.layout.xaxis.title else None
    existing_yaxis_title = chart.layout.yaxis.title.text if chart.layout.yaxis.title else None

    # Add specific x-axis titles for B.5 and B.6
    if analysis_key == 'tactics_by_severity':
        existing_xaxis_title = 'Tactic'
    elif analysis_key == 'technique_by_severity_b6':
        existing_xaxis_title = 'Technique'

    # Determine if this is a tactic/technique chart (many legend items — needs compact legend)
    _is_compact_legend_chart = (
        'technique_by_severity' in (analysis_key or '') or
        'tactics_by_severity' in (analysis_key or '')
    )
    # Font size: 8 for tactic/technique charts (many items), 11 for everything else
    legend_font_size = 8 if _is_compact_legend_chart else 11

    # Build legend config — compact for tactic/technique charts to avoid scrolling
    _legend_cfg = dict(
        font=dict(family='Arial', size=legend_font_size, color='#333333'),
        traceorder='reversed',  # Show highest values at top
        itemsizing='constant',  # Prevent scrolling
    )
    if _is_compact_legend_chart:
        # Compact vertical legend: tighten row gaps and cap item width
        _legend_cfg.update(dict(
            tracegroupgap=0,
            itemwidth=30,
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='#e5e7eb',
            borderwidth=1,
        ))

    # Update layout with PDF fonts - optimized for 2-page readability
    chart.update_layout(
        # Remove chart title completely (we use HTML titles above charts instead)
        title='',
        showlegend=True,
        # Axes: Arial 11pt
        xaxis=dict(
            title=existing_xaxis_title,
            title_font=dict(family='Arial', size=11, color='#333333'),
            tickfont=dict(family='Arial', size=10, color='#333333')
        ),
        yaxis=dict(
            title=existing_yaxis_title,
            title_font=dict(family='Arial', size=11, color='#333333'),
            tickfont=dict(family='Arial', size=10, color='#333333')
        ),
        legend=_legend_cfg,
        # Uniform styling - readable
        font=dict(
            family='Arial',
            size=11,
            color='#333333'
        ),
        # Better margins for 2-page layout
        margin=dict(
            l=45,
            r=40,
            t=40,
            b=45
        )
    )

    # Update traces individually based on chart type
    for i, trace in enumerate(chart.data):
        if trace.type == 'bar':
            # Bar charts: Show data labels outside with black text
            # Get the values (y for vertical bars, x for horizontal bars)
            if hasattr(trace, 'orientation') and trace.orientation == 'h':
                # Horizontal bars (like B.4 Files)
                values = trace.x if hasattr(trace, 'x') else []
            else:
                # Vertical bars
                values = trace.y if hasattr(trace, 'y') else []

            # Hide labels for zero values - set empty string for zeros
            text_values = []
            for val in values:
                if val is not None and val != 0:
                    text_values.append(str(int(val)) if isinstance(val, (int, float)) else str(val))
                else:
                    text_values.append('')  # Empty string for zero or None

            trace.update(
                text=text_values,
                textposition='outside',
                textfont=dict(
                    family='Arial',
                    size=10,
                    color='#000000'
                ),
                cliponaxis=False
            )
        elif trace.type in ['scatter', 'scattergl']:
            # Line/Scatter charts: Show values on top of markers
            if trace.mode and 'markers' in trace.mode:
                # Get y values for text labels
                y_values = trace.y if hasattr(trace, 'y') else []
                text_values = [str(int(val)) if isinstance(val, (int, float)) and val != 0 else '' for val in y_values]

                trace.update(
                    text=text_values,
                    textfont=dict(
                        family='Arial',
                        size=10,
                        color='#000000'
                    ),
                    textposition='top center',
                    mode='lines+markers+text',
                    cliponaxis=False
                )

    # Add extra y-axis headroom for line charts so peak labels aren't clipped
    has_scatter = any(t.type in ['scatter', 'scattergl'] for t in chart.data)
    if has_scatter:
        all_y = []
        for t in chart.data:
            if t.type in ['scatter', 'scattergl'] and hasattr(t, 'y') and t.y is not None:
                all_y.extend([v for v in t.y if v is not None and isinstance(v, (int, float))])
        if all_y:
            y_max = max(all_y)
            chart.update_layout(yaxis=dict(range=[0, y_max * 1.25]))


def check_data_availability() -> bool:
    """Check if required data is available in session state"""
    return (
        'host_analysis_results' in st.session_state or
        'detection_analysis_results' in st.session_state or
        'time_analysis_results' in st.session_state or
        'ticket_lifecycle_results' in st.session_state
    )


def extract_months_from_data(host_data, detection_data, time_data):
    """Extract month names from available data"""
    months = []

    # Try to get months from different data sources
    if host_data and 'overview_key_metrics' in host_data:
        df = host_data['overview_key_metrics']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    if not months and detection_data and 'severity_trend' in detection_data:
        df = detection_data['severity_trend']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    if not months and time_data and 'daily_trends' in time_data:
        df = time_data['daily_trends']
        if 'Month' in df.columns:
            months = df['Month'].unique().tolist()

    # Default fallback
    if not months:
        months = ['Month 1', 'Month 2', 'Month 3']

    return months[:3]  # Limit to 3 months


if __name__ == "__main__":
    falcon_dashboard_pdf_layout()
