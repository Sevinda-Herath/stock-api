import yfinance as yf
import os
from datetime import datetime
import pandas as pd

# === Configuration ===
stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'META', 'TSLA', 'BRK-B', 'UNH', 'JPM'
]
start_date = '2000-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')
output_dir = "datasets"
os.makedirs(output_dir, exist_ok=True)

# === Download & Save ===
for symbol in stocks:
    print(f"⬇️ Downloading data for {symbol}...")
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        if df.empty:
            raise ValueError("No data returned")
        df.reset_index(inplace=True)
        df.to_csv(f"{output_dir}/{symbol}_daily_data.csv", index=False)
        print(f"✅ Saved {symbol} to {output_dir}/{symbol}_daily_data.csv")
    except Exception as e:
        print(f"❌ Failed to download {symbol}: {e}")

# === Clean Saved CSVs (Optional: Remove first row) ===
for symbol in stocks:
    file_path = os.path.join(output_dir, f"{symbol}_daily_data.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        continue

    try:
        df = pd.read_csv(file_path)
        if len(df) > 1:
            df = df.iloc[1:].reset_index(drop=True)
            df.to_csv(file_path, index=False)
            print(f"🧹 Cleaned: {file_path}")
        else:
            print(f"⚠️ Not enough rows to clean: {file_path}")
    except Exception as e:
        print(f"❌ Failed to clean {symbol}: {e}")
