def predict_lstm_sentiment_price(symbol, time_steps):
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    from datetime import datetime
    import os

    today = datetime.today().strftime('%Y-%m-%d')
    model_path = f"models/{symbol}_best_model.h5"
    sentiment_path = f"sentiment/{today}/{symbol}_sentiment.csv"
    stock_path = f"datasets/{symbol}_daily_data.csv"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not os.path.exists(sentiment_path):
        raise FileNotFoundError(f"Sentiment file not found: {sentiment_path}")
    if not os.path.exists(stock_path):
        raise FileNotFoundError(f"Stock data file not found: {stock_path}")

    model = load_model(model_path)
    stock_df = pd.read_csv(stock_path)
    stock_df['Date'] = pd.to_datetime(stock_df['Date'])

    sentiment_df = pd.read_csv(sentiment_path)
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df['sentiment_score'] = sentiment_df['sentiment'].map({'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0})

    daily_sentiment = sentiment_df.groupby('date')['sentiment_score'].mean().reset_index()
    daily_sentiment.columns = ['Date', 'Sentiment']

    merged_df = pd.merge(stock_df[['Date', 'Close']], daily_sentiment, on='Date', how='left')
    merged_df['Sentiment'].fillna(0, inplace=True)

    if len(merged_df) < time_steps:
        raise ValueError("Not enough data for time steps")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(merged_df[['Close', 'Sentiment']])
    last_sequence = scaled[-time_steps:]
    last_sequence = np.expand_dims(last_sequence, axis=0)

    scaled_prediction = model.predict(last_sequence)
    combined = np.concatenate([scaled_prediction, np.zeros_like(scaled_prediction)], axis=1)
    predicted_price = scaler.inverse_transform(combined)[0][0]
    return predicted_price
