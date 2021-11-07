# twitch-rec

twitch-rec will record your favorite streamer so you don't have to rely on VODs when you missed a stream.

## Getting Started

```
git clone https://github.com/seriousm4x/twitch-rec.git && cd twitch-rec
```

Install dependencies

```
pip3 install -r requirements.txt
```

Edit the `settings.json` file. There are 4 mandatory values:

* streamer
* quality
* client_id
* client_secret

The last 2 can be created at [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps).

Leave `oauth` empty. The script will create it for you.

If you wanna use pushover, paste a token and user id. If not, just leave it blank.

```
python3 twitch-rec.py
```

## Docker

Sample docker-compose.yml file to build image and spin-up a container.

Change %%EDITME%% with the absolute path of the folder you want to store the vids at.

```
version: '3.5'
services:
  twitch-rec:
    restart: always
    build:
      context: .
    image: twitch-rec
    container_name: twitch-rec
    volumes:
      - %%EDITME%%:/app/recs
      - ${PWD}/config:/app/config
    environment:
      TZ: Europe/Paris
```

## Contributing

Feel free to contribute and bring in your ideas to enhance this tool or to add more notification possibilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
