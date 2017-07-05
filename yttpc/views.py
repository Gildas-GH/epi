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

    #Add channel data to video data to make single context
    playlist_data['channel_data'] = channel_data
    
    #Add media type to context
    playlist_data['podcast_type'] = podcast_type
    
    #Add media extension
    playlist_data['media_extension'] = 'mp4' if podcast_type == 'video' else 'm4a'

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

    stream = video.getbest(preftype="mp4") if media_type == 'video' else video.getbestaudio(preftype="m4a")
    
    redirect_url = stream.url
    return redirect(redirect_url)


def get_channel_data(id_type, id):
    """Return a dictionary of channel data from a channel id or username."""

    id_type = 'id' if id_type == 'channel' else 'forUsername'
    channel_data = yt_api_call('channels', 'contentDetails,snippet', id_type, id)
    
    return channel_data


def get_playlist_data(playlist_id):
    """Return a dictionary of playlist data from a playlist id."""

    playlist_data = yt_api_call('playlistItems', 'snippet', 'playlistId', playlist_id)
    return playlist_data


# def get_videos_data(playlist_data):

#     video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]

#     videos_data = yt_api_call('videos', 'snippet,contentDetails', 'id', ','.join(video_ids))
#     return videos_data


def get_uploads_playlist_id(channel_data):
    """Extract the 'uploads' playlist id from a channel."""

    playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return playlist_id


def get_channel_id(playlist_data):
    """Extract the channel id from a playlist."""
 
    channel_id = playlist_data['items'][0]['snippet']['channelId']
    return channel_id


def yt_api_call(path, part, id_type, id):

    params = {'key': KEY,
              id_type: id,
              'part': part,
              'maxResults': 50}

    data_url = (ENDPOINT + path + '?' + urlencode(params))

    with urlopen(data_url) as response:
        json_data = response.read()

    return json.loads(json_data)



