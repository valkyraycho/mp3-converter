import datetime
import os

import jwt
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))  # type:ignore[arg-type]

mysql = MySQL(server)

JWT_SECRET = os.environ.get("JWT_SECRET")


@server.route("/login", methods=["POST"])
def login() -> str | tuple[str, int]:
    auth = request.authorization

    if not auth:
        # headers not provided
        return "missing credentials", 401

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT password FROM user WHERE email=%s", (auth.username,))

    if res > 0:
        user = cur.fetchone()
        password = user[0]
        if auth.password != password:
            return "invalid credentials", 401
        else:
            return create_jwt(auth.username, JWT_SECRET, True)  # type:ignore[arg-type]
    else:
        # user does not exist in the database
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate() -> tuple[str, int]:
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded_jwt = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as e:
        print(e)
        return "not authorized", 403
    return decoded_jwt, 200


def create_jwt(username: str, secret: str, is_auth: bool) -> str:
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": is_auth,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
