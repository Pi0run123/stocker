import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

class StockAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker

    def fetch_earnings_estimate(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
        }
        url = f"https://finance.yahoo.com/quote/{self.ticker}/analysis?p={self.ticker}"
        soup = BeautifulSoup(requests.get(url, headers=headers).content, "html5lib")
        th_row = [th.text for th in soup.find("table").find_all("th")]
        avg_estimate_row = soup.find_all("tr")[2]
        avg_estimate_values = [td.text for td in avg_estimate_row.find_all("td")[1:]]
        result = dict(zip(th_row[1:], avg_estimate_values))
        df = pd.DataFrame({'Next Year (2025)': [result['Next Year (2025)']]})
        return float(df['Next Year (2025)'].iloc[0])

    def fetch_current_price(self):
        data = yf.download(self.ticker, progress=False)
        return data["Close"].iloc[-1]

    def calculate_forward_pe(self, current_price, earnings_estimate):
        return current_price / earnings_estimate
    

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    analyzer = StockAnalyzer(ticker)
    earnings_estimate = analyzer.fetch_earnings_estimate()
    current_price = analyzer.fetch_current_price()
    forward_pe = analyzer.calculate_forward_pe(current_price, earnings_estimate)
    print(f"Forward PE Ratio: {forward_pe}")
