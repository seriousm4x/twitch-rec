FROM python:slim

WORKDIR /app

ADD requirements.txt ./
ADD twitch-rec.py ./

RUN pip install -r requirements.txt

# to store videos and config files
VOLUME [ "/app/recordings", "/app/config" ]

ENTRYPOINT [ "python", "twitch-rec.py" ]