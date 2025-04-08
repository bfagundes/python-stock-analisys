import streamlit as streamlit
import yfinance as yfinance
import plotly.graph_objects as plotly_go
from datetime import date, timedelta

def show():
    streamlit.header("Stock Info")
    ticker = streamlit.text_input("Enter the stock ticker (e.g. PETR4.SA)", value="PETR4.SA")

    if ticker:
        try:
            # Getting the stock data from yFinance
            stock = yfinance.Ticker(ticker)

            # Fetching metadata
            info = stock.info 

            streamlit.subheader(f"{info.get('shortName', 'N/A')}")
            col1, col2 = streamlit.columns(2)

            with col1:
                streamlit.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                streamlit.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                streamlit.markdown(f"**Country:** {info.get('country', 'N/A')}")
                streamlit.markdown(f"**Currency:** {info.get('currency', 'N/A')}")

            with col2:
                streamlit.markdown(f"**Current Price:** {info.get('currentPrice', 'N/A')}")
                streamlit.markdown(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
                streamlit.markdown(f"**52w High:** {info.get('fiftyTwoWeekHigh', 'N/A')}")
                streamlit.markdown(f"**52w Low:** {info.get('fiftyTwoWeekLow', 'N/A')}")

            streamlit.markdown("---")
            streamlit.subheader("Price Chart")

            # Default range: 1 year ago to today
            today = date.today()
            default_start = today - timedelta(days=365)

            # User selects date range
            start_date, end_date = streamlit.date_input("Select date range:", value=(default_start, today), max_value=today)

            # Only proceed if valid date range
            if start_date < end_date:
                try:
                    hist = stock.history(start=start_date, end=end_date)

                    if hist.empty:
                        streamlit.warning(f"No historical data available for this range.")
                    else:

                        # Plotting the graph with Streamlit
                        #streamlit.line_chart(hist["Close"])

                        # Plotting the graph with Plotly
                        fig = plotly_go.Figure()
                        fig.add_trace(plotly_go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close"))
                        fig.update_layout(title=f"{ticker.upper()} - Price History", xaxis_title="Date", yaxis_title="Price")
                        streamlit.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    streamlit.error(f"Error fetching historical data: {e}")

            else:
                streamlit.warning(f"Select a valid date range.")

            streamlit.markdown("---")
            streamlit.subheader("Financial Metrics")
            streamlit.write("TBA the metrics that will be here. Mostly the ones for Fundamental Analisys, Balance, DRE, etc.")
    
        except Exception as e:
            streamlit.error(f"Failed to fetch data for ticker '{ticker}'. Error: {e}")