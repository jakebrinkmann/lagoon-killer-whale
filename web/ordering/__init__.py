from django.apps import AppConfig
from django.conf import settings
from ordering.models import Configuration

class OrderingAppConfig(AppConfig):
    name = 'ordering'
    verbose_name = 'ESPA Level 2 Bulk Ordering'
    
    def ready(self):
        # look through all the values in settings.CONFIGURATION and make
        # sure there's an entry in Configuration model for them.  If not
        # populate them with the default value
        pass