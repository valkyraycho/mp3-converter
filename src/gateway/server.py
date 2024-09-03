import json
import os
from typing import Any

import gridfs
import pika
import requests
from flask import Flask, request
from flask_pymongo import PyMongo

from auth.validation import validate_token
from storage import utils

server = Flask(__name__)

mongo_video = PyMongo(server, uri="mongodb://mongodb:27017/videos")

fs_video = gridfs.GridFS(mongo_video.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login() -> str | tuple[str, int]:
    auth = request.authorization

    if not auth:
        return "missing credentials", 401

    login_response = requests.post(
        url=f"http://{os.environ.get("AUTH_SVC_ADDRESS")}/login",
        auth=(auth.username, auth.password),
    )

    if login_response.status_code != 200:
        return login_response.text, login_response.status_code

    return login_response.text


@server.route("/upload", methods=["POST"])  # type:ignore[type-var]
def upload() -> tuple[str, int] | None:
    access, err = validate_token(request)

    if err:
        return err

    assert access
    access_payload = json.loads(access)

    if access_payload["admin"]:
        if not len(request.files) == 1:
            return "exactly 1 file required", 400
        for file in request.files.values():
            err = utils.upload(file, fs_video, channel, access_payload)
            if err:
                return err
        return None
    else:
        return "unauthorized", 401


@server.route("/download", methods=["POST"])
def download() -> Any: ...


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
