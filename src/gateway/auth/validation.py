import os

import requests
from flask import Request


def validate_token(request: Request) -> tuple[str | None, tuple[str, int] | None]:
    if "Authorization" not in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)

    token_response = requests.post(
        url=f"http://{os.environ.get("AUTH_SVC_ADDRESS")}/validate",
        headers={"Authorization": token},
    )

    if token_response.status_code != 200:
        return None, (token_response.text, token_response.status_code)

    return token_response.text, None
