import streamlit as streamlit
from utils.tesouro_direto import (
    TESOURO_BONDS,
    get_bonds,
    get_bond_returns
)

def show():
    streamlit.header("Tesouro Direto Info")

    ticker = "Tesouro Prefixado|2031-01-01"
    asset_type = "Fixed Income"
    operation_type = "Buy"
    date = "2024-12-04"
    price = 4998.20
    quantity = 10.62

    ticker, maturity_date = ticker.split("|")
    maturity_year = maturity_date.split("-")[0]
    ticker_display_name = TESOURO_BONDS[ticker].upper() + "_" + maturity_year
    ticker_display_shortname = ticker + " " + maturity_year

    try:
        df = get_bonds()
        
        if df.empty:
            streamlit.warning("Nenhum título encontrado no momento.")
        else:
            streamlit.dataframe(df, use_container_width=True)

    except Exception as e:
        streamlit.error(f"Erro ao carregar dados do Tesouro Direto: {e}")

    bond_returns = get_bond_returns(ticker, maturity_date, date, price)
    current_value = bond_returns.iloc[-1, 0]
    last_price = current_value / quantity
    gain_loss_pct = ((current_value - price) / price) * 100

    streamlit.write(bond_returns)

    streamlit.write(f"Type: {asset_type}")
    streamlit.write(f"Ticker: {ticker_display_name}")
    streamlit.write(f"Name: {ticker_display_shortname}")
    streamlit.write(f"Quantity: {quantity}")
    streamlit.write(f"Avg Price: TBD")
    streamlit.write(f"Last Price: {last_price}")
    streamlit.write(f"Invested $: {price}")
    streamlit.write(f"Current $: {current_value}")
    streamlit.write(f"Gain/Loss $: {gain_loss_pct}")