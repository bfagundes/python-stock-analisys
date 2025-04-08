import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as streamlit
import yfinance as yfinance
import pandas as pandas
import plotly.graph_objects as plotly_go
from datetime import date, timedelta

def show():
    streamlit.header("Stocks Comparison")

    # Loading file with IBOV tickers
    base_path = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_path, "data", "ibov_tickers.csv")

    try:
        ibov_df = pandas.read_csv(csv_path)
    except FileNotFoundError:
        streamlit.error(f"Could not find file: {csv_path}")
        return

    ticker_dict = dict(zip(ibov_df["name"], ibov_df["ticker"]))

    # Input selector
    selected_companies = streamlit.multiselect("Select stocks", options=ticker_dict.keys())
    selected_tickers = [ticker_dict[name] for name in selected_companies]

    if len(selected_tickers) < 2:
        streamlit.warning(f"Please, select at least 2 stocks to compare")

    else:
        # Default range: 1 year ago to today
        today = date.today()
        default_start = today - timedelta(days=365)

        # User selects date range
        start_date, end_date = streamlit.date_input("Select date range:", value=(default_start, today), max_value=today)

        if start_date >= end_date:
            streamlit.warning(f"Please, select a valid date range")

        else:
            fig = plotly_go.Figure()
            metrics_data = {}

            for ticker in selected_tickers:
                try:
                    stock = yfinance.Ticker(ticker)
                    hist = stock.history(start=start_date, end=end_date)
                    info = stock.info

                    if not hist.empty:
                        fig.add_trace(
                            plotly_go.Scatter(
                                x=hist.index,
                                y=hist["Close"],
                                mode="lines",
                                name=info.get("shortName", ticker)
                            )
                        )
                    
                    # Store metrics
                    metrics_data[ticker] = {
                        "Current Price": info.get("currentPrice", "N/A"),
                        "Market Cap": info.get("marketCap", "N/A"),
                        "P/E Ratio": info.get("trailingPE", "N/A"),
                        "Dividend Yield": info.get("dividendYield", "N/A"),
                        "ROE": info.get("returnOnEquity", "N/A"),
                        "52w High": info.get("fiftyTwoWeekHigh", "N/A"),
                        "52w Low": info.get("fiftyTwoWeekLow", "N/A")
                    }

                except Exception as e:
                    streamlit.error(f"Error loading data for {ticker}: {e}")

            # Show the chart
            fig.update_layout(title="Price Comparison", xaxis_title="Date", yaxis_title="Close Price")
            streamlit.plotly_chart(fig, use_container_width=True)

            # Build metrics comparison table
            streamlit.subheader(f"Financial Metrics Comparison")

            metrics_list = list(next(iter(metrics_data.values())).keys())
            columns = streamlit.columns(len(selected_tickers) + 1)

            with columns[0]:
                streamlit.markdown(f"**Metric**")
                for metric in metrics_list:
                    streamlit.markdown(f"{metric}")

                for idx, ticker in enumerate(selected_tickers):
                    with columns[idx + 1]:
                        streamlit.markdown(f"**{ticker}**")
                        for metric in metrics_list:
                            value = metrics_data[ticker].get(metric, "N/A")
                            if isinstance(value, float):
                                if "Yield" in metric or "ROE" in metric:
                                    value = f"{value:.2%}"  # Format percentage
                                else:
                                    value = f"{value:,.2f}"
                            elif isinstance(value, int):
                                value = f"{value:,}"
                            streamlit.markdown(f"{value}")