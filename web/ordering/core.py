'''
core.py
Purpose: Holds all of espa-web's business logic
Original Author: David V. Hill
'''

import logging
import json
import datetime
import urllib
import os
from cStringIO import StringIO

from django.contrib.auth.models import User
from django.db import transaction
from django.db import IntegrityError
from django.db import connection
from django.core.cache import cache

from ordering.models.order import Scene
from ordering.models.order import Order
from ordering.models.configuration import Configuration as config
from ordering.models.user import UserProfile
from ordering import lta
from ordering import lpdaac
from ordering import errors
from ordering import emails
from ordering import nlaps
from ordering import sensor
from ordering import onlinecache
from ordering import utilities

logger = logging.getLogger(__name__)


@transaction.atomic
def set_product_retry(name,
                      orderid,
                      processing_loc,
                      error,
                      note,
                      retry_after,
                      retry_limit=None):
    '''Sets a product to retry status'''

    product = Scene.objects.get(name=name, order__orderid=orderid)

    #if a new retry limit has been provided, update the db and use it
    if retry_limit is not None:
        product.retry_limit = retry_limit

    if product.retry_count + 1 <= product.retry_limit:
        product.status = 'retry'
        product.retry_count = product.retry_count + 1
        product.retry_after = retry_after
        product.log_file_contents = error
        product.processing_loc = processing_loc
        product.note = note
        product.save()
    else:
        raise Exception("Retry limit exceeded")


@transaction.atomic
def set_product_unavailable(name, orderid, processing_loc, error, note):
    ''' Marks a scene unavailable and stores a reason '''

    product = Scene.objects.get(name=name, order__orderid=orderid)

    product.status = 'unavailable'
    product.processing_location = processing_loc
    product.completion_date = datetime.datetime.now()
    product.log_file_contents = error
    product.note = note
    product.save()

    if product.order.order_source == 'ee':
        #update ee
        lta.update_order_status(product.order.ee_order_id,
                                product.ee_unit_id, 'R')

    return True


def set_products_unavailable(products, reason):
    '''Bulk updates products to unavailable status and updates EE if
    necessary.

    Keyword args:
    products - A list of models.Scene objects
    reason - The user facing reason the product was rejected
    '''
    for p in products:
        if not isinstance(p, Scene):
            raise TypeError()

    for p in products:
        p.status = 'unavailable'
        p.completion_date = datetime.datetime.now()
        p.note = reason
        p.save()

        if p.order.order_source == 'ee':
            lta.update_order_status(p.order.ee_order_id, p.ee_unit_id, 'R')


@transaction.atomic
def handle_retry_products():
    ''' handles all products in retry status '''

    now = datetime.datetime.now()

    filter_args = {'status': 'retry',
                   'retry_after__lt': now}

    update_args = {'status': 'submitted',
                   'note': ''}

    Scene.objects.filter(**filter_args).update(**update_args)


@transaction.atomic
def handle_onorder_landsat_products():
    ''' handles landsat products still on order '''

    filters = {
        'tram_order_id__isnull': False,
        'status': 'onorder'
    }

    select_related = 'order'

    products = Scene.objects.filter(**filters).select_related(select_related)
    product_tram_ids = products.values_list('tram_order_id')
    tram_ids = list(set([p[0] for p in product_tram_ids]))

    rejected = []
    available = []

    for tid in tram_ids:
        order_status = lta.get_order_status(tid)

        # There are a variety of product statuses that come back from tram
        # on this call.  I is inprocess, Q is queued for the backend system,
        # D is duplicate, C is complete and R is rejected.  We are ignoring
        # all the statuses except for R and C because we don't care.
        # In the case of D (duplicates), when the first product completes, all
        # duplicates will also be marked C
        for unit in order_status['units']:
            if unit['unit_status'] == 'R':
                rejected.append(unit['sceneid'])
            elif unit['unit_status'] == 'C':
                available.append(unit['sceneid'])

    #Go find all the tram units that were rejected and mark them
    #unavailable in our database.  Note that we are not looking for
    #specific tram_order_id/sceneids as duplicate tram orders may have been
    #submitted and we want to bulk update all scenes that are onorder but
    #have been rejected
    if len(rejected) > 0:
        rejected_products = [p for p in products if p.name in rejected]
        set_products_unavailable(rejected_products,
                                 'Level 1 product could not be produced')

    #Now update everything that is now on cache
    filters = {
        'status': 'onorder',
        'name__in': available
    }
    updates = {
        'status': 'oncache',
    }

    if len(available) > 0:
        Scene.objects.filter(**filters).update(**updates)


