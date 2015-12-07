# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

def bootstrap_config(apps, schema_editor):

    initial = {
        'cache.ttl': {'default':7 * 24 * 60 * 60, 'units':'seconds'},
        'cache.key.handle_orders_lock_timeout': {'default':21 * 60,
                                                 'units':'seconds'},
        'cache.stat.ttl': {'default': 600, 'units':'seconds'},

        'email.espa_address': {'default':'espa@usgs.gov', 'units':''},
        'email.espa_server': {'default':'gssdsflh01.cr.usgs.gov', 'units':''},
        'email.corrupt_gzip_notification_list': {'default': '', 'units':'csv'},

        'file.extension.modis.input.filename': {'default': '.hdf',
                                                'units': 'string'},
        'file.extension.landsat.input.filename': {'default': '.tar.gz',
                                                  'units':'string'},

        'lock.timeout.handle_orders': {'default': 60 * 21, 'units': 'seconds'},
        'ladsftp.password': {'default': '', 'units': 'string'},
        'ladsftp.username': {'default': '', 'units': 'string'},
        'landsatds.host': {'default': '', 'units': 'string'},
        'landsatds.password': {'default': '', 'units': 'string'},
        'landsatds.port': {'default': '', 'units': 'int'},
        'landsatds.username': {'default': '', 'units': 'string'},

        'msg.system_message_title': {'default': '', 'units':'string'},
        'msg.system_message_body': {'default': '', 'units': 'string'},

        'path.aqua_base_source': {'default':'/MOLA', 'units':'string'},
        'path.terra_base_source': {'default':'/MOLT', 'units':'string'},

        'pixel.size.meters.09A1': {'default': 500, 'units':'meters'},
        'pixel.size.meters.09GA': {'default': 500, 'units':'meters'},
        'pixel.size.meters.09GQ': {'default': 250, 'units':'meters'},
        'pixel.size.meters.09Q1': {'default': 250, 'units':'meters'},
        'pixel.size.meters.13Q1': {'default': 250, 'units':'meters'},
        'pixel.size.meters.13A3': {'default': 1000, 'units':'meters'},
        'pixel.size.meters.13A2': {'default': 1000, 'units':'meters'},
        'pixel.size.meters.13A1': {'default': 1000, 'units':'meters'},
        'pixel.size.meters.LC8': {'default': 30, 'units':'meters'},
        'pixel.size.meters.LO8': {'default': 30, 'units':'meters'},
        'pixel.size.meters.LE7': {'default': 30, 'units':'meters'},
        'pixel.size.meters.LT4': {'default': 30, 'units':'meters'},
        'pixel.size.meters.LT5': {'default': 30, 'units':'meters'},

        'pixel.size.dd.09A1': {'default': 0.00449155, 'units':'meters'},
        'pixel.size.dd.09GA': {'default': 0.00449155, 'units':'meters'},
        'pixel.size.dd.09GQ': {'default': 0.002245775, 'units':'meters'},
        'pixel.size.dd.09Q1': {'default': 0.002245775, 'units':'meters'},
        'pixel.size.dd.13Q1': {'default': 0.002245775, 'units':'meters'},
        'pixel.size.dd.13A3': {'default': 0.0089831, 'units':'meters'},
        'pixel.size.dd.13A2': {'default': 0.0089831, 'units':'meters'},
        'pixel.size.dd.13A1': {'default': 0.0089831, 'units':'meters'},
        'pixel.size.dd.LC8': {'default': 0.0002695, 'units':'meters'},
        'pixel.size.dd.LO8': {'default': 0.0002695, 'units':'meters'},
        'pixel.size.dd.LE7': {'default': 0.0002695, 'units':'meters'},
        'pixel.size.dd.LT4': {'default': 0.0002695, 'units':'meters'},
        'pixel.size.dd.LT5': {'default': 0.0002695, 'units':'meters'},

        'policy.purge_orders_after': {'default': 10, 'units': 'days'},

        'retry.http_errors.timeout': {'default':60 * 15, 'units':'seconds'},
        'retry.http_errors.retries': {'default':10, 'units':'seconds'},
        'retry.ftp_errors.timeout': {'default':60 * 15, 'units':'seconds'},
        'retry.ftp_errors.retries': {'default':10, 'units':'seconds'},
        'retry.gzip_errors.timeout': {'default':60 * 60 * 6, 'units':'seconds'},
        'retry.gzip_errors.retries': {'default':10, 'units':'seconds'},
        'retry.network_errors.timeout': {'default':60 * 2, 'units':'seconds'},
        'retry.network_errors.retries': {'default':5, 'units':'seconds'},
        'retry.db_lock_timeout.timeout': {'default':60 * 5, 'units':'seconds'},
        'retry.db_lock_timeout.retries': {'default':10, 'units':'seconds'},
        'retry.lta_soap_errors.timeout': {'default':60 * 60, 'units':'seconds'},
        'retry.lta_soap_errors.retries': {'default':12, 'units':'seconds'},
        'retry.missing_aux_data.timeout': {'default':60 * 60 * 24, 'units':'seconds'},
        'retry.missing_aux_data.retries': {'default':5, 'units':'seconds'},
        'retry.retry_missing_l1.timeout': {'default':60 * 60, 'units':'seconds'},
        'retry.retry_missing_l1.retries': {'default':8, 'units':'seconds'},
        'retry.ssh_errors.timeout': {'default':60 * 5, 'units':'seconds'},
        'retry.ssh_errors.retries': {'default':3, 'units':'seconds'},
        'retry.sixs_errors.timeout': {'default':60, 'units':'seconds'},
        'retry.sixs_errors.retries': {'default':3, 'units':'seconds'},

        'sensor.L08.name': {'default': 'oli', 'units':'string'},
        'sensor.L08.lta_name': {'default':'LANDSAT_8', 'units':'string'},
        'sensor.LC8.name': {'default': 'olitirs', 'units':'string'},
        'sensor.LC8.lta_name': {'default':'LANDSAT_8', 'units':'string'},
        'sensor.LE7.name': {'default': 'etm', 'units':'string'},
        'sensor.LE7.lta_name': {'default':'LANDSAT_ETM_PLUS', 'units':'string'},
        'sensor.LT4.name': {'default': 'tm', 'units':'string'},
        'sensor.LT4.lta_name': {'default':'LANDSAT_TM', 'units':'string'},
        'sensor.LT5.name': {'default': 'tm', 'units':'string'},
        'sensor.LT5.lta_name': {'default':'LANDSAT_TM', 'units':'string'},
        'sensor.MYD.name': {'default':'aqua', 'units':'string'},
        'sensor.MOD.name': {'default':'terra', 'units':'string'},

        'soap.client_timeout': {'default': 60 * 30, 'units':'seconds'},
        'soap.cache_location': {'default': '/tmp/suds', 'units':'string'},

        'system.load_ee_orders_enabled': {'default':'False', 'units':''},
        'system.run_order_purge_every': {'default': 24 * 60 * 60,
                                         'units':'seconds'},
        'system.display_system_message': {'default': 'False',
                                          'units':'string'},


        'url.sys.distribution.cache': {'default':'http://localhost',
                                       'units': 'string'},
        'url.sys.external_cache': {'default':'',
                                   'units':'string'},
        'url.tst.internal_cache': {'default':'',
                                   'units':'csv'},
        'url.sys.orderservice': {'default': '', 'units':'string'},
        'url.sys.orderdelivery': {'default': '', 'units':'string'},
        'url.sys.orderupdate': {'default': '', 'units':'string'},
        'url.sys.massloader': {'default': '', 'units':'string'},
        'url.sys.registration': {'default': '', 'units':'string'},
        'url.sys.register_user': {'default': '', 'units':'string'},
        'url.sys.earthexplorer': {'default': '', 'units':'string'},
        'url.sys.forgot_login': {'default': '', 'units':'string'},
        'url.sys.status_url': {'default': 'http://localhost/status',
                               'units':'string'},


        'url.dev.distribution.cache': {'default':'http://espa-dev.cr.usgs.gov',
                                       'units': 'string'},
        'url.dev.external_cache': {'default':'',
                                   'units':'string'},
        'url.dev.internal_cache': {'default':'',
                                   'units':'csv'},
        'url.dev.orderservice': {'default': '', 'units':'string'},
        'url.dev.orderdelivery': {'default': '', 'units':'string'},
        'url.dev.orderupdate': {'default': '', 'units':'string'},
        'url.dev.massloader': {'default': '', 'units':'string'},
        'url.dev.registration': {'default': '', 'units':'string'},
        'url.dev.register_user': {'default': '', 'units':'string'},
        'url.dev.earthexplorer': {'default': '', 'units':'string'},
        'url.dev.forgot_login': {'default': '', 'units':'string'},
        'url.dev.status_url': {'default': 'http://espa-dev.cr.usgs.gov/status',
                               'units':'string'},

        'url.tst.distribution.cache': {'default':'http://espa-tst.cr.usgs.gov',
                                       'units': 'string'},
        'url.tst.external_cache': {'default':'',
                                   'units':'string'},
        'url.tst.internal_cache': {'default':'',
                                   'units':'csv'},
        'url.tst.orderservice': {'default': '', 'units':'string'},
        'url.tst.orderdelivery': {'default': '', 'units':'string'},
        'url.tst.orderupdate': {'default': '', 'units':'string'},
        'url.tst.massloader': {'default': '', 'units':'string'},
        'url.tst.registration': {'default': '', 'units':'string'},
        'url.tst.register_user': {'default': '', 'units':'string'},
        'url.tst.earthexplorer': {'default': '', 'units':'string'},
        'url.tst.forgot_login': {'default': '', 'units':'string'},
        'url.tst.status_url': {'default': 'http://espa-tst.cr.usgs.gov/status',
                               'units':'string'},

        'url.ops.distribution.cache': {'default':'http://espa.cr.usgs.gov',
                                       'units': 'string'},
        'url.ops.external_cache': {'default':'',
                                   'units':'string'},
        'url.ops.internal_cache': {'default':'',
                                   'units':'csv'},
        'url.ops.orderservice': {'default': '', 'units':'string'},
        'url.ops.orderdelivery': {'default': '', 'units':'string'},
        'url.ops.orderupdate': {'default': '', 'units':'string'},
        'url.ops.massloader': {'default': '', 'units':'string'},
        'url.ops.registration': {'default': '', 'units':'string'},
        'url.ops.register_user': {'default': '', 'units':'string'},
        'url.ops.earthexplorer': {'default': '', 'units':'string'},
        'url.ops.forgot_login': {'default': '', 'units':'string'},
        'url.ops.status_url': {'default': 'http://espa.cr.usgs.gov/status',
                               'units':'string'},

    }

    Configuration = apps.get_model("ordering", "Configuration")
    keys = Configuration.objects.filter(key__in=initial.keys())
    keys = list(keys.values_list('key', flat=True))

    for item in initial.keys():
        if item not in keys:
            Configuration(key=item, value=initial[item]['default']).save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=255)),
                ('value', models.CharField(max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderid', models.CharField(unique=True, max_length=255, db_index=True)),
                ('email', models.EmailField(max_length=254, db_index=True)),
                ('order_type', models.CharField(db_index=True, max_length=50, choices=[(b'level2_ondemand', b'Level 2 On Demand'), (b'lpcs', b'Product Characterization')])),
                ('priority', models.CharField(db_index=True, max_length=10, choices=[(b'low', b'Low'), (b'normal', b'Normal'), (b'high', b'High')])),
                ('order_date', models.DateTimeField(db_index=True, verbose_name=b'date ordered', blank=True)),
                ('completion_date', models.DateTimeField(db_index=True, null=True, verbose_name=b'date completed', blank=True)),
                ('initial_email_sent', models.DateTimeField(db_index=True, null=True, verbose_name=b'initial_email_sent', blank=True)),
                ('completion_email_sent', models.DateTimeField(db_index=True, null=True, verbose_name=b'completion_email_sent', blank=True)),
                ('status', models.CharField(db_index=True, max_length=20, choices=[(b'ordered', b'Ordered'), (b'partial', b'Partially Filled'), (b'complete', b'Complete'), (b'purged', b'Purged')])),
                ('note', models.CharField(max_length=2048, null=True, blank=True)),
                ('product_options', models.TextField()),
                ('order_source', models.CharField(db_index=True, max_length=10, choices=[(b'espa', b'ESPA'), (b'ee', b'EE')])),
                ('ee_order_id', models.CharField(max_length=13, blank=True)),
                ('user', models.ForeignKey(related_name='order', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, db_index=True)),
                ('sensor_type', models.CharField(db_index=True, max_length=50, choices=[(b'landsat', b'Landsat'), (b'modis', b'Modis'), (b'plot', b'Plotting and Statistics')])),
                ('note', models.CharField(max_length=2048, null=True, blank=True)),
                ('job_name', models.CharField(max_length=255, null=True, blank=True)),
                ('product_distro_location', models.CharField(max_length=1024, blank=True)),
                ('product_dload_url', models.CharField(max_length=1024, blank=True)),
                ('cksum_distro_location', models.CharField(max_length=1024, blank=True)),
                ('cksum_download_url', models.CharField(max_length=1024, blank=True)),
                ('tram_order_id', models.CharField(max_length=13, null=True, blank=True)),
                ('ee_unit_id', models.IntegerField(max_length=11, null=True, blank=True)),
                ('status', models.CharField(db_index=True, max_length=30, choices=[(b'submitted', b'Submitted'), (b'onorder', b'On Order'), (b'oncache', b'On Cache'), (b'queued', b'Queued'), (b'processing', b'Processing'), (b'complete', b'Complete'), (b'retry', b'Retry'), (b'unavailable', b'Unavailable'), (b'error', b'Error'), (b'purged', b'Purged')])),
                ('processing_location', models.CharField(max_length=256, blank=True)),
                ('completion_date', models.DateTimeField(db_index=True, null=True, verbose_name=b'date completed', blank=True)),
                ('log_file_contents', models.TextField(null=True, verbose_name=b'log_file', blank=True)),
                ('retry_after', models.DateTimeField(db_index=True, null=True, verbose_name=b'retry_after', blank=True)),
                ('retry_limit', models.IntegerField(default=5, max_length=3, null=True, blank=True)),
                ('retry_count', models.IntegerField(default=0, max_length=3, null=True, blank=True)),
                ('order', models.ForeignKey(to='ordering.Order')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contactid', models.CharField(max_length=10)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(bootstrap_config),
    ]
