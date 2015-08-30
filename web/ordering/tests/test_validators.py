from django.test import TestCase
from ordering import validators
from ordering import sensor
from django.conf import settings


class NewOrderFilesTestCase(TestCase):
    ''' Tests the validators the web project uses to filter bad input '''
    
    modis_collection_6 = 'MYD09GA.A2002195.h10v10.006.2007164050547.hdf'
    modis_mistyped = 'D09GA.ADA2002195.h10v10.005.2007164050547.hdf'    
    
    modis_collection_5 = 'MYD09GA.A2002195.h10v10.005.2007164050547.hdf'
    modis_no_extension = 'MYD09GA.A2002195.h10v10.005.2007164050547'
     
    mod09a1 = 'MOD09A1.A2000049.h22v13.005.2006268221249.hdf'
    mod09ga = 'MOD09GA.A2010012.h24v12.005.2010014132501.hdf'
    mod09gq = 'MOD09GQ.A2013287.h24v06.005.2013302062832.hdf'
    mod09q1 = 'MOD09Q1.A2000105.h08v08.005.2006267183100.hdf'
    mod13a1 = 'MOD13A1.A2000225.h20v08.005.2006307183245.hdf'
    mod13a2 = 'MOD13A2.A2002161.h29v05.005.2008242084157.hdf'
    mod13a3 = 'MOD13A3.A2000275.h27v04.005.2007111212432.hdf'
    mod13q1 = 'MOD13Q1.A2005209.h33v07.005.2008058130925.hdf '
    myd09a1 = 'MYD09A1.A2012065.h04v09.005.2012075044707.hdf'
    myd09ga = 'MYD09GA.A2002195.h20v06.005.2007164075511.hdf'
    myd09gq = 'MYD09GQ.A2009273.h16v06.005.2009275165721.hdf'
    myd09q1 = 'MYD09Q1.A2013265.h22v07.005.2013274071948.hdf'
    myd13a1 = 'MYD13A1.A2002329.h21v09.005.2007246034812.hdf'
    myd13a2 = 'MYD13A2.A2003089.h19v07.005.2007311191801.hdf'
    myd13a3 = 'MYD13A3.A2007121.h18v04.005.2007161234044.hdf'
    myd13q1 = 'MYD13Q1.A2002217.h34v10.005.2007194113811.hdf'
    
    # sometimes landsat scenes are reprocessed and these ids may become 
    # invalid.  If the tests are failing and you can't figure out why, 
    # check the inventory via EE to see if these are still available
    tm = 'LT50290302011188PAC01'
    etm = 'LE70290302015111EDC00'
    olitirs = 'LC80290302015215LGN00'
    oli = 'LO80430342015041LGN00'

    landsat1 = 'LM10290301972226AAA06'
    landsat2 = 'LM20290301981151AAA03'
    landsat3 = 'LM30290301982083AAA03'
    landsat4 = 'LT40070581987360XXX03'
    landsat5 = 'LT50290302011300PAC01'
    landsat7 = 'LE70290302015239EDC00'
    landsat8 = 'LC80290302015199LGN00'

    good_landsat = [landsat4, landsat5, landsat7,
                    landsat8, tm, etm, olitirs, oli]
                    
    bad_landsat = [landsat1, landsat2, landsat3]
    
    good_modis = [modis_collection_5, modis_no_extension,
                  mod09a1, mod09ga, mod09gq, mod09q1,
                  mod13a1, mod13a2, mod13a3, mod13q1, 
                  myd09a1, myd09ga, myd09gq, myd09q1,
                  myd13a1, myd13a2, myd13a3, myd13q1]
                  
    bad_modis = [modis_collection_6, modis_mistyped]
                                    
    def test_empty_fail(self):
        '''
        Fail on empty scene list        
        should fail if no scenes are provided
        '''
        
        with self.assertRaises(KeyError):
            validators.NewOrderFilesValidator({})
                
    def test_normal_tile_str_fail(self):
        '''
        Fail on string types instead of sensor instance
        
        should fail if the scene provided was not an instance of
        sensor.SensorProduct
        '''
        
        parameters = {'input_products': [self.modis_collection_5]}
        with self.assertRaises(TypeError):
            validators.NewOrderFilesValidator(parameters)
            
    def test_nonexistent_tile_str_fail(self):
        '''
        Fail on string types instead of sensor instance        
        should fail if the scene provided was not an instance of
        sensor.SensorProduct
        '''
        
        parameters = {'input_products': [self.modis_collection_6]}
        with self.assertRaises(TypeError):
            validators.NewOrderFilesValidator(parameters)
        
    def test_mistyped_str_fail(self):
        '''
        Fail on string types instead of sensor instance        
        should fail if the scene provided was not an instance of
        sensor.SensorProduct
        '''
        
        parameters = {'input_products': [self.modis_mistyped]}
        with self.assertRaises(TypeError):
            validators.NewOrderFilesValidator(parameters)
            
    def test_normal_sensor_pass(self):
        '''
        Accept modis collection 5        
        this is how the scenelist validation code is intended to work
        '''
        
        _sensor = sensor.instance(self.modis_collection_5)
        params = {'input_products': [_sensor]}        
        validator = validators.NewOrderFilesValidator(params)
        self.assertIsNone(validator.errors())
        
    def test_sensor_collection6_fail(self):
        '''
        Reject modis collection 6        
        fail if they requested modis collection 6.  we don't support it
        '''
        
        with self.assertRaises(sensor.ProductNotImplemented):
            sensor.instance(self.modis_collection_6)
            
    def test_sensor_mistyped_fail(self):
        '''
        Reject mistyped scene names        
        fail if what they requested doesnt exist
        '''
        with self.assertRaises(sensor.ProductNotImplemented):
            sensor.instance(self.modis_mistyped)
    
    # This will not pass unless the test is run in the ops environment
    # This is due to an inventory check by EE services but their dev + tst
    # inventories are incomplete and out of date        
    def test_all_good_landsat(self):
        '''
        Test known good landsat scenes
        
        This will not pass unless the test is run in the ops environment
        due to an inventory check by EE services.  Their dev + tst
        inventories are incomplete and out of date.  If run in ops they
        should all pass as long as these scenes are still in the inventory
        '''
        
        if settings.ESPA_ENV == 'ops':
            inputs = [sensor.instance(x) for x in self.good_landsat]
            p = {'input_products': inputs}
            self.assertIsNone(validators.NewOrderFilesValidator(p).errors())
        
    def test_all_good_modis(self):
        '''
        Test known good modis list        
        This should pass no matter what
        '''
        inputs = [sensor.instance(x) for x in self.good_modis]
        params = {'input_products': inputs}
        self.assertIsNone(validators.NewOrderFilesValidator(params).errors())
        
        
