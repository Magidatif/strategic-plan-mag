import pandas as pd
import requests
import io
import re
import streamlit as st
import datetime
from config import SHEET_SOURCES, CACHE_TTL_SECONDS

# Session reuse for HTTP Connection Pooling (much faster fetches)
session = requests.Session()

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_data():
    """
    High-performance live data fetcher for Google Sheets multi-worksheet workbook.
    Utilizes HTTP connection pooling and vectorized pandas operations.
    """
    try:
        all_dfs = []
        for sheet_id, expected_branch_name in SHEET_SOURCES.items():
            try:
                xlsx_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                resp = session.get(xlsx_url, timeout=15)
                if resp.status_code != 200:
                    continue
                
                df_dict = pd.read_excel(io.BytesIO(resp.content), engine='openpyxl', sheet_name=None)
                
                for tab_name, df_tab in df_dict.items():
                    try:
                        # Hardcode the known branch name from config instead of guessing from arbitrary columns
                        df_tab['Branch Name'] = expected_branch_name
                        all_dfs.append(df_tab)
                    except Exception:
                        continue
            except Exception:
                continue
                
        if not all_dfs:
            return pd.DataFrame(), None, "Failed to load worksheet data"
            
        df = pd.concat(all_dfs, ignore_index=True)
        
        # Ensure key columns exist
        expected_cols = [
            'Branch Name', 'S.G sr', 'STRATEGIC OBJECTIVES', 'OUTCOMES / PROGRAMS', 
            'Activity', 'Sub-Activity', 'Timeframe (days)', 'Start Date', 'Due Date', 
            'KPI', 'Baseline', 'Target', 'Current Value', 'Frequency', 'Data Source', 
            'Gap', 'Gap Cause', 'Priority', 'Proposed Action', 'Required Resources', 
            'notes', 'completion rate', 'STATUS', 'month', 'responsable dep'
        ]
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
                
        # Vectorized cleaning for completion rate
        completion_str = df['completion rate'].astype(str).str.replace('%', '', regex=False).str.strip()
        df['completion_numeric'] = pd.to_numeric(completion_str, errors='coerce').fillna(0.0)
        
        # Convert decimal values e.g. 0.75 -> 75%
        mask_decimal = (df['completion_numeric'] > 0) & (df['completion_numeric'] <= 1.0) & (~df['completion rate'].astype(str).str.contains('%', na=False))
        df.loc[mask_decimal, 'completion_numeric'] = df.loc[mask_decimal, 'completion_numeric'] * 100.0
        
        # Standardize STATUS
        df['STATUS_clean'] = df['STATUS'].astype(str).str.strip().str.lower()
        df['STATUS_std'] = 'in progress'
        df.loc[df['STATUS_clean'].str.contains('complete', na=False), 'STATUS_std'] = 'Completed'
        df.loc[df['STATUS_clean'].str.contains('delay', na=False), 'STATUS_std'] = 'delayed'
        
        # Standardize Priority
        df['Priority_clean'] = df['Priority'].astype(str).str.strip().str.lower()
        df['Priority'] = 'Unspecified'
        df.loc[df['Priority_clean'].str.contains('high|عاجل|أول|اول|قصوى', regex=True, na=False), 'Priority'] = 'High'
        df.loc[df['Priority_clean'].str.contains('medium|midium|ثاني|متوسط', regex=True, na=False), 'Priority'] = 'Medium'
        df.loc[df['Priority_clean'].str.contains('low|ثالث|ضعيف|منخفض', regex=True, na=False), 'Priority'] = 'Low'

        # Clean string columns
        string_cols = ['Branch Name', 'STRATEGIC OBJECTIVES', 'OUTCOMES / PROGRAMS', 
                       'Activity', 'Sub-Activity', 'Priority', 'responsable dep', 'month', 'Gap Cause',
                       'KPI', 'Target', 'Current Value', 'Data Source', 'Gap', 'Proposed Action', 
                       'Required Resources', 'notes']
        for col in string_cols:
            df[col] = df[col].astype(str).str.strip().replace({'nan': 'Unspecified', 'None': 'Unspecified', '': 'Unspecified'})
            
        last_updated = datetime.datetime.now().strftime("%H:%M:%S")
        return df, last_updated, None
        
    except Exception as e:
        return pd.DataFrame(), None, str(e)
