import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title = "Stock Dashboard", layout = "wide")

DB_PATH = "data/market_data2.db"

# 1. Load data and variable construction (cached so it only reruns when the DB changes)

@st.cache_data
def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM stocks", conn)
        
    df["date"] = pd.to_datetime(df["date"])
    
    df = df.sort_values(["symbol","date"])
    
    grouped_close = df.groupby("symbol")["close_price"]
    df["daily_return"] = grouped_close.pct_change()
    df["ma_7"] = grouped_close.transform(lambda x: x.rolling(7).mean())
    df["ma_50"] = grouped_close.transform(lambda x: x.rolling(50).mean())
    df["volatility"] = grouped_close.transform(lambda x: x.pct_change().rolling(30).std()
)
    
    return df

df = load_data()

if df.empty:
    st.error(f"No data found in {DB_PATH}. Check the table name / file path.")
    st.stop()
    
# 2. Sidebar filters

st.sidebar.header("Filters")
symbols = sorted(df["symbol"].unique())
symbol = st.sidebar.selectbox("Choose a stock", symbols)

filtered = df[df["symbol"] == symbol].sort_values("date")

min_date, max_date = filtered["date"].min(), filtered["date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value = (min_date, max_date),
    min_value = min_date,
    max_value = max_date,
)

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]
    
st.title(f"{symbol} Dashboard")

# 3. Headline metrics

if len(filtered) >= 2:
    latest = filtered.iloc[-1]
    prev = filtered.iloc[-2]
    day_change = (latest["close_price"] - prev["close_price"]) / prev["close_price"]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest Close", f"${latest['close_price']:.2f}", f"{day_change:.2%}")
    c2.metric("52-Wk High", f"${filtered['close_price'].max():.2f}")
    c3.metric("52-Wk Low", f"${filtered['close_price'].min():.2f}")
    c4.metric("30d Volatility", f"{latest['volatility']:.2%}" if pd.notna(latest["volatility"]) else "N/A")
    
# 4. Moving averages

fig_ma = px.line(
    filtered, x = "date", y = ["ma_7", "ma_50"],
    title = f"{symbol}: 7-day MA vs 50-day MA",
    labels = {"value": "Price (USD)", "variable": "Series"},
)

st.plotly_chart(fig_ma, use_container_width = True)

# 5. Daily returns summary (instead of a raw dumped series)

st.subheader("Daily Return Summary")
r1, r2, r3 = st.columns(3)
r1.metric("Mean Daily Return", f"{filtered['daily_return'].mean():.2%}")
r2.metric("Std Dev (Daily)", f"{filtered['daily_return'].std():.2%}")
cum_return = (1 + filtered["daily_return"].fillna(0)).prod() - 1
r3.metric("Cumulative Return", f"{cum_return:.2%}")

with st.expander("Show raw daily returns"):
    st.dataframe(
        filtered[["date", "close_price", "daily_return"]].style.format({"close_price": "${:.2f}", "daily_return": "{:.2%}"}
        )
    )
    
# 6. Candlestick + volume
volume_colors = np.where(filtered["close_price"] >= filtered["open_price"], "green", "red")

fig_cs = go.Figure(data = [
    go.Candlestick(
        x = filtered["date"],
        open = filtered["open_price"],
        high = filtered["high_price"],
        low = filtered["low_price"],
        close = filtered["close_price"],
        increasing_line_color = "green",
        decreasing_line_color = "red",
        name = "Price",
    )
])

fig_cs.add_trace(go.Bar(
    x = filtered["date"],
    y = filtered["daily_volume"],
    name = "Volume",
    marker_color = "blue",
    opacity = 0.4,
    yaxis = "y2",
))

fig_cs.update_layout(
    title = f"{symbol} Candlestick Chart",
    xaxis_title = "Date",
    yaxis_title = "Price (USD)",
    yaxis2 = dict(overlaying = "y", side = "right", title = "Volume", showgrid = False), xaxis_rangeslider_visible = False,
)

st.plotly_chart(fig_cs, use_container_width = True)