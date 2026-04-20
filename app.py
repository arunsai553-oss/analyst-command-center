import streamlit as st
import pandas as pd
from utils import load_and_generate_data, calculate_kpis

# Must be the first Streamlit command
st.set_page_config(
    page_title="Analyst Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    /* Gradient text for main headers */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-head {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
    }
    /* Hide default Streamlit elements for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="gradient-text">Analyst Command Center</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-head">A comprehensive portfolio demonstrating full-stack analytics, forecasting & EDA.</p>', unsafe_allow_html=True)

st.write("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🎯 Platform Capabilities
    Welcome to my Analytics Portfolio. This application is an interactive showcase of my capabilities as a Data/Financial Analyst. 
    It is divided into four main functional areas designed to reflect real-world business challenges:
    
    1. **📊 Market & Company Scanner**: Top-level macro filtering, time-series analysis, and KPI tracking across sectors.
    2. **🔬 Deep Dive Lab**: Dynamic correlation matrices, aggregations, and custom pivoting of complex financial structures.
    3. **📈 Forecast & Scenarios**: Predictive modelling using exponential smoothing with interactive "what-if" margin/growth adjustments.
    4. **🧪 Experiments & KPIs**: Rigorous A/B test evaluation, tracking statistical significance for product/marketing experiments.
    5. **📝 Executive Summary**: Automated synthesis and strategic narrative generation for leadership readouts.
    
    *Use the sidebar to navigate between these modules.*
    """)

with col2:
    st.info("""
    **💡 Portfolio Details**
    - **Tech Stack**: Python, Streamlit, Pandas, NumPy, Plotly, SciPy.
    - **Data Context**: Synthetic B2B/SaaS & Telecom datasets mimicking real corporate financial behavior (Revenue, Margins, Debt, CAC, LTV).
    - **Deployment**: Streamlit Community Cloud.
    """)

st.write("---")
st.markdown("### 🌐 Global High-Level Overview")
st.caption("Data generated synthetically for demonstration purposes.")

# Pre-load data to ensure generation and provide a sneak peek
with st.spinner("Initializing Data Engine..."):
    raw_df = load_and_generate_data()
    df = calculate_kpis(raw_df)

# Show high-level metrics for the most recent month
latest_date = df['date'].max()
latest_data = df[df['date'] == latest_date]

total_revenue = latest_data['revenue'].sum()
avg_margin = latest_data['gross_margin_%'].mean()
avg_roe = latest_data['roe_%'].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Global Monthly Revenue", f"${total_revenue/1e6:.1f}M", "+5.2% MoM")
m2.metric("Avg Gross Margin", f"{avg_margin*100:.1f}%", "-0.3% MoM")
m3.metric("Avg Return on Equity", f"{avg_roe*100:.1f}%", "+1.1% MoM")
m4.metric("Companies Tracked", len(latest_data['company'].unique()), "Active")

st.markdown("### Raw Dataset Snapshot")
st.dataframe(df.head(), use_container_width=True)
