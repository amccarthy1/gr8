# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0009_auto_20150322_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 26, 12, 41, 26, 371644, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 26, 12, 41, 26, 371644, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
