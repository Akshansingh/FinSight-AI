import pandas as pd

df = pd.read_csv("data/raw/AAPL.csv")

print(df.head())
print(df.shape)
print(df.columns)