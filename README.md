# twitch-rec

twitch-rec will record your favorite streamer so you don't have to rely on VODs when you missed a stream.

## Getting Started

Sample docker-compose.yml file to build image and spin-up a container. Clone the repo and change the placeholders.

```
version: '3'
services:
  twitch-rec:
    container_name: twitch-rec
    build: .
    restart: always
    volumes:
      - ./recordings:/app/recordings
    environment:
      STREAMER: xxxxx
      QUALITY: best
      INTERVAL: 15
      CLIENT_ID: xxxxx
      CLIENT_SECRET: xxxxx
      PUSHOVER_TOKEN: xxxxx
      PUSHOVER_USER: xxxxx
      TZ: Europe/Paris
```

## Things to change in docker-compose.yml:

* volume path "recordings" to the folder you want to store the vids at
* STREAMER
* CLIENT_ID
* CLIENT_SECRET
* PUSHOVER_TOKEN
* PUSHOVER_USER

`CLIENT_ID` and `CLIENT_SECRET` can be created at [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps).

If you don't use pushover, just delete both lines.

## Contributing

Feel free to contribute and bring in your ideas to enhance this tool or to add more notification possibilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
