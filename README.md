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

## 📊 Project Methodology

This project follows a "Full-Stack Analyst" workflow:
1. **Data Ingestion**: Synthetic SaaS data generated via `utils.py` mimicking real-world distributions.
2. **Feature Engineering**: Dynamic calculation of LTV, CAC, ROIC, and P/E ratios.
3. **Statistical Evaluation**: A/B testing module utilizing SciPy for T-tests and P-value significance.
4. **Predictive Modeling**: EWMA-based forecasting for revenue and margin scenario testing.

## 🌟 Strategic Impact

Instead of just building charts, this platform provides:
- **Decision Support**: High-risk companies are flagged automatically based on leverage and margin compression.
- **Hypothesis Testing**: Direct link between product changes and conversion lift.
- **Investor Ready View**: Professional valuation multiples (P/S, P/E) for portfolio-wide benchmarking.

## 🚀 Deployment

The live application is hosted on **Streamlit Community Cloud**, connected directly to this repository.

*(Note to Recruiters: The following visual mocks represent the integrated dashboard state)*

| Scanner Dashboard | Risk Radar |
| :---: | :---: |
| Time-series & Sector filtering | Leverage vs. Profitability analysis |

---
*Created by Arun Sai Thota as a demonstration of Financial Analytics & Data Engineering.*
