# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0005_auto_20150309_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='credits',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='enrolled_in',
            name='is_enrolled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='course_session',
            name='day',
            field=models.CharField(max_length=5, choices=[('SUN', 'Sunday'), ('MON', 'Monday'), ('TUES', 'Tuesday'), ('WED', 'Wednesday'), ('THURS', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='enrolled_in',
            name='grade',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=12, unique=True),
            preserve_default=True,
        ),
    ]
