from django.db import models
from django.conf import settings
from django.core.cache import cache

class Configuration(models.Model):
    '''Implements a key/value datastore on top of a relational database
    '''
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=2048)

    def __unicode__(self):
        return ('%s : %s') % (self.key, self.value)
        
    @staticmethod
    def url_for(name):
        ''' Looks up the url value based on the configured environment '''
        key = 'url.{0}.{1}'.format(settings.ESPA_ENV, name)
        return Configuration.get(key)
        
    @staticmethod
    def get(key):
        ''' Used to retrieve values from Configuration.  Incorporates 
        caching '''

        value = cache.get(key)

        if value is None:
            value = Configuration.objects.get(key=key)
            value = str(value.value)
            ttl = Configuration.objects.get(key='cache.ttl')
            cache.set(key, value, int(ttl.value))
            
        return str(value) if (value is not None and len(value) > 0) else str()

    @staticmethod
    def clear_cache(self):
        for config in Configuration.objects.all():
            cache.delete(config.key)

    def save(self, *args, **kwargs):
        ''' Override save.  Clear cached value if exists '''
        cache.delete(self.key)
        super(Configuration, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ''' Override delete to clear the cache if the value exists there '''
        cache.delete(self.key)
        super(Configuration, self).delete(*args, **kwargs)
