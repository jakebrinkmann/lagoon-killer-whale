'''
core.py
Purpose: Holds common logic needed between views.py and api.py
Original Author: David V. Hill
'''


from models import Scene
from models import Order
from models import Configuration
from models import UserProfile
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction

import json
import datetime
import lta

import common


def frange(start,end,step):
    '''Provides Python range functions over floating point values'''
    return [x*step for x in range(int(start * 1./step), int(end * 1./step))]


# Sends the order submission confirmation email
def send_initial_email(order):

    status_base_url = Configuration().getValue('espa.status.url')

    status_url = ('%s/%s') % (status_base_url, order.user.email)

    m = list()
    m.append("Thank you for your order (%s).  " % order.orderid)
    m.append("Your order has been received and is currently ")
    m.append("being processed.  ")
    m.append("You will receive an email notification when all units on this ")
    m.append("order have been completed.\n\n")
    m.append("You can check the status of your order and download already ")
    m.append("completed scenes directly from %s\n\n" % status_url)
    m.append("Requested scenes:\n")

    scenes = Scene.objects.filter(order__id=order.id)

    for s in scenes:
        m.append("%s\n" % s.name)

    email_msg = ''.join(m)

    common.util.send_email(recipient=order.user.email,
                           subject='Processing Order Received',
                           body=email_msg)


def send_completion_email(email, ordernum, readyscenes=[]):

    config = Configuration()

    status_base_url = config.getValue('espa.status.url')

    config = None

    status_url = ('%s/%s') % (status_base_url, email)
    m = list()
    m.append("Your order is now complete and can be downloaded ")
    m.append("from %s.\n" % status_url)
    m.append("This order will remain available for 14 days.  ")
    m.append("Any data not downloaded will need to be reordered ")
    m.append("after this time.\n")
    m.append("Please contact Customer Services at 1-800-252-4547 or ")
    m.append("email custserv@usgs.gov with any questions.\n")
    m.append("Your scenes\n")
    m.append("-------------------------------------------\n")
    for r in readyscenes:
        m.append("%s\n" % r)

    #build the email message with the input_product_list tacked onto it
    email_msg = ''.join(m)

    #for r in readyscenes:
        #msg = msg.join([r, '\n'])
    #    msg = msg + r + '\n'

    common.util.send_email(recipient=email,
                           subject='Processing for %s Complete' % ordernum,
                           body=email_msg)


def scenes_on_cache(input_product_list):
    """Proxy method call to determine if the scenes in question are on disk

    Keyword args:
    input_product_list -- A Python list of scene identifiers

    Returns:
    A subset of scene identifiers
    """
    return common.util.scenecache_client().scenes_exist(input_product_list)


def scenes_are_nlaps(input_product_list):
    """Proxy method call to determine if the scenes are nlaps scenes

    Keyword args:
    input_product_list -- A Python list of scene identifiers

    Return:
    A subset of scene identifiers
    """
    return common.util.scenecache_client().is_nlaps(input_product_list)


def get_landsat_products_to_process():
    pass

def get_modis_products_to_process():
    pass

