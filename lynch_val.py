import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

# Function to get the forward P/E ratio
def calculate_forward_pe(current_price, earnings_estimate):
    return current_price / earnings_estimate

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}
url = f"https://finance.yahoo.com/quote/MSFT/analysis?p=MSFT"
soup = BeautifulSoup(requests.get(url, headers=headers).content, "html5lib")

# Find the row containing the quarters and years
th_row = [th.text for th in soup.find("table").find_all("th")]

# Find the row containing the average estimates
avg_estimate_row = soup.find_all("tr")[2]  # Assuming it's the third row (index 2)

# Extract the "Avg. Estimate" values corresponding to each quarter and year
avg_estimate_values = [td.text for td in avg_estimate_row.find_all("td")[1:]]

# Zip the quarter/year headers with the corresponding average estimate values
result = dict(zip(th_row[1:], avg_estimate_values))

# Convert the 'Next Year (2025)' data to a pandas DataFrame
df = pd.DataFrame({'Next Year (2025)': [result['Next Year (2025)']]})

# Get the current price of the share
ticker = "MSFT"
current_price = yf.download(ticker, progress=False)["Close"].iloc[-1]

# Calculate the forward P/E ratio
earnings_estimate_next_year = float(df['Next Year (2025)'].iloc[0])
forward_pe = calculate_forward_pe(current_price, earnings_estimate_next_year)

# Display the DataFrame and forward P/E ratio
print("Earnings Estimate Data:")
print(df)
print("\nCurrent Price:", current_price)
print("Forward P/E Ratio:", forward_pe)
