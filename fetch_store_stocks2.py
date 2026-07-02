#1
import os
import sqlite3
import requests
import pandas as pd
import time # To avoid API rate limits

#2
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing ALPHA_VANTAGE_API_KEY. Set it as an environment variable "
        "(see .env.example) before running this script."
    )
symbols = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]


#3 SQLite connection
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/market_data2.db")
cursor = conn.cursor()

#4 Creating the table if it doesnt exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT,
    date TEXT,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    daily_volume INTEGER,
    PRIMARY KEY (symbol, date)
    );
    ''')

conn.commit()

# Fetches historical data from Alpha Vantage for a given symbol

def fetch_stock_data(symbol):

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
#5 Make an API request  
    response = requests.get(url)
    data = response.json()
#6 Check if response contains valid data 
    if "Time Series (Daily)" not in data:
        print (f"Error fetching data for {symbol}:{data}")
        return None
#7 Extract 'Time Series (Daily)' section from the API response   
    time_series = data["Time Series (Daily)"]
#8 convert the JSON data to a pandas dataframe     
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.reset_index(inplace=True)
    df.columns = ["date", "open_price", "high_price", "low_price", "close_price", "daily_volume"]
    df = df[["date", "open_price", "high_price", "low_price", "close_price", "daily_volume"]]
    
#9 Convert to data types
    df["date"] = pd.to_datetime(df["date"])
    df[["open_price", "high_price", "low_price", "close_price"]] = df[["open_price", "high_price", "low_price", "close_price"]].astype(float)
    
    df['daily_volume'] = df['daily_volume'].astype(int)
    
    return df

def save_to_db(df, symbol):
#10 Loops through each row in the dataframe   
    for _, row in df.iterrows():
#11 Inserts the stock data into SQLite table
        cursor.execute('''
            INSERT OR IGNORE INTO stocks (symbol, date, open_price, high_price, low_price, close_price, daily_volume)
            VALUES (?,?,?,?,?,?,?)
        ''', (symbol, row["date"].strftime('%Y-%m-%d'), row["open_price"], row["high_price"], row["low_price"], row["close_price"], row["daily_volume"]))
    conn.commit()

#12 Loop through symbols and saves API request for each to the SQLite table    
for symbol in symbols:
    print(f"Fetching data for {symbol}")
    df = fetch_stock_data(symbol)
    
    if df is not None:
        save_to_db(df, symbol)
        print(f"Data for {symbol} saved.")
    
    time.sleep(15)

conn.close()

print("All data fetched and stored successfully")