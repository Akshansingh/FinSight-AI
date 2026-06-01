from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.aws_s3 import upload_file_to_s3
from sqlalchemy.orm import Session

import numpy as np
import joblib
import yfinance as yf
import ta

from tensorflow.keras.models import load_model

from backend.database import engine, get_db
from backend.models import Base, StockPrediction

# Create database tables
Base.metadata.create_all(bind=engine)

# Load ML model and scalers
model = load_model("models/final_lstm_stock_model.keras")
feature_scaler = joblib.load("models/feature_scaler.pkl")
target_scaler = joblib.load("models/target_scaler.pkl")

app = FastAPI(
    title="FinSight AI",
    description="AI-powered stock forecasting API using LSTM, FastAPI, and PostgreSQL",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FEATURES = [
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


@app.get("/")
def home():
    return {
        "message": "FinSight AI API Running",
        "docs": "http://127.0.0.1:8000/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "loaded",
        "database": "connected"
    }


@app.get("/predict/latest/{ticker}")
def predict_latest(
    ticker: str,
    db: Session = Depends(get_db)
):
    try:
        ticker = ticker.upper().strip()

        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No data found for ticker"
            )

        if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        df.reset_index(inplace=True)

        # Feature engineering
        df["RSI"] = ta.momentum.RSIIndicator(
            df["Close"],
            window=14
        ).rsi()

        df["MACD"] = ta.trend.MACD(
            df["Close"]
        ).macd()

        bb = ta.volatility.BollingerBands(
            df["Close"],
            window=20,
            window_dev=2
        )

        df["BB_High"] = bb.bollinger_hband()
        df["BB_Low"] = bb.bollinger_lband()

        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["Daily_Return"] = df["Close"].pct_change()
        df["Volatility"] = df["Daily_Return"].rolling(window=20).std()

        df.dropna(inplace=True)

        if len(df) < 60:
            raise HTTPException(
                status_code=400,
                detail="Not enough historical data for prediction"
            )

        latest_sequence = df[FEATURES].tail(60)

        scaled_sequence = feature_scaler.transform(latest_sequence)

        X = np.array([scaled_sequence])

        prediction_scaled = model.predict(X, verbose=0)

        predicted_price = target_scaler.inverse_transform(
            prediction_scaled
        )[0][0]

        latest_close = float(df["Close"].iloc[-1])
        predicted_price = float(predicted_price)

        difference = predicted_price - latest_close
        percentage_change = (difference / latest_close) * 100

        trend = "Bullish" if difference > 0 else "Bearish"

        confidence = max(
            0,
            min(
                100,
                100 - abs(percentage_change)
            )
        )

        saved_prediction = StockPrediction(
            ticker=ticker,
            latest_close=round(latest_close, 2),
            predicted_next_close=round(predicted_price, 2),
            trend=trend,
            difference=round(difference, 2)
        )

        db.add(saved_prediction)
        db.commit()
        db.refresh(saved_prediction)

        return {
            "id": saved_prediction.id,
            "ticker": ticker,
            "latest_close": round(latest_close, 2),
            "predicted_next_close": round(predicted_price, 2),
            "trend": trend,
            "difference": round(difference, 2),
            "percentage_change": round(percentage_change, 2),
            "confidence": round(confidence, 2),
            "message": "Prediction saved successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/predictions/history")
def prediction_history(db: Session = Depends(get_db)):
    predictions = (
        db.query(StockPrediction)
        .order_by(StockPrediction.created_at.desc())
        .limit(20)
        .all()
    )

    return predictions


@app.get("/predictions/history/{ticker}")
def prediction_history_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
):
    ticker = ticker.upper().strip()

    predictions = (
        db.query(StockPrediction)
        .filter(StockPrediction.ticker == ticker)
        .order_by(StockPrediction.created_at.desc())
        .limit(20)
        .all()
    )

    return predictions
    
@app.get("/stock/history/{ticker}")
def stock_history(ticker: str):

    ticker = ticker.upper().strip()

    df = yf.download(
        ticker,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No stock history found"
        )

    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    df.reset_index(inplace=True)

    data = []

    for _, row in df.tail(120).iterrows():
        data.append(
            {
                "date": str(row["Date"])[:10],
                "close": round(float(row["Close"]), 2)
            }
        )

    return data


@app.post("/cloud/backup")
    
def cloud_backup():
    files = [
        ("data/raw/AAPL.csv", "raw-data/AAPL.csv"),
        ("data/processed/AAPL_features.csv", "processed-data/AAPL_features.csv"),
        ("data/processed/AAPL_training.csv", "processed-data/AAPL_training.csv"),
        ("models/final_lstm_stock_model.keras", "models/final_lstm_stock_model.keras"),
        ("models/feature_scaler.pkl", "models/feature_scaler.pkl"),
        ("models/target_scaler.pkl", "models/target_scaler.pkl"),
    ]

    results = []

    for local_path, s3_key in files:
        result = upload_file_to_s3(local_path, s3_key)
        results.append(result)

    return {
        "message": "Cloud backup completed",
        "results": results
    }

@app.get("/analytics/dashboard")

def analytics_dashboard(db: Session = Depends(get_db)):

    total_predictions = db.query(StockPrediction).count()

    bullish_predictions = (
        db.query(StockPrediction)
        .filter(StockPrediction.trend == "Bullish")
        .count()
    )

    bearish_predictions = (
        db.query(StockPrediction)
        .filter(StockPrediction.trend == "Bearish")
        .count()
    )

    most_tracked = (
        db.query(
            StockPrediction.ticker
        )
        .all()
    )

    ticker_count = {}

    for row in most_tracked:
        ticker = row[0]
        ticker_count[ticker] = ticker_count.get(ticker, 0) + 1

    most_predicted_stock = (
        max(ticker_count, key=ticker_count.get)
        if ticker_count
        else "N/A"
    )

    return {
        "total_predictions": total_predictions,
        "bullish_predictions": bullish_predictions,
        "bearish_predictions": bearish_predictions,
        "most_predicted_stock": most_predicted_stock
    }