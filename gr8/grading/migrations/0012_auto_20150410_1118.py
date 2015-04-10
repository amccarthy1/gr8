# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0011_auto_20150410_1108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='name',
        ),
        migrations.AddField(
            model_name='course_code',
            name='name',
            field=models.CharField(max_length=80, default='#sorry'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='prereq',
            name='course',
            field=models.ForeignKey(related_name='_', to='grading.Course_Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='prereq',
            name='prereq_class',
            field=models.ForeignKey(related_name='prereq_set', to='grading.Course_Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 10, 15, 17, 54, 592754, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 10, 15, 17, 54, 592754, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
