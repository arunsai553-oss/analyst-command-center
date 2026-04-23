import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_and_generate_data, calculate_kpis, get_data

st.set_page_config(page_title="Executive Summary", page_icon="📝", layout="wide")

st.markdown("# 📝 Executive Summary")
st.markdown("Automated strategic synthesis of portfolio data for leadership.")

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
    st.markdown("#### Strategic Recommendations")
    st.info(f"""
    **To Leadership:**
    Based on the latest portfolio signals:
    1. **Scale the Winner**: Accelerate capital allocation towards **{top_grower['company']}** to capitalize on their **{top_grower['growth']*100:.1f}%** momentum.
    2. **Operational Recovery**: Initiate an urgent performance audit for **{bottom_grower['company']}** to address the recent **{bottom_grower['growth']*100:.1f}%** drag.
    3. **Go-to-Market (GTM)**: Review acquisition channels for companies with CAC exceeding **${latest_data['cac'].mean()*1.2:.2f}** (20% above portfolio average).
    4. **Funnel UX**: Roll out the one-click checkout verified in Q4 experiments to all high-traffic retail segments.
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
