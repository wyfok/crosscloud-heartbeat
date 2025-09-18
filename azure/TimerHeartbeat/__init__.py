import logging
import os
import requests
import datetime
from requests.exceptions import Timeout

AWS_ENDPOINT = os.environ.get("AWS_ENDPOINT")
SECRET = os.environ.get("HTTPHEARTBEAT_SECRET")


def main(mytimer):
    """Send out a Http Request to AWS and listen to response
    Response is logged.

    Args:
        mytimer (_type_): Timer Trigger for Azure function.
    """
    utc_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Send Http Get request to AWS Lambda with secret
    # If the status code of the response is 200, consider the request successful. Else failed.
    try:
        r = requests.get(AWS_ENDPOINT, headers={"x-auth-token": SECRET}, timeout=10)
        latency = r.elapsed.total_seconds() * 1000
        if r.status_code == 200:
            logging.info(
                f"[Azure→AWS] {utc_time} Success {r.status_code}, {latency:.2f} ms"
            )
        else:
            logging.warning(
                f"[Azure→AWS] {utc_time} Failed {r.status_code}, {latency:.2f} ms"
            )
    # Capture Timeout error
    except Timeout as e:
        logging.error(f"[Azure→AWS] {utc_time} Timeout {e}")
    # Capture all other unexpected errors.
    except Exception as e:
        logging.error(f"[Azure→AWS] {utc_time} Error {e}")
    # Log for completion
    finally:
        logging.info(f"[Azure→AWS] {utc_time} Completed.")
