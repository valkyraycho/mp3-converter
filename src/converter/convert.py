import json
import os
import tempfile

import moviepy
import moviepy.editor
import pika
import pika.spec
from bson import ObjectId
from gridfs import GridFS
from pika.adapters.blocking_connection import BlockingChannel


def to_mp3(
    msg: bytes, fs_videos: GridFS, fs_mp3s: GridFS, channel: BlockingChannel
) -> str | None:
    message = json.loads(msg)

    with tempfile.NamedTemporaryFile() as tf:
        tf.write(fs_videos.get(ObjectId(message["video_fid"])).read())
        audio = moviepy.editor.VideoFileClip(tf.name).audio

    tf_path = tempfile.gettempdir() + f"/{message["video_fid"]}.mp3"
    audio.write_audiofile(tf_path)

    with open(tf_path, "rb") as f:
        fid = fs_mp3s.put(f.read())
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        fs_mp3s.delete(fid)
        print(e)
        return "failed to publish message"

    return None
