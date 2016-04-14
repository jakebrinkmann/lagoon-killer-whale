import collections


class User(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    @property
    def is_staff(self):
        return 'staff' in self.roles


def deep_update(source, overrides):
    """
    update a nested dictionary. modify source in place
    credit: stackoverflow user charlax
    http://stackoverflow.com/questions/3232943
    :param source: dictionary to update
    :param overrides: values to override
    :return: updated source
    """
    for key, value in overrides.iteritems():
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def is_num(value):
    try:
        # is it an int
        rv = int(value)
    except:
        try:
            # is it a float
            rv = float(value)
        except:
            # then return a str
            rv = value
    return rv


def gen_nested_dict(inlist, val):
    inlist.reverse()
    for idx, item in enumerate(inlist):
        _indict = {item: val} if idx is 0 else {item: _indict}
    return _indict


def format_errors(indict):
    outlist = []
    for key in indict:
        outlist.append(key+"<br/>")
        for item in indict[key]:
            outlist.append("&#8594;"+item+"<br/>")
    return "".join(outlist)

conversions = {
    'products': {
         'l1': 'original input products',
         'swe': 'dynamic surface water extent',
         'sr_evi': 'sr_evi',
         'cloud': 'cfmask',
         'sr_savi': 'sr_savi',
         'sr_nbr2': 'sr_nbr2',
         'sr_nbr': 'sr_nbr',
         'sr_ndmi': 'sr_ndmi',
         'sr': 'surface reflectance',
         'sr_msavi': 'sr_msavi',
         'lst': 'land surface temperature',
         'source_metadata': 'original input metadata',
         'bt': 'brightness temperature',
         'toa': 'top of atmosphere',
         'stats': 'plots and statistics',
         'sr_ndvi': 'sr_ndvi'
    }
}
