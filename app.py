import os

import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objs as go

from trade_utils import signal_generator, fetch_last_60_days

st.title("Day Trading Bro")

if "last_60_days" not in st.session_state:
    st.session_state["last_60_days"] = fetch_last_60_days('STEM')

candlesticks = st.session_state["last_60_days"]
fig = go.Figure(data=[go.Candlestick(
    x=candlesticks.index,
    open=candlesticks['Open'],
    high=candlesticks['High'],
    low=candlesticks['Low'],
    close=candlesticks['Close'],
    name='Candlesticks',
)])
fig.update_layout(
    title='STEM Candlesticks',
    xaxis_title='',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False,
    width=600,
    height=600
)
st.write(fig)

signals = ['HODL']
for i in range(1, len(candlesticks)):
    pair = candlesticks.iloc[i - 1:i + 1]
    signals.append(signal_generator(pair))
candlesticks['Signal'] = signals

st.write(candlesticks.Signal.value_counts())
