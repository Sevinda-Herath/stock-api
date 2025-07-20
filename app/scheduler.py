from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from datetime import datetime
import csv
import os

LOG_FILE = "logs/scheduler_log.csv"

def write_log(status):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status])

def run_daily_scripts():
    print(f"[{datetime.now()}] Running daily dataset and sentiment update...")
    write_log("Started daily update")

    try:
        subprocess.run(["python3", "app/download_datasets.py"], check=True)
        subprocess.run(["python3", "app/generate_sentiment.py"], check=True)
        subprocess.run(["python3", "app/save_predictions.py"], check=True)
        write_log("Completed daily update")
        print(f"[{datetime.now()}] Daily update completed.")
    except subprocess.CalledProcessError as e:
        write_log(f"Daily update failed: {e}")
        print(f"[{datetime.now()}] Daily update failed: {e}")

def run_git_sync():
    print(f"[{datetime.now()}] Starting Git sync...")
    write_log("Started Git sync")

    try:
        subprocess.run(["git", "pull"], check=True)

        # Check for changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m",
                f"Auto update: datasets and sentiment ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            ], check=True)
            subprocess.run(["git", "push"], check=True)
            write_log("Git commit and push completed")
            print(f"[{datetime.now()}] Git commit and push completed.")
        else:
            write_log("No changes to commit")
            print(f"[{datetime.now()}] No changes to commit.")
    except subprocess.CalledProcessError as e:
        write_log(f"Git sync failed: {e}")
        print(f"[{datetime.now()}] Git sync failed: {e}")

# Schedule the tasks
scheduler = BackgroundScheduler()
scheduler.add_job(run_daily_scripts, 'cron', hour=2, minute=30)  # 02:30 UTC
scheduler.add_job(run_git_sync, 'cron', hour=3, minute=43)        # 03:00 UTC
scheduler.start()
