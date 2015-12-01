''' Holds logic necessary for interacting with the online distribution
cache '''

import logging
import re
from ordering import sshcmd
from ordering.models.configuration import Configuration

logger = logging.getLogger(__name__)

class OnlineCacheException(Exception):
    ''' General exception raised from the OnlineCache '''
    pass

class OnlineCache(object):
    ''' Client code to interact with the LSRD online cache '''

    __default_order_path = '/data2/science_lsrd/LSRD/orders'
    __order_path_key = 'online_cache_orders_dir'

    def __init__(self, host=None, user=None, pw=None):

        if host is None:
            host = Configuration.get('landsatds.host')
        if user is None:
            user = Configuration.get('landsatds.username')
        if pw is None:
            pw = Configuration.get('landsatds.password')

        self.client = sshcmd.RemoteHost(host, user, pw, debug=False)

        try:
            self.orderpath = Configuration.get(self.__order_path_key)
        except Configuration.DoesNotExist:
            logger.info('{0} not defined, setting to {1}'
                .format(self.__order_path_key, self.__default_order_path))
            config = Configuration()
            config.key = self.__order_path_key
            config.value = self.__default_order_path
            config.save()

            self.orderpath = config.value

    def delete(self, orderid):
        ''' Removes an order from physical online cache disk '''

        # centrally locate this in the settings and pull in here plus urls.py
        espa_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{6,8}-[0-9]{3,6}'
        ee_order = r'[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{13}'

        if not (re.match(espa_order, orderid) or re.match(ee_order, orderid)):
            raise OnlineCacheException('invalid orderid parameter specified:{0}'.format(orderid))

        path = '/'.join([self.orderpath, orderid])

        # this should be the dir where the order is held
        logger.info('Deleting {0} from online cache'.format(path))

        try:
            result = self.client.execute('sudo chattr -fR -i {0};rm -rf {0}'.format(path))
        except Exception, exception:
            raise OnlineCacheException(exception)

        if result['stderr'] is not None and len(result['stderr']) > 0:
            raise OnlineCacheException('Error deleting order {0}: {1}'
                .format(orderid, result['stderr']))

    def capacity(self):
        ''' Returns the capacity of the online cache '''

        cmd = 'df -mhP {0}'.format(self.orderpath)
        try:
            result = self.client.execute(cmd)
        except Exception, exception:
            raise OnlineCacheException(exception)

        if result['stderr'] is not None and len(result['stderr']) > 0:
            raise OnlineCacheException('Error retrieving cache capacity:{0}'
                .format(result['stderr']))

        logger.debug('call to {0} returned {1}'.format(cmd, result['stdout']))

        line = result['stdout'][1].split(' ')
        results = {'capacity':line[2],
                   'used':line[5],
                   'available':line[8],
                   'percent_free':line[10]}
        return results

# Below here should be considered to be the public interface for this module

def delete(orderid):
    return OnlineCache().delete(orderid)

def capacity():
    return OnlineCache().capacity()