def handle_submitted_landsat_products():
    ''' handles all submitted landsat products '''

    @transaction.atomic
    def mark_nlaps_unavailable():
        ''' inner function to support marking nlaps products unavailable '''

        logger.debug("In mark_nlaps_unavailable")

        #First things first... filter out all the nlaps scenes
        filters = {
            'status': 'submitted',
            'sensor_type': 'landsat'
        }

        logger.debug("Looking for submitted landsat products")

        landsat_products = Scene.objects.filter(**filters)

        logger.debug("Found {0} submitted landsat products"
                     .format(len(landsat_products)))

        landsat_submitted = [l.name for l in landsat_products]

        logger.debug("Checking for TMA data in submitted landsat products")

        # find all the submitted products that are nlaps and reject them
        landsat_nlaps = nlaps.products_are_nlaps(landsat_submitted)

        landsat_submitted = None

        logger.debug("Found {0} landsat TMA products"
            .format(len(landsat_nlaps)))

        # bulk update the nlaps scenes
        if len(landsat_nlaps) > 0:

            _nlaps = [p for p in landsat_products if p.name in landsat_nlaps]

            landsat_nlaps = None

            set_products_unavailable(_nlaps, 'TMA data cannot be processed')

    def get_contactids_for_submitted_landsat_products():

        logger.debug("Retrieving contact ids for submitted landsat products")

        filters = {
            'order__scene__status': 'submitted',
            'order__scene__sensor_type': 'landsat'
        }
        u = User.objects.filter(**filters)
        u = u.select_related('userprofile__contactid')
        contact_ids = u.values_list('userprofile__contactid').distinct()

        logger.debug("Found contact ids:{0}".format(contact_ids))

        return [c[0] for c in contact_ids]

    @transaction.atomic
    def update_landsat_product_status(contact_id):
        ''' updates the product status for all landsat products for the
        ee contact id '''

        logger.debug("Updating landsat product status")

        filters = {
            'status': 'submitted',
            'sensor_type': 'landsat',
            'order__user__userprofile__contactid': contact_id
        }

        #limit this to 500, 9000+ scenes are stressing EE
        products = Scene.objects.filter(**filters)[:500]
        product_list = [p.name for p in products]

        logger.debug("Ordering {0} scenes for contact:{1}"
                     .format(len(product_list), contact_id))

        results = lta.order_scenes(product_list, contact_id)

        logger.debug("Checking ordering results for contact:{0}"
                     .format(contact_id))

        if 'available' in results and len(results['available']) > 0:
            #update db
            filter_args = {
                'status': 'submitted',
                'name__in': results['available'],
                'sensor_type': 'landsat',
                'order__user__userprofile__contactid': contact_id
            }

            update_args = {'status': 'oncache'}

            Scene.objects.filter(**filter_args).update(**update_args)

        if 'ordered' in results and len(results['ordered']) > 0:
            #response = lta.order_scenes(orderable, contact_id)

            filter_args = {'status': 'submitted',
                           'name__in': results['ordered'],
                           'order__user__userprofile__contactid': contact_id}

            update_args = {'status': 'onorder',
                           'tram_order_id': results['lta_order_id']}

            Scene.objects.filter(**filter_args).update(**update_args)

        if 'invalid' in results and len(results['invalid']) > 0:
            #look to see if they are ee orders.  If true then update the
            #unit status

            invalid = [p for p in products if p.name in results['invalid']]

            set_products_unavailable(invalid, 'Not found in landsat archive')

    logger.info('Handling submitted landsat products...')

    #Here's the real logic for this handling submitted landsat products
    mark_nlaps_unavailable()

    for contact_id in get_contactids_for_submitted_landsat_products():
        try:
            logger.info("Updating landsat_product_status for {0}"
                        .format(contact_id))

            update_landsat_product_status(contact_id)

        except Exception, e:
            msg = ('Could not update_landsat_product_status for {0}\n'
                   'Exception:{1}'.format(contact_id, e))
            logger.exception(msg)


