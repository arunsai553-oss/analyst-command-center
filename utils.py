import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

@st.cache_data
def load_and_generate_data():
    """
    Generates synthetic corporate financial and KPI data if a local dataset is not found.
    Designed to be a plug-and-play substitute for real CSVs.
    """
    # Try loading from local CSV (in a real scenario)
    try:
        df = pd.read_csv("data/raw/financials.csv")
        return pd.to_datetime(df['date']), df
    except:
        pass # Generate synthetic data instead
        
    np.random.seed(42)
    
    companies = [
        {"company": "Quantum Dynamics", "ticker": "QDYN", "sector": "Technology", "region": "North America"},
        {"company": "Stellar Networks", "ticker": "STNK", "sector": "Technology", "region": "Europe"},
        {"company": "Apex Financials", "ticker": "APEX", "sector": "Finance", "region": "North America"},
        {"company": "Global Trade Co", "ticker": "GLTR", "sector": "Finance", "region": "Asia"},
        {"company": "MedTech Innovations", "ticker": "MTIN", "sector": "Healthcare", "region": "North America"},
        {"company": "BioGenesis", "ticker": "BGEN", "sector": "Healthcare", "region": "Europe"},
        {"company": "EcoEnergy Group", "ticker": "ECOE", "sector": "Energy", "region": "North America"},
        {"company": "Aura Cosmetics", "ticker": "AURA", "sector": "Retail", "region": "Europe"},
        {"company": "Urban Retailers", "ticker": "URBN", "sector": "Retail", "region": "Asia"},
        {"company": "Velocity Motors", "ticker": "VLMT", "sector": "Manufacturing", "region": "North America"},
    ]
    
    dates = pd.date_range(start="2020-01-01", end="2023-12-31", freq='ME') # Monthly data
    records = []
    
    for comp in companies:
        base_revenue = np.random.uniform(10e6, 50e6)
        growth_trend = np.random.uniform(-0.02, 0.05) # monthly growth rate trend with some noise
        
        current_revenue = base_revenue
        for i, date in enumerate(dates):
            # Financials
            noise = np.random.normal(0, 0.05)
            monthly_growth = growth_trend + noise
            current_revenue = current_revenue * (1 + monthly_growth)
            
            gross_margin = np.random.uniform(0.4, 0.8)
            operating_margin = gross_margin * np.random.uniform(0.3, 0.7)
            net_margin = operating_margin * np.random.uniform(0.5, 0.8)
            
            gross_profit = current_revenue * gross_margin
            operating_income = current_revenue * operating_margin
            net_income = current_revenue * net_margin
            
            # Balance sheet (simplified relative to revenue scale)
            assets = current_revenue * np.random.uniform(5, 12)
            liabilities = assets * np.random.uniform(0.3, 0.8)
            equity = assets - liabilities
            debt = liabilities * np.random.uniform(0.4, 0.9)
            
            # KPIs
            arpu = np.random.uniform(50, 500)
            customers = int(current_revenue / arpu)
            orders = int(customers * np.random.uniform(1, 5))
            marketing_spend = current_revenue * np.random.uniform(0.05, 0.2)
            cac = marketing_spend / (customers * 0.1) if customers > 0 else 0 # assumed 10% new
            channel = np.random.choice(["Direct", "Partners", "Online", "Enterprise"])
            conversion_rate = np.random.uniform(0.01, 0.15)
            
            # Market Data (Safe & Deterministic Valuation)
            shares_outstanding = np.random.uniform(1e6, 10e6)
            # Use Revenue multiple as a floor for share price to avoid negative valuation
            rev_multiple = np.random.uniform(2, 6)
            earnings_multiple = np.random.uniform(15, 25)
            
            value_from_rev = (current_revenue * 12 * rev_multiple) / shares_outstanding
            value_from_earnings = max(0, (net_income * 12 * earnings_multiple) / shares_outstanding)
            
            share_price = max(value_from_rev * 0.7, value_from_earnings) + np.random.uniform(1, 5)
            market_cap = share_price * shares_outstanding
            
            records.append({
                **comp,
                "date": date,
                "revenue": current_revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "assets": assets,
                "liabilities": liabilities,
                "equity": equity,
                "debt": debt,
                "customers": customers,
                "orders": orders,
                "marketing_spend": marketing_spend,
                "cac": cac,
                "arpu": arpu,
                "channel": channel,
                "conversion_rate": conversion_rate,
                "share_price": share_price,
                "market_cap": market_cap,
                "shares_outstanding": shares_outstanding
            })
            
    df = pd.DataFrame(records)
    
    # Save a mock csv for demonstration purposes so the user sees data is generated
    import os
    os.makedirs("data/processed", exist_ok=True)
    try:
        df.to_csv("data/processed/synthetic_financials.csv", index=False)
    except:
        pass
        
    return df

