from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^watch', views.watch_url, name='watch_url'),
    
    url(r'^channel/(?P<channel_id>[a-zA-Z0-9_-]+)',
        views.make_feed_from_channel,
        name='make_feed_from_channel'),

    url(r'^user/(?P<username>[a-zA-Z0-9_-]+)',
        views.make_feed_from_user,
        name='make_feed_from_user'),

    url(r'^playlist',
        views.make_feed_from_playlist,
        name='make_feed_from_playlist'),

    url(r'^download/(?P<video_id>[a-zA-Z0-9_-]+$)',
        views.redirect_to_file,
        name='redirect_to_file'), 

]