@transaction.atomic
def get_scenes_to_process():
    # sanity checks

    # load up any orders from ee that are waiting for us.
    if settings.DEBUG:
        print("Load ee orders")
    load_ee_orders()

    # are there even any scenes to handle?
    statuses = ['submitted', 'onorder', 'oncache']

    if Scene.objects.filter(status__in=statuses).count() <= 0:
        return []

    # is cache online?
    if not common.util.scenecache_is_alive():
        print("Could not contact the scene cache...")
        raise Exception("Could not contact the scene cache...")

    # the cache is online and there are scenes to process...

    # get all the scenes that are in submitted status in the order in which
    # they were placed... limit to 500 at once

    submitted = Scene.objects.filter(status='submitted')\
        .order_by('order__order_date')[:500]

    if submitted:
        if settings.DEBUG:
            print("Found %i submitted scenes" % len(submitted))

        #check to see which ones are sitting on cache
        submitted_list = [s.name for s in submitted]

         # find all the submitted scenes that are nlaps and reject them
        nlaps_scenes = scenes_are_nlaps(submitted_list)

        if settings.DEBUG:
            print("Found %i nlaps scenes" % len(nlaps_scenes))

        # bulk update the nlaps scenes
        if len(nlaps_scenes) > 0:
            Scene.objects.filter(status='submitted', name__in=nlaps_scenes)\
                .update(status='unavailable',
                        completion_date = datetime.datetime.now(),
                        note='TMA data cannot be processed')

        # find all the submitted scenes that are available in the tm/etm
        # dirs on the online cache
        oncache_scenes = scenes_on_cache(submitted_list)

        if settings.DEBUG:
            print("Found %i oncache scenes" % len(nlaps_scenes))

        # bulk update the oncache scene status
        if len(oncache_scenes) > 0:
            Scene.objects.filter(status='submitted', name__in=oncache_scenes)\
                .update(status='oncache')

        # placeholder list for all the scenes that are not nlaps but are
        # not oncache
        need_to_order = set(submitted_list) - set(nlaps_scenes)

        need_to_order = set(need_to_order) - set(oncache_scenes)

        if settings.DEBUG:
            print("Found %i scenes to order" % len(need_to_order))

        # Need to run another query because the calls to order_scenes require
        # the user contactid.  We don't want to make 500 separate calls to the
        # EE service so this will allow us to group all the scenes by
        # the order and thus the contactid

        # this resultset is only a dict of orderids, not a normal queryset
        # result
        orders = Scene.objects.filter(status='submitted',
                                      name__in=need_to_order)\
            .values('order').distinct()

        order_wrapper = lta.OrderWrapperServiceClient()

        # look through the Orders that are part of this 500 scene set
        # and place one order with lta for each one that has scenes that
        # need to be ordered
        #
        # The response that comes back is a dictionary with
        # the lta_order_id key and a list of scene names in a key 'ordered'
        # Two other lists may exist as well, 'invalid' and 'available'
        # The lta_order_id and 'ordered' lists are either both present or
        # missing if nothing was ordered.
        # The other two lists may or may not exist as well depending on if
        # there are any scenes in those statuses
        for o in orders:
            eo = Order.objects.get(id=o.get('order'))

            try:
                contactid = None
                contactid = eo.user.userprofile.contactid
            except Exception, e:
                print("Exception getting contactid for user:%s"
                      % eo.user.username)
                print(e)

            if not contactid:
                print("No contactid associated with order:%s... skipping"
                      % o.get('order'))
                continue

            eo_scenes = eo.scene_set.filter(status='submitted').values('name')

            eo_scene_list = [s.get('name') for s in eo_scenes]

            if settings.DEBUG:
                print("Ordering  %i scenes" % len(eo_scene_list))
                print eo_scene_list

            if len(eo_scene_list) > 0:
                resp_dict = order_wrapper.order_scenes(eo_scene_list,
                                                       contactid)

                if settings.DEBUG:
                    print("Resp dict")
                    print(resp_dict)

                if 'ordered' in resp_dict:
                    eo.scene_set.filter(status='submitted',
                                        name__in=resp_dict['ordered'])\
                        .update(status='onorder',
                                tram_order_id=resp_dict['lta_order_id'])

                if 'invalid' in resp_dict:
                    eo.scene_set.filter(status='submitted',
                                        name__in=resp_dict['invalid'])\
                        .update(status='unavailable',
                                completion_date = datetime.datetime.now(),
                                note='Not found in landsat archive')

                if 'available' in resp_dict:
                    eo.scene_set.filter(status='submitted',
                                        name__in=resp_dict['available'])\
                        .update(status='oncache')

    ''' This completes handling all the scenes that were in submitted status
    TODO -- Create new method handle_submitted_scenes() or something to that
    effect.  get_scenes_to_process down to this comment should be included
    in it.

    The rest of this method down should actually be 'get_scenes_to_process()'

    TODO -- renamed this module 'actions.py'
    TODO -- OO'ize the order handling into OrderHandler()
    TODO -- Encapsulate all models.py classes here... don't let them flow
    TODO --     up into the callers of this module.
    TODO -- OrderHandler().get_scenes_to_process()
    TODO -- OrderHandler().determine_disposition()
    TODO -- OrderHandler().cancel(Order())
    TODO -- OrderHandler().cancel(Order(), ProductSensor())
    TODO -- OrderHandler().cleanup(Order())
    TODO -- OrderHandler().status(Order())
    TODO -- OrderHandler().status(Order(), ProductSensor())

    TODO -- Build HadoopHandler() as well.
    TODO -- HadoopHandler().cluster_status()
    TODO -- HadoopHandler().cancel_job(jobid)
    '''

    # Now going to go through and check for scenes that were in onorder status
    # and then go ahead and build the actual response for this method

    # Check all onorder scenes and update if they are oncache
    ordered_scenes = Scene.objects.filter(status='onorder')

    if ordered_scenes:
        #oncache2 = cache.has_scenes(ordered_list)
        oncache2 = scenes_on_cache([s.name for s in ordered_scenes])

        ordered_scenes.filter(name__in=oncache2).update(status='oncache')

    #don't do anything with the ones that weren't oncache.
    #They remain on order.
    #
    #Now the database should be fully updated
    #with the current status.
    #
    #Pull the current oncache set from the db
    #and include it as the result
    results = []

    # get 500 scenes ready to be processed in the order in which they were
    # submitted
    available_scenes = Scene.objects.filter(status='oncache')\
        .order_by('order__order_date')[:500]

    if available_scenes:

        for a in available_scenes:
            order = a.order
            options = json.loads(order.product_options)
            oid = order.orderid

            orderline = json.dumps(
                {'orderid': oid, 'scene': a.name, 'options': options})

            results.append(orderline)

    return results


