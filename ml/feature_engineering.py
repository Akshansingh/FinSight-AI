import pandas as pd
import ta
import os

# Load Dataset
df = pd.read_csv("data/raw/AAPL.csv")

# Clean Columns
df.columns = [col.strip() for col in df.columns]

# Technical Indicators

# RSI
df["RSI"] = ta.momentum.RSIIndicator(
    close=df["Close"],
    window=14
).rsi()

# MACD
df["MACD"] = ta.trend.MACD(
    close=df["Close"]
).macd()

# Bollinger Bands
bb = ta.volatility.BollingerBands(
    close=df["Close"],
    window=20
)

df["BB_High"] = bb.bollinger_hband()
df["BB_Low"] = bb.bollinger_lband()

# Moving Averages
df["SMA_20"] = df["Close"].rolling(20).mean()
df["SMA_50"] = df["Close"].rolling(50).mean()

# Exponential Moving Average
df["EMA_20"] = df["Close"].ewm(span=20).mean()

# Daily Returns
df["Daily_Return"] = df["Close"].pct_change()

# Volatility
df["Volatility"] = df["Daily_Return"].rolling(20).std()

# Remove Null Values
df.dropna(inplace=True)

os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    "data/processed/AAPL_features.csv",
    index=False
)

print(df.head())
print(df.shape)