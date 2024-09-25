import requests
import pandas as pd
from io import StringIO
from time import sleep


def get_nse_tickers_scraping():
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    try:
        sleep(1)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_str = response.content.decode("utf-8")
        df = pd.read_csv(StringIO(data_str))
        return df["SYMBOL"].tolist()
    except Exception as e:
        print(f"Error scraping NSE website: {e}")
        return None