def handle_submitted_modis_products():
    ''' Moves all submitted modis products to oncache if true '''

    logger.info("Handling submitted modis products...")

    filter_args = {'status': 'submitted', 'sensor_type': 'modis'}
    modis_products = Scene.objects.filter(**filter_args)

    logger.debug("Found {0} submitted modis products"
                 .format(len(modis_products)))

    if len(modis_products) > 0:

        for product in modis_products:
            if lpdaac.input_exists(product.name) is True:
                product.status = 'oncache'
                product.save()
                logger.debug('{0} is on cache'.format(product.name))
            else:
                product.status = 'unavailable'
                product.note = 'not found in modis data pool'
                product.save()
                logger.debug('{0} was not found in the modis data pool'
                             .format(product.name))

@transaction.atomic
def handle_submitted_plot_products():
    ''' Moves plot products from submitted to oncache status once all
        their underlying rasters are complete or unavailable '''

    logger.info("Handling submitted plot products...")

    filter_args = {'status': 'ordered', 'order_type': 'lpcs'}
    plot_orders = Order.objects.filter(**filter_args)

    logger.debug("Found {0} submitted plot orders"
                 .format(len(plot_orders)))

    for order in plot_orders:
        product_count = order.scene_set.count()

        filter_args = {'status': 'complete'}
        complete_products = order.scene_set.filter(**filter_args).count()

        filter_args = {'status': 'unavailable'}
        unavailable_products = order.scene_set.filter(**filter_args).count()

        #if this is an lpcs order and there is only 1 product left that
        #is not done, it must be the plot product.  Will verify this
        #in next step.  Plotting cannot run unless everything else
        #is done.

        if product_count - (unavailable_products + complete_products) == 1:
            filter_args = {'status': 'submitted', 'sensor_type': 'plot'}
            plot = order.scene_set.filter(**filter_args)
            if len(plot) >= 1:
                for p in plot:
                    if complete_products == 0:
                        p.status = 'unavailable'
                        p.note = ('No input products were available for '
                                  'plotting and statistics')
                        logger.debug('No input products available for '
                                     'plotting in order {0}'
                                     .format(order.orderid))
                    else:
                        p.status = 'oncache'
                        p.note = ''
                        logger.debug("{0} plot is on cache"
                                     .format(order.orderid))
                    p.save()


@transaction.atomic
def handle_submitted_products():
    ''' handles all submitted products in the system '''

    logger.info('Handling submitted products...')
    handle_submitted_landsat_products()
    handle_submitted_modis_products()
    handle_submitted_plot_products()


