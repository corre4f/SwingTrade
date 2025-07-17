import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(page_title="Swing Trader (Live)", layout="wide")
st.title("📊 Real-Time Swing Trader Dashboard")

# Reduced ticker list for testing
tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]

@st.cache_data(ttl=300)
def fetch_stock_data(ticker, period="1mo", interval="1d"):
    """Fetch stock data for a single ticker with caching."""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return pd.DataFrame()
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def run_analysis(tickers):
    """Run basic analysis for all tickers."""
    records = []
    for ticker in tickers:
        try:
            data = fetch_stock_data(ticker)
            if data.empty:
                st.warning(f"No data available for {ticker}")
                continue

            close = data['Close']
            current_price = close.iloc[-1] if not close.empty else None
            if current_price is None:
                st.warning(f"No closing price for {ticker}")
                continue

            records.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Ticker": ticker,
                "CurrentPrice": round(current_price, 2),
                "Status": "Success"
            })
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            st.warning(f"Error processing {ticker}: {e}")
            records.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Ticker": ticker,
                "CurrentPrice": None,
                "Status": f"Error: {str(e)}"
            })
    return records

# Sidebar filters
st.sidebar.header("Filters")
selected_tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=tickers,
    default=tickers,  # Default to all tickers
    key="ticker_filter"
)

# Clear cache button for debugging
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared! Refreshing data...")

# Run analysis with loading spinner
with st.spinner("Fetching and analyzing stock data..."):
    results = run_analysis(selected_tickers if selected_tickers else tickers)

# Display results
if not results:
    st.error("No data found for any tickers. Check logs for details.")
else:
    df = pd.DataFrame(results)
    st.subheader(f"🔍 Ticker Data ({len(df)} found)")
    st.write("### Raw Data (for debugging)")
    st.dataframe(df)  # Display raw data for troubleshooting

    # Display formatted output
    for _, row in df.iterrows():
        with st.container():
            st.markdown(f"**{row['Ticker']}**")
            if row['Status'] == "Success":
                st.write(f"Current Price: ${row['CurrentPrice']}")
                st.write(f"Updated: {row['Timestamp']}")
            else:
                st.error(f"Failed to load: {row['Status']}")
            st.write("---")

st.caption("⏱️ Refreshes every 5 minutes (auto-cached)")
