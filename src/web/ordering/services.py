'''
TODO -- Create new method handle_submitted_scenes() or something to that effect
_process down to this comment should be included in it.

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

'''
class UserNotFoundException(Exception):
    pass

class ProductHandler(object):

    def __init__(self, product_id, order_handler):
        self.product_id = product_id
        self.order_handler = order_handler

    def check_ordered(self):
        pass

    def accept_submitted(self):
        pass

    def move_to_queued(self):
        pass

    def move_to_complete(self):
        pass

    def move_to_unavailable(self):
        pass

    def move_to_error(self):
        pass

    def move_to_retry(self):
        pass

    def move_to_submitted(self):
        pass

    def are_oncache(self):
        pass


class BulkProductHandler(object):

    def accept_submitted(self):
        pass

    def move_to_queued(self):
        pass

    def move_to_complete(self):
        pass

    def move_to_unavailable(self):
        pass

    def move_to_error(self):
        pass

    def move_to_retry(self):
        pass

    def move_to_submitted(self):
        pass

    def are_on_cache(self):
        pass

class LandsatProductHandler(object):

    def __init__(self, *args, **kwargs):
        super(LandsatProductHandler, self).__init__(*args, **kwargs)

    def check_ordered(self):
        pass

    def accept_submitted(self):
        pass


class ModisProductHandler(object):

    def __init__(self, *args, **kwargs):
        super(ModisProductHandler, self).__init__(*args, **kwargs)

class UserHandler(object):

    def __init__(self, userid):
        try:
            u = User.objects.get(Q(email = userid) | Q(username = userid))
            self.username = u.username
            self.email = u.email
            self.contactid = u.userprofile.contactid
            self.join_date = u.join_date
            self.last_login = u.last_login
        except User.DoesNotExist:
            raise UserNotFoundException(userid)

    def orders(self):
        pass

    def last_login(self):
        pass

    def join_date(self):
        pass

    def contact_id(self):
        pass


class OrderHandler(object):

    def __init__(self, orderid, product_handlers):
        self.orderid = orderid
        self.product_handlers = product_handlers

    def are_all_products_complete(self):
        pass

    def cancel(self):
        pass

    def status(self):
        pass

    def details(self):
        pass

    def cleanup(self):
        pass

    def complete(self):
        pass

    def purge(self):
        pass


class EEOrderHandler(OrderHandler):

    def load_orders(self):
        pass

    def order_status(self, ee_order_id):
        pass

    def unit_status(self, ee_order_id, unit_id):
        pass

    def complete_order(self, ee_order_id):
        pass

    def complete_unit(self, ee_order_id, unit_id):
        pass
'''