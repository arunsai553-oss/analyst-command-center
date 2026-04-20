import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, calculate_kpis, apply_chart_theme

st.set_page_config(page_title="Deep Dive Lab", page_icon="🔬", layout="wide")

st.markdown("# 🔬 Deep Dive Lab")
st.markdown("Exploratory Data Analysis (EDA) interface for investigating correlations and multifaceted groups.")

@st.cache_data
def get_data():
    return calculate_kpis(load_and_generate_data())

df = get_data()

st.sidebar.markdown("### Lab Controls")
selected_company = st.sidebar.selectbox("Isolate Company (Optional)", ["All"] + list(df['company'].unique()))
if selected_company != "All":
    df = df[df['company'] == selected_company]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧩 Correlation Matrix")
    st.caption("Identify relationships between operational metrics and financial outcomes.")
    corr_cols = st.multiselect("Select Variables", 
                               options=['revenue', 'marketing_spend', 'cac', 'arpu', 'conversion_rate', 'gross_margin_%', 'roe_%', 'ltv_to_cac', 'debt_to_equity'],
                               default=['revenue', 'marketing_spend', 'cac', 'gross_margin_%', 'ltv_to_cac'])
    
    if len(corr_cols) > 1:
        corr_matrix = df[corr_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
        fig.update_layout(**apply_chart_theme(), margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Select at least 2 variables for correlation.")

with col2:
    st.markdown("### 🎲 Custom Dissection (Pivot)")
    st.caption("Aggregate and segment data dynamically.")
    
    pivot_index = st.selectbox("Group By", ["sector", "region", "channel", "company"])
    pivot_val = st.selectbox("Value to Aggregate", ["revenue", "customers", "marketing_spend", "operating_income"])
    pivot_agg = st.selectbox("Aggregation Function", ["sum", "mean", "median"])
    
    # Advanced logic for time mapping (yearly) if needed
    df['Year'] = df['date'].dt.year
    pivot_cols = st.selectbox("Columns (Optional)", ["None", "Year"])
    
    if pivot_cols != "None":
        pivot_df = pd.pivot_table(df, values=pivot_val, index=pivot_index, columns=pivot_cols, aggfunc=pivot_agg).fillna(0)
        st.dataframe(pivot_df.style.background_gradient(cmap='Blues'), use_container_width=True)
        
        # Heatmap of pivot
        fig2 = px.imshow(pivot_df, text_auto=True, color_continuous_scale='Viridis', aspect="auto")
        fig2.update_layout(title=f"{pivot_val} by {pivot_index} and {pivot_cols}", **apply_chart_theme())
        st.plotly_chart(fig2, use_container_width=True)
    else:
        agg_df = df.groupby(pivot_index)[pivot_val].agg(pivot_agg).reset_index().sort_values(by=pivot_val, ascending=False)
        fig2 = px.bar(agg_df, x=pivot_index, y=pivot_val, color=pivot_index)
        fig2.update_layout(**apply_chart_theme())
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Scatter Analysis")
sc_x = st.selectbox("X-Axis", ['cac', 'marketing_spend', 'revenue', 'gross_margin_%'])
sc_y = st.selectbox("Y-Axis", ['ltv_to_cac', 'conversion_rate', 'net_income', 'roe_%'], index=0)
sc_size = st.selectbox("Size (Optional)", ['None', 'revenue', 'customers', 'assets'])
sc_color = st.selectbox("Color Segment", ['sector', 'region', 'channel'])

size_arg = sc_size if sc_size != 'None' else None

fig_scatter = px.scatter(df, x=sc_x, y=sc_y, size=size_arg, color=sc_color, hover_name='company', 
                         title=f"{sc_y} vs {sc_x} segmented by {sc_color}",
                         marginal_x="box", marginal_y="box")
fig_scatter.update_layout(**apply_chart_theme())
st.plotly_chart(fig_scatter, use_container_width=True)
