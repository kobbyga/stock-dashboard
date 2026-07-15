SELECT date,
       close_price,
       LAG(close_price) OVER (PARTITION BY symbol ORDER BY date) AS prev_close,
       (close_price - prev_close) / prev_close AS daily_return
FROM stocks
WHERE symbol = 'AAPL'
ORDER BY date DESC
LIMIT 30;
