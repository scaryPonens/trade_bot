import datetime

import pandas as pd
import yfinance as yf


def _bearish_candlesticks(candle_sticks: pd.DataFrame) -> bool:
    """
    This function returns True if the latest candlesticks demonstrate a bearish engulfing pattern
    ```
        Bearish Engulfing Pattern:
            |
         ___|___     _______
        |       |   |       |
        |       |   |       |
        |___ ___|   |       |
            |       |_______|
            |           |
            |           |
        -----------------------
          04-01       04-02
    ```
    This specific combination of conditions could be used to identify potential reversal patterns or significant
    shifts in market sentiment from bullish to bearish between two consecutive sessions. Such patterns are valuable
    for traders who use technical analysis to make trading decisions, as they can signify the beginning of a
    downtrend or a bearish reversal, especially after a bullish period.
    :param candle_sticks:
    :return:
    """
    open_price = candle_sticks.Open.iloc[-1]  # latest open price
    prev_open_price = candle_sticks.Open.iloc[-2]  # previous open price

    close_price = candle_sticks.Close.iloc[-1]  # latest close price
    prev_close_price = candle_sticks.Close.iloc[-2]  # previous close price

    if open_price > close_price \
            and close_price < prev_open_price < prev_close_price <= open_price:
        return True

    return False


def _bullish_candlesticks(candle_sticks: pd.DataFrame) -> bool:
    """
    This function returns True if the latest candlesticks demonstrate a bullish engulfing pattern
    ```
        Bullish Engulfing Pattern:
            |
         ___|___     _______
        |       |   |       |
        |       |   |       |
        |___ ___|   |       |
            |       |_______|
            |           |
            |           |
        -----------------------
          04-01       04-02
    ```
    This specific combination of conditions could be used to identify potential reversal patterns or significant
    shifts in market sentiment from bearish to bullish between two consecutive sessions. Such patterns are valuable
    for traders who use technical analysis to make trading decisions, as they can signify the beginning of an
    uptrend or a bullish reversal, especially after a bearish period.
    :param candle_sticks:
    :return:
    """
    open_price = candle_sticks.Open.iloc[-1]  # latest open price
    prev_open_price = candle_sticks.Open.iloc[-2]  # previous open price

    close_price = candle_sticks.Close.iloc[-1]  # latest close price
    prev_close_price = candle_sticks.Close.iloc[-2]  # previous close price

    if open_price < close_price \
            and close_price > prev_open_price > prev_close_price >= open_price:
        return True

    return False


def signal_generator(candle_sticks: pd.DataFrame) -> str:
    """
    This function generates a signal based on the latest candlesticks.
    :param candle_sticks:
    :return:
    """
    if _bearish_candlesticks(candle_sticks):
        return 'SELL'
    elif _bullish_candlesticks(candle_sticks):
        return 'BUY'
    else:
        return 'HODL'


def fetch_last_60_days(ticker: str) -> pd.DataFrame:
    """
    This function fetches the last 60 days of historical data for a given stock ticker.
    :param ticker:
    :return:
    """
    today = datetime.datetime.utcnow()
    sixty_days_ago = today - datetime.timedelta(days=60)
    return yf.download(ticker, start=sixty_days_ago, end=today, interval='15m')
