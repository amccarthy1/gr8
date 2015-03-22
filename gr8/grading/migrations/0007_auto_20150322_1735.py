# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0006_auto_20150322_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 17, 35, 15, 207744)),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='term',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 17, 35, 15, 207744)),
            preserve_default=True,
        ),
    ]
