import streamlit as st
import pandas as pd
import io
from utils import load_and_generate_data, calculate_kpis, get_data, get_risk_rating, apply_chart_theme
import plotly.express as px

# Must be the first Streamlit command
st.set_page_config(
    page_title="Analyst Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a Power BI / Tableau dashboard feel
st.markdown("""
<style>
    /* Power BI light grey background for the app */
    .stApp {
        background-color: #f1f5f9;
    }
    /* Gradient text for main headers */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #0284c7, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-head {
        font-size: 1.1rem;
        color: #475569;
        margin-top: -10px;
        margin-bottom: 25px;
    }
    
    /* Power BI / Tableau style metric cards (White with subtle shadow) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-color: #3b82f6;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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

# ─────────────────────────────────────────
# SIDEBAR — Global Connect & Filters
# ─────────────────────────────────────────
st.sidebar.markdown("## 🔌 Connect Your Data")
st.sidebar.caption("Upload a CSV with your real financial data to replace the demo dataset.")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV", type=["csv"],
    help="Must have columns: date, company, sector, region, revenue, gross_profit, operating_income, net_income, assets, liabilities, equity, debt, customers, marketing_spend, cac, arpu"
)

# Required columns for user guidance
REQUIRED_COLS = [
    'date', 'company', 'sector', 'region', 'channel',
    'revenue', 'gross_profit', 'operating_income', 'net_income',
    'assets', 'liabilities', 'equity', 'debt',
    'customers', 'orders', 'marketing_spend', 'cac', 'arpu', 'conversion_rate'
]

if uploaded_file:
    try:
        # Check if this is a NEW file to trigger state cleanup
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get('last_file_id') != file_id:
            st.session_state['uploaded_df'] = None  # Clear old data
            st.session_state['last_file_id'] = file_id
            # Clear all filter caches so they repopulate from new data
            for key in ['global_sectors', 'global_regions', 'global_companies']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        user_df = pd.read_csv(uploaded_file)
        user_df['date'] = pd.to_datetime(user_df['date'])
        # Validate required columns
        missing = [c for c in REQUIRED_COLS if c not in user_df.columns]
        if missing:
            st.sidebar.error(f"Missing columns: {', '.join(missing)}")
        else:
            # Pad market data columns if not present
            if 'market_cap' not in user_df.columns:
                user_df['market_cap'] = user_df['revenue'] * 12 * 3
                user_df['share_price'] = user_df['market_cap'] / 5e6
                user_df['shares_outstanding'] = 5e6
            st.session_state['uploaded_df'] = user_df
            st.sidebar.success(f"✅ **Live Data Active** — {len(user_df):,} rows loaded")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
else:
    if st.session_state.get('uploaded_df') is not None:
        # User removed the file — clear everything
        st.session_state['uploaded_df'] = None
        for key in ['global_sectors', 'global_regions', 'global_companies', 'last_file_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎯 Global Portfolio Filters")
st.sidebar.caption("Filters apply across all pages instantly")

# ── CRITICAL FIX: Always load filter options from the ACTIVE data source ──
# This ensures that when a user uploads their own CSV, the sector/company
# filter dropdowns populate with THEIR data, not the synthetic demo data.
filter_source_df = get_data()  # Respects uploaded_df if present

all_sectors  = sorted(filter_source_df['sector'].unique().tolist())
all_regions  = sorted(filter_source_df['region'].unique().tolist()) if 'region' in filter_source_df.columns else []
all_companies = sorted(filter_source_df['company'].unique().tolist()) if 'company' in filter_source_df.columns else []

st.session_state['global_sectors'] = st.sidebar.multiselect(
    "Sectors", options=all_sectors,
    default=st.session_state.get('global_sectors', all_sectors)
)

if all_regions:
    st.session_state['global_regions'] = st.sidebar.multiselect(
        "Regions", options=all_regions,
        default=st.session_state.get('global_regions', all_regions)
    )
else:
    st.session_state['global_regions'] = []

available_companies = sorted(
    filter_source_df[
        filter_source_df['sector'].isin(st.session_state['global_sectors'])
    ]['company'].unique().tolist()
) if 'company' in filter_source_df.columns else all_companies

st.session_state['global_companies'] = st.sidebar.multiselect(
    "Companies", options=available_companies,
    default=st.session_state.get('global_companies', available_companies)
)

st.sidebar.markdown("---")

# Template Download
st.sidebar.markdown("**📥 Need a template?**")
template_cols = {c: '' for c in REQUIRED_COLS}
template_df = pd.DataFrame([template_cols])
template_csv = template_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download Template",
    data=template_csv,
    file_name="analyst_center_template.csv",
    mime="text/csv"
)

st.write("---")
st.markdown("### 🌐 Global High-Level Overview")

# Data source badge
if st.session_state.get('uploaded_df') is not None:
    st.success("🟢 **Live Data Mode** — Charts reflect your uploaded dataset.")
else:
    st.caption("Data generated synthetically for demonstration purposes. Upload a CSV in the sidebar to use real data.")

# Load data via master loader (respects global filters)
with st.spinner("Initializing Data Engine..."):
    from utils import get_filtered_data
    df = get_filtered_data()

# Slice most recent vs prior period
dates = sorted(df['date'].unique())
latest_date = dates[-1]
prev_date = dates[-2]
latest_data = df[df['date'] == latest_date]
prev_data = df[df['date'] == prev_date]

# Revenue MoM
total_revenue = latest_data['revenue'].sum()
prev_revenue = prev_data['revenue'].sum()
rev_delta = (total_revenue - prev_revenue) / prev_revenue

# Returns & Valuation
avg_roe = latest_data['roe_%'].mean()
prev_roe = prev_data['roe_%'].mean()
roe_delta = avg_roe - prev_roe

avg_pe = latest_data['pe_ratio'].mean()
avg_roic = latest_data['roic_%'].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Global Monthly Revenue", f"${total_revenue/1e6:.1f}M", f"{rev_delta*100:+.1f}% MoM")
m2.metric("Avg Portfolio ROE", f"{avg_roe*100:.1f}%", f"{roe_delta*100:+.1f}% MoM")
m3.metric("Avg ROIC (Projected)", f"{avg_roic*100:.1f}%", "Efficient" if avg_roic > 0.1 else "Capital Heavy")
m4.metric("Avg P/E Ratio", f"{avg_pe:.1f}x", "Market Standard")

st.write("---")

col_radar, col_df = st.columns([1, 1])

with col_radar:
    st.markdown("### 🎯 Portfolio Risk Radar")
    from utils import get_risk_rating, apply_chart_theme
    import plotly.express as px
    
    # Calculate risk for latest period
    radar_df = latest_data.copy()
    radar_df['Risk'] = radar_df.apply(get_risk_rating, axis=1)
    
    fig_radar = px.scatter(radar_df, x="debt_to_equity", y="net_margin_%", 
                           color="Risk", size="revenue", hover_name="company",
                           labels={'debt_to_equity': 'Leverage (D/E)', 'net_margin_%': 'Net Margin (%)'},
                           color_discrete_map={'Distress Zone': '#ef4444', 'Grey Zone': '#f59e0b', 'Safe Zone': '#10b981'})
    fig_radar.update_layout(title="Leverage vs. Profitability (Altman Z-Score)", **apply_chart_theme())
    st.plotly_chart(fig_radar, use_container_width=True)

with col_df:
    st.markdown("### 🏆 Top 5 Valuations")
    top_v = latest_data.sort_values('market_cap', ascending=False).head(5)
    st.table(top_v[['company', 'sector', 'market_cap', 'pe_ratio']].rename(columns={'market_cap': 'Market Cap ($)', 'pe_ratio': 'P/E'}))

st.markdown("### 📊 Raw Dataset Peek")
st.dataframe(df.head(10), use_container_width=True)

# Data export from home page too
st.download_button(
    "⬇️ Download Full Dataset (CSV)",
    df.to_csv(index=False).encode('utf-8'),
    file_name='analyst_command_center_data.csv',
    mime='text/csv'
)
