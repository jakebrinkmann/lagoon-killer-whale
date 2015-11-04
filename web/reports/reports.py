from django.db import connection
from ordering.utilities import dictfetchall

reports = {
    'scene_report': {
        'display_name': 'Current Scene Report',
        'description': 'Shows the total scenes currently in the system by user',
        'query': r'''SELECT COUNT(s.name) "Total Scenes",
                   SUM(case when s.status in ('complete', 'unavailable') then 1 else 0 end) "Complete",
                   SUM(case when s.status not in ('complete', 'unavailable') then 1 else 0 end) "Processing",
                   u.email, u.first_name, u.last_name
                   FROM ordering_scene s, ordering_order o, auth_user u
                   WHERE s.order_id = o.id 
                   AND o.user_id = u.id 
                   AND s.status != 'purged' 
                   GROUP BY u.email, u.first_name, u.last_name 
                   ORDER BY "Total Scenes" DESC'''
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

}


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


