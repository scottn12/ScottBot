# ScottBot
ScottBot is a bot made for discord servers using python. ScottBot was initially deployed using Heroku (that's why there are so many commits), and AWS S3 Buckets to store files. Now ScottBot is deployed on a personal raspberry pi using a custom launch script along with JSON storage files and a sqlite database.

To add ScottBot to your server, please contact me on discord: `skaht#6034`.

Please note many commands require administrative permissions.

To run ScottBot locally, please note:
- FFmpeg must be installed to play audio.
- Some assets may not be included in the repository.
- ScottBot uses many environment variables (whenever you see `os.environ.get()` called), you will need to recreate this environment variables with your own values.