@transaction.atomic
def get_products_to_process(record_limit=500,
                            for_user=None,
                            priority=None,
                            product_types=['landsat', 'modis'],
                            encode_urls=False):
    '''Find scenes that are oncache and return them as properly formatted
    json per the interface description between the web and processing tier'''

    logger.info('Retrieving products to process...')
    logger.debug('Record limit:{0}'.format(record_limit))
    logger.debug('Priority:{0}'.format(priority))
    logger.debug('For user:{0}'.format(for_user))
    logger.debug('Product types:{0}'.format(product_types))
    logger.debug('Encode urls:{0}'.format(encode_urls))

    buff = StringIO()
    buff.write('WITH order_queue AS ')
    buff.write('(SELECT u.email "email", count(name) "running" ')
    buff.write('FROM ordering_scene s ')
    buff.write('JOIN ordering_order o ON o.id = s.order_id ')
    buff.write('JOIN auth_user u ON u.id = o.user_id ')
    buff.write('WHERE ')
    buff.write('s.status in (\'queued\', \'processing\') ')
    buff.write('GROUP BY u.email) ')
    buff.write('SELECT ')
    buff.write('p.contactid, ')
    buff.write('s.name, ')
    buff.write('s.sensor_type, ')
    buff.write('o.orderid, ')
    buff.write('o.product_options, ')
    buff.write('o.priority, ')
    buff.write('o.order_date, ')
    buff.write('q.running ')
    buff.write('FROM ordering_scene s ')
    buff.write('JOIN ordering_order o ON o.id = s.order_id ')
    buff.write('JOIN auth_user u ON u.id = o.user_id ')
    buff.write('JOIN ordering_userprofile p ON u.id = p.user_id ')
    buff.write('LEFT JOIN order_queue q ON q.email = u.email ')
    buff.write('WHERE ')
    buff.write('o.status = \'ordered\' ')
    buff.write('AND s.status = \'oncache\' ')

    if product_types is not None and len(product_types) > 0:
        type_str = ','.join('\'{0}\''.format(x) for x in product_types)
        buff.write('AND s.sensor_type IN ({0}) '.format(type_str))

    if for_user is not None:
        buff.write('AND u.username = \'{0}\' '.format(for_user))

    if priority is not None:
        buff.write('AND o.priority = \'{0}\' '.format(priority))

    buff.write('ORDER BY q.running ASC, o.order_date ASC LIMIT {0}'.format(record_limit))

    '''
    buffer = StringIO()
    buffer.write('SELECT ')
    buffer.write('p.contactid, s.name, s.sensor_type, ')
    buffer.write('o.orderid, o.product_options, o.priority ')
    buffer.write('FROM ')
    buffer.write('ordering_order o, ')
    buffer.write('ordering_scene s, ')
    buffer.write('ordering_userprofile p, ')
    buffer.write('auth_user u ')
    buffer.write('WHERE ')
    buffer.write('o.user_id = u.id AND ')
    buffer.write('s.order_id = o.id AND ')
    buffer.write('u.id = p.user_id AND ')
    buffer.write('s.status = \'oncache\' ')

    if product_types is not None and len(product_types) > 0:
        type_str = ','.join('\'{0}\''.format(x) for x in product_types)
        buffer.write('AND s.sensor_type IN ({0}) '.format(type_str))

    if for_user is not None:
        buffer.write('AND u.username = \'{0}\' '.format(for_user))

    if priority is not None:
        buffer.write('AND o.priority = \'{0}\' '.format(priority))

    buffer.write('ORDER BY ')
    buffer.write('o.order_date ')
    buffer.write('LIMIT {0}'.format(record_limit))

    query = buffer.getvalue()
    buffer.close()
    '''
    query = buff.getvalue()
    buff.close()
    logger.info("QUERY:{0}".format(query))

    query_results = None
    cursor = connection.cursor()

    if cursor is not None:
        try:
            cursor.execute(query)
            query_results = utilities.dictfetchall(cursor)
        finally:
            if cursor is not None:
                cursor.close()

    # Need the results reorganized by contact id so we can get dload urls from
    # ee in bulk by id.
    by_cid = {}
    for result in query_results:
        cid = result.pop('contactid')
        # ['orderid', 'sensor_type', 'contactid', 'name', 'product_options']
        by_cid.setdefault(cid, []).append(result)

    #this will be returned to the caller
    results = []
    for cid in by_cid.keys():
        cid_items = by_cid[cid]

        landsat = [item['name'] for item in cid_items if item['sensor_type'] == 'landsat']
        logger.debug('Retrieving {0} landsat download urls for cid:{1}'
                     .format(len(landsat), cid))

        start = datetime.datetime.now()
        landsat_urls = lta.get_download_urls(landsat, cid)
        stop = datetime.datetime.now()
        interval = stop - start
        logger.debug('Retrieving download urls took {0} seconds'
                     .format(interval.seconds))
        logger.info('Retrieved {0} landat urls for cid:{1}'.format(len(landsat_urls), cid))

        modis = [item['name'] for item in cid_items if item['sensor_type'] == 'modis']
        modis_urls = lpdaac.get_download_urls(modis)

        logger.info('Retrieved {0} urls for cid:{1}'.format(len(modis_urls), cid))

        for item in cid_items:
            dload_url = None
            if item['sensor_type'] == 'landsat':
               
                 # check to see if the product is still available
                
                if ('status' in landsat_urls[item['name']] and
                        landsat_urls[item['name']]['status'] != 'available'):
                    try:
                        limit = config.get('retry.retry_missing_l1.retries')
                        timeout = config.get('retry.retry_missing_l1.timeout')
                        ts = datetime.datetime.now()
                        after = ts + datetime.timedelta(seconds=timeout)

                        logger.info('{0} for order {1} was oncache '
                                    'but now unavailable, reordering'
                                    #format(scene.name, scene.order.orderid))
                                    .format(item['name'], item['orderid']))

                        #set_product_retry(scene.name,
                        #                  scene.order.orderid,
                        #                  'get_products_to_process',
                        #                  'product was not available',
                        #                  'reorder missing level1 product',
                        #                  after, limit)
                        set_product_retry(item['name'],
                                          item['orderid'],
                                          'get_products_to_process',
                                          'product was not available',
                                          'reorder missing level1 product',
                                          after, limit)
                    except Exception:
   
                        logger.info('Retry limit exceeded for {0} in '
                                    'order {1}... moving to error status.'
                                    #.format(scene.name, scene.order.orderid))
                                    .format(item['name'], item['orderid']))

                        #set_product_error(scene.name, scene.order.orderid,
                        set_product_error(item['name'], item['orderid'],
                                          'get_products_to_process',
                                          ('level1 product data '
                                           'not available after EE call '
                                           'marked product as available'))
                    continue

                if 'download_url' in landsat_urls[item['name']]:
                    logger.info('download_url was in landsat_urls for {0}'.format(item['name']))
                    dload_url = landsat_urls[item['name']]['download_url']
                    if encode_urls:
                        dload_url = urllib.quote(dload_url, '')

            elif item['sensor_type'] == 'modis':
                if 'download_url' in modis_urls[item['name']]:
                    dload_url = modis_urls[item['name']]['download_url']
                    if encode_urls:
                        dload_url = urllib.quote(dload_url, '')

            result = {
                'orderid': item['orderid'],
                'product_type': item['sensor_type'],
                'scene': item['name'],
                'priority': item['priority'],
                'options': json.loads(item['product_options'])
            }

            if item['sensor_type'] == 'plot':
                # no dload url for plot items, just append it
                results.append(result)
            elif dload_url is not None:
                result['download_url'] = dload_url
                results.append(result)
            else:
                logger.info('dload_url for {0} in order {0} '
                            'was None, skipping...'
                            .format(item['orderid'], item['name']))
    return results


