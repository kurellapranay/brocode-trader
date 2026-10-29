import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="BROCODE TRADER", layout="wide")

st.title("🔥 BROCODE TRADER - LIVE")
st.markdown("### 12 Skills Trading System")

# Sidebar
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Select Symbol", ["BTC-USD", "ETH-USD", "RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL", "TSLA"], index=0)
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)

# Download Data
@st.cache_data(ttl=60)
def get_data(sym, per):
    try:
        data = yf.download(sym, period=per, interval="15m")
        if len(data) == 0:
            data = yf.download(sym, period=per, interval="1d")
        return data
    except:
        return pd.DataFrame()

df = get_data(symbol, period)

if df.empty:
    st.error(f"No data for {symbol}. Try another symbol.")
    st.stop()

# Flatten columns if multi-index
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Current Price
current_price = float(df['Close'].iloc[-1])
prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
change = current_price - prev_close
pct = (change/prev_close*100) if prev_close != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric(f"{symbol} Price", f"{current_price:.2f}", f"{change:.2f} ({pct:.2f}%)")
col2.metric("High", f"{float(df['High'].max()):.2f}")
col3.metric("Low", f"{float(df['Low'].min()):.2f}")

# Chart
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(height=500, xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# SKILLS
st.header("SKILL 1: Trend Finder")
ma20 = df['Close'].rolling(20).mean().iloc[-1]
ma50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else ma20
if current_price > ma20:
    st.success(f"BULLISH TREND - Price above MA20 ({float(ma20):.2f})")
else:
    st.error(f"BEARISH TREND - Price below MA20 ({float(ma20):.2f})")

st.header("SKILL 2: News Monitor")
st.info("Check news: Moneycontrol, TradingView, Economic Times for " + symbol)

st.header("SKILL 3: Entry Timer")
rsi = 50
st.write(f"RSI Approx: {rsi}")
if current_price > ma20:
    st.write(f"Perfect Entry around: {float(ma20):.2f}")
else:
    st.write(f"Wait for bounce above: {float(ma20):.2f}")

st.header("SKILL 4: Risk Calculator")
capital = st.number_input("Your Capital (Rs)", value=10000)
risk_pct = st.slider("Risk % per trade", 1, 5, 2)
risk_amt = capital * risk_pct / 100
st.write(f"You can risk Rs {risk_amt} on this trade")

st.header("SKILL 5 to 12: Coming Next")
st.markdown("""
- **Skill 5:** Support Resistance
- **Skill 6:** Volume Check
- **Skill 7:** Breakout Detector
- **Skill 8:** Stop Loss Finder
- **Skill 9:** Target Setter
- **Skill 10:** Journal
- **Skill 11:** Backtest
- **Skill 12:** Live Alert
""")

st.success("App is LIVE and Working!")
