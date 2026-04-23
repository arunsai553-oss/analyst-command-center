import streamlit as st
import pandas as pd
import sys
import os
import streamlit.components.v1 as components

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_data

st.set_page_config(page_title="Tableau Data Studio", page_icon="🧮", layout="wide")

st.markdown("# 🧮 Power BI / Tableau Drag-&-Drop Studio")
st.markdown("Build custom visuals and dashboards instantly by dragging and dropping columns onto the axis, **exactly like Tableau**.")
st.write("---")

df = get_data()

try:
    from pygwalker.api.streamlit import StreamlitRenderer
    
    # Initialize pygwalker renderer
    @st.cache_resource
    def get_pyg_renderer(data):
        return StreamlitRenderer(data, spec="./gw_config.json", spec_io_mode="rw")
        
    renderer = get_pyg_renderer(df)
    
    # Render the Tableau interface
    st.markdown("### 🖱️ Drag dimensions to X/Y axes to build your own charts:")
    renderer.explorer()
    
except ImportError:
    st.error("PyGWalker is not installed. Please add `pygwalker` to your requirements.txt.")

