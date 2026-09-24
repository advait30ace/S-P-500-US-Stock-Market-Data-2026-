# 📊 Financial Default Risk Analytics

A Python data analytics project that analyses historical stock market data to assess **financial default risk**, detect volatility patterns, and generate business decision signals.

---

## 🗂️ Project Structure

```
IBM2/
├── master_stock_data.csv          # Raw dataset
└── financial_default_risk/
    ├── app.py                     # Streamlit frontend (main entry point)
    └── utils/
        ├── __init__.py
        ├── data_loader.py         # Load, validate, clean, feature engineering
        ├── analytics.py           # Grouping, summaries, KPIs, insights
        └── visualizations.py     # Plotly chart factory functions
```

---

## 📁 Dataset

**File:** `master_stock_data.csv`  
**Source:** Historical stock price data (multi-ticker)

| Column        | Description                             |
|---------------|-----------------------------------------|
| `Date`        | Trading date                            |
| `Ticker`      | Stock ticker symbol                     |
| `Adj Close`   | Adjusted closing price                  |
| `Close`       | Raw closing price                       |
| `Dividends`   | Dividend paid on that date              |
| `High`        | Intraday high price                     |
| `Low`         | Intraday low price                      |
| `Open`        | Opening price                           |
| `Stock Splits`| Stock split factor                      |
| `Volume`      | Number of shares traded                 |

---

## ⚙️ Features

### 1. Data Loading & Validation
- Detects missing values, duplicate rows, negative prices, and High < Low inversions
- Generates a full validation report presented in the UI

### 2. Data Cleaning
- Drops rows with null critical fields
- Removes duplicates and negative/zero price rows
- Swaps High/Low where inverted
- Replaces ±Infinity with NaN and forward-fills

### 3. Feature Engineering (Risk Metrics)
| Feature              | Description                                       |
|----------------------|---------------------------------------------------|
| `Daily_Return`       | Day-over-day % price change                       |
| `Volatility_30d`     | 30-day rolling standard deviation of returns      |
| `Price_Range_Pct`    | Intraday (High−Low)/Low %                         |
| `Drawdown`           | Distance from 52-week rolling high                |
| `Volume_Spike`       | Volume vs 20-day rolling average                  |
| `RSI_14`             | 14-period Relative Strength Index                 |
| `Default_Risk_Score` | Composite 0–100 risk score (higher = more risk)   |
| `Risk_Category`      | Low / Medium / High / Critical                    |

### 4. Analytics & Grouping
- Per-ticker summary: totals, averages, counts
- Annual & monthly aggregations
- Top 10 risky and safest tickers
- Volatility bucket distribution
- Risk metric correlation matrix

### 5. Charts (14 interactive Plotly charts)
- Risk Score Histogram
- Risk Category Pie Chart
- Top Risky / Safe Ticker Bar Charts
- Annual Risk & Volatility Dual-Axis Line
- Annual Volume Bar
- Price & Volume History (per ticker)
- Risk Score Over Time (per ticker)
- Volatility vs Drawdown Scatter
- Volatility Bucket Bar
- RSI Distribution Histogram
- Correlation Heatmap
- Monthly Risk Trend
- Drawdown Over Time

### 6. Business Insights
- Automatic detection of critical/high-risk tickers
- Dividend vs non-dividend risk comparison
- Portfolio Decision Matrix (Buy/Hold/Reduce/Exit signals)

---

## 🚀 How to Run

### Prerequisites
```
Python 3.9+
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Launch the dashboard
```bash
# From the IBM2 directory (workspace root)
streamlit run financial_default_risk/app.py
```

The app will open at **http://localhost:8501** in your browser.

> **Note:** The dataset path defaults to `../master_stock_data.csv` relative to `app.py`. If you move the CSV, update the path in the sidebar text box at runtime.

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 Overview | KPI cards, risk distribution, full ticker summary table |
| 🧹 Data Quality | Validation report, cleaning steps, raw sample |
| 📈 Risk Dashboard | Scatter plots, volatility buckets, RSI, correlation heatmap |
| 🏆 Top Risky & Safe | Top 10 risky vs safest tickers with charts and tables |
| 📅 Time Series | Monthly/annual trend lines with year-range slider |
| 🔍 Ticker Deep Dive | Per-ticker price, risk, drawdown, raw data table |
| 💡 Business Insights | Actionable insights, decision matrix, risk-return scatter |

---

## 🧮 Default Risk Score Formula

```
Default Risk Score = (0.35 × Volatility Score)
                   + (0.30 × Drawdown Score)
                   + (0.20 × RSI Extremity Score)
                   + (0.15 × Price Range Score)
```
All components are normalised to [0, 1] before weighting. Final score is multiplied by 100.

| Score Range | Category |
|-------------|----------|
| 0 – 25      | Low      |
| 25 – 50     | Medium   |
| 50 – 75     | High     |
| 75 – 100    | Critical |

---

## 📋 Requirements

See [`requirements.txt`](requirements.txt)

---

## ⚠️ Disclaimer

This project is for educational and analytical purposes only. The default risk scores are statistical proxies derived from historical market data and should not be used as sole criteria for real investment decisions. Always consult a qualified financial advisor.
