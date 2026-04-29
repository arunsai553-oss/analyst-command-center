import streamlit as st
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_data, get_numeric_cols, get_categorical_cols, get_date_col, apply_chart_theme, auto_metric, auto_group, format_value
import plotly.express as px

st.set_page_config(page_title="Tableau Data Studio", page_icon="🧮", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem; }
    .sub-text { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        background-color: white;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
        background-color: #f8fafc;
        transform: translateY(-2px);
    }
    .active-btn > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🧮 Tableau Data Studio</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Advanced drag-and-drop exploration combined with one-click quick charts.</p>', unsafe_allow_html=True)

# Master Data Load
df = get_data()
num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)
date_col = get_date_col(df)

if df.empty:
    st.warning("No data loaded. Please upload a CSV in the sidebar or use the demo data.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: QUICK BUILDER (Plotly based)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### ⚡ Quick Chart Builder")
st.caption("Select a chart type and axes to instantly visualize patterns.")

# Layout for Quick Builder
col_ctrl, col_chart = st.columns([1, 3])

with col_ctrl:
    chart_type = st.selectbox("Chart Type", 
                                ["Bar", "Line", "Area", "Scatter", "Pie", "Histogram", "Box Plot", "Heatmap"],
                                index=0)
    
    if num_cols:
        default_x = date_col if date_col and chart_type in ["Line", "Area"] else (cat_cols[0] if cat_cols else num_cols[0])
        x_axis = st.selectbox("X-Axis", df.columns, index=df.columns.get_loc(default_x) if default_x in df.columns else 0)
        
        default_y = auto_metric(df) or num_cols[0]
        y_axis = st.selectbox("Y-Axis", num_cols, index=num_cols.index(default_y) if default_y in num_cols else 0)
        
        color_opts = ["(none)"] + cat_cols
        color_by = st.selectbox("Color/Legend", color_opts, index=0)
        color_arg = None if color_by == "(none)" else color_by
        
        agg_fn = st.selectbox("Aggregation", ["sum", "mean", "median", "count", "max", "min"], index=0)
    else:
        st.warning("No numeric columns found for chart building.")

with col_chart:
    if num_cols:
        try:
            fig = None
            title = f"{agg_fn.title()} {y_axis} by {x_axis}"
            
            if chart_type == "Bar":
                agg_df = df.groupby([x_axis] + ([color_by] if color_arg else []))[y_axis].agg(agg_fn).reset_index()
                fig = px.bar(agg_df, x=x_axis, y=y_axis, color=color_arg, title=title)
            
            elif chart_type == "Line":
                agg_df = df.groupby([x_axis] + ([color_by] if color_arg else []))[y_axis].agg(agg_fn).reset_index()
                fig = px.line(agg_df, x=x_axis, y=y_axis, color=color_arg, title=title, markers=True)
                
            elif chart_type == "Area":
                agg_df = df.groupby([x_axis] + ([color_by] if color_arg else []))[y_axis].agg(agg_fn).reset_index()
                fig = px.area(agg_df, x=x_axis, y=y_axis, color=color_arg, title=title)
                
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color_arg, title=title, opacity=0.7)
                
            elif chart_type == "Pie":
                agg_df = df.groupby(x_axis)[y_axis].agg(agg_fn).reset_index()
                fig = px.pie(agg_df, names=x_axis, values=y_axis, title=title)
                
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_axis, color=color_arg, title=f"Distribution of {x_axis}")
                
            elif chart_type == "Box Plot":
                fig = px.box(df, x=x_axis, y=y_axis, color=color_arg, title=f"Box Plot of {y_axis} by {x_axis}")
                
            elif chart_type == "Heatmap" and cat_cols:
                y_cat = st.selectbox("Y-Category", [c for c in cat_cols if c != x_axis], key="heat_y")
                piv = df.pivot_table(values=y_axis, index=y_cat, columns=x_axis, aggfunc=agg_fn).fillna(0)
                fig = px.imshow(piv, text_auto=True, aspect="auto", title=f"{agg_fn.title()} {y_axis} Heatmap")

            if fig:
                fig.update_layout(**apply_chart_theme())
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

st.write("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: ADVANCED EXPLORER (PyGWalker)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 🧱 Advanced Drag-and-Drop Explorer")
st.caption("Native Tableau-like experience. Drag fields from the left to columns/rows/color to build custom views.")

@st.cache_resource
def get_pyg_renderer(df_hashable):
    # PyGWalker needs the actual dataframe
    return StreamlitRenderer(df, spec="./gw_config.json", debug=False)

# We use a trick to make the dataframe "hashable" or just rely on session state
renderer = get_pyg_renderer(id(df))
renderer.explorer()
