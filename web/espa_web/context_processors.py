from ordering.models.configuration import Configuration as config
from django.db import connection
from django.core.cache import cache
from datetime import datetime, timedelta
from ordering.utilities import dictfetchall


def scene_stats(request):
    '''Includes stats for scene backlog and completed 24 hrs'''
    context = {}
    cutoff = datetime.now() - timedelta(hours=24)
    stats = {'stats_current_backlog': "select count(*) \"count\" from ordering_scene where status not in ('purged', 'complete', 'unavailable')",
            'stats_completed_last_day': "select count(*) \"count\" from ordering_scene where completion_date >= now()::date - interval '24 hours'"}

    for key in stats.keys():
        count = cache.get(key)
        if count is None:
            with connection.cursor() as cursor:
                cursor.execute(stats[key])
                count = dictfetchall(cursor)[0]['count']
                if count is None or count < 0:
                    count = 0
                cache.set(key, count, 120)
        context[key] = count
    return context

def include_external_urls(request):
    '''Django context processor to include needed urls in the
    request contexts.  This method must be included in the
    list of TEMPLATE_CONTEXT_PROCESSORS in settings.py to be active.

    Keyword args:
    request -- HTTP request object

    Return:
    A dictionary of values to be included in the request context
    '''
    context = {}
    context['register_user'] = config.url_for('register_user')
    context['forgot_login'] = config.url_for('forgot_login')
    context['earthexplorer'] = config.url_for('earthexplorer')
    return context
