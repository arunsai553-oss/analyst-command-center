import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, apply_chart_theme, get_data, get_filtered_data, get_historical_growth

st.set_page_config(page_title="Forecasting & Scenarios", page_icon="📈", layout="wide")

st.markdown("# 📈 Forecast & Scenarios")
st.markdown("Project future performance and stress-test assumptions with dynamic scenarios.")

# Use Filtered Data (Global Sync)
df = get_filtered_data()
hist_df = df.groupby('date')[['revenue', 'operating_income', 'gross_profit', 'net_income', 'customers']].sum().reset_index()

st.sidebar.markdown("### What-If Parameters")
st.sidebar.caption("Adjust to see impact on baseline forecast")
target_metric = st.sidebar.selectbox(
    "Target Metric to Forecast", 
    ['revenue', 'operating_income', 'gross_profit', 'net_income', 'customers'],
    format_func=lambda x: x.replace('_', ' ').title()
)
forecast_months = st.sidebar.slider("Forecast Horizon (Months)", 3, 24, 12)

# --- AUTO-CLEAN LOGIC ---
# Calculate historical growth to seed the scenario automatically
hist_growth_rate = get_historical_growth(df, target_metric)

# Scenario inputs - seeded with historical baseline for "Clean" experience
scen_growth = st.sidebar.number_input(
    f"Scenario M-o-M Growth Rate (%)", 
    value=float(hist_growth_rate * 100), # Clean: automatically updates to historical reality
    step=0.1,
    help="Default is set to the historical average growth of your 'Hooked' data."
) / 100.0
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
hist_vol = hist_df[target_metric].pct_change().std()

# Run Simulation
last_historical_val = hist_df[target_metric].iloc[-1]
mc_results = run_monte_carlo(last_historical_val, scen_growth, hist_vol, periods=forecast_months)

mc_median = np.median(mc_results, axis=0)
mc_upper = np.percentile(mc_results, 95, axis=0)
mc_lower = np.percentile(mc_results, 5, axis=0)
mc_mid_upper = np.percentile(mc_results, 75, axis=0)
mc_mid_lower = np.percentile(mc_results, 25, axis=0)

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df[target_metric], mode='lines', name=f'Historical {target_metric.title()}', line=dict(color='#118DFF', width=3)))
    
    # Monte Carlo Confidence Bands
    fig.add_trace(go.Scatter(x=future_dates, y=mc_upper, mode='lines', line=dict(width=0), showlegend=False, name='95% CI Upper'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(26, 171, 64, 0.1)', name='95% Confidence Interval'))
    
    fig.add_trace(go.Scatter(x=future_dates, y=mc_mid_upper, mode='lines', line=dict(width=0), showlegend=False, name='50% CI Upper'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_mid_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(26, 171, 64, 0.2)', name='Interquartile Range (50%)'))

    # Probabilistic Median (Scen Validation)
    fig.add_trace(go.Scatter(x=future_dates, y=mc_median, mode='lines', name='Monte Carlo Median', line=dict(color='#1AAB40', width=3)))
    
    prefix = "$" if target_metric != 'customers' else ""
    fig.update_layout(title=f"Probabilistic {target_metric.replace('_', ' ').title()} Forecast (1,000 Trials)", yaxis_tickprefix=prefix, **apply_chart_theme())
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
        st.success(f"High-growth scenario: Probabilistic median indicates **{prefix}{mc_median[-1]/1e6:.1f}M** terminal scale. 95% confidence ceiling at **{prefix}{mc_upper[-1]/1e6:.1f}M**.")
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