class NewOrderParametersTestCase(TestCase):
    '''
    This tests all the requested parameters that the users submit to us
    through the UI, like requested processing levels and customization
    '''
    
    def test_nothing_selected_fail(self):
        '''
        Reject request with empty parameters
        '''
        validator = validators.NewOrderPostValidator({})
        errs = validator.errors()
        self.assertIsNotNone(errs)
        self.assertIsNotNone(errs['product_selected'])
        self.assertIsNotNone(errs['output_format'])

    def test_output_format_not_selected_fail(self):
        validator = validators.NewOrderPostValidator({'include_sr': True})
        errs = validator.errors()
        self.assertIsNotNone(errs)
        self.assertIsNotNone(errs['output_format'])
        
    def test_output_format_validator_fail(self):
        validator = validators.OutputFormatValidator({'include_sr': True})
        errs = validator.errors()
        self.assertIsNotNone(errs)
        self.assertIsNotNone(errs['output_format'])
        
    def test_invalid_output_format_fail(self):
        validator = validators.OutputFormatValidator({'include_sr': True,
                                                      'output_format': 'adsf'})
        errs = validator.errors()
        self.assertIsNotNone(errs)
        self.assertIsNotNone(errs['output_format'])
        
    def test_valid_output_format_gtiff_pass(self):
        params = {'include_sr': True, 'output_format': 'gtiff'}
        validator = validators.OutputFormatValidator(params)
        errs = validator.errors()
        self.assertIsNone(errs)
        
    def test_valid_output_format_hdf_pass(self):
        params = {'include_sr': True, 'output_format': 'hdf-eos2'}
        validator = validators.OutputFormatValidator(params)
        errs = validator.errors()
        self.assertIsNone(errs)
        
    def test_valid_output_format_envi_pass(self):
        params = {'include_sr': True, 'output_format': 'envi'}
        validator = validators.OutputFormatValidator(params)
        errs = validator.errors()
        self.assertIsNone(errs)
        
    def test_image_extents(self):
        pass
    
    def test_resizing(self):
        pass
    
    def test_reprojection(self):
        pass
    
    def test_reprojection_sinu(self):
        pass
    
    # and so on with all the other projections and permutations
        
        
        
        
        
        