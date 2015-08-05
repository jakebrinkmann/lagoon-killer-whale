'''
Purpose: exposes models via the django admin site
Author: David V. Hill
'''

from django.contrib import admin

from .models import Scene
from .models import Order
from .models import Configuration
from .models import UserProfile

__author__ = "David V. Hill"


class SceneInline(admin.StackedInline):
    model = Scene


class SceneAdmin(admin.ModelAdmin):
    fields = ['name',
              'sensor_type',
              'job_name',
              'order',
              'status',
              'completion_date',
              'tram_order_id',
              'ee_unit_id',
              'product_distro_location',
              'product_dload_url',
              'cksum_distro_location',
              'cksum_download_url',
              'processing_location',
              'note',
              'log_file_contents',
              ('retry_after',
              'retry_limit',
              'retry_count')]

    #this should stop django from querying the Order in addition to the Scene
    list_select_related = ()

    readonly_fields = ('order', 'name', 'tram_order_id', 'ee_unit_id',
                       'product_distro_location', 'product_dload_url',
                       'cksum_distro_location', 'cksum_download_url',
                       'processing_location', 'retry_count')

    list_display = ('name',
                    'sensor_type',
                    'status',
                    'job_name',
                    'completion_date',
                    'order',
                    )

    list_filter = ('status',
                   'order__priority',
                   'completion_date',
                   'sensor_type',
                   'processing_location',
                   'order'
                   )

    search_fields = ['name',
                     'status',
                     'processing_location',
                     'sensor_type',
                     'job_name',
                     'order__orderid',
                     'order__priority',
                     'order__user__email',
                     'order__user__first_name',
                     'order__user__last_name']


class OrderAdmin(admin.ModelAdmin):
    fields = ['user', 'orderid', 'order_source', 'priority', 'status',
              'ee_order_id', 'order_type', ('order_date', 'completion_date'),
              'note', 'product_options',
              ('initial_email_sent', 'completion_email_sent') ]

    list_display = ('orderid', 'user',  'status', 'priority', 'order_type',
                    'order_date', 'completion_date', 'ee_order_id',
                    'order_source', 'product_options')

    list_filter = ('order_date', 'completion_date', 'order_source', 'status',
                   'priority', 'order_type', 'orderid',  'user', 'user__email',
                   'ee_order_id')

    search_fields = ['user__username',
                     'user__email',
                     'user__first_name',
                     'user__last_name',
                     'orderid',
                     'priority',
                     'order_source',
                     'ee_order_id',
                     'status',
                     'order_type']

    readonly_fields = ('order_source', 'orderid', 'ee_order_id', 'order_type')

    inlines = [SceneInline, ]


class ConfigurationAdmin(admin.ModelAdmin):
    fields = ['key', 'value']
    list_display = ('key', 'value')
    list_filter = ('key', 'value')
    search_fields = ['key', 'value']


class UserProfileAdmin(admin.ModelAdmin):

    fields = ['user', 'contactid']

    list_display = ['user', 'contactid']

    list_filter = ['user', 'contactid']

    search_fields = ['user__username',
                     'user__email',
                     'user__first_name',
                     'user__last_name',
                     'contactid']

    readonly_fields = ('user',)


admin.site.register(Scene, SceneAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
