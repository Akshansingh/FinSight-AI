import os
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Load Data
df = pd.read_csv("data/processed/AAPL_training.csv")

print("Available Columns:")
print(df.columns.tolist())

# Feature columns
possible_features = [
    "Close",
    "Volume",
    "RSI",
    "MACD",
    "MACD_Signal",
    "BB_High",
    "BB_Low",
    "BB_Mid",
    "SMA_20",
    "SMA_50",
    "EMA_20",
    "Daily_Return",
    "Volatility"
]

# Use only columns that exist
features = [col for col in possible_features if col in df.columns]

print("\nFeatures Used:")
print(features)

target = "Target"

if target not in df.columns:
    raise ValueError("Target column not found. Run: python ml/prepare_dataset.py")

# Remove missing values
df = df.dropna(subset=features + [target])

# Scale features
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(df[features])

# Create LSTM sequences
X = []
y = []

window_size = 60

for i in range(window_size, len(scaled_features)):
    X.append(scaled_features[i - window_size:i])
    y.append(df[target].iloc[i])

X = np.array(X)
y = np.array(y)

print("\nX Shape:", X.shape)
print("y Shape:", y.shape)

# Train-test split
split = int(len(X) * 0.8)

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# Build LSTM Model
model = Sequential()

model.add(
    LSTM(
        units=100,
        return_sequences=True,
        input_shape=(X_train.shape[1], X_train.shape[2])
    )
)

model.add(Dropout(0.2))

model.add(
    LSTM(
        units=100,
        return_sequences=False
    )
)

model.add(Dropout(0.2))

model.add(Dense(50, activation="relu"))
model.add(Dense(1))

model.compile(
    optimizer="adam",
    loss="mse"
)

model.summary()

# Train model
history = model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# Predictions
predictions = model.predict(X_test)

# Evaluation
rmse = np.sqrt(mean_squared_error(y_test, predictions))
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\nModel Evaluation")
print("RMSE:", rmse)
print("MAE:", mae)
print("R2:", r2)

# Save model
os.makedirs("models", exist_ok=True)

model.save("models/lstm_stock_model.h5")

print("\nModel Saved Successfully at models/lstm_stock_model.h5")