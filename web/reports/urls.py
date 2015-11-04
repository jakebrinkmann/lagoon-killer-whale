from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import Report 

urlpatterns = patterns('', 
    url(r'^generate/?P<name>/$',
        login_required(Report.as_view()), name='show_report'),
    url(r'^$',
        login_required(Report.as_view()), name='listreports')
    )

