# agent.py
import time
import signal
import sys
from config import INTERVAL_SECONDS
from metrics import collect_all_metrics
from sender import send_metrics
from logger import log_success, log_failure, log_startup, log_shutdown

# Track if agent should keep running
running = True


def handle_shutdown(signum, frame):
    """Gracefully stop agent on Ctrl+C"""
    global running
    print("\n⏹  Stopping agent...")
    log_shutdown()
    running = False
    sys.exit(0)


# Register Ctrl+C handler
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def run_agent():
    """Main loop — collect and send metrics every N seconds"""
    log_startup()
    print(f"🚀 Agent started | Sending every {INTERVAL_SECONDS} seconds")
    print(f"📡 Target: {__import__('config').POST_ENDPOINT}")
    print("Press Ctrl+C to stop\n")

    consecutive_failures = 0
    MAX_FAILURES = 5  # warn after 5 consecutive fails

    while running:
        try:
            # Step 1: Collect metrics
            metrics = collect_all_metrics()
            hostname = metrics["system"]["hostname"]

            print(f"📊 Collected | CPU: {metrics['cpu']['usage_percent']}% | "
                  f"RAM: {metrics['ram']['usage_percent']}% | "
                  f"Disk: {metrics['disk']['usage_percent']}%")

            # Step 2: Send to backend
            success = send_metrics(metrics)

            if success:
                log_success(hostname)
                consecutive_failures = 0  # reset failure count
            else:
                consecutive_failures += 1
                log_failure(f"Send failed (attempt {consecutive_failures})")

                if consecutive_failures >= MAX_FAILURES:
                    print(f"⚠️  {MAX_FAILURES} consecutive failures! Check backend.")

            # Step 3: Wait before next cycle
            time.sleep(INTERVAL_SECONDS)

        except Exception as e:
            print(f"❌ Unexpected error in main loop: {e}")
            log_failure(str(e))
            time.sleep(INTERVAL_SECONDS)  # still wait before retry


if __name__ == "__main__":
    run_agent()
