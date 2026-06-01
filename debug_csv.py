import pandas as pd

df = pd.read_csv("data/raw/AAPL.csv")

print("COLUMNS:")
print(df.columns.tolist())

print("\nFIRST 10 ROWS:")
print(df.head(10))

print("\nDTYPES:")
print(df.dtypes)