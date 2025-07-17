import os
import requests
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/stock-api/.env.settings")

# === Configuration Section ===
 
NEWS_API_KEY = os.getenv("API_KEY")

def get_current_date():
    """Always return the current date to avoid caching issues"""
    return datetime.today().strftime('%Y-%m-%d')

date_str = get_current_date()

# Output directories
sentiment_dir = os.path.join("sentiments/sentiment", date_str)
chart_dir = os.path.join("sentiments/charts", date_str)
summary_dir = os.path.join("sentiments/summary", date_str)
log_dir = "logs"
log_file = os.path.join(log_dir, f"{date_str}.log")

os.makedirs(sentiment_dir, exist_ok=True)
os.makedirs(chart_dir, exist_ok=True)
os.makedirs(summary_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Logging Helper
def log(message):
    print(message)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

log("🟢 Sentiment analysis job started")

# === Stock Symbol => Query Mapping ===
stock_queries = symbols = {
    'AMZN':'Amazon',
    'AAPL':'Apple',
    'GOOGL':'Google',
    '005930.KS':'Samsung',
    '2317.TW':'Foxconn ',
    'MSFT':'Microsoft',
    'JD':'JD.com',
    'BABA':'Alibaba',
    'T':'AT&T',
    'META':'Meta'
}

# === Load FinBERT Model ===
log("🔄 Loading FinBERT model...")
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
log("✅ FinBERT model loaded")

# === Helper Function to Clean Text ===
def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# === Fetch News & Analyze Sentiment ===
for symbol, query in stock_queries.items():
    log(f"\n🔍 Fetching news for {symbol}...")
    all_articles = []

    for i in range(7):
        day = datetime.today() - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        url = (
            f"https://newsapi.org/v2/everything?q={query}&from={day_str}&to={day_str} - {date_str}"
            f"&sortBy=publishedAt&pageSize=14&apiKey={NEWS_API_KEY}&language=en"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
        except Exception as e:
            log(f"❌ Error fetching news for {symbol} on {day_str}: {e}")
            continue

        for article in articles:
            if not article.get("publishedAt"):
                continue
            title = clean_text(article.get("title", ""))
            description = clean_text(article.get("description", ""))
            if title:
                all_articles.append({
                    "date": article["publishedAt"][:10],
                    "title": title,
                    "description": description
                })

    if not all_articles:
        log(f"⚠️ No valid news articles found for {symbol}.")
        continue

    texts = [f"{a['title']}. {a['description']}" for a in all_articles]
    try:
        results = sentiment_pipeline(texts)
    except Exception as e:
        log(f"❌ Sentiment analysis failed for {symbol}: {e}")
        continue

    df = pd.DataFrame(all_articles)
    df["sentiment"] = [r["label"].lower() for r in results]
    df["confidence"] = [r["score"] for r in results]

    csv_path = os.path.join(sentiment_dir, f"{symbol}_sentiment.csv")
    df.to_csv(csv_path, index=False)
    log(f"✅ Saved sentiment CSV: {csv_path}")

    # Chart
    try:
        plt.figure(figsize=(6, 4))
        df["sentiment"].value_counts().plot(kind='bar', color=["green", "red", "gray"])
        plt.title(f"Sentiment for {symbol} News (Last 7 Days, 14/Day) ")
        plt.xlabel("Sentiment")
        plt.ylabel("Number of Articles")
        plt.xticks(rotation=0)
        plt.tight_layout()
        chart_path = os.path.join(chart_dir, f"{symbol}_chart.png")
        plt.savefig(chart_path)
        plt.close()
        log(f"📊 Saved chart: {chart_path}")
    except Exception as e:
        log(f"❌ Failed to generate chart for {symbol}: {e}")

# === Final Summary Output ===
all_summaries = []

for symbol in stock_queries:
    csv_file = os.path.join(sentiment_dir, f"{symbol}_sentiment.csv")
    if not os.path.exists(csv_file):
        log(f"⚠️ Missing sentiment file for {symbol}, skipping summary")
        continue

    df = pd.read_csv(csv_file)
    if df.empty:
        log(f"⚠️ Empty sentiment file for {symbol}")
        continue

    sentiment_counts = df["sentiment"].value_counts().to_dict()
    avg_confidence = df.groupby("sentiment")["confidence"].mean().to_dict()

    summary_data = {
        "date_collected": get_current_date(),
        "symbol": symbol,
        "total_articles": len(df),
        "positive_count": sentiment_counts.get("positive", 0),
        "neutral_count": sentiment_counts.get("neutral", 0),
        "negative_count": sentiment_counts.get("negative", 0),
        "avg_confidence_positive": round(avg_confidence.get("positive", 0), 4),
        "avg_confidence_neutral": round(avg_confidence.get("neutral", 0), 4),
        "avg_confidence_negative": round(avg_confidence.get("negative", 0), 4),
    }

    summary_df = pd.DataFrame([summary_data])
    summary_path = os.path.join(summary_dir, f"{symbol}_summary.csv")
    summary_df.to_csv(summary_path, index=False)
    log(f"📁 Saved summary for {symbol}: {summary_path}")
    all_summaries.append(summary_data)

# === Save combined summary ===
if all_summaries:
    combined_df = pd.DataFrame(all_summaries)
    combined_path = os.path.join(summary_dir, "all_symbols_summary.csv")
    combined_df.to_csv(combined_path, index=False)
    log(f"\n📊 Combined summary saved to: {combined_path}")
else:
    log("⚠️ No data available to write combined summary.")

# === Final Log Message ===
log(f"\n✅ Sentiment analysis completed for all stocks on {get_current_date()}")
