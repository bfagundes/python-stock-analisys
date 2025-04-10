import yfinance as yf

def get_last_close(ticker: str) -> float | None:
    """Fetches the latest closing price for a given ticker."""
    
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        return hist["Close"].iloc[-1] if not hist.empty else None
    
    except Exception as e:
        print(f"Error fetching last close for {ticker}: {e}")
        return None

def get_short_name(ticker: str) -> str:
    """Fetches the short name of the company or asset."""
    
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName", "")
    
    except Exception as e:
        print(f"Error fetching short name for {ticker}: {e}")
        return ""


def get_info(ticker: str) -> dict:
    """Returns the full .info dictionary for a ticker."""
    
    try:
        return yf.Ticker(ticker).info
    
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {}


def get_historical_prices(ticker: str, start_date, end_date):
    """Returns historical price data for a given date range."""
    
    try:
        return yf.Ticker(ticker).history(start=start_date, end=end_date)
    
    except Exception as e:
        print(f"Error fetching historical prices for {ticker}: {e}")
        return None

def is_valid_yfinance_ticker(ticker):
    """Checks whether a given ticker is valid on yFinance"""

    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period="1d")
        return not hist.empty
    
    except:
        return False