import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, timedelta

# Expanded Pair List
ALL_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURAUD", "GBPJPY", "AUDJPY", "EURCAD", "NZDJPY", "GBPAUD",
    "CADCHF", "EURCHF", "AUDCAD", "CHFJPY", "GBPCAD", "GBPCHF"
]

# Simulated News Schedule
news_schedule = [
    {"event": "GDP Release", "time": "05:30:00", "pair": "EURUSD"},
]

def check_news_timing():
    now = datetime.now()
    for item in news_schedule:
        event_time = datetime.strptime(item["time"], "%H:%M:%S").time()
        event_dt = datetime.combine(datetime.today(), event_time)
        alert_time = event_dt - timedelta(seconds=10) # 10 seconds before
        
        # Trigger condition at 05:29:50
        if now.strftime("%H:%M:%S") == alert_time.strftime("%H:%M:%S"):
            return item
    return None

st.title("SHAWKAT TRADEZ TERMINAL")

if st.button("GET ALL SIGNALS"):
    # Logic for scanning all pairs
    for pair in ALL_PAIRS:
        st.write(f"Scanning {pair}...")
        # Add your signal calculation logic here
    
    # Check for news alert
    alert = check_news_timing()
    if alert:
        st.error(f"⚠️ NEWS ALERT: {alert['event']} in 10s! Pair: {alert['pair']}")