'''
def purge_expired_orders():
    config = None
    username  = None
    password = None
    host = None
    port = None
    ds = None
    orders = None

    try:
        cutoff = datetime.datetime.now() - timedelta(days=14)
        #get orders where status == complete and
        #that were completed > than 14 days ago
        orders = Order.objects.raw('select * from ordering_order oo \
        where oo.id not in \
        (select order_id from ordering_scene where status in \
        ("queued","onorder","processing","distributing","oncache","purged"))')

        config = Configuration()
        username = config.getValue('distrods.user')
        password = config.getValue('distrods.password')
        host = config.getValue('distrods.host')
        port = config.getValue('distrods.port')
        ds = DistributionDataSource(None, None, username, password, host, port)
        for o in orders:
            diff = cutoff - o.completion_date
            if diff.days >= 0:
                scenes = Scene.objects.filter(order__id = o.id)
                for s in scenes:
                    ds.delete(s.name, s.product_distro_location)
                o.delete()
    finally:
        config = None
        username  = None
        password = None
        host = None
        port = None
        ds = None
        orders = None
'''


# Simple logger method for this module
def helper_logger(msg):
    print(msg)
    #h = open('/tmp/helper.log', 'a+')
    #h.write(msg)
    #h.flush()
    #h.close()
    #pass


@transaction.atomic
def update_status(name, orderid, processing_loc, status):

    helper_logger("Updating scene:%s order:%s from location:%s to %s\n"
                  % (name, orderid, processing_loc, status))

    try:
        s = Scene.objects.get(name=name, order__orderid=orderid)
        if s:
            helper_logger("Running update query for %s.  Setting status to:%s"
                          % (s.name, status))

            s.status = status
            s.processing_location = processing_loc
            s.log_file_contents = ""
            s.save()
            s = None
            return True
        else:
            helper_logger("Scene[%s] not found in order[%s]"
                          % (name, orderid))

            return False
    except Exception, e:
        helper_logger("Exception in updateStatus:%s" % e)


