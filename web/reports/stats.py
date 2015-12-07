from django.core.cache import cache
import logging
from django.db import connection
from ordering.utilities import dictfetchall
import copy

logger = logging.getLogger(__name__)

STATS = {
    'stat_open_orders': {
        'display_name': 'Open Orders',
        'description': 'Number of open orders in the system',
        'query': r'''SELECT 
                     COUNT(orderid) "statistic"
                     FROM ordering_order 
                     WHERE status = 'ordered' '''
    },
    'stat_waiting_users': {
        'display_name': 'Waiting Users',
        'description': 'Number of users with open orders in the system',
        'query': r'''SELECT 
                     COUNT(DISTINCT user_id) "statistic"
                     FROM ordering_order 
                     WHERE status = 'ordered'  '''
    },
    'stat_backlog_depth': {
        'display_name': 'Backlog Depth',
        'description': 'Number of products to be fulfilled',
        'query': r'''SELECT COUNT(*) "statistic" 
                     FROM ordering_scene 
                     WHERE status 
                     NOT IN ('purged', 'complete', 'unavailable')'''
    },
    'stat_products_complete_24_hrs': {
        'display_name': 'Products Complete 24hrs',
        'description': 'Number of products completed last 24 hrs',
        'query': r'''SELECT COUNT(*) "statistic"
                     FROM ordering_scene s 
                     WHERE s.status = 'complete' 
                     AND completion_date > now() - interval '24 hours' '''
    },
}


#'stat_duplicate_active_products': {
#        'display_name': 'Duplicate Active Product Pct',
#        'description': 'Percentage of active product duplication',
#        'query': r'''SELECT 
#                     (1 - (count(distinct name)::float / count(name)::float) * 100) "statistic" 
#                      FROM ordering_scene'''
#},

class Statistics(object):

    def listing(self, show_query=False):

        # make a copy of this as we dont want to modify the
        # actual dict in this module
        _stats = copy.deepcopy(STATS)

        for key, value in _stats.iteritems():
            if show_query is False:
                value.pop('query')
        return _stats

    def get(self, name, skip_cache=False):

        if name not in STATS:
            raise NotImplementedError

        if skip_cache is False:
            value = cache.get(name)
            if value is not None: 
                return value
  
        query = STATS[name]['query']

        if query is not None and len(query) > 0:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = dictfetchall(cursor)
                stat = result[0]['statistic']
                cache.set(name, stat, 120)
                return stat
        else:
            logger.error("Query was empty for {0}: {1}".format(name, query))
            return None


listing = Statistics().listing

get = lambda name, skip_cache=False: Statistics().get(name, skip_cache)

display_name = lambda name: STATS[name]['display_name']
