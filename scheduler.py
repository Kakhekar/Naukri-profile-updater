"""
Scheduler — runs the Naukri updater at a set interval.
Default: every 24 hours. Change INTERVAL_HOURS as needed.
"""

import schedule
import time
from naukri_updater import run

INTERVAL_HOURS = 24  # How often to update (in hours)


def job():
    print(f"\n{'='*40}")
    print("Running scheduled Naukri profile update...")
    print('='*40)
    try:
        run()
    except Exception as e:
        print(f"Update failed: {e}")


if __name__ == "__main__":
    print(f"Scheduler started. Will update every {INTERVAL_HOURS} hour(s).")
    print("Press Ctrl+C to stop.\n")

    # Run immediately on start
    job()

    # Then schedule repeating runs
    schedule.every(INTERVAL_HOURS).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
