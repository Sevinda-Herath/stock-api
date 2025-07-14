def predict_lstm_price(symbol, time_steps):
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    from datetime import datetime
    import os

    model_path = f"models/lstm/{symbol}_best_model.h5"
    data_path = f"datasets/{symbol}_daily_data.csv"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Stock data file not found: {data_path}")

    model = load_model(model_path)

    df = pd.read_csv(data_path)
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