@transaction.atomic
def update_status(name, orderid, processing_loc, status):
    ''' updates scene/product status '''

    product = Scene.objects.get(name=name, order__orderid=orderid)

    product.status = status
    product.processing_location = processing_loc
    product.log_file_contents = ""
    product.save()

    return True


@transaction.atomic
def set_product_error(name, orderid, processing_loc, error):
    ''' Marks a scene in error and accepts the log file contents '''

    product = Scene.objects.get(name=name, order__orderid=orderid)

    #attempt to determine the disposition of this error
    resolution = errors.resolve(error, name)

    if resolution is not None:

        if resolution.status == 'submitted':
            product.status = 'submitted'
            product.note = ''
            product.save()
        elif resolution.status == 'unavailable':
            set_product_unavailable(product.name,
                                    product.order.orderid,
                                    processing_loc,
                                    error,
                                    resolution.reason)
        elif resolution.status == 'retry':
            try:
                set_product_retry(product.name,
                                  product.order.orderid,
                                  processing_loc,
                                  error,
                                  resolution.reason,
                                  resolution.extra['retry_after'],
                                  resolution.extra['retry_limit'])
            except Exception, e:
                logger.debug("Exception setting {0} to retry:{1}"
                             .format(name, e))
                product.status = 'error'
                product.processing_location = processing_loc
                product.log_file_contents = error
                product.save()
    else:
        product.status = 'error'
        product.processing_location = processing_loc
        product.log_file_contents = error
        product.save()

    return True


@transaction.atomic
def queue_products(order_name_tuple_list, processing_location, job_name):
    ''' Allows the caller to place products into queued status in bulk '''

    if not isinstance(order_name_tuple_list, list):
        msg = list()
        msg.append("queue_products expects a list of ")
        msg.append("tuples(order_id, product_id) for the first argument")
        raise TypeError(''.join(msg))

    # this should be a dictionary of lists, with order as the key and
    # the scenes added to the list
    orders = {}

    for order, product_name in order_name_tuple_list:
        if not order in orders:
            orders[order] = list()
        orders[order].append(product_name)

    # now use the orders dict we built to update the db
    for order in orders:
        products = orders[order]

        filter_args = {'name__in': products, 'order__orderid': order}

        update_args = {'status': 'queued',
                       'processing_location': processing_location,
                       'log_file_contents': '',
                       'job_name': job_name}

        Scene.objects.filter(**filter_args).update(**update_args)

    return True


