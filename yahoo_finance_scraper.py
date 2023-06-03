# ==================================================================
# Imports
# ==================================================================

from bs4 import BeautifulSoup
import requests 
import os
import json
import pandas as pd
from datetime import date

# ==================================================================
# Helper Functions
# ==================================================================

# loadCSV(): Load's CSV to DataFrame
def loadCSV(folder_filepath, filename):
  # Check if there is a / at the end of folder filepath
  if not folder_filepath[:-1] == "/":
    folder_filepath += "/"
  # Check if the folder exists
  if not os.path.exists(folder_filepath):
    os.makedirs(folder_filepath)
  # Check if the file exists
  if os.path.exists(folder_filepath + filename):
    return pd.read_csv(folder_filepath + filename)
  else:
    data = {
      "date": [],
      "ticker": [],
      "market_cap": [],
      "eps_ttm": []
    }
    return pd.DataFrame(data)

# getMarketCapAndEPS(): scrapes and returns market cap and EPS data from YahooFinance
def getMarketCapAndEPS(ticker):
  marketCap = None
  eps = None

  url = "https://finance.yahoo.com/quote/{}".format(ticker)

  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
  req = requests.get(url=url, headers=headers)

  soup = BeautifulSoup(req.content, "html5lib")
  
  # Get the Market Cap
  td =  soup.find('td', attrs={'data-test': 'MARKET_CAP-value'})
  # Check if the html element has been found
  if td is not None:
    marketCapString = td.text
    # Convert the string to a float
    number = 0
    if marketCapString[-1] == "T":
      number = marketCapString[:-1]
      number = float(number)
      number *= 1000
    elif marketCapString[-1] == "B":
      number = marketCapString[:-1]
      number = float(number)
    elif marketCapString[-1] == "M":
      number = marketCapString[:-1]
      number = float(number)
      number /= 1000
    else:
      marketCapString = marketCapString.replace(",", "")
      number = float(number)
      number /= 1000000
    
    marketCap = number

  # Get the EPS
  td = soup.find('td', attrs={"data-test": "EPS_RATIO-value"})
  if td is not None:
    epsString = td.text
    try:
      eps = float(epsString)
    except ValueError:
      eps = None
  return marketCap, eps

# ==================================================================
# Scrape and save the data to CSV
# ==================================================================

# Get todays current date
today = date.today()

# Array of tickers
tickers = []

companies_file_path = "./resources/companies.json"
with open(companies_file_path, "r") as file:
    data = json.load(file)
    for key in data:
      tickers.append(data[key]["ticker"])

df = loadCSV("./data", "yahoo_finance.csv")

for ticker in tickers:
  valuation, eps = getMarketCapAndEPS(ticker)
  dfToAdd = pd.DataFrame({
    "date": today,
    "ticker": [ticker],
    "market_cap": [valuation],
    "eps_ttm": [eps]
  })
  df = pd.concat([df, dfToAdd])
  print(str(ticker) + ": " + str(valuation) + "B" + " with a " + str(eps) + " EPS (TTM)")

df.to_csv("./data/yahoo_finance.csv", index=False)

