import os
import time
import random
from datetime import datetime
from utils.apis.get_classes import get_classes
from utils.apis.cancel_class import cancel_class
from utils.helper import get_undetected_driver
from utils.automation import (
    capture_jwt_token, login,
    navigate_to_class_listings
)


SCHEDULE_INTERVAL_SECONDS = 24 * 60 * 60


def run_every_24_hours():
    print("Starting scheduled automation (runs every 24 hours)")
    run_count = 0

    while True:
        run_count += 1
        start = time.time()

        print(f"\n{'=' * 50}")
        print(f"SCHEDULED RUN #{run_count}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")

        try:
            main()
        except Exception as e:
            print(f"Unhandled error in scheduled run #{run_count}: {e}")

        # --- Timing Logic ---
        elapsed = time.time() - start
        remaining = SCHEDULE_INTERVAL_SECONDS - elapsed

        if remaining > 0:
            next_run_timestamp = time.time() + remaining
            next_run_time = datetime.fromtimestamp(next_run_timestamp).strftime('%Y-%m-%d %H:%M:%S')

            print(f"Run #{run_count} completed in {elapsed:.1f}s")
            print(f"Next run scheduled for: {next_run_time}")

            # Converted log to show Hours instead of Minutes for clarity
            print(f"Waiting {remaining / 3600:.2f} hours...")

            time.sleep(remaining)
        else:
            print(f"Run #{run_count} took {elapsed:.1f}s (>= 12 hours). Starting next run immediately.")


def main():
    page_number = 0
    driver = get_undetected_driver(headless=True)
    try:
        login(driver)
        navigate_to_class_listings(driver)
        jwt_token = capture_jwt_token(driver)
        if driver:
            print("JWT token captured successfully.")
            driver.quit()
        while True:
            islast_page, classes = get_classes(page_number, jwt_token)
            if classes:
                print(f"Found {len(classes)} classes on page {page_number + 1}.")
                for classId in classes:
                    cancel_class(classId, jwt_token)
            else:
                print(f"Classes on page {page_number + 1} are already cancelled.")
            print(f"{'-'*50}\nFinished processing page {page_number + 1}.\n{'-'*50}")
            page_number += 1
            time.sleep(random.randint(1, 3))
            if islast_page:
                print("All pages processed.")
                break

    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    run_every_24_hours()
