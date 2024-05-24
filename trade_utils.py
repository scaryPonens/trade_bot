import datetime
from ctypes import Union
from termcolor import colored as cl
import pandas as pd
import yfinance as yf
from pandas import Timedelta


def _bearish_candlesticks(candle_sticks: pd.DataFrame) -> bool:
    """
    This function returns True if the latest candlesticks demonstrate a bearish engulfing pattern
    ```
        Bearish Engulfing Pattern:
                        |
            |           |
         ___|___     ___|___
        |       |   |       |
        |       |   |       |
        |___ ___|   |       |
            |       |       |
            |       |_______|
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
                     ___|___
         ___|___    |       |
        |       |   |       |
        |       |   |       |
        |___ ___|   |       |
            |       |_______|
                        |
                        |
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


def get_signals(data: pd.DataFrame) -> pd.DataFrame:
    signals = ['HODL']
    for i in range(1, len(data)):
        pair = data.iloc[i - 1:i + 1]
        signals.append(signal_generator(pair))
    data['Signal'] = signals
    return data


def get_donchian_channel_signals(data: pd.DataFrame) -> pd.DataFrame:
    signals = ['HODL', 'HODL', 'HODL']
    in_position = False
    for i in range(3, len(data)):
        if data.High.iloc[i] == data.dcu.iloc[i] and not in_position:
            signals.append('BUY')
            in_position = True
        elif data.Low.iloc[i] == data.dcl.iloc[i] and in_position:
            signals.append('SELL')
            in_position = False
        else:
            signals.append('HODL')

    data['Signal'] = signals
    return data


def get_donchian_channel(data: pd.DataFrame, lower_length: int = 40, upper_length: int = 50) -> pd.DataFrame:
    """
    This function calculates the Donchian Channel for given stock data. The Donchian Channel is a trend-following
    indicator that plots the highest high and lowest low over a specific period of time, typically 20 days.

    :param data: the stock data, expecting a yfinance pandas DataFrame
    :param lower_length: the short period, default is 40
    :param upper_length: the long period, default is 50
    :return: a pandas DataFrame containing the Donchian Channel data
    """
    data['dcu'] = data['High'].rolling(window=Timedelta(days=upper_length)).max()
    data['dcl'] = data['Low'].rolling(window=Timedelta(days=lower_length)).min()
    data['dcm'] = (data['dcu'] + data['dcl']) / 2
    data = data.dropna()
    return data


def implement_strategy(stock, investment):
    """
    This function implements a simple trading strategy based on the Donchian Channel. The strategy is as follows:
    - Buy when the stock price reaches the upper band of the Donchian Channel
    - Sell when the stock price reaches the lower band of the Donchian Channel

    :param stock:  the stock data, expecting a yfinance pandas DataFrame
    :param investment:  the initial investment amount
    :return:  None
    """
    no_of_shares = 0
    equity = investment
    logs = []

    for i in range(3, len(stock)):
        if stock.High.iloc[i] == stock.dcu.iloc[i] and not no_of_shares:
            no_of_shares = equity // stock['Close'].iloc[i]
            equity -= no_of_shares * stock['Close'].iloc[i]
            logs.append(f':green[BUY]: {no_of_shares} Shares are bought at {stock.Close.iloc[i]}USD'
                        f' on {str(stock.index[i])[:10]}')
        elif stock['Low'].iloc[i] == stock['dcl'].iloc[i] and no_of_shares > 0:
            equity += no_of_shares * stock['Close'].iloc[i]
            logs.append(f':red[SELL]: {no_of_shares} Shares are sold at {stock.Close.iloc[i]}USD'
                        f' on {str(stock.index[i])[:10]}')
            no_of_shares = 0
    if no_of_shares > 0:
        equity += no_of_shares * stock['Close'].iloc[i]
        logs.append(f'\n*Closing position at {stock.Close.iloc[i]}USD on {str(stock.index[i])[:10]}*')

    earnings = round(equity - investment, 2)
    roi = round(earnings / investment * 100, 2)
    logs.append(f'\n**INITIAL: {investment}USD ; EARNING: {earnings}USD ; ROI: {roi}%**')
    return '\n\n'.join(logs)


def implement_day_trading_strategy(stock, investment) -> str:
    no_of_shares = 0
    equity = investment
    logs = []

    for i in range(0, len(stock)):
        if stock.Signal.iloc[i] == 'BUY' and not no_of_shares:
            no_of_shares = equity // stock['Close'].iloc[i]
            equity -= no_of_shares * stock['Close'].iloc[i]
        elif stock.Signal.iloc[i] == 'SELL' and no_of_shares > 0:
            equity += no_of_shares * stock['Close'].iloc[i]
            no_of_shares = 0
    if no_of_shares > 0:
        equity += no_of_shares * stock['Close'].iloc[-1]

    earnings = round(equity - investment, 2)
    roi = round(earnings / investment * 100, 2)
    logs.append(f'\n**INITIAL: {investment}USD ; EARNING: {earnings}USD ; ROI: {roi}%**')
    return '\n\n'.join(logs)
