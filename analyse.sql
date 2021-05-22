-------------------------------------------------

How did Bitcoin price in USD vary over time?

SELECT time_bucket('7 days', time) AS period,
      last(close, time) AS last_closing_price
FROM klines
WHERE symb = 'BTCUSDT' and res='1d'
GROUP BY period
ORDER BY period;

-------------------------------------------------

How did Bitcoin price in USD vary over time?

SELECT time,
      close / lead(close) over prices AS daily_factor
FROM (
  SELECT time,
         close
  FROM klines
  WHERE symb = 'BTCUSDT' and res='1d'
  GROUP BY 1,2
) sub window prices AS (ORDER BY time DESC);

-------------------------------------------------

-------------------------------------------------

-------------------------------------------------

-------------------------------------------------

-------------------------------------------------

-------------------------------------------------

-------------------------------------------------

