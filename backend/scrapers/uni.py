import os
import subprocess
import sys
import time
import logging
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────
INTERVAL_DAYS = 15          # Change to run more/less often
LOG_FILE = "scraper_schedule.log"
# ────────────────────────────────────────────────────────

folder = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger()


def run_all_scrapers():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    log.info("=" * 50)
    log.info("Starting all scrapers (UTF-8 safe)...")
    log.info("=" * 50)

    success_count = 0
    fail_count = 0

    for file in sorted(os.listdir(folder)):
        if file.endswith(".py") and file not in {"uni.py", "__init__.py"}:
            path = os.path.join(folder, file)
            log.info(f"Running {file} ...")
            try:
                result = subprocess.run(
                    [sys.executable, path],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    log.info(result.stdout.strip())
                log.info(f"✓ {file} done\n")
                success_count += 1
            except subprocess.CalledProcessError as e:
                log.error(f"✗ {file} failed!\n{e.stderr}\n")
                fail_count += 1

    log.info(f"All scrapers finished! ✓ {success_count} passed, ✗ {fail_count} failed")
    log.info("=" * 50)


def main():
    log.info(f"Scheduler started — scrapers will run every {INTERVAL_DAYS} days.")
    log.info("Press Ctrl+C to stop.\n")

    # Run immediately on first start
    run_all_scrapers()

    while True:
        next_run = datetime.now() + timedelta(days=INTERVAL_DAYS)
        log.info(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Sleep in 60s chunks so Ctrl+C works cleanly
        total_seconds = INTERVAL_DAYS * 24 * 60 * 60
        for _ in range(total_seconds // 60):
            time.sleep(60)

        log.info("Interval reached — running scrapers now...")
        run_all_scrapers()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("\nScheduler stopped by user.")