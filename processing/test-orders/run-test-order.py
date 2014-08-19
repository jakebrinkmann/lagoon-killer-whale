#! /usr/bin/env python

'''
License:
  "NASA Open Source Agreement 1.3"

Description:
  Execute test orders using the local environment.

History:
  Created April/2014 by Ron Dilley, USGS/EROS
'''

import os
import sys
import logging
import json
import subprocess
from cStringIO import StringIO
from argparse import ArgumentParser

import parameters


# ============================================================================
def build_argument_parser():
    '''
    Description:
      Build the command line argument parser.
    '''

    # Create a command line argument parser
    description = "Configures and executes a test order"
    parser = ArgumentParser(description=description)

    # Add parameters
    parser.add_argument('--keep-log',
                        action='store_true', dest='keep_log', default=False,
                        help="keep the log file")

    parser.add_argument('--request-file',
                        action='store', dest='request_file', required=True,
                        help="file containing request specifics")

    parser.add_argument('--products-file',
                        action='store', dest='products_file', required=True,
                        help="file containing products to process")

    return parser
# END - build_argument_parser


# ============================================================================
def process_test_order(request_file, products_file, env_vars, keep_log):
    '''
    Description:
      Process the test order file.
    '''

    logger = logging.getLogger(__name__)

    tmp_order = 'tmp-' + request_file

    order_id = request_file.split('.json')[0]

    have_error = False
    error_msg = ''

    with open(products_file, 'r') as scenes_fd:
        while (1):
            product_name = scenes_fd.readline().strip()
            if not product_name:
                break

            with open(request_file, 'r') as order_fd:
                order_contents = order_fd.read()
                if not order_contents:
                    raise Exception("Order file [%s] is empty" % request_file)

                # Validate using our parameter object
                #order = parameters.instance(json.loads(order_contents))
                #print json.dumps(order, indent=4, sort_keys=True)

                with open(tmp_order, 'w') as tmp_fd:

                    tmp_line = order_contents

                    # Update the order for the developer
                    tmp = product_name[:3]
                    is_modis = False
                    if tmp == 'MOD' or tmp == 'MYD':
                        is_modis = True

                    if not is_modis:
                        product_path = ('%s/%s%s'
                                        % (env_vars['dev_data_dir']['value'],
                                           product_name, '.tar.gz'))

                        if not os.path.isfile(product_path):
                            error_msg = ("Missing product data (%s)"
                                         % product_path)
                            have_error = True
                            break

                    tmp_line = tmp_line.replace('\n', '')

                    tmp_line = tmp_line.replace("ORDER_ID", order_id)
                    tmp_line = tmp_line.replace("SCENE_ID", product_name)
                    tmp_line = \
                        tmp_line.replace("DEV_DATA_DIRECTORY",
                                         env_vars['dev_data_dir']['value'])
                    tmp_line = \
                        tmp_line.replace("DEV_CACHE_DIRECTORY",
                                         env_vars['dev_cache_dir']['value'])

                    tmp_fd.write(tmp_line)

                    # Validate again, since we modified it
                    parms = parameters.instance(json.loads(tmp_line))
                    print json.dumps(parms, indent=4, sort_keys=True)

                # END - with tmp_order
            # END - with request_file
        # END - while (1)
    # END - with products_file

    if have_error:
        print error_msg
        return False

    keep_log_str = ''
    if keep_log:
        keep_log_str = '--keep-log'

    cmd = ("cd ..; cat test-orders/%s | ./cdr_ecv_mapper.py %s"
           % (tmp_order, keep_log_str))

    output = ''
    proc = None
    status = True
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True)
        output = proc.communicate()[0]
        if len(output) > 0:
            print output

        if proc.returncode < 0:
            print "Application terminated by signal [%s]" % cmd
            status = False

        elif proc.returncode != 0:
            print "Application failed to execute [%s]" % cmd
            status = False

        else:
            application_exitcode = proc.returncode >> 8
            if application_exitcode != 0:
                print "Application [%s] returned error code [%d]" \
                    % (cmd, application_exitcode)
                status = False

    except Exception, e:
        print str(e)
        status = False

    finally:
        del proc
        proc = None

    os.unlink(tmp_order)

    return status


# ============================================================================
if __name__ == '__main__':
    '''
    Description:
        Main code for executing a test order.
    '''

    logging.basicConfig(format=('%(asctime)s.%(msecs)03d %(process)d'
                                ' %(levelname)-8s'
                                ' %(filename)s:%(lineno)d:%(funcName)s'
                                ' -- %(message)s'),
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    # Build the command line argument parser
    parser = build_argument_parser()

    env_vars = dict()
    env_vars = {'dev_data_dir': {'name': 'DEV_DATA_DIRECTORY',
                                 'value': None},
                'dev_cache_dir': {'name': 'DEV_CACHE_DIRECTORY',
                                  'value': None},
                'espa_work_dir': {'name': 'ESPA_WORK_DIR',
                                  'value': None}}

    missing_environment_variable = False
    for var in env_vars:
        env_vars[var]['value'] = os.environ.get(env_vars[var]['name'])

        if env_vars[var]['value'] is None:
            logger.warning("Missing environment variable [%s]"
                           % env_vars[var]['name'])
            missing_environment_variable = True

    # Terminate FAILURE if missing environment variables
    if missing_environment_variable:
        logger.critical("Please fix missing environment variables")
        sys.exit(1)

    # Parse the command line arguments
    args = parser.parse_args()

    if not os.path.isfile(args.request_file):
        logger.critical("Request file [%s] does not exist" % args.request_file)
        sys.exit(1)

    if not os.path.isfile(args.products_file):
        logger.critical("Products file [%s] does not exist"
                        % args.products_file)
        sys.exit(1)

    # Avoid the creation of the *.pyc files
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    if not process_test_order(args.request_file, args.products_file, env_vars,
                              args.keep_log):
        logger.critical("Request file (%s) failed to process"
                        % args.request_file)
        sys.exit(1)

    # Terminate SUCCESS
    sys.exit(0)
