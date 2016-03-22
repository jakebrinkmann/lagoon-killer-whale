# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=250, verbose_name=b'key')),
                ('command', models.CharField(max_length=2048, verbose_name=b'command')),
                ('description', models.TextField(null=True, verbose_name=b'description', blank=True)),
                ('enable', models.BooleanField(verbose_name=b'enable')),
                ('last_updated', models.DateTimeField(null=True, verbose_name=b'last_updated', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_name', models.CharField(max_length=255, verbose_name=b'target_name')),
                ('target_url', models.URLField(max_length=255, verbose_name=b'target_url')),
                ('checksum_name', models.CharField(max_length=255, null=True, verbose_name=b'checksum_name', blank=True)),
                ('checksum_url', models.URLField(max_length=255, null=True, verbose_name=b'checksum_url', blank=True)),
                ('readme_text', models.TextField(null=True, verbose_name=b'readme_text', blank=True)),
                ('display_order', models.IntegerField()),
                ('visible', models.BooleanField(verbose_name=b'visible')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'name')),
                ('text', models.TextField(verbose_name=b'section_text')),
                ('display_order', models.IntegerField()),
                ('visible', models.BooleanField(verbose_name=b'visible')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderid', models.CharField(unique=True, max_length=255, db_index=True)),
                ('email', models.EmailField(max_length=75, db_index=True)),
                ('order_type', models.CharField(db_index=True, max_length=50, choices=[(b'level2_ondemand', b'Level 2 On Demand'), (b'lpcs', b'Product Characterization')])),
                ('priority', models.CharField(db_index=True, max_length=10, choices=[(b'low', b'Low'), (b'normal', b'Normal'), (b'high', b'High')])),
                ('order_date', models.DateTimeField(db_index=True, verbose_name=b'date ordered', blank=True)),
                ('completion_date', models.DateTimeField(db_index=True, null=True, verbose_name=b'date completed', blank=True)),
                ('initial_email_sent', models.DateTimeField(db_index=True, null=True, verbose_name=b'initial_email_sent', blank=True)),
                ('completion_email_sent', models.DateTimeField(db_index=True, null=True, verbose_name=b'completion_email_sent', blank=True)),
                ('status', models.CharField(db_index=True, max_length=20, choices=[(b'ordered', b'Ordered'), (b'partial', b'Partially Filled'), (b'complete', b'Complete')])),
                ('note', models.CharField(max_length=2048, null=True, blank=True)),
                ('product_options', models.TextField()),
                ('order_source', models.CharField(db_index=True, max_length=10, choices=[(b'espa', b'ESPA'), (b'ee', b'EE')])),
                ('ee_order_id', models.CharField(max_length=13, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
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
                ('status', models.CharField(db_index=True, max_length=30, choices=[(b'submitted', b'Submitted'), (b'onorder', b'On Order'), (b'oncache', b'On Cache'), (b'queued', b'Queued'), (b'processing', b'Processing'), (b'complete', b'Complete'), (b'retry', b'Retry'), (b'unavailable', b'Unavailable'), (b'error', b'Error')])),
                ('processing_location', models.CharField(max_length=256, blank=True)),
                ('completion_date', models.DateTimeField(db_index=True, null=True, verbose_name=b'date completed', blank=True)),
                ('log_file_contents', models.TextField(null=True, verbose_name=b'log_file', blank=True)),
                ('retry_after', models.DateTimeField(db_index=True, null=True, verbose_name=b'retry_after', blank=True)),
                ('retry_limit', models.IntegerField(default=5, max_length=3, null=True, blank=True)),
                ('retry_count', models.IntegerField(default=0, max_length=3, null=True, blank=True)),
                ('order', models.ForeignKey(to='ordering.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=255, verbose_name=b'tag')),
                ('description', models.TextField(null=True, verbose_name=b'description', blank=True)),
                ('last_updated', models.DateTimeField(null=True, verbose_name=b'last_updated', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contactid', models.CharField(max_length=10)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='download',
            name='section',
            field=models.ForeignKey(to='ordering.DownloadSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='tags',
            field=models.ManyToManyField(to='ordering.Tag'),
            preserve_default=True,
        ),
    ]
