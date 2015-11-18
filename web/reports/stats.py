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
# FROM ordering_scene'''


#'users_with_orders_count' :{
#         'display_name': 'Users - Open Order Count',
#         'description': 'Number of users that are waiting on products',
#         'query': r'''SELECT
#                      COUNT(DISTINCT u.username)
#                      FROM auth_user u
#                      JOIN ordering_order o ON o.user_id = u.id
#                      JOIN ordering_scene s ON s.order_id = o.id
#                      WHERE s.status IN
#                          ('queued', 'processing', 'oncache',
#                          'onorder', 'error', 'retry', 'submitted')'''
#     },


#This would need to be a report since it could display something other than a value
#Products added since (or between)
#add flag for 'summary'.  If no 'summary' then display all the values (name, orderid, time ordered)
#select count(s.name) from ordering_scene s join ordering_order o on o.id = s.order_id where o.order_date >= '2015-11-18:00:00.00' and o.order_date <= '2015-11-19:00:00.00'
