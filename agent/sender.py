import requests
import json
from config import POST_ENDPOINT


def send_metrics(data: dict) -> bool:
    """
    Send collected metrics to FastAPI backend
    Returns True if successful, False if failed
    """
    try:
        response = requests.post(
            POST_ENDPOINT,
            json=data,                          # auto converts dict to JSON
            headers={"Content-Type": "application/json"},
            timeout=5                           # dont wait more than 5 seconds
        )

        if response.status_code == 200:
            print(f"✅ Metrics sent successfully | Status: {response.status_code}")
            return True
        else:
            print(f"⚠️ Server returned error | Status: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed — backend not reachable, will retry...")
        return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out — backend too slow")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    sample_data = {"test": "hello from agent", "status": "ok"}
    send_metrics(sample_data)
