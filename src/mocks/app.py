def api_up_user(url, response_type='json', json=None, uauth=None):
    return {'username': 'bob'}


def api_up_user_fail(url, response_type='json', json=None, uauth=None):
    return {'messages': {'errors': ['Invalid username/password']}}


def api_up_list_orders(*args, **kwargs):
    return []


def api_up_order_status(*args):
    url = args[0]
    if 'order' in url:
        orderid = url.split("/").pop()
        product_opts = {"etm7": {"inputs": ["LE70270292003144EDC00"],
                                 "products": ["source_metadata", "l1", "sr_nbr2", "toa"]},
                        "format": "gtiff",
                        "resize": {"pixel_size": 1000, "pixel_size_units": "meters"},
                        "projection": {"utm": {"zone": 15, "zone_ns": "north"}},
                        "resampling_method": "nn"}
        return {'orderid': orderid, 'product_opts': product_opts}
    elif 'item-status' in url:
        # going after item-status
        return {'orderid': {'bob@google.com-12345-9876': [{'id': 4, 'status': 'complete'}]}}


def api_post_order(*args, **kwargs):
    url = args[0]
    if 'available-products' in url:
        if 'json' in kwargs and 'inputs' in kwargs.get('json', ''):
            inputs = kwargs['json']['inputs']
        else:
            inputs = ['LT42181092013069PFS00']
        avail_prods = {'tm4': {'inputs': inputs,
                                'products': ['source_metadata', 'l1', 'toa', 'bt',
                                            'sr', 'swe', 'sr_ndvi', 'sr_evi', 'sr_msavi',
                                            'sr_ndmi', 'sr_nbr', 'sr_nbr2', 'stats']}}
        return avail_prods
    elif '/order' in url:
        # test is posting an order
        return {'orderid': 'bob@google.com-03072016-085432'}


def api_up_system_config(*args):
    return {'retry.lta_soap_errors.timeout': '3600',
            'retry.retry_missing_l1.retries': '8',
            'url.dev.modis.datapool': 'e4ftl01.cr.usgs.gov'}


def api_post_status(*args, **kwargs):
    return {'foo':'bar'}


def update_status_details_true():
    return True


def api_up_reports(*args):
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


def api_up_stats_all(*args):
    return {'stat_open_orders': 1,
            'stat_products_complete_24_hrs': 9,
            'stat_waiting_users': 99,
            'stat_backlog_depth': 100}


def api_up_show_report(*args):
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


def api_up_rss_feed(*args, **kwargs):
    url = args[0]
    if 'list-orders' in url:
        return ['bob@google.com-03072016-085432']
    elif 'item-status' in url:
        return {'bob@google.com-03072016-085432': [
                    {
                        "cksum_download_url": "http://espa.cr.usgs.gov/.../orders/.../LC080270272016072201T1-SC20160728135757.md5",
                        "completion_date": "2016-08-01T14:17:08.589621",
                        "name": "LE07_L1TP_010028_20050420_20160925_01_T1",
                        "note": "",
                        "product_dload_url": "http://downloadserver.com/LE70270292003144-SC20160411120638.tar.gz",
                        "status": "complete"
                    }
                ]
            }
    elif 'order' in url:
        return { "completion_date": "2016-08-01T14:47:08.589621",
                  "note": "",
                  "order_date": "2016-08-01T14:17:48.589621",
                  "orderid": 'bob@google.com-03072016-085432',
                  "priority": "normal",
                  "status": "complete"
                }


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
