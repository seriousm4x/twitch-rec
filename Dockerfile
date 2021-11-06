FROM python:slim

WORKDIR /app

ADD requirements.txt ./
ADD twitch-rec.py ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "twitch-rec.py"]