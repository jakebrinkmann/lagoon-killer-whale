'''
Purpose: exposes a system api for internal use only
Author: David V. Hill
'''

import logging
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings

from . import core
from .models import Configuration

logger = logging.getLogger(__name__)


@csrf_exempt
def rpc_handler(request):
    """
    the actual handler:
    if you setup your urls.py properly, all calls to the xml-rpc service
    should be routed through here.
    If post data is defined, it assumes it's XML-RPC and tries to process
     as such. Empty post assumes you're viewing from a browser and tells you
     about the service.
    """

    d = SimpleXMLRPCDispatcher(allow_none=True, encoding=None)

    if len(request.body):
        d.register_function(_update_status, 'update_status')
        d.register_function(_set_product_error, 'set_scene_error')
        d.register_function(_set_product_unavailable, 'set_scene_unavailable')
        d.register_function(_mark_product_complete, 'mark_scene_complete')
        d.register_function(_handle_orders, 'handle_orders')
        d.register_function(_queue_products, 'queue_products')
        d.register_function(_get_configuration, 'get_configuration')
        d.register_function(_get_products_to_process, 'get_scenes_to_process')
        d.register_function(_get_data_points, 'get_data_points')

        #response = HttpResponse(mimetype="application/xml")
        response = HttpResponse(content_type="application/xml")
        response.write(d._marshaled_dispatch(request.body))
    else:
        response = HttpResponse()
        response.write("<b>This is an XML-RPC Service.</b><br>")
        response.write("You need to invoke it using an XML-RPC Client!<br>")
        response.write("The following methods are available:<ul>")
        methods = d.system_listMethods()

        for method in methods:
            sig = d.system_methodSignature(method)

            # this just reads your docblock, so fill it in!
            help_msg = d.system_methodHelp(method)

            response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help_msg))

        response.write("</ul>")

    response['Content-length'] = str(len(response.content))
    return response


def _update_status(name, orderid, processing_loc, status):
        return core.update_status(name, orderid, processing_loc, status)


def _set_product_error(name, orderid, processing_loc, error):
    return core.set_product_error(name, orderid, processing_loc, error)


def _set_product_unavailable(name, orderid, processing_loc, error, note):
    return core.set_product_unavailable(name,
                                        orderid,
                                        processing_loc,
                                        error,
                                        note)


def _queue_products(order_name_tuple_list, processing_location, job_name):

    return core.queue_products(order_name_tuple_list,
                               processing_location,
                               job_name)


def _mark_product_complete(name,
                           orderid,
                           processing_loc,
                           completed_scene_location,
                           cksum_file_location,
                           log_file_contents_binary):

    log_file_contents = None
    if type(log_file_contents_binary) is str:
        log_file_contents = log_file_contents_binary
    else:
        log_file_contents = log_file_contents_binary.data

    return core.mark_product_complete(name,
                                      orderid,
                                      processing_loc,
                                      completed_scene_location,
                                      cksum_file_location,
                                      log_file_contents)


def _handle_orders():
    key = settings.CACHE_KEYS['handle_orders_lock']['key']
    timeout = settings.CACHE_KEYS['handle_orders_lock']['timeout']

    logger.debug('Ready for caching with key {0} '
                 ' and a timeout of {1}'.format(key, timeout))

    results = True
    logger.info('handle orders triggered...')
    if cache.get(key) is None:
        logger.debug('Cache key {0} was None...'.format(key))
        cache.set(key, '', timeout)
        results = core.handle_orders()

        #import time
        #logger.debug('sleeping for 20 seconds')
        #time.sleep(20)

        cache.delete(key)
    else:
        logger.debug('handle_orders was locked, skipping call to core')

    return results


#method to expose master configuration repository to the system
def _get_configuration(key):
    return Configuration().getValue(key)


def _get_products_to_process(limit, for_user, priority, product_types):

    return core.get_products_to_process(record_limit=limit,
                                        for_user=for_user,
                                        priority=priority,
                                        product_types=product_types,
                                        encode_urls=True)


def _get_data_points(tags=[]):
    return DataPoint.get_data_points(tags)
