import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_data

st.set_page_config(page_title="Tableau Data Studio", page_icon="🧮", layout="wide")

# ── CSS for chart-type buttons ──────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlock"] button {
    width: 100% !important;
}
.chart-header {
    background: linear-gradient(135deg, #1a1f3c 0%, #2d3561 100%);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 8px;
    color: #a78bfa;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧮 Tableau Data Studio")
st.write("---")

df = get_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")
if "sector" in df.columns:
    sectors = st.sidebar.multiselect("Sector", sorted(df["sector"].unique()), default=list(df["sector"].unique()))
    df = df[df["sector"].isin(sectors)]
if "company" in df.columns:
    companies = st.sidebar.multiselect("Company", sorted(df["company"].unique()), default=list(df["company"].unique()))
    df = df[df["company"].isin(companies)]

numeric_cols  = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(exclude="number").columns.tolist()
all_cols      = df.columns.tolist()

# ── Section 1: Quick Chart Builder ──────────────────────────────────────────
st.markdown('<div class="chart-header">⚡ SECTION 1 — Quick Chart Builder (Choose a Chart Type Below)</div>', unsafe_allow_html=True)

# ── Big labelled chart type buttons ─────────────────────────────────────────
chart_types = [
    ("📊", "Bar"),
    ("📈", "Line"),
    ("📉", "Area"),
    ("🔵", "Scatter"),
    ("🍩", "Pie"),
    ("🟦", "Histogram"),
    ("📦", "Box Plot"),
    ("🔥", "Heatmap"),
]

if "selected_chart" not in st.session_state:
    st.session_state.selected_chart = "Bar"

cols = st.columns(len(chart_types))
for i, (icon, name) in enumerate(chart_types):
    with cols[i]:
        is_active = st.session_state.selected_chart == name
        btn_style = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {name}", key=f"chart_btn_{name}", type=btn_style, use_container_width=True):
            st.session_state.selected_chart = name

chart_type = st.session_state.selected_chart
st.caption(f"Selected: **{chart_type}**  — Configure axes below, chart updates instantly.")

# ── Axis controls ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

if chart_type in ["Bar", "Line", "Area", "Scatter"]:
    with c1:
        x_col = st.selectbox("X Axis", all_cols, index=all_cols.index("date") if "date" in all_cols else 0, key="x_col")
    with c2:
        y_col = st.selectbox("Y Axis", numeric_cols, index=0, key="y_col")
    with c3:
        color_col_opts = ["None"] + category_cols
        color_col = st.selectbox("Color By", color_col_opts, key="color_col")
        color_col = None if color_col == "None" else color_col
    with c4:
        agg = st.selectbox("Aggregation", ["sum","mean","median","count","max","min"], key="agg")

elif chart_type == "Pie":
    with c1:
        pie_names = st.selectbox("Slice Labels", category_cols, key="pie_names")
    with c2:
        pie_vals  = st.selectbox("Slice Values", numeric_cols, key="pie_vals")
    with c3:
        hole = st.slider("Donut Hole", 0.0, 0.7, 0.0, 0.05, key="hole")
    with c4:
        agg = st.selectbox("Aggregation", ["sum","mean"], key="agg_pie")

elif chart_type == "Histogram":
    with c1:
        hist_col = st.selectbox("Column", numeric_cols, key="hist_col")
    with c2:
        nbins = st.slider("Bins", 5, 100, 30, key="nbins")
    with c3:
        color_col_opts = ["None"] + category_cols
        color_col = st.selectbox("Color By", color_col_opts, key="color_col_h")
        color_col = None if color_col == "None" else color_col
    with c4:
        st.empty()

elif chart_type == "Box Plot":
    with c1:
        box_y = st.selectbox("Value (Y)", numeric_cols, key="box_y")
    with c2:
        box_x_opts = ["None"] + category_cols
        box_x = st.selectbox("Group By (X)", box_x_opts, key="box_x")
        box_x = None if box_x == "None" else box_x
    with c3:
        color_col_opts = ["None"] + category_cols
        color_col = st.selectbox("Color By", color_col_opts, key="color_col_b")
        color_col = None if color_col == "None" else color_col
    with c4:
        st.empty()

elif chart_type == "Heatmap":
    with c1:
        hm_x = st.selectbox("X (Category)", category_cols, key="hm_x")
    with c2:
        hm_y = st.selectbox("Y (Category)", category_cols, index=min(1,len(category_cols)-1), key="hm_y")
    with c3:
        hm_val = st.selectbox("Value", numeric_cols, key="hm_val")
    with c4:
        st.empty()

# ── Render chart ─────────────────────────────────────────────────────────────
fig = None
try:
    if chart_type == "Bar":
        grp = [x_col] + ([color_col] if color_col else [])
        plot_df = df.groupby(grp)[y_col].agg(agg).reset_index()
        fig = px.bar(plot_df, x=x_col, y=y_col, color=color_col,
                     title=f"{agg.title()} of {y_col} by {x_col}",
                     template="plotly_white", barmode="group")

    elif chart_type == "Line":
        grp = [x_col] + ([color_col] if color_col else [])
        plot_df = df.groupby(grp)[y_col].agg(agg).reset_index()
        fig = px.line(plot_df, x=x_col, y=y_col, color=color_col,
                      title=f"{y_col} over {x_col}", template="plotly_white", markers=True)

    elif chart_type == "Area":
        grp = [x_col] + ([color_col] if color_col else [])
        plot_df = df.groupby(grp)[y_col].agg(agg).reset_index()
        fig = px.area(plot_df, x=x_col, y=y_col, color=color_col,
                      title=f"{y_col} Area over {x_col}", template="plotly_white")

    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                         title=f"{y_col} vs {x_col}", template="plotly_white", opacity=0.7)

    elif chart_type == "Pie":
        plot_df = df.groupby(pie_names)[pie_vals].agg(agg).reset_index()
        fig = px.pie(plot_df, names=pie_names, values=pie_vals,
                     title=f"{pie_vals} by {pie_names}", hole=hole, template="plotly_white")

    elif chart_type == "Histogram":
        fig = px.histogram(df, x=hist_col, color=color_col, nbins=nbins,
                           title=f"Distribution of {hist_col}", template="plotly_white")

    elif chart_type == "Box Plot":
        fig = px.box(df, x=box_x, y=box_y, color=color_col,
                     title=f"Distribution of {box_y}", template="plotly_white", points="outliers")

    elif chart_type == "Heatmap":
        pivot = df.groupby([hm_y, hm_x])[hm_val].mean().reset_index().pivot(index=hm_y, columns=hm_x, values=hm_val)
        fig = px.imshow(pivot, title=f"Avg {hm_val} Heatmap",
                        color_continuous_scale="viridis", template="plotly_white", aspect="auto")

    if fig:
        fig.update_layout(height=520, font=dict(family="Inter, sans-serif", size=13),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Chart error: {e}. Try changing the axis selection.")

# ── KPI row ─────────────────────────────────────────────────────────────────
st.write("---")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Rows", f"{len(df):,}")
k2.metric("Columns", len(df.columns))
if numeric_cols:
    k3.metric(f"Avg {numeric_cols[0]}", f"${df[numeric_cols[0]].mean()/1e6:.1f}M")
    k4.metric(f"Total {numeric_cols[0]}", f"${df[numeric_cols[0]].sum()/1e9:.2f}B")

# ── Section 2: Advanced Drag-and-Drop ───────────────────────────────────────
st.write("---")
st.markdown('<div class="chart-header">🖱️ SECTION 2 — Advanced: Drag & Drop Explorer (PyGWalker)</div>', unsafe_allow_html=True)
st.caption("Drag fields from the **Field List** → **X-Axis** / **Y-Axis** boxes. Chart type icons are in the **second row of the toolbar** (the small icons after the undo/redo arrows).")

try:
    from pygwalker.api.streamlit import StreamlitRenderer

    @st.cache_resource
    def get_renderer():
        return StreamlitRenderer(df, kernel_computation=True)

    renderer = get_renderer()
    renderer.explorer(default_tab="vis")

except ImportError:
    st.info("PyGWalker not installed — install it for drag-and-drop mode.")
except Exception as e:
    st.error(f"PyGWalker error: {e}")
