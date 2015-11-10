from django.db import connection
from ordering.utilities import dictfetchall

reports = {
    'current_scenes': {
        'display_name': 'Current Scenes',
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
    'current_orders': {
        'display_name': 'Current Orders',
        'description': 'Shows the total number of orders in the system grouped by user',
        'query': r'''SELECT COUNT(o.orderid) "Total Orders",
              SUM(case when o.status = 'complete' then 1 else 0 end) "Complete",
              SUM(case when o.status = 'ordered' then 1 else 0 end) "Open",
              u.email "Email", u.first_name "First Name", u.last_name "Last Name"
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
                     (1 - (count(distinct name)::float / count(name)::float) * 100) "Duplicate Scenes"
                     FROM ordering_scene'''
    },
    'orders_processing': {
        'display_name': 'Orders Currently Processing',
        'description': 'Shows orders that have scenes which are currently processing', 
        'query': r'''SELECT o.order_date "Date Ordered", o.orderid "Order ID", count(s.name) "Scene Count" 
                     FROM ordering_order o, ordering_scene s 
                     WHERE o.id = s.order_id 
                     AND s.status = 'processing' 
                     GROUP BY o.orderid, o.order_date 
                     ORDER BY o.order_date, "Scene Count" DESC'''
    },
    'orders_queued': {
        'display_name': 'Orders Currently Queued',
        'description': 'Shows order that have scenes in queued status',
        'query': r'''SELECT o.order_date "Date Ordered", 
                     o.orderid "Order ID", 
                     count(s.name) "Scene Count" 
                     FROM ordering_order o, ordering_scene s 
                     WHERE o.id = s.order_id  
                     AND s.status = 'queued' 
                     GROUP BY o.orderid, o.order_date 
                     ORDER BY o.order_date, "Scene Count" DESC'''
    },
    'order_position_in_line': {
        'display_name': 'Order Queue Position',
        'description': 'Shows orders and scenes with status and priority position',
        'query': r'''SELECT o.order_date "Date Ordered",
                     o.orderid "Order ID",
                     o.priority "Order Priority",
                     COUNT(s.name) "Scene Count",
                     SUM(CASE when s.status in ('complete', 'unavailable') then 1 else 0 end) "Complete",
                     SUM(CASE when s.status = 'processing' then 1 ELSE 0 END) "Processing",
                     SUM(CASE when s.status = 'error' then 1 ELSE 0 END) "Error",
                     u.username "User Name"
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
                     s.name "Scene",
                     o.order_date "Date Ordered",
                     o.orderid "Order ID",
                     o.priority "Order Priority",
                     q.running "Currently Running Count"
                     FROM ordering_scene s, ordering_order o, auth_user u, order_queue q
                     WHERE u.id = o.user_id
                     AND o.id = s.order_id
                     AND o.status = 'ordered'
                     AND s.status = 'oncache'
                     AND q.email = u.email
                     ORDER BY q.running ASC, o.order_date ASC'''
     },
}



class Report(object):

    def listing(self, show_query=False):
        result = {}
        for key, value in reports.iteritems():
            if show_query is False:
                value['query'] = ''
            result[key] = value
       
        return result

    def run(self, name):
        if name not in reports:
            raise NotImplementedError

        with connection.cursor() as cursor:
            query = reports[name]['query']
            cursor.execute(query)
            return dictfetchall(cursor)

listing = lambda x=None: Report().listing()
run = lambda name: Report().run(name)
display_name = lambda name: reports[name]['display_name']
