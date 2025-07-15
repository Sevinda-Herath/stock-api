from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime
import csv
import os

def run_daily_scripts():
    print(f"[{datetime.now()}] Running daily dataset and sentiment update...")

    # Run the scripts
    subprocess.run(["python3", "app/download_datasets.py"])
    subprocess.run(["python3", "app/generate_sentiment.py"])
    subprocess.run(["python3", "app/save_predictions.py"])

    # Log completion
    log_file = "logs/scheduler_log.csv"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    log_entry = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Completed daily update"]

    # Write log entry
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Status"])  # header
        writer.writerow(log_entry)

    print(f"[{datetime.now()}] Daily dataset and sentiment update completed.")

# Schedule the task
scheduler = BackgroundScheduler()
scheduler.add_job(run_daily_scripts, 'cron', hour=2, minute=30)  # 01:30 AM UTC / 07:00 AM SLST
scheduler.start()
