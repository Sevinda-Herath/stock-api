import os
import pandas as pd
from datetime import datetime
from app.predict_lstm import predict_lstm_price
from app.predict_lstm_sentiment import predict_lstm_sentiment_price

# === Setup ===
symbols = [
    "AMZN",        # Amazon
    "AAPL",        # Apple
    "GOOGL",       # Alphabet (Class A)
    "005930.KS",   # Samsung Electronics
    "2317.TW",     # Foxconn (Taiwan)
    "MSFT",        # Microsoft
    "JD",          # JD.com
    "BABA",        # Alibaba
    "T",           # AT&T
    "META"         # Meta (Facebook)
]
time_steps = 60
today = datetime.today().strftime('%Y-%m-%d')

# Directories
result_dir = os.path.join("results", today)
log_dir = "logs"
log_file = os.path.join(log_dir, f"{today}.log")
os.makedirs(result_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Logging Helper
def log(message):
    print(message)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

log(f"🟢 Prediction job started for {today}")

# === Store Results in Memory ===
lstm_predictions = []
lstm_senti_predictions = []

for symbol in symbols:
    log(f"🔍 Predicting {symbol}...")

    try:
        price_lstm = predict_lstm_price(symbol, time_steps)
        lstm_predictions.append({
            "symbol": symbol,
            "predicted_price": round(price_lstm, 2),
            "date": today
        })
        log(f"✅ {symbol} LSTM Prediction: ${price_lstm:.2f}")
    except Exception as e:
        lstm_predictions.append({
            "symbol": symbol,
            "predicted_price": None,
            "date": today,
            "error": str(e)
        })
        log(f"❌ {symbol} LSTM Error: {e}")

    try:
        price_lstm_sent = predict_lstm_sentiment_price(symbol, time_steps)
        lstm_senti_predictions.append({
            "symbol": symbol,
            "predicted_price": round(price_lstm_sent, 2),
            "date": today
        })
        log(f"✅ {symbol} LSTM+Sentiment Prediction: ${price_lstm_sent:.2f}")
    except Exception as e:
        lstm_senti_predictions.append({
            "symbol": symbol,
            "predicted_price": None,
            "date": today,
            "error": str(e)
        })
        log(f"❌ {symbol} LSTM+Sentiment Error: {e}")

# === Save Combined CSVs ===
df_lstm = pd.DataFrame(lstm_predictions)
df_lstm_senti = pd.DataFrame(lstm_senti_predictions)

df_lstm.to_csv(os.path.join(result_dir, "lstm.csv"), index=False)
df_lstm_senti.to_csv(os.path.join(result_dir, "lstm_senti.csv"), index=False)

log(f"✅ Combined results saved to: {result_dir}/lstm.csv and lstm_senti.csv")
log("🛑 Prediction job completed.\n")
