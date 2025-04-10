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
import utils.finance_data as finance_data
import utils.tesouro_direto as tesouro_direto
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OPERATIONS_PATH = os.path.join(DATA_DIR, "portfolio_operations.csv")
CSV_COLUMNS = ["ticker", "operation_date", "operation_type", "investment_amount", "quantity", "asset_type"]
OPERATIONS = ["buy", "sell", "bonus"]
ASSET_TYPES = ["Stock", "FII", "ETF", "Crypto", "Fixed Income"]

def load_operations():
    if not os.path.exists(OPERATIONS_PATH):
        pandas.DataFrame(columns=CSV_COLUMNS).to_csv(OPERATIONS_PATH, index=False)

    try:
        df = pandas.read_csv(OPERATIONS_PATH, parse_dates=["operation_date"])
        
        # Check if required columns exist
        if not all(col in df.columns for col in CSV_COLUMNS):
            raise ValueError("CSV missing required columns.")
        return df
    
    except (FileNotFoundError, pandas.errors.EmptyDataError, pandas.errors.ParserError, ValueError) as e:
        print(f"Error loading operations: {e}")
        
        # Reset file with correct columns
        pandas.DataFrame(columns=CSV_COLUMNS).to_csv(OPERATIONS_PATH, index=False)
        return pandas.DataFrame(columns=CSV_COLUMNS)
    
def save_operation(ticker, operation_date, operation_type, investment_amount, quantity, asset_type):
    new_operation = pandas.DataFrame([{
        "ticker": ticker,
        "operation_date": operation_date,
        "operation_type": operation_type,
        "investment_amount": investment_amount,
        "quantity": quantity,
        "asset_type": asset_type
    }])
    operations = load_operations()
    operations = pandas.concat([operations, new_operation], ignore_index=True)
    operations.to_csv(OPERATIONS_PATH, index=False)

def compute_portfolio(operations):
    if operations.empty or "ticker" not in operations.columns:
        return pandas.DataFrame(columns=CSV_COLUMNS)
    
    portfolio = []
    for ticker in operations["ticker"].unique():
        data = operations[operations["ticker"] == ticker]
        
        buys = data[data["operation_type"] == "buy"]
        sells = data[data["operation_type"] == "sell"]
        bonuses = data[data["operation_type"] == "bonus"]

        total_bought = buys["quantity"].sum() + bonuses["quantity"].sum()
        total_sold = sells["quantity"].sum()
        current_qty = total_bought - total_sold

        if current_qty > 0:
            weighted_avg_price = (buys["investment_amount"] * buys["quantity"]).sum() / buys["quantity"].sum()

            asset_type_var = data["asset_type"].iloc[0]
            original_ticker = ticker

            # If Fixed Income, adapt display names
            if asset_type_var == "Fixed Income":
                bond_name, maturity_date = ticker.split("|")
                
                # Normalizing the TESOURO_BONDS for comparison
                normalized_bonds = {k.lower(): v for k, v in tesouro_direto.TESOURO_BONDS.items()}
                bond_code = normalized_bonds[bond_name.lower().strip()]

                ticker_display = f"{bond_code.upper()}_{maturity_date.split('-')[0]}"
                ticker_shortname = f"{bond_name} {maturity_date.split('-')[0]}"
            
            else:
                ticker_display = ticker
                ticker_shortname = finance_data.get_short_name(ticker)

            portfolio.append({
                "original_ticker": original_ticker,
                "ticker": ticker_display,
                "ticker_shortname": ticker_shortname,
                "quantity": current_qty,
                "avg_price": round(weighted_avg_price, 2),
                "asset_type": asset_type_var,
                "operation_date": buys["operation_date"].min(),
                "investment_amount": buys["investment_amount"].sum()
            })
    return pandas.DataFrame(portfolio)

def get_last_price(row):
    if row["asset_type"] == "Fixed Income":
        try:
            bond_name, maturity_date = row["original_ticker"].split("|")
            return tesouro_direto.get_last_price(bond_name, row["operation_date"], row["quantity"], row["investment_amount"])
        except Exception as e:
            print("Tesouro Direto price error:", e)
            return None
    else:
        return finance_data.get_last_close(row["ticker"])

