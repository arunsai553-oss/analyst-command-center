import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_data, get_numeric_cols, get_categorical_cols, get_date_col, format_value

st.set_page_config(page_title="Executive Summary", page_icon="📝", layout="wide")
st.markdown("# 📝 Executive Summary")
st.markdown("Auto-generated narrative from your data — works with any dataset.")

df = get_data()
num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)
date_col = get_date_col(df)

if df.empty:
    st.warning("No data loaded.")
    st.stop()

st.write("---")
st.markdown("### 📋 Auto-Generated Narrative")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Dataset Facts")
    facts = [
        f"- **Total rows:** {len(df):,}",
        f"- **Total columns:** {len(df.columns)}",
        f"- **Numeric columns:** {', '.join(num_cols[:5])}{'...' if len(num_cols)>5 else ''}",
    ]
    if cat_cols:
        facts.append(f"- **Categorical columns:** {', '.join(cat_cols[:5])}{'...' if len(cat_cols)>5 else ''}")
    if date_col:
        try:
            df_dt = df.copy()
            df_dt[date_col] = pd.to_datetime(df_dt[date_col], errors='coerce')
            min_d = df_dt[date_col].min()
            max_d = df_dt[date_col].max()
            facts.append(f"- **Date range:** {min_d.strftime('%Y-%m-%d')} → {max_d.strftime('%Y-%m-%d')}")
        except:
            pass

    # Top/Bottom for each categorical × numeric pair
    if cat_cols and num_cols:
        grp_col = cat_cols[0]
        val_col = num_cols[0]
        try:
            grp_sum = df.groupby(grp_col)[val_col].sum()
            top = grp_sum.idxmax()
            bot = grp_sum.idxmin()
            facts.append(f"- **Top {grp_col}** by {val_col}: **{top}** ({format_value(grp_sum[top])})")
            facts.append(f"- **Lowest {grp_col}** by {val_col}: **{bot}** ({format_value(grp_sum[bot])})")
        except:
            pass

    # Period-over-period change
    if date_col and num_cols:
        try:
            df_dt = df.copy()
            df_dt[date_col] = pd.to_datetime(df_dt[date_col], errors='coerce')
            dates = sorted(df_dt[date_col].dropna().unique())
            if len(dates) >= 2:
                latest = df_dt[df_dt[date_col]==dates[-1]]
                prev   = df_dt[df_dt[date_col]==dates[-2]]
                for vc in num_cols[:3]:
                    c = latest[vc].sum()
                    p = prev[vc].sum()
                    if p != 0:
                        chg = (c - p) / abs(p) * 100
                        arrow = "▲" if chg > 0 else "▼"
                        facts.append(f"- **{vc.replace('_',' ').title()} MoM:** {arrow} {chg:+.1f}% (latest: {format_value(c)})")
        except:
            pass

    st.markdown("\n".join(facts))

with col2:
    st.markdown("#### Strategic Insights")
    insights = []
    if num_cols:
        for col in num_cols[:4]:
            mean_v = df[col].mean()
            std_v  = df[col].std()
            cv     = (std_v / mean_v * 100) if mean_v else 0
            insights.append(f"**{col.replace('_',' ').title()}**: avg {format_value(mean_v)}, "
                            f"std {format_value(std_v)}, CV {cv:.1f}%")
    if cat_cols:
        for cc in cat_cols[:3]:
            top_val = df[cc].value_counts().index[0]
            top_pct = df[cc].value_counts().iloc[0] / len(df) * 100
            insights.append(f"**{cc.replace('_',' ').title()}**: most common is **'{top_val}'** ({top_pct:.1f}% of rows)")

    st.info("\n\n".join(f"{i+1}. {ins}" for i, ins in enumerate(insights)) if insights else "Upload data to generate insights.")

st.write("---")
st.markdown("### Descriptive Statistics Table")
if num_cols:
    desc = df[num_cols].describe().T
    desc.index = [c.replace('_',' ').title() for c in desc.index]
    st.dataframe(desc.style.background_gradient(cmap='Blues', axis=1), use_container_width=True)

st.markdown("### Export")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Full Dataset (CSV)", csv, file_name='export.csv', mime='text/csv')
