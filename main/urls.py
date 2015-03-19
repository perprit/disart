from django.conf.urls import patterns, url

urlpatterns = patterns('main.views',
    url(r'^$', 'upload', name='upload'),
    url(r'^draw/(?P<id>\d+)/$', 'draw', name='draw'),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name='delete'),
    url(r'^chartrecog/$', 'chartrecog', name='chartrecog'),
)
