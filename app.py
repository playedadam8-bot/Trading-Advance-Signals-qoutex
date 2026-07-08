import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime

st.title("⚡ Auto-Signal Scanner")

ALL_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY"]

@st.cache_data(ttl=600)
def get_data(symbol):
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
    base, quote = symbol[:3], symbol[3:]
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base}&to_symbol={quote}&apikey={api_key}"
    response = requests.get(url).json()
    if 'Time Series FX (Daily)' not in response: return None
    df = pd.DataFrame.from_dict(response['Time Series FX (Daily)'], orient='index').astype(float)
    return df.sort_index()

def get_signal(df):
    # This block calculates MACD and returns 'None' if it fails
    try:
        macd_df = df.ta.macd(fast=12, slow=26, signal=9)
        if macd_df is None: return None
        
        # Merge back to original df
        df = pd.concat([df, macd_df], axis=1)
        
        # Get last values safely
        if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]:
            return "CALL"
        elif df['MACD_12_26_9'].iloc[-1] < df['MACDs_12_26_9'].iloc[-1]:
            return "PUT"
    except:
        return None
    return None

if st.button("GET ALL SIGNALS"):
    for pair in ALL_PAIRS:
        df = get_data(pair)
        if df is not None and len(df) > 30:
            signal = get_signal(df)
            if signal:
                st.success(f"PAIR: {pair} | DIRECTION: {signal} | TIME: {datetime.now().strftime('%H:%M')}")
        else:
            st.warning(f"Skipping {pair}: Data not ready.")
