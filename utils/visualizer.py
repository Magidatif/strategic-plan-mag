import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import COLORS

def get_plotly_layout(is_dark=True):
    text_color = '#F8FAFC' if is_dark else '#000000'
    muted_color = '#94A3B8' if is_dark else '#64748B'
    
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=text_color, size=13),
        margin=dict(l=60, r=20, t=60, b=100),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color=muted_color)
        )
    )

def create_overall_completion_gauge(completion_avg, is_dark=True):
    """Render a semi-circle gauge meter for total completion percentage"""
    text_color = '#F8FAFC' if is_dark else '#000000'
    bg_color = "#1E293B" if is_dark else "#F1F5F9"
    border_color = "#334155" if is_dark else "#CBD5E1"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=completion_avg,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Average Overall Completion Rate", 'font': {'size': 18, 'color': text_color}},
        number={'suffix': "%", 'font': {'size': 36, 'color': '#14B8A6', 'weight': 800}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': border_color},
            'bar': {'color': "#14B8A6", 'thickness': 0.3},
            'bgcolor': bg_color,
            'borderwidth': 1,
            'bordercolor': border_color,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [40, 75], 'color': 'rgba(59, 130, 246, 0.2)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#10B981", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=260, **get_plotly_layout(is_dark))
    return fig

def create_status_donut_chart(df, is_dark=True):
    """Render status distribution donut chart"""
    status_counts = df['STATUS_std'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    color_map = {
        'Completed': COLORS['completed'],
        'In Progress': COLORS['in_progress'],
        'Delayed': COLORS['delayed']
    }
    
    labels_en = {
        'Completed': 'Completed',
        'in progress': 'In Progress',
        'delayed': 'Delayed'
    }
    status_counts['Status_EN'] = status_counts['Status'].map(labels_en)
    
    fig = px.pie(
        status_counts, 
        values='Count', 
        names='Status_EN',
        color='Status_EN',
        color_discrete_map=color_map,
        hole=0.5,
        title="Activity Execution Status Breakdown"
    )
    
    border_color = '#0F172A' if is_dark else '#FFFFFF'
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label+value',
        marker=dict(line=dict(color=border_color, width=2))
    )
    fig.update_layout(height=300, **get_plotly_layout(is_dark))
    return fig

def create_department_performance_chart(df, is_dark=True):
    """Render completion rate ranking per department"""
    dept_df = df.groupby('responsable dep')['completion_numeric'].agg(['mean', 'count']).reset_index()
    dept_df.columns = ['Department', 'Avg_Completion', 'Total_Tasks']
    dept_df = dept_df.sort_values(by='Avg_Completion', ascending=True)
    
    fig = px.bar(
        dept_df,
        y='Department',
        x='Avg_Completion',
        orientation='h',
        text=dept_df['Avg_Completion'].apply(lambda x: f"{x:.1f}%"),
        color='Avg_Completion',
        color_continuous_scale=['#EF4444', '#3B82F6', '#10B981'],
        labels={'Department': 'Responsible Department', 'Avg_Completion': 'Avg Completion Rate (%)'},
        title="Completion Rate by Responsible Department"
    )
    
    border_color = '#0F172A' if is_dark else '#FFFFFF'
    grid_color = '#334155' if is_dark else '#E2E8F0'
    
    text_color = '#F8FAFC' if is_dark else '#000000'
    fig.update_traces(
        textposition='outside',
        textfont=dict(color=text_color, size=14),
        marker=dict(line=dict(color=border_color, width=1))
    )
    fig.update_layout(
        height=max(350, len(dept_df) * 35),
        coloraxis_showscale=False,
        xaxis=dict(range=[0, 120], gridcolor=grid_color),
        yaxis=dict(gridcolor=grid_color, title="", automargin=True),
        **get_plotly_layout(is_dark)
    )
    fig.update_layout(margin=dict(l=250, r=40))
    return fig

def create_objective_progress_chart(df, is_dark=True):
    """Render completion rate per Strategic Objective"""
    obj_df = df.groupby('STRATEGIC OBJECTIVES')['completion_numeric'].mean().reset_index()
    obj_df.columns = ['Objective', 'Avg_Completion']
    
    obj_df['Short_Objective'] = obj_df['Objective'].apply(lambda x: str(x)[:70] + '...' if len(str(x)) > 70 else str(x))
    obj_df = obj_df.sort_values(by='Avg_Completion', ascending=True)
    
    fig = px.bar(
        obj_df,
        y='Short_Objective',
        x='Avg_Completion',
        orientation='h',
        hover_data={'Objective': True, 'Short_Objective': False, 'Avg_Completion': ':.1f%'},
        color='Avg_Completion',
        color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
        title="Completion Rate by Strategic Objective"
    )
    grid_color = '#334155' if is_dark else '#E2E8F0'
    
    text_color = '#F8FAFC' if is_dark else '#000000'
    fig.update_traces(
        text=obj_df['Avg_Completion'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        textfont=dict(color=text_color, size=14)
    )
    fig.update_layout(
        height=max(300, len(obj_df) * 45),
        coloraxis_showscale=False,
        xaxis=dict(range=[0, 120], gridcolor=grid_color),
        yaxis=dict(gridcolor=grid_color, title="", automargin=True),
        **get_plotly_layout(is_dark)
    )
    fig.update_layout(margin=dict(l=250, r=40))
    return fig

def create_priority_status_chart(df, is_dark=True):
    """Stacked bar chart showing status breakdown across priority levels"""
    priority_status = df.groupby(['Priority', 'STATUS_std']).size().reset_index(name='Count')
    labels_en = {'Completed': 'Completed', 'in progress': 'In Progress', 'delayed': 'Delayed'}
    priority_status['Status_EN'] = priority_status['STATUS_std'].map(labels_en)
    
    color_map = {
        'Completed': COLORS['completed'],
        'In Progress': COLORS['in_progress'],
        'Delayed': COLORS['delayed']
    }
    
    grid_color = '#334155' if is_dark else '#E2E8F0'
    
    priority_status['Text_Label'] = priority_status['Status_EN'] + ': ' + priority_status['Count'].astype(str)
    
    fig = px.bar(
        priority_status,
        x='Priority',
        y='Count',
        color='Status_EN',
        text='Text_Label',
        color_discrete_map=color_map,
        barmode='group',
        labels={'Priority': 'Priority Level', 'Count': 'Number of Activities', 'Status_EN': 'Status'},
        title="Activities Distribution by Priority & Execution Status"
    )
    text_color = '#F8FAFC' if is_dark else '#000000'
    fig.update_traces(
        textposition='outside',
        textfont=dict(color=text_color, size=11),
        textangle=-90
    )
    fig.update_layout(height=380, xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color), **get_plotly_layout(is_dark))
    return fig

def create_gap_summary_chart(gap_df, is_dark=True):
    """Render Gap Causes & Department Risk chart for Tab 3"""
    if gap_df.empty:
        return None
        
    gap_counts = gap_df['responsable dep'].value_counts().reset_index()
    gap_counts.columns = ['Department', 'Gap_Count']
    gap_counts = gap_counts.head(10).sort_values(by='Gap_Count', ascending=True)
    
    grid_color = '#334155' if is_dark else '#E2E8F0'
    
    fig = px.bar(
        gap_counts,
        y='Department',
        x='Gap_Count',
        orientation='h',
        text='Gap_Count',
        color='Gap_Count',
        color_continuous_scale=['#F59E0B', '#EF4444'],
        title="Top Departments with Operational Gaps & Delays"
    )
    text_color = '#F8FAFC' if is_dark else '#0F172A'
    fig.update_traces(
        textposition='outside',
        textfont=dict(color=text_color, size=14)
    )
    fig.update_layout(height=280, coloraxis_showscale=False, xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color, title="", automargin=True), **get_plotly_layout(is_dark))
    fig.update_layout(margin=dict(l=250, r=40))
    return fig
