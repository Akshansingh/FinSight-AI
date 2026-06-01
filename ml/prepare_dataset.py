import pandas as pd
import os

# Load feature engineered data
df = pd.read_csv("data/processed/AAPL_features.csv")

# Target = Next day's closing price
df["Target"] = df["Close"].shift(-1)

# Remove last row (Target becomes NaN)
df.dropna(inplace=True)

os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    "data/processed/AAPL_training.csv",
    index=False
)

print("Training Dataset Created Successfully")
print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())