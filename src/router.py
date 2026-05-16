import json
from http import HTTPStatus

from services.redirect_service import RedirectService


def route(event):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        code = (event.get("pathParameters") or {}).get("codigo")
        return RedirectService().redirect(code)

    return {
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Method not allowed"}),
    }
