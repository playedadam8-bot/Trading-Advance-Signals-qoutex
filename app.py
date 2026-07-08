import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime

st.title("⚡ Auto-Signal Scanner")

# List of pairs to scan
ALL_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY"]

@st.cache_data(ttl=600)
def get_data(symbol):
    # Ensure you keep your API Key here or in st.secrets
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
    base, quote = symbol[:3], symbol[3:]
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base}&to_symbol={quote}&apikey={api_key}"
    response = requests.get(url).json()
    if 'Time Series FX (Daily)' not in response: return None
    df = pd.DataFrame.from_dict(response['Time Series FX (Daily)'], orient='index').astype(float)
    return df.sort_index()

def get_signal(df):
    # MACD Calculation for "Pre-signal" trends
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]:
        return "CALL"
    elif df['MACD_12_26_9'].iloc[-1] < df['MACDs_12_26_9'].iloc[-1]:
        return "PUT"
    return None

if st.button("GET ALL SIGNALS"):
    st.write(f"Scanning market at {datetime.now().strftime('%H:%M:%S')}...")
    for pair in ALL_PAIRS:
        df = get_data(pair)
        if df is not None:
            signal = get_signal(df)
            if signal:
                st.success(f"PAIR: {pair} | DIRECTION: {signal} | TIME: {datetime.now().strftime('%H:%M')}")
