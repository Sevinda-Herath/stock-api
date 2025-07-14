def predict_lstm_price(symbol, time_steps):
    import yfinance as yf
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    from datetime import datetime, timedelta
    import os

    model_path = f"models/{symbol}_best_model.h5"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found for {symbol}")

    model = load_model(model_path)

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=time_steps * 2)).strftime('%Y-%m-%d')

    df = yf.download(symbol, start=start_date, end=end_date)
    df = df[['Close']].dropna()

    if len(df) < time_steps:
        raise ValueError("Not enough data")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df.values)
    last_sequence = scaled[-time_steps:]
    last_sequence = np.expand_dims(last_sequence, axis=0)

    scaled_pred = model.predict(last_sequence)
    predicted_price = scaler.inverse_transform(scaled_pred)[0][0]
    return predicted_price
