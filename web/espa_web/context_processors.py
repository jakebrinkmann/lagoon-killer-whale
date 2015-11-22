from ordering.models.configuration import Configuration as config
from reporting import stats

def scene_stats(request):
    '''Includes stats for scene backlog and completed 24 hrs'''
    
    context = {}
    context['stat_backlog_depth'] = stats.get('stat_backlog_depth', skip_cache=False)
    context['stat_products_complete_24_hrs'] = stats.get('stat_products_complete_24_hrs', skip_cache=False)
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
