import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, calculate_kpis

st.set_page_config(page_title="Executive Summary", page_icon="📝", layout="wide")

st.markdown("# 📝 Executive Summary")
st.markdown("Automated strategic synthesis of portfolio data for leadership.")

@st.cache_data
def get_data():
    return calculate_kpis(load_and_generate_data())

df = get_data()
latest_date = df['date'].max()
prev_date = df['date'].unique()[-2] # Assuming sorted, get the prior period

latest_data = df[df['date'] == latest_date]
prev_data = df[df['date'] == prev_date]

total_rev_cur = latest_data['revenue'].sum()
total_rev_prev = prev_data['revenue'].sum()
rev_growth = (total_rev_cur - total_rev_prev) / total_rev_prev

# Identify top grower
growth_df = pd.merge(latest_data[['company', 'revenue']], prev_data[['company', 'revenue']], on='company', suffixes=('_cur', '_prev'))
growth_df['growth'] = (growth_df['revenue_cur'] - growth_df['revenue_prev']) / growth_df['revenue_prev']
top_grower = growth_df.loc[growth_df['growth'].idxmax()]
bottom_grower = growth_df.loc[growth_df['growth'].idxmin()]

st.markdown("---")
st.markdown("### 📋 Auto-Generated Narrative Board")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Macro Trends")
    st.markdown(f"""
    - **Global Revenue Growth:** Portfolio overall revenue evolved by **{rev_growth*100:.1f}%** compared to the previous period.
    - **Top Performer:** **{top_grower['company']}** led the pack with a staggering **{top_grower['growth']*100:.1f}%** growth.
    - **Area of Concern:** **{bottom_grower['company']}** experienced the most drag at **{bottom_grower['growth']*100:.1f}%**.
    - **Efficiency:** Average Customer Acquisition Cost (CAC) across the board currently sits at **${latest_data['cac'].mean():.2f}**.
    """)

with col2:
    st.markdown("#### Strategic Recommendations (Template)")
    st.info("""
    **To Leadership:**
    Based on the exploratory analysis and funnel optimization test:
    1. **Scale the Winner**: Accelerate marketing spend towards the channels performing well for top growers.
    2. **Implement Features**: Roll out the one-click checkout across all retail domains given the statistically significant lift observed in Q4 tests.
    3. **Investigate Drag**: Open an operational review for the bottom quartile companies failing to meet baseline margin assumptions.
    """)

st.write("---")
st.markdown("### Export Capability")
st.caption("Allow stakeholders to download clean, processed datasets directly from the dashboard.")

csv = latest_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Latest Period Data (CSV)",
    data=csv,
    file_name='latest_portfolio_data.csv',
    mime='text/csv',
)
