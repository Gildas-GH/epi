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
    uploads_playlist_id = get_uploads_playlist_id(channel_data)
    playlist_data = get_playlist_data(uploads_playlist_id)
    
    playlist_data['channel_data'] = channel_data

    return render(request, 'yttpc/feed.xml', playlist_data)

def make_feed_from_playlist(request):

    if 'list' in request.GET:
        playlist_id = request.GET['list']
    playlist_data = get_playlist_data(playlist_id)
    channel_id = get_channel_id(playlist_data)
    channel_data = get_channel_data('channel', channel_id)
    
    playlist_data['channel_data'] = channel_data

    return render(request, 'yttpc/feed.xml', playlist_data)


    #Reformat dates for RSS
    # for item in context['items']:
    #     date_ISO = item['snippet']['publishedAt']
    #     parsed = parse_datetime(date_ISO)
    #     date_RFC = email.utils.format_datetime(parsed)
    #     item['snippet']['publishedAt'] = date_RFC


def watch_url(request):
    """Handle '/watch?v=' urls, which may contain playlist parameters or just single videos."""

    if 'list' in request.GET:
        return make_feed_from_playlist(request)
    else:
        return HttpResponse('This is just a single video.')



def redirect_to_file(request, video_id):
    """Redirect for media download"""

    video_url = BASE_VIDEO_URL + video_id
    video = pafy.new(video_url)

    stream = video.getbestaudio(preftype='m4a') 

    return redirect(stream.url)


def get_channel_data(id_type, id):

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

    try: 
        playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except IndexError:
        return

    return playlist_id


def get_channel_id(playlist_data):

    try: 
        channel_id = playlist_data['items'][0]['snippet']['channelId']
    except IndexError:
        return

    return channel_id

