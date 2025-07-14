import os
import requests
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re

# === Configuration Section ===
NEWS_API_KEY = 'e3762f837b5d4677a8fc78db2fdc0d2f'  # Replace with your NewsAPI key
date_str = datetime.today().strftime('%Y-%m-%d')

# Create output directories
sentiment_dir = os.path.join("sentiment", date_str)
chart_dir = os.path.join("charts", date_str)
summary_dir = os.path.join("summary", date_str)
os.makedirs(sentiment_dir, exist_ok=True)
os.makedirs(chart_dir, exist_ok=True)
os.makedirs(summary_dir, exist_ok=True)

# === Stock Symbol => Query Mapping ===
stock_queries = {
    'AAPL': 'Apple Inc',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc',
    'AMZN': 'Amazon.com Inc',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc',
    'TSLA': 'Tesla Inc',
    'BRK-B': 'Berkshire Hathaway Inc',
    'UNH': 'UnitedHealth Group Incorporated',
    'JPM': 'JPMorgan Chase & Co'
}

# === Load FinBERT Model for Sentiment Analysis ===
print("Loading FinBERT model...")
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# === Helper Function to Clean Text ===
def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# === Loop Through Each Stock to Fetch News and Analyze Sentiment ===
for symbol, query in stock_queries.items():
    print(f"\nFetching news for {symbol} using query: {query}")
    all_articles = []

    for i in range(7):
        day = datetime.today() - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')

        url = (
            f"https://newsapi.org/v2/everything?q={query}&from={day_str}&to={day_str}"
            f"&sortBy=publishedAt&pageSize=14&apiKey={NEWS_API_KEY}&language=en"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
        except Exception as e:
            print(f"Error fetching news for {symbol} on {day_str}: {e}")
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
        print(f"No valid news articles found for {symbol}.")
        continue

    texts = [f"{a['title']}. {a['description']}" for a in all_articles]
    try:
        results = sentiment_pipeline(texts)
    except Exception as e:
        print(f"Sentiment analysis failed for {symbol}: {e}")
        continue

    df = pd.DataFrame(all_articles)
    df["sentiment"] = [r["label"] for r in results]
    df["confidence"] = [r["score"] for r in results]

    csv_path = os.path.join(sentiment_dir, f"{symbol}_sentiment.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved sentiment CSV to {csv_path}")

    plt.figure(figsize=(6, 4))
    df["sentiment"].value_counts().plot(kind='bar', color=["green", "red", "gray"])
    plt.title(f"Sentiment for {symbol} News (Last 7 Days, 14/Day)")
    plt.xlabel("Sentiment")
    plt.ylabel("Number of Articles")
    plt.xticks(rotation=0)
    plt.tight_layout()

    chart_path = os.path.join(chart_dir, f"{symbol}_chart.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Saved sentiment chart to {chart_path}")

# === Final Summary Output ===
all_summaries = []

for symbol in stock_queries:
    csv_file = os.path.join(sentiment_dir, f"{symbol}_sentiment.csv")
    if not os.path.exists(csv_file):
        continue

    df = pd.read_csv(csv_file)
    if df.empty:
        continue

    sentiment_counts = df["sentiment"].value_counts().to_dict()
    avg_confidence = df.groupby("sentiment")["confidence"].mean().to_dict()

    summary_data = {
        "date_collected": date_str,
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
    summary_file_path = os.path.join(summary_dir, f"{symbol}_summary.csv")
    summary_df.to_csv(summary_file_path, index=False)
    print(f"📁 Saved individual summary: {summary_file_path}")

    all_summaries.append(summary_data)

# Save combined summary
if all_summaries:
    combined_df = pd.DataFrame(all_summaries)
    combined_path = os.path.join(summary_dir, "all_symbols_summary.csv")
    combined_df.to_csv(combined_path, index=False)
    print(f"\n📊 Combined summary saved to: {combined_path}")
else:
    print("⚠️ No data available to write combined summary.")

# === Final Log Messages ===
print(f"\n✅ All sentiment CSVs saved in: {sentiment_dir}")
print(f"✅ All sentiment charts saved in: {chart_dir}")
print(f"✅ All summary files saved in: {summary_dir}")