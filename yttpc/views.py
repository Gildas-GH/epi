from django.shortcuts import redirect, render
from django.http import HttpResponse
import json
import pafy
from urllib.parse import urlencode
from urllib.request import urlopen


#Youtube API
KEY = 'AIzaSyBVKqUnRv1X67Y9wjTfd_5u0vg9LND9Zg0'
ENDPOINT = 'https://www.googleapis.com/youtube/v3/'
GLOBAL_PARAMS = {'key': KEY,
                 'part': 'snippet',
                 'order': 'date',
                 'maxResults': 50,
                 'type': 'video'}
BASE_VIDEO_URL = 'https://www.youtube.com/watch?v='

def index(request):
    return HttpResponse('This is the landing page.')


def make_feed_from_channel(request, channel_id):
    
    query_params = {'channelId': channel_id}
    query_params.update(GLOBAL_PARAMS)

    data_url = (ENDPOINT + 'search?' + urlencode(query_params))

    with urlopen(data_url) as response:
        json_data = response.read()
    
    context = json.loads(json_data)

    return render(request, 'yttpc/feed.xml', context)


def make_feed_from_user(request, username):

    query_params = {'forUsername': username}
    query_params.update(GLOBAL_PARAMS)

    data_url = (ENDPOINT + 'channels?' + urlencode(query_params))

    with urlopen(data_url) as response:
        json_data = response.read()
    
    data_dict = json.loads(json_data)
    channel_id = data_dict['items'][0]['id']

    return make_feed_from_channel(request, channel_id)


def make_feed_from_playlist(request):

    query_params = {'playlistId': request.GET['list']}
    query_params.update(GLOBAL_PARAMS)

    data_url = (ENDPOINT + 'playlistItems?' + urlencode(query_params))

    with urlopen(data_url) as response:
        json_data = response.read()

    context = json.loads(json_data)

    return render(request, 'yttpc/feed.xml', context)


def watch_url(request):
    if 'list' in request.GET:
        return make_feed_from_playlist(request)
    else:
        return HttpResponse('This is just a single video.')


def redirect_to_file(request, video_id):

    video_url = BASE_VIDEO_URL + video_id.split('.')[0]
    video = pafy.new(video_url)

    stream = video.getbestaudio(preftype='m4a') 

    return redirect(stream.url)