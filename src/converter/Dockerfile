FROM python:3.12-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \ 
    build-essential ffmpeg \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . .

CMD [ "python3", "consumer.py" ]