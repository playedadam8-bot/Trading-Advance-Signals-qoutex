import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime

st.title("⚡ Auto-Signal Scanner")

# Expanded list of major and minor currency pairs
ALL_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", # Majors
    "EURGBP", "EURAUD", "GBPJPY", "AUDJPY", "EURCAD", "NZDJPY", "GBPAUD", # Minors
    "CADCHF", "EURCHF", "AUDCAD", "CHFJPY", "GBPCAD", "GBPCHF"
]

@st.cache_data(ttl=600)
def get_data(symbol):
    # Ensure you have your API key set in Streamlit secrets
    api_key = st.secrets.get("ALPHA_VANTAGE_KEY")
    if not api_key:
        st.error("API Key not found. Please set 'ALPHA_VANTAGE_KEY' in your secrets.")
        return None
        
    base, quote = symbol[:3], symbol[3:]
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base}&to_symbol={quote}&apikey={api_key}"
    response = requests.get(url).json()
    
    if 'Time Series FX (Daily)' not in response: 
        return None
        
    df = pd.DataFrame.from_dict(response['Time Series FX (Daily)'], orient='index').astype(float)
    return df.sort_index()

def get_signal(df):
    try:
        # Calculate MACD
        macd_df = df.ta.macd(fast=12, slow=26, signal=9)
        if macd_df is None: return None
        
        # Merge back to original df
        df = pd.concat([df, macd_df], axis=1)
        
        # Check the most recent signal
        if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]:
            return "CALL"
        elif df['MACD_12_26_9'].iloc[-1] < df['MACDs_12_26_9'].iloc[-1]:
            return "PUT"
    except Exception:
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
            # Using warning for pairs where data couldn't be fetched
            st.warning(f"Skipping {pair}: Data not ready or unavailable.")
