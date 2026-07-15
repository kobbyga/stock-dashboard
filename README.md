# Stock Dashboard

A Streamlit dashboard for exploring daily OHLCV stock data (moving averages,
returns, volatility, and candlestick/volume charts), backed by a SQLite
database populated from the Alpha Vantage API.

[Live Dashboard](https://stock-dashboard-d3zuky2gumfdrtl5tnemrm.streamlit.app/)

## Project structure

```
stock-dashboard/
├── dashboard2.py            # Streamlit app
├── fetch_store_stocks2.py   # Pulls daily prices from Alpha Vantage into SQLite
├── data/
│   └── market_data2.db      # Sample SQLite database (AAPL, MSFT, TSLA, GOOGL, AMZN)
├── migrations/
│   ├── 001_create_stocks_table_mssql.sql
│   └── 001_create_stocks_table_sqlite.sql
├── tests/
│   └── test_etl.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Overview

- **ETL:** `fetch_store_stocks2.py` fetches daily OHLCV from Alpha Vantage, validates types, and writes idempotent inserts into `data/market_data2.db`.
- **DB schema:** `stocks(symbol TEXT, date TEXT, open_price REAL, high_price REAL, low_price REAL, close_price REAL, daily_volume INTEGER)` with composite primary key **(symbol, date)** to prevent duplicates.
- **Dashboard:** `dashboard2.py` reads the DB and provides interactive charts and analytics.

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/kobbyga/stock-dashboard
   cd stock-dashboard
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Get a free API key from
   [Alpha Vantage](https://www.alphavantage.co/support/#api-key), then:
   ```bash
   cp .env.example .env
   # edit .env and paste your key in
   python fetch_store_stocks2.py
   ```

## Running the dashboard

The repo ships with a sample database, so you can run the dashboard right away:

```bash
streamlit run dashboard2.py
```

## Running the test

1. Install pytest if not already downloaded:

```bash
pip install pytest
```
2. Run test from repository root:

```bash
pytest -q
```

## Migration Plan

Migrations: SQL migration files are in migrations/.

- 01_create_stocks_table_sqlite.sql creates the prototype table for local testing.

- 001_create_stocks_table_mssql.sql is the production schema for MS SQL Server (use in SSMS or via sqlcmd or a migration tool).

## Notes

- `fetch_store_stocks2.py` reads your Alpha Vantage key from the
  `ALPHA_VANTAGE_API_KEY` environment variable
- Alpha Vantage's free tier is rate-limited (5 calls/minute), which is why
  the fetch script sleeps 15s between symbols.
  
## Development Container

This repository includes a Dev Container configuration for GitHub Codespaces and
VS Code Dev Containers. Opening the project in a supported environment will:

- Install the required system and Python dependencies.
- Install the Streamlit package.
- Automatically launch the dashboard (`dashboard2.py`).
- Forward port 8501 and open the application preview.
