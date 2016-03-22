from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as login
from django.contrib.admin.views.decorators import staff_member_required as staff

from views import Index, StatusMessage, Config

urlpatterns = patterns('', 
    url(r'^config$',
        login(staff(Config.as_view(), login_url='login')), 
            name='console_config_listing'),
    url(r'^config/(?P<key>.+)',
        login(staff(Config.as_view(), login_url='login')), 
            name='console_config'),
    url(r'^statusmsg',
        login(staff(StatusMessage.as_view(), login_url='login')), 
            name='console_statusmsg'),
    url(r'^$',
        login(staff(Index.as_view(), login_url='login')), 
            name='console_index')
    )
