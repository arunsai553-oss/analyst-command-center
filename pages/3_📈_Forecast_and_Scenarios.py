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

# --- 1000 IQ Monte Carlo Simulation (Probabilistic Forecasting) ---
def run_monte_carlo(last_val, growth_rate, volatility, periods=12, trials=1000):
    all_trials = []
    for _ in range(trials):
        trial_path = [last_val]
        for _ in range(periods):
            # Normal distribution of monthly growth
            daily_growth = np.random.normal(growth_rate, volatility)
            trial_path.append(trial_path[-1] * (1 + daily_growth))
        all_trials.append(trial_path[1:])
    return np.array(all_trials)

# Baseline Volatility from historical data
hist_vol = hist_df['revenue'].pct_change().std()

# Run Simulation
mc_results = run_monte_carlo(hist_df['revenue'].iloc[-1], scen_growth, hist_vol, periods=forecast_months)
mc_median = np.median(mc_results, axis=0)
mc_upper = np.percentile(mc_results, 95, axis=0)
mc_lower = np.percentile(mc_results, 5, axis=0)
mc_mid_upper = np.percentile(mc_results, 75, axis=0)
mc_mid_lower = np.percentile(mc_results, 25, axis=0)

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df['revenue'], mode='lines', name='Historical Revenue', line=dict(color='#3b82f6', width=3)))
    
    # Monte Carlo Confidence Bands
    fig.add_trace(go.Scatter(x=future_dates, y=mc_upper, mode='lines', line=dict(width=0), showlegend=False, name='95% CI Upper'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)', name='95% Confidence Interval'))
    
    fig.add_trace(go.Scatter(x=future_dates, y=mc_mid_upper, mode='lines', line=dict(width=0), showlegend=False, name='50% CI Upper'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_mid_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(16, 185, 129, 0.2)', name='Interquartile Range (50%)'))

    # Probabilistic Median (Scen Validation)
    fig.add_trace(go.Scatter(x=future_dates, y=mc_median, mode='lines', name='Monte Carlo Median', line=dict(color='#10b981', width=3)))
    
    fig.update_layout(title="Probabilistic Revenue Forecast (1,000 Trials)", yaxis_tickprefix="$", **apply_chart_theme())
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Projection Summary")
    st.write(f"**Period:** Next {forecast_months} Months")
    st.metric("Terminal Revenue (Median)", f"${mc_median[-1]/1e6:.1f}M")
    
    st.metric("95th Percentile (Optimistic)", f"${mc_upper[-1]/1e6:.1f}M")
    st.metric("5th Percentile (Pessimistic)", f"${mc_lower[-1]/1e6:.1f}M")
    
    st.markdown("---")
    st.markdown("### 💡 Analyst Insight")
    if scen_growth > 0.015:
        st.success(f"High-growth scenario: Probabilistic median indicates **${mc_median[-1]/1e6:.1f}M** revenue. 95% confidence ceiling at **${mc_upper[-1]/1e6:.1f}M**.")
    else:
        st.info("The forecast bands represent the probability distribution based on 1,000 historical volatility simulations.")

st.markdown("---")
st.markdown("### Raw Probabilistic Output")
out_df = pd.DataFrame({
    'Date': future_dates,
    'Median Forecast': mc_median,
    'Upper Bound (95%)': mc_upper,
    'Lower Bound (5%)': mc_lower
}).set_index('Date')

st.dataframe(out_df.style.format("${:,.0f}"), use_container_width=True)
