# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 10:07:52 2015

@author: dhill
"""

# a stat is a single value item.
# multi-value items belong in reports.

# show disk space on cache
# show number of users with open orders
#'''SELECT COUNT(DISTINCT user_id) FROM ordering_order o WHERE o.status = 'ordered' '''
# show number of open orders
#'''SELECT COUNT(orderid) FROM ordering_order WHERE status = 'ordered' '''
# show backlog depth
#'''SELECT COUNT(*) FROM ordering_scene WHERE status NOT IN ('purged', 'complete', 'unavailable')'''
# show products completed 24 hrs
#'''SELECT COUNT(*) FROM ordering_scene s WHERE s.status = 'complete'  AND  completion_date > now() - interval '24 hours' '''

# show duplicate scene count
#'duplicate_scene_percentage': {
#                'display_name': 'Duplicate Scenes (Percentage)',
#                        'description': 'Displays the percentage of scenes that have been requested more than once',
#                                'query': r'''SELECT
#                                                     (1 - (count(distinct name)::float / count(name)::float) * 100) "Duplicate Scenes"
#                                                                          FROM ordering_scene'''
                                                                            


