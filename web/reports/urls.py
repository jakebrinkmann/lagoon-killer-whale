from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from views import Report 

urlpatterns = patterns('', 
    url(r'^(?P<name>[A-Za-z0-9._-]+)/$',
        login_required(staff_member_required(Report.as_view())),
        name='show_report'),
    url(r'^$',
        login_required(staff_member_required(Report.as_view())),
        name='listreports'),
    url(r'^/$',
        login_required(staff_member_required(Report.as_view())),
        name='listreports')
    )
