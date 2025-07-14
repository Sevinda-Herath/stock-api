from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import os
from datetime import datetime

import app.scheduler  # ensures the daily scheduler runs

app = FastAPI()
TODAY = datetime.today().strftime("%Y-%m-%d")

@app.get("/")
def root():
    return {"message": "Stock Prediction API is running."}

@app.get("/sentiment_summary/{symbol}")
def get_summary(symbol: str):
    file_path = f"summary/{TODAY}/{symbol.upper()}_summary.csv"
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "Summary not found"}, status_code=404)
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")[0]

@app.get("/sentiment_chart/{symbol}")
def get_chart(symbol: str):
    chart_path = f"charts/{TODAY}/{symbol.upper()}_chart.png"
    if os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/png")
    return JSONResponse(content={"error": "Chart not found"}, status_code=404)

@app.get("/predict/lstm")
def predict_price(symbol: str = Query(...), days: int = Query(60)):
    from app.predict_lstm import predict_lstm_price
    try:
        price = predict_lstm_price(symbol.upper(), days)
        return {
            "symbol": symbol.upper(),
            "predicted_price": float(round(price, 2))  # Fix: convert numpy.float32 to float
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/predict/lstm_sentiment")
def predict_price_sentiment(symbol: str = Query(...), days: int = Query(60)):
    from app.predict_lstm_sentiment import predict_lstm_sentiment_price
    try:
        price = predict_lstm_sentiment_price(symbol.upper(), days)
        return {
            "symbol": symbol.upper(),
            "predicted_price": float(round(price, 2))  # Fix: convert numpy.float32 to float
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
