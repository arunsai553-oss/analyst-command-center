import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_experiment_data, apply_chart_theme, get_data

st.set_page_config(page_title="Experiments & KPIs", page_icon="🧪", layout="wide")

st.markdown("# 🧪 Experiments & KPIs")
st.markdown("Evaluate A/B tests and extract statistically rigorous insights for product decisions.")

# Use main portfolio data for experiment-level KPIs where applicable
df = get_data()
# Experiment-specific data (A/B testing synthetic cohorts)
ab_df = load_experiment_data()

st.sidebar.markdown("### Experiment Parameters")
st.sidebar.caption("Filter test subjects")
date_range = st.sidebar.date_input("Filter Date Range", [ab_df['date'].min(), ab_df['date'].max()])

# Filter data
mask = (ab_df['date'].dt.date >= date_range[0]) & (ab_df['date'].dt.date <= date_range[1])
filtered_df = ab_df[mask]

st.markdown("### 📊 Test Readout: Q4 Checkout Funnel Optimization")
st.markdown("**Hypothesis**: Introducing a one-click checkout will increase overall conversion rates.")

control_group = filtered_df[filtered_df['group'] == 'Control']['value']
treatment_group = filtered_df[filtered_df['group'] == 'Treatment']['value']

ctrl_mean = control_group.mean()
trt_mean = treatment_group.mean()
lift = (trt_mean - ctrl_mean) / ctrl_mean if ctrl_mean > 0 else 0

# T-Test (Independent)
t_stat, p_val = stats.ttest_ind(treatment_group, control_group, equal_var=False)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Control Conversion", f"{ctrl_mean*100:.2f}%")
col2.metric("Treatment Conversion", f"{trt_mean*100:.2f}%")
col3.metric("Observed Lift", f"{lift*100:.2f}%", f"{t_stat:.2f} t-stat")
col4.metric("P-Value", f"{p_val:.4f}", "Significant" if p_val < 0.05 else "Not Significant", delta_color="inverse" if p_val >= 0.05 else "normal")

st.markdown("---")

col_chart, col_text = st.columns([2, 1])

with col_chart:
    # Daily running conversion rate
    cume_data = filtered_df.sort_values('date').groupby(['date', 'group']).agg({'value': ['count', 'sum']}).reset_index()
    cume_data.columns = ['date', 'group', 'trials', 'successes']
    cume_data['cume_trials'] = cume_data.groupby('group')['trials'].cumsum()
    cume_data['cume_successes'] = cume_data.groupby('group')['successes'].cumsum()
    cume_data['cume_conv_rate'] = cume_data['cume_successes'] / cume_data['cume_trials']

    fig = px.line(cume_data, x='date', y='cume_conv_rate', color='group', title='Cumulative Conversion Rate over Time')
    fig.update_layout(yaxis_tickformat='.2%', **apply_chart_theme())
    st.plotly_chart(fig, use_container_width=True)

with col_text:
    st.info("💡 **Executive Interpretation**")
    if p_val < 0.05:
        st.success(f"""
        **Test is Statistically Significant!** 
        We observed a {lift*100:.1f}% relative lift in the treatment group. 
        There is a {(1-p_val)*100:.1f}% probability that this result is not due to random chance. 
        
        **Recommendation:** Roll out the one-click checkout feature to 100% of the user base.
        """)
    else:
        st.warning(f"""
        **Result is Inconclusive.** 
        While we observed a {lift*100:.1f}% difference, the p-value of {p_val:.3f} is above our 0.05 alpha threshold.
        
        **Recommendation:** Continue monitoring the experiment to gather more statistical power, or redesign the intervention.
        """)

    st.markdown("### Confidence Intervals")
    # Basic confidence intervals
    ci_ctrl = stats.t.interval(0.95, len(control_group)-1, loc=np.mean(control_group), scale=stats.sem(control_group))
    ci_trt = stats.t.interval(0.95, len(treatment_group)-1, loc=np.mean(treatment_group), scale=stats.sem(treatment_group))
    
    st.write(f"**Control 95% CI:** {ci_ctrl[0]*100:.1f}% - {ci_ctrl[1]*100:.1f}%")
    st.write(f"**Treatment 95% CI:** {ci_trt[0]*100:.1f}% - {ci_trt[1]*100:.1f}%")
