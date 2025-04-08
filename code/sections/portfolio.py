import os
import pandas as pandas
import streamlit as streamlit
from datetime import date

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
        "quantity": quantity
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
        display_df["avg_price"] = display_df["avg_price"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["quantity"] = display_df["quantity"].apply(lambda x: f"{x:,.2f}")
        streamlit.dataframe(display_df.rename(columns={
            "ticker": "Ticker",
            "quantity": "Quantity",
            "avg_price": "Average Price"
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
        streamlit.write("DEBUG: Portfolio DataFrame", portfolio_df)

        current_qty = portfolio_df[portfolio_df["ticker"] == ticker]["quantity"].sum()
        if operation == "sell" and quantity > current_qty:
            streamlit.error(f"❌ Cannot sell {quantity} shares. You only hold {current_qty}.")
        else:
            save_operation(ticker, op_date, operation, price, quantity)
            streamlit.success(f"✅ {operation.capitalize()} recorded for {ticker}.")
            streamlit.rerun()