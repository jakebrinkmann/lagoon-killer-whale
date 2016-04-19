
import json

def api_get_user(url, response_type='json', json=None, uauth=None):
    return {'username': 'bob'}


def api_get_user_fail(url, response_type='json', json=None, uauth=None):
    return {'msg': 'user not found'}


def api_get_list_orders(*args, **kwargs):
    return [{'orderid': 'abc', 'products_ordered': 1,
             'products_complete': 1, 'order_status': 'complete',
             'order_note': 'comments'}]


def api_get_order_status(*args):
    if 'order' in args[0]:
        orderid = args[0].split("/").pop()
        product_opts = {"etm7": {"inputs": ["LE70270292003144EDC00"],
                                 "products": ["source_metadata", "l1", "sr_nbr2", "cloud", "toa"]},
                        "format": "gtiff",
                        "resize": {"pixel_size": 1000, "pixel_size_units": "meters"},
                        "projection": {"utm": {"zone": 15, "zone_ns": "north"}},
                        "resampling_method": "nn"}
        return {'orderid': orderid, 'product_opts': product_opts}
    else:
        # going after item-status
        return {'orderid': {'bob@google.com-12345-9876': [{'id': 4, 'status': 'complete'}]}}


def api_post_order(*args):
    class JSpoof(object):
        def __init__(self, indict):
            self.value = indict

        @property
        def status_code(self):
            return 200

        def json(self):
           return self.value

    if 'available-products' in args[0]:
        avail_prods = {'tm4': {'inputs': ['LT42181092013069PFS00'],
                                'outputs': ['source_metadata', 'l1', 'toa', 'bt', 'cloud',
                                            'sr', 'swe', 'sr_ndvi', 'sr_evi', 'sr_msavi',
                                            'sr_ndmi', 'sr_nbr', 'sr_nbr2', 'stats']}}
        ap = JSpoof(avail_prods)
    else:
        # test is posting an order
        ap = JSpoof({'orderid': 'bob@google.com-03072016-085432'})
    return ap

def api_get_system_config(*args):
    return {'retry.lta_soap_errors.timeout': '3600',
            'retry.retry_missing_l1.retries': '8',
            'url.dev.modis.datapool': 'e4ftl01.cr.usgs.gov'}

def api_post_status(*args):
    class JSpoof(object):
        def __init__(self, indict):
            self.value = indict

        @property
        def status_code(self):
            return 200

        def json(self):
            return self.value

    return JSpoof({'foo':'bar'})


def update_status_details_true():
    return True


def api_get_reports(*args):
    return {u'backlog_input_product_types':
                {u'query': u'',
                 u'display_name': u'Backlog - Input Types',
                 u'description': u'Input product type counts'},
            u'product_counts':
                {u'query': u'',
                 u'display_name': u'Products - Counts',
                 u'description': u'Active product totals per user'},
            u'order_counts':
                {u'query': u'',
                 u'display_name': u'Orders - Counts',
                 u'description': u'Orders and status per user'},
            u'scheduling_next_up':
                {u'query': u'',
                 u'display_name': u'Scheduling - Next Up',
                 u'description': u'Shows products that will be scheduled to run next'}
            }


def api_get_stats_all(*args):
    return {'stat_open_orders': 1,
            'stat_products_complete_24_hrs': 9,
            'stat_waiting_users': 99,
            'stat_backlog_depth': 100}


def api_get_show_report(*args):
    return "[OrderedDict([('Total Orders', 11L), " \
           "('Complete', 1L), ('Open', 10L), ('Email', 'cgaustin@usgs.gov'), " \
           "('First Name', 'clay'), ('Last Name', 'austin')]), " \
           "OrderedDict([('Total Orders', 4L), ('Complete', 0L), ('Open', 4L), " \
           "('Email', 'klsmith@usgs.gov'), ('First Name', 'Kelcy'), ('Last Name', 'Smith')]), " \
           "OrderedDict([('Total Orders', 2L), ('Complete', 0L), ('Open', 2L), " \
           "('Email', 'dhill@usgs.gov'), ('First Name', 'David'), ('Last Name', 'Hill')]), " \
           "OrderedDict([('Total Orders', 2L), ('Complete', 0L), ('Open', 2L), " \
           "('Email', 'dhill@usgs.gov'), ('First Name', ''), ('Last Name', '')]), " \
           "OrderedDict([('Total Orders', 1L), ('Complete', 0L), ('Open', 1L), " \
           "('Email', 'rdilley@usgs.gov'), ('First Name', 'Ron'), ('Last Name', 'Dilley')])]"

form_order = {'projection|utm|zone_ns': 'north',
              'resize|pixel_size_units': 'meters',
              'projection': 'on',
              'source_metadata': 'on',
              'format': 'gtiff',
              'image_extents|west': '',
              'resize|pixel_size': '1000',
              'l1': 'on',
              'target_projection': 'utm',
              'resampling_method': 'nn',
              'image_extents|east': '',
              'image_extents|south': '',
              'projection|utm|zone': '15',
              'note': '',
              'sr_nbr2': 'on',
              'resize': 'on',
              'image_extents|units': 'dd',
              'toa': 'on',
              'cloud': 'on',
              'image_extents|north': ''}


base_order = {'projection': {'lonlat': None},
                'image_extents': {'units': 'dd',
                                  'west': 0,
                                  'east': 0.002695,
                                  'north': 0.002695,
                                  'south': 0},
                'format': 'gtiff',
                'resampling_method': 'cc',
                'plot_statistics': True,
                'resize': {'pixel_size_units': 'dd',
                           'pixel_size': 0.0002695},
                'myd13a2': {'inputs': ['MYD13A2.A2000072.h02v09.005.2008237032813'],
                            'products': ['l1', 'stats']},
                'myd09gq': {'inputs': ['MYD09GQ.A2000072.h02v09.005.2008237032813'],
                            'products': ['l1', 'stats']},
                'tm4': {'inputs': ['LT42181092013069PFS00'],
                        'products': ['source_metadata', 'l1', 'toa', 'bt','cloud',
                                     'sr', 'swe', 'sr_ndvi', 'sr_evi', 'sr_msavi',
                                     'sr_ndmi', 'sr_nbr', 'sr_nbr2', 'stats']}}
