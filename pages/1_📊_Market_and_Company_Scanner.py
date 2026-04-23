import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Ensure utils can be imported when running from pages/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, calculate_kpis, apply_chart_theme, format_currency, get_metric_label, get_data

st.set_page_config(page_title="Market Scanner", page_icon="📊", layout="wide")

st.markdown("# 📊 Market & Company Scanner")
st.markdown("Filter and drill down into absolute performance and sector-wide macroeconomic trends.")

df = get_data()


# --- Filters ---
st.sidebar.header("Filter Portfolio")
sectors = st.sidebar.multiselect("Sectors", options=df['sector'].unique(), default=df['sector'].unique())

available_companies = df[df['sector'].isin(sectors)]['company'].unique()
companies = st.sidebar.multiselect("Specific Companies", options=available_companies, default=available_companies)

regions = st.sidebar.multiselect("Regions", options=df['region'].unique(), default=df['region'].unique())

# Date Filter
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Time Horizon", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
mask = (
    (df['sector'].isin(sectors)) & 
    (df['region'].isin(regions)) & 
    (df['company'].isin(companies))
)
if len(date_range) == 2:
    mask = mask & (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])

filtered_df = df[mask]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- Tabs ---
tab1, tab2 = st.tabs(["📈 Time Series Analysis", "🏆 Rankings & Cross-Sectional"])

with tab1:
    col_metric, col_agg = st.columns([2, 1])
    with col_metric:
        metric = st.selectbox("Select Metric", ["revenue", "gross_profit", "operating_income", "net_income", "customers"], index=0)
    with col_agg:
        agg_level = st.selectbox("Aggregation Level", ["Company", "Sector", "Region"], index=0)
    
    # Aggregation logic
    if agg_level == "Company":
        chart_data = filtered_df.groupby(['date', 'company'])[metric].sum().reset_index()
        color_col = 'company'
    elif agg_level == "Sector":
        chart_data = filtered_df.groupby(['date', 'sector'])[metric].sum().reset_index()
        color_col = 'sector'
    else:
        chart_data = filtered_df.groupby(['date', 'region'])[metric].sum().reset_index()
        color_col = 'region'
        
    # Plotly Line Chart
    fig = px.area(chart_data, x="date", y=metric, color=color_col, 
                  title=f"{get_metric_label(metric)} Trends by {agg_level}",
                  labels={metric: get_metric_label(metric), 'date': 'Period', color_col: agg_level})
    fig.update_layout(**apply_chart_theme())
    # If metric is currency
    if metric in ['revenue', 'gross_profit', 'operating_income', 'net_income']:
        fig.update_layout(yaxis_tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)
    
    # Margin Analysis
    st.markdown("### Margin Compression / Expansion")
    margin_data = filtered_df.groupby(['date'])[['gross_margin_%', 'operating_margin_%', 'net_margin_%']].mean().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=margin_data['date'], y=margin_data['gross_margin_%'], mode='lines', name='Gross Margin'))
    fig2.add_trace(go.Scatter(x=margin_data['date'], y=margin_data['operating_margin_%'], mode='lines', name='Operating Margin'))
    fig2.add_trace(go.Scatter(x=margin_data['date'], y=margin_data['net_margin_%'], mode='lines', name='Net Margin'))
    fig2.update_layout(title="Average Margins Over Time (Sector/Region Filtered)", yaxis_tickformat='.1%', **apply_chart_theme())
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Top Performers (Most Recent Period)")
    latest_date = filtered_df['date'].max()
    latest_df = filtered_df[filtered_df['date'] == latest_date]
    
    rank_metric = st.selectbox("Rank By", ["revenue", "roe_%", "gross_margin_%", "ltv_to_cac"], index=0)
    top_n = st.slider("Top N", 5, 20, 10, step=5)
    
    ranked_df = latest_df.sort_values(by=rank_metric, ascending=False).head(top_n)
    
    fig3 = px.bar(ranked_df, x="company", y=rank_metric, color="sector", text_auto='.2s' if rank_metric == 'revenue' else '.1%',
                  title=f"Top {top_n} Companies by {rank_metric.replace('_', ' ').title()}")
    fig3.update_layout(**apply_chart_theme())
    st.plotly_chart(fig3, use_container_width=True)
    
    st.dataframe(ranked_df[['company', 'sector', 'region', 'revenue', 'roe_%', 'gross_margin_%', 'ltv_to_cac']].reset_index(drop=True), use_container_width=True)
