"""
Section: Portfolio Tracker

This module allows users to:
- Record operations: buy, sell, bonus
- Track historical portfolio operations (saved to CSV)
- Compute current holdings with average price
- Display a summary of the user's portfolio with total invested, current value, gain/loss
- Show a line chart of portfolio evolution over time

Data is persisted in `data/portfolio_operations.csv`.
"""

import os
import pandas as pandas
import streamlit as streamlit
from datetime import date
import yfinance as yfinance
import plotly.graph_objects as plotly_go

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OPERATIONS_PATH = os.path.join(DATA_DIR, "portfolio_operations.csv")
    
def load_operations():
    expected_cols = ["ticker", "date", "operation", "price", "quantity"]

    if not os.path.exists(OPERATIONS_PATH):
        pandas.DataFrame(columns=expected_cols).to_csv(OPERATIONS_PATH, index=False)

    try:
        df = pandas.read_csv(OPERATIONS_PATH, parse_dates=["date"])
        
        # Check if required columns exist
        if not all(col in df.columns for col in expected_cols):
            raise ValueError("CSV missing required columns.")
        return df
    
    except (FileNotFoundError, pandas.errors.EmptyDataError, pandas.errors.ParserError, ValueError) as e:
        print(f"Error loading operations: {e}")
        
        # Reset file with correct columns
        pandas.DataFrame(columns=expected_cols).to_csv(OPERATIONS_PATH, index=False)
        return pandas.DataFrame(columns=expected_cols)
    
def save_operation(ticker, op_date, operation, price, quantity):
    new_op = pandas.DataFrame([{
        "ticker": ticker,
        "date": op_date,
        "operation": operation,
        "price": price,
        "quantity": quantity,
    }])
    ops = load_operations()
    ops = pandas.concat([ops, new_op], ignore_index=True)
    ops.to_csv(OPERATIONS_PATH, index=False)

def compute_portfolio(ops):
    if ops.empty or "ticker" not in ops.columns:
        return pandas.DataFrame(columns=["ticker", "quantity", "avg_price"])
    
    portfolio = []
    for ticker in ops["ticker"].unique():
        data = ops[ops["ticker"] == ticker]
        buys = data[data["operation"] == "buy"]
        sells = data[data["operation"] == "sell"]
        bonuses = data[data["operation"] == "bonus"]

        total_bought = buys["quantity"].sum() + bonuses["quantity"].sum()
        total_sold = sells["quantity"].sum()
        current_qty = total_bought - total_sold

        if current_qty > 0:
            weighted_avg_price = (buys["price"] * buys["quantity"]).sum() / buys["quantity"].sum()
            portfolio.append({
                "ticker": ticker,
                "quantity": current_qty,
                "avg_price": round(weighted_avg_price, 2)
            })
    return pandas.DataFrame(portfolio)

def show():
    streamlit.header("💼 Portfolio Tracker")
    ops = load_operations()
    portfolio_df = compute_portfolio(ops)

    if portfolio_df.empty:
        streamlit.info("No holdings yet.")
        
    else:
        display_df = portfolio_df.copy()

        # Gets current prices
        def get_last_close(ticker):
            try:
                hist = yfinance.Ticker(ticker).history(period="5d")
                return hist["Close"].iloc[-1] if not hist.empty else None
            except:
                return None
            
        def get_short_name(ticker):
            try:
                info = yfinance.Ticker(ticker).info
                return info.get("shortName", "")
            except:
                return ""

        display_df["ticker_shortname"] = display_df["ticker"].apply(get_short_name)
        display_df["last_close"] = display_df["ticker"].apply(get_last_close)
        display_df["invested_value"] = display_df["quantity"] * display_df["avg_price"]
        display_df["current_value"] = display_df["quantity"] * display_df["last_close"]
        display_df["gain_loss_pct"] = (display_df["current_value"] - display_df["invested_value"]) / display_df["invested_value"] * 100

        # Calculating data for the portfolio Summary
        num_stocks = len(display_df)
        total_qty = display_df["quantity"].sum()
        total_invested = display_df["invested_value"].sum()
        total_current = display_df["current_value"].sum()
        total_return_pct = 0
        if total_invested > 0:
            total_return_pct = (total_current - total_invested) / total_invested * 100

        # Portfolio summary
        col1, col2, col3 = streamlit.columns(3)
        col1.metric("💵 Current Value", f"R$ {total_current:,.2f}", delta=f"{total_return_pct:.2f}%")
        col2.metric("🏢 Tickers", f"{num_stocks}")
        col3.metric("📦 Stocks Held", f"{int(total_qty)}")
        
        # Format for display
        display_df["quantity"] = display_df["quantity"].apply(lambda x: f"{x:,.0f}")
        display_df["avg_price"] = display_df["avg_price"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["last_close"] = display_df["last_close"].apply(lambda x: f"R$ {x:,.2f}" if x else "N/A")
        display_df["invested_value"] = display_df["invested_value"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["current_value"] = display_df["current_value"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["gain_loss_pct"] = display_df["gain_loss_pct"].apply(lambda x: f"{x:.2f}%")

        # Reorder columns before renaming
        display_df = display_df[[
            "ticker",
            "ticker_shortname",
            "quantity",
            "avg_price",
            "last_close",
            "invested_value",
            "current_value",
            "gain_loss_pct"
        ]]

        streamlit.dataframe(display_df.rename(columns={
            "ticker": "Ticker",
            "ticker_shortname": "Name",
            "quantity": "Quantity",
            "avg_price": "Avg Price",
            "last_close": "Last Price",
            "invested_value": "Invested $",
            "current_value": "Current $",
            "gain_loss_pct": "Gain/Loss"
        }), use_container_width=True)

    streamlit.subheader("➕ Add New Operation")

    with streamlit.form("add_operation_form", clear_on_submit=True):
        ticker = streamlit.text_input("Ticker (e.g. PETR4.SA)", max_chars=12).upper()
        operation = streamlit.selectbox("Operation Type", ["buy", "sell", "bonus"])
        op_date = streamlit.date_input("Date", value=date.today())
        quantity = streamlit.number_input("Quantity", step=1, min_value=1)
        price = 0.0 if operation == "bonus" else streamlit.number_input("Price", format="%.2f")
        submit = streamlit.form_submit_button("💾 Save Operation")

    if submit:
        # Prevent invalid sells
        current_qty = portfolio_df[portfolio_df["ticker"] == ticker]["quantity"].sum()
        if operation == "sell" and quantity > current_qty:
            streamlit.error(f"❌ Cannot sell {quantity} shares. You only hold {current_qty}.")

        # Save Operation
        else:
            save_operation(ticker, op_date, operation, price, quantity)
            streamlit.success(f"✅ {operation.capitalize()} recorded for {ticker}.")
            streamlit.rerun()