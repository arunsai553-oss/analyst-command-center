import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
from utils import (get_data, get_filtered_data, get_numeric_cols,
                   get_categorical_cols, get_date_col, auto_metric,
                   auto_group, apply_chart_theme, format_value, infer_and_coerce_dates,
                   clean_numeric_columns)

st.set_page_config(
    page_title="Analyst Command Center",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background-color: #f1f5f9; }
.gradient-text {
    background: -webkit-linear-gradient(45deg, #0284c7, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem; font-weight: 800; margin-bottom: 0px;
}
.sub-head { font-size:1.1rem; color:#475569; margin-top:-10px; margin-bottom:25px; }
div[data-testid="stMetric"] {
    background-color: #ffffff; border: 1px solid #e2e8f0;
    padding: 15px 20px; border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: #3b82f6; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="gradient-text">Analyst Command Center</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-head">Upload any dataset — the dashboard adapts automatically.</p>', unsafe_allow_html=True)
st.write("---")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Upload ANY CSV
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔌 Connect Your Data")
st.sidebar.caption("Upload **any** CSV — sales, HR, operations, survey, financial — the app adapts.")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    try:
        with st.spinner("🚀 AI Analyzing Data Structure..."):
            raw_bytes = uploaded_file.read()
            user_df = pd.read_csv(io.BytesIO(raw_bytes))

            # Normalize column names: lowercase, strip, underscores
            user_df.columns = [c.strip().lower().replace(' ', '_').replace('-','_') for c in user_df.columns]

            # Senior Analyst Cleaning
            user_df = clean_numeric_columns(user_df)
            user_df = infer_and_coerce_dates(user_df)

            if user_df.empty or len(user_df.columns) == 0:
                st.sidebar.error("❌ File appears empty or unreadable.")
            else:
                file_id = f"{uploaded_file.name}_{len(raw_bytes)}"
                if st.session_state.get('last_file_id') != file_id:
                    # NUCLEAR RESET: Clear everything that might hold old column names
                    st.cache_data.clear()
                    keys_to_clear = [k for k in st.session_state.keys() if k not in ['last_file_id', 'uploaded_df']]
                    for k in keys_to_clear:
                        st.session_state.pop(k, None)
                    
                    st.session_state['last_file_id'] = file_id
                    st.rerun() # Force a clean refresh for the new dataset

                st.session_state['uploaded_df'] = user_df
                n_num = len(get_numeric_cols(user_df))
                n_cat = len(get_categorical_cols(user_df))
                n_dt  = 1 if get_date_col(user_df) else 0
                st.sidebar.success(
                    f"✅ **Loaded** — {len(user_df):,} rows\n\n"
                    f"📊 {n_num} metrics · 🏷️ {n_cat} segments"
                )
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")
else:
    if st.session_state.get('uploaded_df') is not None:
        st.session_state['uploaded_df'] = None
        st.cache_data.clear()
        for k in ['global_filter_col','global_filter_vals','last_file_id']:
            st.session_state.pop(k, None)
        st.rerun()

st.sidebar.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Dynamic Filter (works on ANY column)
# ─────────────────────────────────────────────────────────────────────────────
df_for_filter = get_data()
cat_cols = get_categorical_cols(df_for_filter)

if cat_cols:
    st.sidebar.markdown("## 🎯 Global Filter")
    filter_col = st.sidebar.selectbox(
        "Filter by column",
        ["(none)"] + cat_cols,
        key="global_filter_col_widget"
    )
    if filter_col != "(none)":
        options = sorted(df_for_filter[filter_col].dropna().unique().tolist())
        selected = st.sidebar.multiselect(
            f"Select {filter_col} values",
            options, default=options,
            key="global_filter_vals_widget"
        )
        st.session_state['global_filter_col'] = filter_col
        st.session_state['global_filter_vals'] = selected
    else:
        st.session_state['global_filter_col'] = None
        st.session_state['global_filter_vals'] = []
    st.sidebar.markdown("---")

# Download current dataset
st.sidebar.markdown("**📥 Download current dataset**")
dl_df = get_data()
st.sidebar.download_button(
    "Download CSV", dl_df.to_csv(index=False).encode('utf-8'),
    file_name="current_dataset.csv", mime="text/csv"
)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT — Fully Dynamic Overview
# ─────────────────────────────────────────────────────────────────────────────
is_live = st.session_state.get('uploaded_df') is not None

if is_live:
    st.success("🟢 **Live Data Mode** — all pages reflect your uploaded dataset.")
else:
    st.info("📊 **Demo Mode** — showing synthetic financial data. Upload any CSV in the sidebar.")

df = get_filtered_data()
num_cols  = get_numeric_cols(df)
cat_cols  = get_categorical_cols(df)
date_col  = get_date_col(df)

# ── Dataset Info Cards ───────────────────────────────────────────────────────
st.markdown("### 📋 Dataset Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric("Numeric Metrics", len(num_cols))
c4.metric("Categories", len(cat_cols))

# ── AI Executive Summary (Senior AI Analyst Mode) ────────────────────────────
with st.container():
    st.markdown("""
    <div style="background-color: #f8fafc; padding: 20px; border-left: 5px solid #3b82f6; border-radius: 8px; margin: 20px 0;">
        <h3 style="margin-top:0; color: #1e3a8a;">🧠 AI Executive Summary</h3>
        <p style="color: #64748b; font-size: 0.9rem;">Synthesizing strategic insights across all data dimensions...</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        if num_cols:
            top_metric = auto_metric(df)
            avg_val = df[top_metric].mean()
            volatility = (df[top_metric].std() / avg_val * 100) if avg_val != 0 else 0
            st.markdown(f"**📈 Primary Metric Analysis ({top_metric.title()}):**")
            st.write(f"- Average performance is sitting at **{format_value(avg_val)}**.")
            st.write(f"- Data volatility is **{volatility:.1f}%**, suggesting {'stable' if volatility < 20 else 'high'} fluctuation.")
        else:
            st.write("- No numeric metrics found to analyze.")

    with col_ai2:
        if cat_cols:
            primary_cat = auto_group(df) or cat_cols[0]
            top_segment = df[primary_cat].value_counts().idxmax()
            coverage = (df[primary_cat].value_counts().max() / len(df)) * 100
            st.markdown(f"**🏷️ Segment Concentration ({primary_cat.title()}):**")
            st.write(f"- The dominant segment is **'{top_segment}'**.")
            st.write(f"- It accounts for **{coverage:.1f}%** of the total dataset activity.")
        else:
            st.write("- No categorical segments found to analyze.")

# ── Quick KPI metrics from numeric columns ───────────────────────────────────
if num_cols:
    st.markdown("### 📈 Quick Stats")
    kpi_cols = num_cols[:8]  # show up to 8
    rows = [st.columns(4), st.columns(4)] if len(kpi_cols) > 4 else [st.columns(len(kpi_cols))]
    flat = [c for row in rows for c in row]
    for i, col in enumerate(kpi_cols[:len(flat)]):
        val = df[col].sum() if df[col].sum() > df[col].mean()*5 else df[col].mean()
        label = "Total" if df[col].sum() > df[col].mean()*5 else "Avg"
        flat[i].metric(f"{label} {col.replace('_',' ').title()}", format_value(val))

st.write("---")

# ── Automatic Charts ─────────────────────────────────────────────────────────
st.markdown("### 📊 Automatic Analysis")

if date_col and num_cols:
    # Time series of first numeric col
    metric = auto_metric(df)
    group  = auto_group(df)
    try:
        ts_df = df.copy()
        ts_df[date_col] = pd.to_datetime(ts_df[date_col])
        if group:
            agg = ts_df.groupby([date_col, group])[metric].sum().reset_index()
            fig = px.area(agg, x=date_col, y=metric, color=group,
                          title=f"{metric.replace('_',' ').title()} over Time by {group.replace('_',' ').title()}")
        else:
            agg = ts_df.groupby(date_col)[metric].sum().reset_index()
            fig = px.line(agg, x=date_col, y=metric,
                          title=f"{metric.replace('_',' ').title()} over Time")
        fig.update_layout(**apply_chart_theme())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render time series: {e}")

col_l, col_r = st.columns(2)

with col_l:
    if cat_cols and num_cols:
        grp = auto_group(df) or cat_cols[0]
        met = auto_metric(df) or num_cols[0]
        try:
            bar_df = df.groupby(grp)[met].sum().sort_values(ascending=False).head(15).reset_index()
            fig2 = px.bar(bar_df, x=grp, y=met, color=grp,
                          title=f"Total {met.replace('_',' ').title()} by {grp.replace('_',' ').title()}")
            fig2.update_layout(**apply_chart_theme(), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Bar chart error: {e}")

with col_r:
    if len(num_cols) >= 2:
        try:
            fig3 = px.scatter(df, x=num_cols[0], y=num_cols[1],
                              color=auto_group(df),
                              title=f"{num_cols[0].replace('_',' ').title()} vs {num_cols[1].replace('_',' ').title()}")
            fig3.update_layout(**apply_chart_theme())
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.warning(f"Scatter error: {e}")
    elif cat_cols and num_cols:
        try:
            pie_df = df.groupby(cat_cols[0])[num_cols[0]].sum().reset_index()
            fig3 = px.pie(pie_df, names=cat_cols[0], values=num_cols[0],
                          title=f"{num_cols[0].replace('_',' ').title()} breakdown")
            fig3.update_layout(**apply_chart_theme())
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.warning(f"Pie chart error: {e}")

# ── Raw Data Preview ─────────────────────────────────────────────────────────
st.markdown("### 🔍 Data Preview")
st.dataframe(df.head(20), use_container_width=True)

st.download_button(
    "⬇️ Download Full Dataset (CSV)",
    df.to_csv(index=False).encode('utf-8'),
    file_name='dataset.csv', mime='text/csv'
)
