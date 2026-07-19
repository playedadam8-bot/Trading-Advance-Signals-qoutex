import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import time
from datetime import datetime

# Expanded pair list
ALL_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURAUD", "GBPJPY", "AUDJPY", "EURCAD", "NZDJPY", "GBPAUD",
    "CADCHF", "EURCHF", "AUDCAD", "CHFJPY", "GBPCAD", "GBPCHF"
]

st.set_page_config(page_title="SHAWKAT TRADEZ TERMINAL", layout="centered")
st.title("⚡ SHAWKAT TRADEZ TERMINAL")

def get_data(symbol):
    api_key = st.secrets.get("ALPHA_VANTAGE_KEY")
    base, quote = symbol[:3], symbol[3:]
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base}&to_symbol={quote}&apikey={api_key}"
    response = requests.get(url).json()
    if 'Time Series FX (Daily)' not in response: return None
    return pd.DataFrame.from_dict(response['Time Series FX (Daily)'], orient='index').astype(float).sort_index()

def get_signal(df):
    try:
        macd_df = df.ta.macd(fast=12, slow=26, signal=9)
        if macd_df is None: return None
        df = pd.concat([df, macd_df], axis=1)
        if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]: return "CALL"
        elif df['MACD_12_26_9'].iloc[-1] < df['MACDs_12_26_9'].iloc[-1]: return "PUT"
    except: return None
    return None

if st.button("GET ALL SIGNALS"):
    # Using st.status to provide clean, non-blocking UI feedback
    with st.status("Scanning markets...", expanded=True) as status:
        for pair in ALL_PAIRS:
            st.write(f"Analyzing {pair}...")
            try:
                df = get_data(pair)
                if df is not None and len(df) > 30:
                    signal = get_signal(df)
                    if signal:
                        st.success(f"{pair}: {signal} | {datetime.now().strftime('%H:%M:%S')}")
                else:
                    st.warning(f"{pair}: Data unavailable or rate limited.")
                
                # Pace requests to avoid API bans (critical for free tiers)
                time.sleep(1.2) 
            except Exception as e:
                st.error(f"Error on {pair}: {e}")
        
        status.update(label="Scan complete!", state="complete", expanded=False)
