import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — accepts ANY CSV, no schema requirements
# ─────────────────────────────────────────────────────────────────────────────

def get_data():
    """
    Master data loader. Returns uploaded CSV if present, otherwise synthetic demo.
    NO column requirements — works with any dataset.
    """
    if st.session_state.get('uploaded_df') is not None:
        return st.session_state['uploaded_df']
    return load_demo_data()

def get_filtered_data():
    """Apply global filters (if set) to active dataset."""
    df = get_data()
    if 'global_filter_col' in st.session_state and 'global_filter_vals' in st.session_state:
        col = st.session_state['global_filter_col']
        vals = st.session_state['global_filter_vals']
        if col and col in df.columns and vals:
            df = df[df[col].isin(vals)]
    return df

# ─────────────────────────────────────────────────────────────────────────────
# COLUMN TYPE DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def get_numeric_cols(df):
    return df.select_dtypes(include='number').columns.tolist()

def get_categorical_cols(df):
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def get_date_col(df):
    """Return the first datetime column, or None."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    # Try to find a column that looks like a date
    for col in df.columns:
        try:
            sample = df[col].dropna().iloc[:5]
            pd.to_datetime(sample)
            return col
        except:
            pass
    return None

def auto_metric(df):
    """Pick the first numeric column as default metric."""
    nums = get_numeric_cols(df)
    return nums[0] if nums else None

def auto_group(df):
    """Pick the first low-cardinality categorical column as default group."""
    cats = get_categorical_cols(df)
    for c in cats:
        if 1 < df[c].nunique() <= 50:
            return c
    return cats[0] if cats else None

def infer_and_coerce_dates(df):
    """Attempt to parse any columns that look like dates into datetime."""
    df = df.copy()
    for col in df.select_dtypes(include='object').columns:
        if df[col].nunique() < len(df) * 0.95:  # skip high-cardinality text
            continue
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors='coerce')
            if parsed.notna().mean() > 0.7:  # >70% parsed successfully
                df[col] = parsed
        except:
            pass
    return df

# ─────────────────────────────────────────────────────────────────────────────
# DEMO FALLBACK DATA
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_demo_data():
    np.random.seed(42)
    companies = [
        {"company": "Quantum Dynamics", "sector": "Technology", "region": "North America"},
        {"company": "Stellar Networks",  "sector": "Technology", "region": "Europe"},
        {"company": "Apex Financials",   "sector": "Finance",    "region": "North America"},
        {"company": "Global Trade Co",   "sector": "Finance",    "region": "Asia"},
        {"company": "MedTech Innovations","sector": "Healthcare","region": "North America"},
        {"company": "BioGenesis",         "sector": "Healthcare","region": "Europe"},
        {"company": "EcoEnergy Group",    "sector": "Energy",    "region": "North America"},
        {"company": "Aura Cosmetics",     "sector": "Retail",    "region": "Europe"},
        {"company": "Urban Retailers",    "sector": "Retail",    "region": "Asia"},
        {"company": "Velocity Motors",    "sector": "Manufacturing","region": "North America"},
    ]
    dates = pd.date_range("2020-01-01", "2023-12-31", freq='ME')
    records = []
    for comp in companies:
        base = np.random.uniform(10e6, 50e6)
        trend = np.random.uniform(-0.02, 0.05)
        cur = base
        for date in dates:
            cur *= (1 + trend + np.random.normal(0, 0.05))
            gm = np.random.uniform(0.4, 0.8)
            om = gm * np.random.uniform(0.3, 0.7)
            nm = om * np.random.uniform(0.5, 0.8)
            arpu = np.random.uniform(50, 500)
            customers = int(cur / arpu)
            ms = cur * np.random.uniform(0.05, 0.2)
            records.append({
                **comp,
                "date": date, "channel": np.random.choice(["Direct","Partners","Online","Enterprise"]),
                "revenue": cur, "gross_profit": cur*gm, "operating_income": cur*om, "net_income": cur*nm,
                "assets": cur*np.random.uniform(5,12), "liabilities": cur*np.random.uniform(2,6),
                "equity": cur*np.random.uniform(2,5), "debt": cur*np.random.uniform(1,4),
                "customers": customers, "orders": int(customers*np.random.uniform(1,5)),
                "marketing_spend": ms, "cac": ms/max(customers*0.1,1),
                "arpu": arpu, "conversion_rate": np.random.uniform(0.01,0.15),
                "market_cap": cur*12*np.random.uniform(2,6),
            })
    return pd.DataFrame(records)

# ─────────────────────────────────────────────────────────────────────────────
# A/B TEST DATA (standalone synthetic)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_experiment_data():
    np.random.seed(123)
    n = 2000
    data = []
    for _ in range(n//2):
        data.append({"user_id": np.random.randint(10000,99999), "group":"Control",
                     "value": np.random.binomial(1,0.05),
                     "date": pd.Timestamp('2023-11-01') + pd.Timedelta(days=int(np.random.uniform(0,30)))})
    for _ in range(n//2):
        data.append({"user_id": np.random.randint(10000,99999), "group":"Treatment",
                     "value": np.random.binomial(1,0.058),
                     "date": pd.Timestamp('2023-11-01') + pd.Timedelta(days=int(np.random.uniform(0,30)))})
    return pd.DataFrame(data)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────────────────────

def apply_chart_theme():
    return dict(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="'Segoe UI', sans-serif", color="#1e293b", size=13),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        colorway=["#118DFF","#12239E","#E66C37","#6B007B","#E044A7","#744EC2","#D9B300","#D64550","#197278","#1AAB40"],
        title_font=dict(size=18, color="#0f172a"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
    )

def format_value(val):
    if isinstance(val, float) or isinstance(val, int):
        if abs(val) >= 1e9: return f"{val/1e9:.2f}B"
        if abs(val) >= 1e6: return f"{val/1e6:.2f}M"
        if abs(val) >= 1e3: return f"{val/1e3:.1f}K"
        return f"{val:.2f}"
    return str(val)

def get_historical_growth(df, col, date_col):
    try:
        ts = df.groupby(date_col)[col].sum().sort_index()
        return float(ts.pct_change().mean())
    except:
        return 0.015

# Legacy aliases so old page imports don't break
def calculate_kpis(df): return df
def load_and_generate_data(): return load_demo_data()
def get_risk_rating(row): return "N/A"
def format_currency(val): return format_value(val)
def get_metric_label(col): return col.replace('_',' ').title()
