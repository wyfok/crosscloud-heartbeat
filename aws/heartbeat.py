import logging
import os
import json
import datetime
import urllib3

SECRET = os.environ.get("HTTPHEARTBEAT_SECRET")
AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")

http = urllib3.PoolManager()


def receiving_heartbeat(event: dict, context) -> dict:
    """This is to receive Http Request from Azure Function.
    Auth token is pulled from the Request to verify that the Http Request is from Azure Function.
    If the token does not match with the secret stored in env, respond "Forbidden" with 403 status code.
    If the token matches with the secret, respond "Alive" with 200 status code.

    Args:
        event (dict): Dict containing the Lambda function event data
        context : Lambda runtime context

    Returns:
        dict: Dict containing status message
    """
    header = event.get("headers", {})
    token = header.get("x-auth-token")

    if token != SECRET:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "AWS Response: Forbidden"}),
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "AWS Response: Alive"}),
        }


def sending_heartbeat(event: dict, context):
    """Send out a Http Request to Azure Endpoint and listen to response
    Response is logged.

    Args:
        event (_type_): Dict containing the Lambda function event data
        context (_type_): Lambda runtime context

    Returns:
        _type_: Dict containing status message
    """
    utc_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r = http.request(
            "GET", AZURE_ENDPOINT, headers={"x-auth-token": SECRET}, timeout=10.0
        )
        latency = r.headers.get("x-response-time-ms")
        if latency is None:
            # fallback if Azure does not set custom header
            latency = "N/A"

        if r.status == 200:
            logging.info(
                f"[AWS→Azure] {utc_time} Success {r.status}, latency {latency}"
            )
        else:
            logging.warning(
                f"[AWS→Azure] {utc_time} Failed {r.status}, latency {latency}"
            )

    except urllib3.exceptions.TimeoutError as e:
        logging.error(
            json.dumps(
                {
                    "direction": "AWS→Azure",
                    "timestamp": utc_time,
                    "error": "timeout",
                    "detail": str(e),
                }
            )
        )
    except Exception as e:
        logging.error(
            json.dumps(
                {
                    "direction": "AWS→Azure",
                    "timestamp": utc_time,
                    "error": "exception",
                    "detail": str(e),
                }
            )
        )
    finally:
        logging.info(
            json.dumps(
                {"direction": "AWS→Azure", "timestamp": utc_time, "result": "completed"}
            )
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Execution completed", "timestamp": utc_time}),
    }


def lambda_handler(event, context):
    # Receiving heartbeat
    if "httpMethod" in event and event["httpMethod"] == "GET":
        return receiving_heartbeat(event, context)
    # Sending heartbeat
    else:
        return sending_heartbeat(event, context)