@transaction.atomic
def mark_product_complete(name,
                          orderid,
                          processing_loc,
                          completed_file_location,
                          destination_cksum_file=None,
                          log_file_contents=""):

    ''' Marks a scene complete in the database for a given order '''
    logger.debug("Marking {0} complete for {1}".format(name, orderid))
    product = Scene.objects.get(name=name, order__orderid=orderid)

    product.status = 'complete'
    product.processing_location = processing_loc
    product.product_distro_location = completed_file_location
    product.completion_date = datetime.datetime.now()
    product.cksum_distro_location = destination_cksum_file
    product.log_file_contents = log_file_contents
    product.note = '' 

    base_url = config.url_for('distribution.cache')

    product_file_parts = completed_file_location.split('/')
    product_file = product_file_parts[len(product_file_parts) - 1]
    cksum_file_parts = destination_cksum_file.split('/')
    cksum_file = cksum_file_parts[len(cksum_file_parts) - 1]

    product.product_dload_url = ('%s/orders/%s/%s') % \
                                (base_url, orderid, product_file)

    product.cksum_download_url = ('%s/orders/%s/%s') % \
                                 (base_url, orderid, cksum_file)

    product.save()

    if product.order.order_source == 'ee':
        #update ee
        lta.update_order_status(product.order.ee_order_id,
                                product.ee_unit_id, 'C')
        return True


@transaction.atomic
def update_order_if_complete(order):
    '''Method to send out the order completion email
    for orders if the completion of a scene
    completes the order

    Keyword args:
    orderid -- id of the order

    '''
    complete_scene_status = ['complete', 'unavailable']

    if type(order) == str:
        #will raise Order.DoesNotExist
        order = Order.objects.get(orderid=order)
    elif type(order) == int:
        order = Order.objects.get(id=order)

    if not type(order) == Order:
        msg = "%s must be of type models.ordering.Order, int or str" % order
        raise TypeError(msg)

    # find all scenes that are not complete
    scenes = order.scene_set.exclude(status__in=complete_scene_status)

    if len(scenes) == 0:

        logger.info('Completing order: {0}'.format(order.orderid))
        order.status = 'complete'
        order.completion_date = datetime.datetime.now()
        order.save()

        #only send the email if this was an espa order.
        if order.order_source == 'espa' and not order.completion_email_sent:
            try:
                sent = None
                sent = send_completion_email(order)
                if sent is None:
                    logger.exception('Completeion email not sent for {0}'
                                     .format(order.orderid))
                    raise Exception("Completion email not sent")
                else:
                    order.completion_email_sent = datetime.datetime.now()
                    order.save()
            except Exception, e:
                #msg = "Error calling send_completion_email:{0}".format(e)
                logger.exception('Error calling send_completion_email')
                raise e


