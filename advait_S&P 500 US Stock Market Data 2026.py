"""
app.py
------
Streamlit frontend for Financial Default Risk Analytics Dashboard.

Run with:
    streamlit run financial_default_risk/app.py
"""

import os
import sys
import pathlib

# ── Ensure utils package is importable from any working directory ──────────
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import numpy as np

from utils.data_loader import load_and_prepare
from utils.analytics import (
    ticker_summary,
    risk_distribution,
    annual_summary,
    monthly_summary,
    top_risky_tickers,
    top_safe_tickers,
    volatility_buckets,
    risk_correlation,
    generate_business_insights,
    dataset_overview,
)
from utils.visualizations import (
    fig_risk_score_histogram,
    fig_risk_category_pie,
    fig_top_risky_bar,
    fig_top_safe_bar,
    fig_annual_risk_volatility,
    fig_annual_volume,
    fig_price_history,
    fig_risk_over_time,
    fig_volatility_vs_drawdown,
    fig_volatility_buckets,
    fig_rsi_distribution,
    fig_correlation_heatmap,
    fig_monthly_risk_trend,
    fig_drawdown_over_time,
)

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Default Risk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-card h3 { margin: 0 0 4px 0; font-size: 0.82rem; color: #64748b; }
    .metric-card p  { margin: 0; font-size: 1.5rem; font-weight: 700; color: #1e293b; }
    .insight-card {
        border-left: 5px solid #3b82f6;
        background: #f0f9ff;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
    }
    .insight-card.critical { border-left-color: #7c3aed; background: #f5f3ff; }
    .insight-card.high     { border-left-color: #ef4444; background: #fff1f2; }
    .insight-card.medium   { border-left-color: #f59e0b; background: #fffbeb; }
    .insight-card.low      { border-left-color: #22c55e; background: #f0fdf4; }
    .insight-card.opportunity { border-left-color: #06b6d4; background: #ecfeff; }
    .section-header {
        font-size: 1.25rem; font-weight: 700;
        color: #1e293b; margin: 1.5rem 0 0.75rem 0;
        border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3rem;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading (cached) ───────────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Loading and processing dataset…")
def get_data(path: str):
    return load_and_prepare(path)


@st.cache_data(show_spinner="⏳ Computing analytics…")
def get_analytics(df_json: str):
    df = pd.read_json(df_json, orient="split")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Risk_Category"] = pd.Categorical(
        df["Risk_Category"], categories=["Low", "Medium", "High", "Critical"], ordered=True
    )
    summary = ticker_summary(df)
    risk_dist = risk_distribution(df)
    annual = annual_summary(df)
    vol_bkt = volatility_buckets(summary)
    corr = risk_correlation(summary)
    top_risky = top_risky_tickers(summary)
    top_safe = top_safe_tickers(summary)
    insights = generate_business_insights(df, summary)
    return summary, risk_dist, annual, vol_bkt, corr, top_risky, top_safe, insights


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.title("📊 Financial Default Risk")
    st.markdown("---")

    # Dataset path
    default_path = str(ROOT.parent / "master_stock_data.csv")
    data_path = st.text_input("📁 Dataset Path", value=default_path)

    if not os.path.exists(data_path):
        st.error("Dataset not found. Check the path above.")
        st.stop()

    st.success("✅ Dataset found")
    st.markdown("---")

    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Overview",
         "🧹 Data Quality",
         "📈 Risk Dashboard",
         "🏆 Top Risky & Safe",
         "📅 Time Series",
         "🔍 Ticker Deep Dive",
         "💡 Business Insights"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#94a3b8'>Financial Default Risk Analytics<br/>Built with Streamlit & Plotly</small>",
        unsafe_allow_html=True,
    )


# ── Load data ────────────────────────────────────────────────────────────────
df, validation_report = get_data(data_path)

# Cache analytics using JSON round-trip (hashable)
df_json = df.assign(Risk_Category=df["Risk_Category"].astype(str)).to_json(orient="split", date_format="iso")
summary, risk_dist, annual, vol_bkt, corr, top_risky, top_safe, insights = get_analytics(df_json)

overview_stats = dataset_overview(df, validation_report)
tickers_list = sorted(df["Ticker"].unique().tolist())


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════ #
if page == "🏠 Overview":
    st.title("📊 Financial Default Risk Analytics Dashboard")
    st.markdown(
        "> Analyse historical stock market data to identify default risk, "
        "volatility patterns, and investment decision signals across multiple securities."
    )
    st.markdown("---")

    # KPI row
    cols = st.columns(4)
    kpi_items = list(overview_stats.items())
    for i, (label, val) in enumerate(kpi_items[:4]):
        with cols[i % 4]:
            st.metric(label=label, value=val)

    cols2 = st.columns(4)
    for i, (label, val) in enumerate(kpi_items[4:8]):
        with cols2[i % 4]:
            st.metric(label=label, value=val)

    st.markdown("---")
    st.markdown('<div class="section-header">Risk Score Distribution</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(fig_risk_score_histogram(df), use_container_width=True)
    with c2:
        st.plotly_chart(fig_risk_category_pie(risk_dist), use_container_width=True)

    st.markdown('<div class="section-header">Risk Category Summary Table</div>', unsafe_allow_html=True)
    rc_display = risk_dist.copy()
    rc_display["Percentage"] = rc_display["Percentage"].map(lambda x: f"{x:.2f}%")
    rc_display["Count"] = rc_display["Count"].map(lambda x: f"{x:,}")
    st.dataframe(rc_display, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">Per-Ticker Summary (first 50 tickers)</div>', unsafe_allow_html=True)
    display_cols = ["Ticker", "Trading_Days", "Avg_Close", "Avg_Daily_Return_Pct",
                    "Volatility_30d_Avg", "Avg_Drawdown_Pct", "Worst_Drawdown_Pct",
                    "Avg_Risk_Score", "Dominant_Risk_Category"]
    st.dataframe(
        summary[display_cols].head(50).style.format({
            "Avg_Close":            "${:.2f}",
            "Avg_Daily_Return_Pct": "{:.4f}%",
            "Volatility_30d_Avg":   "{:.4f}%",
            "Avg_Drawdown_Pct":     "{:.2f}%",
            "Worst_Drawdown_Pct":   "{:.2f}%",
            "Avg_Risk_Score":       "{:.2f}",
        }).background_gradient(subset=["Avg_Risk_Score"], cmap="RdYlGn_r"),
        use_container_width=True,
        hide_index=True,
    )


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: DATA QUALITY
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "🧹 Data Quality":
    st.title("🧹 Data Quality Report")
    st.markdown("Assessment of the raw dataset before and after cleaning.")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Missing Columns", len(validation_report.get("missing_columns", [])),
              delta="issues found" if validation_report.get("missing_columns") else "none")
    c2.metric("Duplicate Rows", validation_report.get("duplicate_rows", 0))
    c3.metric("Negative Price Rows", validation_report.get("negative_price_rows", 0))

    c4, c5, c6 = st.columns(3)
    c4.metric("High < Low Rows", validation_report.get("high_lt_low_rows", 0))
    c5.metric("Zero/Neg Volume Rows", validation_report.get("zero_or_neg_volume", 0))
    c6.metric("Columns with NULLs", len(validation_report.get("null_counts", {})))

    st.markdown("---")

    if validation_report.get("null_counts"):
        st.markdown('<div class="section-header">Missing Values per Column</div>', unsafe_allow_html=True)
        null_df = pd.DataFrame.from_dict(
            validation_report["null_counts"], orient="index", columns=["Null Count"]
        ).reset_index().rename(columns={"index": "Column"})
        st.dataframe(null_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No missing values detected in required columns.")

    if validation_report.get("inf_value_counts"):
        st.warning("⚠️ Infinite values found and replaced with NaN during cleaning.")
        st.json(validation_report["inf_value_counts"])
    else:
        st.success("✅ No infinite values detected.")

    st.markdown("---")
    st.markdown('<div class="section-header">Cleaning Steps Applied</div>', unsafe_allow_html=True)
    steps = [
        ("✅", "Parse `Date` column as datetime"),
        ("✅", "Drop rows with missing Date, Ticker, Close, High, Low, Open, Volume"),
        ("✅", "Remove exact duplicate rows"),
        ("✅", "Remove rows where Close ≤ 0 or Volume ≤ 0"),
        ("✅", "Swap High/Low where High < Low"),
        ("✅", "Replace ±Inf with NaN, then forward-fill / back-fill"),
        ("✅", "Sort by Ticker → Date"),
    ]
    for icon, desc in steps:
        st.markdown(f"{icon} {desc}")

    st.markdown("---")
    st.markdown('<div class="section-header">Cleaned Dataset Sample</div>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: RISK DASHBOARD
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "📈 Risk Dashboard":
    st.title("📈 Risk Analytics Dashboard")
    st.markdown("Aggregate risk, volatility, and market metrics across all tickers and time.")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_volatility_vs_drawdown(summary), use_container_width=True)
    with c2:
        st.plotly_chart(fig_volatility_buckets(vol_bkt), use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_rsi_distribution(df), use_container_width=True)
    with c4:
        st.plotly_chart(fig_correlation_heatmap(corr), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Annual Risk & Volatility Trends</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_annual_risk_volatility(annual), use_container_width=True)

    st.markdown('<div class="section-header">Annual Total Trading Volume</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_annual_volume(annual), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Annual Summary Table</div>', unsafe_allow_html=True)
    annual_display = annual.copy()
    annual_display["Avg_Close"]       = annual_display["Avg_Close"].map("${:.2f}".format)
    annual_display["Avg_Volatility"]  = (annual_display["Avg_Volatility"] * 100).map("{:.4f}%".format)
    annual_display["Avg_Daily_Return"]= (annual_display["Avg_Daily_Return"] * 100).map("{:.4f}%".format)
    annual_display["Avg_Risk_Score"]  = annual_display["Avg_Risk_Score"].map("{:.2f}".format)
    annual_display["Total_Volume"]    = annual_display["Total_Volume"].map("{:,.0f}".format)
    st.dataframe(annual_display, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: TOP RISKY & SAFE
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "🏆 Top Risky & Safe":
    st.title("🏆 Top Risky & Safest Tickers")
    st.markdown("Identify the most and least risky securities based on the composite Default Risk Score.")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">🔴 Top 10 Most Risky Tickers</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_top_risky_bar(top_risky), use_container_width=True)
        st.dataframe(
            top_risky.style.format({
                "Avg_Risk_Score":     "{:.2f}",
                "Max_Risk_Score":     "{:.2f}",
                "Volatility_30d_Avg": "{:.4f}%",
                "Avg_Drawdown_Pct":   "{:.2f}%",
                "Worst_Drawdown_Pct": "{:.2f}%",
            }).background_gradient(subset=["Avg_Risk_Score"], cmap="Reds"),
            use_container_width=True,
            hide_index=True,
        )

    with c2:
        st.markdown('<div class="section-header">🟢 Top 10 Safest Tickers</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_top_safe_bar(top_safe), use_container_width=True)
        st.dataframe(
            top_safe.style.format({
                "Avg_Risk_Score":     "{:.2f}",
                "Max_Risk_Score":     "{:.2f}",
                "Volatility_30d_Avg": "{:.4f}%",
                "Avg_Drawdown_Pct":   "{:.2f}%",
                "Worst_Drawdown_Pct": "{:.2f}%",
            }).background_gradient(subset=["Avg_Risk_Score"], cmap="Greens_r"),
            use_container_width=True,
            hide_index=True,
        )


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: TIME SERIES
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "📅 Time Series":
    st.title("📅 Time Series Analysis")
    st.markdown("Explore monthly and annual trends in risk, volatility, and returns.")
    st.markdown("---")

    year_min = int(df["Date"].dt.year.min())
    year_max = int(df["Date"].dt.year.max())

    col_a, col_b = st.columns([2, 1])
    with col_a:
        year_range = st.slider(
            "Filter Year Range",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
        )
    with col_b:
        ts_ticker = st.selectbox(
            "Ticker (optional monthly filter)",
            ["All Tickers"] + tickers_list,
            index=0,
        )

    df_ts = df[(df["Date"].dt.year >= year_range[0]) & (df["Date"].dt.year <= year_range[1])]

    monthly = monthly_summary(
        df_ts,
        ticker=(None if ts_ticker == "All Tickers" else ts_ticker)
    )
    annual_ts = annual_summary(df_ts)

    # Monthly risk trend
    fig_m = fig_monthly_risk_trend(monthly, ticker=ts_ticker)
    st.plotly_chart(fig_m, use_container_width=True)

    # Annual
    st.plotly_chart(fig_annual_risk_volatility(annual_ts), use_container_width=True)
    st.plotly_chart(fig_annual_volume(annual_ts), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Monthly Summary Table</div>', unsafe_allow_html=True)
    m_display = monthly.copy()
    m_display["Avg_Close"]       = m_display["Avg_Close"].map("${:.2f}".format)
    m_display["Total_Volume"]    = m_display["Total_Volume"].map("{:,.0f}".format)
    m_display["Avg_Risk_Score"]  = m_display["Avg_Risk_Score"].map("{:.2f}".format)
    m_display["Avg_Daily_Return"]= (m_display["Avg_Daily_Return"] * 100).map("{:.4f}%".format)
    st.dataframe(m_display, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: TICKER DEEP DIVE
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "🔍 Ticker Deep Dive":
    st.title("🔍 Ticker Deep Dive")
    st.markdown("Examine price history, risk score evolution, drawdown, and key stats for any ticker.")
    st.markdown("---")

    sel_ticker = st.selectbox("Select Ticker", tickers_list)

    ticker_data = df[df["Ticker"] == sel_ticker]
    ticker_stats = summary[summary["Ticker"] == sel_ticker].iloc[0]

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Avg Close",        f"${ticker_stats['Avg_Close']:.2f}")
    k2.metric("Avg Risk Score",   f"{ticker_stats['Avg_Risk_Score']:.1f}")
    k3.metric("Avg Volatility",   f"{ticker_stats['Volatility_30d_Avg']:.4f}%")
    k4.metric("Worst Drawdown",   f"{ticker_stats['Worst_Drawdown_Pct']:.2f}%")
    k5.metric("Dominant Risk Cat",str(ticker_stats["Dominant_Risk_Category"]))

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_price_history(df, sel_ticker), use_container_width=True)
    with c2:
        st.plotly_chart(fig_risk_over_time(df, sel_ticker), use_container_width=True)

    st.plotly_chart(fig_drawdown_over_time(df, sel_ticker), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Raw Daily Data</div>', unsafe_allow_html=True)
    display_raw_cols = ["Date", "Open", "High", "Low", "Close", "Adj Close",
                        "Volume", "Daily_Return", "Volatility_30d",
                        "RSI_14", "Drawdown", "Default_Risk_Score", "Risk_Category"]
    st.dataframe(
        ticker_data[display_raw_cols].sort_values("Date", ascending=False)
        .style.format({
            "Open":              "${:.2f}",
            "High":              "${:.2f}",
            "Low":               "${:.2f}",
            "Close":             "${:.2f}",
            "Adj Close":         "${:.2f}",
            "Volume":            "{:,.0f}",
            "Daily_Return":      "{:.4f}",
            "Volatility_30d":    "{:.6f}",
            "RSI_14":            "{:.2f}",
            "Drawdown":          "{:.4f}",
            "Default_Risk_Score":"{:.2f}",
        }).background_gradient(subset=["Default_Risk_Score"], cmap="RdYlGn_r"),
        use_container_width=True,
        hide_index=True,
    )


# ════════════════════════════════════════════════════════════════════════════ #
# PAGE: BUSINESS INSIGHTS
# ════════════════════════════════════════════════════════════════════════════ #
elif page == "💡 Business Insights":
    st.title("💡 Business Decision Insights")
    st.markdown(
        "Data-driven findings and actionable recommendations derived from the "
        "Financial Default Risk analysis."
    )
    st.markdown("---")

    severity_map = {
        "Critical":    "critical",
        "High":        "high",
        "Medium":      "medium",
        "Low":         "low",
        "Opportunity": "opportunity",
    }

    for insight in insights:
        sev = insight.get("severity", "medium")
        css_class = severity_map.get(sev, "medium")
        st.markdown(
            f"""<div class="insight-card {css_class}">
            <strong>{insight['title']}</strong><br/>
            <span style="color:#374151">{insight['finding']}</span><br/>
            <span style="color:#6b7280; font-style:italic">💼 {insight['recommendation']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown('<div class="section-header">Risk Score vs Average Daily Return</div>', unsafe_allow_html=True)
    import plotly.express as px
    fig_scatter = px.scatter(
        summary,
        x="Avg_Daily_Return_Pct",
        y="Avg_Risk_Score",
        color="Dominant_Risk_Category",
        color_discrete_map={
            "Low": "#22c55e", "Medium": "#f59e0b",
            "High": "#ef4444", "Critical": "#7c3aed"
        },
        hover_name="Ticker",
        size="Total_Volume",
        size_max=18,
        title="Risk Score vs Avg Daily Return – All Tickers",
        labels={
            "Avg_Daily_Return_Pct": "Avg Daily Return (%)",
            "Avg_Risk_Score":       "Avg Default Risk Score",
        },
    )
    fig_scatter.update_layout(template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-header">Dividend-Paying vs Non-Dividend Stocks</div>', unsafe_allow_html=True)
    summary_div = summary.copy()
    summary_div["Pays_Dividend"] = summary_div["Total_Dividends"] > 0
    div_risk = (
        summary_div.groupby("Pays_Dividend")["Avg_Risk_Score"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Avg_Risk_Score", "count": "Count"})
    )
    div_risk["Pays_Dividend"] = div_risk["Pays_Dividend"].map({True: "Pays Dividends", False: "No Dividends"})
    fig_div = px.bar(
        div_risk,
        x="Pays_Dividend",
        y="Avg_Risk_Score",
        color="Pays_Dividend",
        text="Count",
        title="Average Default Risk: Dividend vs Non-Dividend Stocks",
        color_discrete_sequence=["#22c55e", "#ef4444"],
        labels={"Avg_Risk_Score": "Avg Default Risk Score"},
    )
    fig_div.update_traces(texttemplate="n=%{text}", textposition="outside")
    fig_div.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig_div, use_container_width=True)

    # Summary recommendation table
    st.markdown('<div class="section-header">Portfolio Decision Matrix</div>', unsafe_allow_html=True)
    decision_data = {
        "Risk Category": ["Low (0–25)", "Medium (25–50)", "High (50–75)", "Critical (75–100)"],
        "Signal":        ["✅ Buy / Hold", "⚠️ Monitor", "🔶 Reduce Position", "🔴 Exit / Avoid"],
        "Action":        [
            "Overweight in defensive portfolios; suitable for income investors",
            "Maintain current exposure; set trailing stop-loss at 10%",
            "Trim by 30–50%; review fundamentals; hedge with inverse ETF",
            "Exit immediately; do not average down; quarantine from new capital",
        ],
        "Review Frequency": ["Quarterly", "Monthly", "Weekly", "Daily"],
    }
    st.dataframe(pd.DataFrame(decision_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.info(
        "📌 **Disclaimer:** This analysis is derived from historical market data only. "
        "Risk scores are statistical proxies and should not be used as sole criteria "
        "for investment decisions. Always consult a qualified financial advisor."
    )
