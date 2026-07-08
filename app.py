import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests

st.title("Forex Signal Dashboard")

# 1. Fetch Price Data
def get_forex_data(symbol):
    # Alpha Vantage API call
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={symbol[:3]}&to_symbol={symbol[3:]}&apikey={st.secrets['ALPHA_VANTAGE_KEY']}"
    response = requests.get(url).json()
    
    # Convert JSON to DataFrame
    data = response['Time Series FX (Daily)']
    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = ['open', 'high', 'low', 'close']
    df = df.astype(float)
    return df

# 2. Generate Signal
def get_signal(df):
    # Calculate RSI using pandas_ta
    df.ta.rsi(length=14, append=True)
    last_rsi = df['RSI_14'].iloc[-1]
    
    if last_rsi < 30: return "CALL (Oversold)"
    if last_rsi > 70: return "PUT (Overbought)"
    return "WAIT (Neutral)"

# 3. Fetch News
def get_news(symbol):
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={st.secrets['NEWS_API_KEY']}"
    news = requests.get(url).json()
    return news.get('articles', [])[:3] # Get top 3 headlines

# App UI
pair = st.selectbox("Select Pair", ["EURUSD", "GBPUSD", "USDJPY"])

if st.button("Generate Signal"):
    df = get_forex_data(pair)
    signal = get_signal(df)
    
    st.subheader(f"Signal: {signal}")
    
    st.write("### Recent News Sentiment:")
    news_list = get_news(pair)
    for item in news_list:
        st.write(f"- {item['title']}")
