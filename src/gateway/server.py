import json
import os

import gridfs
import pika
import requests
from bson import ObjectId
from flask import Flask, Response, request, send_file
from flask_pymongo import PyMongo

from auth.validation import validate_token
from storage import utils

server = Flask(__name__)

mongo_videos = PyMongo(server, uri="mongodb://mongodb:27017/videos")
mongo_mp3s = PyMongo(server, uri="mongodb://mongodb:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_videos.db)
fs_mp3s = gridfs.GridFS(mongo_mp3s.db)


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
def upload() -> tuple[str, int]:
    access, err = validate_token(request)
    if err:
        return err

    assert access
    access_payload = json.loads(access)

    if access_payload["admin"]:
        if not len(request.files) == 1:
            return "exactly 1 file required", 400
        for file in request.files.values():
            err = utils.upload(file, fs_videos, channel, access_payload)
            if err:
                return err
        return "success!", 200
    else:
        return "unauthorized", 401


@server.route("/download", methods=["POST"])
def download() -> tuple[str, int] | Response:
    access, err = validate_token(request)
    if err:
        return err

    assert access
    access_payload = json.loads(access)

    if access_payload["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400
        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as e:
            print(e)
            return "internal server error", 500
    else:
        return "unauthorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
