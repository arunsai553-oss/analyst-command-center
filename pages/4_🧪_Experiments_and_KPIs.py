import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_data, get_numeric_cols, get_categorical_cols, apply_chart_theme, load_experiment_data

st.set_page_config(page_title="Statistics & A/B Tests", page_icon="🧪", layout="wide")
st.markdown("# 🧪 Statistics & A/B Testing")

df = get_data()
num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)

tab1, tab2 = st.tabs(["📊 Distribution & Stats", "🔬 A/B Test Simulator"])

with tab1:
    st.markdown("### Descriptive Statistics")
    if num_cols:
        st.dataframe(df[num_cols].describe().T.style.background_gradient(cmap='Blues', axis=1),
                     use_container_width=True)

        st.markdown("### Box Plot — Compare Distributions")
        c1, c2 = st.columns(2)
        with c1: box_col = st.selectbox("Numeric Column", num_cols, key="box_col")
        with c2:
            grp_opts = ["(none)"] + cat_cols
            box_grp  = st.selectbox("Group By", grp_opts, key="box_grp")
            box_grp  = None if box_grp == "(none)" else box_grp

        try:
            fig = px.box(df, x=box_grp, y=box_col, color=box_grp, points="outliers",
                         title=f"Distribution of {box_col.replace('_',' ').title()}")
            fig.update_layout(**apply_chart_theme(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Box plot error: {e}")

        if cat_cols and len(num_cols) >= 1:
            st.markdown("### Statistical Significance Test (t-test)")
            st.caption("Compare means of a numeric column between two groups.")
            c1, c2, c3 = st.columns(3)
            with c1: test_col = st.selectbox("Numeric Column", num_cols, key="ttest_col")
            with c2: grp_col  = st.selectbox("Group Column", cat_cols, key="ttest_grp")
            groups = df[grp_col].dropna().unique().tolist()
            with c3:
                if len(groups) >= 2:
                    sel_grp = st.multiselect("Select 2 Groups", groups,
                                             default=groups[:2], max_selections=2, key="ttest_grps")
                else:
                    sel_grp = groups
                    st.info("Need 2+ groups")

            if len(sel_grp) == 2:
                g1 = df[df[grp_col]==sel_grp[0]][test_col].dropna()
                g2 = df[df[grp_col]==sel_grp[1]][test_col].dropna()
                t, p = stats.ttest_ind(g1, g2, equal_var=False)
                lift = (g2.mean() - g1.mean()) / g1.mean() * 100 if g1.mean() else 0
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(f"{sel_grp[0]} Mean", f"{g1.mean():.3f}")
                m2.metric(f"{sel_grp[1]} Mean", f"{g2.mean():.3f}")
                m3.metric("Difference", f"{lift:+.2f}%", f"t={t:.2f}")
                m4.metric("P-Value", f"{p:.4f}", "Significant ✅" if p < 0.05 else "Not Sig ⚠️",
                          delta_color="normal" if p < 0.05 else "inverse")

                fig2 = px.histogram(df[df[grp_col].isin(sel_grp)], x=test_col, color=grp_col,
                                    barmode='overlay', opacity=0.7, nbins=30,
                                    title=f"Distribution Comparison: {test_col.replace('_',' ').title()}")
                fig2.update_layout(**apply_chart_theme())
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No numeric columns found in your dataset.")

with tab2:
    st.markdown("### A/B Test Simulator (Synthetic Data)")
    st.caption("Built-in A/B test data: Q4 checkout funnel optimization experiment.")

    ab_df = load_experiment_data()
    date_range = st.sidebar.date_input("Filter Date Range", [ab_df['date'].min(), ab_df['date'].max()])

    try:
        mask = (ab_df['date'].dt.date >= date_range[0]) & (ab_df['date'].dt.date <= date_range[1])
        ab_filt = ab_df[mask]

        ctrl = ab_filt[ab_filt['group']=='Control']['value']
        trt  = ab_filt[ab_filt['group']=='Treatment']['value']
        t_s, p_v = stats.ttest_ind(trt, ctrl, equal_var=False)
        lift = (trt.mean()-ctrl.mean())/ctrl.mean() if ctrl.mean() else 0

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Control Conv.", f"{ctrl.mean()*100:.2f}%")
        m2.metric("Treatment Conv.", f"{trt.mean()*100:.2f}%")
        m3.metric("Lift", f"{lift*100:+.2f}%", f"t={t_s:.2f}")
        m4.metric("P-Value", f"{p_v:.4f}", "Significant ✅" if p_v < 0.05 else "Not Sig ⚠️",
                  delta_color="normal" if p_v < 0.05 else "inverse")

        cum = ab_filt.sort_values('date').groupby(['date','group']).agg(
            trials=('value','count'), wins=('value','sum')).reset_index()
        cum['cum_trials'] = cum.groupby('group')['trials'].cumsum()
        cum['cum_wins']   = cum.groupby('group')['wins'].cumsum()
        cum['conv_rate']  = cum['cum_wins'] / cum['cum_trials']

        fig = px.line(cum, x='date', y='conv_rate', color='group',
                      title='Cumulative Conversion Rate')
        fig.update_layout(yaxis_tickformat='.2%', **apply_chart_theme())
        st.plotly_chart(fig, use_container_width=True)

        if p_v < 0.05:
            st.success(f"**Significant!** {lift*100:.1f}% lift. Confidence: {(1-p_v)*100:.1f}%.")
        else:
            st.warning(f"**Inconclusive.** p={p_v:.3f} > 0.05. Gather more data.")
    except Exception as e:
        st.error(f"A/B test error: {e}")
