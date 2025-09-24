import azure.functions as func
import os

SECRET = os.environ.get("HTTPHEARTBEAT_SECRET")


def main(req: func.HttpRequest) -> func.HttpRequest:
    """This is to receive Http Request from AWS Lambda.
    Auth token is pulled from the Request to verify that the Http Request is from AWS Lambda.
    If the token does not match with the secret stored in env, respond "Forbidden" with 403 status code.
    If the token matches with the secret, respond "Alive" with 200 status code.

    Args:
        req (func.HttpRequest): Http Request

    Returns:
        func.HttpRequest: Response string with status code
    """
    request_token = req.headers.get("x-auth-token")
    if request_token != SECRET:
        return func.HttpResponse("Azure response: Forbidden", status_code=403)

    return func.HttpResponse("Azure response: Alive", status_code=200)
