import yfinance as yf
import os

os.makedirs("data/raw", exist_ok=True)

df = yf.download(
    "AAPL",
    start="2015-01-01",
    end="2025-12-31",
    auto_adjust=True,
    progress=False
)

# Flatten columns if needed
if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
    df.columns = df.columns.get_level_values(0)

df.to_csv("data/raw/AAPL.csv", index=True)

print(df.head())
print(df.shape)