from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
import email.utils
import json
import pafy
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

#Youtube API
KEY = 'AIzaSyBVKqUnRv1X67Y9wjTfd_5u0vg9LND9Zg0'
ENDPOINT = 'https://www.googleapis.com/youtube/v3/'
BASE_VIDEO_URL = 'https://www.youtube.com/watch?v='


def index(request):
    """The landing page."""
    return HttpResponse('This is the landing page.')


def make_feed_from_channel(request, id_type, id):
    
    channel_data = get_channel_data(id_type, id)
    
    try:
        uploads_playlist_id = get_uploads_playlist_id(channel_data)
    except IndexError as e:
        return HttpResponse('Invalid user or channel.')

    playlist_data = get_playlist_data(uploads_playlist_id)

    return render_feed(request, playlist_data, channel_data, request.GET.get('type', 'audio'))


def make_feed_from_playlist(request):

    try:
        playlist_id = request.GET['list']
    except KeyError:
        return HttpResponse('Invalid playlist.')
    
    try:
        playlist_data = get_playlist_data(playlist_id)
    except HTTPError:
        return HttpResponse('Invalid playlist.')
    
    channel_id = get_channel_id(playlist_data)
    channel_data = get_channel_data('channel', channel_id)

    return render_feed(request, playlist_data, channel_data, request.GET.get('type', 'audio'))


def render_feed(request, playlist_data, channel_data, podcast_type):
    """Render an RSS feed, given the playlist data, channel data, and desired media type."""

    #Reformat dates for RSS (RFC 2822)
    for item in playlist_data['items']:
        date_ISO = item['snippet']['publishedAt']
        parsed = parse_datetime(date_ISO)
        date_RFC = email.utils.format_datetime(parsed)
        item['snippet']['publishedAt'] = date_RFC

    #Add channel data to playlist data to make single context
    playlist_data['channel_data'] = channel_data
    
    #Add media type
    playlist_data['podcast_type'] = podcast_type
    
    #Add media extension
    if podcast_type == 'video':
        playlist_data['media_extension'] = 'mp4'
    else:
        playlist_data['media_extension'] = 'mp3'

    return render(request, 'yttpc/feed.xml', playlist_data)


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

    if media_type == 'video':
        stream = video.getbest(preftype="mp4")
    else:
        stream = video.getbestaudio(preftype='mp3')

    with open('scratch/text.txt', 'w') as f:
        f.write(stream.url)

    return redirect(stream.url)


def get_channel_data(id_type, id):
    """Return a dictionary of channel data from a username or channel id."""

    if id_type == 'channel':
        id_type = 'id'
    if id_type == 'user':
        id_type = 'forUsername'

    qs_params = {'key': KEY,
                id_type: id,
                'part': 'contentDetails,snippet'}

    data_url = (ENDPOINT + 'channels?' + urlencode(qs_params))

    with urlopen(data_url) as response:
        channel_data = response.read()

    channel_data = json.loads(channel_data)
    return channel_data


def get_playlist_data(playlist_id):
    """Return a dictionary of playlist data from a playlist id."""

    qs_params = {'key': KEY,
                 'playlistId': playlist_id,
                 'part': 'snippet',
                 'maxResults': 50}

    data_url = (ENDPOINT + 'playlistItems?' + urlencode(qs_params))

    with urlopen(data_url) as response:
        json_data = response.read()

    playlist_data = json.loads(json_data)
    return playlist_data


def get_uploads_playlist_id(channel_data):
    """Extract the 'uploads' playlist id from a channel."""

    playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return playlist_id


def get_channel_id(playlist_data):
    """Extract the channel id from a playlist."""
 
    channel_id = playlist_data['items'][0]['snippet']['channelId']
    return channel_id