@transaction.atomic
def load_ee_orders():
    ''' Loads all the available orders from lta into
    our database and updates their status
    '''

    #check to make sure this operation is enabled.  Bail if not
    enabled = config.get("system.load_ee_orders_enabled")
    if enabled.lower() != 'true':
        logger.info('system.load_ee_orders_enabled is disabled,'
                    'skipping load_ee_orders()')
        return

    # This returns a dict that contains a list of dicts{}
    # key:(order_num, email, contactid) = list({sceneid:, unit_num:})
    orders = lta.get_available_orders()

    # use this to cache calls to EE Registration Service username lookups
    local_cache = {}

    # Capture in our db
    for eeorder, email_addr, contactid in orders:

        # create the orderid based on the info from the eeorder
        order_id = Order.generate_ee_order_id(email_addr, eeorder)

        # paranoia... initialize this to None since it's used in the loop.
        order = None

        # go look to see if it already exists in the db
        try:
            order = Order.objects.get(orderid=order_id)
        except Order.DoesNotExist:

            # retrieve the username from the EE registration service
            # cache this call
            if contactid in local_cache:
                username = local_cache[contactid]
            else:
                username = lta.get_user_name(contactid)
                local_cache[contactid] = username

            # now look the user up in our db.  Create if it doesn't exist
            # we'll want to put some caching in place here too
            try:
                user = User.objects.get(username=username)

                # make sure the email we have on file is current
                if not user.email or user.email is not email_addr:
                    user.email = email_addr
                    user.save()

                #try to retrieve the userprofile.  if it doesn't exist create
                try:
                    user.userprofile
                except UserProfile.DoesNotExist:
                    UserProfile(contactid=contactid, user=user).save()

            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from RegistrationServiceClient will.
                user = User(username=username, password='this isnt used')
                user.is_staff = False
                user.is_superuser = False
                user.email = email_addr
                user.last_login = datetime.datetime(year=1970, month=1, day=1)
                user.save()

                UserProfile(contactid=contactid, user=user).save()

            # We have a user now.  Now build the new Order since it
            # wasn't found.
            # TODO: This code should be housed in the models module.
            # TODO: This logic should not be visible at this level.
            order = Order()
            order.orderid = order_id
            order.user = user
            order.order_type = 'level2_ondemand'
            order.status = 'ordered'
            order.note = 'EarthExplorer order id: %s' % eeorder
            order.product_options = json.dumps(Order.get_default_ee_options(),
                                               sort_keys=True,
                                               indent=4)
            order.ee_order_id = eeorder
            order.order_source = 'ee'
            order.order_date = datetime.datetime.now()
            order.priority = 'normal'
            order.save()

        for s in orders[eeorder, email_addr, contactid]:
            #go look for the scene by ee_unit_id.  This will stop
            #duplicate key update collisions

            scene = None
            try:
                scene = Scene.objects.get(order=order,
                                          ee_unit_id=s['unit_num'])

                if scene.status == 'complete':

                    success, msg, status =\
                        lta.update_order_status(eeorder, s['unit_num'], "C")

                    if not success:
                        log_msg = ("Error updating lta for "
                                   "[eeorder:%s ee_unit_num:%s "
                                   "scene name:%s order:%s to 'C' status")
                        log_msg = log_msg % (eeorder, s['unit_num'],
                                             scene.name, order.orderid)

                        logger.error(log_msg)

                        log_msg = ("Error detail: lta return message:%s "
                                   "lta return status code:%s")
                        log_msg = log_msg % (msg, status)

                        logger.error(log_msg)

                elif scene.status == 'unavailable':
                    success, msg, status =\
                        lta.update_order_status(eeorder, s['unit_num'], "R")

                    if not success:
                        log_msg = ("Error updating lta for "
                                   "[eeorder:%s ee_unit_num:%s "
                                   "scene name:%s order:%s to 'R' status")
                        log_msg = log_msg % (eeorder, s['unit_num'],
                                             scene.name, order.orderid)

                        logger.error(log_msg)

                        log_msg = ("Error detail: "
                                   "lta return message:%s  lta return "
                                   "status code:%s") % (msg, status)

                        logger.error(log_msg)
            except Scene.DoesNotExist:
                # TODO: This code should be housed in the models module.
                # TODO: This logic should not be visible at this level.
                scene = Scene()

                product = None
                try:
                    product = sensor.instance(s['sceneid'])
                except Exception:
                    log_msg = ("Received product via EE that "
                               "is not implemented: %s" % s['sceneid'])
                    logger.warn(log_msg)
                    continue

                sensor_type = None

                if isinstance(product, sensor.Landsat):
                    sensor_type = 'landsat'
                elif isinstance(product, sensor.Modis):
                    sensor_type = 'modis'

                scene.sensor_type = sensor_type
                scene.name = product.product_id
                scene.ee_unit_id = s['unit_num']
                scene.order = order
                scene.order_date = datetime.datetime.now()
                scene.status = 'submitted'
                scene.save()

            # Update LTA
            success, msg, status =\
                lta.update_order_status(eeorder, s['unit_num'], "I")

            if not success:
                log_msg = ("Error updating lta for "
                           "[eeorder:%s ee_unit_num:%s scene "
                           "name:%s order:%s to 'I' status") % (eeorder,
                                                                s['unit_num'],
                                                                scene.name,
                                                                order.orderid)

                logger.error(log_msg)

                log_msg = ("Error detail: lta return message:%s  "
                           "lta return status code:%s") % (msg, status)

                logger.error(log_msg)


def send_initial_email(order):
    ''' public interface to send the initial email '''
    return emails.Emails().send_initial(order)


def send_completion_email(order):
    ''' public interface to send the completion email '''
    return emails.Emails().send_completion(order)


def send_initial_emails():
    ''' public interface to send all initial emails '''
    return emails.Emails().send_all_initial()


