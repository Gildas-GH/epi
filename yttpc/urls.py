from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^watch$', views.watch_url, name='watch_url'),
    
    url(r'^(channel|user)/([a-zA-Z0-9_-]+)', views.get_uploads_playlist),

    url(r'^playlist', views.make_feed_from_playlist),

    url(r'^download/([a-zA-Z0-9_-]+)\.m4a$',
        views.redirect_to_file,
        name='redirect_to_file'),

    url(r'^([a-zA-Z0-9_-]+)$', views.get_uploads_playlist),

]