# logger.py
import logging
import os
from datetime import datetime

# Create logs folder if not exists
os.makedirs("logs", exist_ok=True)

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/agent.log"),   # save to file
        logging.StreamHandler()                   # also print to terminal
    ]
)

logger = logging.getLogger("SystemAgent")


def log_success(hostname: str):
    logger.info(f"✅ Metrics sent successfully from {hostname}")


def log_failure(reason: str):
    logger.error(f"❌ Failed to send metrics | Reason: {reason}")


def log_startup():
    logger.info("🚀 System Monitor Agent started")


def log_shutdown():
    logger.info("🛑 System Monitor Agent stopped")
