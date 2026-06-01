from backend.aws_s3 import upload_file_to_s3

files = [
    ("data/raw/AAPL.csv", "raw-data/AAPL.csv"),
    ("data/processed/AAPL_features.csv", "processed-data/AAPL_features.csv"),
    ("data/processed/AAPL_training.csv", "processed-data/AAPL_training.csv"),
    ("models/final_lstm_stock_model.keras", "models/final_lstm_stock_model.keras"),
    ("models/feature_scaler.pkl", "models/feature_scaler.pkl"),
    ("models/target_scaler.pkl", "models/target_scaler.pkl"),
]

for local_path, s3_key in files:
    result = upload_file_to_s3(local_path, s3_key)
    print(result)