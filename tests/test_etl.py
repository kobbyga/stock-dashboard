import sqlite3
import pandas as pd
from fetch_store_stocks2 import fetch_stock_data, save_to_db

def test_fetch_stock_data_monkeypatch(monkeypatch):
    sample_json = {
        "Time Series (Daily)": {
            "2026-07-01": {"1. open":"100","2. high":"110","3. low":"95","4. close":"105","5. volume":"1000000"}
        }
    }
    class DummyResp:
        def json(self): return sample_json
    monkeypatch.setattr("fetch_store_stocks2.requests.get", lambda url: DummyResp())
    df = fetch_stock_data("AAPL")
    assert not df.empty
    assert df.iloc[0]["close_price"] == 105.0

def test_save_to_db_in_memory(tmp_path):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE stocks (symbol TEXT, date TEXT, open_price REAL, high_price REAL, low_price REAL, close_price REAL, daily_volume INTEGER, PRIMARY KEY(symbol,date))''')
    conn.commit()
    df = pd.DataFrame([{"date":"2026-07-01","open_price":100.0,"high_price":110.0,"low_price":95.0,"close_price":105.0,"daily_volume":1000000}])
    # call save_to_db with a wrapper that uses this in-memory conn or refactor save_to_db to accept a connection
    # assert row inserted