@st.cache_data
def load_experiment_data():
    """Generates synthetic A/B test data."""
    np.random.seed(123)
    n = 2000
    
    data = []
    # Control Group
    for _ in range(n // 2):
        data.append({
            "user_id": np.random.randint(10000, 99999),
            "group": "Control",
            "metric": "conversion",
            "value": np.random.binomial(1, 0.05), # 5% baseline conversion
            "date": pd.Timestamp('2023-11-01') + pd.Timedelta(days=int(np.random.uniform(0, 30)))
        })
    
    # Treatment Group (Simulate a lift)
    for _ in range(n // 2):
        data.append({
            "user_id": np.random.randint(10000, 99999),
            "group": "Treatment",
            "metric": "conversion",
            "value": np.random.binomial(1, 0.058), # 5.8% conversion (lift)
            "date": pd.Timestamp('2023-11-01') + pd.Timedelta(days=int(np.random.uniform(0, 30)))
        })
        
    df = pd.DataFrame(data)
    return df

def format_currency(val):
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    elif val >= 1e6:
        return f"${val/1e6:.2f}M"
    elif val >= 1e3:
        return f"${val/1e3:.2f}K"
    else:
        return f"${val:.2f}"

def format_percentage(val):
    return f"{val*100:.1f}%"

def calculate_kpis(df):
    """Calculates additional derived metrics with safety checks (1000 IQ Level)."""
    df = df.copy()
    
    # Financial Margins
    df['gross_margin_%'] = (df['gross_profit'] / df['revenue']).fillna(0)
    df['operating_margin_%'] = (df['operating_income'] / df['revenue']).fillna(0)
    df['net_margin_%'] = (df['net_income'] / df['revenue']).fillna(0)
    
    # Returns & Efficiency
    df['roe_%'] = (df['net_income'] / df['equity']).fillna(0)
    df['roa_%'] = (df['net_income'] / df['assets']).fillna(0)
    df['roic_%'] = ((df['operating_income'] * 0.75) / (df['debt'] + df['equity'])).fillna(0)
    df['debt_to_equity'] = (df['debt'] / df['equity']).fillna(0)
    
    # Valuation Multiples
    df['price_to_sales'] = (df['market_cap'] / (df['revenue'] * 12)).fillna(0)
    df['pe_ratio'] = (df['market_cap'] / (df['net_income'] * 12)).replace([np.inf, -np.inf], 0).fillna(0)
    
    # --- Altman Z-Score (Modified for Private Firms Analysis) ---
    # Working Capital Approx = 0.2 * Revenue
    # Retained Earnings Approx = 0.4 * Total Assets
    X1 = (df['revenue'] * 0.2) / df['assets']
    X2 = (df['assets'] * 0.4) / df['assets'] 
    X3 = df['operating_income'] / df['assets']
    X4 = df['equity'] / df['debt'].replace(0, 1e-6)
    X5 = (df['revenue'] * 12) / df['assets']
    
    df['altman_z_score'] = (0.717 * X1) + (0.847 * X2) + (3.107 * X3) + (0.420 * X4) + (0.998 * X5)
    
    # Customer/Marketing Metrics
    df['ltv_approx'] = (df['arpu'] * df['gross_margin_%']) / 0.05
    df['ltv_to_cac'] = (df['ltv_approx'] / df['cac']).replace([np.inf, -np.inf], 0).fillna(0)
    
    return df

def get_risk_rating(row):
    """Categorizes company risk using the Altman Z-Score threshold."""
    z = row['altman_z_score']
    if z < 1.23: return 'Distress Zone'
    if z < 2.90: return 'Grey Zone'
    return 'Safe Zone'

def get_metric_label(col):
    """Maps internal column names to professional labels."""
    mapping = {
        'revenue': 'Revenue',
        'gross_profit': 'Gross Profit',
        'operating_income': 'Operating Income',
        'net_income': 'Net Income',
        'gross_margin_%': 'Gross Margin (%)',
        'operating_margin_%': 'Operating Margin (%)',
        'net_margin_%': 'Net Margin (%)',
        'roe_%': 'ROE (%)',
        'roa_%': 'ROA (%)',
        'cac': 'CAC',
        'ltv_to_cac': 'LTV to CAC',
        'arpu': 'ARPU',
        'customers': 'Total Customers',
        'conversion_rate': 'Conversion Rate'
    }
    return mapping.get(col, col.replace('_', ' ').title())

def apply_chart_theme():
    """Returns a unified chart layout theme dictionary."""
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color="#e2e8f0"),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        colorway=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"],
        title_font=dict(size=20, weight="bold")
    )
