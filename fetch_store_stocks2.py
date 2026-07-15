import os
import sqlite3
import requests
import pandas as pd
import time  # To avoid API rate limits


symbols = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]


# Fetches historical data from Alpha Vantage for a given symbol
def fetch_stock_data(symbol):

    API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

    if not API_KEY:
        raise RuntimeError(
            "Missing ALPHA_VANTAGE_API_KEY. Set it as an environment variable "
            "(see .env.example) before running this script."
        )

    url = (
        f"https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    )

    # Make an API request
    response = requests.get(url)
    data = response.json()

    # Check if response contains valid data
    if "Time Series (Daily)" not in data:
        print(f"Error fetching data for {symbol}: {data}")
        return None

    # Extract daily time series
    time_series = data["Time Series (Daily)"]

    # Convert JSON data to pandas dataframe
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.reset_index(inplace=True)

    df.columns = [
        "date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "daily_volume"
    ]

    df = df[
        [
            "date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "daily_volume",
        ]
    ]

    # Convert data types
    df["date"] = pd.to_datetime(df["date"])

    df[
        [
            "open_price",
            "high_price",
            "low_price",
            "close_price",
        ]
    ] = df[
        [
            "open_price",
            "high_price",
            "low_price",
            "close_price",
        ]
    ].astype(float)

    df["daily_volume"] = df["daily_volume"].astype(int)

    return df


def save_to_db(df, symbol, conn):

    cursor = conn.cursor()

    # Loop through dataframe rows
    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT OR IGNORE INTO stocks
            (
                symbol,
                date,
                open_price,
                high_price,
                low_price,
                close_price,
                daily_volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                row["date"].strftime("%Y-%m-%d"),
                row["open_price"],
                row["high_price"],
                row["low_price"],
                row["close_price"],
                row["daily_volume"],
            ),
        )

    conn.commit()


def create_database(conn):

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT,
            date TEXT,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            daily_volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
        """
    )

    conn.commit()


def main():

    # Create database folder
    os.makedirs("data", exist_ok=True)

    # Open SQLite connection
    conn = sqlite3.connect("data/market_data2.db")

    # Create table
    create_database(conn)

    # Fetch and save stock data
    for symbol in symbols:

        print(f"Fetching data for {symbol}")

        df = fetch_stock_data(symbol)

        if df is not None:
            save_to_db(df, symbol, conn)
            print(f"Data for {symbol} saved.")

        # Alpha Vantage free tier limit
        time.sleep(15)

    conn.close()

    print("All data fetched and stored successfully")


# Only run ETL when script is executed directly
# Does NOT run when imported by tests
if __name__ == "__main__":
    main()
