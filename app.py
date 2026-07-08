import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests

st.set_page_config(page_title="Forex Signal Bot", layout="wide")
st.title("📈 Advanced Forex Signal Bot")

# 1. Fetch Price Data (Alpha Vantage)
def get_forex_data(symbol):
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
    base = symbol[:3]
    quote = symbol[3:]
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base}&to_symbol={quote}&apikey={api_key}"
    
    response = requests.get(url).json()
    if 'Time Series FX (Daily)' not in response:
        return None
        
    data = response['Time Series FX (Daily)']
    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = ['open', 'high', 'low', 'close']
    df = df.astype(float)
    return df.sort_index()

# 2. Logic: Generate Signal
def generate_signal(df):
    # Calculate RSI
    df.ta.rsi(length=14, append=True)
    last_rsi = df['RSI_14'].iloc[-1]
    
    if last_rsi < 30: return "CALL (Oversold)"
    if last_rsi > 70: return "PUT (Overbought)"
    return "WAIT (Neutral)"

# 3. Fetch News
def get_news(symbol):
    api_key = st.secrets["NEWS_API_KEY"]
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}"
    response = requests.get(url).json()
    articles = response.get('articles', [])
    return articles[:3]

# --- UI ---
pair = st.selectbox("Select Pair", ["EURUSD", "GBPUSD", "USDJPY"])

if st.button("Get Signal & News"):
    with st.spinner("Analyzing..."):
        df = get_forex_data(pair)
        if df is not None:
            signal = generate_signal(df)
            st.subheader(f"Current Signal: {signal}")
            
            st.write("### Latest Market News:")
            for article in get_news(pair):
                st.write(f"- **{article['title']}**")
        else:
            st.error("Error fetching data. Check your API key or try again later.")
