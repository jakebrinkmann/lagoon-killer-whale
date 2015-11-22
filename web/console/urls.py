from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import Index, StatusMessage, Config

urlpatterns = patterns('', 
    url(r'^config$',
        login_required(Config.as_view()), name='console_config_listing'),
    url(r'^config/(?P<key>.+)',
        login_required(Config.as_view()), name='console_config'),
    url(r'^statusmsg',
        login_required(StatusMessage.as_view()), name='console_statusmsg'),
    url(r'^$',
        login_required(Index.as_view()), name='console_index')
    )
