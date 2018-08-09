# YouTube to podcast converter

This tool can convert any YouTube channel or a playlist into a downloadable podcast. You can choose audio or video format, and use it online or install it on your own server.

## Online

1. Head over to YouTube in your browser, and find the URL of your favorite user, channel, or playlist. The URL will look like one of these:
	+ `https://m.youtube.com/user/latenight`
	+ `https://www.youtube.com/channel/UCVTyTA7-g9nopHeHbeuvpRA`
	+ `https://www.youtube.com/playlist?list=PLUl4u3cNGP61Oq3tWYp6V_F-5jb5L2iHb`

2. Open up your podcasts app and add a new podcast by URL. Copy and paste in the URL from step 1, except type in `epi` right before `youtube`.
Your modified URL should look like one of these:
	+ `https://m.epiyoutube.com/user/latenight`
	+ `https://www.epiyoutube.com/channel/UCVTyTA7-g9nopHeHbeuvpRA`
	+ `https://www.epiyoutube.com/playlist?list=PLUl4u3cNGP61Oq3tWYp6V_F-5jb5L2iHb`

3. EPI generates video podcasts by default. If you'd like an audio-only podcast instead, simply add `?a` to the end of the URL for users or channels, or add `&a` to the end of the URL for playlists:
	+ `https://m.epiyoutube.com/user/latenight?a`
	+ `https://www.epiyoutube.com/channel/UCVTyTA7-g9nopHeHbeuvpRA?a`
	+ `https://www.epiyoutube.com/playlist?list=PLUl4u3cNGP61Oq3tWYp6V_F-5jb5L2iHb&a`

4. Hit subscribe. You're all set. You can now download and refresh episodes, just like with any other podcast.

**If you enjoy this service, please consider making a donation to help keep it up and running.**


## Install it on your own server

If you don't want to use the online version, you can install EPI on your own server. It requires Python 3.5+ (tested on Python 3.5.3 and 3.6.1), pip, git and [youtube-dl](http://rg3.github.io/youtube-dl/download.html).
### Steps :
- Clone the repository : ``git clone https://github.com/Gildas-GH/epi``
- Install requirements : ``pip3 install -r requirements.txt``
- You'll need a [YouTube API key](https://stackoverflow.com/questions/44399219/where-to-find-the-youtube-api-key), put it in a new file named ``g.py`` in /epi/ like this : ``KEY = 'R4nd0mAp1k3y'``
- Run ``python3 manage.py migrate``
- And then ``python3 manage.py runserver``

The software is now installed and listening on port 8000. We'll need to allow access to this port from the Internet and configure a daemon to let the software run in background.

### Nginx reverse proxy
I am using nginx on my server. If you know the configuration for other web servers, a pull request is welcome!
Put this configuration in a ``server`` block.
```
location / {
  proxy_pass        http://127.0.0.1:8000;
  proxy_redirect    off;
  proxy_set_header  Host $host;
  proxy_set_header  X-Real-IP $remote_addr;
  proxy_set_header  X-Forwarded-Proto $scheme;
  proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header  X-Forwarded-Host $server_name;
  
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";

  more_clear_input_headers 'Accept-Encoding';
}
```

### Create a daemon

We need to run EPI in the background. On Debian, create and edit a new systemd service :
`` vi /etc/systemd/system/epi.service``
In this file, paste the following configuration :
```
[Unit]
Description=Convert any YouTube channel into a downloadable podcast
After=network-online.target
 
[Service]
Type=simple
 
User=user
Group=group
UMask=007
 
ExecStart=/usr/bin/python3 /path/to/epi/manage.py runserver
 
Restart=on-failure
 
# Configures the time to wait before service is stopped forcefully.
TimeoutStopSec=300
 
[Install]
WantedBy=multi-user.target
```
Make sure you edit user, group and the software path.

Then you can run ``service epi start`` to start the software and access it from the address you set in nginx. The rules to create a podcast will be the same (``http(s)://domain.tld/playlist?list=PLUl4u3cNGP61Oq3tWYp6V_F-5jb5L2iHb&a`` for example).

## Note
You can also use EPI to download a single video :
- Video format : https://www.epiyoutube.com/download/video/VideoID.mp4
- Audio format : https://www.epiyoutube.com/download/audio/VideoID.m4a
