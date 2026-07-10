# Stock Dashboard

A Streamlit dashboard for exploring daily OHLCV stock data (moving averages,
returns, volatility, and candlestick/volume charts), backed by a SQLite
database populated from the Alpha Vantage API.

[Live Dashboard](https://stock-dashboard-d3zuky2gumfdrtl5tnemrm.streamlit.app/)

## Project structure

```
.
├── dashboard2.py            # Streamlit app
├── fetch_store_stocks2.py   # Pulls daily prices from Alpha Vantage into SQLite
├── data/
│   └── market_data2.db      # Sample SQLite database (AAPL, MSFT, TSLA, GOOGL, AMZN)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/kobbyga/stock-dashboard
   cd stock-dashboard
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. (Optional — only needed to refresh the data) Get a free API key from
   [Alpha Vantage](https://www.alphavantage.co/support/#api-key), then:
   ```bash
   cp .env.example .env
   # edit .env and paste your key in
   export $(cat .env | xargs)   # or use a tool like python-dotenv / direnv
   python fetch_store_stocks2.py
   ```

## Running the dashboard

The repo ships with a sample database, so you can run the dashboard right away:

```bash
streamlit run dashboard2.py
```

## Notes

- `fetch_store_stocks2.py` reads your Alpha Vantage key from the
  `ALPHA_VANTAGE_API_KEY` environment variable
- Alpha Vantage's free tier is rate-limited (5 calls/minute), which is why
  the fetch script sleeps 15s between symbols.
