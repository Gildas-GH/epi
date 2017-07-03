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
    """Present the homepage."""

    return HttpResponse('This is the landing page.')


def get_uploads_playlist(request, id_type, id):
    """Get the 'uploads' playlist from user or channel, and then generate
    a feed from the playlist."""

    if id_type == 'user':
        id_type = 'forUsername'
    if id_type == 'channel':
        id_type = 'id'

    qs_params = {'key': KEY,
                id_type: id,
                'part': 'contentDetails'}

    data_url = (ENDPOINT + 'channels?' + urlencode(qs_params))

    with urlopen(data_url) as response:
        json_data = response.read()
    
    data_dict = json.loads(json_data)

    try:
        uploads_playlist_id = data_dict['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except IndexError as e:
        return HttpResponse('No such channel/user found.')

    return make_feed_from_playlist(request, uploads_playlist_id)


def make_feed_from_playlist(request, playlist_id=None):
    """Generate an RSS feed from JSON playlist data."""

    if not playlist_id:
        playlist_id = request.GET['list']
    
    qs_params = {'key': KEY,
                 'playlistId': playlist_id,
                 'part': 'snippet',
                 'maxResults': 50}

    data_url = (ENDPOINT + 'playlistItems?' + urlencode(qs_params))

    with urlopen(data_url) as response:
        json_data = response.read()

    context = json.loads(json_data)

    #Reformat dates for RSS
    # for item in context['items']:
    #     date_ISO = item['snippet']['publishedAt']
    #     parsed = parse_datetime(date_ISO)
    #     date_RFC = email.utils.format_datetime(parsed)
    #     item['snippet']['publishedAt'] = date_RFC

    return render(request, 'yttpc/feed.xml', context)


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