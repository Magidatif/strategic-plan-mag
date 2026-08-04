import streamlit as st
import pandas as pd
import datetime
import io

# Set page config FIRST before any other streamlit commands
st.set_page_config(
    page_title="Governorates Strategic Plan Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import GOOGLE_SHEET_URL, COLORS, STATUS_MAP_EN, PRIORITY_MAP_EN
from utils.data_loader import load_data
from utils.visualizer import (
    create_overall_completion_gauge,
    create_status_donut_chart,
    create_department_performance_chart,
    create_objective_progress_chart,
    create_priority_status_chart,
    create_gap_summary_chart
)

# Load Base CSS
def inject_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

inject_css()

# Sidebar Theme Switcher & Controls
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
        <p style="font-size: 12px; color: #64748B; margin-bottom: 2px;">Design & Development:</p>
        <p style="font-size: 14px; font-weight: 700; color: #0F172A; margin-bottom: 5px;">MAG Healthcare Solutions</p>
        <p style="font-size: 13px; color: #10B981; font-weight: 600;">📱 WhatsApp: +20 15 05378760</p>
    </div>
    """, unsafe_allow_html=True)
    
    is_dark = False
    
    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 15px;">
        <span class="sync-badge">🟢 Connected Live to Sheet</span><br>
        <small style="color: {'#94A3B8' if is_dark else '#64748B'};">Cache Expiration: 30s</small>
    </div>
    """, unsafe_allow_html=True)
    
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_ref2:
        st.markdown(f'<a href="{GOOGLE_SHEET_URL}" target="_blank" style="text-decoration: none;"><button style="width: 100%; height: 38px; border-radius: 8px; background: #334155; color: white; border: none; cursor: pointer;">📂 Open Sheet</button></a>', unsafe_allow_html=True)
        
    st.divider()
    st.subheader("🔍 Filters & Options")
    
    # Fetch Data
    df_raw, last_updated, error_msg = load_data()

    if not df_raw.empty:
        # Filter 1: Governorate / Branch
        branches = ['All'] + sorted([str(x) for x in df_raw['Branch Name'].unique() if str(x) != 'غير محدد'])
        selected_branch = st.selectbox("📍 Governorate / Branch:", branches)
        
        # Filter 2: Strategic Objective
        objectives = ['All'] + sorted([str(x) for x in df_raw['STRATEGIC OBJECTIVES'].unique() if str(x) != 'غير محدد'])
        selected_objective = st.selectbox("🎯 Strategic Objective:", objectives)
        
        # Filter 3: Responsible Department
        departments = ['All'] + sorted([str(x) for x in df_raw['responsable dep'].unique() if str(x) != 'غير محدد'])
        selected_department = st.selectbox("🏛️ Responsible Dept:", departments)
        
        # Filter 4: Status
        statuses = ['All', 'Completed', 'In Progress', 'Delayed']
        selected_status_filter = st.selectbox("🚦 Execution Status:", statuses)
        
        # Filter 5: Priority
        priorities = ['All', 'High', 'Medium']
        selected_priority = st.selectbox("⚡ Priority Level:", priorities)

# Card colors based on theme
kpi_bg = "rgba(30, 41, 59, 0.8)" if is_dark else "#FFFFFF"
kpi_border = "rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0"
kpi_title_color = "#94A3B8" if is_dark else "#64748B"
kpi_val_color = "#F8FAFC" if is_dark else "#0F172A"

# Header Banner
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1>🏥 Governorates Strategic Plan Executive Dashboard</h1>
            <p>Real-time KPI Tracking, Operational Performance, Completion Analytics & Gap Controls — Live Google Sheets Sync</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle Fetch Errors
if error_msg:
    st.error(f"❌ Error connecting to Google Sheets: {error_msg}")
    st.info("Please verify internet connection and sheet sharing permissions.")
    st.stop()

if df_raw.empty:
    st.warning("⚠️ No data available in the Google Sheet.")
    st.stop()

# Apply Filters to DataFrame
df_filtered = df_raw.copy()

if selected_branch != 'All':
    df_filtered = df_filtered[df_filtered['Branch Name'] == selected_branch]

if selected_objective != 'All':
    df_filtered = df_filtered[df_filtered['STRATEGIC OBJECTIVES'] == selected_objective]

if selected_department != 'All':
    df_filtered = df_filtered[df_filtered['responsable dep'] == selected_department]

if selected_status_filter != 'All':
    status_map_lookup = {'Completed': 'Completed', 'In Progress': 'in progress', 'Delayed': 'delayed'}
    df_filtered = df_filtered[df_filtered['STATUS_std'] == status_map_lookup[selected_status_filter]]

