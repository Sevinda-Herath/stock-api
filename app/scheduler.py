from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime

def run_daily_scripts():
    print(f"[{datetime.now()}] Running daily sentiment and summary generation...")
    subprocess.run(["python3", "app/generate_sentiment.py"])

scheduler = BackgroundScheduler()
scheduler.add_job(run_daily_scripts, 'cron', hour=6, minute=0)  # Adjust time
scheduler.start()
