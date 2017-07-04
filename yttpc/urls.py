from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^watch$', views.handle_watch_url, name='watch_url'),
    
    url(r'^(channel|user)/([a-zA-Z0-9_-]+)', views.make_feed_from_channel),

    url(r'^playlist', views.make_feed_from_playlist),

    url(r'^download/([a-zA-Z0-9_-]+)\.m4a$',
        views.download,
        name='download'),

    url(r'^([a-zA-Z0-9_-]+)$', views.get_channel_data),

]