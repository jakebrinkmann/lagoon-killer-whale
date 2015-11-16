from django.db import connection
from ordering.utilities import dictfetchall

reports = {
    'users_by_capacity_share': {
        'display_name': 'Users by Capacity Share',
        'description': 'Shows users by number of open and running products',
        'query': r'''SELECT u.username "Username",
                     SUM(CASE WHEN s.status = 'processing'
                         THEN 1 ELSE 0 END) "Processing",
                     SUM(CASE WHEN s.status = 'queued'
                         THEN 1 ELSE 0 END) "Queued",
                     SUM(CASE WHEN s.status IN
                         ('queued', 'processing')
                         THEN 1 ELSE 0 END) "Total Running",
                     SUM(CASE WHEN s.status IN
                         ('queued', 'processing', 'onorder',
                          'submitted', 'error', 'retry', 'oncache')
                         THEN 1 ELSE 0 END) "Open Products",
                     u.email "Email",
                     u.first_name "First Name",
                     u.last_name "Last Name"
                     FROM ordering_scene s
                     JOIN ordering_order o on o.id = s.order_id
                     JOIN auth_user u on u.id = o.user_id
                     WHERE s.status not in ('complete',
                                            'unavailable',
                                            'purged')
                     GROUP BY u.username, u.email, u.first_name, u.last_name
                     ORDER BY "Total Running" DESC'''
    },
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
    'orders_by_product_status': {
        'display_name': 'Orders By Product Status',
        'description': 'Shows orders by product status',
        'query': r'''SELECT o.order_date "Date Ordered",
                     o.orderid "Order ID",
                     COUNT(s.name) "Scene Count",
                     s.status "Status"
                     FROM ordering_order o
                     JOIN ordering_scene s ON o.id = s.order_id
                     WHERE s.status IN ('processing', 'queued',
                                        'oncache', 'onorder', 'error')
                     GROUP BY o.orderid,
                              o.order_date,
                              s.status
                     ORDER BY
                         CASE s.status WHEN 'processing' then 1
                                       WHEN 'queued' THEN 2
                                       WHEN 'oncache' THEN 3
                                       WHEN 'onorder' THEN 4
                                       WHEN 'error' THEN 5
                                       WHEN 'retry' THEN 6
                                       WHEN 'submitted' THEN 7
                                       ELSE 8 END,
                         o.order_date ASC'''
    },

    'order_position_in_line': {
        'display_name': 'Order Queue Position',
        'description': 'Shows orders and scenes with status',
        'query': r'''SELECT o.order_date "date ordered",
                     o.orderid "Order ID",
                     COUNT(s.name) "Scene Count",
                     SUM(CASE when s.status in ('complete', 'unavailable') then 1 else 0 end) "Complete",
                     SUM(CASE when s.status = 'processing' then 1 ELSE 0 END) "Processing",
                     SUM(CASE when s.status = 'error' then 1 ELSE 0 END) "Error",
                     u.username "user name"
                     FROM ordering_scene s, ordering_order o, auth_user u
                     WHERE o.id = s.order_id
                     AND u.id = o.user_id
                     AND o.status = 'ordered'
                     GROUP BY
                     o.orderid,
                     u.username,
                     o.order_date 
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
                     q.running "Currently Running Count"
                     FROM ordering_scene s,
                          ordering_order o,
                          auth_user u,
                          order_queue q
                     WHERE u.id = o.user_id
                     AND o.id = s.order_id
                     AND o.status = 'ordered'
                     AND s.status = 'oncache'
                     AND q.email = u.email
                     ORDER BY q.running ASC, o.order_date ASC'''
     },
     'scenes_by_status': {
         'display_name': 'Scene Status Counts',
         'description': 'Displays all current status with counts for each',
         'query': r'''SELECT status,
                      COUNT(status)
                      FROM ordering_scene
                      GROUP BY status'''
     },
     'product_completion_log': {
         'display_name': 'Product Completion Log',
         'description': 'Show the last 100 products that have completed',
         'query': r'''SELECT s.completion_date "Completion Date", 
                      u.username "Username", 
                      o.orderid "Order ID", 
                      s.name "Product Name"
                      FROM auth_user u 
                      JOIN ordering_order o on u.id = o.user_id 
                      JOIN ordering_scene s on o.id = s.order_id 
                      WHERE s.completion_date IS NOT NULL 
                      AND o.status != 'purged' 
                      AND s.status != 'purged' 
                      ORDER BY s.completion_date DESC LIMIT 100'''
     },
     'users_with_orders_count' :{
         'display_name': 'Waiting User Count',
         'description': 'Number of users that are waiting on products',
         'query': r'''SELECT 
                      COUNT(DISTINCT u.username) 
                      FROM auth_user u 
                      JOIN ordering_order o ON o.user_id = u.id 
                      JOIN ordering_scene s ON s.order_id = o.id 
                      WHERE s.status IN 
                          ('queued', 'processing', 'oncache', 
                          'onorder', 'error', 'retry', 'submitted')'''
     },
     'machine_performance': {
         'display_name': 'Machine Performance',
         'description': 'Number of completions by machine past 24 hours',
         'query': r'''SELECT processing_location, COUNT(*)
                      FROM ordering_scene s 
                      WHERE s.status = 'complete' 
                      AND  completion_date > now() - interval '24 hours'  
                      GROUP BY processing_location'''
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

        query = reports[name]['query']
        if query is not None and len(query) > 0:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return dictfetchall(cursor)
        else:
            print("query was empty for {0}: {1}".format(name, query))
            return {}

listing = lambda x=None: Report().listing()
run = lambda name: Report().run(name)
display_name = lambda name: reports[name]['display_name']
