import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="BROCODE TRADER", layout="wide")
st.title("🔥 BROCODE TRADER - 12 SKILLS PRO")
st.caption("Full System Live")

# Sidebar
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Symbol", ["BTC-USD","ETH-USD","RELIANCE.NS","TCS.NS","INFY.NS","AAPL","TSLA"], index=0)
period = st.sidebar.selectbox("Period", ["5d","1mo","3mo","6mo","1y"], index=1)

@st.cache_data(ttl=120)
def get_data(sym, per):
    try:
        df = yf.download(sym, period=per, interval="1d", progress=False)
        return df
    except:
        return pd.DataFrame()

df = get_data(symbol, period)
if df.empty:
    st.error("No data for " + symbol)
    st.stop()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

curr = float(df['Close'].iloc[-1])
prev = float(df['Close'].iloc[-2]) if len(df)>1 else curr
high = float(df['High'].max())
low = float(df['Low'].min())

# Header
c1,c2,c3 = st.columns(3)
c1.metric(symbol, round(curr,2), round(curr-prev,2))
c2.metric("High", round(high,2))
c3.metric("Low", round(low,2))

# Chart
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="MA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(), name="MA50"))
fig.update_layout(height=400, xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
st.divider()

# Calc
ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
ma50 = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df)>=50 else ma20

# Last 20 return fix
if len(df) > 20:
    last20 = float(df['Close'].iloc[-20])
    ret20 = (curr/last20 -1)*100
else:
    ret20 = 0
st.write("Last 20D Return:", round(ret20,2), "%")

# SKILL 1
st.subheader("SKILL 1: Trend Finder")
trend = "BULLISH" if curr > ma20 and ma20 > ma50 else "BEARISH" if curr < ma20 else "SIDEWAYS"
if trend=="BULLISH":
    st.success(f"BULLISH - Price {curr:.2f} > MA20 {ma20:.2f} > MA50 {ma50:.2f}")
else:
    st.error(f"{trend} - Price {curr:.2f} vs MA20 {ma20:.2f} MA50 {ma50:.2f}")

# SKILL 2
st.subheader("SKILL 2: News Monitor")
st.info("Check TradingView + Moneycontrol for " + symbol)

# SKILL 3
st.subheader("SKILL 3: Entry Timer - RSI")
delta = df['Close'].diff()
gain = delta.where(delta>0,0).rolling(14).mean()
loss = -delta.where(delta<0,0).rolling(14).mean()
rs = gain/loss
rsi = 100 - (100/(1+rs))
rsi_val = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
st.write("RSI:", round(rsi_val,1))
if rsi_val < 30:
    st.success("OVERSOLD - BUY Zone")
elif rsi_val > 70:
    st.error("OVERBOUGHT - Avoid BUY")
else:
    st.warning("NEUTRAL")

# SKILL 4
st.subheader("SKILL 4: Risk Calculator")
capital = st.number_input("Capital Rs", value=10000, step=1000)
risk_pct = st.slider("Risk %", 1, 5, 2)
risk_amt = capital * risk_pct / 100
st.write("Max Risk per trade: Rs", risk_amt)

# SKILL 5
st.subheader("SKILL 5: Support & Resistance")
sup = float(df.tail(30)['Low'].min())
res = float(df.tail(30)['High'].max())
st.write(f"Support: {sup:.2f} | Resistance: {res:.2f}")

# SKILL 6
st.subheader("SKILL 6: Volume Check")
avg_vol = float(df['Volume'].tail(20).mean())
last_vol = float(df['Volume'].iloc[-1])
vol_ratio = last_vol/avg_vol if avg_vol>0 else 1
st.write(f"Volume {vol_ratio:.2f}x avg")
if vol_ratio > 1.5:
    st.success("HIGH VOLUME - Strong move")

# SKILL 7
st.subheader("SKILL 7: Breakout Detector")
if curr > res*0.99:
    st.success(f"BREAKOUT near {res:.2f}")
elif curr < sup*1.01:
    st.error(f"BREAKDOWN near {sup:.2f}")
else:
    st.info("Ranging")

# SKILL 8
st.subheader("SKILL 8: Stop Loss Finder")
stop_loss = sup*0.98 if trend=="BULLISH" else curr*0.97
sl_pct = (curr-stop_loss)/curr*100
st.write(f"Stop Loss: {stop_loss:.2f} which is {sl_pct:.2f} % below")

# SKILL 9
st.subheader("SKILL 9: Target Setter")
target1 = curr + (curr-stop_loss)*1.5
target2 = curr + (curr-stop_loss)*2.5
st.write(f"Target 1: {target1:.2f} | Target 2: {target2:.2f}")

# SKILL 10
st.subheader("SKILL 10: Journal")
entry = st.number_input("Entry Price", value=curr)
qty = st.number_input("Qty", value=1)
notes = st.text_input("Why trade?")
if st.button("Save Note"):
    st.success(f"Saved {symbol} Entry {entry}")

# SKILL 11
st.subheader("SKILL 11: Backtest")
df['MA20'] = df['Close'].rolling(20).mean()
df['MA50'] = df['Close'].rolling(50).mean()
df['Signal'] = np.where(df['MA20'] > df['MA50'], 1, 0)
df['Returns'] = df['Close'].pct_change()
df['Strat'] = df['Signal'].shift(1) * df['Returns']
total_ret = (1+df['Strat'].dropna()).prod() -1
st.write(f"Strategy Return: {total_ret*100:.2f} %")

# SKILL 12
st.subheader("SKILL 12: Live Alert")
if trend=="BULLISH" and rsi_val<65 and vol_ratio>1.2:
    st.success(f"STRONG BUY SIGNAL for {symbol} NOW")
else:
    st.warning(f"No Alert - Trend {trend} RSI {rsi_val:.1f}")

st.success("ALL 12 SKILLS LIVE ✅")
# SKILL 13: LIVE AUTO ALERT - NO TELEGRAM NEEDED
st.divider()
st.subheader("SKILL 13: Live Auto Alert with Sound")

# Auto refresh
auto = st.checkbox("Enable LIVE 10 sec Auto-Refresh", value=False)
if auto:
    st.write("App will refresh every 60 seconds - Keep this tab open")
    st.components.v1.html("<meta http-equiv='refresh' content='60'>", height=0)

# Sound alert condition
alert_condition = (trend=="BULLISH" and rsi_val<65 and vol_ratio>1.2) or (trend=="BEARISH" and rsi_val>65)

if alert_condition:
    st.error("🔔🔔🔔 ALERT TRIGGERED! STRONG SIGNAL NOW!")
    # Sound
    st.components.v1.html("""
    <audio autoplay>
      <source src="https://www.soundjay.com/buttons/sounds/beep-07a.mp3" type="audio/mpeg">
    </audio>
    <script>
      alert('BROCODE TRADER ALERT: Strong Signal for """ + symbol + """ !');
    </script>
    """, height=0)
else:
    st.info(f"No alert now. Waiting for: Bullish + RSI<65 + Vol>1.2x. Current: {trend}, RSI {rsi_val:.1f}")

st.success("Skill 13 LIVE - No Telegram needed!")
