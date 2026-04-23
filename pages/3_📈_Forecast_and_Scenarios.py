import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, apply_chart_theme

st.set_page_config(page_title="Forecasting & Scenarios", page_icon="📈", layout="wide")

st.markdown("# 📈 Forecast & Scenarios")
st.markdown("Project future performance and stress-test assumptions with dynamic scenarios.")

@st.cache_data
def get_historical_data():
    df = load_and_generate_data()
    # Let's do a top-level aggregation for forecasting
    return df.groupby('date')[['revenue', 'operating_income']].sum().reset_index()

hist_df = get_historical_data()

st.sidebar.markdown("### What-If Parameters")
st.sidebar.caption("Adjust to see impact on baseline forecast")
forecast_months = st.sidebar.slider("Forecast Horizon (Months)", 3, 24, 12)

# Scenario inputs
scen_growth = st.sidebar.number_input("Scenario M-o-M Growth Rate (%)", value=1.5, step=0.1) / 100.0
scen_margin_adj = st.sidebar.slider("Scenario Operating Margin Adj (%)", -5.0, 5.0, 0.0) / 100.0

# --- Simple Exponential Smoothing for Baseline Forecasting ---
def forecast_exponential_smoothing(series, alpha=0.3, periods=12):
    # Very basic EWMA for demonstrative forecasting
    smoothed = [series.iloc[0]]
    for i in range(1, len(series)):
        smoothed.append(alpha * series.iloc[i] + (1 - alpha) * smoothed[i-1])
        
    last_val = smoothed[-1]
    # Trend estimation based on last 6 periods
    if len(series) > 6:
        trend = (series.iloc[-1] - series.iloc[-6]) / 6
    else:
        trend = 0
        
    forecasts = []
    for p in range(1, periods + 1):
        forecasts.append(last_val + trend * p)
    return forecasts

last_date = hist_df['date'].max()
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_months, freq='ME')

# Base Projections
base_rev_forecast = forecast_exponential_smoothing(hist_df['revenue'], periods=forecast_months)

# Scenario Projections (Compound Growth from last actual)
last_actual_rev = hist_df['revenue'].iloc[-1]
scen_rev_forecast = [last_actual_rev * ((1 + scen_growth) ** i) for i in range(1, forecast_months + 1)]

last_actual_margin = (hist_df['operating_income'].iloc[-1] / hist_df['revenue'].iloc[-1]) if hist_df['revenue'].iloc[-1] else 0
scen_margin = last_actual_margin + scen_margin_adj
scen_op_income = [r * scen_margin for r in scen_rev_forecast]

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df['revenue'], mode='lines', name='Historical Revenue', line=dict(color='#3b82f6', width=3)))
    
    # Baseline Forecast
    fig.add_trace(go.Scatter(x=future_dates, y=base_rev_forecast, mode='lines', name='Baseline Forecast (EWMA)', line=dict(color='#94a3b8', width=2, dash='dot')))
    
    # Scenario Forecast
    fig.add_trace(go.Scatter(x=future_dates, y=scen_rev_forecast, mode='lines', name='Scenario Validation', line=dict(color='#10b981', width=3)))
    
    fig.update_layout(title="Revenue: Historical vs Forecasts", yaxis_tickprefix="$", **apply_chart_theme())
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Projection Summary")
    st.write(f"**Period:** Next {forecast_months} Months")
    st.metric("Baseline Final Month Rev", f"${base_rev_forecast[-1]/1e6:.1f}M")
    
    delta = (scen_rev_forecast[-1] - base_rev_forecast[-1]) / base_rev_forecast[-1]
    st.metric("Scenario Final Month Rev", f"${scen_rev_forecast[-1]/1e6:.1f}M", f"{delta*100:+.1f}% vs Base")
    
    st.metric("Scenario Operating Income (End)", f"${scen_op_income[-1]/1e6:.1f}M")
    
    st.markdown("---")
    st.markdown("### 💡 Analyst Insight")
    if scen_growth > 0.015:
        st.success(f"The aggressive **{scen_growth*100:.1f}%** monthly growth scenario suggests a terminal revenue scale of **${scen_rev_forecast[-1]/1e6:.1f}M**. This requires significant capital efficiency.")
    elif scen_growth < 0.01:
        st.warning("Low growth assumptions indicate a flattening curve. Portfolio focus should shift towards margin optimization rather than scale.")
    else:
        st.info("The current scenario represents a steady-state expansion aligned with historical SaaS benchmarks.")

st.markdown("---")
st.markdown("### Raw Forecast Output")
out_df = pd.DataFrame({
    'Date': future_dates,
    'Baseline Revenue': base_rev_forecast,
    'Scenario Revenue': scen_rev_forecast,
    'Scenario Op Income': scen_op_income
}).set_index('Date')

st.dataframe(out_df.style.format("${:,.0f}"), use_container_width=True)
