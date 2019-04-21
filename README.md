# twitch-rec

twitch-rec will record your favorite streamer so you don't have to use muted VOD's when you missed a stream and will send a pushover notification once recorded. It uses the new twich helix api.


## Getting Started

These instructions will help you to get it up an running.

### Prerequisites

You need python3, pip3 and streamlink. (python2 will not work)

```
pip3 install streamlink
```

### Installing

Go ahead an clone the repo

```
git clone https://github.com/seriousm4x/twitch-rec.git
```

cd into the repo

```
cd twitch-rec
```

run the script

```
python3 twitch-rec.py
```

and answer the questions you are asked.

## Usage

You can run the script like above and go through the setup, or tell the script the infomation it needs via cli args.

`python3 twitch-rec.py -h`

```
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
```

When you pass arguments to the script, it will update the config file with the newest settings. 

## Understanding the config.json file

```
{
    "rec": {
        "streamer": "somecoolstreamer",
        "quality": "best"
    },
    "twitch": {
        "client_id": "xxxxx",
        "oauth": "xxxxx"
    },
    "pushover": {
        "token": "xxxxx",
        "user": "xxxxx"
    }
}
```

It might be confusing, what each setting is for, but let me explain.
* **streamer**: Obviously the twitch streamer you want to record.
* **quality**: The stream resolution for the stream. "Best" will use the highes resolution. You can see all available options in the terminal output once you run it.
* **client-id**: With this unique id you authorize with twitch to allow api requests. If you don't know how to get one, [read "Step 1: Setup"](https://dev.twitch.tv/docs/api/) in the twitch api doc or create your id on [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps).
* **oauth**: Also for twitch authentification required by streamlink. To get one, run `streamlink --twitch-oauth-authenticate` in your terminal.
* **token**: An app specific token from pushover.net. Log in to your account and create a new application. You'll be given the app token.
* **user**: Like client-id but for pushover. You will see it on the top right once you log in.

## Contributing

Feel free to contribute and bring in your ideas to enhance this tool or to add more notification possibilities.

## Authors

* **SeriousM4x** - *Initial work* - [SeriousM4x on Github](https://github.com/seriousm4x)

See also the list of [contributors](https://github.com/seriousm4x/twitch-rec/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details