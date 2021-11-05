#!/usr/bin/env python3

import datetime
import json
import logging
import os
import subprocess
import time

from pathlib import Path

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
    url = "https://api.twitch.tv/helix/streams?user_login=" + streamer
    info = None
    status = 3
    try:
        headers = {
            "Client-ID": client_id,
            "Authorization": "Bearer " + oauth
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

def check_path(path):
    Path(path).mkdir(exist_ok=True)

def read_settings(_file):
    with open(_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def write_settings(_file, data):
    with open(_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def create_settings(_file):
    data = {"rec": "", "twitch": "", "pushover": ""}
    data["rec"] = {"streamer": "xxxxx", "quality": "best", "interval": 15}
    data["twitch"] = {"client_id": "xxxxx", "client_secret": "xxxxx", "oauth": ""}
    data["pushover"] = {"token": "", "user": ""}
    check_path("config/")
    with open(_file, "x", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def main():
    while True:
        settings_file = Path("config/settings.json")
        legacy_settings_file = Path("settings.json")

        #move old settings file if exists
        if legacy_settings_file.exists():
            check_path("config/")
            legacy_settings_file.replace(settings_file)

        #create settings file if needed
        if not settings_file.exists():
            create_settings(settings_file)
            exit(f"{settings_file} file created. Please replace \"xxxxx\" values by your own and restart the script")

        # read settings
        settings = read_settings(settings_file)
        try:
            settings["rec"]["streamer"]
            settings["rec"]["quality"]
            settings["twitch"]["client_id"]
            settings["twitch"]["client_secret"]
            logger.debug("Settings passed.")
        except KeyError:
            logging.error(
                "Streamer, quality, client_id and client_secret are mandatory for running the script. Please add them in the settings.json file.")
        if not settings["twitch"]["oauth"]:
            bearer = update_bearer(
                settings["twitch"]["client_id"], settings["twitch"]["client_secret"])
            if bearer:
                settings["twitch"]["oauth"] = bearer
                write_settings(settings_file, settings)
                logger.debug("Successfully created oauth token.")

        # check stream status
        status = check_stream(
            settings["rec"]["streamer"], settings["twitch"]["client_id"], settings["twitch"]["oauth"])
        if status == 401:
            logger.debug("API request unauthorized. Requesting now token.")
            bearer = update_bearer(
                settings["twitch"]["client_id"], settings["twitch"]["client_secret"])
            if bearer:
                settings["twitch"]["oauth"] = bearer
                write_settings(settings_file, settings)
                logger.debug("Successfully updated oauth token.")
            continue
        elif status == 3:
            logger.error("Unexpected error. Will try again in 5 minutes.")
            time.sleep(5*60)
            continue
        elif status == 2:
            logger.error("Streamer not found. Invalid streamer or typo.")
            time.sleep(settings["rec"]["interval"])
            continue
        elif status == 1:
            logger.info(
                f"{settings['rec']['streamer']} currently offline. Checking again in {settings['rec']['interval']} seconds.")
            time.sleep(settings["rec"]["interval"])
            continue

        # stream live
        logger.info(f"{settings['rec']['streamer']} is live. Recording ...")
        file_name = settings["rec"]["streamer"] + "_" + \
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mkv"

        if not os.path.isdir("recordings"):
            os.mkdir("recordings")
        video_file = os.path.join("recordings", file_name)

        # open stream and write to file
        cmd = ["streamlink", f"twitch.tv/{settings['rec']['streamer']}", settings['rec']['quality'],
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
        if settings["pushover"]["token"] and settings["pushover"]["user"]:
            data = {
                "token": settings["pushover"]["token"],
                "user": settings["pushover"]["user"],
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
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    log_file = os.path.join(
        "logs", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
    logger = logging.getLogger('twitch-rec')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(
        filename=log_file, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    main()
