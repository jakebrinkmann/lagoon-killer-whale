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

from ordering import core
from ordering.models.configuration import Configuration as config

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
    try:
        resp = core.update_status(name, orderid, processing_loc, status)
        return resp
    except Exception, e:
        logger.exception('Exception on call to _update_status')
        raise e


def _set_product_error(name, orderid, processing_loc, error):
    try:
        return core.set_product_error(name, orderid, processing_loc, error)
    except Exception, e:
        logger.exception('Exception in _set_product_error')
        raise e


def _set_product_unavailable(name, orderid, processing_loc, error, note):
    try:
        return core.set_product_unavailable(name,
                                            orderid,
                                            processing_loc,
                                            error,
                                            note)
    except Exception, e:
        logger.exception('Exception in _set_product_unavailable')
        raise e


def _queue_products(order_name_tuple_list, processing_location, job_name):
    try:
        return core.queue_products(order_name_tuple_list,
                                   processing_location,
                                   job_name)
    except Exception, e:
        logger.exception('Exception in _queue_products()')
        raise e


def _mark_product_complete(name,
                           orderid,
                           processing_loc,
                           completed_scene_location,
                           cksum_file_location,
                           log_file_contents_binary):

    try:
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
    except Exception, e:
        logger.exception('Exception in _mark_product_complete()')
        raise e


def _handle_orders():

    try:    
        key = '_handle_orders_lock'
        timeout = int(config.get('cache.key.handle_orders_lock_timeout'))
    
        logger.debug('Ready for caching with key {0} '
                     ' and a timeout of {1}'.format(key, timeout))

        results = True
        logger.info('handle orders triggered...')
        if cache.get(key) is None:
            logger.debug('Cache key {0} was None...'.format(key))
            cache.set(key, '', timeout)
            results = core.handle_orders()

            cache.delete(key)
        else:
            logger.debug('handle_orders was locked, skipping call to core')

        return results
    except Exception, e:
        logger.exception('Exception occurred in _handle_orders()')
        raise e


#method to expose master configuration repository to the system
def _get_configuration(key):
    try:
        return config.get(key)
    except Exception, e:
        logger.exception('Exeption in _get_configuration()')
        raise e


def _get_products_to_process(limit, for_user, priority, product_types):
    try:
        return core.get_products_to_process(record_limit=limit,
                                            for_user=for_user,
                                            priority=priority,
                                            product_types=product_types,
                                            encode_urls=True)
    except Exception, e:
        logger.exception('Exception in _get_products_to_process')
        raise e

