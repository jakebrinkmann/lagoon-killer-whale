import logging
from django.db import connection
from ordering.utilities import dictfetchall
import copy

logger = logging.getLogger(__name__)

REPORTS = {
    'machine_performance': {
        'display_name': 'Machines - 24 Hour Performance',
        'description': 'Number of completions by machine past 24 hours',
        'query': r'''SELECT processing_location "Machine", 
                     COUNT(*) "Count" 
                     FROM ordering_scene s 
                     WHERE s.status = 'complete' 
                     AND completion_date > now() - interval '24 hours' 
                     GROUP BY processing_location'''
    },
    'machine_product_status': {
        'display_name': 'Machines - Product Status',
        'description': 'Product status counts by machine',
        'query': r'''SELECT 
                     processing_location "Machine", 
                     SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) "Processing", 
                     SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) "Complete", 
                     SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) "Error", 
                     SUM(CASE WHEN status='retry' THEN 1 ELSE 0 END) "Retry" 
                     FROM ordering_scene 
                     WHERE status IN ('processing', 
                                      'complete', 
                                      'error', 
                                      'retry') 
                     GROUP BY processing_location 
                     ORDER BY processing_location'''
    },
    'retry_error': {
        'display_name': 'Retries & Errors',
        'description': 'All items in retry and error status with user notes',
        'query': r'''SELECT 
                     s.name "Name", 
                     o.orderid "Order ID", 
                     s.processing_location "Machine", 
                     s.status "Status", 
                     s.note "Note" 
                     FROM ordering_scene s 
                     JOIN ordering_order o ON 
                     o.id = s.order_id 
                     WHERE s.status 
                     IN ('retry', 'error') 
                     ORDER BY s.name'''
    },
    'order_counts': {
        'display_name': 'Orders - Counts',
        'description': 'Orders and status per user',
        'query': r'''SELECT COUNT(o.orderid) "Total Orders", 
                    SUM(case when o.status = 'complete' then 1 else 0 end) "Complete", 
                    SUM(case when o.status = 'ordered' then 1 else 0 end) "Open", 
                    u.email "Email", 
                    u.first_name "First Name", 
                    u.last_name "Last Name" 
                    FROM ordering_order o, auth_user u 
                    WHERE o.user_id = u.id 
                    AND o.status != 'purged' 
                    GROUP BY u.email, u.first_name, u.last_name 
                    ORDER BY "Total Orders" DESC'''
    },
    'orders_status': {
        'display_name': 'Orders - Status',
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
    'order_product_status': {
        'display_name': 'Orders - Product Status',
        'description': 'Shows orders and product counts by date',
        'query': r'''SELECT o.order_date "Date Ordered", 
                     o.orderid "Order ID", 
                     COUNT(s.name) "Scene Count", 
                     SUM(CASE when s.status in ('complete', 'unavailable') then 1 else 0 end) "Complete", 
                     SUM(CASE when s.status = 'processing' then 1 ELSE 0 END) "Processing", 
                     SUM(CASE when s.status = 'error' then 1 ELSE 0 END) "Error", 
                     u.username "User Name" 
                     FROM ordering_scene s,
                          ordering_order o,
                          auth_user u 
                     WHERE o.id = s.order_id 
                     AND u.id = o.user_id 
                     AND o.status = 'ordered' 
                     GROUP BY 
                         o.orderid, 
                         u.username, 
                         o.order_date 
                         ORDER BY o.order_date ASC''',
    },
    'product_counts': {
        'display_name': 'Products - Counts',
        'description': 'Active product totals per user',
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
    'product_completion_log': {
        'display_name': 'Products - Completion Log',
                        'description': 'Show the last 100 products that have completed',
                        'query': r'''SELECT
                                     s.completion_date "Completion Date", 
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
    'aggregate_product_counts': {
        'display_name': 'Products - Aggregate Counts',
        'description': 'Displays current status counts for all products',
        'query': r'''SELECT status,
                     COUNT(status)
                     FROM ordering_scene
                     GROUP BY status'''
    },
    'scheduling_running': {
        'display_name': 'Scheduling - Running',
        'description': 'Shows scheduling information for user product requests',
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
                     GROUP BY u.username, 
                              u.email, 
                              u.first_name, 
                              u.last_name 
                     ORDER BY "Total Running" DESC'''
    },
    'scheduling_next_up': {
        'display_name': 'Scheduling - Next Up',
        'description': 'Shows products that will be scheduled to run next',
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
    }
}


class Report(object):

    def listing(self, show_query=False):

        result = {}

        # make a copy of this as we dont want to modify the
        # actual dict in this module
        _reports = copy.deepcopy(REPORTS)

        for key, value in _reports.iteritems():
            if show_query is False:
                value['query'] = ''
            result[key] = value
        return result

    def run(self, name):

        if name not in REPORTS:
            raise NotImplementedError

        query = REPORTS[name]['query']

        if query is not None and len(query) > 0:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return dictfetchall(cursor)
        else:
            logger.error("Query was empty for {0}: {1}".format(name, query))
            return {}


listing = Report().listing

run = lambda name: Report().run(name)

display_name = lambda name: REPORTS[name]['display_name']
