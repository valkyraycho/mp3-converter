import os
import sys
from typing import Any

import pika
from gridfs import GridFS
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from pymongo import MongoClient

from convert import to_mp3


def main() -> Any:
    client: MongoClient[dict[str, Any]] = MongoClient("mongodb", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s

    fs_videos = GridFS(db_videos)
    fs_mp3s = GridFS(db_mp3s)

    connection = pika.BlockingConnection(
        parameters=pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(
        ch: BlockingChannel,
        method: spec.Basic.Deliver,
        properties: spec.BasicProperties,
        body: bytes,
    ) -> None:
        err = to_mp3(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting form messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except Exception:
            os._exit(0)
