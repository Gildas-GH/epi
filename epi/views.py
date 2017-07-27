import email.utils
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
import isodate
import pafy
from .g import KEY


#Youtube API URLs
ENDPOINT = 'https://www.googleapis.com/youtube/v3/'
BASE_VIDEO_URL = 'https://www.youtube.com/watch?v='

#Project landing page
HOMEPAGE = "https://github.com/amtopel/epi/blob/master/README.md"


def index(request):
    """Redirect to the project homepage if there's no path in the URL."""

    return redirect(HOMEPAGE)


def make_feed_from_channel(request, id_type, id_value):
    """Create an RSS feed from a YouTube username or channel ID"""

    channel_data = get_channel_data(id_type, id_value)

    try:
        uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except IndexError:
        return HttpResponse('It appears that "{}" is not a valid {}.'.format(id_value, id_type))

    playlist_data = get_playlist_data(uploads_playlist_id)

    return render_feed(request, playlist_data, channel_data)


def make_feed_from_playlist(request):
    """Create an RSS feed from a YouTube playlist."""

    try:
        playlist_id = request.GET['list']
    except KeyError:
        return HttpResponse('Invalid URL.')

    try:
        playlist_data = get_playlist_data(playlist_id)
    except HTTPError:
        return HttpResponse('It appears that "{}" is not a valid playlist.'.format(request.GET['list']))

    channel_id = playlist_data['items'][0]['snippet']['channelId']
    channel_data = get_channel_data('channel', channel_id)

    return render_feed(request, playlist_data, channel_data)


def render_feed(request, playlist_data, channel_data):
    """Render the RSS feed from the playlist data,
    channel data, and desired podcast type (audio or video)."""

    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]
    videos_data = yt_api_call('videos', 'snippet,contentDetails', 'id', ','.join(video_ids))

    for item in videos_data['items']:

        #Reformat publication dates for RSS (RFC 2822)
        date_ISO = item['snippet']['publishedAt']
        parsed = parse_datetime(date_ISO)
        date_RFC = email.utils.format_datetime(parsed)
        item['snippet']['publishedAt'] = date_RFC

        #Reformat file duration for iTunes
        duration_iso = item['contentDetails']['duration']
        parsed = isodate.parse_duration(duration_iso)
        item['contentDetails']['duration'] = str(parsed)

    #Add channel data to video data to make single context
    videos_data['channel_data'] = channel_data

    #Add media type
    podcast_type = 'video' if int(request.GET.get('vid', 0)) else 'audio'
    videos_data['podcast_type'] = podcast_type

    #Add media extension
    videos_data['media_extension'] = 'mp4' if podcast_type == 'video' else 'm4a'

    return render(request, 'epi/feed.xml', videos_data)


def get_channel_data(id_type, id_value):
    """Return a dictionary of channel data from a channel id or username."""

    id_type = 'id' if id_type == 'channel' else 'forUsername'
    channel_data = yt_api_call('channels', 'contentDetails,snippet', id_type, id_value)

    return channel_data


def get_playlist_data(playlist_id):
    """Return a dictionary of playlist data from a playlist id."""

    playlist_data = yt_api_call('playlistItems', 'snippet', 'playlistId', playlist_id)
    return playlist_data


def make_feed_from_custom(request, user):
    """Handle custom URL paths like '/coldplayvevo'."""

    return make_feed_from_channel(request, 'user', user)


def handle_watch_url(request):
    """Handle '/watch?v=' urls, which may contain playlist parameters or just single videos."""

    if 'list' in request.GET:
        return make_feed_from_playlist(request)
    else:
        return HttpResponse('This appears to be just a single video.')


def download(request, media_type, video_id):
    """Redirect for media download."""

    video_url = BASE_VIDEO_URL + video_id
    video = pafy.new(video_url)

    stream = video.getbest(preftype="mp4") if media_type == 'video' else video.getbestaudio(preftype="m4a")

    redirect_url = stream.url
    return redirect(redirect_url)


def yt_api_call(path, part, id_type, id_value):
    """Make a call to the Youtube API."""

    params = {'key': KEY,
              id_type: id_value,
              'part': part,
              'maxResults': 50}

    data_url = (ENDPOINT + path + '?' + urlencode(params))

    with urlopen(data_url) as response:
        json_data = response.read()

    return json.loads(json_data)
