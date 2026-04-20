# Analyst Command Center

A professional, multi-page data analytics portfolio project built with **Streamlit**. 
This application demonstrates full-stack capabilities in data ingestion, exploratory data analysis (EDA), statistical evaluation, financial modeling, and predictive forecasting.

## 🌟 Features Tour

- **Market & Company Scanner**: Time-series analysis, global sector filtering, and macro benchmarking.
- **Deep Dive Lab**: Dynamic pivot tables, aggregations, and interactive correlation matrices.
- **Forecast & Scenarios**: Baseline revenue predictions (EWMA) with interactive what-if parameters for margins and growth.
- **Experiments & KPIs**: Statistical significance evaluation (t-tests) for A/B product testing.
- **Executive Summary**: Automated bullet-point narratives and synthesized strategic recommendations.

## 🚀 How to Run Locally

1. **Clone the repository.**
2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Command Center:**
   ```bash
   streamlit run app.py
   ```

## 🔌 Using Your Own Data

This application currently utilizes an advanced synthetic data generator (`utils.py`) to mimic realistic SaaS and B2B corporate metrics.

To swap this out for your real dataset:
1. Navigate to `utils.py`.
2. Locate the `load_and_generate_data()` function.
3. Update the `pd.read_csv("data/raw/financials.csv")` file path to point to your actual CSV.
4. Ensure your CSV contains standard columns (e.g., `date`, `company`, `sector`, `revenue`, `gross_profit`, `marketing_spend`, etc.).
5. Drop your real CSV files directly into the `data/raw/` directory.

## 🌐 Deploying to Streamlit Community Cloud

1. Commit and push this entire repository to your GitHub account.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app**.
4. Connect your GitHub repository, specify the branch, and set the **Main file path** to `app.py`.
5. Click **Deploy!**

## 📸 Screenshots

*(Replace these placeholders with real screenshots once deployed)*

![Dashboard View](https://via.placeholder.com/800x400?text=Scanner+Dashboard)
![EDA Features](https://via.placeholder.com/800x400?text=Deep+Dive+EDA)
