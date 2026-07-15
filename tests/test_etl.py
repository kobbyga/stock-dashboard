import sqlite3
import pandas as pd
import os
import pytest

# Import functions from your script. Adjust module name if your file is named differently.
from fetch_store_stocks2 import fetch_stock_data, save_to_db, create_database

# Helpers / Dummy responses 
class DummyResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

# Tests 
def test_fetch_stock_data_monkeypatch(monkeypatch):
    # Ensure the function finds an API key (it reads env inside the function)
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "DUMMY_KEY")

    sample_json = {
        "Time Series (Daily)": {
            "2026-07-01": {
                "1. open": "100",
                "2. high": "110",
                "3. low": "95",
                "4. close": "105",
                "5. volume": "1000000",
            }
        }
    }

    # Patch requests.get used inside fetch_stock_data
    monkeypatch.setattr("fetch_store_stocks2.requests.get", lambda url: DummyResp(sample_json))

    df = fetch_stock_data("AAPL")
    assert df is not None
    # Check columns and a value
    assert "close_price" in df.columns
    assert float(df.iloc[0]["close_price"]) == 105.0


def test_create_database_and_save_to_db_in_memory():
    # Use an in-memory SQLite DB for isolation and speed
    conn = sqlite3.connect(":memory:")
    try:
        # Create table using the function from your script
        create_database(conn)

        # Prepare a small dataframe matching the expected schema
        df = pd.DataFrame(
            [
                {
                    "date": pd.to_datetime("2026-07-01"),
                    "open_price": 100.0,
                    "high_price": 110.0,
                    "low_price": 95.0,
                    "close_price": 105.0,
                    "daily_volume": 1000000,
                }
            ]
        )

        # Call save_to_db with the connection
        save_to_db(df, "AAPL", conn)

        # Verify the row was inserted
        cur = conn.cursor()
        cur.execute("SELECT symbol, date, close_price FROM stocks WHERE symbol = 'AAPL'")
        rows = cur.fetchall()
        assert len(rows) == 1
        symbol, date_str, close_price = rows[0]
        assert symbol == "AAPL"
        # date is stored as text 'YYYY-MM-DD'
        assert date_str == "2026-07-01"
        assert float(close_price) == 105.0
    finally:
        conn.close()
