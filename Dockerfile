FROM python:slim as build
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update &&\
    apt-get install -y gcc libxml2-dev libxslt-dev python-dev zlib1g-dev &&\
    pip install --user --no-cache-dir -r requirements.txt

FROM python:slim
WORKDIR /app
COPY --from=build /root/.local /root/.local
COPY twitch-rec.py .
RUN apt-get update &&\
    apt-get install -y --no-install-recommends libxslt1.1 &&\
    apt-get clean -y
ENV DEBIAN_FRONTEND=noninteractive PATH=/root/.local/bin:$PATH

CMD ["python", "twitch-rec.py"]
