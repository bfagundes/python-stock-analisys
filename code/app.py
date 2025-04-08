import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st

# Set page config
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Sidebar
st.sidebar.title("📊 Stock Analysis")
st.sidebar.markdown("Welcome! Use the menu below to explore.")

# Sidebar options
menu = st.sidebar.selectbox("Choose a section", [
    "Overview",
    "Stock Info"
])

# Main Title
st.title("📈 Stock Analysis Dashboard")

# Show different sections
if menu == "Overview":
    st.header("📄 Project Overview")
    st.write("This dashboard allows you to analyze Brazilian stocks, track portfolios, compare benchmarks, and more.")

elif menu == "Stock Info":
    st.header("🔎 Single Stock Info")
    
    ticker = st.text_input("Enter the stock ticker (e.g. PETR4.SA)", value="ITSA4.SA")

    if ticker:
        try:
            import yfinance as yfinance

            # Getting the stock data from yFinance
            stock = yfinance.Ticker(ticker)

            # Fetching metadata
            info = stock.info 

            st.subheader(f"📌 {info.get('shortName', 'N/A')}")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                st.markdown(f"**Country:** {info.get('country', 'N/A')}")
                st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")

            with col2:
                st.markdown(f"**Current Price:** {info.get('currentPrice', 'N/A')}")
                st.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
                st.markdown(f"**52w High:** {info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.markdown(f"**52w Low:** {info.get('fiftyTwoWeekLow', 'N/A')}")

        except Exception as e:
            st.error(f"Failed to fetch data for ticker '{ticker}'. Error: {e}")