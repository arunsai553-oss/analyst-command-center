import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_filtered_data, get_numeric_cols, get_categorical_cols, get_date_col, apply_chart_theme, auto_metric, auto_group

st.set_page_config(page_title="Market Scanner", page_icon="📊", layout="wide")
st.markdown("# 📊 Trends & Time Series")

df = get_filtered_data()
num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)
date_col = get_date_col(df)

if not date_col:
    st.warning("⚠️ No date/time column detected. Time series analysis requires a date column.")
    st.dataframe(df.head(20), use_container_width=True)
    st.stop()

if not num_cols:
    st.warning("⚠️ No numeric columns found for analysis.")
    st.stop()

# Ensure date is datetime
df = df.copy()
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df = df.dropna(subset=[date_col])

tab1, tab2 = st.tabs(["📈 Time Series", "🏆 Rankings"])

with tab1:
    col_m, col_g, col_a = st.columns(3)
    with col_m:
        metric = st.selectbox("Metric", num_cols, index=0, key="ts_metric")
    with col_g:
        group_opts = ["(none)"] + cat_cols
        group = st.selectbox("Group By", group_opts,
                             index=group_opts.index(auto_group(df)) if auto_group(df) in group_opts else 0,
                             key="ts_group")
        group = None if group == "(none)" else group
    with col_a:
        agg_fn = st.selectbox("Aggregation", ["sum","mean","median","max","min"], key="ts_agg")

    try:
        if group:
            agg_df = df.groupby([date_col, group])[metric].agg(agg_fn).reset_index()
            fig = px.area(agg_df, x=date_col, y=metric, color=group,
                          title=f"{agg_fn.title()} {metric.replace('_',' ').title()} over Time by {group.replace('_',' ').title()}")
        else:
            agg_df = df.groupby(date_col)[metric].agg(agg_fn).reset_index()
            fig = px.line(agg_df, x=date_col, y=metric, markers=True,
                          title=f"{agg_fn.title()} {metric.replace('_',' ').title()} over Time")
        fig.update_layout(**apply_chart_theme())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")

    # Multi-metric trend
    if len(num_cols) > 1:
        st.markdown("### Multi-Metric Trend")
        sel_metrics = st.multiselect("Compare metrics", num_cols, default=num_cols[:3], key="multi_metric")
        if sel_metrics:
            try:
                m_df = df.groupby(date_col)[sel_metrics].mean().reset_index()
                fig2 = go.Figure()
                for m in sel_metrics:
                    fig2.add_trace(go.Scatter(x=m_df[date_col], y=m_df[m], mode='lines', name=m.replace('_',' ').title()))
                fig2.update_layout(title="Multi-Metric Comparison (Avg)", **apply_chart_theme())
                st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.error(f"Multi-metric error: {e}")

with tab2:
    st.markdown("### Rankings")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        rank_metric = st.selectbox("Rank By", num_cols, key="rank_metric")
    with r_col2:
        rank_group  = st.selectbox("Group By", cat_cols, key="rank_group") if cat_cols else None
        top_n = st.slider("Top N", 5, 50, 10, key="rank_n")

    if rank_group:
        try:
            ranked = df.groupby(rank_group)[rank_metric].sum().sort_values(ascending=False).head(top_n).reset_index()
            fig3 = px.bar(ranked, x=rank_group, y=rank_metric, color=rank_group,
                          title=f"Top {top_n} {rank_group.replace('_',' ').title()} by {rank_metric.replace('_',' ').title()}")
            fig3.update_layout(**apply_chart_theme(), showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(ranked, use_container_width=True)
        except Exception as e:
            st.error(f"Ranking error: {e}")
    else:
        st.info("Add a categorical column to your data to enable rankings.")
