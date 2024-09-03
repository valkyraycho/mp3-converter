import json
from typing import Any

import pika
import pika.spec
from gridfs import GridFS
from pika.adapters.blocking_connection import BlockingChannel
from werkzeug.datastructures import FileStorage


def upload(
    file: FileStorage,
    fs_video: GridFS,
    channel: BlockingChannel,
    access: dict[str, Any],
) -> tuple[str, int] | None:
    try:
        fid = fs_video.put(file)
    except Exception as e:
        print(e)
        return "internal server error from mongo", 500

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(
                {"video_fid": str(fid), "mp3_fid": None, "username": access["username"]}
            ),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        fs_video.delete(fid)
        print(e)
        return "internal server error from rabbitmq", 500

    return None
