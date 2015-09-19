'''
Purpose: database model definitions for espa-web
Author: David V. Hill
'''
import datetime
import json
import logging

from django.db import models

logger = logging.getLogger(__name__)

class DownloadSection(models.Model):
    ''' Persists grouping of download items and controls appearance order'''
    title = models.CharField('name', max_length=255)
    text = models.TextField('section_text')
    display_order = models.IntegerField()
    visible = models.BooleanField('visible')


class Download(models.Model):
    section = models.ForeignKey(DownloadSection)
    target_name = models.CharField('target_name', max_length=255)
    target_url = models.URLField('target_url', max_length=255)
    checksum_name = models.CharField('checksum_name',
                                     max_length=255,
                                     blank=True,
                                     null=True)
    checksum_url = models.URLField('checksum_url',
                                   max_length=255,
                                   blank=True,
                                   null=True)
    readme_text = models.TextField('readme_text', blank=True, null=True)
    display_order = models.IntegerField()
    visible = models.BooleanField('visible')


class Tag(models.Model):
    tag = models.CharField('tag', max_length=255)
    description = models.TextField('description', blank=True, null=True)
    last_updated = models.DateTimeField('last_updated',
                                        blank=True,
                                        null=True)

    def __unicode__(self):
        return self.tag

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.now()
        super(Tag, self).save(*args, **kwargs)


class DataPoint(models.Model):
    tags = models.ManyToManyField(Tag)
    key = models.CharField('key', max_length=250)
    command = models.CharField('command', max_length=2048)
    description = models.TextField('description', blank=True, null=True)
    enable = models.BooleanField('enable')
    last_updated = models.DateTimeField('last_updated',
                                        blank=True,
                                        null=True)

    def __unicode__(self):
        return "%s:%s" % (self.key, self.command)

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.now()
        super(DataPoint, self).save(*args, **kwargs)

    @staticmethod
    def get_data_points(tagnames=[]):
        js = {}

        if len(tagnames) > 0:
            dps = DataPoint.objects.filter(enable=True, tags__tag__in=tagnames)
        else:
            dps = DataPoint.objects.filter(enable=True)

        for d in dps:
            js[d.key] = d.command

        return json.dumps(js)
