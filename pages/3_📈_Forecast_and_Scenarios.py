import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_filtered_data, get_numeric_cols, get_date_col, apply_chart_theme, get_historical_growth, format_value

st.set_page_config(page_title="Forecast & Scenarios", page_icon="📈", layout="wide")
st.markdown("# 📈 Forecast & Scenarios")
st.markdown("Probabilistic forecasting via Monte Carlo simulation — on any numeric column.")

df = get_filtered_data()
num_cols  = get_numeric_cols(df)
date_col  = get_date_col(df)

if not date_col or not num_cols:
    st.warning("⚠️ Forecasting requires at least one date column and one numeric column.")
    st.dataframe(df.head(10), use_container_width=True)
    st.stop()

df = df.copy()
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df = df.dropna(subset=[date_col])

hist_df = df.groupby(date_col)[num_cols].sum().reset_index().sort_values(date_col)

# ── Sidebar controls ─────────────────────────────────────────────────────────
st.sidebar.markdown("### Forecast Controls")
target = st.sidebar.selectbox("Column to Forecast", num_cols)
forecast_months = st.sidebar.slider("Horizon (periods)", 3, 36, 12)

hist_growth = get_historical_growth(df, target, date_col)
scen_growth = st.sidebar.number_input(
    "Scenario Growth Rate (%/period)",
    value=round(float(hist_growth * 100), 2), step=0.1
) / 100.0

is_currency = df[target].mean() > 1000

# ── Monte Carlo ───────────────────────────────────────────────────────────────
def monte_carlo(last_val, growth, vol, periods, trials=1000):
    results = []
    for _ in range(trials):
        path = [last_val]
        for _ in range(periods):
            path.append(path[-1] * (1 + np.random.normal(growth, vol)))
        results.append(path[1:])
    return np.array(results)

hist_vol = hist_df[target].pct_change().std()
last_val  = float(hist_df[target].iloc[-1])
last_date = hist_df[date_col].max()

# Infer frequency
try:
    inferred_freq = pd.infer_freq(hist_df[date_col])
    future_dates = pd.date_range(start=last_date, periods=forecast_months+1, freq=inferred_freq or 'ME')[1:]
except:
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=30), periods=forecast_months, freq='ME')

mc = monte_carlo(last_val, scen_growth, hist_vol or 0.05, forecast_months)
mc_med   = np.median(mc, axis=0)
mc_p95   = np.percentile(mc, 95, axis=0)
mc_p5    = np.percentile(mc, 5, axis=0)
mc_p75   = np.percentile(mc, 75, axis=0)
mc_p25   = np.percentile(mc, 25, axis=0)

def fmt(v):
    if is_currency: return format_value(v)
    return f"{v:,.1f}"

col1, col2 = st.columns([3,1])

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_df[date_col], y=hist_df[target],
                             mode='lines', name=f'Historical {target}',
                             line=dict(color='#118DFF', width=3)))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_p95, line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_p5,  line=dict(width=0),
                             fill='tonexty', fillcolor='rgba(26,171,64,0.1)', name='90% CI'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_p75, line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_p25, line=dict(width=0),
                             fill='tonexty', fillcolor='rgba(26,171,64,0.2)', name='IQR (50%)'))
    fig.add_trace(go.Scatter(x=future_dates, y=mc_med,  mode='lines',
                             name='Monte Carlo Median', line=dict(color='#1AAB40', width=3)))
    prefix = "$" if is_currency else ""
    fig.update_layout(title=f"Probabilistic Forecast: {target.replace('_',' ').title()} (1,000 trials)",
                      yaxis_tickprefix=prefix, **apply_chart_theme())
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Projection Summary")
    metric_label = target.replace('_',' ').title()
    st.metric(f"Terminal {metric_label} (Median)", fmt(mc_med[-1]))
    st.metric("95th Percentile (Optimistic)",      fmt(mc_p95[-1]))
    st.metric("5th Percentile (Pessimistic)",       fmt(mc_p5[-1]))
    st.markdown("---")
    if scen_growth > 0.015:
        st.success(f"📈 **Growth scenario** — median terminal: **{fmt(mc_med[-1])}**")
    elif scen_growth < -0.01:
        st.error(f"📉 **Decline scenario** — median terminal: **{fmt(mc_med[-1])}**")
    else:
        st.info("Flat/slow-growth scenario.")

st.markdown("---")
st.markdown("### Raw Forecast Output")
fmt_str = "${:,.0f}" if is_currency else "{:,.2f}"
out = pd.DataFrame({'Date': future_dates, 'Median': mc_med,
                    'Upper 95%': mc_p95, 'Lower 5%': mc_p5}).set_index('Date')
st.dataframe(out.style.format(fmt_str), use_container_width=True)
