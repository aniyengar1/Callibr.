import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="QuantMarkets", page_icon="📈", layout="wide")

st.title("📈 QuantMarkets")
st.subheader("Backtesting engine for prediction markets")
st.markdown("---")

# Load data
CSV_FILE = os.path.expanduser("~/Documents/quantmarkets/market_prices.csv")

@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    df = pd.read_csv(CSV_FILE)
    return df

df_raw = load_data()

if df_raw.empty:
    st.warning("No data collected yet. Run collector.py first.")
    st.stop()

# Sidebar controls
st.sidebar.title("Strategy Settings")
min_prob = st.sidebar.slider("Minimum opening probability", 0.0, 1.0, 0.05, 0.05)
max_prob = st.sidebar.slider("Maximum opening probability", 0.0, 1.0, 0.95, 0.05)

source_options = ["All"] + sorted(df_raw["source"].unique().tolist())
source_filter = st.sidebar.selectbox("Data source", source_options)

# Show raw data stats in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Pipeline")
st.sidebar.metric("Total snapshots", len(df_raw))
st.sidebar.metric("Unique markets", df_raw["ticker"].nunique())
st.sidebar.metric("Sources", df_raw["source"].nunique())
if "timestamp" in df_raw.columns:
    st.sidebar.metric("Latest snapshot", df_raw["timestamp"].max()[:16])

# Apply filters
df = df_raw.copy()
df = df[(df["mid_price"] >= min_prob) & (df["mid_price"] <= max_prob)]
if source_filter != "All":
    df = df[df["source"] == source_filter]

# Get first snapshot per market as opening price
df_open = df.sort_values("timestamp").groupby("ticker").first().reset_index()

# Simulate backtest — we don't have resolution yet so show current distribution
st.markdown("## 📊 Market Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Markets tracked", df_raw["ticker"].nunique())
col2.metric("Active snapshots", len(df))
col3.metric("Avg opening price", f"{df_open['mid_price'].mean():.2%}")
col4.metric("Price range", f"{df_open['mid_price'].min():.2%} - {df_open['mid_price'].max():.2%}")

st.markdown("---")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Market Distribution by Opening Price")
    df_open['prob_bucket'] = pd.cut(df_open['mid_price'],
                                     bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                     labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'])
    bucket_counts = df_open.groupby("prob_bucket").size()
    fig, ax = plt.subplots()
    ax.bar(bucket_counts.index, bucket_counts.values, color="#6C47FF")
    ax.set_xlabel("Opening Probability")
    ax.set_ylabel("Number of Markets")
    st.pyplot(fig)

with col_right:
    st.subheader("Price Distribution")
    fig2, ax2 = plt.subplots()
    ax2.hist(df_open["mid_price"], bins=20, color="#00C2A8", edgecolor="white")
    ax2.set_xlabel("Opening Price")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)

st.markdown("---")

# Market browser
st.subheader("📋 Market Browser")
st.dataframe(
    df_open[["source", "ticker", "event_ticker", "mid_price", "open_time", "close_time"]]
    .sort_values("mid_price")
    .reset_index(drop=True),
    use_container_width=True
)