@transaction.atomic
#  Marks a scene in error and accepts the log file contents
def set_scene_error(name, orderid, processing_loc, error):
    o = Order.objects.get(orderid=orderid)
    s = Scene.objects.get(name=name, order__id=o.id)
    if s:
        s.status = 'error'
        s.processing_location = processing_loc
        s.log_file_contents = error
        s.save()
        return True
    else:
        #something went wrong, don't clean up other disk.
        if settings.DEBUG:
            print("Scene[%s] not found in Order[%s]" % (name, orderid))

        return False


@transaction.atomic
#  Marks a scene unavailable and stores a reason
def set_scene_unavailable(name, orderid, processing_loc, error, note):
    o = Order.objects.get(orderid=orderid)
    s = Scene.objects.get(name=name, order__id=o.id)
    if s:
        s.status = 'unavailable'
        s.processing_location = processing_loc
        s.completion_date = datetime.datetime.now()
        s.log_file_contents = error
        s.note = note
        s.save()

        if o.order_source == 'ee':
            #update ee
            client = lta.OrderUpdateServiceClient()

            client.update_order(o.ee_order_id, s.ee_unit_id, 'R')

        return True
    else:
        #something went wrong, don't clean up other disk.
        msg = "Scene[%s] not found in Order[%s]" \
              % (name, orderid)

        print(msg)

        return False


@transaction.atomic
#  Marks a scene complete in the database for a given order
def mark_scene_complete(name,
                        orderid,
                        processing_loc,
                        completed_file_location,
                        destination_cksum_file=None,
                        log_file_contents=""):

    print ("Marking scene:%s complete for order:%s" % (name, orderid))
    o = Order.objects.get(orderid=orderid)
    s = Scene.objects.get(name=name, order__id=o.id)
    if s:
        s.status = 'complete'
        s.processing_location = processing_loc
        s.product_distro_location = completed_file_location
        s.completion_date = datetime.datetime.now()
        s.cksum_distro_location = destination_cksum_file

        s.log_file_contents = log_file_contents

        base_url = Configuration().getValue('distribution.cache.home.url')

        product_file_parts = completed_file_location.split('/')
        product_file = product_file_parts[len(product_file_parts) - 1]
        cksum_file_parts = destination_cksum_file.split('/')
        cksum_file = cksum_file_parts[len(cksum_file_parts) - 1]

        s.product_dload_url = ('%s/orders/%s/%s') % \
                              (base_url, orderid, product_file)

        s.cksum_download_url = ('%s/orders/%s/%s') % \
                               (base_url, orderid, cksum_file)

        s.save()

        if o.order_source == 'ee':
            #update ee
            client = lta.OrderUpdateServiceClient()
            client.update_order(o.ee_order_id, s.ee_unit_id, 'C')

        return True
    else:
        print("MarkSceneComplete:No scene was found with the name:%s" % name)
        return False


@transaction.atomic
def update_order_if_complete(order):
    '''Method to send out the order completion email
    for orders if the completion of a scene
    completes the order

    Keyword args:
    orderid -- id of the order

    '''
    complete_scene_status = ['complete', 'unavailable']

    o = None

    if type(order) == Order:
        o = order
    elif type(order) == str:
        #will raise Order.DoesNotExist
        o = Order.objects.get(orderid=order)
    else:
        msg = "%s must be of type models.ordering.Order or str" % order
        raise TypeError(msg)

    # find all scenes that are not complete
    scenes = o.scene_set.exclude(status__in=complete_scene_status)

    if len(scenes) == 0:
        # if this condition is true then the order is complete
        complete_scenes = o.scene_set.exclude(status='unavailable')
        scene_names = [s.name for s in complete_scenes]
        o.status = 'complete'
        o.completion_date = datetime.datetime.now()
        o.save()

        #only send the email if this was an espa order.
        if o.order_source == 'espa':
            order_email = o.user.email
            if not order_email:
                order_email = o.email

            sent = send_completion_email(order_email,
                                         o.orderid,
                                         readyscenes=scene_names)
            if sent:
                o.completion_email_sent = datetime.now()
                o.save()
            else:
                msg = "Could not send completion email to %s for order: %s" % \
                    (o.user.email, o.orderid)

                raise Exception(msg)