if selected_priority != 'All':
    df_filtered = df_filtered[df_filtered['Priority'] == selected_priority]

# Compute Key Metrics
total_activities = len(df_filtered)
completed_count = len(df_filtered[df_filtered['STATUS_std'] == 'Completed'])
in_progress_count = len(df_filtered[df_filtered['STATUS_std'] == 'in progress'])
delayed_count = len(df_filtered[df_filtered['STATUS_std'] == 'delayed'])
avg_completion = df_filtered['completion_numeric'].mean() if total_activities > 0 else 0.0

# Render Top KPI Cards Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="background: {kpi_bg}; border: 1px solid {kpi_border};">
        <div class="kpi-title" style="color: {kpi_title_color};">Total Activities</div>
        <div class="kpi-value" style="color: {kpi_val_color};">{total_activities}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card kpi-rate" style="background: {kpi_bg}; border: 1px solid {kpi_border};">
        <div class="kpi-title" style="color: {kpi_title_color};">Avg Completion</div>
        <div class="kpi-value" style="color: #14B8A6;">{avg_completion:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card kpi-completed" style="background: {kpi_bg}; border: 1px solid {kpi_border};">
        <div class="kpi-title" style="color: {kpi_title_color};">Completed</div>
        <div class="kpi-value" style="color: #10B981;">{completed_count}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card kpi-in-progress" style="background: {kpi_bg}; border: 1px solid {kpi_border};">
        <div class="kpi-title" style="color: {kpi_title_color};">In Progress</div>
        <div class="kpi-value" style="color: #3B82F6;">{in_progress_count}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card kpi-delayed" style="background: {kpi_bg}; border: 1px solid {kpi_border};">
        <div class="kpi-title" style="color: {kpi_title_color};">Delayed</div>
        <div class="kpi-value" style="color: #EF4444;">{delayed_count}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Dashboard Tabs
tab_overview, tab_departments, tab_gaps, tab_data = st.tabs([
    "📊 Executive Summary & Strategic Objectives",
    "🏛️ Department Operational Performance",
    "⚠️ Operational Gap Analysis & Controls",
    "📋 Master Strategic Data Table & Export"
])

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab_overview:
    st.subheader("📈 Overall Completion & Execution Analytics")
    
    # Progress Bar Meter
    progress_val = min(max(float(avg_completion) / 100.0, 0.0), 1.0)
    st.write(f"**Overall Strategic Completion Meter:** `{avg_completion:.1f}%`")
    st.progress(progress_val)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### ⏱️ Overall Completion Gauge")
    gauge_fig = create_overall_completion_gauge(avg_completion, is_dark=is_dark)
    st.plotly_chart(gauge_fig, use_container_width=True, key=f"gauge_{is_dark}", theme=None)
        
    st.divider()

    st.markdown("#### 🍩 Execution Status Breakdown")
    donut_fig = create_status_donut_chart(df_filtered, is_dark=is_dark)
    st.plotly_chart(donut_fig, use_container_width=True, key=f"donut_{is_dark}", theme=None)
    
    st.divider()
    
    st.markdown("#### 🎯 Completion Rate by Strategic Objective")
    obj_fig = create_objective_progress_chart(df_filtered, is_dark=is_dark)
    st.plotly_chart(obj_fig, use_container_width=True, key=f"obj_{is_dark}", theme=None)
        
    st.divider()

    st.markdown("#### ⚡ Priority & Execution Status Breakdown")
    prio_fig = create_priority_status_chart(df_filtered, is_dark=is_dark)
    st.plotly_chart(prio_fig, use_container_width=True, key=f"prio_{is_dark}", theme=None)

# --- TAB 2: DEPARTMENT PERFORMANCE ---
with tab_departments:
    st.markdown("### 🏛️ Department Workload & Performance Ranking")
    dept_fig = create_department_performance_chart(df_filtered, is_dark=is_dark)
    st.plotly_chart(dept_fig, use_container_width=True, key=f"dept_{is_dark}", theme=None)
    
    st.divider()
    st.markdown("### 📊 Task Status Breakdown per Department")
    dept_status_summary = df_filtered.groupby(['responsable dep', 'STATUS_std']).size().unstack(fill_value=0)
    
    rename_dict = {}
    if 'Completed' in dept_status_summary.columns: rename_dict['Completed'] = 'Completed 🟢'
    if 'in progress' in dept_status_summary.columns: rename_dict['in progress'] = 'In Progress 🔵'
    if 'delayed' in dept_status_summary.columns: rename_dict['delayed'] = 'Delayed 🔴'
    
    dept_status_summary = dept_status_summary.rename(columns=rename_dict)
    dept_status_summary.index.name = 'Department'
    
    # Native Streamlit visual chart for Department Status
    st.bar_chart(dept_status_summary)
    
    th_styles = [{'selector': 'th', 'props': [('color', 'black'), ('font-weight', 'bold')]}]
    
    with st.expander("📋 View Department Data Summary Table"):
        st.dataframe(dept_status_summary.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}).set_table_styles(th_styles), use_container_width=True)

