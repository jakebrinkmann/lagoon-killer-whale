from django.db import connection
from ordering.utilities import dictfetchall

reports = {
    'scene_report': {
        'display_name': 'Current Scene Report',
        'description': 'Shows the total scenes currently in the system by user',
        'query': r'''SELECT COUNT(s.name) "Total Active Scenes",
                   SUM(case when s.status in ('complete', 'unavailable') then 1 else 0 end) "Complete",
                   SUM(case when s.status not in ('processing', 'complete', 'unavailable') then 1 else 0 end) "Open",
                   SUM(case when s.status = 'processing' then 1 else 0 end) "Processing",
                   u.email "Email",
                   u.first_name "First Name",
                   u.last_name "Last Name",
                   SUM(case when s.status = 'error' then 1 else 0 end) "Error",
                   SUM(case when s.status = 'onorder' then 1 else 0 end) "On Order"
                   FROM ordering_scene s, ordering_order o, auth_user u
                   WHERE s.order_id = o.id 
                   AND o.user_id = u.id 
                   AND s.status != 'purged' 
                   GROUP BY u.email, u.first_name, u.last_name 
                   ORDER BY "Total Active Scenes" DESC'''
    },
    'order_report': {
        'display_name': 'Current Order Report',
        'description': 'Shows the total number of orders in the system grouped by user',
        'query': r'''SELECT COUNT(o.orderid) "Total Orders",
              SUM(case when o.status = 'complete' then 1 else 0 end) "Complete",
              SUM(case when o.status = 'ordered' then 1 else 0 end) "Open",
              u.email, u.first_name, u.last_name
              FROM ordering_order o, auth_user u
              WHERE o.user_id = u.id 
              AND o.status != 'purged'
              GROUP BY u.email, u.first_name, u.last_name
              ORDER BY "Total Orders" DESC'''
    },
    'duplicate_scene_percentage': {
        'display_name': 'Duplicate Scenes (Percentage)',
        'description': 'Displays the percentage of scenes that have been requested more than once',
        'query': r'''SELECT
                     (1 - (count(distinct name)::float / count(name)::float)) * 100 "Cache Hit Ratio"
                     FROM ordering_scene'''
    },
    'order_position_in_line': {
        'display_name': 'Order Queue Position',
        'description': 'Shows orders and scenes with status and priority position',
        'query': r'''SELECT o.order_date "date ordered",
                     o.orderid "order id",
                     o.priority "order priority",
                     COUNT(s.name) "scene count",
                     SUM(CASE when s.status in ('complete', 'unavailable') then 1 else 0 end) "complete",
                     SUM(CASE when s.status = 'processing' then 1 ELSE 0 END) "processing",
                     u.username "user name"
                     FROM ordering_scene s, ordering_order o, auth_user u
                     WHERE o.id = s.order_id
                     AND u.id = o.user_id
                     AND o.status = 'ordered'
                     GROUP BY
                     o.orderid,
                     u.username,
                     o.order_date,
                     o.priority
                     ORDER BY o.order_date ASC''',
        '''select o.order_date "date ordered", o.orderid, o.priority, count(s.name) "scene count", SUM(CASE when s.status in ('complete', 'unavailable') then 1 else 0 end) "complete", SUM(CASE when s.status = 'processing' then 1 ELSE 0 END) "processing", u.username from ordering_scene s, ordering_order o, auth_user u where o.id = s.order_id and u.id = o.user_id and o.status = 'ordered' group by o.orderid, u.username, o.order_date, o.priority order by processing ASC, o.order_date ASC;''',
        
    },
    'scenes_selection': {
        'display_name': 'Scenes Selection Strategy',
        'description': 'Shows the order scenes are going to be submitted to the cluster',
        'query': r'''WITH order_queue AS
                        (SELECT u.email "email", count(name) "running"
                         FROM ordering_scene s, ordering_order o, auth_user u
                         WHERE
                         u.id = o.user_id
                         AND o.id = s.order_id
                         AND s.status in ('queued', 'processing')
                         GROUP BY u.email)
                     SELECT
                     s.name,
                     o.order_date,
                     o.orderid,
                     o.priority,
                     q.running
                     FROM ordering_scene s, ordering_order o, auth_user u, order_queue q
                     WHERE u.id = o.user_id
                     AND o.id = s.order_id
                     AND o.status = 'ordered'
                     AND s.status = 'oncache'
                     AND q.email = u.email
                     ORDER BY q.running ASC, o.order_date ASC''',


    },
    'orders_running': {
        'query': r'''SELECT o.order_date, o.orderid, count(s.name)
                     FROM ordering_order o, ordering_scene s
                     WHERE o.id = s.order_id and s.status = 'processing'
                     GROUP BY o.orderid, o.order_date
                     GROUP BY o.order_date, count DESC'''
    },
    'orders_queued': {
        'query': r'''SELECT o.order_date, o.orderid, count(s.name)
                     FROM ordering_order o, ordering_scene s
                     WHERE o.id = s.order_id
                     AND s.status = 'queued'
                     GROUP BY o.orderid, o.order_date
                     ORDER BY o.order_date, count DESC''',
    }
}

with total_scenes as (select count(name) from ordering_scene where status != 'purged'),
distinct_scenes  as (select count(distinct name) from ordering_scene where status != 'purged')
select ds.count "Distinct Scenes", ts.count "Total Scenes" from distinct_scenes ds, total_scenes ts;


class Report(object):

    def listing(self, show_query=False):
        result = {}
        for key, value in reports.iteritems():
            if show_query is False:
                value.pop('query')
            result[key] = value
        return result

    def run(self, name):
        if name not in reports:
            raise NotImplementedError

        with connection.cursor() as cursor:
            cursor.execute(reports[name]['query'])
            return dictfetchall(cursor)


