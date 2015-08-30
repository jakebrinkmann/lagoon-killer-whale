from django.test import TestCase
from ordering import errors

class ErrorHandlerTestCase(TestCase): 
    ''' Tests the error handling module in the ordering app.
    
    Most of the errors captured and tested here originate with the 
    backend processing/production system on hadoop.  The errors make it
    to espa-web via xmlrpc calls in the rpc.py.  A few others are found
    in the ordering app itself when interacting with outside entities such
    as lta soap services.
    
    There are a variety of transient conditions in the processing environment
    that we have attempted to correct through collaborative engineering.
    Given the decentralized nature of the building it is impossible to 
    coordinate full systemic testing across all projects.  The error handler
    module keeps us sane as it automatically detects these conditions and 
    returns the proper resolution code which we can then use to update 
    the database, etc.
    
    As new errors are observed in ops, they should
    be captured from the log file, correctly categorized and added
    to one of these test cases.  Then the error handler should be fixed 
    to properly handle the case.  It's likely that not all categories
    are represented here, so make a new one if you really have to, but
    try to keep them sanely organized and grouped.'''
    
    landsat_scene = 'LE70300292003123EDC00'
    
    def __test_retry_case(self, msg, scene=landsat_scene):
        ''' utility test for all cases that mark products for retry '''
        
        result = errors.resolve(msg, scene)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'retry')
        self.assertIsNotNone(result.extra)
        self.assertIsNotNone(result.extra['retry_after'])
        self.assertIsNotNone(result.extra['retry_limit'])
        
    def __test_unavailable_case(self, msg):
        '''
        utility test for how we handle cases that should be 
        marked unavailable
        '''
        
        result = errors.resolve(msg, None)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'unavailable')
        self.assertIsNotNone(result.reason)
        self.assertTrue(len(result.reason) > 0)
        
    def __test_submitted_case(self, msg):
        '''
        utility test for handling items that should go directly back 
        to submitted status with no retry or wait time
        '''
        
        result = errors.resolve(msg, None)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'submitted')
        self.assertIsNotNone(result.reason)
        self.assertTrue(len(result.reason) > 0)
                
    def test_ssh_errors(self):
        '''
        errors relating to performing ssh operations
        '''
        
        msgs = ['Application failed to execute [ssh -q -o StrictHostKeyChe']
        [self.__test_retry_case(msg) for msg in msgs]
            
    def test_http_errors(self):
        '''
        errors detected during external http operations
        '''
        
        msgs = ['Read timed out.',
                'Connection aborted.',
                'Connection timed out',
                'Connection broken: IncompleteRead',
                '502 Server Error: Proxy Error',
                '404 Client Error: Not Found',
                'Transfer Failed - HTTP - exceeded retry limit']
        [self.__test_retry_case(msg) for msg in msgs]

    def test_db_lock_errors(self):
        '''
        db locking errors have been returned to the processing tier
        when trying to update scenes, which throws processing into 
        error status
        '''
        
        msgs = ['Lock wait timeout exceeded']
        [self.__test_retry_case(msg) for msg in msgs]
            
    def test_gzip_errors(self):
        '''
        experienced when the processing code pulls a level 1 product.  
        These errors have all been observed to be related to the transfer
        and thus can be retried
        '''
        
        msgs = ['not in gzip format',
                'gzip: stdin: unexpected end of file']
        [self.__test_retry_case(msg) for msg in msgs]
                    
    def test_gzip_errors_online_cache(self):
        '''
        experienced when processing is pulling a level 1 product.  In 
        this case, the error is not related to the transfer but is a 
        corrupt file itself and thus needs to be reprocessed before being
        rerun.  This method will automatically send an email to the ops 
        staff to reprocess the level 1.  The retry_after is set much 
        further in the future to give them time to do this before attempting
        a retry.
        
        pass None to this so it doesnt send an email to ops staff
        '''
        
        msgs = ['gzip: stdin: invalid compressed data--format violated']
        [self.__test_retry_case(msg, None) for msg in msgs]
        
    def test_oli_no_sr(self):
        '''
        experienced when end-users request surface reflectance 
        processing on an oli-only scene.  Must have tirs thermal to do 
        sr (technically, to do cloud masking)
        '''
        
        msgs = ['oli-only cannot be corrected to surface reflectance',
                'include_sr is an unavailable product option for OLI-Only dat']
        [self.__test_unavailable_case(msg) for msg in msgs]
        
    def test_night_scene(self):
        '''
        cannot perform atmospheric correction on scenes that were 
        collected at night
        '''
        
        msgs = ['solar zenith angle out of range',
                'Solar zenith angle is out of range']
        [self.__test_unavailable_case(msg) for msg in msgs]
        
    def test_missing_aux_data(self):
        '''
        the aux data needed for processing is not yet available, so 
        retry until it is
        '''
        
        msgs = ['Verify the missing auxillary data products',
                'Warning: main : Could not find auxnm data file']
        [self.__test_retry_case(msg, None) for msg in msgs]
                
    def test_ftp_errors(self):
        '''
        found during ops with the ftp server.  could be unavailble, 
        being restarted, over limits, or whatever.
        '''
        
        msgs = ['timed out|150 Opening BINARY mode data connection',
                '500 OOPS',
                'ftplib.error_reply']
        [self.__test_retry_case(msg, None) for msg in msgs]
        
    def test_network_errors(self):
        '''
        general network errors found during processing... retry them
        '''
        
        msgs = ['error: [Errno 111] Connection refused',
                'Network is unreachable',
                'Connection timed out',
                'socket.timeout']
        [self.__test_retry_case(msg) for msg in msgs]     

    def test_no_such_file_or_directory(self):
        '''
        the only time this has been found is in the order disposition code
        within espa-web.  This code creates a list of scenes to process and
        returns them to the processing code.  Before returning this list, it 
        does one final check to see if the products are all available.  There
        is a possibility that a product was purged from the level 1 cache and
        therefore needs to be reordered by us before processing.  This handles
        that case.
        '''
        
        msgs = ['No such file or directory']    
        [self.__test_submitted_case(msg) for msg in msgs]
        
    def test_dswe_unavailable(self):
        '''
        marks dswe unavailable for olitirs.  this message is returned 
        to by the processing tier
        '''
        
        msgs = ['include_dswe is an unavailable product option for OLITIRS']
        [self.__test_unavailable_case(msg) for msg in msgs]
   
    def test_oli_only_no_thermal(self):
        '''
        oli only data doesn't include the brightness temp bands, thus
        we cannot provide a thermal product for them
        '''
        
        msgs = [('include_sr_thermal is an unavailable '
                 'product option for OLI-Only data')]
        [self.__test_unavailable_case(msg) for msg in msgs]
        
    def test_lta_soap_errors(self):
        '''
        experienced when lta has their oracle database down. retry until
        it becomes available again
        '''
        
        msgs = ['Listener refused the connection with the following error']
        [self.__test_retry_case(msg) for msg in msgs]
        
    def test_warp_errors(self):
        '''
        this happens when users mess up their warp parameter requests.  we
        used to manually intervene and fix the orders but that was chewing up
        too much of our staff's time.  users will see the message that warp 
        failed and the products will be marked unavailable... then they can 
        fix thier parameters and retry later
        '''
        
        msgs = ['GDAL Warp failed to transform',
                'ERROR 1: Too many points',
                'unable to compute output bounds']
        [self.__test_unavailable_case(msg) for msg in msgs]
        
    def test_sixs_errors(self):
        '''
        transient condition with the sixs radiative transfer model in
        processing.  Theres not much we can do with fixing the code itself
        because it wasn't developed here and we don't have the capacity to 
        apply our engineering practices against the codebase
        '''
        
        msgs = ['cannot create temp file for here-document: Permission denied']
        [self.__test_retry_case(msg) for msg in msgs]