# --- TAB 3: GAP ANALYSIS & RISKS ---
with tab_gaps:
    st.markdown("### ⚠️ Operational Gap Control & Corrective Action Matrix")
    st.info("💡 Highlighting activities with operational gaps, high priorities, or delayed status requiring immediate intervention.")
    
    gap_df = df_filtered[(df_filtered['STATUS_std'] == 'delayed') | 
                         (df_filtered['Priority'] == 'High') | 
                         (df_filtered['Gap'].notna() & (df_filtered['Gap'] != ''))]
    
    gap_fig = create_gap_summary_chart(gap_df, is_dark=is_dark)
    if gap_fig:
        try:
            st.plotly_chart(gap_fig, use_container_width=True, key=f"gap_chart_{is_dark}", theme=None)
        except Exception:
            gap_depts = gap_df['responsable dep'].value_counts()
            st.bar_chart(gap_depts)
        st.divider()
    
    if gap_df.empty:
        st.success("🎉 No high-risk operational gaps or delayed activities found in current selection!")
    else:
        display_gap_cols = [
            'Branch Name', 'STRATEGIC OBJECTIVES', 'Activity', 'Priority', 
            'completion_numeric', 'Gap Cause', 'Proposed Action', 'Required Resources', 'responsable dep'
        ]
        
        show_gap_df = gap_df[display_gap_cols].copy()
        show_gap_df.columns = [
            'Branch/Governorate', 'Strategic Objective', 'Activity', 'Priority', 
            'Completion %', 'Gap Cause', 'Proposed Action', 'Required Resources', 'Department'
        ]
        
        th_styles = [{'selector': 'th', 'props': [('color', 'black'), ('font-weight', 'bold')]}]
        st.dataframe(
            show_gap_df.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}).set_table_styles(th_styles),
            column_config={
                "Completion %": st.column_config.ProgressColumn(
                    "Completion %",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            use_container_width=True,
            hide_index=True
        )

# --- TAB 4: MASTER DATA TABLE & EXPORT ---
with tab_data:
    st.markdown("### 📋 Complete Strategic Activities Master Directory")
    
    col_search, col_export = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("🔍 Search Activity, KPI, or Department:", "")
        
    master_display = df_filtered.copy()
    if search_query:
        mask = (
            master_display['Activity'].str.contains(search_query, case=False, na=False) |
            master_display['KPI'].str.contains(search_query, case=False, na=False) |
            master_display['responsable dep'].str.contains(search_query, case=False, na=False) |
            master_display['OUTCOMES / PROGRAMS'].str.contains(search_query, case=False, na=False)
        )
        master_display = master_display[mask]
        
    with col_export:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            master_display.to_excel(writer, index=False, sheet_name='StrategicPlan')
        
        st.download_button(
            label="📥 Export to Excel",
            data=buffer.getvalue(),
            file_name=f"Strategic_Plan_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    display_cols_master = [
        'Branch Name', 'STRATEGIC OBJECTIVES', 'OUTCOMES / PROGRAMS', 'Activity', 
        'KPI', 'Target', 'Current Value', 'completion_numeric', 'STATUS_std', 'Priority', 'responsable dep'
    ]
    
    table_df = master_display[display_cols_master].copy()
    table_df.columns = [
        'Governorate', 'Strategic Objective', 'Program / Outcome', 'Activity', 
        'KPI', 'Target', 'Current Value', 'Completion Rate', 'Status', 'Priority', 'Department'
    ]
    
    table_df['Status'] = table_df['Status'].map(STATUS_MAP_EN)
    table_df['Priority'] = table_df['Priority'].map(PRIORITY_MAP_EN)
    
    th_styles = [{'selector': 'th', 'props': [('color', 'black'), ('font-weight', 'bold')]}]
    st.dataframe(
        table_df.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}).set_table_styles(th_styles),
        column_config={
            "Completion Rate": st.column_config.ProgressColumn(
                "Completion %",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
        },
        use_container_width=True,
        hide_index=True
    )
