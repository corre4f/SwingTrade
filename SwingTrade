import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import AverageTrueRange
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(page_title="Swing Trader (Live)", layout="wide")
st.title("📊 Real-Time Swing Trader Dashboard")

# Reduced ticker list to avoid resource overload
tickers = [
    "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN",
    "NVDA", "META", "AMD", "INTC", "NFLX"
]

@st.cache_data(ttl=300)
def fetch_stock_data(ticker, period="3mo", interval="1d"):
    """Fetch stock data for a single ticker with caching."""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def run_analysis(tickers):
    """Run technical analysis for all tickers."""
    records = []
    for ticker in tickers:
        try:
            data = fetch_stock_data(ticker, period="3mo", interval="1d")
            if data.empty:
                logger.warning(f"No data for {ticker}")
                continue

            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']

            rsi = RSIIndicator(close).rsi().iloc[-1]
            macd_diff = MACD(close).macd_diff().iloc[-1]
            atr = AverageTrueRange(high, low, close).average_true_range().iloc[-1]

            current_price = close.iloc[-1]
            prev_price = close.iloc[-2]
            avg_volume = volume.rolling(window=10).mean().iloc[-1]
            vol_spike = volume.iloc[-1] > 1.5 * avg_volume
            gap = current_price - prev_price if abs(current_price - prev_price) > atr else 0

            # MA crossover detection
            ema_9 = close.ewm(span=9).mean()
            ema_21 = close.ewm(span=21).mean()
            crossover = "None"
            if ema_9.iloc[-2] < ema_21.iloc[-2] and ema_9.iloc[-1] > ema_21.iloc[-1]:
                crossover = "Bullish Crossover"
            elif ema_9.iloc[-2] > ema_21.iloc[-2] and ema_9.iloc[-1] < ema_21.iloc[-1]:
                crossover = "Bearish Crossover"

            # RSI + MACD combo
            rsi_macd_combo = 40 < rsi < 60 and macd_diff > 0

            # Pattern detection
            pattern = "None"
            trend = "Neutral"
            if len(close) >= 5:
                if close.iloc[-3] < close.iloc[-4] and close.iloc[-1] > close.iloc[-3]:
                    neckline = close.iloc[-2]
                    if close.iloc[-1] > neckline:
                        pattern = "Double Bottom"
                        trend = "Bullish"
                elif close.iloc[-4] > close.iloc[-3] < close.iloc[-2] and close.iloc[-1] > close.iloc[-2]:
                    neckline = max(close.iloc[-4], close.iloc[-2])
                    if close.iloc[-1] > neckline:
                        pattern = "Inverse Head & Shoulders"
                        trend = "Bullish"
                elif close.iloc[-5] > close.iloc[-4] > close.iloc[-3] < close.iloc[-2] < close.iloc[-1]:
                    pattern = "Falling Wedge"
                    trend = "Bullish"
                elif close.iloc[-5] < close.iloc[-4] < close.iloc[-3] > close.iloc[-2] > close.iloc[-1]:
                    pattern = "Rising Wedge"
                    trend = "Bearish"
                elif close.iloc[-4] < close.iloc[-3] > close.iloc[-2] and close.iloc[-1] < close.iloc[-2]:
                    pattern = "Head & Shoulders"
                    trend = "Bearish"

            # Composite signal summary
            signals = []
            if crossover != "None":
                signals.append(crossover)
            if rsi_macd_combo:
                signals.append("RSI+MACD Combo")
            if vol_spike:
                signals.append("Volume Spike")
            signal_label = ", ".join(signals) if signals else "None"

            prob = 80 if trend == "Bullish" and "Combo" in signal_label else 60

            records.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Ticker": ticker,
                "Pattern": pattern,
                "Trend": trend,
                "RSI": round(rsi, 2),
                "MACD": round(macd_diff, 2),
                "ATR": round(atr, 2),
                "Volume": int(volume.iloc[-1]),
                "Gap": round(gap, 2),
                "CurrentPrice": round(current_price, 2),
                "Price_Target_Up": round(current_price + atr * 2, 2),
                "Price_Target_Down": round(current_price - atr * 2, 2),
                "Probability": prob,
                "Signals": signal_label
            })
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            continue
    return records

# Sidebar filters
st.sidebar.header("Filters")
selected_tickers = st.sidebar.multiselect(
    "Select Tickers",
    sorted(tickers),
    default=sorted(tickers[:5]),  # Limit default to 5 tickers for performance
    key="ticker_filter"
)
interval = st.sidebar.selectbox("Chart Interval", options=["1m", "5m", "15m", "1d", "1wk"], index=3)
trends = st.sidebar.multiselect("Select Trend", ["Bullish", "Bearish", "Neutral"], default=["Bullish", "Bearish"], key="trend_filter")

# Run analysis with loading spinner
with st.spinner("Fetching and analyzing stock data..."):
    results = run_analysis(selected_tickers)

# Display results
if not results:
    st.warning("No data found for the selected tickers.")
else:
    df = pd.DataFrame(results)
    df["Trend_Icon"] = df["Trend"].map({"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪"})
    df["Up_Prob"] = df["Probability"].astype(str) + "%"

    filtered_df = df[(df["Ticker"].isin(selected_tickers)) & (df["Trend"].isin(trends))]

    st.subheader(f"🔍 Trade Signals ({len(filtered_df)} found)")
    for _, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{row['Ticker']}** — {row['Pattern']} {row['Trend_Icon']}")
                st.caption(f"RSI: {row['RSI']} | MACD: {row['MACD']} | ATR: {row['ATR']}")
            with col2:
                st.metric("Price Target ↑", f"${row['Price_Target_Up']}", delta=f"{row['Probability']}%")
                st.metric("Price Target ↓", f"${row['Price_Target_Down']}")
            with col3:
                st.write(f"Gap: {row['Gap']} | Volume: {row['Volume']}")
                st.write(f"Now: ${row['CurrentPrice']}")
                st.write(f"📌 Signals: {row['Signals']}")

            with st.expander("📈 Price Trend", expanded=False):
                try:
                    period_map = {
                        "1m": "1d",
                        "5m": "5d",
                        "15m": "7d",
                        "1d": "3mo",
                        "1wk": "6mo"
                    }
                    period = period_map.get(interval, "1mo")
                    hist = fetch_stock_data(row["Ticker"], period=period, interval=interval)

                    if not hist.empty and "Close" in hist:
                        hist["Smooth"] = hist["Close"].rolling(window=3).mean()
                        st.line_chart(hist[["Close", "Smooth"]])
                    else:
                        st.caption("No chart data available.")
                except Exception as e:
                    st.error(f"Chart error for {row['Ticker']}: {e}")

st.caption("⏱️ Refreshes every 5 minutes (auto-cached)")
