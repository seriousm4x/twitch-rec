FROM python:slim as build
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"
COPY requirements.txt .
RUN apt-get update &&\
    apt-get install -y gcc libxml2-dev libxslt-dev python-dev zlib1g-dev &&\
    pip install --no-cache-dir -r requirements.txt

FROM python:slim
WORKDIR /app
COPY --from=build /app/venv venv
ENV PATH="/app/venv/bin:$PATH" DEBIAN_FRONTEND=noninteractive
COPY twitch-rec.py .
RUN apt-get update &&\
    apt-get install -y --no-install-recommends libxslt1.1 &&\
    apt-get clean -y

CMD ["python", "twitch-rec.py"]
