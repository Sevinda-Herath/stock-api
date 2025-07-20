from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import subprocess
from datetime import datetime
import csv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path="/home/stock-api/.env.settings")
GIT_TOKEN = os.getenv("GIT_TOKEN")

# Constants
LOG_FILE = "logs/scheduler_log.csv"
GIT_REPO = f"https://{GIT_TOKEN}@github.com/Sevinda-Herath/stock-api.git"

def write_log(status: str):
    """Append a log entry to the CSV log file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status])

def run_command(command: list[str], label: str):
    """Run a subprocess command and handle errors."""
    try:
        subprocess.run(command, check=True)
        write_log(f"{label} completed")
    except subprocess.CalledProcessError as e:
        write_log(f"{label} failed: {e}")
        raise

def run_daily_scripts():
    """Run the daily update pipeline."""
    print(f"[{datetime.now()}] Running daily dataset and sentiment update...")
    write_log("Started daily update")

    try:
        run_command(["python3", "app/download_datasets.py"], "Download datasets")
        run_command(["python3", "app/generate_sentiment.py"], "Generate sentiment")
        run_command(["python3", "app/save_predictions.py"], "Save predictions")
        print(f"[{datetime.now()}] Daily update completed.")
    except subprocess.CalledProcessError:
        print(f"[{datetime.now()}] Daily update failed.")

def run_git_sync():
    """Sync local changes with remote GitHub repo."""
    print(f"[{datetime.now()}] Starting Git sync...")
    write_log("Started Git sync")

    try:
        subprocess.run(["git", "pull"], check=True)

        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():  # Changes exist
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m",
                f"Auto update: datasets and sentiment ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            ], check=True)

            # Set the token-based repo URL temporarily
            subprocess.run(["git", "remote", "set-url", "origin", GIT_REPO], check=True)
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
scheduler.add_job(run_git_sync, 'cron', hour=4, minute=18)       # 03:43 UTC
scheduler.start()

print(f"[{datetime.now()}] Scheduler started and running in background.")
