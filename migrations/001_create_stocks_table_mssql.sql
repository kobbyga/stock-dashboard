-- Create stocks table for MS SQL Server (use in production)
-- Run this in SSMS or via sqlcmd / migration tool

CREATE TABLE dbo.stocks (
    symbol       NVARCHAR(16) NOT NULL,
    trade_date   DATE         NOT NULL,
    open_price   FLOAT        NULL,
    high_price   FLOAT        NULL,
    low_price    FLOAT        NULL,
    close_price  FLOAT        NULL,
    daily_volume BIGINT       NULL,
    CONSTRAINT PK_stocks PRIMARY KEY CLUSTERED (symbol, trade_date)
);

-- Nonclustered index to support queries by date
CREATE INDEX IX_stocks_trade_date ON dbo.stocks (trade_date);

-- Notes:
-- - Use DATE type for efficient date operations.
-- - Consider partitioning by year for very large historical tables.
