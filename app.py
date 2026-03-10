import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from supabase import create_client

st.set_page_config(page_title="QuantMarkets", page_icon="📈", layout="wide")

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #1C1C1E; }

[data-testid="stSidebar"] {
    background-color: #161618;
    border-right: 1px solid #2A2A2C;
}
[data-testid="stSidebar"] * { color: #E0E0E0 !important; }
[data-testid="stSidebar"] .stMetric {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: 1px solid #1E1E1E;
    gap: 0; padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #555555;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 12px 24px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #FFFFFF; }
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #FFFFFF !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 32px; }

[data-testid="stMetric"] {
    background: #111111;
    border: 1px solid #1E1E1E;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s ease;
}
[data-testid="stMetric"]:hover { border-color: #333333; }
[data-testid="stMetricLabel"] {
    color: #555555 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}
h2 { border-bottom: 1px solid #1A1A1A; padding-bottom: 12px; }

.stButton > button {
    background-color: #FFFFFF;
    color: #000000;
    border: none;
    border-radius: 6px;
    padding: 10px 28px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: #E8E8E8;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(255,255,255,0.08);
}

.stSelectbox > div > div,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background-color: #111111 !important;
    border: 1px solid #222222 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-size: 13px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1A1A1A;
    border-radius: 10px;
    overflow: hidden;
}

.stInfo {
    background-color: #111111 !important;
    border: 1px solid #222222 !important;
    border-left: 3px solid #FFFFFF !important;
    border-radius: 8px !important;
}
.stWarning { border-left: 3px solid #F59E0B !important; }
.stError   { border-left: 3px solid #DC2626 !important; }

.stRadio > div > label {
    background: #111111;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 8px 16px;
    color: #AAAAAA !important;
    font-size: 12px;
    transition: all 0.15s ease;
}
.stRadio > div > label:hover {
    border-color: #444444;
    color: #FFFFFF !important;
}

hr { border: none; border-top: 1px solid #1A1A1A; margin: 28px 0; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0A0A0A; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }

table { width: 100%; border-collapse: collapse; font-size: 13px; }
table th {
    background: #111111; color: #555555;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 12px 16px; border-bottom: 1px solid #1E1E1E; text-align: left;
}
table td { padding: 12px 16px; border-bottom: 1px solid #151515; color: #CCCCCC; }
table tr:hover td { background: #111111; }
table a {
    color: #FFFFFF; text-decoration: none; font-weight: 600;
    border-bottom: 1px solid #333333; padding-bottom: 1px;
    transition: border-color 0.15s ease;
}
table a:hover { border-bottom-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# ── page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:40px 0 28px 0; border-bottom:1px solid #1A1A1A; margin-bottom:32px;">
    <div style="font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#444444;margin-bottom:10px;">PREDICTION MARKETS</div>
    <div style="font-size:38px;font-weight:700;color:#FFFFFF;letter-spacing:-0.03em;line-height:1;">QuantMarkets</div>
    <div style="font-size:14px;color:#444444;margin-top:10px;font-weight:400;letter-spacing:0.01em;">Backtest strategies · Find edges · Place smarter bets</div>
</div>
""", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
SUPABASE_URL      = st.secrets["SUPABASE_URL"]
SUPABASE_KEY      = st.secrets["SUPABASE_KEY"]
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SOURCE_COLORS = {
    "polymarket":        "#8B5CF6",
    "kalshi":            "#3B82F6",
    "kalshi_historical": "#6B7280",
}
SOURCE_LABELS = {
    "polymarket":        "🟣 Polymarket",
    "kalshi":            "🔵 Kalshi (live)",
    "kalshi_historical": "📚 Kalshi (resolved)",
}

# Shared Plotly layout defaults
PLOT_LAYOUT = dict(
    paper_bgcolor="#1C1C1E",
    plot_bgcolor="#1C1C1E",
    font=dict(family="Inter", color="#888888", size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor="#1A1A1A", linecolor="#222222", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1A1A1A", linecolor="#222222", tickfont=dict(size=10)),
    hoverlabel=dict(
        bgcolor="#1A1A1A",
        bordercolor="#333333",
        font=dict(family="Inter", size=12, color="#FFFFFF"),
    ),
)

def apply_layout(fig, title="", height=300):
    fig.update_layout(**PLOT_LAYOUT, title=dict(text=title, font=dict(size=12, color="#666666")), height=height)
    return fig

# ── helpers ───────────────────────────────────────────────────────────────────
def categorize(question):
    q = question.lower()
    if any(x in q for x in ["trump","president","election","congress","senate","biden",
                              "republican","democrat","ukraine","russia","china","taiwan",
                              "ceasefire","tariff","fed","federal reserve","interest rate","inflation","gdp"]):
        return "Politics & Macro"
    elif any(x in q for x in ["nhl","nba","nfl","mlb","fifa","world cup","stanley cup",
                                "super bowl","championship","soccer","football","basketball",
                                "baseball","hockey","tennis","golf"]):
        return "Sports"
    elif any(x in q for x in ["bitcoin","btc","eth","crypto","ethereum","solana","coinbase","binance"]):
        return "Crypto"
    elif any(x in q for x in ["openai","gpt","anthropic","google","apple","microsoft","nvidia","stock","ipo","earnings"]):
        return "Tech & Markets"
    elif any(x in q for x in ["album","movie","gta","taylor swift","rihanna","oscar","grammy",
                                "celebrity","convicted","sentenced","trial","weinstein"]):
        return "Entertainment & Legal"
    else:
        return "Other"

@st.cache_data(ttl=300)
def load_data():
    all_rows, offset, batch_size = [], 0, 1000
    while True:
        batch = supabase.table("market_prices").select("*")\
            .order("timestamp", desc=False)\
            .range(offset, offset + batch_size - 1).execute().data
        if not batch: break
        all_rows.extend(batch)
        if len(batch) < batch_size: break
        offset += batch_size
    if not all_rows: return pd.DataFrame()
    df = pd.DataFrame(all_rows)
    df["mid_price"] = pd.to_numeric(df["mid_price"], errors="coerce")
    df["category"]  = df["event_ticker"].apply(categorize)
    return df

def build_markets_df(df):
    df_first  = df.sort_values("timestamp").groupby("ticker").first().reset_index()
    df_latest = df.sort_values("timestamp").groupby("ticker").last().reset_index()
    df_latest = df_latest.rename(columns={"mid_price": "current_price"})
    df_m = df_first.merge(df_latest[["ticker","current_price"]], on="ticker")
    df_m["price_change"]     = (df_m["current_price"] - df_m["mid_price"]).round(4)
    df_m["price_change_pct"] = ((df_m["price_change"] / df_m["mid_price"]) * 100).round(2)
    df_m["days_to_close"]    = (
        pd.to_datetime(df_m["close_time"], errors="coerce").dt.tz_localize(None) - pd.Timestamp.now()
    ).dt.days
    return df_m

def parse_strategy_with_claude(user_input):
    system = """You are a trading strategy parser for a prediction markets backtesting platform.
Convert the user's plain-English strategy into structured rules.
Return ONLY a valid JSON object with exactly these fields:
{
  "condition": "less than" | "greater than" | "between",
  "threshold_1": <float 0.05–0.95>,
  "threshold_2": <float 0.05–0.95 or null>,
  "category": "All" | "Politics & Macro" | "Sports" | "Crypto" | "Tech & Markets" | "Entertainment & Legal" | "Other",
  "source": "all" | "polymarket" | "kalshi",
  "explanation": "<one sentence plain English summary of the rule>"
}
Return ONLY the JSON, no markdown, no extra text."""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 500, "system": system,
                  "messages": [{"role": "user", "content": user_input}]},
            timeout=15
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"].strip().replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

# ── load + split data ─────────────────────────────────────────────────────────
df_raw = load_data()
if df_raw.empty:
    st.warning("No data yet."); st.stop()

df_poly_raw   = df_raw[df_raw["source"] == "polymarket"]
df_kalshi_raw = df_raw[df_raw["source"] == "kalshi"]
df_hist_raw   = df_raw[df_raw["source"] == "kalshi_historical"]
df_live_raw   = df_raw[df_raw["source"].isin(["polymarket","kalshi"])]

df_poly_markets   = build_markets_df(df_poly_raw)   if not df_poly_raw.empty   else pd.DataFrame()
df_kalshi_markets = build_markets_df(df_kalshi_raw)  if not df_kalshi_raw.empty  else pd.DataFrame()
df_hist_markets   = build_markets_df(df_hist_raw)   if not df_hist_raw.empty   else pd.DataFrame()
df_markets        = build_markets_df(df_live_raw)

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## QuantMarkets")
st.sidebar.markdown("<div style='font-size:11px;color:#444;margin-bottom:16px;'>Prediction market intelligence</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Pipeline")
st.sidebar.metric("Total snapshots", f"{len(df_raw):,}")
st.sidebar.metric("Last updated",    df_raw["timestamp"].max()[:16])
st.sidebar.markdown("**Sources**")
for src in ["polymarket","kalshi","kalshi_historical"]:
    n = df_raw[df_raw["source"] == src]["ticker"].nunique()
    st.sidebar.markdown(f"{SOURCE_LABELS[src]}: **{n:,}** markets")

# ── tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "🔀 Sources", "📚 Resolved",
    "🤖 AI Strategy", "🔬 Backtester", "💰 Recommender"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("## Market Overview")

    f1, f2, f3, f4 = st.columns(4)
    with f1: min_prob = st.slider("Min probability", 0.0, 1.0, 0.05, 0.05, key="ov_min")
    with f2: max_prob = st.slider("Max probability", 0.0, 1.0, 0.95, 0.05, key="ov_max")
    with f3: category_filter = st.selectbox("Category", ["All"]+sorted(df_markets["category"].unique().tolist()), key="ov_cat")
    with f4: sort_by = st.selectbox("Sort by", ["Opening Price","Current Price","Price Change","Days to Close"], key="ov_sort")

    df = df_markets.copy()
    df = df[(df["mid_price"] >= min_prob) & (df["mid_price"] <= max_prob)]
    if category_filter != "All": df = df[df["category"] == category_filter]
    sort_map = {"Opening Price":"mid_price","Current Price":"current_price","Price Change":"price_change","Days to Close":"days_to_close"}
    df = df.sort_values(sort_map[sort_by], ascending=False).reset_index(drop=True)

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Markets tracked",   f"{len(df):,}")
    c2.metric("Avg opening price", f"{df['mid_price'].mean():.2%}")
    c3.metric("Biggest mover",     f"{df['price_change_pct'].abs().max():.1f}%")
    c4.metric("Categories",        df["category"].nunique())
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Avg current price",   f"{df['current_price'].mean():.2%}")
    c6.metric("Markets moving up",   f"{len(df[df['price_change']>0]):,}")
    c7.metric("Markets moving down", f"{len(df[df['price_change']<0]):,}")
    c8.metric("Avg days to close",   f"{df['days_to_close'].mean():.0f}d" if df["days_to_close"].notna().any() else "N/A")

    st.markdown("---")
    st.markdown("### Prediction Market Intelligence")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        bins   = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]
        blabs  = ["0-10%","10-20%","20-30%","30-40%","40-50%","50-60%","60-70%","70-80%","80-90%","90-100%"]
        df["bucket"] = pd.cut(df["mid_price"], bins=bins, labels=blabs)
        bdata = df["bucket"].value_counts().sort_index().reset_index()
        bdata.columns = ["Bucket","Count"]
        fig = px.bar(bdata, x="Bucket", y="Count", color_discrete_sequence=["#3B82F6"])
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y} markets<extra></extra>")
        apply_layout(fig, "Probability Buckets")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        sentiment = pd.DataFrame({
            "Type":  ["Strong YES (>80%)", "Strong NO (<20%)", "Contested (40-60%)"],
            "Count": [len(df[df["current_price"]>0.8]),
                      len(df[df["current_price"]<0.2]),
                      len(df[(df["current_price"]>=0.4)&(df["current_price"]<=0.6)])]
        })
        fig2 = px.bar(sentiment, x="Type", y="Count",
                      color="Type", color_discrete_map={
                          "Strong YES (>80%)":"#00C2A8",
                          "Strong NO (<20%)":"#DC2626",
                          "Contested (40-60%)":"#F59E0B"})
        fig2.update_traces(hovertemplate="<b>%{x}</b><br>%{y} markets<extra></extra>")
        fig2.update_layout(showlegend=False)
        apply_layout(fig2, "Market Sentiment")
        st.plotly_chart(fig2, use_container_width=True)

    with col_c:
        drift = df.groupby("category")["price_change_pct"].mean().sort_values().reset_index()
        drift.columns = ["Category","Avg Change %"]
        drift["Color"] = drift["Avg Change %"].apply(lambda x: "#00C2A8" if x >= 0 else "#DC2626")
        fig3 = px.bar(drift, x="Avg Change %", y="Category", orientation="h",
                      color="Color", color_discrete_map="identity")
        fig3.add_vline(x=0, line_color="#333333", line_width=1)
        fig3.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
        fig3.update_layout(showlegend=False)
        apply_layout(fig3, "Price Drift by Category")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # Scatter — opening vs current, colour by source
    fig_sc = go.Figure()
    for src in ["polymarket","kalshi"]:
        sub = df[df["source"]==src] if "source" in df.columns else pd.DataFrame()
        if not sub.empty:
            fig_sc.add_trace(go.Scatter(
                x=sub["mid_price"], y=sub["current_price"],
                mode="markers",
                marker=dict(color=SOURCE_COLORS[src], size=5, opacity=0.5),
                name=SOURCE_LABELS[src],
                hovertemplate="<b>%{text}</b><br>Open: %{x:.2%}<br>Current: %{y:.2%}<extra></extra>",
                text=sub["event_ticker"].str[:50]
            ))
    fig_sc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                                line=dict(color="#333333", dash="dash", width=1),
                                name="No change", hoverinfo="skip"))
    fig_sc.update_xaxes(tickformat=".0%")
    fig_sc.update_yaxes(tickformat=".0%")
    apply_layout(fig_sc, "Opening vs Current Price", height=380)
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔥 Biggest Price Movers")
    top_movers = df_markets.nlargest(10,"price_change_pct")[
        ["event_ticker","source","category","current_price","price_change_pct"]].copy()
    top_movers["source"]        = top_movers["source"].map(SOURCE_LABELS).fillna(top_movers["source"])
    top_movers["Resolves YES"]  = top_movers["current_price"].apply(lambda x: f"{x*100:.0f}%")
    top_movers["Latest Change"] = top_movers["price_change_pct"].apply(lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%")
    top_movers = top_movers[["event_ticker","source","category","Resolves YES","Latest Change"]]
    top_movers.columns = ["Market","Source","Category","Resolves YES","Latest Change"]
    st.dataframe(top_movers.reset_index(drop=True), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Market Browser")
    disp = df[["source","category","event_ticker","current_price","price_change_pct"]].copy()
    disp["source"]        = disp["source"].map(SOURCE_LABELS).fillna(disp["source"])
    disp["Resolves YES"]  = disp["current_price"].apply(lambda x: f"{x*100:.0f}%")
    disp["Latest Change"] = disp["price_change_pct"].apply(lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%")
    disp = disp[["source","category","event_ticker","Resolves YES","Latest Change"]]
    disp.columns = ["Source","Category","Market","Resolves YES","Latest Change"]
    st.dataframe(disp, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — SOURCES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("## Polymarket vs Kalshi")

    def source_panel(col, df_src, label, color):
        with col:
            st.markdown(f"#### {label}")
            if df_src.empty: st.info("No data yet."); return
            m1,m2,m3 = st.columns(3)
            m1.metric("Markets",        f"{len(df_src):,}")
            m2.metric("Avg probability", f"{df_src['current_price'].mean():.2%}")
            m3.metric("Moving up",       f"{len(df_src[df_src['price_change']>0]):,}")

            bins   = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]
            blabs  = ["0-10%","10-20%","20-30%","30-40%","40-50%","50-60%","60-70%","70-80%","80-90%","90-100%"]
            bkts   = pd.cut(df_src["current_price"], bins=bins, labels=blabs).value_counts().sort_index().reset_index()
            bkts.columns = ["Bucket","Count"]
            fig = px.bar(bkts, x="Bucket", y="Count", color_discrete_sequence=[color])
            fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y} markets<extra></extra>")
            apply_layout(fig, "Probability Distribution", height=260)
            st.plotly_chart(fig, use_container_width=True)

            cats = df_src["category"].value_counts().reset_index()
            cats.columns = ["Category","Count"]
            fig2 = px.bar(cats, x="Count", y="Category", orientation="h", color_discrete_sequence=[color])
            fig2.update_traces(hovertemplate="<b>%{y}</b><br>%{x} markets<extra></extra>")
            apply_layout(fig2, "Markets by Category", height=260)
            st.plotly_chart(fig2, use_container_width=True)

            drift = df_src.groupby("category")["price_change_pct"].mean().sort_values().reset_index()
            drift.columns = ["Category","Avg Change %"]
            drift["Color"] = drift["Avg Change %"].apply(lambda x: "#00C2A8" if x>=0 else "#DC2626")
            fig3 = px.bar(drift, x="Avg Change %", y="Category", orientation="h",
                          color="Color", color_discrete_map="identity")
            fig3.add_vline(x=0, line_color="#333333", line_width=1)
            fig3.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
            fig3.update_layout(showlegend=False)
            apply_layout(fig3, "Price Drift by Category", height=260)
            st.plotly_chart(fig3, use_container_width=True)

    lc, rc = st.columns(2)
    source_panel(lc, df_poly_markets,   "🟣 Polymarket",    SOURCE_COLORS["polymarket"])
    source_panel(rc, df_kalshi_markets, "🔵 Kalshi (live)", SOURCE_COLORS["kalshi"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — RESOLVED
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("## Kalshi Resolved Markets")
    if df_hist_markets.empty:
        st.info("No resolved Kalshi markets collected yet.")
    else:
        h1,h2,h3,h4 = st.columns(4)
        h1.metric("Resolved markets",     f"{len(df_hist_markets):,}")
        h2.metric("Settled YES (≥0.9)",   len(df_hist_markets[df_hist_markets["current_price"]>=0.9]))
        h3.metric("Settled NO (≤0.1)",    len(df_hist_markets[df_hist_markets["current_price"]<=0.1]))
        h4.metric("Avg settlement price", f"{df_hist_markets['current_price'].mean():.2%}")

        hc1, hc2 = st.columns(2)
        with hc1:
            bins  = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]
            blabs = ["0-10%","10-20%","20-30%","30-40%","40-50%","50-60%","60-70%","70-80%","80-90%","90-100%"]
            hb = pd.cut(df_hist_markets["current_price"], bins=bins, labels=blabs).value_counts().sort_index().reset_index()
            hb.columns = ["Bucket","Count"]
            fig_h = px.bar(hb, x="Bucket", y="Count", color_discrete_sequence=[SOURCE_COLORS["kalshi_historical"]])
            fig_h.update_traces(hovertemplate="<b>%{x}</b><br>%{y} markets<extra></extra>")
            apply_layout(fig_h, "Settlement Price Distribution")
            st.plotly_chart(fig_h, use_container_width=True)

        with hc2:
            hcats = df_hist_markets["category"].value_counts().reset_index()
            hcats.columns = ["Category","Count"]
            fig_hc = px.bar(hcats, x="Count", y="Category", orientation="h",
                            color_discrete_sequence=[SOURCE_COLORS["kalshi_historical"]])
            fig_hc.update_traces(hovertemplate="<b>%{y}</b><br>%{x} markets<extra></extra>")
            apply_layout(fig_hc, "Resolved Markets by Category")
            st.plotly_chart(fig_hc, use_container_width=True)

        st.markdown("##### Most Recently Resolved")
        hd = df_hist_markets.sort_values("close_time", ascending=False).head(20)[
            ["event_ticker","category","mid_price","current_price","close_time"]].copy()
        hd.columns = ["Market","Category","Entry Price","Settlement Price","Closed"]
        st.dataframe(hd.reset_index(drop=True), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — AI STRATEGY BUILDER
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("## AI Strategy Builder")
    st.markdown("<div style='color:#555;font-size:14px;margin-bottom:24px;'>Describe your strategy in plain English. AI converts it to rules, shows you what it understood, then runs the backtest.</div>", unsafe_allow_html=True)

    if not ANTHROPIC_API_KEY:
        st.error("Add `ANTHROPIC_API_KEY` to your Streamlit secrets to enable this feature.")
    else:
        examples = [
            "Buy underdog politics markets under 20%",
            "Buy contested crypto markets between 40% and 60%",
            "Buy high probability Polymarket sports above 70%",
            "Find mispriced Kalshi markets under 30%",
        ]
        ex = st.selectbox("Start from an example:", ["(type your own below)"] + examples)
        default = ex if ex != "(type your own below)" else ""
        user_strategy = st.text_area("Your strategy", value=default,
                                     placeholder="e.g. Buy YES on politics markets where probability is below 25%",
                                     height=90)

        if st.button("🧠 Parse with AI"):
            if not user_strategy.strip():
                st.warning("Please enter a strategy.")
            else:
                with st.spinner("Parsing..."):
                    result = parse_strategy_with_claude(user_strategy)
                if "error" in result:
                    st.error(f"Parsing failed: {result['error']}")
                else:
                    st.session_state["ai_strategy"] = result

        if "ai_strategy" in st.session_state:
            result = st.session_state["ai_strategy"]
            st.markdown("---")
            st.markdown("### ✅ AI understood this")

            condition   = result.get("condition","N/A")
            threshold_1 = result.get("threshold_1", 0)
            threshold_2 = result.get("threshold_2")
            category    = result.get("category","All")
            source      = result.get("source","all")
            explanation = result.get("explanation","")

            if condition == "between" and threshold_2:
                prob_rule = f"Between {threshold_1:.0%} and {threshold_2:.0%}"
            elif condition == "less than":
                prob_rule = f"Less than {threshold_1:.0%}"
            else:
                prob_rule = f"Greater than {threshold_1:.0%}"

            r1,r2,r3 = st.columns(3)
            r1.metric("Probability Rule", prob_rule)
            r2.metric("Category",         category)
            r3.metric("Source",           source.title())
            st.info(f"💡 {explanation}")

            st.markdown("---")
            st.markdown("### Run Backtest with These Rules?")
            ai_src = st.radio("Data source",
                              ["Live (Polymarket + Kalshi)","Polymarket only","Kalshi live only","Include resolved Kalshi"],
                              horizontal=True, key="ai_bt_src")

            col_run, col_reset = st.columns([1,5])
            with col_run:
                run = st.button("▶ Confirm & Run")
            with col_reset:
                if st.button("↩ Try different strategy"):
                    del st.session_state["ai_strategy"]; st.rerun()

            if run:
                if "Polymarket only" in ai_src:     bt_base = df_poly_markets.copy()
                elif "Kalshi live only" in ai_src:  bt_base = df_kalshi_markets.copy()
                elif "resolved" in ai_src:          bt_base = build_markets_df(pd.concat([df_live_raw,df_hist_raw],ignore_index=True))
                else:                               bt_base = df_markets.copy()

                if source == "polymarket":   bt_base = bt_base[bt_base["source"]=="polymarket"]
                elif source == "kalshi":     bt_base = bt_base[bt_base["source"]=="kalshi"]
                if category != "All":        bt_base = bt_base[bt_base["category"]==category]

                if condition == "less than":   bt_df = bt_base[bt_base["mid_price"] < threshold_1]
                elif condition == "greater than": bt_df = bt_base[bt_base["mid_price"] > threshold_1]
                else: bt_df = bt_base[(bt_base["mid_price"]>=threshold_1)&(bt_base["mid_price"]<=threshold_2)]

                if bt_df.empty:
                    st.warning("No markets matched. Try adjusting thresholds.")
                else:
                    st.markdown(f"### Results — {len(bt_df):,} markets matched")
                    res1,res2,res3,res4 = st.columns(4)
                    res1.metric("Avg Opening Price", f"{bt_df['mid_price'].mean():.2%}")
                    res2.metric("Avg Current Price", f"{bt_df['current_price'].mean():.2%}")
                    res3.metric("Avg Price Change",  f"{bt_df['price_change_pct'].mean():.1f}%")
                    res4.metric("Markets Moving Up", len(bt_df[bt_df["price_change"]>0]))

                    trade_df = bt_df[["event_ticker","source","category","mid_price","current_price","price_change_pct","close_time"]].copy()
                    trade_df["source"] = trade_df["source"].map(SOURCE_LABELS).fillna(trade_df["source"])
                    trade_df.columns   = ["Market","Source","Category","Entry Price","Current Price","Change %","Closes"]
                    st.dataframe(trade_df.reset_index(drop=True), use_container_width=True)

                    bt_s = bt_df.sort_values("mid_price").reset_index(drop=True)
                    bt_s["cumulative"] = bt_s["price_change"].cumsum()
                    fig_c = go.Figure()
                    fig_c.add_trace(go.Scatter(
                        x=bt_s.index, y=bt_s["cumulative"],
                        mode="lines", line=dict(color="#8B5CF6", width=2),
                        fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
                        hovertemplate="Trade %{x}<br>Cumulative: %{y:.4f}<extra></extra>"
                    ))
                    fig_c.add_hline(y=0, line_color="#333333", line_width=1)
                    apply_layout(fig_c, "Cumulative Performance", height=320)
                    st.plotly_chart(fig_c, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — BACKTESTER
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("## Strategy Backtester")
    st.markdown("<div style='color:#555;font-size:14px;margin-bottom:24px;'>Define rules manually and run against tracked markets.</div>", unsafe_allow_html=True)

    bt_source = st.radio("Data source",
                         ["Live (Polymarket + Kalshi)","Polymarket only","Kalshi live only","Include resolved Kalshi"],
                         horizontal=True, key="manual_bt_src")

    cs1,cs2,cs3 = st.columns(3)
    with cs1: entry_condition = st.selectbox("Buy YES if opening probability is", ["less than","greater than","between"])
    with cs2: threshold_1 = st.slider("Threshold 1", 0.05, 0.95, 0.40, 0.05, key="bt_t1")
    with cs3: threshold_2 = st.slider("Threshold 2", 0.05, 0.95, 0.60, 0.05, key="bt_t2") if entry_condition=="between" else None

    cat_bt = st.selectbox("Category", ["All"]+sorted(df_markets["category"].unique().tolist()), key="bt_cat")

    if st.button("▶ Run Backtest", key="manual_bt_run"):
        if "Polymarket only" in bt_source:     bt_base = df_poly_markets.copy()
        elif "Kalshi live only" in bt_source:  bt_base = df_kalshi_markets.copy()
        elif "resolved" in bt_source:          bt_base = build_markets_df(pd.concat([df_live_raw,df_hist_raw],ignore_index=True))
        else:                                  bt_base = df_markets.copy()

        if cat_bt != "All": bt_base = bt_base[bt_base["category"]==cat_bt]

        if entry_condition == "less than":      bt_df = bt_base[bt_base["mid_price"]<threshold_1]
        elif entry_condition == "greater than": bt_df = bt_base[bt_base["mid_price"]>threshold_1]
        else: bt_df = bt_base[(bt_base["mid_price"]>=threshold_1)&(bt_base["mid_price"]<=threshold_2)]

        if bt_df.empty:
            st.warning("No markets match this strategy.")
        else:
            st.markdown(f"### Results — {len(bt_df):,} markets matched")
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("Avg Opening Price", f"{bt_df['mid_price'].mean():.2%}")
            r2.metric("Avg Current Price", f"{bt_df['current_price'].mean():.2%}")
            r3.metric("Avg Price Change",  f"{bt_df['price_change_pct'].mean():.1f}%")
            r4.metric("Markets Moving Up", len(bt_df[bt_df["price_change"]>0]))

            trade_df = bt_df[["event_ticker","source","category","mid_price","current_price","price_change_pct","close_time"]].copy()
            trade_df["source"] = trade_df["source"].map(SOURCE_LABELS).fillna(trade_df["source"])
            trade_df.columns   = ["Market","Source","Category","Entry Price","Current Price","Change %","Closes"]
            st.dataframe(trade_df.reset_index(drop=True), use_container_width=True)

            bt_s = bt_df.sort_values("mid_price").reset_index(drop=True)
            bt_s["cumulative"] = bt_s["price_change"].cumsum()
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(
                x=bt_s.index, y=bt_s["cumulative"],
                mode="lines", line=dict(color="#8B5CF6", width=2),
                fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
                hovertemplate="Trade %{x}<br>Cumulative: %{y:.4f}<extra></extra>"
            ))
            fig_bt.add_hline(y=0, line_color="#333333", line_width=1)
            apply_layout(fig_bt, "Cumulative Performance", height=320)
            st.plotly_chart(fig_bt, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — RECOMMENDER
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown("## Smart Bet Recommender")
    st.markdown("<div style='color:#555;font-size:14px;margin-bottom:24px;'>Set your budget and risk tolerance — we'll find the best markets right now.</div>", unsafe_allow_html=True)

    rc1,rc2,rc3 = st.columns(3)
    with rc1: budget = st.number_input("Budget ($)", min_value=10, max_value=100000, value=100, step=10)
    with rc2: target_return = st.number_input("Target profit ($)", min_value=5, max_value=100000, value=50, step=5)
    with rc3: risk_level = st.selectbox("Risk tolerance", ["Low","Medium","High"])

    rec_src = st.selectbox("Source", ["All (Polymarket + Kalshi)","Polymarket only","Kalshi only"], key="rec_src")
    rec_cat = st.selectbox("Category", ["All"]+sorted(df_markets["category"].unique().tolist()), key="rec_cat")

    if st.button("🎯 Find Best Bets"):
        if risk_level == "Low":
            rec_df = df_markets[(df_markets["current_price"]>=0.65)&(df_markets["current_price"]<=0.95)]
            risk_label = "Low risk — high probability"
        elif risk_level == "Medium":
            rec_df = df_markets[(df_markets["current_price"]>=0.35)&(df_markets["current_price"]<=0.65)]
            risk_label = "Medium risk — contested"
        else:
            rec_df = df_markets[(df_markets["current_price"]>=0.05)&(df_markets["current_price"]<=0.35)]
            risk_label = "High risk — contrarian"

        if "Polymarket only" in rec_src: rec_df = rec_df[rec_df["source"]=="polymarket"]
        elif "Kalshi only"   in rec_src: rec_df = rec_df[rec_df["source"]=="kalshi"]
        if rec_cat != "All": rec_df = rec_df[rec_df["category"]==rec_cat]

        if rec_df.empty:
            st.warning("No markets match. Try adjusting filters.")
        else:
            rec_df = rec_df.copy()
            rec_df["payout_if_yes"] = (1/rec_df["current_price"]).round(2)
            rec_df = rec_df.sort_values("current_price", ascending=False).reset_index(drop=True)
            max_bets = min(10, len(rec_df))
            rec_df   = rec_df.head(max_bets)
            rec_df["bet_amount"]       = round(budget/max_bets, 2)
            rec_df["potential_profit"] = ((rec_df["payout_if_yes"]-1)*rec_df["bet_amount"]).round(2)

            def make_link(row):
                if row["source"]=="polymarket": return f'<a href="https://polymarket.com/event/{row["ticker"]}" target="_blank">Place Bet →</a>'
                elif row["source"]=="kalshi":   return f'<a href="https://kalshi.com/markets/{row["ticker"]}" target="_blank">Place Bet →</a>'
                return ""
            rec_df["link"] = rec_df.apply(make_link, axis=1)

            st.markdown(f"### Top Bets — {risk_label}")
            s1,s2,s3 = st.columns(3)
            s1.metric("Markets found",     len(rec_df))
            s2.metric("Avg probability",   f"{rec_df['current_price'].mean():.2%}")
            s3.metric("Avg payout per $1", f"{rec_df['payout_if_yes'].mean():.2f}x")

            bd = rec_df[["event_ticker","source","category","current_price","payout_if_yes","bet_amount","potential_profit","close_time","link"]].copy()
            bd["source"] = bd["source"].map(SOURCE_LABELS).fillna(bd["source"])
            bd.columns   = ["Market","Source","Category","Probability","Payout/$ 1","Bet ($)","Profit ($)","Closes","🔗"]
            st.write(bd.to_html(escape=False, index=False), unsafe_allow_html=True)

            total_bet, total_profit = rec_df["bet_amount"].sum(), rec_df["potential_profit"].sum()
            st.markdown("---")
            p1,p2,p3 = st.columns(3)
            p1.metric("Capital deployed",   f"${total_bet:.2f}")
            p2.metric("% of budget used",   f"{(total_bet/budget*100):.1f}%")
            p3.metric("Total potential profit", f"${total_profit:.2f}")
