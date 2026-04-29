import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_filtered_data, get_numeric_cols, get_categorical_cols, apply_chart_theme

st.set_page_config(page_title="Deep Dive Lab", page_icon="🔬", layout="wide")
st.markdown("# 🔬 Deep Dive Lab")
st.markdown("Correlations, distributions, pivot analysis — on any dataset.")

df = get_filtered_data()
num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)

if len(num_cols) < 2:
    st.warning("⚠️ Deep Dive requires at least 2 numeric columns. Your dataset has: " + str(num_cols))
    st.dataframe(df.head(10), use_container_width=True)
    st.stop()

# ── Correlation Matrix ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧩 Correlation Matrix")
    sel_corr = st.multiselect("Select columns", num_cols, default=num_cols[:min(6, len(num_cols))])
    if len(sel_corr) >= 2:
        try:
            corr = df[sel_corr].corr()
            fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect='auto',
                            title="Correlation Heatmap")
            fig.update_layout(**apply_chart_theme())
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Correlation error: {e}")
    else:
        st.info("Select at least 2 columns.")

with col2:
    st.markdown("### 📊 Distribution Explorer")
    dist_col = st.selectbox("Column to analyze", num_cols, key="dist_col")
    color_by  = st.selectbox("Color By", ["(none)"] + cat_cols, key="dist_color")
    color_arg = None if color_by == "(none)" else color_by
    try:
        fig2 = px.histogram(df, x=dist_col, color=color_arg, nbins=40,
                            title=f"Distribution of {dist_col.replace('_',' ').title()}",
                            marginal="box")
        fig2.update_layout(**apply_chart_theme())
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Histogram error: {e}")

# ── Pivot Table ──────────────────────────────────────────────────────────────
st.markdown("### 🎲 Dynamic Pivot Table")
if cat_cols:
    c1, c2, c3, c4 = st.columns(4)
    with c1: pivot_idx = st.selectbox("Rows (Group By)", cat_cols, key="piv_idx")
    with c2: pivot_val = st.selectbox("Value", num_cols, key="piv_val")
    with c3: pivot_agg = st.selectbox("Aggregation", ["sum","mean","median","count","max","min"], key="piv_agg")
    with c4:
        col_opts = ["(none)"] + [c for c in cat_cols if c != pivot_idx]
        pivot_col = st.selectbox("Columns (Optional)", col_opts, key="piv_col")

    try:
        if pivot_col != "(none)":
            piv = pd.pivot_table(df, values=pivot_val, index=pivot_idx,
                                 columns=pivot_col, aggfunc=pivot_agg).fillna(0)
            st.dataframe(piv.style.background_gradient(cmap='Blues'), use_container_width=True)
            fig3 = px.imshow(piv, text_auto=True, color_continuous_scale='Viridis', aspect='auto',
                             title=f"{pivot_val} by {pivot_idx} × {pivot_col}")
            fig3.update_layout(**apply_chart_theme())
            st.plotly_chart(fig3, use_container_width=True)
        else:
            agg_df = df.groupby(pivot_idx)[pivot_val].agg(pivot_agg).reset_index().sort_values(pivot_val, ascending=False)
            fig3 = px.bar(agg_df, x=pivot_idx, y=pivot_val, color=pivot_idx,
                          title=f"{pivot_agg.title()} {pivot_val.replace('_',' ').title()} by {pivot_idx.replace('_',' ').title()}")
            fig3.update_layout(**apply_chart_theme(), showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
    except Exception as e:
        st.error(f"Pivot error: {e}")
else:
    st.info("Add categorical columns to enable pivot analysis.")

# ── Scatter ──────────────────────────────────────────────────────────────────
st.markdown("### 🔵 Scatter Analysis")
sc1, sc2, sc3, sc4 = st.columns(4)
with sc1: sc_x = st.selectbox("X Axis", num_cols, index=0, key="sc_x")
with sc2: sc_y = st.selectbox("Y Axis", num_cols, index=min(1,len(num_cols)-1), key="sc_y")
with sc3:
    size_opts = ["(none)"] + num_cols
    sc_sz = st.selectbox("Size", size_opts, key="sc_sz")
    sc_sz = None if sc_sz == "(none)" else sc_sz
with sc4:
    col_opts2 = ["(none)"] + cat_cols
    sc_col = st.selectbox("Color", col_opts2, key="sc_col")
    sc_col = None if sc_col == "(none)" else sc_col

try:
    hover_col = cat_cols[0] if cat_cols else None
    fig4 = px.scatter(df, x=sc_x, y=sc_y, size=sc_sz, color=sc_col,
                      hover_name=hover_col, marginal_x="box", marginal_y="box",
                      title=f"{sc_y.replace('_',' ').title()} vs {sc_x.replace('_',' ').title()}")
    fig4.update_layout(**apply_chart_theme())
    st.plotly_chart(fig4, use_container_width=True)
except Exception as e:
    st.error(f"Scatter error: {e}")
