-- Create stocks table for local prototype (SQLite)

CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,               -- stored as 'YYYY-MM-DD'
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    daily_volume INTEGER,
    PRIMARY KEY (symbol, date)
);