def show():
    streamlit.header("Portfolio Tracker")
    
    # Loads the portfolio from the file
    operations = load_operations()
    portfolio_df = compute_portfolio(operations)

    if portfolio_df.empty:
        streamlit.info("No holdings yet.")
        
    else:
        display_df = portfolio_df.copy()

        # Calculating investment amount differently based on asset_type
        # This iterates the dataframe and returns investment_amount if asset_type is fixed, calculates it if not.
        display_df["investment_amount"] = display_df.apply(
            lambda row: row["investment_amount"] if row["asset_type"] == "Fixed Income"
            else row["quantity"] * row["avg_price"],
            axis=1
        )

        display_df["last_price"] = display_df.apply(get_last_price, axis=1)
        display_df["current_value"] = display_df["quantity"] * display_df["last_price"]
        display_df["gain_loss_pct"] = (display_df["current_value"] - display_df["investment_amount"]) / display_df["investment_amount"] * 100

        # Calculating data for the portfolio Summary
        num_stocks = len(display_df)
        total_qty = display_df["quantity"].sum()
        total_invested = display_df["investment_amount"].sum()
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
        display_df["quantity"] = display_df["quantity"].apply(lambda x: f"{x:,.2f}")
        display_df["avg_price"] = display_df["avg_price"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["last_price"] = display_df["last_price"].apply(lambda x: f"R$ {x:,.2f}" if x else "N/A")
        display_df["investment_amount"] = display_df["investment_amount"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["current_value"] = display_df["current_value"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["gain_loss_pct"] = display_df["gain_loss_pct"].apply(lambda x: f"{x:.2f}%")

        # Reorder columns before renaming
        display_df = display_df[[
            "asset_type",
            "ticker",
            "ticker_shortname",
            "quantity",
            "avg_price",
            "last_price",
            "investment_amount",
            "current_value",
            "gain_loss_pct"
        ]]

        # Renaming the columns
        streamlit.dataframe(display_df.rename(columns={
            "asset_type": "Type",
            "ticker": "Ticker",
            "ticker_shortname": "Name",
            "quantity": "Quantity",
            "avg_price": "Avg Price",
            "last_price": "Last Price",
            "investment_amount": "Invested $",
            "current_value": "Current $",
            "gain_loss_pct": "Gain/Loss"
        }), use_container_width=True)

    # Add Operation Form
    streamlit.subheader("Add New Operation")

    with streamlit.form("add_operation_form", clear_on_submit=True):
        ticker = streamlit.text_input("Ticker (e.g. 'PETR4.SA' or 'Tesouro Prefixado|2031-01-01')")
        asset_type = streamlit.selectbox("Asset Type", ASSET_TYPES)
        operation_type = streamlit.selectbox("Operation Type", options=[op.capitalize() for op in OPERATIONS])
        operation_date = streamlit.date_input("Date", value=date.today())
        quantity = streamlit.number_input("Quantity", step=0.01, min_value=0.01, format="%.2f")
        investment_amount = 0.0 if operation_type == "bonus" else streamlit.number_input("Price", format="%.2f")
        submit = streamlit.form_submit_button("💾 Save Operation")

    if submit:
        form_error = False

        # Prevent invalid sells
        current_qty = portfolio_df[portfolio_df["ticker"] == ticker.upper()]["quantity"].sum()
        if operation_type == "sell" and quantity > current_qty:
            streamlit.error(f"Cannot sell {quantity} shares. You only hold {current_qty}.")
            form_error = True

        # Prevent invalid buys
        if operation_type == "buy" and asset_type != "Fixed Income" and not finance_data.is_valid_yfinance_ticker(ticker):
            streamlit.error(f"Ticker '{ticker.upper()}' not found. Please check the symbol.")
            form_error = True

        # Prevent invalid Tesouro Direto ticker
        if asset_type == "Fixed Income":
            try:
                bond_name, maturity_date = ticker.split("|")
                if bond_name not in tesouro_direto.TESOURO_BONDS:
                    streamlit.error(f"Tesouro Direto ticker '{bond_name}' invalid. The format should be 'Bond_Name|Maturity_date' e.g. 'Tesouro Prefixado|2031-01-01'")
                    form_error = True
                
            except Exception as e:
                streamlit.error(f"Invalid format for Tesouro Direto ticker: {e}.")
                form_error = True

        # Save Operation
        if not form_error:
            save_operation(ticker.upper(), operation_date, operation_type, investment_amount, quantity, asset_type)
            streamlit.success(f"{operation_type.capitalize()} recorded for {ticker}.")
            streamlit.rerun()