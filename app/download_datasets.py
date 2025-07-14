import yfinance as yf
import os
from datetime import datetime
import pandas as pd

# === Configuration ===
stocks = [
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

start_date = '2000-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')
output_dir = "datasets"
today = datetime.today().strftime('%Y-%m-%d')
log_dir = "logs"
log_file = os.path.join(log_dir, f"{today}.log")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# === Logging Helper ===
def log(message):
    print(message)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

log("🟢 Dataset download started")

# === Download & Save ===
for symbol in stocks:
    log(f"⬇️ Downloading data for {symbol}...")
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        if df.empty:
            raise ValueError("No data returned")
        df.reset_index(inplace=True)
        df.to_csv(f"{output_dir}/{symbol}_daily_data.csv", index=False)
        log(f"✅ Saved {symbol} to {output_dir}/{symbol}_daily_data.csv")
    except Exception as e:
        log(f"❌ Failed to download {symbol}: {e}")

# === Clean Saved CSVs ===
for symbol in stocks:
    file_path = os.path.join(output_dir, f"{symbol}_daily_data.csv")
    if not os.path.exists(file_path):
        log(f"⚠️ File not found: {file_path}")
        continue

    try:
        df = pd.read_csv(file_path)
        if len(df) > 1:
            df = df.iloc[1:].reset_index(drop=True)
            df.to_csv(file_path, index=False)
            log(f"🧹 Cleaned first row in: {file_path}")
        else:
            log(f"⚠️ Not enough rows to clean: {file_path}")
    except Exception as e:
        log(f"❌ Failed to clean {symbol}: {e}")

log("✅ Dataset download completed\n")
