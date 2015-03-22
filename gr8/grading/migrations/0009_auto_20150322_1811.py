# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0008_auto_20150322_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 18, 11, 17, 185699)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 18, 11, 17, 185699)),
            preserve_default=True,
        ),
    ]