@transaction.atomic
def finalize_orders():
    '''Checks all open orders in the system and marks them complete if all
    required scene processing is done'''

    orders = Order.objects.filter(status='ordered')
    for o in orders:
        update_order_if_complete(o)

    return True

@transaction.atomic
def send_initial_emails():
    '''Finds all the orders that have not had their initial emails sent and
    sends them'''

    orders = Order.objects.filter(status='ordered')
    for o in orders:
        if not o.initial_email_sent():
            send_initial_email(o)
            o.initial_email_sent(datetime.datetime.now())


@transaction.atomic
def load_ee_orders():
    ''' Loads all the available orders from lta into
    our database and updates their status
    '''

    order_delivery = lta.OrderDeliveryServiceClient()

    registration = lta.RegistrationServiceClient()

    order_update = lta.OrderUpdateServiceClient()

    # This returns a dict that contains a list of dicts{}
    # key:(order_num, email, contactid) = list({sceneid:, unit_num:})
    orders = order_delivery.get_available_orders()

    # use this to cache calls to EE Registration Service username lookups
    local_cache = {}

    # Capture in our db
    for eeorder, email, contactid in orders:

        # create the orderid based on the info from the eeorder
        order_id = Order.generate_ee_order_id(email, eeorder)

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
                username = registration.get_username(contactid)
                local_cache[contactid] = username

            # now look the user up in our db.  Create if it doesn't exist
            # we'll want to put some caching in place here too
            try:
                user = User.objects.get(username=username)

                # make sure the email we have on file is current
                if not user.email or user.email is not email:
                    user.email = email
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
                user.email = email
                user.save()

                UserProfile(contactid=contactid, user=user).save()

            # We have a user now.  Now build the new Order since it
            # wasn't found.
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
            order.save()

        for s in orders[eeorder, email, contactid]:
            #go look for the scene by ee_unit_id.  This will stop
            #duplicate key update collisions

            scene = None
            try:
                scene = Scene.objects.get(order=order,
                                          ee_unit_id=s['unit_num'])

                if scene.status == 'complete':

                    success, msg, status =\
                        order_update.update_order(eeorder,
                                                  s['unit_num'],
                                                  "C")
                    if not success:
                        log_msg = "Error updating lta for \
                        [eeorder:%s ee_unit_num:%s \
                        scene name:%s order:%s" \
                        % (eeorder, s['unit_num'], scene.name, order.orderid)

                        helper_logger(log_msg)

                        log_msg = "Error detail: \
                        lta return message:%s  lta return \
                        status code:%s" % (msg, status)

                        helper_logger(log_msg)

                elif scene.status == 'unavailable':
                    success, msg, status =\
                        order_update.update_order(eeorder,
                                                  s['unit_num'],
                                                  "R")

                    if not success:
                        log_msg = "Error updating lta for \
                        [eeorder:%s ee_unit_num:%s \
                        scene name:%s order:%s" \
                        % (eeorder, s['unit_num'], scene.name, order.orderid)

                        helper_logger(log_msg)

                        log_msg = "Error detail: \
                        lta return message:%s  lta return \
                        status code:%s" % (msg, status)

                        helper_logger(log_msg)
            except Scene.DoesNotExist:
                scene = Scene()
                scene.name = s['sceneid']
                scene.ee_unit_id = s['unit_num']
                scene.order = order
                scene.order_date = datetime.datetime.now()
                scene.status = 'submitted'
                scene.save()

            # Update LTA
            success, msg, status =\
                order_update.update_order(eeorder,
                                          s['unit_num'],
                                          "I")
            if not success:
                log_msg = "Error updating lta for \
                [eeorder:%s ee_unit_num:%s scene \
                name:%s order:%s" % (eeorder, s['unit_num'],
                                     scene.name,
                                     order.orderid)

                helper_logger(log_msg)

                log_msg = "Error detail: lta return message:%s  \
                lta return status code:%s" % (msg, status)

                helper_logger(log_msg)