# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0010_auto_20150326_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='professor',
            field=models.ForeignKey(null=True, blank=True, to='grading.Profile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 10, 15, 8, 4, 111756, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 10, 15, 8, 4, 111756, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
