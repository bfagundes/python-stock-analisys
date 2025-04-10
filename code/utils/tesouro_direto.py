import pandas as pd
import requests
import io

# TESOURO_BONDS = {
#     "Tesouro IPCA+ com Juros Semestrais": "NTN-B",
#     "Tesouro IGPM+ com Juros Semestrais": "NTN-C",
#     "Tesouro Prefixado": "LTN",
#     "Tesouro Prefixado com Juros Semestrais": "NTN-F",
#     "Tesouro Selic": "LTF",
#     "Tesouro IPCA+": "NTN-B PRINCIPAL",
#     "Tesouro RendA+": "RENDA+",
#     "Tesouro Educa+": "EDUCA+",
# }

TESOURO_BONDS = {
    "TESOURO IPCA+ COM JUROS SEMESTRAIS": "NTN-B",
    "TESOURO IGPM+ COM JUROS SEMESTRAIS": "NTN-C",
    "TESOURO PREFIXADO": "LTN",
    "TESOURO PREFIXADO COM JUROS SEMESTRAIS": "NTN-F",
    "TESOURO SELIC": "LTF",
    "TESOURO IPCA+": "NTN-B PRINCIPAL",
    "TESOURO RENDA+": "RENDA+",
    "TESOURO EDUCA+": "EDUCA+",
}

def parse_date_columns(dataframe):
    """Convert date columns (starting with 'Data' or 'Vencimento') to datetime."""
    for col in dataframe.columns:
        if col.startswith(("Data", "Vencimento")):
            dataframe[col] = pd.to_datetime(dataframe[col], format="%d/%m/%Y")
    return dataframe

def get_bonds(type = "venda", group = True):
    if type.lower() == "venda":
        url = "https://www.tesourotransparente.gov.br/ckan/dataset/f0468ecc-ae97-4287-89c2-6d8139fb4343/resource/e5f90e3a-8f8d-4895-9c56-4bb2f7877920/download/VendasTesouroDireto.csv"
    elif type.lower() == "taxa":
        url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
    elif type.lower() == "resgate":
        url = "https://www.tesourotransparente.gov.br/ckan/dataset/f30db6e4-6123-416c-b094-be8dfc823601/resource/30c2b3f5-6edd-499a-8514-062bfda0f61a/download/RecomprasTesouroDireto.csv"
    else:
        raise ValueError("Type not found")
    
    # Getting the data
    data = requests.get(url).text

    # Reading CSV
    data_str = io.StringIO(data)
    dataframe = pd.read_csv(data_str, sep=";", decimal=",")

    print(dataframe)

    # Converting date-related columns into datetime objects
    dataframe = parse_date_columns(dataframe)

    if group:
        # Grouping the data by the first two columns, usually "Título" and "Vencimento"
        # This sets them as a MultiIndex so each row is uniquely identified by both
        multi_index = pd.MultiIndex.from_frame(dataframe.iloc[:, :2])
        
        # Set the new MultiIndex and drop the original first two columns
        dataframe = dataframe.set_index(multi_index).iloc[:, 2:]

    return dataframe

def get_bond_returns(bond_name, maturity_date, investment_date, investment_amount):
    #Gets the bonds data
    bonds = get_bonds(type="taxa", group=True)

    # Retrieve the appropriate bond
    # Why .title() - because the CSV has the data not fully upper or lowercase e.g. Tesouro Prefixado 
    # and title() matches that format
    bond = bonds.loc[(bond_name.title(), maturity_date)]

    # Builds a time series with Preco Unitario 
    # Sorts by date
    # Sets the date as index
    price_series = bond.sort_values("Data Base").set_index("Data Base")[["PU Base Manha"]]

    # Naming the column
    price_series.columns = ["Cumulative Returns"]

    # Filters for dates starting from the investment date
    price_series_from_investment_date = price_series[price_series.index >= pd.to_datetime(investment_date)]
    
    # Calculates daily returns
    daily_pct_returns = price_series_from_investment_date.pct_change()

    # Fills the first NaN with the investment_ammount
    # Then applies compount returns
    cumulative_returns = (1 + daily_pct_returns.fillna(investment_amount)).cumprod() - 1

    return cumulative_returns

def get_last_price(bond_name, maturity_date, investment_date, quantity, investment_amount):
    bond_returns = get_bond_returns(bond_name, maturity_date, investment_date, investment_amount)
    bond_current_value = bond_returns.iloc[-1,0]
    print(f"A: {bond_current_value}")
    return bond_current_value / quantity

def get_bond_name(ticker):
    try:
        bond_name, maturity_date = ticker.split("|")
        return bond_name
    except ValueError as e:
        raise ValueError(f"Invalid ticker format: {e}")

def get_maturity_date(ticker):
    try:
        bond_name, maturity_date = ticker.split("|")
        return maturity_date
    except ValueError as e:
        raise ValueError(f"Invalid ticker format: {e}")