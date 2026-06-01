from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from datetime import datetime

from backend.database import Base


class StockPrediction(Base):
    __tablename__ = "stock_predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticker = Column(
        String,
        nullable=False,
        index=True
    )

    latest_close = Column(
        Float,
        nullable=False
    )

    predicted_next_close = Column(
        Float,
        nullable=False
    )

    trend = Column(
        String,
        nullable=False
    )

    difference = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_name = Column(
        String,
        nullable=False
    )

    rmse = Column(
        Float
    )

    mae = Column(
        Float
    )

    r2_score = Column(
        Float
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )