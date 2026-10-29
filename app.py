import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="BROCODE TRADER", layout="wide", page_icon="🔥")
st.title("🔥 BROCODE TRADER - 12 SKILLS PRO")
st.caption("Full System Live")

# Sidebar
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.selectbox("Symbol", ["BTC-USD","ETH-USD","RELIANCE.NS","TCS.NS","INFY.NS","AAPL","TSLA","NIFTY","BANKNIFTY"], index=0)
period = st.sidebar.selectbox("Period", ["5d","1mo","3mo","6mo","1y"], index=1)

@st.cache_data(ttl=120)
def get_data(sym, per):
    try:
        df = yf.download(sym, period=per, interval="1d", progress=False)
        if len(df) == 0:
            df = yf.download(sym, period=per, progress=False)
        return df
    except:
        return pd.DataFrame()

df = get_data(symbol, period)
if df.empty:
    st.error(f"No data for {symbol}")
    st.stop()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

curr = float(df['Close'].iloc[-1])
prev = float(df['Close'].iloc[-2]) if len(df)>1 else curr
high = float(df['High'].max())
low = float(df['Low'].min())

# Price Header
c1,c2,c3,c4 = st.columns(4)
c1.metric(f"{symbol}", f"{curr:.2f}", f"{curr-prev:.2f}")
c2.metric("High", f"{high:.2f}")
c3.metric("Low", f"{low:.2f}")
c4.metric("Last 20D Return", f"{((curr/float(df['Close'].iloc[-20]) -1)*100) if len(df)>20 else 0):.2f}%")

# Chart
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="MA20", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(), name="MA50", line=dict(color="blue")))
fig.update_layout(height=450, xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# SKILL 1
st.subheader("SKILL 1: Trend Finder")
ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
ma50 = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df)>=50 else ma20
trend = "BULLISH" if curr > ma20 and ma20 > ma50 else "BEARISH" if curr < ma20 else "SIDEWAYS"
if trend=="BULLISH":
    st.success(f"✅ {trend} - Price {curr:.2f} > MA20 {ma20:.2f} > MA50 {ma50:.2f}")
else:
    st.error(f"⚠️ {trend} - Price {curr:.2f} vs MA20 {ma20:.2f} MA50 {ma50:.2f}")

# SKILL 2
st.subheader("SKILL 2: News Monitor")
st.info(f"Check: TradingView + Moneycontrol for {symbol}. News impact = Volatility today. If news = positive + bullish trend = STRONG BUY")

# SKILL 3
st.subheader("SKILL 3: Entry Timer - RSI")
delta = df['Close'].diff()
gain = delta.where(delta>0,0).rolling(14).mean()
loss = -delta.where(delta<0,0).rolling(14).mean()
rs = gain/loss
rsi = 100 - (100/(1+rs))
rsi_val = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
st.write(f"RSI (14): {rsi_val:.1f}")
if rsi_val < 30:
    st.success("OVERSOLD - Good BUY zone")
elif rsi_val > 70:
    st.error("OVERBOUGHT - Avoid BUY, wait for dip")
else:
    st.warning("NEUTRAL - Wait for breakout")

# SKILL 4
st.subheader("SKILL 4: Risk Calculator")
capital = st.number_input("Capital Rs", value=10000, step=1000)
risk_pct = st.slider("Risk %", 1, 5, 2)
risk_amt = capital * risk_pct / 100
st.write(f"Max Risk per trade: Rs {risk_amt}")

# SKILL 5
st.subheader("SKILL 5: Support & Resistance")
recent = df.tail(30)
sup = float(recent['Low'].min())
res = float(recent['High'].max())
st.write(f"Support: {sup:.2f} | Resistance: {res:.2f}")
st.write(f"Entry near Support, Exit near Resistance. Current distance to Support: {((curr-sup)/curr*100):.2f}%")

# SKILL 6
st.subheader("SKILL 6: Volume Check")
avg_vol = float(df['Volume'].tail(20).mean())
last_vol = float(df['Volume'].iloc[-1])
vol_ratio = last_vol/avg_vol if avg_vol>0 else 1
st.write(f"Last Volume: {last_vol:.0f} vs Avg 20D: {avg_vol:.0f} = {vol_ratio:.2f}x")
if vol_ratio > 1.5:
    st.success("HIGH VOLUME - Strong move confirmed")
else:
    st.warning("LOW VOLUME - Weak move, be careful")

# SKILL 7
st.subheader("SKILL 7: Breakout Detector")
if curr > res*0.99:
    st.success(f"🚀 BREAKOUT - Price {curr:.2f} near Resistance {res:.2f} - BUY momentum")
elif curr < sup*1.01:
    st.error(f"💥 BREAKDOWN - Price near Support {sup:.2f} - Risk of fall")
else:
    st.info(f"No Breakout - Ranging between {sup:.2f} - {res:.2f}")

# SKILL 8
st.subheader("SKILL 8: Stop Loss Finder")
stop_loss = sup*0.98 if trend=="BULLISH" else curr*0.97
sl_pct = (curr-stop_loss)/curr*100
st.write(f"Suggested Stop Loss: {stop_loss:.2f} ({sl_pct:.2f}% below)")

# SKILL 9
st.subheader("SKILL 9: Target Setter")
target1 = curr + (curr-stop_loss)*1.5
target2 = curr + (curr-stop_loss)*2.5
st.write(f"Target 1 (1.5x): {target1:.2f} | Target 2 (2.5x): {target2:.2f}")
st.write(f"Risk Reward = 1 : 1.5 and 1 : 2.5 - Risk Rs {curr-stop_loss:.2f} to gain Rs {target1-curr:.2f}")

# SKILL 10
st.subheader("SKILL 10: Journal")
with st.expander("Add Today's Trade"):
    entry = st.number_input("Entry Price", value=curr)
    qty = st.number_input("Qty", value=1)
    notes = st.text_input("Why you took trade?")
    if st.button("Save Trade Note"):
        st.success(f"Saved: {symbol} Entry {entry} Qty {qty} - {notes} (Demo save)")

# SKILL 11
st.subheader("SKILL 11: Backtest (Simple MA Crossover)")
df['MA20'] = df['Close'].rolling(20).mean()
df['MA50'] = df['Close'].rolling(50).mean()
df['Signal'] = np.where(df['MA20'] > df['MA50'], 1, 0)
df['Returns'] = df['Close'].pct_change()
df['Strat'] = df['Signal'].shift(1) * df['Returns']
total_ret = (1+df['Strat'].dropna()).prod() -1
buy_hold = (curr / float(df['Close'].iloc[0]) -1)
st.write(f"Strategy Return (MA20>MA50): {total_ret*100:.2f}% vs Buy Hold: {buy_hold*100:.2f}%")

# SKILL 12
st.subheader("SKILL 12: Live Alert")
if trend=="BULLISH" and rsi_val<65 and vol_ratio>1.2:
    st.success(f"🔔 LIVE ALERT: STRONG BUY SIGNAL for {symbol} NOW! All conditions green")
else:
    st.warning(f"No Alert now. Conditions: Trend={trend}, RSI={rsi_val:.1f}, Vol={vol_ratio:.1f}x")

st.success("✅ ALL 12 SKILLS LIVE")
