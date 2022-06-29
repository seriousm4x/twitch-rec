#!/usr/bin/env python3

import datetime
import logging
import os
import subprocess
import time

import requests
import streamlink


def update_bearer(client_id, client_secret):
    tokenurl = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    try:
        token_response = requests.post(tokenurl)
        token_response.raise_for_status()
        token_json_response = token_response.json()
        bearer = token_json_response["access_token"]
        return bearer
    except Exception as e:
        logger.error(e)


def check_stream(streamer, client_id, oauth):
    # Check if user online, 0: online, 1: offline, 2: not found, 3: error
    url = f"https://api.twitch.tv/helix/streams?user_login={streamer}"
    info = None
    status = 3
    try:
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {oauth}"
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        info = r.json()

        if info.get("status") == 401:
            status = 401
        elif info["data"][0]["type"] == "live":
            status = 0

    except requests.exceptions.RequestException as e:
        logger.error(e)
        if e.response:
            if e.response.reason == "Not Found" or e.response.reason == "Unprocessable Entity":
                status = 2
    except requests.exceptions.HTTPError:
        status = 401
    except IndexError:
        status = 1

    return status


def main():
    env_streamer = os.environ.get("STREAMER")
    env_quality = os.environ.get("QUALITY")
    env_interval = int(os.environ.get("INTERVAL"))
    env_client_id = os.environ.get("CLIENT_ID")
    env_client_secret = os.environ.get("CLIENT_SECRET")
    env_pu_token = os.environ.get("PUSHOVER_TOKEN")
    env_pu_user = os.environ.get("PUSHOVER_USER")
    bearer = update_bearer(env_client_id, env_client_secret)

    while True:
        # check stream status
        status = check_stream(env_streamer, env_client_id, bearer)
        if status == 401:
            logger.debug("API request unauthorized. Requesting now token.")
            bearer = update_bearer(env_client_id, env_client_secret)
            if bearer:
                logger.debug("Successfully updated oauth token.")
            continue
        elif status == 3:
            logger.error("Unexpected error. Will try again in 5 minutes.")
            time.sleep(5*60)
            continue
        elif status == 2:
            logger.error("Streamer not found. Invalid streamer or typo.")
            time.sleep(env_interval)
            continue
        elif status == 1:
            logger.info(
                f"{env_streamer} currently offline. Checking again in {env_interval} seconds.")
            time.sleep(env_interval)
            continue

        # stream live
        logger.info(f"{env_streamer} is live. Recording ...")
        file_name = env_streamer + "_" + \
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mkv"

        video_file = os.path.join("recordings", file_name)

        # open stream and write to file
        cmd = ["streamlink", f"twitch.tv/{env_streamer}", env_quality,
               "--twitch-disable-hosting", "--twitch-disable-ads", "--twitch-disable-reruns", "-o", video_file]
        p = subprocess.Popen(cmd, universal_newlines=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = p.stdout.readline()
            if output == "" and p.poll() is not None:
                break
            if output:
                logger.info(output.strip())

        # send pushover message
        if env_pu_token and env_pu_user:
            data = {
                "token": env_pu_token,
                "user": env_pu_user,
                "html": "1",
                "message": f"Recorded: {file_name}"
            }
            r = requests.post(
                "https://api.pushover.net/1/messages.json", data=data)
            r.raise_for_status()
            if r.status_code == 200:
                logger.info("Pushover message sent.")
            else:
                logger.info("Pushover message failed.")

        # Wait for twitch api to refresh
        logger.info("Waiting 5 minutes for the twitch api to refresh...")
        time.sleep(5*60)


if __name__ == "__main__":
    # setup logging
    logger = logging.getLogger('twitch-rec')
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    main()