@transaction.atomic
def finalize_orders():
    '''Checks all open orders in the system and marks them complete if all
    required scene processing is done'''

    orders = Order.objects.filter(status='ordered')
    [update_order_if_complete(o) for o in orders]
    return True


def purge_orders(send_email=False):
    ''' Will move any orders older than X days to purged status and will also
    remove the files from disk'''

    days = config.get('policy.purge_orders_after')

    logger.info('Using purge policy of {0} days'.format(days))

    cutoff = datetime.datetime.now() - datetime.timedelta(days=int(days))

    orders = Order.objects.filter(status='complete')
    orders = orders.filter(completion_date__lt=cutoff)

    logger.info('Purging {0} orders from the active record.'
        .format(orders.count()))

    start_capacity = onlinecache.capacity()
    logger.info('Starting cache capacity:{0}'.format(start_capacity))

    for order in orders:
        try:
            with transaction.atomic():
                order.status = 'purged'
                order.save()
                for product in order.scene_set.all():
                    product.status = 'purged'
                    product.log_file_contents = ''
                    product.product_distro_location = ''
                    product.product_dload_url = ''
                    product.cksum_distro_location = ''
                    product.cksum_download_url = ''
                    product.job_name = ''
                    product.save()

                # bulk update product status, delete unnecessary field data
                logger.info('Deleting {0} from online cache disk'
                   .format(order.orderid))

                onlinecache.delete(order.orderid)
        except onlinecache.OnlineCacheException:
            logger.exception('Could not delete {0} from the online cache'
                .format(order.orderid))
        except Exception:
            logger.exception('Exception purging {0}'
                .format(order.orderid))

    end_capacity = onlinecache.capacity()
    logger.info('Ending cache capacity:{0}'.format(end_capacity))

    if send_email is True:
        logger.info('Sending purge report')
        emails.send_purge_report(start_capacity, end_capacity, orders)

    return True


def handle_orders():
    '''Logic handler for how we accept orders + products into the system'''
    send_initial_emails()
    handle_onorder_landsat_products()
    handle_retry_products()
    load_ee_orders()
    handle_submitted_products()
    finalize_orders()

    cache_key = 'orders_last_purged'
    result = cache.get(cache_key)

    # dont run this unless the cached lock has expired
    if result is None:
        logger.info('Purge lock expired... running')

        # first thing, populate the cached lock field
        timeout = int(config.get('system.run_order_purge_every'))
        cache.set(cache_key, datetime.datetime.now(), timeout)

        # purge the orders from disk now
        purge_orders(send_email=True)
    else:
        logger.info('Purge lock detected... skipping')
    return True


def dump_config(filepath):
    ''' Dumps the current configuration to a file that can then be imported
    using load_bootstrap '''

    if not os.path.exists(os.path.dirname(filepath)):
        logger.info('Creating {0}'.format(filepath))
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'wb') as output:
        items = config.objects.order_by('key')
        for item in items:
            entry = '{0}={1}\n'.format(item.key.strip(), item.value.strip())
            output.write(entry)
    
    os.chmod(filepath, 0444)


def load_config(filepath, delete_existing=False):
    ''' Loads configuration items from a file in the format of key=value '''
    ts = datetime.datetime.now()

    backup = '{0}-{1}{2}{3}-{4}:{5}.{6}'.format(filepath,
                                                ts.month,
                                                ts.day,
                                                ts.year,
                                                ts.hour,
                                                ts.minute,
                                                ts.second)

    logger.info('Creating backup of {0} at {1}'.format(filepath, backup))

    dump_config(backup)

    with open(filepath, 'rb') as bootstrap:

        logger.info('Checking {0} for bootstrap configuration'
            .format(filepath))

        data = bootstrap.readlines()

        if delete_existing == True:
            logger.info('Removing existing configuration')
            for item in config.objects.all():
                logger.info('Removing item:{0}:{1}'
                    .format(item.key, item.value))

                item.delete()

        for item in data:
            if (len(item) > 0 and item.find('=') != -1):
                parts = item.split('=')
                logger.info('Found item:{0}'.format(parts))

                key = parts[0].strip()
                val = parts[1].strip()

                logger.info("Loading {0}:{1} into Configuration()"
                       .format(key, val))
                
                config.objects.update_or_create(key=key,
                                                defaults={'key':key, 'value':val})

