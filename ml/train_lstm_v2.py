import os
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# Load Dataset
# =========================

df = pd.read_csv("data/processed/AAPL_training.csv")

print("Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())

# =========================
# Features and Target
# =========================

features = [
    "Close",
    "Volume",
    "RSI",
    "MACD",
    "BB_High",
    "BB_Low",
    "SMA_20",
    "SMA_50",
    "EMA_20",
    "Daily_Return",
    "Volatility"
]

target = "Target"

df = df.dropna(subset=features + [target])

# =========================
# Scale Features and Target
# =========================

feature_scaler = MinMaxScaler()
target_scaler = MinMaxScaler()

scaled_features = feature_scaler.fit_transform(df[features])
scaled_target = target_scaler.fit_transform(df[[target]])

# =========================
# Create Sequences
# =========================

X = []
y = []

window_size = 60

for i in range(window_size, len(scaled_features)):
    X.append(scaled_features[i - window_size:i])
    y.append(scaled_target[i][0])

X = np.array(X)
y = np.array(y)

print("X Shape:", X.shape)
print("y Shape:", y.shape)

# =========================
# Train-Test Split
# =========================

split = int(len(X) * 0.8)

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# =========================
# Build Improved LSTM Model
# =========================

model = Sequential([
    Input(shape=(X_train.shape[1], X_train.shape[2])),

    Bidirectional(
        LSTM(
            units=128,
            return_sequences=True
        )
    ),

    Dropout(0.3),

    LSTM(
        units=64,
        return_sequences=False
    ),

    Dropout(0.3),

    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(1)
])

model.compile(
    optimizer="adam",
    loss="mse"
)

model.summary()

# =========================
# Callbacks
# =========================

os.makedirs("models", exist_ok=True)

checkpoint = ModelCheckpoint(
    "models/best_lstm_stock_model.keras",
    monitor="val_loss",
    save_best_only=True,
    mode="min",
    verbose=1
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=8,
    restore_best_weights=True,
    verbose=1
)

# =========================
# Train
# =========================

history = model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=[checkpoint, early_stop],
    verbose=1
)

# =========================
# Predict
# =========================

scaled_predictions = model.predict(X_test)

predictions = target_scaler.inverse_transform(scaled_predictions)
actual = target_scaler.inverse_transform(y_test.reshape(-1, 1))

# =========================
# Evaluation
# =========================

rmse = np.sqrt(mean_squared_error(actual, predictions))
mae = mean_absolute_error(actual, predictions)
r2 = r2_score(actual, predictions)

print("\nModel Evaluation")
print("RMSE:", rmse)
print("MAE:", mae)
print("R2:", r2)

# =========================
# Save Final Model and Scalers
# =========================

model.save("models/final_lstm_stock_model.keras")

joblib.dump(feature_scaler, "models/feature_scaler.pkl")
joblib.dump(target_scaler, "models/target_scaler.pkl")

print("\nFiles Saved:")
print("models/final_lstm_stock_model.keras")
print("models/best_lstm_stock_model.keras")
print("models/feature_scaler.pkl")
print("models/target_scaler.pkl")