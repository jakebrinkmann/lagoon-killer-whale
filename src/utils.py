conversions = {
    'products':
        {'include_source_data': 'l1',
         'include_dswe': 'swe',
         'include_sr_evi': 'sr_evi',
         'include_cfmask': 'cloud',
         'include_sr_savi': 'sr_savi',
         'include_sr_nbr2': 'sr_nbr2',
         'include_sr_nbr': 'sr_nbr',
         'include_sr_ndmi': 'sr_ndmi',
         'include_sr': 'sr',
         'include_sr_msavi': 'sr_msavi',
         'include_lst': 'lst',
         'include_source_metadata': 'source_metadata',
         'include_sr_thermal': 'bt',
         'include_sr_toa': 'toa',
         'include_statistics': 'stats',
         'include_sr_ndvi': 'sr_ndvi'},

    'aea_map':
        {'central_meridian': 'central_meridian',
         'std_parallel_1': 'standard_parallel_1',
         'std_parallel_2': 'standard_parallel_2',
         'datum': 'datum',
         'false_northing': 'false_northing',
         'false_easting': 'false_easting',
         'origin_lat': 'latitude_of_origin'},

    'ps_map':
        {'longitude_pole': 'longitudinal_pole',
         'latitude_true_scale': 'latitude_true_scale'},

    'utm_map':
        {'utm_zone': 'zone',
         'utm_north_south': 'zone_ns'},

    'ext_map':
        {'image_extents_units': 'units',
         'minx': 'west',
         'miny': 'south',
         'maxy': 'north',
         'maxx': 'east'},

    'keywords_map':
        {'resample_method': 'resampling_method',
         'output_format': 'format',
         'image_extents': 'image_extents',
         'resize': 'resize',
         'reproject': 'projection'},

}

def merge_all_the_dicts():
    od = {}
    for key in conversions.keys():
        od.update(conversions[key])
    return od


conversions_all = merge_all_the_dicts()

# conversions_all = {
#     'include_source_data': 'l1',
#          'include_dswe': 'swe',
#          'include_sr_evi': 'sr_evi',
#          'include_cfmask': 'cloud',
#          'include_sr_savi': 'sr_savi',
#          'include_sr_nbr2': 'sr_nbr2',
#          'include_sr_nbr': 'sr_nbr',
#          'include_sr_ndmi': 'sr_ndmi',
#          'include_sr': 'sr',
#          'include_sr_msavi': 'sr_msavi',
#          'include_lst': 'lst',
#          'include_source_metadata': 'source_metadata',
#          'include_sr_thermal': 'bt',
#          'include_sr_toa': 'toa',
#          'include_statistics': 'stats',
#          'include_sr_ndvi': 'sr_ndvi',
#          'central_meridian': 'central_meridian',
#          'std_parallel_1': 'standard_parallel_1',
#          'std_parallel_2': 'standard_parallel_2',
#          'datum': 'datum',
#          'false_northing': 'false_northing',
#          'false_easting': 'false_easting',
#          'origin_lat': 'latitude_of_origin',
#          'longitude_pole': 'longitudinal_pole',
#          'latitude_true_scale': 'latitude_true_scale',
#          'utm_zone': 'zone',
#          'utm_north_south': 'zone_ns',
#          'image_extents_units': 'units',
#          'minx': 'west',
#          'miny': 'south',
#          'maxy': 'north',
#          'maxx': 'east',
#          'resample_method': 'resampling_method',
#          'output_format': 'format',
#          'image_extents': 'image_extents',
#          'resize': 'resize',
#          'reproject': 'projection'
# }
