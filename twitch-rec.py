#!/usr/bin/env python3

import datetime
import getopt
import http.client
import json
import logging
import os
import requests
import subprocess
import sys
import textwrap
import time
import urllib


class Colorlog():
    logging.basicConfig(
        format='[\033[1;32m%(asctime)s\033[1;0m] [%(levelname)s] %(message)s', level=logging.WARNING)
    logging.addLevelName(
        logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(
        logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(
        logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))


class Config():
    def __init__(self):
        self.json_streamer = ""
        self.json_quality = ""
        self.json_tw_client_id = ""
        self.json_tw_oauth_token = ""
        self.json_po_token = ""
        self.json_po_user = ""

        self.cli_streamer = ""
        self.cli_quality = ""
        self.cli_tw_client_id = ""
        self.cli_tw_oauth_token = ""
        self.cli_po_token = ""
        self.cli_po_user = ""

    def write_json(self, data, jsonfile):
        with open(jsonfile, "w+") as self.cf:
            json.dump(data, self.cf, indent=4, separators=(',', ': '))

    def read_json(self):
        with open(config_file, "r") as self.cf:
            return json.load(self.cf)

    def cli(self):
        # Create config if it doesn't exist
        if not os.path.isfile(config_file):
            self.create_config("", "", "", "", "", "")
        # Load current config
        self.data = self.read_json()
        self.json_streamer = self.data["rec"]["streamer"]
        self.json_quality = self.data["rec"]["quality"]
        self.json_tw_client_id = self.data["twitch"]["client_id"]
        self.json_tw_oauth_token = self.data["twitch"]["oauth"]
        self.json_po_token = self.data["pushover"]["token"]
        self.json_po_user = self.data["pushover"]["user"]

        # Read cli args
        self.opts = getopt.getopt(sys.argv[1:], 'hs:q:c:o:t:u:', [
                                  'streamer=', 'quality='])[0]
        for self.opt, self.arg in self.opts:
            if self.opt in ('-h', '--help'):
                print(textwrap.dedent("""

                    Usage: python3 twitch_rec.py [OPTION] [ARG]

                    -h, --help        Shows instructions about this script
                    -s, --streamer    Specifies the twitch streamer to record
                    -q, --quality     Specifies the quality of the livestream
                    -c, --client-id   Specifies the twitch client id. Create one here: https://dev.twitch.tv/dashboard/apps
                    -o, --oauth       Specifies the twitch oauth token. Create one with "streamlink --twitch-oauth-authenticate"
                    -t, --pu-token    Specifies the pushover app token. Create one at pushover.net
                    -u, --pu-user     Specifies the pushover user key. Create one at pushover.net

                    Running the script without cli arguments will ask you for all the settings and will create a json config file for you.
                    If you already have one, it will read the configs from there.

                """))
                sys.exit(0)
            elif self.opt in ('-s', '--streamer'):
                self.cli_streamer = self.arg
            elif self.opt in ('-q', '--quality'):
                self.cli_quality = self.arg
            elif self.opt in ('-c', '--client-id'):
                self.cli_tw_client_id = self.arg
            elif self.opt in ('-o', '--oauth'):
                self.cli_tw_oauth_token = self.arg
            elif self.opt in ('-t', '--pu-token'):
                self.cli_po_token = self.arg
            elif self.opt in ('-u', '--pu-user'):
                self.cli_po_user = self.arg

        # Set streamer
        if not self.cli_streamer:
            if not self.json_streamer:
                self.streamer = input(
                    "Which streamer do you want to record?: ")
            else:
                self.streamer = self.json_streamer
        else:
            self.streamer = self.cli_streamer

        # Set quality
        if not self.cli_quality:
            if not self.json_quality:
                self.quality = input(
                    "In which quality do you want to record? (If you dont know, just type \"best\"): ")
            else:
                self.quality = self.json_quality
        else:
            self.quality = self.cli_quality

        # Set twitch client id
        if not self.cli_tw_client_id:
            if not self.json_tw_client_id:
                self.tw_client_id = input("What is your twitch client id?: ")
            else:
                self.tw_client_id = self.json_tw_client_id
        else:
            self.tw_client_id = self.cli_tw_client_id

        # Set twitch oauth token
        if not self.cli_tw_oauth_token:
            if not self.json_tw_oauth_token:
                self.tw_oauth_token = input(
                    "What is your twitch oauth token?: ")
            else:
                self.tw_oauth_token = self.json_tw_oauth_token
        else:
            self.tw_oauth_token = self.cli_tw_oauth_token

        # Set pushover token
        if not self.cli_po_token:
            if not self.json_po_token:
                self.po_token = input("What is your pushover token?: ")
            else:
                self.po_token = self.json_po_token
        else:
            self.po_token = self.cli_po_token

        # Set pushover user
        if not self.cli_po_user:
            if not self.json_po_user:
                self.po_user = input("What is your pushover user?: ")
            else:
                self.po_user = self.json_po_user
        else:
            self.po_user = self.cli_po_user

        return self.streamer, self.quality, self.tw_client_id, self.tw_oauth_token, self.po_token, self.po_user

    def create_config(self, streamer, quality, tw_client_id, tw_oauth_token, po_token, po_user):
        data = {
            "rec": {
                "streamer": streamer,
                "quality": quality
            },
            "twitch": {
                "client_id": tw_client_id,
                "oauth": tw_oauth_token
            },
            "pushover": {
                "token": po_token,
                "user": po_user
            }}
        self.write_json(data, config_file)


class TwitchRecorder:
    def __init__(self):
        self.refresh = 15.0
        self.root_path = os.path.dirname(os.path.realpath(__file__))

        # Read final config
        self.data = Config().read_json()
        self.streamer = self.data["rec"]["streamer"]
        self.quality = self.data["rec"]["quality"]
        self.tw_client_id = self.data["twitch"]["client_id"]
        self.tw_oauth_token = self.data["twitch"]["oauth"]
        self.po_token = self.data["pushover"]["token"]
        self.po_user = self.data["pushover"]["user"]

    def run(self):
        # Set recording path
        self.rec_path = os.path.join(self.root_path, "recs")
        if(os.path.isdir(self.rec_path) == False):
            os.makedirs(self.rec_path)

        # Check interval
        if(self.refresh < 15):
            logging.warning(
                "Interval should not be lower than 15 seconds.")
            logging.warning("Interval will be set to 15 seconds.")
            self.refresh = 15

        # Start loop
        logging.info("Checking for " + self.streamer + " every " + str(self.refresh) +
                     " seconds. Recording in " + self.quality + " quality.")
        self.loopcheck()

    def check_user(self):
        # Check if user online, 0: online, 1: offline, 2: not found, 3: error
        self.url = "https://api.twitch.tv/helix/streams?user_login=" + self.streamer
        self.info = None
        self.status = 3
        try:
            self.r = requests.get(
                self.url, headers={"Client-ID": self.tw_client_id,
                                   "Authorization": "Bearer " + self.tw_oauth_token}, timeout=15)
            self.r.raise_for_status()
            self.info = self.r.json()
            try:
                if self.info["data"][0]["type"] == "live":
                    self.status = 0
            except IndexError:
                self.status = 1
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.reason == "Not Found" or e.response.reason == "Unprocessable Entity":
                    self.status = 2
        return self.status

    def loopcheck(self):
        while True:
            # Status messages
            status = self.check_user()
            if status == 3:
                logging.error("Unexpected error. Will try again in 5 minutes.")
                time.sleep(300)
            elif status == 2:
                logging.error("streamer not found. Invalid streamer or typo.")
                time.sleep(self.refresh)
            elif status == 1:
                logging.info(self.streamer + " currently offline, checking again in " +
                             str(self.refresh) + " seconds.")
                time.sleep(self.refresh)
            elif status == 0:
                logging.info(self.streamer + " is live. Recording ...")
                self.filename = self.streamer + "_" + \
                    datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss") + ".mkv"

                # File name
                self.rec_filename = os.path.join(self.rec_path, self.filename)

                # Start streamlink process
                subprocess.call(["streamlink", "--twitch-oauth-token",
                                 self.tw_oauth_token,
                                 "twitch.tv/" + self.streamer,
                                 self.quality, "-o", self.rec_filename])

                # Send Pushover
                if self.po_token and self.po_user:
                    logging.info("Sending pushover message ...")
                    conn = http.client.HTTPSConnection("api.pushover.net:443")
                    conn.request("POST", "/1/messages.json",
                                 urllib.parse.urlencode({"token": self.po_token,
                                                         "user": self.po_user, "html": "1",
                                                         "message": "Recorded: " + self.filename, }),
                                 {"Content-type": "application/x-www-form-urlencoded"})
                    conn.getresponse()

                # Wait for twitch api to refresh
                logging.info(
                    "Waiting 5 minutes for the twitch api to refresh ... (yes, the api is that slow)")
                time.sleep(300)
                logging.info("Going back to checking ...")


if __name__ == "__main__":
    try:
        # Define where the config file is located
        config_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "config.json")
        # Update config with cli args and ask user for missing configs
        streamer, quality, tw_client_id, tw_oauth_token, po_token, po_user = Config().cli()
        # Write that config to a file
        Config().create_config(streamer, quality,
                               tw_client_id, tw_oauth_token, po_token, po_user)
        # Start the recoding process
        TwitchRecorder().run()
    except KeyboardInterrupt:
        logging.error("Quit by user.")
