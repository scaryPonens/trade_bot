import datetime
import os
import numpy as np
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.dates as mpl_dates
from dotenv import load_dotenv
import plotly.graph_objs as go

from trade_utils import signal_generator, get_donchian_channel, implement_strategy, get_signals, \
    implement_day_trading_strategy, get_donchian_channel_signals
import yfinance as yf

st.title("Day Trading Bro")

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = 'AAPL'

ticker = st.text_input('Enter a stock symbol', st.session_state['ticker'])

if ticker != st.session_state['ticker'] or "last_60_days" not in st.session_state:
    st.session_state['ticker'] = ticker
    st.session_state["last_60_days"] = yf.download(ticker,
                                                   start=(datetime.date.today() - datetime.timedelta(days=59)),
                                                   end=datetime.date.today() + datetime.timedelta(days=1),
                                                   interval='15m')

candlesticks = st.session_state["last_60_days"]
candlesticks = get_signals(candlesticks)

col1, col2 = st.columns(2)
with col1:
    st.header('Day Trading Strat')
    st.markdown('''
    This strategy is based on the concept of engulfing candlesticks. An engulfing candlestick is a candlestick pattern that
    is formed when a small candlestick is followed by a larger candlestick that completely engulfs the smaller one. This
    pattern is often seen as a sign of a potential uptrend or a bullish reversal, especially after a bearish period.
    A bearish engulfing candlestick pattern is formed when a small bullish candlestick is followed by a larger bearish
    candlestick that completely engulfs the smaller one. This pattern is often seen as a sign of a potential downtrend or a
    bearish reversal, especially after a bullish period.
    
    A sell signal is generated when a bearish engulfing candlestick pattern is formed, while a buy signal is generated when
    a bullish engulfing candlestick pattern is formed.
    ''')
    logs = implement_day_trading_strategy(candlesticks, 1000)
    st.write(logs)

    ohlc = candlesticks[['Open', 'High', 'Low', 'Close']]
    ohlc['date'] = candlesticks.index
    ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
    cols = list(ohlc)
    cols.insert(0, cols.pop(cols.index('date')))
    ohlc = ohlc.loc[:, cols]
    ohlc = ohlc.astype(float)
    fig1, ax1 = plt.subplots(figsize=(20, 10))
    candlestick_ohlc(ax1, ohlc.values, width=0.4, colorup='blue', colordown='grey')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.scatter(candlesticks[candlesticks['Signal'] == 'BUY'].index, candlesticks[candlesticks['Signal'] == 'BUY'].Close,
                color='green', s=200, marker='^', label='BUY')
    ax1.scatter(candlesticks[candlesticks['Signal'] == 'SELL'].index, candlesticks[candlesticks['Signal'] == 'SELL'].Close,
                color='red', s=200, marker='v', label='SELL')
    fig1.suptitle(f'{ticker} 15m Candlesticks')
    st.pyplot(fig1)

with col2:
    st.header('Donchian Strat')
    st.markdown("""
    This strategy is based on the Donchian Channel, which is a trend-following indicator that plots the highest high and
    lowest low over a specific period of time. The Donchian Channel is typically used to identify potential buy and sell
    signals based on the price breaking out of the channel.
    
    A buy signal is generated when the price breaks above the upper band of the Donchian Channel, while a sell signal is
    generated when the price breaks below the lower band of the Donchian Channel.
    """)
    days_in_past = 365
    stock = yf.download(ticker, start=(datetime.date.today() - datetime.timedelta(days=days_in_past)))
    stock = get_donchian_channel(stock, 40, 50).dropna()
    stock = get_donchian_channel_signals(stock)
    logs = implement_strategy(stock, 1000)
    st.write(logs)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(stock[-days_in_past:].Close, label='CLOSE')
    ax.plot(stock[-days_in_past:].dcl, color='black', linestyle='--', alpha=0.3)
    ax.plot(stock[-days_in_past:].dcm, color='orange', label='DCM')
    ax.plot(stock[-days_in_past:].dcu, color='black', linestyle='--', alpha=0.3, label='DCU,DCL')
    ax.scatter(stock[stock['Signal'] == 'BUY'].index, stock[stock['Signal'] == 'BUY'].Close, color='green', s=40,
               marker='^', label='BUY')
    ax.scatter(stock[stock['Signal'] == 'SELL'].index, stock[stock['Signal'] == 'SELL'].Close, color='red', s=40,
               marker='v', label='SELL')
    ax.legend()
    ax.set_title(f'{ticker} DONCHIAN CHANNELS 50')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close (USD)')
    # d.hist(np.random.normal(1, 1, size=1000))
    st.pyplot(fig)
