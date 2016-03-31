class User(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    @property
    def is_staff(self):
        return 'staff' in self.roles